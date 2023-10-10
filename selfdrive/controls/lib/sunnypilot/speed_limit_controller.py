import numpy as np
import time
from common.numpy_fast import interp
from common.conversions import Conversions as CV
from common.params import Params
from openpilot.selfdrive.controls.lib.sunnypilot import LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V, \
  PARAMS_UPDATE_PERIOD, TEMP_INACTIVE_GUARD_PERIOD, EventName, SpeedLimitControlState

from openpilot.selfdrive.controls.lib.drive_helpers import LIMIT_MIN_ACC, LIMIT_MAX_ACC, LIMIT_SPEED_OFFSET_TH, \
  CONTROL_N
from openpilot.selfdrive.controls.lib.events import Events, ET
from openpilot.selfdrive.controls.lib.sunnypilot.common import Source, Policy
from openpilot.selfdrive.controls.lib.sunnypilot.helpers import description_for_state, debug
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_resolver import SpeedLimitResolver
from openpilot.selfdrive.modeld.constants import T_IDXS


class SpeedLimitController:
  def __init__(self):
    self._params = Params()
    self._resolver = SpeedLimitResolver()
    self._last_params_update = 0.0
    self._last_op_enabled_time = 0.0
    self._is_metric = self._params.get_bool("IsMetric")
    self._is_enabled = self._params.get_bool("SpeedLimitControl")
    self._offset_enabled = self._params.get_bool("SpeedLimitPercOffset")
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
    self._a_target = 0.

    self._offset_type = int(self._params.get("SpeedLimitOffsetType", encoding='utf8'))
    self._offset_value = float(self._params.get("SpeedLimitValueOffset", encoding='utf8'))
    self._brake_pressed = False
    self._brake_pressed_prev = False

    # Mapping functions to state transitions
    self.state_transition_strategy = {
      # Transition functions for each state
      SpeedLimitControlState.inactive: self.transition_state_from_inactive,
      SpeedLimitControlState.tempInactive: self.transition_state_from_temp_inactive,
      SpeedLimitControlState.adapting: self.transition_state_from_adapting,
      SpeedLimitControlState.active: self.transition_state_from_active,
    }

    # Solution functions mapped to respective states
    self.acceleration_solutions = {
      # Solution functions for each state
      SpeedLimitControlState.tempInactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitControlState.active: self.get_active_state_target_acceleration,
    }

  @property
  def a_target(self):
    return self._a_target if self.is_active else self._a_ego

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    if value != self._state:
      debug(f'Speed Limit Controller state: {description_for_state(value)}')

      if value == SpeedLimitControlState.tempInactive:
        # Reset previous speed limit to current value as to prevent going out of tempInactive in
        # a single cycle when the speed limit changes at the same time the user has temporarily deactivated it.
        self._speed_limit_prev = self._speed_limit

    self._state = value

  @property
  def is_active(self):
    return self.state > SpeedLimitControlState.tempInactive

  @property
  def speed_limit_offseted(self):
    return self._speed_limit + self.speed_limit_offset

  @property
  def speed_limit_offset(self):
    if self._offset_enabled:
      if self._offset_type == 0:
        return interp(self._speed_limit, LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V) * self._speed_limit
      elif self._offset_type == 1:
        return self._offset_value * 0.01 * self._speed_limit
      elif self._offset_type == 2:
        return self._offset_value * (CV.KPH_TO_MS if self._is_metric else CV.MPH_TO_MS)
    return 0.

  @property
  def speed_limit(self):
    return self._speed_limit

  @property
  def distance(self):
    return self._distance

  @property
  def source(self):
    return self._source

  def _update_params(self):
    t = time.monotonic()
    if t > self._last_params_update + PARAMS_UPDATE_PERIOD:
      self._is_enabled = self._params.get_bool("SpeedLimitControl")
      self._offset_enabled = self._params.get_bool("SpeedLimitPercOffset")
      self._offset_type = int(self._params.get("SpeedLimitOffsetType", encoding='utf8'))
      self._offset_value = float(self._params.get("SpeedLimitValueOffset", encoding='utf8'))
      debug(f'Updated Speed limit params. enabled: {self._is_enabled}, with offset: {self._offset_enabled}')
      self._last_params_update = t

  def _update_calculations(self):
    # Update current velocity offset (error)
    self._v_offset = self.speed_limit_offseted - self._v_ego

    # Track the time op becomes active to prevent going to tempInactive right away after
    # op enabling since controlsd will change the cruise speed every time on enabling and this will
    # cause a temp inactive transition if the controller is updated before controlsd sets actual cruise
    # speed.
    if not self._op_enabled_prev and self._op_enabled:
      self._last_op_enabled_time = time.monotonic()

    # Update change tracking variables
    self._speed_limit_changed = self._speed_limit != self._speed_limit_prev
    self._v_cruise_setpoint_changed = self._v_cruise_setpoint != self._v_cruise_setpoint_prev
    self._speed_limit_prev = self._speed_limit
    self._v_cruise_setpoint_prev = self._v_cruise_setpoint
    self._op_enabled_prev = self._op_enabled
    self._brake_pressed_prev = self._brake_pressed

  def transition_state_from_inactive(self):
    """ Make state transition from inactive state """
    if self._v_offset < LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.adapting
    else:
      self.state = SpeedLimitControlState.active

  def transition_state_from_temp_inactive(self):
    """ Make state transition from temporary inactive state """
    if self._speed_limit_changed:
      self.state = SpeedLimitControlState.inactive

  def transition_state_from_adapting(self):
    """ Make state transition from adapting state """
    if self._v_offset >= LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.active

  def transition_state_from_active(self):
    """ Make state transition from active state """
    if self._v_offset < LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.adapting

  def _state_transition(self):
    self._state_prev = self._state

    # In any case, if op is disabled, or speed limit control is disabled
    # or the reported speed limit is 0 or gas is pressed, deactivate.
    if not self._op_enabled or not self._is_enabled or self._speed_limit == 0 or (self._gas_pressed and self._disengage_on_accelerator):
      self.state = SpeedLimitControlState.inactive
      return

    # In any case, we deactivate the speed limit controller temporarily if the user changes the cruise speed.
    # Ignore if a minimum amount of time has not passed since activation. This is to prevent temp inactivations
    # due to controlsd logic changing cruise setpoint when going active.
    if self._v_cruise_setpoint_changed and \
            time.monotonic() > (self._last_op_enabled_time + TEMP_INACTIVE_GUARD_PERIOD):
      self.state = SpeedLimitControlState.tempInactive
      return

    self.state_transition_strategy[self.state]()

  def get_current_acceleration_as_target(self):
    """ When state is inactive or tempInactive, preserve current acceleration """
    return self._a_ego

  def get_adapting_state_target_acceleration(self):
    """ In adapting state, calculate target acceleration based on speed limit and current velocity """
    if self.distance > 0:
      return (self.speed_limit_offseted**2 - self._v_ego**2) / (2. * self.distance)

    return self._v_offset / T_IDXS[CONTROL_N]

  def get_active_state_target_acceleration(self):
    """ In active state, aim to keep speed constant around control time horizon """
    return self._v_offset / T_IDXS[CONTROL_N]

  def _update_solution(self):
    a_target = self.acceleration_solutions[self.state]()

    # Keep solution limited.
    self._a_target = np.clip(a_target, LIMIT_MIN_ACC, LIMIT_MAX_ACC)

  def _update_events(self, events):
    if not self.is_active:
      # no event while inactive
      return

    if self._state_prev <= SpeedLimitControlState.tempInactive:
      events.add(EventName.speedLimitActive)
    elif self._speed_limit_changed != 0:
      events.add(EventName.speedLimitValueChange)

  def update(self, enabled, v_ego, a_ego, sm, v_cruise_setpoint, events=Events()):
    _car_state = sm['carState']
    self._op_enabled = enabled and sm['controlsState'].enabled and _car_state.cruiseState.enabled and \
                       not (_car_state.brakePressed and (not self._brake_pressed_prev or not _car_state.standstill)) and \
                       not events.contains(ET.OVERRIDE_LONGITUDINAL)
    self._v_ego = v_ego
    self._a_ego = a_ego
    self._v_cruise_setpoint = v_cruise_setpoint
    self._gas_pressed = _car_state.gasPressed
    self._brake_pressed = _car_state.brakePressed

    self._speed_limit, self._distance, self._source = self._resolver.resolve(v_ego, self.speed_limit, sm)

    self._update_params()
    self._update_calculations()
    self._state_transition()
    self._update_solution()
    self._update_events(events)
