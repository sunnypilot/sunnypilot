import numpy as np
import time

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V, \
  PARAMS_UPDATE_PERIOD, TEMP_INACTIVE_GUARD_PERIOD, LIMIT_SPEED_OFFSET_TH
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Policy, Engage, OffsetType
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.helpers import debug
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.state import StateMachine
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName
State = custom.LongitudinalPlanSP.SpeedLimitControlState


class SpeedLimitController:
  def __init__(self, CP: structs.CarParams):
    self._params = Params()
    self._CP = CP
    self._policy = Policy(int(self._params.get("SpeedLimitControlPolicy", encoding='utf8')))
    self._resolver = SpeedLimitResolver(self._policy)
    self._state_machine = StateMachine()
    self._last_params_update = 0.0
    self._last_op_enabled_time = 0.0
    self._is_metric = self._params.get_bool("IsMetric")
    self._enabled_toggle = self._params.get_bool("SpeedLimitControl")
    self._disengage_on_accelerator = self._params.get_bool("DisengageOnAccelerator")
    self._op_enabled = False
    self._op_enabled_prev = False
    self._v_ego = 0.
    self._a_ego = 0.
    self._v_offset = 0.
    self._v_cruise_setpoint = 0.
    self._v_cruise_setpoint_prev = 0.
    self._speed_limit = 0.
    self._speed_limit_prev = 0.
    self._distance = 0.
    self._source = Source.none
    self._gas_pressed = False
    self._pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self._offset_type = int(self._params.get("SpeedLimitOffsetType", encoding='utf8'))
    self._offset_value = float(self._params.get("SpeedLimitValueOffset", encoding='utf8'))
    self._warning_type = int(self._params.get("SpeedLimitWarningType", encoding='utf8'))
    self._warning_offset_type = int(self._params.get("SpeedLimitWarningOffsetType", encoding='utf8'))
    self._warning_offset_value = float(self._params.get("SpeedLimitWarningValueOffset", encoding='utf8'))
    self._engage_type = np.clip(int(self._params.get("SpeedLimitEngageType", encoding='utf8')), Engage.auto, Engage.user_confirm)
    self._brake_pressed = False
    self._brake_pressed_prev = False
    self._current_time = 0.
    self._ms_to_local = CV.MS_TO_KPH if self._is_metric else CV.MS_TO_MPH

    # State tracking
    self._enabled = False
    self._active = False

  @property
  def state(self) -> State:
    return self._state_machine.state

  @property
  def is_enabled(self) -> bool:
    return self._enabled and self._enabled_toggle

  @property
  def is_active(self) -> bool:
    return self._active and self._enabled_toggle

  @property
  def speed_limit_offseted(self) -> float:
    return self._speed_limit + self.speed_limit_offset

  @property
  def speed_limit_offset(self) -> float:
    if self._offset_type == OffsetType.default:
      return float(np.interp(self._speed_limit, LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V) * self._speed_limit)
    elif self._offset_type == OffsetType.fixed:
      return self._offset_value * (CV.KPH_TO_MS if self._is_metric else CV.MPH_TO_MS)
    elif self._offset_type == OffsetType.percentage:
      return self._offset_value * 0.01 * self._speed_limit
    return 0.

  @property
  def speed_limit_warning_offset(self) -> float:
    if self._warning_offset_type == OffsetType.default:
      return float(np.interp(self._speed_limit, LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V) * self._speed_limit)
    elif self._warning_offset_type == OffsetType.fixed:
      return self._warning_offset_value * (CV.KPH_TO_MS if self._is_metric else CV.MPH_TO_MS)
    elif self._warning_offset_type == OffsetType.percentage:
      return self._warning_offset_value * 0.01 * self._speed_limit
    return 0.

  @property
  def speed_limit(self) -> float:
    return self._speed_limit

  @property
  def distance(self) -> float:
    return self._distance

  @property
  def source(self) -> Source:
    return self._source

  def _update_params(self) -> None:
    if self._current_time > self._last_params_update + PARAMS_UPDATE_PERIOD:
      self._enabled_toggle = self._params.get_bool("SpeedLimitControl")
      self._disengage_on_accelerator = self._params.get_bool("DisengageOnAccelerator")
      self._offset_type = int(self._params.get("SpeedLimitOffsetType", encoding='utf8'))
      self._offset_value = float(self._params.get("SpeedLimitValueOffset", encoding='utf8'))
      self._warning_type = int(self._params.get("SpeedLimitWarningType", encoding='utf8'))
      self._warning_offset_type = int(self._params.get("SpeedLimitWarningOffsetType", encoding='utf8'))
      self._warning_offset_value = float(self._params.get("SpeedLimitWarningValueOffset", encoding='utf8'))
      self._policy = Policy(int(self._params.get("SpeedLimitControlPolicy", encoding='utf8')))
      self._is_metric = self._params.get_bool("IsMetric")
      self._ms_to_local = CV.MS_TO_KPH if self._is_metric else CV.MS_TO_MPH
      self._resolver.change_policy(self._policy)
      self._engage_type = Engage.auto if self._pcm_cruise_op_long else \
                          np.clip(int(self._params.get("SpeedLimitEngageType", encoding='utf8')), Engage.auto, Engage.user_confirm)
      debug(f'Updated Speed limit params. enabled: {self._enabled_toggle}, with offset: {self._offset_type}')
      self._last_params_update = self._current_time

  def _generate_events(self, events_sp: EventsSP) -> None:
    """Generate events based on current conditions"""
    if not self._op_enabled or \
       not self._enabled_toggle or \
       self._speed_limit == 0 or \
       (self._gas_pressed and self._disengage_on_accelerator):
      return

    # Track selfdrived enabled time
    if not self._op_enabled_prev and self._op_enabled:
      self._last_op_enabled_time = self._current_time

    # Calculate current state
    v_cruise_rounded = int(round(self._v_cruise_setpoint * self._ms_to_local))
    v_cruise_prev_rounded = int(round(self._v_cruise_setpoint_prev * self._ms_to_local))
    speed_limit_offsetted_rounded = 0 if self._speed_limit == 0 else int(round(self.speed_limit_offseted * self._ms_to_local))

    v_cruise_changed = self._v_cruise_setpoint != self._v_cruise_setpoint_prev
    speed_limit_changed = self._speed_limit != self._speed_limit_prev

    # Update velocity offset
    self._v_offset = self.speed_limit_offseted - self._v_ego

    # Generate state-specific events
    if self._engage_type == Engage.auto:
      self._generate_auto_engage_events(events_sp, v_cruise_changed)
    elif self._engage_type == Engage.user_confirm:
      self._generate_user_confirm_events(events_sp, v_cruise_changed, speed_limit_changed,
                                         v_cruise_rounded, v_cruise_prev_rounded,
                                         speed_limit_offsetted_rounded)

    # Check if we need to adapt (decelerate) to reach speed limit
    if self._v_offset < LIMIT_SPEED_OFFSET_TH and self._enabled:
      events_sp.add(EventNameSP.speedLimitAdapting)
    elif self._v_offset >= LIMIT_SPEED_OFFSET_TH and self._enabled:
      events_sp.add(EventNameSP.speedLimitReached)

    # Speed limit value change notification
    if speed_limit_changed and self._active:
      events_sp.add(EventNameSP.speedLimitValueChange)

    # Warning when over speed limit
    if self._speed_limit > 0 and self._warning_type == 2:
      speed_limit_warning_offsetted_rounded = int(round((self._speed_limit + self.speed_limit_warning_offset) * self._ms_to_local))
      if speed_limit_warning_offsetted_rounded < int(round(self._v_ego * self._ms_to_local)):
        events_sp.add(EventNameSP.speedLimitPreActive)

  def _generate_auto_engage_events(self, events_sp: EventsSP, v_cruise_changed: bool) -> None:
    # In auto mode, activate immediately when conditions are met
    if not self._enabled:
      if self._v_offset < LIMIT_SPEED_OFFSET_TH:
        events_sp.add(EventNameSP.speedLimitAdapting)
      else:
        events_sp.add(EventNameSP.speedLimitActive)

    # User changed cruise speed - temporarily disable
    if v_cruise_changed and self._current_time > (self._last_op_enabled_time + TEMP_INACTIVE_GUARD_PERIOD):
      events_sp.add(EventNameSP.speedLimitUserCancel)

  def _generate_user_confirm_events(self, events_sp: EventsSP, v_cruise_changed: bool, speed_limit_changed: bool,
                                    v_cruise_rounded: float, v_cruise_prev_rounded: float,
                                    speed_limit_offsetted_rounded: float) -> None:
    # Check if we're in the confirmation window (2-7 seconds after op enabled)
    in_confirm_window = (self._last_op_enabled_time + 7.) >= self._current_time >= (self._last_op_enabled_time + 2.)

    if not self._enabled:
      # Need user confirmation to enable
      if in_confirm_window or speed_limit_changed:
        if speed_limit_changed:
          self._last_op_enabled_time = self._current_time - 2.  # immediately prompt
        events_sp.add(EventNameSP.speedLimitEnable)

    elif self.state == State.preActive:
      # Check if user confirmed by adjusting cruise speed
      if in_confirm_window:
        if speed_limit_changed:
          self._last_op_enabled_time = self._current_time - 2.
          events_sp.add(EventNameSP.speedLimitEnable)
        elif v_cruise_prev_rounded < speed_limit_offsetted_rounded:
          if self._v_cruise_setpoint > self._v_cruise_setpoint_prev:
            events_sp.add(EventNameSP.speedLimitUserConfirm)
        elif v_cruise_prev_rounded > speed_limit_offsetted_rounded:
          if self._v_cruise_setpoint < self._v_cruise_setpoint_prev:
            events_sp.add(EventNameSP.speedLimitUserConfirm)
        elif v_cruise_prev_rounded == speed_limit_offsetted_rounded:
          events_sp.add(EventNameSP.speedLimitUserConfirm)
      else:
        # Timeout - cancel
        events_sp.add(EventNameSP.speedLimitUserCancel)

    elif self._active:
      # User changed cruise speed while active
      if v_cruise_changed and v_cruise_rounded != speed_limit_offsetted_rounded:
        events_sp.add(EventNameSP.speedLimitUserCancel)
      # Speed limit changed while active
      elif speed_limit_changed:
        self._last_op_enabled_time = self._current_time - 2.
        events_sp.add(EventNameSP.speedLimitEnable)

  def update(self, enabled: bool, v_ego: float, a_ego: float, sm: messaging.SubMaster, v_cruise_setpoint: float, events_sp: EventsSP) -> None:
    _car_state = sm['carState']
    self._op_enabled = enabled and \
                       not (_car_state.brakePressed and (not self._brake_pressed_prev or not _car_state.standstill)) and \
                       not (_car_state.gasPressed and self._disengage_on_accelerator)
    self._v_ego = v_ego
    self._a_ego = a_ego
    self._v_cruise_setpoint = v_cruise_setpoint
    self._gas_pressed = _car_state.gasPressed
    self._brake_pressed = _car_state.brakePressed
    self._current_time = time.monotonic()

    self._speed_limit, self._distance, self._source = self._resolver.resolve(v_ego, self.speed_limit, sm)

    self._update_params()
    self._generate_events(events_sp)

    self._enabled, self._active = self._state_machine.update(events_sp)

    self._v_cruise_setpoint_prev = self._v_cruise_setpoint
    self._speed_limit_prev = self._speed_limit
    self._op_enabled_prev = self._op_enabled
    self._brake_pressed_prev = self._brake_pressed

    debug(f'Speed limit controller state: enabled: {self._enabled}, active: {self._active}, '
          f'speed limit: {self._speed_limit}, source: {self._source}, distance: {self._distance}')
