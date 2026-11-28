#ifndef SAFETY_MODES_CHRYSLER_H
#define SAFETY_MODES_CHRYSLER_H

#include "opendbc/safety/declarations.h"
#include "opendbc/safety/modes/chrysler_common.h"

// Chrysler Pacifica/Jeep addresses
#define CHRYSLER_EPS_2            0x220  // EPS driver input torque
#define CHRYSLER_ESP_1            0x140  // Brake pedal and vehicle speed
#define CHRYSLER_ESP_8            0x11C  // Brake pedal and vehicle speed
#define CHRYSLER_ECM_5            0x22F  // Throttle position sensor
#define CHRYSLER_DAS_3            0x1F4  // ACC engagement states from DASM
#define CHRYSLER_DAS_6            0x2A6  // LKAS HUD and auto headlight control from DASM
#define CHRYSLER_LKAS_COMMAND     0x292  // LKAS controls from DASM
#define CHRYSLER_CRUISE_BUTTONS   0x23B  // Cruise control buttons
#define CHRYSLER_CRUISE_BUTTONS_ALT  0x000U  // Placeholder, does not exist
#define CHRYSLER_LKAS_HEARTBIT    0x2D9  // LKAS HEARTBIT from DASM
#define CHRYSLER_TRACTION_BUTTON  0x330U // Traction control button
#define CHRYSLER_Center_Stack_2   0x000  // Placeholder, does not exist

// RAM DT addresses
#define CHRYSLER_RAM_DT_EPS_2            0x31
#define CHRYSLER_RAM_DT_ESP_1            0x83
#define CHRYSLER_RAM_DT_ESP_8            0x79
#define CHRYSLER_RAM_DT_ECM_5            0x9D
#define CHRYSLER_RAM_DT_DAS_3            0x99
#define CHRYSLER_RAM_DT_DAS_6            0xFA
#define CHRYSLER_RAM_DT_LKAS_COMMAND     0xA6
#define CHRYSLER_RAM_DT_CRUISE_BUTTONS   0xB1
#define CHRYSLER_RAM_DT_CRUISE_BUTTONS_ALT  0x00U  // Placeholder, does not exist
#define CHRYSLER_RAM_DT_LKAS_HEARTBIT    0x00  // Placeholder, does not exist
#define CHRYSLER_RAM_DT_TRACTION_BUTTON  0x00  // Placeholder, does not exist
#define CHRYSLER_RAM_DT_Center_Stack_2   0x28AU

// RAM HD addresses
#define CHRYSLER_RAM_HD_EPS_2            0x220
#define CHRYSLER_RAM_HD_ESP_1            0x140
#define CHRYSLER_RAM_HD_ESP_8            0x11C
#define CHRYSLER_RAM_HD_ECM_5            0x22F
#define CHRYSLER_RAM_HD_DAS_3            0x1F4
#ifdef ALLOW_DEBUG
#define CHRYSLER_RAM_HD_DAS_6            0x275
#endif
#define CHRYSLER_RAM_HD_LKAS_COMMAND     0x276
#define CHRYSLER_RAM_HD_CRUISE_BUTTONS   0x23A
#define CHRYSLER_RAM_HD_CRUISE_BUTTONS_ALT  0x23BU  // Cruise control buttons for Ram HD alt buttons
#define CHRYSLER_RAM_HD_LKAS_HEARTBIT    0x00  // Placeholder, does not exist
#define CHRYSLER_RAM_HD_TRACTION_BUTTON  0x00  // Placeholder, does not exist
#define CHRYSLER_RAM_HD_Center_Stack_2   0x28AU

#ifdef ALLOW_DEBUG
#define CHRYSLER_RAM_HD_COMMON_TX_MSGS                       \
  {CHRYSLER_RAM_HD_LKAS_COMMAND, 0, 8, .check_relay = true}, \
  {CHRYSLER_RAM_HD_DAS_6, 0, 8, .check_relay = true},
#endif

typedef struct {
  uint32_t EPS_2;
  uint32_t ESP_1;
  uint32_t ESP_8;
  uint32_t ECM_5;
  uint32_t DAS_3;
  uint32_t LKAS_COMMAND;
  uint32_t CRUISE_BUTTONS;
  uint32_t CRUISE_BUTTONS_ALT;
} ChryslerAddrs;

static const ChryslerAddrs *chrysler_get_addrs(void) {
  static const ChryslerAddrs chrysler_addrs = {
    .EPS_2 = CHRYSLER_EPS_2,
    .ESP_1 = CHRYSLER_ESP_1,
    .ESP_8 = CHRYSLER_ESP_8,
    .ECM_5 = CHRYSLER_ECM_5,
    .DAS_3 = CHRYSLER_DAS_3,
    .LKAS_COMMAND = CHRYSLER_LKAS_COMMAND,
    .CRUISE_BUTTONS = CHRYSLER_CRUISE_BUTTONS,
    .CRUISE_BUTTONS_ALT = CHRYSLER_CRUISE_BUTTONS_ALT,
  };
  static const ChryslerAddrs chrysler_ram_dt_addrs = {
    .EPS_2 = CHRYSLER_RAM_DT_EPS_2,
    .ESP_1 = CHRYSLER_RAM_DT_ESP_1,
    .ESP_8 = CHRYSLER_RAM_DT_ESP_8,
    .ECM_5 = CHRYSLER_RAM_DT_ECM_5,
    .DAS_3 = CHRYSLER_RAM_DT_DAS_3,
    .LKAS_COMMAND = CHRYSLER_RAM_DT_LKAS_COMMAND,
    .CRUISE_BUTTONS = CHRYSLER_RAM_DT_CRUISE_BUTTONS,
    .CRUISE_BUTTONS_ALT = CHRYSLER_RAM_DT_CRUISE_BUTTONS_ALT,
  };
  static const ChryslerAddrs chrysler_ram_hd_addrs = {
    .EPS_2 = CHRYSLER_RAM_HD_EPS_2,
    .ESP_1 = CHRYSLER_RAM_HD_ESP_1,
    .ESP_8 = CHRYSLER_RAM_HD_ESP_8,
    .ECM_5 = CHRYSLER_RAM_HD_ECM_5,
    .DAS_3 = CHRYSLER_RAM_HD_DAS_3,
    .LKAS_COMMAND = CHRYSLER_RAM_HD_LKAS_COMMAND,
    .CRUISE_BUTTONS = CHRYSLER_RAM_HD_CRUISE_BUTTONS,
    .CRUISE_BUTTONS_ALT = CHRYSLER_RAM_HD_CRUISE_BUTTONS_ALT,
  };
  return (safety_setup.chrysler_platform == CHRYSLER_RAM_DT) ? &chrysler_ram_dt_addrs :
         ((safety_setup.chrysler_platform == CHRYSLER_RAM_HD) ? &chrysler_ram_hd_addrs : &chrysler_addrs);
}

static uint8_t chrysler_get_counter(const CANPacket_t *msg) {
  return (uint8_t)(msg->data[6] >> 4);
}

static void chrysler_rx_hook(const CANPacket_t *msg) {
  // Measured EPS torque
  if (msg_matches(msg, chrysler_get_addrs()->EPS_2, 0U)) {
    int torque_meas_new = from_offset(GET_BYTES_BE(msg, 4, 2) & 0x7FFU, 1024);
    update_sample(&safety.torque_meas, torque_meas_new);
  }

  // enter controls on rising edge of ACC, exit controls on ACC off
  const unsigned int das_3_bus = (safety_setup.chrysler_platform == CHRYSLER_PACIFICA) ? 0U : 2U;
  if (msg_matches(msg, chrysler_get_addrs()->DAS_3, das_3_bus)) {
    bool cruise_engaged = GET_BIT(msg, 21U);
    pcm_cruise_check(cruise_engaged);
    safety.acc_main_on = GET_BIT(msg, 20U);
  }

  // TODO: use the same message for both
  // update vehicle moving
  if ((safety_setup.chrysler_platform != CHRYSLER_PACIFICA) && msg_matches(msg, chrysler_get_addrs()->ESP_8, 0U)) {
    safety.vehicle_moving = GET_BYTES_BE(msg, 4, 2) != 0U;
  }
  if ((safety_setup.chrysler_platform == CHRYSLER_PACIFICA) && msg_matches(msg, 514U, 0U)) {
    uint32_t speed_l = GET_BYTES_BE(msg, 0, 2) >> 4;
    uint32_t speed_r = GET_BYTES_BE(msg, 2, 2) >> 4;
    safety.vehicle_moving = (speed_l | speed_r) != 0U;
  }

  // exit controls on rising edge of gas press
  if (msg_matches(msg, chrysler_get_addrs()->ECM_5, 0U)) {
    safety.gas_pressed = msg->data[0U] != 0U;
  }

  // exit controls on rising edge of brake press
  if (msg_matches(msg, chrysler_get_addrs()->ESP_1, 0U)) {
    safety.brake_pressed = ((msg->data[0U] & 0xFU) >> 2U) == 1U;
  }

  if ((safety_setup.chrysler_platform == CHRYSLER_PACIFICA) && msg_matches(msg, CHRYSLER_TRACTION_BUTTON, 0U)) {
    safety.mads_button_press = GET_BIT(msg, 53U) ? MADS_BUTTON_PRESSED : MADS_BUTTON_NOT_PRESSED;
  }

  if ((safety_setup.chrysler_platform != CHRYSLER_PACIFICA) && (msg->bus == 0U)) {
    if (msg->addr == CHRYSLER_RAM_DT_Center_Stack_2) {
      safety.mads_button_press = GET_BIT(msg, 57U) ? MADS_BUTTON_PRESSED : MADS_BUTTON_NOT_PRESSED;
    }
  }
}

static bool chrysler_tx_hook(const CANPacket_t *msg) {
  const TorqueSteeringLimits CHRYSLER_STEERING_LIMITS = {
    .max_torque = 261,
    .max_rt_delta = 112,
    .max_rate_up = 3,
    .max_rate_down = 3,
    .max_torque_error = 80,
    .type = TorqueMotorLimited,
  };

  const TorqueSteeringLimits CHRYSLER_RAM_DT_STEERING_LIMITS = {
    .max_torque = 350,
    .max_rt_delta = 112,
    .max_rate_up = 6,
    .max_rate_down = 6,
    .max_torque_error = 80,
    .type = TorqueMotorLimited,
  };

  const TorqueSteeringLimits CHRYSLER_RAM_HD_STEERING_LIMITS = {
    .max_torque = 361,
    .max_rt_delta = 182,
    .max_rate_up = 14,
    .max_rate_down = 14,
    .max_torque_error = 80,
    .type = TorqueMotorLimited,
  };

  bool tx = true;

  // STEERING
  if (msg->addr == chrysler_get_addrs()->LKAS_COMMAND) {
    int start_byte = (safety_setup.chrysler_platform == CHRYSLER_PACIFICA) ? 0 : 1;
    int desired_torque = from_offset(GET_BYTES_BE(msg, start_byte, 2) & 0x7FFU, 1024);

    const TorqueSteeringLimits limits = (safety_setup.chrysler_platform == CHRYSLER_PACIFICA) ? CHRYSLER_STEERING_LIMITS :
                                        (safety_setup.chrysler_platform == CHRYSLER_RAM_DT) ? CHRYSLER_RAM_DT_STEERING_LIMITS : CHRYSLER_RAM_HD_STEERING_LIMITS;

    bool steer_req = (safety_setup.chrysler_platform == CHRYSLER_PACIFICA) ? GET_BIT(msg, 4U) : ((msg->data[3] & 0x7U) == 2U);
    if (steer_torque_cmd_checks(desired_torque, steer_req, limits)) {
      tx = false;
    }
  }

  // FORCE CANCEL: only the cancel button press is allowed
  if ((msg->addr == chrysler_get_addrs()->CRUISE_BUTTONS) || (msg->addr == chrysler_get_addrs()->CRUISE_BUTTONS_ALT)) {
    const bool is_cancel = msg->data[0] == 1U;
    const bool is_accel = msg->data[0] == 0x04U;
    const bool is_decel = msg->data[0] == 0x08U;
    const bool is_resume = msg->data[0] == 0x10U;
    const bool allowed = is_cancel || ((is_resume || is_accel || is_decel) && safety.controls_allowed);
    if (!allowed) {
      tx = false;
    }
  }

  return tx;
}

static safety_config chrysler_init(uint16_t param) {
  const uint32_t CHRYSLER_PARAM_RAM_DT = 1U;  // set for Ram DT platform

  static const RxCheck chrysler_ram_dt_rx_checks[] = {
    {.msg = {{CHRYSLER_RAM_DT_EPS_2, 0, 8, 100U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_DT_ESP_1, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_DT_ESP_8, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_DT_ECM_5, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_DT_DAS_3, 2, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_DT_Center_Stack_2, 0, 8, 1U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true, .ignore_frequency_check = true}, { 0 }, { 0 }}},
  };

  static const RxCheck chrysler_rx_checks[] = {
    {.msg = {{CHRYSLER_EPS_2, 0, 8, 100U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_ESP_1, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{514, 0, 8, 100U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_ECM_5, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_DAS_3, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_TRACTION_BUTTON, 0, 8, 1U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true, .ignore_frequency_check = true}, { 0 }, { 0 }}},
  };

  static const CanMsg CHRYSLER_TX_MSGS[] = {
    {CHRYSLER_CRUISE_BUTTONS, 0, 3, .check_relay = false},
    {CHRYSLER_LKAS_COMMAND, 0, 6, .check_relay = true},
    {CHRYSLER_DAS_6, 0, 8, .check_relay = true},
    {CHRYSLER_LKAS_HEARTBIT, 0, 5, .check_relay = true},
  };

  static const CanMsg CHRYSLER_RAM_DT_TX_MSGS[] = {
    {CHRYSLER_RAM_DT_CRUISE_BUTTONS, 2, 3, .check_relay = false},
    {CHRYSLER_RAM_DT_LKAS_COMMAND, 0, 8, .check_relay = true},
    {CHRYSLER_RAM_DT_DAS_6, 0, 8, .check_relay = true},
  };

#ifdef ALLOW_DEBUG
  static const RxCheck chrysler_ram_hd_rx_checks[] = {
    {.msg = {{CHRYSLER_RAM_HD_EPS_2, 0, 8, 100U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_HD_ESP_1, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_HD_ESP_8, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_HD_ECM_5, 0, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_HD_DAS_3, 2, 8, 50U, .max_counter = 15U, .ignore_quality_flag = true}, { 0 }, { 0 }}},
    {.msg = {{CHRYSLER_RAM_HD_Center_Stack_2, 0, 8, 1U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true, .ignore_frequency_check = true}, { 0 }, { 0 }}},
  };

  const uint32_t CHRYSLER_PARAM_RAM_HD = 2U;  // set for Ram HD platform
  const uint16_t CHRYSLER_PARAM_SP_RAM_HD_ALT_BUTTONS = 1U;
  bool enable_ram_hd = GET_FLAG(param, CHRYSLER_PARAM_RAM_HD);
  bool ram_hd_alt_buttons = GET_FLAG(safety_setup.current_safety_param_sp, CHRYSLER_PARAM_SP_RAM_HD_ALT_BUTTONS);
#endif

  safety_config ret;

  bool enable_ram_dt = GET_FLAG(param, CHRYSLER_PARAM_RAM_DT);

  if (enable_ram_dt) {
    safety_setup.chrysler_platform = CHRYSLER_RAM_DT;
    ret = BUILD_SAFETY_CFG(chrysler_ram_dt_rx_checks, CHRYSLER_RAM_DT_TX_MSGS);
#ifdef ALLOW_DEBUG
  } else if (enable_ram_hd) {
    static const CanMsg CHRYSLER_RAM_HD_TX_MSGS[] = {
      CHRYSLER_RAM_HD_COMMON_TX_MSGS
      {CHRYSLER_RAM_HD_CRUISE_BUTTONS, 2, 3, .check_relay = false},
    };

    static const CanMsg CHRYSLER_RAM_HD_ALT_BUTTONS_TX_MSGS[] = {
      CHRYSLER_RAM_HD_COMMON_TX_MSGS
      {CHRYSLER_RAM_HD_CRUISE_BUTTONS_ALT, 2, 3, .check_relay = false},
    };

    safety_setup.chrysler_platform = CHRYSLER_RAM_HD;
    SET_RX_CHECKS(chrysler_ram_hd_rx_checks, ret);
    if (ram_hd_alt_buttons) {
      SET_TX_MSGS(CHRYSLER_RAM_HD_ALT_BUTTONS_TX_MSGS, ret);
    } else {
      SET_TX_MSGS(CHRYSLER_RAM_HD_TX_MSGS, ret);
    }
#endif
  } else {
    safety_setup.chrysler_platform = CHRYSLER_PACIFICA;
    ret = BUILD_SAFETY_CFG(chrysler_rx_checks, CHRYSLER_TX_MSGS);
  }
  return ret;
}

static const safety_hooks chrysler_hooks = {
  .init = chrysler_init,
  .rx = chrysler_rx_hook,
  .tx = chrysler_tx_hook,
  .get_counter = chrysler_get_counter,
  .get_checksum = chrysler_get_checksum,
  .compute_checksum = chrysler_compute_checksum,
};

#endif  // SAFETY_MODES_CHRYSLER_H
