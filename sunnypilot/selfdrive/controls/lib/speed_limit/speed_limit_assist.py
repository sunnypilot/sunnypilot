"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time

from cereal import custom, car
from openpilot.common.params import Params
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import PCM_LONG_REQUIRED_MAX_SET_SPEED, CONFIRM_SPEED_THRESHOLD
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode, UpshiftAccept
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers import compare_cluster_target, set_speed_limit_assist_availability, \
  get_min_cap_floor

ButtonType = car.CarState.ButtonEvent.Type
EventNameSP = custom.OnroadEventSP.EventName
SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState
AssistDisableReason = custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason
SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimit.Source

ACTIVE_STATES = (SpeedLimitAssistState.active, SpeedLimitAssistState.adapting)
ENABLED_STATES = (SpeedLimitAssistState.preActive, SpeedLimitAssistState.pending, *ACTIVE_STATES)
CAP_ACTIVE_STATES = (SpeedLimitAssistState.capping,)
CAP_ENABLED_STATES = CAP_ACTIVE_STATES  # cap mode has no partially-engaged state

DISABLED_GUARD_PERIOD = 0.5  # secs.
# secs. Time to wait after activation before considering temp deactivation signal.
PRE_ACTIVE_GUARD_PERIOD = {
  True: 15,
  False: 5,
}
SPEED_LIMIT_CHANGED_HOLD_PERIOD = 1  # secs. Time to wait after speed limit change before switching to preActive.
CAP_RAISE_HOLD_PERIOD = 0.2  # secs. Time to confirm limit raise before upshifting.
CAP_SUSPEND_GUARD_PERIOD = 1.0  # secs. Time to hold cap disabled after long_override release.
USER_PAUSE_TIMEOUT_TICKS = 6000  # 5 min / DT_MDL (0.05 s) = 6000 ticks
RESUME_CLUSTER_DELTA_THRESHOLD = 1  # integer display-unit delta (kph or mph)

LIMIT_MIN_ACC = -1.5  # m/s^2 Maximum deceleration allowed for limit controllers to provide.
LIMIT_MAX_ACC = 1.0   # m/s^2 Maximum acceleration allowed for limit controllers to provide while active.
LIMIT_MIN_SPEED = 8.33  # m/s, Minimum speed limit to provide as solution on limit controllers.
LIMIT_SPEED_OFFSET_TH = -1.  # m/s Maximum offset between speed limit and current speed for adapting state.
V_CRUISE_UNSET = 255.

CRUISE_BUTTONS_PLUS = (ButtonType.accelCruise, ButtonType.resumeCruise)
CRUISE_BUTTONS_MINUS = (ButtonType.decelCruise, ButtonType.setCruise)
CRUISE_BUTTON_CONFIRM_HOLD = 0.5  # secs.


class SpeedLimitAssist:
  _speed_limit_final_last: float
  _distance: float
  v_ego: float
  a_ego: float
  v_offset: float
  cap_delta: float

  def __init__(self, CP: car.CarParams, CP_SP: custom.CarParamsSP):
    self.params = Params()
    self.CP = CP
    self.CP_SP = CP_SP
    self.frame = -1
    self.long_engaged_timer = 0
    self.pre_active_timer = 0
    self.is_metric = self.params.get_bool("IsMetric")
    set_speed_limit_assist_availability(self.CP, self.CP_SP, self.params)
    self.enabled = self.params.get("SpeedLimitMode", return_default=True) == Mode.assist
    self.long_enabled = False
    self.long_enabled_prev = False
    self.long_override = False
    self.is_enabled = False
    self.is_active = False
    self.output_v_target = V_CRUISE_UNSET
    self.output_a_target = 0.
    self.cap_delta = 0.0
    self.v_ego = 0.
    self.a_ego = 0.
    self.v_offset = 0.
    self.target_set_speed_conv = 0
    self.prev_target_set_speed_conv = 0
    self.v_cruise_cluster = 0.
    self.v_cruise_cluster_prev = 0.
    self.v_cruise_cluster_conv = 0
    self.prev_v_cruise_cluster_conv = 0
    self._has_speed_limit = False
    self._speed_limit = 0.
    self._speed_limit_final_last = 0.
    self.speed_limit_prev = 0.
    self.speed_limit_final_last_conv = 0
    self.prev_speed_limit_final_last_conv = 0
    self._distance = 0.
    self.state = SpeedLimitAssistState.disabled
    self._state_prev = SpeedLimitAssistState.disabled
    self.pcm_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self._plus_hold = 0.
    self._minus_hold = 0.
    self._last_carstate_ts = 0.

    self._cap_change_timer = 0
    self._cap_suspended_timer = 0
    self._cap_below_floor = False
    self._target_cap = 0.0
    self._cap_upshift_pressed = False
    self._cap_upshift_release_timer = 0
    self._cap_audio_cue_fired = False
    self._cap_raise_accepted = False
    self._accel_pressed = False
    self._was_cap_suspended = False
    self._override_active_last = False
    self._min_cap_floor = get_min_cap_floor(self.params, self.is_metric)
    self._cap_upshift_accept = self.params.get("SpeedLimitUpshiftAccept", return_default=True)
    self._cap_audio_cue_enabled = bool(self.params.get("SpeedLimitCapAudioCue", return_default=True))

    self._user_paused: bool = False
    self._user_paused_timer: int = 0
    self._disable_reason = AssistDisableReason.none
    self._speed_limit_final_last_at_pause = 0.
    self.tempPaused_count = 0  # diagnostic counter for tests

    # TODO-SP: SLA's own output_a_target for planner
    self.acceleration_solutions = {
      SpeedLimitAssistState.disabled: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.preActive: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.pending: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitAssistState.active: self.get_active_state_target_acceleration,
      SpeedLimitAssistState.capping: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.tempPaused: self.get_current_acceleration_as_target,
    }

  @property
  def disable_reason(self):
    return self._disable_reason

  @property
  def _gates_pass(self) -> bool:
    return self.long_enabled and self.enabled

  @property
  def _cap_gates_pass(self) -> bool:
    return self._gates_pass and not self.long_override and self._cap_suspended_timer <= 0

  @property
  def _cap_entry_ready(self) -> bool:
    return self._has_speed_limit and not self._cap_below_floor

  @property
  def speed_limit_changed(self) -> bool:
    return self._has_speed_limit and bool(self._speed_limit != self.speed_limit_prev)

  @property
  def v_cruise_cluster_changed(self) -> bool:
    return bool(self.v_cruise_cluster_conv != self.prev_v_cruise_cluster_conv)

  @property
  def target_set_speed_confirmed(self) -> bool:
    return bool(self.v_cruise_cluster_conv == self.target_set_speed_conv)

  @property
  def v_cruise_cluster_below_confirm_speed_threshold(self) -> bool:
    return bool(self.v_cruise_cluster_conv < CONFIRM_SPEED_THRESHOLD[self.is_metric])

  def update_active_event(self, events_sp: EventsSP) -> None:
    if self.v_cruise_cluster_below_confirm_speed_threshold:
      events_sp.add(EventNameSP.speedLimitChanged)
    else:
      events_sp.add(EventNameSP.speedLimitActive)

  def get_v_target_from_control(self) -> float:
    if self.pcm_op_long:
      if self.state == SpeedLimitAssistState.capping:
        return min(self.v_cruise_cluster, self._target_cap)
    else:
      if self._has_speed_limit and self.is_active:
        return self._speed_limit_final_last

    return V_CRUISE_UNSET

  # TODO-SP: SLA's own output_a_target for planner
  def get_a_target_from_control(self) -> float:
    return self.a_ego

  def update_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.is_metric = self.params.get_bool("IsMetric")
      set_speed_limit_assist_availability(self.CP, self.CP_SP, self.params)
      self.enabled = self.params.get("SpeedLimitMode", return_default=True) == Mode.assist
      self._min_cap_floor = get_min_cap_floor(self.params, self.is_metric)
      self._cap_upshift_accept = self.params.get("SpeedLimitUpshiftAccept", return_default=True)
      self._cap_audio_cue_enabled = bool(self.params.get("SpeedLimitCapAudioCue", return_default=True))

  def update_car_state(self, CS: car.CarState) -> None:
    now = time.monotonic()
    self._last_carstate_ts = now

    for b in CS.buttonEvents:
      if not b.pressed:
        if b.type in CRUISE_BUTTONS_PLUS:
          self._plus_hold = max(self._plus_hold, now + CRUISE_BUTTON_CONFIRM_HOLD)
        elif b.type in CRUISE_BUTTONS_MINUS:
          self._minus_hold = max(self._minus_hold, now + CRUISE_BUTTON_CONFIRM_HOLD)

  def _get_button_release(self, req_plus: bool, req_minus: bool) -> bool:
    now = time.monotonic()
    if req_plus and now <= self._plus_hold:
      self._plus_hold = 0.
      return True
    elif req_minus and now <= self._minus_hold:
      self._minus_hold = 0.
      return True

    # expired
    if now > self._plus_hold:
      self._plus_hold = 0.
    if now > self._minus_hold:
      self._minus_hold = 0.
    return False

  def update_calculations(self, v_cruise_cluster: float) -> None:
    speed_conv = CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH
    self.v_cruise_cluster = v_cruise_cluster

    # Update current velocity offset (error)
    self.v_offset = self._speed_limit_final_last - self.v_ego

    self.speed_limit_final_last_conv = round(self._speed_limit_final_last * speed_conv)
    self.v_cruise_cluster_conv = round(self.v_cruise_cluster * speed_conv)

    cst_low, cst_high = PCM_LONG_REQUIRED_MAX_SET_SPEED[self.is_metric]
    pcm_long_required_max = cst_low if self._has_speed_limit and self.speed_limit_final_last_conv < CONFIRM_SPEED_THRESHOLD[self.is_metric] else \
                            cst_high
    pcm_long_required_max_set_speed_conv = round(pcm_long_required_max * speed_conv)

    if self.pcm_op_long and self.state not in CAP_ACTIVE_STATES:
      self.target_set_speed_conv = pcm_long_required_max_set_speed_conv
    elif not self.pcm_op_long:
      self.target_set_speed_conv = self.speed_limit_final_last_conv
    else:
      self.target_set_speed_conv = self.v_cruise_cluster_conv

  @property
  def apply_confirm_speed_threshold(self) -> bool:
    # below CST: always require user confirmation
    if self.v_cruise_cluster_below_confirm_speed_threshold:
      return True

    # at/above CST:
    # - new speed limit >= CST: auto change
    # - new speed limit < CST: user confirmation required
    return bool(self.speed_limit_final_last_conv < CONFIRM_SPEED_THRESHOLD[self.is_metric])

  def get_current_acceleration_as_target(self) -> float:
    return self.a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    if self._distance > 0:
      return (self._speed_limit_final_last ** 2 - self.v_ego ** 2) / (2. * self._distance)

    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def get_active_state_target_acceleration(self) -> float:
    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def _update_confirmed_state(self):
    if self._has_speed_limit:
      if self.v_offset < LIMIT_SPEED_OFFSET_TH:
        self.state = SpeedLimitAssistState.adapting
      else:
        self.state = SpeedLimitAssistState.active
    else:
      self.state = SpeedLimitAssistState.pending

  def _update_non_pcm_long_confirmed_state(self) -> bool:
    if self.target_set_speed_confirmed:
      return True

    if self.state != SpeedLimitAssistState.preActive:
      return False

    req_plus, req_minus = compare_cluster_target(self.v_cruise_cluster, self._speed_limit_final_last, self.is_metric)

    return self._get_button_release(req_plus, req_minus)

  def _cap_limit_change_held(self) -> bool:
    """Return True when limit-change hold period has elapsed."""
    return self._cap_change_timer >= int(SPEED_LIMIT_CHANGED_HOLD_PERIOD / DT_MDL)

  def _cap_upshift_release_edge(self) -> bool:
    """Return True when limit-raise hold period elapsed after gas release edge."""
    if self._cap_upshift_pressed and not self._accel_pressed:
      self._cap_upshift_release_timer = int(CAP_RAISE_HOLD_PERIOD / DT_MDL)

    self._cap_upshift_pressed = self._accel_pressed

    if self._cap_upshift_release_timer > 0:
      self._cap_upshift_release_timer = max(0, self._cap_upshift_release_timer - 1)
      if self._cap_upshift_release_timer <= 0:
        return True

    return False

  def _go_disabled(self, reason: 'AssistDisableReason') -> None:
    """Transition to disabled state with given reason."""
    self._cap_raise_accepted = False
    self.state = SpeedLimitAssistState.disabled
    self._disable_reason = reason

  def _should_exit_temp_pause(self) -> bool:
    """Check if conditions warrant exiting temp pause state."""
    limit_changed = self._speed_limit_final_last != self._speed_limit_final_last_at_pause
    timer_expired = self._user_paused_timer <= 0
    cluster_realigned = abs(self.v_cruise_cluster_conv - self.speed_limit_final_last_conv) <= RESUME_CLUSTER_DELTA_THRESHOLD
    return limit_changed or timer_expired or cluster_realigned

  def update_state_machine_cap(self, events_sp: EventsSP) -> tuple[bool, bool]:
    """Cap mode FSM for pcm_op_long cars. Returns (enabled, active)."""
    # Bookkeeping: timers, override flags (unchanged)
    self._cap_change_timer = min(self._cap_change_timer + 1,
                                 int((SPEED_LIMIT_CHANGED_HOLD_PERIOD + 1) / DT_MDL))
    self._cap_upshift_release_timer = max(0, self._cap_upshift_release_timer - 1)
    self._user_paused_timer = max(0, self._user_paused_timer - 1)

    if self._override_active_last and not self.long_override and self._was_cap_suspended:
      self._cap_suspended_timer = int(CAP_SUSPEND_GUARD_PERIOD / DT_MDL)
    elif not self.long_override:
      self._cap_suspended_timer = max(0, self._cap_suspended_timer - 1)

    self._override_active_last = self.long_override

    self._cap_below_floor = self._has_speed_limit and self._speed_limit_final_last < self._min_cap_floor

    # Gate checks FIRST: apply to all non-disabled states (including tempPaused)
    if self.state != SpeedLimitAssistState.disabled:
      if not self._gates_pass:
        self._go_disabled(AssistDisableReason.gateDisabled)
        self._was_cap_suspended = False
        self._cap_suspended_timer = 0
      elif self.long_override:
        self._go_disabled(AssistDisableReason.longOverride)
        self._was_cap_suspended = True

      # Sub-state dispatch (only if gates passed)
      elif self.state == SpeedLimitAssistState.tempPaused:
        # Exit conditions: speed limit changed, timer expired, or cluster delta returns
        if self._should_exit_temp_pause():
          self._user_paused = False
          self._user_paused_timer = 0
          self._go_disabled(AssistDisableReason.autoResume)

      elif self.state == SpeedLimitAssistState.capping:
        # Cluster delta entry: user nudged cruise control away from limit
        if self.v_cruise_cluster_changed:
          self._user_paused = True
          self._user_paused_timer = USER_PAUSE_TIMEOUT_TICKS
          self._speed_limit_final_last_at_pause = self._speed_limit_final_last
          self.state = SpeedLimitAssistState.tempPaused
          self._disable_reason = AssistDisableReason.userTempPause
        elif not self._has_speed_limit:
          self._cap_raise_accepted = False
          self.state = SpeedLimitAssistState.pending
          self._disable_reason = AssistDisableReason.mapGap
        elif self._cap_below_floor:
          self._cap_raise_accepted = False
          self.state = SpeedLimitAssistState.pending
          self._disable_reason = AssistDisableReason.belowFloor
        elif self._speed_limit_final_last != self._target_cap and self._cap_limit_change_held():
          old_cap = self._target_cap
          self._target_cap = self._speed_limit_final_last
          self._cap_change_timer = 0
          self._cap_raise_accepted = False
          if self._target_cap > old_cap:
            if self._cap_upshift_accept == UpshiftAccept.NEVER_RAISE:
              self._target_cap = old_cap
            elif self._cap_upshift_accept == UpshiftAccept.ACCEL_PEDAL:
              if not self._accel_pressed:
                self._cap_raise_accepted = True
              else:
                self._target_cap = old_cap
            else:
              self._cap_upshift_release_edge()
          else:
            self._cap_upshift_release_edge()
        else:
          self._cap_upshift_release_edge()

      elif self.state == SpeedLimitAssistState.pending:
        if self._cap_entry_ready:
          if not self._was_cap_suspended:
            self._target_cap = self._speed_limit_final_last
          self._cap_change_timer = 0
          self._cap_audio_cue_fired = False
          self._cap_raise_accepted = False
          self._disable_reason = AssistDisableReason.none
          self.state = SpeedLimitAssistState.capping

    else:
      # Disabled-entry logic: if gates pass + cap_suspended_timer clear, enter capping/pending
      if self._cap_gates_pass:
        if self._cap_entry_ready:
          if not self._was_cap_suspended:
            self._target_cap = self._speed_limit_final_last
          self._cap_change_timer = 0
          self._cap_audio_cue_fired = False
          self._disable_reason = AssistDisableReason.none
          self.state = SpeedLimitAssistState.capping
        else:
          self._disable_reason = AssistDisableReason.mapGap if not self._has_speed_limit else AssistDisableReason.belowFloor
          self.state = SpeedLimitAssistState.pending

    # Audio cue on capping entry
    if self.state == SpeedLimitAssistState.capping and self._state_prev != SpeedLimitAssistState.capping:
      # suppress audio cue on override-release re-entry
      if self._cap_audio_cue_enabled and not self._was_cap_suspended:
        events_sp.add(EventNameSP.speedLimitCapActive)
        self._cap_audio_cue_fired = True
      self._was_cap_suspended = False

    enabled = self.state in CAP_ENABLED_STATES
    active = self.state in CAP_ACTIVE_STATES

    return enabled, active

  def update_state_machine_non_pcm_long(self):
    self.long_engaged_timer = max(0, self.long_engaged_timer - 1)
    self.pre_active_timer = max(0, self.pre_active_timer - 1)

    # ACTIVE, ADAPTING, PENDING, PRE_ACTIVE, INACTIVE
    if self.state != SpeedLimitAssistState.disabled:
      if not self.long_enabled or not self.enabled:
        self.state = SpeedLimitAssistState.disabled

      else:
        # ACTIVE
        if self.state == SpeedLimitAssistState.active:
          if self.v_cruise_cluster_changed:
            self.state = SpeedLimitAssistState.inactive

          elif self.speed_limit_changed and self.apply_confirm_speed_threshold:
            self.state = SpeedLimitAssistState.preActive
            self.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD[self.pcm_op_long] / DT_MDL)

        # PRE_ACTIVE
        elif self.state == SpeedLimitAssistState.preActive:
          if self._update_non_pcm_long_confirmed_state():
            self.state = SpeedLimitAssistState.active
          elif self.pre_active_timer <= 0:
            # Timeout - session ended
            self.state = SpeedLimitAssistState.inactive

        # INACTIVE
        elif self.state == SpeedLimitAssistState.inactive:
          if self.speed_limit_changed:
            self.state = SpeedLimitAssistState.preActive
            self.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD[self.pcm_op_long] / DT_MDL)
          elif self._update_non_pcm_long_confirmed_state():
            self.state = SpeedLimitAssistState.active

    # DISABLED
    elif self.state == SpeedLimitAssistState.disabled:
      if self.long_enabled and self.enabled:
        # start or reset preActive timer if initially enabled or manual set speed change detected
        if not self.long_enabled_prev or self.v_cruise_cluster_changed:
          self.long_engaged_timer = int(DISABLED_GUARD_PERIOD / DT_MDL)

        elif self.long_engaged_timer <= 0:
          if self._update_non_pcm_long_confirmed_state():
            self.state = SpeedLimitAssistState.active
          elif self._has_speed_limit:
            self.state = SpeedLimitAssistState.preActive
            self.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD[self.pcm_op_long] / DT_MDL)
          else:
            self.state = SpeedLimitAssistState.inactive

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES

    return enabled, active

  def update_events(self, events_sp: EventsSP) -> None:
    if not self.pcm_op_long and self.state == SpeedLimitAssistState.preActive:
      events_sp.add(EventNameSP.speedLimitPreActive)

    if self.state == SpeedLimitAssistState.pending and self._state_prev != SpeedLimitAssistState.pending:
      events_sp.add(EventNameSP.speedLimitPending)

    if not self.pcm_op_long and self.is_active:
      if self._state_prev not in ACTIVE_STATES:
        self.update_active_event(events_sp)

      # only notify if we acquire a valid speed limit
      # do not check has_speed_limit here
      elif self._speed_limit != self.speed_limit_prev:
        if self.speed_limit_prev <= 0:
          self.update_active_event(events_sp)
        elif self.speed_limit_prev > 0 and self._speed_limit > 0:
          self.update_active_event(events_sp)

  def update(self, long_enabled: bool, long_override: bool, v_ego: float, a_ego: float, v_cruise_cluster: float, speed_limit: float,
             speed_limit_final_last: float, has_speed_limit: bool, distance: float, events_sp: EventsSP, accel_pressed: bool = False) -> None:
    self.long_enabled = long_enabled
    self.long_override = long_override
    self.v_ego = v_ego
    self.a_ego = a_ego

    self._has_speed_limit = has_speed_limit
    self._speed_limit = speed_limit
    self._speed_limit_final_last = speed_limit_final_last
    self._distance = distance
    self._accel_pressed = accel_pressed

    self.update_params()
    self.update_calculations(v_cruise_cluster)

    self._state_prev = self.state
    if self.pcm_op_long:
      self.is_enabled, self.is_active = self.update_state_machine_cap(events_sp)
    else:
      self.is_enabled, self.is_active = self.update_state_machine_non_pcm_long()

    self.update_events(events_sp)

    # Update change tracking variables
    self.speed_limit_prev = self._speed_limit
    self.v_cruise_cluster_prev = self.v_cruise_cluster
    self.long_enabled_prev = self.long_enabled
    self.prev_target_set_speed_conv = self.target_set_speed_conv
    self.prev_v_cruise_cluster_conv = self.v_cruise_cluster_conv
    self.prev_speed_limit_final_last_conv = self.speed_limit_final_last_conv

    self.output_v_target = self.get_v_target_from_control()
    self.output_a_target = self.get_a_target_from_control()

    if self.pcm_op_long and self.state == SpeedLimitAssistState.capping:
      self.cap_delta = max(0.0, self.v_cruise_cluster - self._target_cap)
    else:
      self.cap_delta = 0.0

    self.frame += 1
