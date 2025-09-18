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
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_assist import PARAMS_UPDATE_PERIOD, LIMIT_SPEED_OFFSET_TH, \
  SpeedLimitAssistState, PRE_ACTIVE_GUARD_PERIOD, REQUIRED_INITIAL_MAX_SET_SPEED, CRUISE_SPEED_TOLERANCE, DISABLED_GUARD_PERIOD
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_assist.common import OffsetType
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.selfdrive.modeld.constants import ModelConstants

EventNameSP = custom.OnroadEventSP.EventName
SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimitSource

ACTIVE_STATES = (SpeedLimitAssistState.active, SpeedLimitAssistState.adapting)
ENABLED_STATES = (SpeedLimitAssistState.preActive, SpeedLimitAssistState.pending, SpeedLimitAssistState.overriding, *ACTIVE_STATES)


class SpeedLimitAssist:
  _speed_limit: float
  _distance: float
  _source: custom.LongitudinalPlanSP.SpeedLimitSource
  v_ego: float
  a_ego: float
  v_offset: float
  last_valid_speed_limit_final: float

  def __init__(self, CP):
    self.params = Params()
    self.CP = CP
    self.frame = -1
    self.long_engaged_timer = 0
    self.pre_active_timer = 0
    self.is_metric = self.params.get_bool("IsMetric")
    self.enabled = self.params.get_bool("SpeedLimitAssist")
    self.long_enabled = False
    self.long_enabled_prev = False
    self.long_override = False
    self.is_enabled = False
    self.is_active = False
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
    self._source = SpeedLimitSource.none
    self.state = SpeedLimitAssistState.disabled
    self._state_prev = SpeedLimitAssistState.disabled
    self.pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self.offset_type = OffsetType(self.params.get("SpeedLimitOffsetType", return_default=True))
    self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)

    # Solution functions mapped to respective states
    self.acceleration_solutions = {
      SpeedLimitAssistState.disabled: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.preActive: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.pending: self.get_current_acceleration_as_target,
      SpeedLimitAssistState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitAssistState.active: self.get_active_state_target_acceleration,
    }

  @property
  def speed_limit_final(self) -> float:
    return self._speed_limit + self.speed_limit_offset

  @property
  def speed_limit_changed(self) -> bool:
    return bool(self._speed_limit != self.speed_limit_prev)

  @property
  def speed_limit_offset(self) -> float:
    return self.get_offset(self.offset_type, self.offset_value)

  @property
  def v_cruise_setpoint_changed(self) -> bool:
    return bool(self.v_cruise_setpoint != self.v_cruise_setpoint_prev)

  def get_v_target_from_control(self) -> float:
    if self.is_enabled:
      # If we have a current valid speed limit, use it
      if self._speed_limit > 0:
        self.last_valid_speed_limit_final = self.speed_limit_final
        return self.speed_limit_final

      # If no current speed limit but we have a last valid one, use that
      if self.last_valid_speed_limit_final > 0:
        return self.last_valid_speed_limit_final

    # Fallback
    return V_CRUISE_UNSET

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
      self.enabled = self.params.get_bool("SpeedLimitAssist")
      self.offset_type = OffsetType(self.params.get("SpeedLimitOffsetType", return_default=True))
      self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
      self.is_metric = self.params.get_bool("IsMetric")

  def initial_max_set_confirmed(self) -> bool:
    return bool(abs(self.v_cruise_setpoint - REQUIRED_INITIAL_MAX_SET_SPEED) <= CRUISE_SPEED_TOLERANCE)

  def detect_manual_cruise_change(self) -> bool:
    # If cruise speed changed and it's not what SLA would set
    if self.v_cruise_setpoint_changed:
      expected_cruise = self.speed_limit_final
      return bool(abs(self.v_cruise_setpoint - expected_cruise) > CRUISE_SPEED_TOLERANCE)

    return False

  def update_calculations(self, v_cruise_setpoint: float) -> None:
    self.v_cruise_setpoint = v_cruise_setpoint if not np.isnan(v_cruise_setpoint) else 0.0

    # Update current velocity offset (error)
    self.v_offset = self.speed_limit_final - self.v_ego

  def get_current_acceleration_as_target(self) -> float:
    return self.a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    if self._distance > 0:
      return (self.speed_limit_final ** 2 - self.v_ego ** 2) / (2. * self._distance)

    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def get_active_state_target_acceleration(self) -> float:
    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def update_state_machine(self):
    self._state_prev = self.state

    self.long_engaged_timer = max(0, self.long_engaged_timer - 1)
    self.pre_active_timer = max(0, self.pre_active_timer - 1)

    # ACTIVE, ADAPTING, PENDING, PRE_ACTIVE, INACTIVE, OVERRIDING
    if self.state != SpeedLimitAssistState.disabled:
      if not self.long_enabled or not self.enabled:
        self.state = SpeedLimitAssistState.disabled
        self.initial_max_set = False
      elif self.long_override:
        self.state = SpeedLimitAssistState.overriding

      else:
        # ACTIVE
        if self.state == SpeedLimitAssistState.active:
          if self.detect_manual_cruise_change():
            self.state = SpeedLimitAssistState.inactive
          elif self._speed_limit > 0 and self.v_offset < LIMIT_SPEED_OFFSET_TH:
            self.state = SpeedLimitAssistState.adapting

        # ADAPTING
        elif self.state == SpeedLimitAssistState.adapting:
          if self.detect_manual_cruise_change():
            self.state = SpeedLimitAssistState.inactive
          elif self.v_offset >= LIMIT_SPEED_OFFSET_TH:
            self.state = SpeedLimitAssistState.active

        # PENDING
        elif self.state == SpeedLimitAssistState.pending:
          if self._speed_limit > 0:
            if self.v_offset < LIMIT_SPEED_OFFSET_TH:
              self.state = SpeedLimitAssistState.adapting
            else:
              self.state = SpeedLimitAssistState.active

        # PRE_ACTIVE
        elif self.state == SpeedLimitAssistState.preActive:
          if self.initial_max_set_confirmed():
            self.initial_max_set = True
            if self._speed_limit > 0:
              if self.v_offset < LIMIT_SPEED_OFFSET_TH:
                self.state = SpeedLimitAssistState.adapting
              else:
                self.state = SpeedLimitAssistState.active
            else:
              self.state = SpeedLimitAssistState.pending
          elif self.pre_active_timer <= PRE_ACTIVE_GUARD_PERIOD:
            # Timeout - session ended
            self.state = SpeedLimitAssistState.inactive

        # OVERRIDING
        elif self.state == SpeedLimitAssistState.overriding:
          if not self.long_override:
            self.state = SpeedLimitAssistState.preActive

        # INACTIVE
        elif self.state == SpeedLimitAssistState.inactive:
          pass

    # DISABLED
    elif self.state == SpeedLimitAssistState.disabled:
      if self.long_enabled and self.enabled:
        if self.long_override:
          self.state = SpeedLimitAssistState.overriding

        elif not self.long_enabled_prev:
          self.pre_active_timer = int(DISABLED_GUARD_PERIOD / DT_MDL)

        elif self.pre_active_timer <= 0:
          self.state = SpeedLimitAssistState.preActive
          self.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD / DT_MDL)
          self.initial_max_set = False

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES

    return enabled, active

  def update_events(self, events_sp: EventsSP) -> None:
    if self.state == SpeedLimitAssistState.preActive and self._state_prev != SpeedLimitAssistState.preActive:
      events_sp.add(EventNameSP.speedLimitPreActive)
    elif self.is_active:
      if self._state_prev not in ACTIVE_STATES:
        events_sp.add(EventNameSP.speedLimitActive)
      elif self.speed_limit_changed:
        events_sp.add(EventNameSP.speedLimitChanged)

  def update(self, long_enabled: bool, long_override: bool, v_ego: float, a_ego: float, v_cruise_setpoint: float,
             speed_limit: float, distance: float, source: custom.LongitudinalPlanSP.SpeedLimitSource, events_sp: EventsSP) -> float:
    self.long_enabled = long_enabled
    self.long_override = long_override
    self.v_ego = v_ego
    self.a_ego = a_ego

    self._speed_limit = speed_limit
    self._distance = distance
    self._source = source

    self.update_params()
    self.update_calculations(v_cruise_setpoint)
    self.is_enabled, self.is_active = self.update_state_machine()
    self.update_events(events_sp)

    # Update change tracking variables
    self.speed_limit_prev = self._speed_limit
    self.v_cruise_setpoint_prev = self.v_cruise_setpoint
    self.long_enabled_prev = self.long_enabled
    self.frame += 1

    v_target = self.get_v_target_from_control()

    return v_target
