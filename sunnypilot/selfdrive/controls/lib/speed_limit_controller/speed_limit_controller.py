"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from cereal import custom
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import PARAMS_UPDATE_PERIOD, LIMIT_SPEED_OFFSET_TH, \
  SpeedLimitControlState, PRE_ACTIVE_GUARD_PERIOD, REQUIRED_INITIAL_MAX_SET_SPEED, CRUISE_SPEED_TOLERANCE
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Engage, OffsetType
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.selfdrive.modeld.constants import ModelConstants

EventNameSP = custom.OnroadEventSP.EventName

ACTIVE_STATES = (SpeedLimitControlState.active, SpeedLimitControlState.adapting)
ENABLED_STATES = (SpeedLimitControlState.preActive, SpeedLimitControlState.pending, *ACTIVE_STATES)


class SpeedLimitController:
  _speed_limit: float
  _distance: float
  _source: Source
  v_ego: float
  a_ego: float
  v_offset: float
  last_valid_speed_limit_final: float

  def __init__(self, CP):
    self.params = Params()
    self.CP = CP
    self.frame = -1
    self.last_op_engaged_frame = 0.0
    self.last_preactive_frame = 0.0
    self.is_metric = self.params.get_bool("IsMetric")
    self.enabled = self.params.get_bool("SpeedLimitControl")
    self.op_engaged = False
    self.op_engaged_prev = False
    self.v_ego = 0.
    self.a_ego = 0.
    self.v_offset = 0.
    self.v_cruise_setpoint = 0.
    self.v_cruise_setpoint_prev = 0.
    self.initial_max_set = False
    self._speed_limit = 0.
    self.speed_limit_prev = 0.
    self.last_valid_speed_limit_final = 0.
    self._distance = 0.
    self._source = Source.none
    self.state = SpeedLimitControlState.disabled
    self._state_prev = SpeedLimitControlState.disabled
    self.pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self.offset_type = OffsetType(self.params.get("SpeedLimitOffsetType", return_default=True))
    self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)

    # Mapping functions to state transitions
    self._state_transition_strategy = {
      SpeedLimitControlState.disabled: self.transition_state_from_disabled,
      SpeedLimitControlState.inactive: self.transition_state_from_inactive,
      SpeedLimitControlState.preActive: self.transition_state_from_preactive,
      SpeedLimitControlState.pending: self.transition_state_from_pending,
      SpeedLimitControlState.adapting: self.transition_state_from_adapting,
      SpeedLimitControlState.active: self.transition_state_from_active,
    }

    # Solution functions mapped to respective states
    self.acceleration_solutions = {
      SpeedLimitControlState.disabled: self.get_current_acceleration_as_target,
      SpeedLimitControlState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.preActive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.pending: self.get_current_acceleration_as_target,
      SpeedLimitControlState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitControlState.active: self.get_active_state_target_acceleration,
    }

  @property
  def is_enabled(self) -> bool:
    return self.state in ENABLED_STATES

  @property
  def is_active(self) -> bool:
    return self.state in ACTIVE_STATES

  @property
  def speed_limit_final(self) -> float:
    return self._speed_limit + self.speed_limit_offset

  @property
  def speed_limit_offset(self) -> float:
    return self.get_offset(self.offset_type, self.offset_value)

  @property
  def speed_limit(self) -> float:
    return self._speed_limit

  @property
  def distance(self) -> float:
    return self._distance

  @property
  def source(self) -> Source:
    return self._source

  @property
  def final_cruise_speed(self) -> float:
    if self.is_active:
      # If we have a current valid speed limit, use it
      if self._speed_limit > 0:
        self.last_valid_speed_limit_final = self.speed_limit_final
        return self.speed_limit_final

      # If no current speed limit but we have a last valid one, use that
      if self.last_valid_speed_limit_final > 0:
        return self.last_valid_speed_limit_final

    # Fallback
    return V_CRUISE_UNSET

  @property
  def v_cruise_setpoint_changed(self) -> bool:
    return bool(self.v_cruise_setpoint != self.v_cruise_setpoint_prev)

  @property
  def speed_limit_changed(self) -> bool:
    return bool(self._speed_limit != self.speed_limit_prev)

  def get_offset(self, offset_type: OffsetType, offset_value: int) -> float:
    if offset_type == OffsetType.off:
      return 0
    elif offset_type == OffsetType.fixed:
      return offset_value * (CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS)
    elif offset_type == OffsetType.percentage:
      return offset_value * 0.01 * self._speed_limit
    else:
      raise NotImplementedError("Offset not supported")

  def update_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("SpeedLimitControl")
      self.offset_type = OffsetType(self.params.get("SpeedLimitOffsetType", return_default=True))
      self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
      self.is_metric = self.params.get_bool("IsMetric")

  @staticmethod
  def read_engage_type_param() -> Engage:
    return Engage.auto

  def initial_max_set_confirmed(self) -> bool:
    return bool(abs(self.v_cruise_setpoint - REQUIRED_INITIAL_MAX_SET_SPEED) <= CRUISE_SPEED_TOLERANCE)

  def detect_manual_cruise_change(self) -> bool:
    # If cruise speed changed and it's not what SLC would set
    if self.v_cruise_setpoint_changed:
      expected_cruise = self.speed_limit_final
      return bool(abs(self.v_cruise_setpoint - expected_cruise) > CRUISE_SPEED_TOLERANCE)

    return False

  def update_calculations(self, v_ego: float, a_ego: float, v_cruise_setpoint: float) -> None:
    self.v_cruise_setpoint = v_cruise_setpoint if not np.isnan(v_cruise_setpoint) else 0.0
    self.v_ego = v_ego
    self.a_ego = a_ego

    # Update current velocity offset (error)
    self.v_offset = self.speed_limit_final - self.v_ego

    if not self.op_engaged_prev and self.op_engaged:
      self.last_op_engaged_frame = self.frame

    if not self._state_prev == SpeedLimitControlState.preActive and self.state == SpeedLimitControlState.preActive:
      self.last_preactive_frame = self.frame

  def transition_state_from_disabled(self) -> None:
    # Wait 2 seconds after long engaged before starting fresh session
    if (self.frame - self.last_op_engaged_frame) * DT_MDL >= 2.:
      self.state = SpeedLimitControlState.preActive
      self.initial_max_set = False

  def transition_state_from_inactive(self) -> None:
    pass

  def transition_state_from_preactive(self) -> None:
    if self.initial_max_set_confirmed():
      self.initial_max_set = True
      if self._speed_limit > 0:
        if self.v_offset < LIMIT_SPEED_OFFSET_TH:
          self.state = SpeedLimitControlState.adapting
        else:
          self.state = SpeedLimitControlState.active
      else:
        self.state = SpeedLimitControlState.pending
    elif (self.frame - self.last_preactive_frame) * DT_MDL >= PRE_ACTIVE_GUARD_PERIOD:
      # Timeout - session ended
      self.state = SpeedLimitControlState.inactive

  def transition_state_from_pending(self) -> None:
    if self._speed_limit > 0:
      if self.v_offset < LIMIT_SPEED_OFFSET_TH:
        self.state = SpeedLimitControlState.adapting
      else:
        self.state = SpeedLimitControlState.active

  def transition_state_from_adapting(self) -> None:
    if self.detect_manual_cruise_change():
      self.state = SpeedLimitControlState.inactive
    elif self.v_offset >= LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.active

  def transition_state_from_active(self) -> None:
    if self.detect_manual_cruise_change():
      self.state = SpeedLimitControlState.inactive
    elif self._speed_limit > 0 and self.v_offset < LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.adapting

  def state_control(self) -> None:
    self._state_prev = self.state

    # If op is disabled or SLC is disabled, go to disabled state (not inactive)
    if not self.op_engaged or not self.enabled:
      self.state = SpeedLimitControlState.disabled  # Changed from inactive
      self.initial_max_set = False
      return

    self._state_transition_strategy[self.state]()

  def get_current_acceleration_as_target(self) -> float:
    return self.a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    if self._distance > 0:
      return (self.speed_limit_final ** 2 - self.v_ego ** 2) / (2. * self._distance)

    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def get_active_state_target_acceleration(self) -> float:
    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def update_events(self, events_sp: EventsSP) -> None:
    if self.is_active:
      if self.state == SpeedLimitControlState.preActive:
        events_sp.add(EventNameSP.speedLimitPreActive)
      elif self._state_prev not in ACTIVE_STATES:
        events_sp.add(EventNameSP.speedLimitActive)
      elif self.speed_limit_changed:
        events_sp.add(EventNameSP.speedLimitValueChange)

  def update(self, long_active: bool, v_ego: float, a_ego: float, v_cruise_setpoint: float,
             speed_limit: float, distance: float, source: Source, events_sp: EventsSP) -> float:
    self.op_engaged = long_active

    self._speed_limit = speed_limit
    self._distance = distance
    self._source = source

    self.update_params()
    self.update_calculations(v_ego, a_ego, v_cruise_setpoint)
    self.state_control()
    self.update_events(events_sp)

    # Update change tracking variablesZ
    self.speed_limit_prev = self._speed_limit
    self.v_cruise_setpoint_prev = self.v_cruise_setpoint
    self.op_engaged_prev = self.op_engaged

    self.frame += 1

    return self.final_cruise_speed
