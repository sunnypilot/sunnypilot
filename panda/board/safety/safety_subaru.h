const int SUBARU_MAX_STEER = 2047; // 1s
const int SUBARU_MAX_STEER_2020 = 1439; // lower limit for Impreza/Crosstrek 2020+
// real time torque limit to prevent controls spamming
// the real time limit is 1500/sec
const int SUBARU_MAX_RT_DELTA = 940;          // max delta torque allowed for real time checks
const uint32_t SUBARU_RT_INTERVAL = 250000;    // 250ms between real time checks
const int SUBARU_MAX_RATE_UP = 50;
const int SUBARU_MAX_RATE_DOWN = 70;
const int SUBARU_DRIVER_TORQUE_ALLOWANCE = 60;
const int SUBARU_DRIVER_TORQUE_FACTOR = 10;
const int SUBARU_STANDSTILL_THRSLD = 20;  // about 1kph

const CanMsg SUBARU_TX_MSGS[] = {{0x122, 0, 8}, {0x221, 0, 8}, {0x321, 0, 8}, {0x322, 0, 8}, {0x40, 2, 8}, {0x139, 2, 8}};
#define SUBARU_TX_MSGS_LEN (sizeof(SUBARU_TX_MSGS) / sizeof(SUBARU_TX_MSGS[0]))

const CanMsg SUBARU_GEN2_TX_MSGS[] = {{0x122, 0, 8}, {0x321, 0, 8}, {0x322, 0, 8}, {0x40, 2, 8}, {0x139, 2, 8}};
#define SUBARU_GEN2_TX_MSGS_LEN (sizeof(SUBARU_GEN2_TX_MSGS) / sizeof(SUBARU_GEN2_TX_MSGS[0]))

AddrCheckStruct subaru_addr_checks[] = {
  {.msg = {{ 0x40, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 10000U}, { 0 }, { 0 }}},
  {.msg = {{0x119, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x139, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x13a, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x13c, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x240, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 50000U}, { 0 }, { 0 }}},
};
#define SUBARU_ADDR_CHECK_LEN (sizeof(subaru_addr_checks) / sizeof(subaru_addr_checks[0]))
addr_checks subaru_rx_checks = {subaru_addr_checks, SUBARU_ADDR_CHECK_LEN};

AddrCheckStruct subaru_gen2_addr_checks[] = {
  {.msg = {{ 0x40, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 10000U}, { 0 }, { 0 }}},
  {.msg = {{0x119, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x139, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x13a, 1, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x13c, 1, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 20000U}, { 0 }, { 0 }}},
  {.msg = {{0x240, 1, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 50000U}, { 0 }, { 0 }}},
};
#define SUBARU_GEN2_ADDR_CHECK_LEN (sizeof(subaru_gen2_addr_checks) / sizeof(subaru_gen2_addr_checks[0]))
addr_checks subaru_gen2_rx_checks = {subaru_gen2_addr_checks, SUBARU_GEN2_ADDR_CHECK_LEN};

AddrCheckStruct subaru_hybrid_addr_checks[] = {
  {.msg = {{0x119, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep =  20000U}, { 0 }, { 0 }}},
  {.msg = {{0x139, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep =  20000U}, { 0 }, { 0 }}},
  {.msg = {{0x13a, 0, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep =  20000U}, { 0 }, { 0 }}},
  {.msg = {{0x168, 1, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep =  40000U}, { 0 }, { 0 }}},
  {.msg = {{0x226, 1, 8, .expected_timestep = 40000U}, { 0 }, { 0 }}},
  {.msg = {{0x321, 2, 8, .check_checksum = true, .max_counter = 15U, .expected_timestep = 100000U}, { 0 }, { 0 }}},
};
#define SUBARU_HYBRID_ADDR_CHECK_LEN (sizeof(subaru_hybrid_addr_checks) / sizeof(subaru_hybrid_addr_checks[0]))
addr_checks subaru_hybrid_rx_checks = {subaru_hybrid_addr_checks, SUBARU_HYBRID_ADDR_CHECK_LEN};


const uint16_t SUBARU_PARAM_MAX_STEER_2020 = 1;
bool subaru_max_steer_2020 = false;

static uint8_t subaru_get_checksum(CAN_FIFOMailBox_TypeDef *to_push) {
  return (uint8_t)GET_BYTE(to_push, 0);
}

static uint8_t subaru_get_counter(CAN_FIFOMailBox_TypeDef *to_push) {
  return (uint8_t)(GET_BYTE(to_push, 1) & 0xF);
}

static uint8_t subaru_compute_checksum(CAN_FIFOMailBox_TypeDef *to_push) {
  int addr = GET_ADDR(to_push);
  int len = GET_LEN(to_push);
  uint8_t checksum = (uint8_t)(addr) + (uint8_t)((unsigned int)(addr) >> 8U);
  for (int i = 1; i < len; i++) {
    checksum += (uint8_t)GET_BYTE(to_push, i);
  }
  return checksum;
}

static int subaru_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  bool valid = addr_safety_check(to_push, &subaru_rx_checks,
                            subaru_get_checksum, subaru_compute_checksum, subaru_get_counter);

  if (valid && (GET_BUS(to_push) == 0)) {
    int addr = GET_ADDR(to_push);
    if (addr == 0x119) {
      int torque_driver_new;
      torque_driver_new = ((GET_BYTES_04(to_push) >> 16) & 0x7FF);
      torque_driver_new = -1 * to_signed(torque_driver_new, 11);
      update_sample(&torque_driver, torque_driver_new);
    }

    if (addr == 0x240) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 8) & 1); // ACC main_on signal
      if (acc_main_on && !acc_main_on_prev)
      {
        controls_allowed = 1;
      }
      acc_main_on_prev = acc_main_on;
    }

    // enter controls on rising edge of ACC, exit controls on ACC off
    if (addr == 0x240) {
      int cruise_engaged = ((GET_BYTES_48(to_push) >> 9) & 1);
      if (cruise_engaged && !cruise_engaged_prev) {
        controls_allowed = 1;
      }
      cruise_engaged_prev = cruise_engaged;
    }

    if (addr == 0x240) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 8) & 1); // ACC main_on signal
      if (acc_main_on_prev != acc_main_on)
      {
        disengageFromBrakes = false;
        controls_allowed = 0;
      }
      acc_main_on_prev = acc_main_on;
    }

    // sample wheel speed, averaging opposite corners
    if (addr == 0x13a) {
      int subaru_speed = (GET_BYTES_04(to_push) >> 12) & 0x1FFF;  // FR
      subaru_speed += (GET_BYTES_48(to_push) >> 6) & 0x1FFF;  // RL
      subaru_speed /= 2;
      vehicle_moving = subaru_speed > SUBARU_STANDSTILL_THRSLD;
    }

    if (addr == 0x13c) {
      brake_pressed = ((GET_BYTE(to_push, 7) >> 6) & 1);
    }

    if (addr == 0x40) {
      gas_pressed = GET_BYTE(to_push, 4) != 0;
    }

    generic_rx_checks((addr == 0x122));
  }
  return valid;
}

static int subaru_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  int tx = 1;
  int addr = GET_ADDR(to_send);

  if (!msg_allowed(to_send, SUBARU_TX_MSGS, SUBARU_TX_MSGS_LEN)) {
    tx = 0;
  }

  if (relay_malfunction) {
    tx = 0;
  }

  // steer cmd checks
  if (addr == 0x122) {
    int desired_torque = ((GET_BYTES_04(to_send) >> 16) & 0x1FFF);
    bool violation = 0;
    uint32_t ts = microsecond_timer_get();

    desired_torque = -1 * to_signed(desired_torque, 13);

    if (controls_allowed) {

      if (subaru_max_steer_2020) {
        // *** global torque limit check ***
        violation |= max_limit_check(desired_torque, SUBARU_MAX_STEER_2020, -SUBARU_MAX_STEER_2020);

        // *** torque rate limit check ***
        violation |= driver_limit_check(desired_torque, desired_torque_last, &torque_driver,
          SUBARU_MAX_STEER_2020, SUBARU_MAX_RATE_UP, SUBARU_MAX_RATE_DOWN,
          SUBARU_DRIVER_TORQUE_ALLOWANCE, SUBARU_DRIVER_TORQUE_FACTOR);
      }
      else {
        // *** global torque limit check ***
        violation |= max_limit_check(desired_torque, SUBARU_MAX_STEER, -SUBARU_MAX_STEER);

        // *** torque rate limit check ***
        violation |= driver_limit_check(desired_torque, desired_torque_last, &torque_driver,
          SUBARU_MAX_STEER, SUBARU_MAX_RATE_UP, SUBARU_MAX_RATE_DOWN,
          SUBARU_DRIVER_TORQUE_ALLOWANCE, SUBARU_DRIVER_TORQUE_FACTOR);
      }

      // used next time
      desired_torque_last = desired_torque;

      // *** torque real time rate limit check ***
      violation |= rt_rate_limit_check(desired_torque, rt_torque_last, SUBARU_MAX_RT_DELTA);

      // every RT_INTERVAL set the new limits
      uint32_t ts_elapsed = get_ts_elapsed(ts, ts_last);
      if (ts_elapsed > SUBARU_RT_INTERVAL) {
        rt_torque_last = desired_torque;
        ts_last = ts;
      }
    }

    // no torque if controls is not allowed
    if (!controls_allowed && (desired_torque != 0)) {
      violation = 1;
    }

    // reset to 0 if either controls is not allowed or there's a violation
    if (violation || !controls_allowed) {
      desired_torque_last = 0;
      rt_torque_last = 0;
      ts_last = ts;
    }

    if (violation) {
      tx = 0;
    }

  }
  return tx;
}

static int subaru_fwd_hook(int bus_num, CAN_FIFOMailBox_TypeDef *to_fwd) {
  int bus_fwd = -1;
  int addr = GET_ADDR(to_fwd);

  if (!relay_malfunction) {
    if (bus_num == 0) {
      // Global platform
      // 0x40 Throttle
      // 0x139 Brake_Pedal
      int block_msg = ((addr == 0x40) || (addr == 0x139));
      if (!block_msg) {
        bus_fwd = 2;  // Camera CAN
      }
    }
    if (bus_num == 2) {
      // Global platform
      // 0x122 ES_LKAS
      // 0x221 ES_Distance
      // 0x321 ES_DashStatus
      // 0x322 ES_LKAS_State
      int block_msg = ((addr == 0x122) || (addr == 0x221) || (addr == 0x321) || (addr == 0x322));
      if (!block_msg) {
        bus_fwd = 0;  // Main CAN
      }
    }
  }
  // fallback to do not forward
  return bus_fwd;
}

// subaru gen2
static int subaru_gen2_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  bool valid = addr_safety_check(to_push, &subaru_gen2_rx_checks,
                            subaru_get_checksum, subaru_compute_checksum, subaru_get_counter);
  int addr = GET_ADDR(to_push);

  if (valid && (GET_BUS(to_push) == 0)) {
    if (addr == 0x119) {
      int torque_driver_new;
      torque_driver_new = ((GET_BYTES_04(to_push) >> 16) & 0x7FF);
      torque_driver_new = -1 * to_signed(torque_driver_new, 11);
      update_sample(&torque_driver, torque_driver_new);
    }
  }



  if (valid && (GET_BUS(to_push) == 1)) {
    if (addr == 0x240) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 8) & 1); // ACC main_on signal
      if (acc_main_on && !acc_main_on_prev)
      {
        controls_allowed = 1;
      }
      acc_main_on_prev = acc_main_on;
    }

    // enter controls on rising edge of ACC, exit controls on ACC off
    if (addr == 0x240) {
      int cruise_engaged = ((GET_BYTES_48(to_push) >> 9) & 1);
      if (cruise_engaged && !cruise_engaged_prev) {
        controls_allowed = 1;
      }
      cruise_engaged_prev = cruise_engaged;
    }

    if (addr == 0x240) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 8) & 1); // ACC main_on signal
      if (acc_main_on_prev != acc_main_on)
      {
        disengageFromBrakes = false;
        controls_allowed = 0;
      }
      acc_main_on_prev = acc_main_on;
    }

    // sample wheel speed, averaging opposite corners
    if (addr == 0x13a) {
      int subaru_speed = (GET_BYTES_04(to_push) >> 12) & 0x1FFF;  // FR
      subaru_speed += (GET_BYTES_48(to_push) >> 6) & 0x1FFF;  // RL
      subaru_speed /= 2;
      vehicle_moving = subaru_speed > SUBARU_STANDSTILL_THRSLD;
    }

    if (addr == 0x13c) {
      brake_pressed = ((GET_BYTE(to_push, 7) >> 6) & 1);
    }
    // exit controls on rising edge of brake press
    if (brake_pressed && (!brake_pressed_prev || vehicle_moving)) {
      controls_allowed = 0;
    }
    brake_pressed_prev = brake_pressed;
  }

  if (valid && (GET_BUS(to_push) == 0)) {
    if (addr == 0x40) {
      gas_pressed = GET_BYTE(to_push, 4) != 0;
    }
    // exit controls on rising edge of gas press
    if (gas_pressed && !gas_pressed_prev && !(unsafe_mode & UNSAFE_DISABLE_DISENGAGE_ON_GAS)) {
      controls_allowed = 0;
    }
    gas_pressed_prev = gas_pressed;

    // check if stock ECU is on bus broken by car harness
    if (addr == 0x122) {
      if (safety_mode_cnt > RELAY_TRNS_TIMEOUT) {
        relay_malfunction_set();
      }
    }
  }
  return valid;
}

static int subaru_gen2_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  int tx = 1;
  int addr = GET_ADDR(to_send);

  if (!msg_allowed(to_send, SUBARU_GEN2_TX_MSGS, SUBARU_GEN2_TX_MSGS_LEN)) {
    tx = 0;
  }

  if (relay_malfunction) {
    tx = 0;
  }

  // steer cmd checks
  if (addr == 0x122) {
    int desired_torque = ((GET_BYTES_04(to_send) >> 16) & 0x1FFF);
    bool violation = 0;
    uint32_t ts = microsecond_timer_get();

    desired_torque = -1 * to_signed(desired_torque, 13);

    if (controls_allowed) {

      // *** global torque limit check ***
      violation |= max_limit_check(desired_torque, SUBARU_MAX_STEER, -SUBARU_MAX_STEER);

      // *** torque rate limit check ***
      violation |= driver_limit_check(desired_torque, desired_torque_last, &torque_driver,
        SUBARU_MAX_STEER, SUBARU_MAX_RATE_UP, SUBARU_MAX_RATE_DOWN,
        SUBARU_DRIVER_TORQUE_ALLOWANCE, SUBARU_DRIVER_TORQUE_FACTOR);

      // used next time
      desired_torque_last = desired_torque;

      // *** torque real time rate limit check ***
      violation |= rt_rate_limit_check(desired_torque, rt_torque_last, SUBARU_MAX_RT_DELTA);

      // every RT_INTERVAL set the new limits
      uint32_t ts_elapsed = get_ts_elapsed(ts, ts_last);
      if (ts_elapsed > SUBARU_RT_INTERVAL) {
        rt_torque_last = desired_torque;
        ts_last = ts;
      }
    }

    // no torque if controls is not allowed
    if (!controls_allowed && (desired_torque != 0)) {
      violation = 1;
    }

    // reset to 0 if either controls is not allowed or there's a violation
    if (violation || !controls_allowed) {
      desired_torque_last = 0;
      rt_torque_last = 0;
      ts_last = ts;
    }

    if (violation) {
      tx = 0;
    }

  }
  return tx;
}


static int subaru_gen2_fwd_hook(int bus_num, CAN_FIFOMailBox_TypeDef *to_fwd) {
  int bus_fwd = -1;
  int addr = GET_ADDR(to_fwd);

  if (!relay_malfunction) {
    if (bus_num == 0) {
      // Global platform
      // 0x40 Throttle
      // 0x139 Brake_Pedal
      int block_msg = ((addr == 0x40) || (addr == 0x139));
      if (!block_msg) {
        bus_fwd = 2;  // Camera CAN
      }
    }
    if (bus_num == 2) {
      // Global platform
      // 0x122 ES_LKAS
      // 0x321 ES_DashStatus
      // 0x322 ES_LKAS_State
      int block_msg = ((addr == 0x122) || (addr == 0x321) || (addr == 0x322));
      if (!block_msg) {
        bus_fwd = 0;  // Main CAN
      }
    }
  }
  // fallback to do not forward
  return bus_fwd;
}

// hybrid
static int subaru_hybrid_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  bool valid = addr_safety_check(to_push, &subaru_hybrid_rx_checks,
                            subaru_get_checksum, subaru_compute_checksum, subaru_get_counter);
  int addr = GET_ADDR(to_push);

  if (valid && (GET_BUS(to_push) == 0)) {
    if (addr == 0x119) {
      int torque_driver_new;
      torque_driver_new = ((GET_BYTES_04(to_push) >> 16) & 0x7FF);
      torque_driver_new = -1 * to_signed(torque_driver_new, 11);
      update_sample(&torque_driver, torque_driver_new);
    }

    // sample subaru wheel speed, averaging opposite corners (Wheel_Speeds)
    if (addr == 0x13a) {
      int subaru_speed = (GET_BYTES_04(to_push) >> 12) & 0x1FFF;  // FR
      subaru_speed += (GET_BYTES_48(to_push) >> 6) & 0x1FFF;  // RL
      subaru_speed /= 2;
      vehicle_moving = subaru_speed > SUBARU_STANDSTILL_THRSLD;
    }

    // check if stock ECU is on bus broken by car harness
    if ((safety_mode_cnt > RELAY_TRNS_TIMEOUT) && (addr == 0x122)) {
      relay_malfunction_set();
    }
  }

/*
  if (valid && (GET_BUS(to_push) == 1)) {

    // exit controls on rising edge of brake press (Brake_Hybrid)
    if (addr == 0x226) {
      brake_pressed = ((GET_BYTES_48(to_push) >> 5) & 1);
      if (brake_pressed && (!brake_pressed_prev || vehicle_moving)) {
        controls_allowed = 0;
      }
      brake_pressed_prev = brake_pressed;
    }

    // exit controls on rising edge of gas press (Throttle_Hybrid)
    if (addr == 0x168) {
      gas_pressed = GET_BYTE(to_push, 4) != 0;
      if (gas_pressed && !gas_pressed_prev && !(unsafe_mode & UNSAFE_DISABLE_DISENGAGE_ON_GAS)) {
        controls_allowed = 0;
      }
      gas_pressed_prev = gas_pressed;
    }
  }
*/
  if (valid && (GET_BUS(to_push) == 2)) {

    if (addr == 0x321) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 17) & 1); // ACC main_on signal
      if (acc_main_on && !acc_main_on_prev)
      {
        controls_allowed = 1;
      }
      acc_main_on_prev = acc_main_on;
    }

    // enter controls on rising edge of ACC, exit controls on ACC off (ES_DashStatus)
    if (addr == 0x321) {
      int cruise_engaged = ((GET_BYTES_48(to_push) >> 4) & 1);
      if (cruise_engaged && !cruise_engaged_prev) {
        controls_allowed = 1;
      }
      cruise_engaged_prev = cruise_engaged;
    }

    if (addr == 0x321) {
      bool acc_main_on = ((GET_BYTES_48(to_push) >> 17) & 1); // ACC main_on signal
      if (acc_main_on_prev != acc_main_on)
      {
        disengageFromBrakes = false;
        controls_allowed = 0;
      }
      acc_main_on_prev = acc_main_on;
    }

  }

  return valid;
}


static const addr_checks* subaru_init(int16_t param) {
  disengageFromBrakes = false;
  controls_allowed = false;
  relay_malfunction_reset();
  // Checking for lower max steer from safety parameter
  subaru_max_steer_2020 = GET_FLAG(param, SUBARU_PARAM_MAX_STEER_2020);
  return &subaru_rx_checks;
}

static const addr_checks* subaru_gen2_init(int16_t param) {
  disengageFromBrakes = false;
  UNUSED(param);
  controls_allowed = false;
  relay_malfunction_reset();
  return &subaru_gen2_rx_checks;
}

static const addr_checks* subaru_hybrid_init(int16_t param) {
  disengageFromBrakes = false;
  UNUSED(param);
  controls_allowed = false;
  relay_malfunction_reset();
  return &subaru_hybrid_rx_checks;
}


const safety_hooks subaru_hooks = {
  .init = subaru_init,
  .rx = subaru_rx_hook,
  .tx = subaru_tx_hook,
  .tx_lin = nooutput_tx_lin_hook,
  .fwd = subaru_fwd_hook,
};

const safety_hooks subaru_gen2_hooks = {
  .init = subaru_gen2_init,
  .rx = subaru_gen2_rx_hook,
  .tx = subaru_gen2_tx_hook,
  .tx_lin = nooutput_tx_lin_hook,
  .fwd = subaru_gen2_fwd_hook,
};

const safety_hooks subaru_hybrid_hooks = {
  .init = subaru_hybrid_init,
  .rx = subaru_hybrid_rx_hook,
  .tx = subaru_gen2_tx_hook,
  .tx_lin = nooutput_tx_lin_hook,
  .fwd = subaru_gen2_fwd_hook,
};
