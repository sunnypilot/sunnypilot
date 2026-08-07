import math

import numpy as np

from opendbc.car.interfaces import ACCEL_MAX
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalPlanSource
from openpilot.sunnypilot import get_sanitize_int_param
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  CAP_FILTER_FRAMES, COMFORT_DECEL, DEPARTURE_MOTION_NOISE_FLOOR, LAUNCH_END_SPEED, LAUNCH_TARGET_HEADROOM, LAUNCH_TARGET_SLEW,
  LEAD_BRAKING_ACCEL_THRESHOLD, LEAD_DROPOUT_COAST_TIME, LEAD_LOSS_HOLD_TIME, LEAD_MATCH_ACCEL_SLEW, LEAD_MATCH_GAP_GAIN, LEAD_MATCH_SPEED_HEADROOM,
  LEAD_SWITCH_MAX_HOLD_TIME,
  MATCHED_SPEED_DECEL_RATE, MPC_DECEL_JERK_COST_MULTIPLIER, MPC_DECEL_JERK_MAX_REQUIRED_DECEL, MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE,
  MPC_DECEL_JERK_MAX_TARGET_REDUCTION, MPC_DECEL_TREND_FRAMES, SPEED_RELIEF_DEADBAND, SPEED_RESTRICT_DEADBAND, TARGET_SPEED_ARM_MARGIN,
  TARGET_RELEASE_SLEW, TARGET_SPEED_RESERVE, PLANNER_BRAKING_ACCEL_THRESHOLD, RADAR_STALE_TIMEOUT, STOP_HOLD_CREEP_DISTANCE, STOP_HOLD_EGO_SPEED,
  STOP_HOLD_EXIT_FRAMES, STOP_HOLD_EXIT_SPEED, STOP_HOLD_MAX_LEAD_DISTANCE, VEGO_NOISE_TOLERANCE, PARAM_READ_INTERVAL, AccelProfile,
  profile_accel_max, sanitize_profile,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.helpers import build_accel_ceiling, is_valid_context
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.lead import LeadPlan, calculate_lead_plan, has_radar_lead, is_lead_source
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.state import AccelControllerState, TargetState


class AccelController:
  def __init__(self, CP, dt: float = DT_MDL):
    if not math.isfinite(dt) or dt <= 0.0:
      raise ValueError("dt must be finite and positive")

    self.dt = dt
    self.delay = float(CP.longitudinalActuatorDelay) + DT_MDL
    self.lead_loss_hold_frames = max(CAP_FILTER_FRAMES, math.ceil(LEAD_LOSS_HOLD_TIME / dt))
    self.lead_dropout_coast_frames = max(self.lead_loss_hold_frames, math.ceil(LEAD_DROPOUT_COAST_TIME / dt))
    self.lead_switch_max_hold_frames = max(self.lead_loss_hold_frames, math.ceil(LEAD_SWITCH_MAX_HOLD_TIME / dt))
    self.radar_stale_frames = max(1, math.ceil(RADAR_STALE_TIMEOUT / dt))
    self.params = Params()
    self.available = bool(CP.openpilotLongitudinalControl)
    self.enabled = False
    self.profile = AccelProfile.normal
    self._param_read_frames = max(1, int(round(PARAM_READ_INTERVAL / dt)))
    self._param_frame = 0
    self._jerk_smoothing_blocked = False
    self._required_decel_samples: list[float] = []
    self._required_decel_lead = -1
    self._required_decel_lead_track_id = -1
    self._lead_trend_warmup = False
    self._cruise_accel_limited = False
    self.target_state = TargetState()
    self._held_lead_plan: LeadPlan | None = None
    self.is_active = self.launching = self.departure_launching = False
    self.output_v_target = 0.0
    self.mpc_accel_max: tuple[float, ...] | None = None
    self.cruise_accel_max: float | None = None
    self.state = AccelControllerState.inactive
    self.selected_lead = -1
    self.selected_lead_track_id = -1
    self.required_decel = 0.0

  @property
  def is_enabled(self) -> bool:
    return self.available and self.enabled

  def update_params(self) -> None:
    if self._param_frame % self._param_read_frames == 0:
      self.enabled = self.params.get_bool("AccelPersonalityEnabled")
      self.profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._param_frame += 1

  def _update_target(self, lead_plan: LeadPlan, base_speed: float, v_ego: float, profile: int, profile_max_accel: float,
                     previous_should_stop: bool, previous_mpc_source, planner_speed: float, planner_accel: float) -> float:
    state = self.target_state
    lead_filter_ready = state.update_samples(lead_plan, self.dt)
    state.active_frames += 1
    has_lead = lead_plan.selected_lead >= 0
    filtered_cap = state.filtered_cap
    slot_changed = has_lead and state.selected_lead >= 0 and lead_plan.selected_lead != state.selected_lead
    track_changed = (has_lead and state.selected_lead >= 0 and lead_plan.selected_lead == state.selected_lead
      and lead_plan.selected_lead_track_id != state.selected_lead_track_id
      and (state.selected_lead_track_id >= 0 or lead_plan.selected_lead_track_id >= 0))
    false_relief = has_lead and math.isfinite(filtered_cap) and lead_plan.cap >= filtered_cap + SPEED_RELIEF_DEADBAND
    guarded_restriction = state.state in (AccelControllerState.restrict, AccelControllerState.hold, AccelControllerState.release)
    switched_to_relief = ((slot_changed or track_changed) and false_relief
                          and (guarded_restriction or planner_accel <= PLANNER_BRAKING_ACCEL_THRESHOLD))
    confirmed_relief = (not has_lead or (state.target_speed is not None and lead_plan.closing_speed <= 0.0
                        and lead_plan.cap >= state.target_speed + SPEED_RELIEF_DEADBAND))
    state.update_lead_switch_guard(switched_to_relief, confirmed_relief, slot_changed or track_changed or false_relief,
                                   self.lead_loss_hold_frames, self.lead_switch_max_hold_frames)
    if has_lead:
      state.selected_lead = lead_plan.selected_lead
      state.selected_lead_track_id = lead_plan.selected_lead_track_id
    elif state.lead_loss_frames >= self.lead_loss_hold_frames:
      state.reset_lead_switch_guard()
      state.selected_lead = state.selected_lead_track_id = -1
    departure_separation = (lead_plan.departure_lead_separations[lead_plan.departure_lead_index]
                            if lead_plan.departure_lead_index >= 0 else math.inf)
    stopped_lead_hold = (has_lead and lead_plan.has_nearly_stopped_lead
      and (lead_plan.departure_cap < 0.50 or (state.lead_braking and departure_separation <= STOP_HOLD_MAX_LEAD_DISTANCE)))
    invalid_lead = lead_plan.lead_status and not has_lead
    prior_lead_context = is_lead_source(previous_mpc_source) or math.isfinite(filtered_cap) or state.lead_braking
    previous_stop = previous_should_stop and prior_lead_context and (not has_lead or lead_plan.departure_lead_speed < STOP_HOLD_EXIT_SPEED)
    stop_evidence = stopped_lead_hold or lead_plan.cap < 0.50 or filtered_cap < 0.50 or (previous_stop and not state.launching) or invalid_lead
    departure_motion_confirmed = (state.launching and state.departure_launch and has_lead
      and (state.departure.progress(lead_plan, DEPARTURE_MOTION_NOISE_FLOOR) or state.departure.recent_motion()))
    if state.active_frames >= self.lead_loss_hold_frames and math.isfinite(filtered_cap) and has_lead and planner_accel <= PLANNER_BRAKING_ACCEL_THRESHOLD:
      state.lead_braking = True
    elif not has_lead and state.lead_loss_frames >= self.lead_loss_hold_frames:
      state.lead_braking = False

    if state.target_speed is None:
      e2e_handoff = previous_mpc_source == LongitudinalPlanSource.e2e
      seed_from_ego = has_lead and planner_accel > PLANNER_BRAKING_ACCEL_THRESHOLD and not e2e_handoff
      state.target_speed = min(base_speed, v_ego) if seed_from_ego else base_speed
      if seed_from_ego and v_ego >= LAUNCH_END_SPEED and lead_plan.closing_speed > 0.0:
        state.arm_release_slew()
      state.e2e_braking_handoff = e2e_handoff and planner_accel < 0.0
      state.state = AccelControllerState.free
      if v_ego < STOP_HOLD_EGO_SPEED and not stop_evidence:
        state.target_speed = min(base_speed, v_ego + LAUNCH_TARGET_HEADROOM)
        state.state = AccelControllerState.release
        state.launching = True
        state.departure_launch = False
    elif state.e2e_braking_handoff and planner_accel >= 0.0:
      state.e2e_braking_handoff = False

    state.target_speed = min(state.target_speed, base_speed)
    if v_ego < STOP_HOLD_EGO_SPEED and stop_evidence and not departure_motion_confirmed and state.state != AccelControllerState.stopHold:
      state.enter_stop_hold(lead_plan)
      return state.target_speed

    if state.state == AccelControllerState.stopHold:
      state.departure.backfill_references()
      fast_departure = (has_lead and min(lead_plan.selected_lead_speed, lead_plan.departure_lead_speed) > STOP_HOLD_EXIT_SPEED
        and lead_plan.departure_cap > STOP_HOLD_EXIT_SPEED)
      raw_departure = fast_departure or not lead_plan.lead_status and state.lead_loss_frames >= self.lead_loss_hold_frames
      departed = state.departure.progress(lead_plan, STOP_HOLD_CREEP_DISTANCE) or raw_departure
      if fast_departure and state.departure_frames == 0:
        state.departure.keep_latest_motion_sample()
      state.departure_frames = state.departure_frames + 1 if departed else 0
      state.target_speed = 0.0
      fast_departure_confirmed = fast_departure and state.departure.recent_motion()
      if state.departure_frames < STOP_HOLD_EXIT_FRAMES or fast_departure and not fast_departure_confirmed:
        return state.target_speed
      state.target_speed = base_speed
      state.state = AccelControllerState.release
      state.departure_frames = 0
      state.launching = True
      state.departure_launch = has_lead
      return state.target_speed

    if state.launching:
      renewed_stop = (has_lead and not departure_motion_confirmed
        and (lead_plan.cap < STOP_HOLD_EXIT_SPEED
             or (lead_plan.has_nearly_stopped_lead and lead_plan.departure_cap < STOP_HOLD_EXIT_SPEED)))
      guarded_departure_loss = state.departure_launch and not lead_plan.lead_status and state.lead_loss_frames < self.lead_loss_hold_frames
      if invalid_lead:
        state.launching = state.departure_launch = False
        if v_ego < STOP_HOLD_EGO_SPEED:
          state.enter_stop_hold(lead_plan)
          return state.target_speed
        state.state = AccelControllerState.hold
        return state.target_speed
      if guarded_departure_loss:
        state.state = AccelControllerState.hold
        return state.target_speed
      if state.departure_launch and not has_lead:
        state.departure_launch = False
      if renewed_stop:
        state.launching = state.departure_launch = False
        if v_ego < STOP_HOLD_EGO_SPEED:
          state.enter_stop_hold(lead_plan)
          return state.target_speed
      if state.launching:
        if state.departure_launch:
          state.target_speed = base_speed
        else:
          launch_target = min(base_speed, v_ego + LAUNCH_TARGET_HEADROOM)
          state.target_speed = min(base_speed, max(state.target_speed, launch_target) + LAUNCH_TARGET_SLEW * self.dt)
        if v_ego >= LAUNCH_END_SPEED:
          state.launching = state.departure_launch = False

    comfort_decel = COMFORT_DECEL[profile]
    if (has_lead and not state.launching and state.state == AccelControllerState.restrict
      and lead_plan.closing_speed <= 0.0 and v_ego >= state.filtered_lead_speed - VEGO_NOISE_TOLERANCE):
      state.matched_lead = True
    elif not has_lead and state.lead_loss_frames >= self.lead_loss_hold_frames:
      state.matched_lead = False

    lost_lead_source = is_lead_source(previous_mpc_source) and not has_lead and planner_speed < state.target_speed
    if not has_lead and (state.matched_lead or lost_lead_source):
      if lost_lead_source:
        state.lead_dropout = True
        state.target_speed = planner_speed
        state.arm_release_slew()
      state.state = AccelControllerState.hold
      return state.target_speed

    if state.matched_lead:
      if math.isfinite(state.filtered_lead_speed):
        recovery_speed = min(base_speed, state.filtered_lead_speed + min(LEAD_MATCH_SPEED_HEADROOM, LEAD_MATCH_GAP_GAIN * lead_plan.usable_gap))
        desired_accel_limit = min(profile_max_accel, max(recovery_speed - v_ego, 0.0))
      else:
        desired_accel_limit = 0.0
      if state.filtered_lead_accel < LEAD_BRAKING_ACCEL_THRESHOLD:
        desired_accel_limit = profile_max_accel
      if state.matched_accel_limit is None:
        state.matched_accel_limit = profile_max_accel
      if state.lead_switch_guard_frames > 0:
        desired_accel_limit = min(desired_accel_limit, state.matched_accel_limit)
      state.matched_accel_limit = min(profile_max_accel, float(np.clip(
        desired_accel_limit, state.matched_accel_limit - LEAD_MATCH_ACCEL_SLEW * self.dt,
        state.matched_accel_limit + LEAD_MATCH_ACCEL_SLEW * self.dt,
      )))
      matched_ceiling = min(base_speed, filtered_cap)
      if matched_ceiling <= state.target_speed - SPEED_RESTRICT_DEADBAND:
        state.target_speed = max(matched_ceiling, state.target_speed - MATCHED_SPEED_DECEL_RATE * self.dt)
        state.arm_release_slew()
        state.state = AccelControllerState.restrict
      elif (state.lead_switch_guard_frames == 0 and matched_ceiling >= state.target_speed + SPEED_RELIEF_DEADBAND
            and (state.lead_switch_elapsed_frames < self.lead_switch_max_hold_frames or planner_accel > PLANNER_BRAKING_ACCEL_THRESHOLD)):
        state.target_speed = min(matched_ceiling, state.target_speed + profile_max_accel * self.dt)
        state.state = AccelControllerState.free if state.target_speed >= base_speed - SPEED_RESTRICT_DEADBAND else AccelControllerState.release
      else:
        state.state = AccelControllerState.free if state.target_speed >= base_speed - SPEED_RESTRICT_DEADBAND else AccelControllerState.hold
      if state.state == AccelControllerState.free:
        state.reset_release_slew(state.target_speed)
      else:
        state.update_release_slew(matched_ceiling, math.isfinite(matched_ceiling) and state.target_speed == matched_ceiling)
      return state.target_speed
    state.matched_accel_limit = None

    ceiling = min(base_speed, filtered_cap)
    synced_to_planner = lead_filter_ready and not state.launching and planner_speed < state.target_speed
    if synced_to_planner:
      state.target_speed = max(planner_speed, state.target_speed - comfort_decel * self.dt)

    if ceiling <= state.target_speed - SPEED_RESTRICT_DEADBAND or (state.state == AccelControllerState.restrict and ceiling < state.target_speed):
      if not synced_to_planner:
        state.target_speed = max(ceiling, state.target_speed - comfort_decel * self.dt)
      state.arm_release_slew()
      state.state = AccelControllerState.restrict
      return state.target_speed

    filter_warmup = has_lead and not math.isfinite(filtered_cap)
    guarded_lead_loss = not has_lead and state.lead_loss_frames < (self.lead_dropout_coast_frames if state.lead_dropout else self.lead_loss_hold_frames)
    if (filter_warmup or guarded_lead_loss) and state.target_speed < base_speed - SPEED_RESTRICT_DEADBAND:
      state.state = AccelControllerState.hold
      return state.target_speed

    confirmed_clear_road = not math.isfinite(filtered_cap) and not guarded_lead_loss
    relief = (not has_lead or lead_plan.closing_speed <= 0.0) and planner_accel > PLANNER_BRAKING_ACCEL_THRESHOLD
    continuing_release = state.release_slew_armed and ceiling > state.target_speed
    if relief and (continuing_release or ceiling >= state.target_speed + SPEED_RELIEF_DEADBAND
                   or (confirmed_clear_road and ceiling > state.target_speed)):
      if state.lead_switch_guard_frames == 0:
        timed_out = state.lead_switch_elapsed_frames >= self.lead_switch_max_hold_frames
        if not state.release_slew_armed and (timed_out or (state.release_settle_speed is not None
                                                          and ceiling - state.target_speed > TARGET_RELEASE_SLEW * self.dt)):
          state.arm_release_slew(force=True)
        release_rate = comfort_decel if timed_out else TARGET_RELEASE_SLEW
        state.target_speed = min(ceiling, state.target_speed + release_rate * self.dt) if state.release_slew_armed else ceiling
      if state.release_slew_armed and state.target_speed < ceiling:
        state.state = AccelControllerState.release
      else:
        state.state = AccelControllerState.free if state.target_speed >= base_speed - SPEED_RESTRICT_DEADBAND else AccelControllerState.hold
    else:
      state.state = AccelControllerState.free if state.target_speed >= base_speed - SPEED_RESTRICT_DEADBAND else AccelControllerState.hold
    if state.target_speed >= base_speed:
      state.lead_dropout = False
      state.reset_release_slew(state.target_speed)
    else:
      state.update_release_slew(ceiling, math.isfinite(ceiling) and state.target_speed == ceiling)
    return state.target_speed

  def _update_freshness(self, radar_fresh: bool) -> None:
    self.target_state.stale_frames = 0 if radar_fresh else self.target_state.stale_frames + 1
    if self.target_state.stale_frames >= self.radar_stale_frames:
      self.target_state = TargetState()

  def reset(self) -> None:
    self.target_state = TargetState()
    self._held_lead_plan = None
    self._jerk_smoothing_blocked = False
    self._required_decel_samples.clear()
    self._required_decel_lead = self._required_decel_lead_track_id = -1
    self._lead_trend_warmup = False
    self._cruise_accel_limited = False
    self.is_active = self.launching = self.departure_launching = False
    self.output_v_target = 0.0
    self.mpc_accel_max = None
    self.cruise_accel_max = None
    self.state = AccelControllerState.inactive
    self.selected_lead = -1
    self.selected_lead_track_id = -1
    self.required_decel = 0.0

  def update(self, radar_state, *, base_speed: float, v_ego: float, a_ego: float, follow_personality, acc_selected: bool,
             engaged: bool, cruise_initialized: bool, stock_accel_max: float, previous_should_stop: bool, radar_fresh: bool = True,
             previous_mpc_source=None, planner_speed: float | None = None, planner_accel: float = 0.0) -> None:
    self.profile = sanitize_profile(self.profile)
    sanitized_v_ego = max(v_ego, 0.0) if math.isfinite(v_ego) and v_ego >= -VEGO_NOISE_TOLERANCE else v_ego
    profile_max_accel = profile_accel_max(self.profile, sanitized_v_ego)
    stock_accel_max = float(stock_accel_max)
    positive_accel_max = (max(0.0, min(profile_max_accel, stock_accel_max, ACCEL_MAX))
                          if math.isfinite(profile_max_accel) and math.isfinite(stock_accel_max) else math.nan)
    planner_speed = sanitized_v_ego if planner_speed is None else planner_speed
    valid_context = is_valid_context(base_speed, sanitized_v_ego, a_ego, planner_speed, planner_accel, stock_accel_max, self.delay,
                                     engaged, cruise_initialized)
    enabled_context = valid_context and self.is_enabled and bool(acc_selected)
    if enabled_context and radar_fresh:
      lead_plan = calculate_lead_plan(radar_state, sanitized_v_ego, a_ego, self.delay, self.profile, follow_personality)
      self._held_lead_plan = lead_plan
    elif enabled_context and self._held_lead_plan is not None:
      lead_plan = self._held_lead_plan
    else:
      lead_plan = LeadPlan(lead_status=has_radar_lead(radar_state))
      self._held_lead_plan = None

    if enabled_context:
      self._update_freshness(radar_fresh)
    active = enabled_context and (radar_fresh or self.target_state.target_speed is not None)
    if active and radar_fresh:
      target_speed = self._update_target(
        lead_plan, base_speed, sanitized_v_ego, self.profile, profile_max_accel, previous_should_stop,
        previous_mpc_source, planner_speed, planner_accel,
      )
    elif active:
      target_speed = self.target_state.target_speed
    else:
      self.target_state = TargetState()
      target_speed = base_speed

    if not radar_fresh and not active:
      self._held_lead_plan = None
      lead_plan = LeadPlan(lead_status=has_radar_lead(radar_state))

    state = self.target_state
    stop_hold_active = active and state.state == AccelControllerState.stopHold
    matched_limit_active = active and state.matched_lead and state.matched_accel_limit is not None and not state.e2e_braking_handoff
    lead_accel_request = active and lead_plan.selected_lead >= 0 and lead_plan.closing_speed <= 0.0 and planner_accel >= 0.0
    profile_limit_active = active and not stop_hold_active and (state.launching or not lead_plan.lead_status or lead_accel_request)
    if matched_limit_active:
      effective_accel_max = min(positive_accel_max, state.matched_accel_limit)
    elif profile_limit_active:
      effective_accel_max = positive_accel_max
    else:
      effective_accel_max = math.inf
    mpc_accel_max = build_accel_ceiling(effective_accel_max, planner_accel) if matched_limit_active or profile_limit_active else None
    guarded_lead_loss = not lead_plan.lead_status and state.selected_lead >= 0 and state.lead_loss_frames < self.lead_loss_hold_frames
    lead_context = lead_plan.lead_status or math.isfinite(state.filtered_cap) or guarded_lead_loss
    reserve_eligible = active and lead_context and not stop_hold_active and not state.launching and not state.e2e_braking_handoff
    reserve_can_arm = reserve_eligible and state.lead_switch_guard_frames == 0
    if not lead_context:
      state.speed_reserve_armed = False
    elif (reserve_can_arm and not state.speed_reserve_armed and math.isfinite(state.filtered_cap)
          and state.filtered_cap <= target_speed + TARGET_SPEED_ARM_MARGIN):
      state.speed_reserve_armed = True

    output_target = 0.0 if stop_hold_active else target_speed
    if reserve_eligible and state.speed_reserve_armed:
      output_target = max(0.0, output_target - TARGET_SPEED_RESERVE)

    self.is_active = active
    self.launching = active and state.launching
    self.departure_launching = self.launching and state.departure_launch
    self.output_v_target = output_target
    self.mpc_accel_max = mpc_accel_max
    start_cruise_accel_limit = (active and state.state == AccelControllerState.free and lead_plan.lead_status
                                and lead_plan.closing_speed > 0.0 and planner_accel >= 0.0
                                and previous_mpc_source == LongitudinalPlanSource.cruise)
    keep_cruise_accel_limit = (self._cruise_accel_limited and active and lead_context and state.state == AccelControllerState.free
                               and not state.e2e_braking_handoff)
    self._cruise_accel_limited = start_cruise_accel_limit or keep_cruise_accel_limit
    self.cruise_accel_max = positive_accel_max if self._cruise_accel_limited else None
    self.state = state.state
    self.selected_lead = lead_plan.selected_lead
    self.selected_lead_track_id = lead_plan.selected_lead_track_id
    self.required_decel = lead_plan.required_decel

  def get_jerk_cost_multiplier(self, actuating: bool, prev_accel_constraint: bool, target_reduction: float, previous_mpc_failed: bool) -> float:
    lead_restriction = (actuating and prev_accel_constraint and self.state == AccelControllerState.restrict and self.selected_lead >= 0
      and not self.launching and target_reduction > 1e-6)
    same_lead = self.selected_lead == self._required_decel_lead and self.selected_lead_track_id == self._required_decel_lead_track_id
    lead_changed = lead_restriction and self._required_decel_lead >= 0 and not same_lead
    if lead_changed:
      self._lead_trend_warmup = True
    elif not lead_restriction:
      self._lead_trend_warmup = False
    if not lead_restriction or not same_lead or not math.isfinite(self.required_decel):
      self._required_decel_samples.clear()
    if lead_restriction and math.isfinite(self.required_decel):
      self._required_decel_samples.append(self.required_decel)
      if len(self._required_decel_samples) > MPC_DECEL_TREND_FRAMES:
        self._required_decel_samples.pop(0)
    self._required_decel_lead = self.selected_lead if lead_restriction else -1
    self._required_decel_lead_track_id = self.selected_lead_track_id if lead_restriction else -1

    history = self._required_decel_samples
    history_ready = len(history) == MPC_DECEL_TREND_FRAMES
    tightening_lead = (history_ready
      and (history[-1] - history[0]) / (self.dt * (len(history) - 1)) > MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE
      and sum(after > before for before, after in zip(history[:-1], history[1:], strict=True)) >= 2)
    modest_decel = (lead_restriction and target_reduction < MPC_DECEL_JERK_MAX_TARGET_REDUCTION
      and 0.0 < self.required_decel < MPC_DECEL_JERK_MAX_REQUIRED_DECEL)
    smoothing_eligible = modest_decel and (not self._lead_trend_warmup or history_ready) and not tightening_lead
    if history_ready:
      self._lead_trend_warmup = False
    if previous_mpc_failed or (lead_restriction and not self._jerk_smoothing_blocked and (not modest_decel or tightening_lead)):
      self._jerk_smoothing_blocked = True
    elif not lead_restriction:
      self._jerk_smoothing_blocked = False
    return MPC_DECEL_JERK_COST_MULTIPLIER if smoothing_eligible and not self._jerk_smoothing_blocked else 1.0

  def update_should_stop(self, should_stop: bool) -> bool:
    if not self.is_active:
      return should_stop
    if self.departure_launching:
      return False
    return should_stop or self.state == AccelControllerState.stopHold
