import numpy as np
import time

from cereal import messaging, custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V, \
  PARAMS_UPDATE_PERIOD, TEMP_INACTIVE_GUARD_PERIOD, LIMIT_SPEED_OFFSET_TH, SpeedLimitControlState
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Policy, Engage, OffsetType
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.helpers import description_for_state, debug
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.selfdrive.modeld.constants import ModelConstants

EventNameSP = custom.OnroadEventSP.EventName

ACTIVE_STATES = (SpeedLimitControlState.active, SpeedLimitControlState.adapting)
ENABLED_STATES = (SpeedLimitControlState.preActive, SpeedLimitControlState.tempInactive, *ACTIVE_STATES)


class SpeedLimitController:
  def __init__(self, CP):
    self._params = Params()
    self._CP = CP
    self._policy = Policy(int(self._params.get("SpeedLimitControlPolicy", encoding='utf8')))
    self._resolver = SpeedLimitResolver(self._policy)
    self._last_params_update = 0.0
    self._last_op_enabled_time = 0.0
    self._is_metric = self._params.get_bool("IsMetric")
    self._is_enabled = self._params.get_bool("SpeedLimitControl")
    self._disengage_on_accelerator = self._params.get_bool("DisengageOnAccelerator")
    self._op_enabled = False
    self._op_enabled_prev = False
    self._v_ego = 0.
    self._a_ego = 0.
    self._v_offset = 0.
    self._v_cruise_setpoint = 0.
    self._v_cruise_setpoint_prev = 0.
    self._v_cruise_setpoint_changed = False
    self._speed_limit = 0.
    self._speed_limit_prev = 0.
    self._speed_limit_changed = False
    self._distance = 0.
    self._source = Source.none
    self._state = SpeedLimitControlState.inactive
    self._state_prev = SpeedLimitControlState.inactive
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
    self._v_cruise_rounded = 0.
    self._v_cruise_prev_rounded = 0.
    self._speed_limit_offsetted_rounded = 0.
    self._speed_limit_warning_offsetted_rounded = 0.
    self._ms_to_local = CV.MS_TO_KPH if self._is_metric else CV.MS_TO_MPH

    # Mapping functions to state transitions
    self.state_transition_strategy = {
      # Transition functions for each state
      SpeedLimitControlState.inactive: self.transition_state_from_inactive,
      SpeedLimitControlState.tempInactive: self.transition_state_from_temp_inactive,
      SpeedLimitControlState.adapting: self.transition_state_from_adapting,
      SpeedLimitControlState.active: self.transition_state_from_active,
      SpeedLimitControlState.preActive: self.transition_state_from_pre_active,
    }

    # FIXME-SP: unused?
    # Solution functions mapped to respective states
    self.acceleration_solutions = {
      # Solution functions for each state
      SpeedLimitControlState.tempInactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitControlState.active: self.get_active_state_target_acceleration,
      SpeedLimitControlState.preActive: self.get_current_acceleration_as_target,
    }

  @property
  def state(self) -> SpeedLimitControlState:
    return self._state

  @state.setter
  def state(self, value) -> None:
    if value != self._state:
      debug(f'Speed Limit Controller state: {description_for_state(value)}')

      if value == SpeedLimitControlState.tempInactive:
        # Reset previous speed limit to current value as to prevent going out of tempInactive in
        # a single cycle when the speed limit changes at the same time the user has temporarily deactivated it.
        self._speed_limit_prev = self._speed_limit

    self._state = value

  @property
  def is_enabled(self) -> bool:
    return self.state in ENABLED_STATES and self._is_enabled

  @property
  def is_active(self) -> bool:
    return self.state in ACTIVE_STATES and self._is_enabled

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

  def _update_v_cruise_setpoint_prev(self) -> None:
    self._v_cruise_setpoint_prev = self._v_cruise_setpoint

  def _update_params(self) -> None:
    if self._current_time > self._last_params_update + PARAMS_UPDATE_PERIOD:
      self._is_enabled = self._params.get_bool("SpeedLimitControl")
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
      debug(f'Updated Speed limit params. enabled: {self._is_enabled}, with offset: {self._offset_type}')
      self._last_params_update = self._current_time

  def _update_calculations(self) -> None:
    # Update current velocity offset (error)
    self._v_offset = self.speed_limit_offseted - self._v_ego

    # Track the time op becomes active to prevent going to tempInactive right away after
    # op enabling since controlsd will change the cruise speed every time on enabling and this will
    # cause a temp inactive transition if the controller is updated before controlsd sets actual cruise
    # speed.
    if not self._op_enabled_prev and self._op_enabled:
      self._last_op_enabled_time = self._current_time

    # Update change tracking variables
    self._speed_limit_changed = self._speed_limit != self._speed_limit_prev
    self._v_cruise_setpoint_changed = self._v_cruise_setpoint != self._v_cruise_setpoint_prev
    self._speed_limit_prev = self._speed_limit
    if self._engage_type != Engage.user_confirm:
      self._update_v_cruise_setpoint_prev()
    self._op_enabled_prev = self._op_enabled
    self._brake_pressed_prev = self._brake_pressed

    self._v_cruise_rounded = int(round(self._v_cruise_setpoint * self._ms_to_local))
    self._v_cruise_prev_rounded = int(round(self._v_cruise_setpoint_prev * self._ms_to_local))
    self._speed_limit_offsetted_rounded = 0 if self._speed_limit == 0 else int(round((self._speed_limit + self.speed_limit_offset) * self._ms_to_local))
    self._speed_limit_warning_offsetted_rounded = 0 if self._speed_limit == 0 else \
                                                  int(round((self._speed_limit + self.speed_limit_warning_offset) * self._ms_to_local))

  def transition_state_from_inactive(self) -> None:
    """ Make state transition from inactive state """
    if self._engage_type == Engage.user_confirm:
      if (((self._last_op_enabled_time + 7.) >= self._current_time >= (self._last_op_enabled_time + 2.)) or
            self._speed_limit_changed):
        if self._speed_limit_changed:
          self._last_op_enabled_time = self._current_time - 2.  # immediately prompt confirmation
        self.state = SpeedLimitControlState.preActive
    elif self._engage_type == Engage.auto:
      if self._v_offset < LIMIT_SPEED_OFFSET_TH:
        self.state = SpeedLimitControlState.adapting
      else:
        self.state = SpeedLimitControlState.active

  def transition_state_from_temp_inactive(self) -> None:
    """ Make state transition from temporary inactive state """
    if self._speed_limit_changed:
      if self._engage_type == Engage.user_confirm:
        self._last_op_enabled_time = self._current_time - 2.  # immediately prompt confirmation
        self.state = SpeedLimitControlState.preActive
      elif self._engage_type == Engage.auto:
        self.state = SpeedLimitControlState.inactive

  def transition_state_from_pre_active(self) -> None:
    """ Make state transition from preActive state """
    if self._current_time >= (self._last_op_enabled_time + 7.):
      self.state = SpeedLimitControlState.inactive
    elif (self._last_op_enabled_time + 7.) > self._current_time > (self._last_op_enabled_time + 2.):
      if self._speed_limit_changed:
        self._last_op_enabled_time = self._current_time - 2.  # immediately prompt confirmation
      elif self._v_cruise_prev_rounded < self._speed_limit_offsetted_rounded:
        if self._v_cruise_setpoint > self._v_cruise_setpoint_prev:
          self.state = SpeedLimitControlState.active
      elif self._v_cruise_prev_rounded > self._speed_limit_offsetted_rounded:
        if self._v_cruise_setpoint < self._v_cruise_setpoint_prev:
          self.state = SpeedLimitControlState.active
      elif self._v_cruise_prev_rounded == self._speed_limit_offsetted_rounded:
        self.state = SpeedLimitControlState.active

  def transition_state_from_adapting(self) -> None:
    """ Make state transition from adapting state """
    if self._v_offset >= LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.active

  def transition_state_from_active(self) -> None:
    """ Make state transition from active state """
    if self._engage_type == Engage.user_confirm:
      if self._state_prev == SpeedLimitControlState.active:
        if self._v_cruise_setpoint_changed and self._v_cruise_rounded != self._speed_limit_offsetted_rounded:
          self.state = SpeedLimitControlState.tempInactive
        elif self._speed_limit_changed:
          self._last_op_enabled_time = self._current_time - 2.  # immediately prompt confirmation
          self.state = SpeedLimitControlState.preActive
    elif self._engage_type == Engage.auto:
      if self._v_offset < LIMIT_SPEED_OFFSET_TH:
        self.state = SpeedLimitControlState.adapting

  def _state_transition(self) -> None:
    self._state_prev = self._state

    # In any case, if op is disabled, or speed limit control is disabled
    # or the reported speed limit is 0 or gas is pressed, deactivate.
    if not self._op_enabled or not self._is_enabled or self._speed_limit == 0 or \
          (self._gas_pressed and self._disengage_on_accelerator):
      self.state = SpeedLimitControlState.inactive
      return

    # In any case, we deactivate the speed limit controller temporarily if the user changes the cruise speed.
    # Ignore if a minimum amount of time has not passed since activation. This is to prevent temp inactivations
    # due to controlsd logic changing cruise setpoint when going active.
    if self._engage_type == Engage.auto and self._v_cruise_setpoint_changed and \
          self._current_time > (self._last_op_enabled_time + TEMP_INACTIVE_GUARD_PERIOD):
      self.state = SpeedLimitControlState.tempInactive
      return

    self.state_transition_strategy[self.state]()

    if self._engage_type == Engage.user_confirm:
      self._update_v_cruise_setpoint_prev()

  def get_current_acceleration_as_target(self) -> float:
    """ When state is inactive or tempInactive, preserve current acceleration """
    return self._a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    """ In adapting state, calculate target acceleration based on speed limit and current velocity """
    if self.distance > 0:
      return (self.speed_limit_offseted ** 2 - self._v_ego ** 2) / (2. * self.distance)

    return self._v_offset / ModelConstants.T_IDXS[CONTROL_N]

  def get_active_state_target_acceleration(self) -> float:
    """ In active state, aim to keep speed constant around control time horizon """
    return self._v_offset / ModelConstants.T_IDXS[CONTROL_N]

  def _update_events(self, events_sp: EventsSP) -> None:
    if self._speed_limit > 0 and self._warning_type == 2 and \
        self._speed_limit_warning_offsetted_rounded < int(round(self._v_ego * self._ms_to_local)):
      events_sp.add(EventNameSP.speedLimitPreActive)

    if not self.is_active:
      if self._state == SpeedLimitControlState.preActive and self._state_prev != SpeedLimitControlState.preActive and \
          self._v_cruise_rounded != self._speed_limit_offsetted_rounded:
        events_sp.add(EventNameSP.speedLimitPreActive)
    else:
      if self._engage_type == Engage.user_confirm:
        if self._state_prev == SpeedLimitControlState.preActive:
          events_sp.add(EventNameSP.speedLimitConfirmed)
          events_sp.add(EventNameSP.speedLimitActive)
      elif self._engage_type == Engage.auto:
        if self._state_prev not in ACTIVE_STATES:
          events_sp.add(EventNameSP.speedLimitActive)
        elif self._speed_limit_changed != 0:
          events_sp.add(EventNameSP.speedLimitValueChange)

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
    self._update_calculations()
    self._state_transition()
    self._update_events(events_sp)
