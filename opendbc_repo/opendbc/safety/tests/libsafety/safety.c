#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#define SAFETY_SET(field, val) \
  do { \
    (safety_a.state.field) = (val); \
    (safety_b.state.field) = (safety_a.state.field); \
  } while (false)

// B first, like the safety hooks
#define SAFETY_RUN(call) \
  do { \
    current_copy = &safety_b; \
    call; \
    current_copy = &safety_a; \
    call; \
  } while (false)

// TODO: time should just be passed into the hooks we expose
uint32_t timer_cnt = 0;
uint32_t timer_step = 0;
uint32_t microsecond_timer_get(void);
uint32_t microsecond_timer_get(void) {
  timer_cnt += timer_step;
  return timer_cnt;
}

#include "opendbc/safety/can.h"
#include "opendbc/safety/safety.h"
#include "opendbc/safety/ignition.h"

bool safety_config_valid() {
  if (safety_setup.current_safety_config.rx_checks_len <= 0) {
    printf("missing RX checks\n");
    return false;
  }

  for (int i = 0; i < safety_setup.current_safety_config.rx_checks_len; i++) {
    const RxStatus status = safety.rx_status[i];
    bool valid = status.msg_seen && !status.lagging && status.valid_checksum && (status.wrong_counters < MAX_WRONG_COUNTERS) && status.valid_quality_flag;
    if (!valid) {
      // printf("i %d seen %d lagging %d valid checksum %d wrong counters %d valid quality flag %d\n", i, status.msg_seen, status.lagging, status.valid_checksum, status.wrong_counters, status.valid_quality_flag);
      return false;
    }
  }
  return true;
}

int get_rx_checks_len(void) {
  return safety_setup.current_safety_config.rx_checks_len;
}

// all RX checks valid, check stale last received age us ago
void set_rx_checks_received(int stale, uint32_t age) {
  for (int i = 0; i < safety_setup.current_safety_config.rx_checks_len; i++) {
    SAFETY_SET(rx_status[i].msg_seen, true);
    SAFETY_SET(rx_status[i].valid_checksum, true);
    SAFETY_SET(rx_status[i].valid_quality_flag, true);
    SAFETY_SET(rx_status[i].wrong_counters, 0);
    SAFETY_SET(rx_status[i].last_timestamp, (i == stale) ? (timer_cnt - age) : timer_cnt);
  }
}

void set_controls_allowed(bool c){
  SAFETY_SET(controls_allowed, c);
}

void set_alternative_experience(int mode){
  safety_alternative_experience(mode);
}

void mads_apply_alternative_experience(int mode){
  SAFETY_RUN(mads_set_alternative_experience(&mode));
}

void tick_mads_state(bool vm, bool acc_main, bool op_allowed, bool braking, bool steering_disengage){
  SAFETY_RUN(mads_state_update(vm, acc_main, op_allowed, braking, steering_disengage));
}

void set_unseen_rx_checks_valid(void){
  for (int i = 0; i < safety_setup.current_safety_config.rx_checks_len; i++) {
    if (!safety.rx_status[i].msg_seen) {
      SAFETY_SET(rx_status[i].msg_seen, true);
      SAFETY_SET(rx_status[i].index, 0);
      SAFETY_SET(rx_status[i].valid_checksum, true);
      SAFETY_SET(rx_status[i].wrong_counters, 0);
      SAFETY_SET(rx_status[i].valid_quality_flag, true);
      SAFETY_SET(rx_status[i].last_timestamp, microsecond_timer_get());
      SAFETY_SET(rx_status[i].lagging, false);
    }
  }
}

int get_ignore_frequency_check_count(void){
  int count = 0;
  for (int i = 0; i < safety_setup.current_safety_config.rx_checks_len; i++) {
    for (uint8_t j = 0U; (j < MAX_ADDR_CHECK_MSGS) && (safety_setup.current_safety_config.rx_checks[i].msg[j].addr != 0U); j++) {
      if (safety_setup.current_safety_config.rx_checks[i].msg[j].ignore_frequency_check) {
        count++;
      }
    }
  }
  return count;
}

bool get_rx_check_ignore_frequency(int addr, int bus){
  bool ignore = false;
  for (int i = 0; i < safety_setup.current_safety_config.rx_checks_len; i++) {
    for (uint8_t j = 0U; (j < MAX_ADDR_CHECK_MSGS) && (safety_setup.current_safety_config.rx_checks[i].msg[j].addr != 0U); j++) {
      const CanMsgCheck *msg = &safety_setup.current_safety_config.rx_checks[i].msg[j];
      if (((int)msg->addr == addr) && ((int)msg->bus == bus) && msg->ignore_frequency_check) {
        ignore = true;
      }
    }
  }
  return ignore;
}

void set_relay_malfunction(bool c){
  SAFETY_SET(relay_malfunction, c);
}

bool get_controls_allowed(void){
  return safety.controls_allowed;
}

bool get_ignition_can(void){
  return ignition_can;
}

bool get_relay_malfunction(void){
  return safety.relay_malfunction;
}

bool get_gas_pressed_prev(void){
  return safety.gas_pressed_prev;
}

void set_gas_pressed_prev(bool c){
  SAFETY_SET(gas_pressed_prev, c);
}

bool get_brake_pressed_prev(void){
  return safety.brake_pressed_prev;
}

bool get_regen_braking_prev(void){
  return safety.regen_braking_prev;
}

bool get_steering_disengage_prev(void){
  return safety.steering_disengage_prev;
}

bool get_cruise_engaged_prev(void){
  return safety.cruise_engaged_prev;
}

void set_cruise_engaged_prev(bool engaged){
  SAFETY_SET(cruise_engaged_prev, engaged);
}

bool get_vehicle_moving(void){
  return safety.vehicle_moving;
}

bool get_acc_main_on(void){
  return safety.acc_main_on;
}

float get_vehicle_speed_min(void){
  return safety.vehicle_speed.min / VEHICLE_SPEED_FACTOR;
}

float get_vehicle_speed_max(void){
  return safety.vehicle_speed.max / VEHICLE_SPEED_FACTOR;
}

int get_current_safety_mode(void){
  return safety_setup.current_safety_mode;
}

int get_current_safety_param(void){
  return safety_setup.current_safety_param;
}

void set_timer(uint32_t t){
  timer_cnt = t;
}

void set_timer_step(uint32_t s){
  timer_step = s;
}

void set_torque_meas(int min, int max){
  SAFETY_SET(torque_meas.min, min);
  SAFETY_SET(torque_meas.max, max);
}

int get_torque_meas_min(void){
  return safety.torque_meas.min;
}

int get_torque_meas_max(void){
  return safety.torque_meas.max;
}

void set_torque_driver(int min, int max){
  SAFETY_SET(torque_driver.min, min);
  SAFETY_SET(torque_driver.max, max);
}

int get_torque_driver_min(void){
  return safety.torque_driver.min;
}

int get_torque_driver_max(void){
  return safety.torque_driver.max;
}

void set_rt_torque_last(int t){
  SAFETY_SET(rt_torque_last, t);
}

void set_desired_torque_last(int t){
  SAFETY_SET(desired_torque_last, t);
}

void set_desired_angle_last(int t){
  SAFETY_SET(desired_angle_last, t);
}

void set_angle_meas(int min, int max){
  SAFETY_SET(angle_meas.min, min);
  SAFETY_SET(angle_meas.max, max);
}

int get_angle_meas_min(void){
  return safety.angle_meas.min;
}

int get_angle_meas_max(void){
  return safety.angle_meas.max;
}

void set_desired_curvature_last(int t){
  SAFETY_SET(curvature_state.desired_last, t);
}

int get_desired_curvature_last(void){
  return safety.curvature_state.desired_last;
}

void set_curvature_meas(int min, int max){
  SAFETY_SET(curvature_state.meas.min, min);
  SAFETY_SET(curvature_state.meas.max, max);
}

int get_curvature_meas_min(void){
  return safety.curvature_state.meas.min;
}

int get_curvature_meas_max(void){
  return safety.curvature_state.meas.max;
}


// ***** car specific helpers *****

void set_honda_alt_brake_msg(bool c){
  safety_a.setup.honda_alt_brake_msg = c;
  safety_b.setup.honda_alt_brake_msg = c;
}

void set_honda_fwd_brake(bool c){
  SAFETY_SET(honda_fwd_brake, c);
}

bool get_honda_fwd_brake(void){
  return safety.honda_fwd_brake;
}

static MADSState *get_mads_state(void) {
  return &safety.m_mads_state;
}

bool get_controls_allowed_lateral(void){
  return safety.controls_allowed_lateral;
}

bool get_controls_requested_lateral(void){
  return get_mads_state()->controls_requested_lateral;
}

bool get_enable_mads(void){
  return get_mads_state()->system_enabled;
}

bool get_disengage_lateral_on_brake(void){
  return get_mads_state()->disengage_lateral_on_brake;
}

bool get_pause_lateral_on_brake(void){
  return get_mads_state()->pause_lateral_on_brake;
}

void set_acc_main_on(bool c){
  SAFETY_SET(acc_main_on, c);
}

void set_current_safety_param_sp(uint16_t param){
  safety_param_sp(param);
}

uint32_t get_acc_main_on_mismatches(void) {
  return safety.hyundai_acc_main_on_mismatches;
}

uint16_t get_current_safety_param_sp(void){
  return safety_setup.current_safety_param_sp;
}

void set_mads_button_press(int c){
  SAFETY_SET(mads_button_press, c);
}

int get_mads_button_press(void){
  return safety.mads_button_press;
}

void set_controls_allowed_lateral(bool c){
  SAFETY_SET(controls_allowed_lateral, c);
}

bool get_mads_acc_main(void){
  return safety.m_mads_state.acc_main.current;
}

int mads_get_current_disengage_reason(void) {
  return get_mads_state()->current_disengage.active_reason;
}

void mads_set_current_disengage_reason(int reason) {
  SAFETY_SET(m_mads_state.current_disengage.active_reason, reason);
}

void set_controls_requested_lateral(bool c){
  SAFETY_SET(m_mads_state.controls_requested_lateral, c);
}

void set_mads_params(bool enable_mads, bool disengage_lateral_on_brake, bool pause_lateral_on_brake){
  int alt_exp = 0;
  if (enable_mads) {
    alt_exp |= ALT_EXP_ENABLE_MADS;

    if (disengage_lateral_on_brake) {
      alt_exp |= ALT_EXP_MADS_DISENGAGE_LATERAL_ON_BRAKE;
    } else if (pause_lateral_on_brake) {
      alt_exp |= ALT_EXP_MADS_PAUSE_LATERAL_ON_BRAKE;
    } else {
    }
  }

  safety_alternative_experience(alt_exp);
  safety_mads_alternative_experience();
}

void set_heartbeat_engaged_mads(bool c){
  safety_heartbeat_mads(c);
}

// without the controls_allowed check of safety_heartbeat_check
void mads_heartbeat_check(void){
  SAFETY_RUN(mads_heartbeat_engaged_check());
}

void set_heartbeat_engaged_mismatches(uint32_t c){
  SAFETY_SET(heartbeat_engaged_mismatches, c);
}

uint32_t get_heartbeat_engaged_mismatches(void){
  return safety.heartbeat_engaged_mismatches;
}

void set_steering_disengage(bool c){
  SAFETY_SET(steering_disengage, c);
}

int get_gas_interceptor_prev(void){
  return safety.gas_interceptor_prev;
}

// a deeper frame of junk on the stack the next call at this depth reuses
void dirty_stack(void){
  volatile uint8_t junk[4096];
  for (int i = 0; i < 4096; i++) {
    junk[i] = 0xA5U;
  }
  (void)junk[0];
}

int set_safety_hooks_dirty_stack(uint16_t mode, uint16_t param){
  dirty_stack();
  return set_safety_hooks(mode, param);
}

void init_tests(void){
  SAFETY_SET(safety_mode_cnt, 2U);  // avoid ignoring relay_malfunction logic
  safety_alternative_experience(0);
  safety_param_sp(0);
  set_timer(0);
  timer_step = 0;
  SAFETY_SET(ts_steer_req_mismatch_last, 0);
  SAFETY_SET(valid_steer_req_count, 0);
  SAFETY_SET(invalid_steer_req_count, 0);

  // assumes autopark on safety mode init to avoid a fault. get rid of that for testing
  SAFETY_SET(tesla_autopark, false);

  ignition_can_reset();

  safety_redundancy_fault = false;

  // reset MADS state to prevent leaking between tests
  SAFETY_RUN(mads_set_system_state(false, false, false));
  SAFETY_SET(mads_button_press, MADS_BUTTON_UNAVAILABLE);
  safety_heartbeat_mads(false);
  SAFETY_SET(heartbeat_engaged_mads_mismatches, 0U);
}
