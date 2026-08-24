#!/usr/bin/env python3
import numpy as np

import openpilot.cereal.messaging as messaging
from opendbc.car.structs import car
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.accel_boost import AccelBoost
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc, LongitudinalPlanSource
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, get_accel_from_plan, should_stop
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import (
  LongitudinalPlannerSP,
  LongitudinalPlanSource as SpeedLimitPlanSource,
  limit_speed_limit_decel_target,
  no_lead_normal_decel_idle_active,
  speed_limit_current_limit_decel_needed,
  speed_limit_idle_active,
  speed_limit_no_brake_accel_target,
  speed_limit_no_brake_active,
)
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.slc_config import (
  get_longitudinal_no_lead_idle_min_decel,
  get_longitudinal_no_lead_idle_decel_cooldown_s,
  get_longitudinal_no_lead_idle_overspeed_margin_kph,
  get_longitudinal_no_lead_decel_mode,
  get_slc_no_brake,
  get_slc_no_brake_accel,
  get_slc_no_brake_mode,
  get_slc_no_brake_release_gap_kph,
  get_slc_speed_limit_max_decel,
)

# v_ego speed lookup table in m/s: 0, 10, 36, 90, 144 kph.
J_CRUISE_BP = [0., 2.8, 10.0, 25., 40.]
# Max target acceleration change rate in m/s^3 at the speeds above.
J_CRUISE_VALS = [1.0, 0.95, 0.65, 0.4, 0.3]
A_CRUISE_MIN = -0.5
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
MIN_ALLOW_THROTTLE_SPEED = 2.5
CRUISE_TARGET_CHANGE_MIN_KPH = 0.1
LONGITUDINAL_IDLE_REENTRY_BLOCK_FRAMES = int(1.0 / DT_MDL)
ButtonType = car.CarState.ButtonEvent.Type
CRUISE_TARGET_DOWN_BUTTONS = (ButtonType.decelCruise, ButtonType.setCruise)
CRUISE_TARGET_UP_BUTTONS = (ButtonType.accelCruise, ButtonType.resumeCruise)


def get_cruise_accel(v_cruise, v_ego, a_cruise_prev, dt):
  target_accel = np.clip(v_cruise - v_ego, A_CRUISE_MIN, ACCEL_MAX)
  j_cruise = np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS)
  target_accel = float(np.clip(target_accel, a_cruise_prev - j_cruise * dt, a_cruise_prev + j_cruise * dt))

  return target_accel


def get_coast_accel(pitch):
  return np.sin(pitch) * -5.65 - 0.3


class LongitudinalPlanner(LongitudinalPlannerSP):
  def __init__(self, CP, CP_SP, init_v=0.0, init_a=0.0, dt=DT_MDL):
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    LongitudinalPlannerSP.__init__(self, self.CP, CP_SP, self.mpc)
    self.fcw = False
    self.dt = dt
    self.accel_boost = AccelBoost()
    self.speed_limit_no_brake = get_slc_no_brake()
    self.longitudinal_idle = False
    self.longitudinal_idle_block_frames = 0
    self.no_lead_idle_target = 0.
    self.v_cruise_kph_prev = V_CRUISE_UNSET

    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.a_cruise = init_a
    self.output_a_target = init_a
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)

  def update(self, sm):
    LongitudinalPlannerSP.update(self, sm)
    self.speed_limit_no_brake = get_slc_no_brake()

    accel_coast = get_coast_accel(sm['carControl'].orientationNED[1]) if len(sm['carControl'].orientationNED) == 3 else 0.

    v_ego = sm['carState'].vEgo
    v_cruise_kph = min(sm['carState'].vCruise, V_CRUISE_MAX)
    v_cruise_raw = v_cruise_kph * CV.KPH_TO_MS
    v_cruise = v_cruise_raw
    if sm['controlsState'].forceDecel:
      v_cruise = 0.0

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    v_cruise_initialized = sm['carState'].vCruise != V_CRUISE_UNSET
    reset_state = reset_state or not v_cruise_initialized
    cruise_down_pressed = any(b.pressed and b.type in CRUISE_TARGET_DOWN_BUTTONS for b in sm['carState'].buttonEvents)
    cruise_up_pressed = any(b.pressed and b.type in CRUISE_TARGET_UP_BUTTONS for b in sm['carState'].buttonEvents)
    cruise_target_decreased = (
      v_cruise_initialized and
      self.v_cruise_kph_prev != V_CRUISE_UNSET and
      v_cruise_kph < self.v_cruise_kph_prev - CRUISE_TARGET_CHANGE_MIN_KPH
    )
    cruise_target_increased = (
      v_cruise_initialized and
      self.v_cruise_kph_prev != V_CRUISE_UNSET and
      v_cruise_kph > self.v_cruise_kph_prev + CRUISE_TARGET_CHANGE_MIN_KPH
    )

    if reset_state:
      self.v_desired_filter.x = v_ego
      self.output_a_target = np.clip(sm['carState'].aEgo, ACCEL_MIN, ACCEL_MAX)
      self.a_cruise = self.output_a_target

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    # Get new v_cruise and a_target from Smart Cruise Control and Speed Limit Assist
    v_cruise, self.output_a_target = LongitudinalPlannerSP.update_targets(self, sm, self.v_desired_filter.x, self.output_a_target, v_cruise)
    has_lead = sm['radarState'].leadOne.present
    no_lead_decel_mode = get_longitudinal_no_lead_decel_mode()
    no_lead_idle_min_decel = get_longitudinal_no_lead_idle_min_decel()
    no_lead_idle_overspeed_margin = get_longitudinal_no_lead_idle_overspeed_margin_kph() * CV.KPH_TO_MS
    no_lead_idle_decel_block_frames = int(get_longitudinal_no_lead_idle_decel_cooldown_s() / DT_MDL)
    no_brake_mode = get_slc_no_brake_mode()
    no_brake_release_gap = get_slc_no_brake_release_gap_kph() * CV.KPH_TO_MS
    if reset_state or cruise_up_pressed or cruise_target_increased:
      self.no_lead_idle_target = 0.
      self.longitudinal_idle_block_frames = LONGITUDINAL_IDLE_REENTRY_BLOCK_FRAMES
    elif v_cruise_initialized and (cruise_down_pressed or cruise_target_decreased):
      self.no_lead_idle_target = v_cruise_raw
    elif self.no_lead_idle_target > 0. and v_ego <= self.no_lead_idle_target + no_brake_release_gap:
      self.no_lead_idle_target = 0.
    idle_reentry_blocked = self.longitudinal_idle_block_frames > 0
    no_brake_for_speed_limit = speed_limit_no_brake_active(self.speed_limit_no_brake, self.resolver.lower_lookahead_active, has_lead)
    speed_limit_idle = (
      not idle_reentry_blocked and
      no_brake_for_speed_limit and
      v_ego > MIN_ALLOW_THROTTLE_SPEED and
      not sm['carState'].standstill and
      not sm['carState'].brakePressed and
      not sm['carState'].gasPressed and
      speed_limit_idle_active(v_ego, self.resolver.speed_limit_final_last, no_brake_release_gap, no_brake_mode)
    )
    no_brake_accel = speed_limit_no_brake_accel_target(v_ego, self.resolver.speed_limit_final_last, no_brake_release_gap,
                                                       get_slc_no_brake_accel(), no_brake_mode,
                                                       self.resolver.distance, self.resolver.lookahead_speed_factor_down,
                                                       accel_coast, A_CRUISE_MIN)
    if no_brake_for_speed_limit:
      self.output_a_target = no_brake_accel

    self.mpc.set_weights(prev_accel_constraint, personality=sm['selfdriveState'].personality)
    if self.CP.openpilotLongitudinalControl:
      self.mpc.set_cur_state(self.v_desired_filter.x, self.output_a_target)
    else:
      self.mpc.set_cur_state(v_ego, sm['carState'].aEgo)
    self.mpc.update(sm['radarState'], personality=sm['selfdriveState'].personality)

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = self.mpc.crash_cnt > 2 and not sm['carState'].standstill
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Save starting point for next iteration
    a_prev = self.output_a_target

    action_t =  self.CP.longitudinalActuatorDelay + DT_MDL
    output_a_target_mpc = get_accel_from_plan(self.v_desired_trajectory, self.a_desired_trajectory, CONTROL_N_T_IDX,
                                              action_t=action_t)
    output_should_stop_mpc = should_stop(v_ego, output_a_target_mpc)
    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration
    output_should_stop_e2e = sm['modelV2'].action.shouldStop

    if no_brake_for_speed_limit:
      self.a_cruise = no_brake_accel
    else:
      self.a_cruise = get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.dt)
    cruise_should_stop = should_stop(v_ego, self.a_cruise)

    output_a_target_e2e = self.accel_boost.update(sm, output_a_target_e2e, output_a_target_mpc, self.a_cruise)

    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),
                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop),
                  (output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e)]

    output_a_target, selected_source, _ = min(candidates, key=lambda c: c[0])
    any_should_stop = any(should_stop for _, _, should_stop in candidates)
    speed_limit_source_active = self.source == SpeedLimitPlanSource.speedLimitAssist
    speed_limit_current_limit_decel = speed_limit_current_limit_decel_needed(speed_limit_source_active, self.resolver.lower_lookahead_active,
                                                                             v_ego, self.resolver.speed_limit_final_last,
                                                                             no_lead_idle_overspeed_margin)
    if speed_limit_current_limit_decel:
      self.longitudinal_idle_block_frames = max(self.longitudinal_idle_block_frames, no_lead_idle_decel_block_frames)
    idle_blocked = self.longitudinal_idle_block_frames > 0
    intentional_no_lead_decel = (
      self.no_lead_idle_target > 0. or
      (speed_limit_source_active and not speed_limit_current_limit_decel)
    )
    normal_decel_idle = (
      not idle_blocked and
      no_lead_normal_decel_idle_active(no_lead_decel_mode, intentional_no_lead_decel, selected_source == LongitudinalPlanSource.cruise,
                                       output_a_target, no_lead_idle_min_decel, has_lead, any_should_stop) and
      v_ego > MIN_ALLOW_THROTTLE_SPEED and
      not sm['carState'].standstill and
      not sm['carState'].brakePressed and
      not sm['carState'].gasPressed
    )
    self.longitudinal_idle = speed_limit_idle or normal_decel_idle
    if self.longitudinal_idle:
      output_a_target = 0.
    cap_speed_limit_decel = (
      not self.longitudinal_idle and
      not no_brake_for_speed_limit and
      selected_source == LongitudinalPlanSource.cruise and
      self.source == SpeedLimitPlanSource.speedLimitAssist
    )
    output_a_target = limit_speed_limit_decel_target(output_a_target, cap_speed_limit_decel,
                                                     has_lead, get_slc_speed_limit_max_decel())
    self.mpc.source = selected_source
    self.output_should_stop = any_should_stop
    self.output_a_target = np.clip(output_a_target, ACCEL_MIN, ACCEL_MAX)

    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.output_a_target + a_prev) / 2.0
    if self.longitudinal_idle_block_frames > 0:
      self.longitudinal_idle_block_frames -= 1
    self.v_cruise_kph_prev = v_cruise_kph if v_cruise_initialized else V_CRUISE_UNSET

  def publish(self, sm, pm):
    plan_send = messaging.new_message('longitudinalPlan')

    plan_send.valid = sm.all_checks()

    longitudinalPlan = plan_send.longitudinalPlan
    longitudinalPlan.modelMonoTime = sm.logMonoTime['modelV2']
    longitudinalPlan.processingDelay = (plan_send.logMonoTime / 1e9) - sm.logMonoTime['modelV2']
    longitudinalPlan.solverExecutionTime = self.mpc.solve_time

    longitudinalPlan.speeds = self.v_desired_trajectory.tolist()
    longitudinalPlan.accels = self.a_desired_trajectory.tolist()
    longitudinalPlan.jerks = self.j_desired_trajectory.tolist()

    longitudinalPlan.hasLead = sm['radarState'].leadOne.present
    longitudinalPlan.longitudinalPlanSource = self.mpc.source
    longitudinalPlan.fcw = self.fcw

    longitudinalPlan.aTarget = float(self.output_a_target)
    longitudinalPlan.accelBoost = float(self.accel_boost.total_boost)
    longitudinalPlan.shouldStop = bool(self.output_should_stop)
    longitudinalPlan.allowBrake = True

    pm.send('longitudinalPlan', plan_send)

    self.publish_longitudinal_plan_sp(sm, pm)
