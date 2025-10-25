#pragma once

#include "opendbc/safety/safety_declarations.h"

static uint8_t rivian_get_counter(const CANPacket_t *msg) {
  uint8_t cnt = 0;
  if ((msg->addr == 0x208U) || (msg->addr == 0x150U)) {
    // Signal: ESP_Status_Counter, VDM_PropStatus_Counter
    cnt = msg->data[1] & 0xFU;
  }
  return cnt;
}

static uint32_t rivian_get_checksum(const CANPacket_t *msg) {
  uint8_t chksum = 0;
  if ((msg->addr == 0x208U) || (msg->addr == 0x150U)) {
    // Signal: ESP_Status_Checksum, VDM_PropStatus_Checksum
    chksum = msg->data[0];
  } else {
  }
  return chksum;
}

static uint8_t _rivian_compute_checksum(const CANPacket_t *msg, uint8_t poly, uint8_t xor_output) {
  int len = GET_LEN(msg);

  uint8_t crc = 0;
  // Skip the checksum byte
  for (int i = 1; i < len; i++) {
    crc ^= msg->data[i];
    for (int j = 0; j < 8; j++) {
      if ((crc & 0x80U) != 0U) {
        crc = (crc << 1) ^ poly;
      } else {
        crc <<= 1;
      }
    }
  }
  return crc ^ xor_output;
}

static uint32_t rivian_compute_checksum(const CANPacket_t *msg) {
  uint8_t chksum = 0;
  if (msg->addr == 0x208U) {
    chksum = _rivian_compute_checksum(msg, 0x1D, 0xB1);
  } else if (msg->addr == 0x150U) {
    chksum = _rivian_compute_checksum(msg, 0x1D, 0x9A);
  } else {
  }
  return chksum;
}

static bool rivian_get_quality_flag_valid(const CANPacket_t *msg) {
  bool valid = false;
  if (msg->addr == 0x208U) {
    valid = ((msg->data[3] >> 3) & 0x3U) == 0x1U;  // ESP_Vehicle_Speed_Q
  } else if (msg->addr == 0x150U) {
    valid = (msg->data[1] >> 6) == 0x1U;  // VDM_VehicleSpeedQ
  } else {
  }
  return valid;
}

static void rivian_rx_hook(const CANPacket_t *msg) {

  if (msg->bus == 0U)  {
    // Vehicle speed
    if (msg->addr == 0x208U) {
      float speed = ((msg->data[6] << 8) | msg->data[7]) * 0.01;
      vehicle_moving = speed > 0.0;
      UPDATE_VEHICLE_SPEED(speed * KPH_TO_MS);
    }

    // Gas pressed and second speed source for variable torque limit
    if (msg->addr == 0x150U) {
      gas_pressed = msg->data[3] | (msg->data[4] & 0xC0U);

      // Disable controls if speeds from VDM and ESP ECUs are too far apart.
      float vdm_speed = ((msg->data[5] << 8) | msg->data[6]) * 0.01 * KPH_TO_MS;
      speed_mismatch_check(vdm_speed);
    }

    // Driver torque
    if (msg->addr == 0x380U) {
      int torque_driver_new = (((msg->data[2] << 4) | (msg->data[3] >> 4))) - 2050U;
      update_sample(&torque_driver, torque_driver_new);
    }

    // Brake pressed
    if (msg->addr == 0x38fU) {
      brake_pressed = (msg->data[2] >> 7) & 1U;
    }
  }

  if (msg->bus == 2U) {
    // Cruise state
    if (msg->addr == 0x100U) {
      const int feature_status = msg->data[2] >> 5U;
      pcm_cruise_check(feature_status == 2);
    }
  }
}

static bool rivian_tx_hook(const CANPacket_t *msg) {
  const AngleSteeringLimits RIVIAN_ANGLE_LIMITS = {
    .angle_deg_to_can = 10,
    .angle_rate_up_lookup = {
      {5., 25., 25.},
      {25., 15., 5.},  // deg/s, faster at low speed
    },
    .angle_rate_down_lookup = {
      {5., 25., 25.},
      {50., 30., 10.},  // deg/s, faster recovery
    },
  };

  const LongitudinalLimits RIVIAN_LONG_LIMITS = {
    .max_accel = 200,
    .min_accel = -350,
    .inactive_accel = 0,
  };

  bool tx = true;

  if (msg->bus == 0U) {
    // Angle-based steering control (Driver+)
    if (msg->addr == 0x110U) {
      // ACM_SteeringAngleRequest: bit 23, 15 bits, little endian, scale 0.1, offset -1638.4
      // Bit 23 starts in byte 2 (bit 16-23), spans into byte 3 and 4
      int desired_angle_raw = (msg->data[2] >> 7) | (msg->data[3] << 1) | ((msg->data[4] & 0x3F) << 9);
      float desired_angle = (desired_angle_raw * 0.1) - 1638.4;
      bool steer_req = ((msg->data[1] >> 5) & 3U) == 1U;  // ACM_EacEnabled == 1

      if (steer_angle_cmd_checks(desired_angle, steer_req, RIVIAN_ANGLE_LIMITS)) {
        tx = false;
      }
    }

    // Longitudinal control
    if (msg->addr == 0x160U) {
      int raw_accel = ((msg->data[2] << 3) | (msg->data[3] >> 5)) - 1024U;
      if (longitudinal_accel_checks(raw_accel, RIVIAN_LONG_LIMITS)) {
        tx = false;
      }
    }
  }

  return tx;
}

static safety_config rivian_init(uint16_t param) {
  // SCCM_WheelTouch: for hiding hold wheel alert
  // VDM_AdasSts: for canceling stock ACC and setting driver mode status
  // EPASS_Status: for EPAS EAC status on bus 0
  // ACM_SteeringControl: for angle-based steering (Driver+) on bus 0
  // ACM_longitudinalRequest: for long interface enable on bus 0
  // EPAS_AdasStatus: for EPAS EAC status on bus 0
  // 0x110 = ACM_SteeringControl, 0x160 = ACM_longitudinalRequest, 0x321 = SCCM_WheelTouch, 0x162 = VDM_AdasSts, 0x360 = EPASS_Status, 0x390 = EPAS_AdasStatus
  static const CanMsg RIVIAN_TX_MSGS[] = {{0x110, 0, 8, .check_relay = true}, {0x160, 0, 5, .check_relay = true}, {0x321, 2, 7, .check_relay = true}, {0x162, 2, 8, .check_relay = true}, {0x360, 0, 4, .check_relay = true}, {0x390, 0, 7, .check_relay = true}};
  // 0x160 = ACM_longitudinalRequest (on bus 0 for both interface enable and actual long control)
  static const CanMsg RIVIAN_LONG_TX_MSGS[] = {{0x110, 0, 8, .check_relay = true}, {0x160, 0, 5, .check_relay = true}, {0x321, 2, 7, .check_relay = true}, {0x162, 2, 8, .check_relay = true}, {0x360, 0, 4, .check_relay = true}, {0x390, 0, 7, .check_relay = true}};

  static RxCheck rivian_rx_checks[] = {
    {.msg = {{0x208, 0, 8, 50U, .max_counter = 14U}, { 0 }, { 0 }}},                                                             // ESP_Status (speed)
    {.msg = {{0x150, 0, 7, 50U, .max_counter = 14U}, { 0 }, { 0 }}},                                                             // VDM_PropStatus (gas pedal & 2nd speed)
    {.msg = {{0x380, 0, 5, 100U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // EPAS_SystemStatus (driver torque)
    {.msg = {{0x38f, 0, 6, 50U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true}, { 0 }, { 0 }}},   // iBESP2 (brakes)
    {.msg = {{0x100, 2, 8, 100U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // ACM_Status (cruise state)
  };

  bool rivian_longitudinal = false;

  UNUSED(param);
  #ifdef ALLOW_DEBUG
    const int FLAG_RIVIAN_LONG_CONTROL = 1;
    rivian_longitudinal = GET_FLAG(param, FLAG_RIVIAN_LONG_CONTROL);
  #endif

  // FIXME: cppcheck thinks that rivian_longitudinal is always false. This is not true
  // if ALLOW_DEBUG is defined but cppcheck is run without ALLOW_DEBUG
  // cppcheck-suppress knownConditionTrueFalse
  return rivian_longitudinal ? BUILD_SAFETY_CFG(rivian_rx_checks, RIVIAN_LONG_TX_MSGS) : \
                               BUILD_SAFETY_CFG(rivian_rx_checks, RIVIAN_TX_MSGS);
}

const safety_hooks rivian_hooks = {
  .init = rivian_init,
  .rx = rivian_rx_hook,
  .tx = rivian_tx_hook,
  .get_counter = rivian_get_counter,
  .get_checksum = rivian_get_checksum,
  .compute_checksum = rivian_compute_checksum,
  .get_quality_flag_valid = rivian_get_quality_flag_valid,
};
