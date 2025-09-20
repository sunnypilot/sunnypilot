"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from cereal import custom
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode
from openpilot.selfdrive.modeld.constants import ModelConstants

EventNameSP = custom.OnroadEventSP.EventName
SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState
SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimit.Source

ACTIVE_STATES = (SpeedLimitAssistState.active, SpeedLimitAssistState.adapting)
ENABLED_STATES = (SpeedLimitAssistState.preActive, SpeedLimitAssistState.pending, *ACTIVE_STATES)

DISABLED_GUARD_PERIOD = 2  # secs.
PRE_ACTIVE_GUARD_PERIOD = 5  # secs. Time to wait after activation before considering temp deactivation signal.

LIMIT_MIN_ACC = -1.5  # m/s^2 Maximum deceleration allowed for limit controllers to provide.
LIMIT_MAX_ACC = 1.0   # m/s^2 Maximum acceleration allowed for limit controllers to provide while active.
LIMIT_MIN_SPEED = 8.33  # m/s, Minimum speed limit to provide as solution on limit controllers.
LIMIT_SPEED_OFFSET_TH = -1.  # m/s Maximum offset between speed limit and current speed for adapting state.

# Speed Limit Assist Auto mode constants
REQUIRED_INITIAL_MAX_SET_SPEED = 35.7632  # m/s 80 MPH  # TODO-SP: customizable with params
CRUISE_SPEED_TOLERANCE = 0.44704  # m/s ±1 MPH tolerance  # TODO-SP: metric vs imperial
FALLBACK_CRUISE_SPEED = 255.0  # m/s fallback when no speed limit available


class SpeedLimitAssist:
  _speed_limit: float
  _speed_limit_offset: float
  _distance: float
  v_ego: float
  a_ego: float
  v_offset: float
  last_valid_speed_limit_final: float
  output_v_target: float = V_CRUISE_UNSET
  output_a_target: float = 0.

  def __init__(self, CP):
    self.params = Params()
    self.CP = CP
    self.frame = -1
    self.long_engaged_timer = 0
    self.pre_active_timer = 0
    self.is_metric = self.params.get_bool("IsMetric")
    self.enabled = self.params.get("SpeedLimitMode", return_default=True) == Mode.assist
    self.long_enabled = False
    self.long_enabled_prev = False
    self.is_enabled = False
    self.is_active = False
    self.v_ego = 0.
    self.a_ego = 0.
    self.v_offset = 0.
    self.v_cruise_cluster = 0.
    self.v_cruise_cluster_prev = 0.
    self._speed_limit = 0.
    self._speed_limit_offset = 0.
    self.speed_limit_prev = 0.
    self.last_valid_speed_limit_final = 0.
    self._distance = 0.
    self.state = SpeedLimitAssistState.disabled
    self._state_prev = SpeedLimitAssistState.disabled
    self.pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    # TODO-SP: SLA's own output_a_target for planner
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
    return self._speed_limit + self._speed_limit_offset

  @property
  def speed_limit_changed(self) -> bool:
    return bool(self._speed_limit != self.speed_limit_prev)

  @property
  def v_cruise_cluster_changed(self) -> bool:
    return bool(self.v_cruise_cluster != self.v_cruise_cluster_prev)

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

  # TODO-SP: SLA's own output_a_target for planner
  def get_a_target_from_control(self) -> float:
    return self.a_ego

  def update_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.is_metric = self.params.get_bool("IsMetric")
      self.enabled = self.params.get("SpeedLimitMode", return_default=True) == Mode.assist

  def initial_max_set_confirmed(self) -> bool:
    return bool(abs(self.v_cruise_cluster - REQUIRED_INITIAL_MAX_SET_SPEED) <= CRUISE_SPEED_TOLERANCE)

  def update_calculations(self, v_cruise_cluster: float) -> None:
    self.v_cruise_cluster = v_cruise_cluster if not np.isnan(v_cruise_cluster) else 0.0

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

    # ACTIVE, ADAPTING, PENDING, PRE_ACTIVE, INACTIVE
    if self.state != SpeedLimitAssistState.disabled:
      if not self.long_enabled or not self.enabled:
        self.state = SpeedLimitAssistState.disabled

      else:
        # ACTIVE
        if self.state == SpeedLimitAssistState.active:
          if self.v_cruise_cluster_changed:
            self.state = SpeedLimitAssistState.inactive
          elif self._speed_limit > 0 and self.v_offset < LIMIT_SPEED_OFFSET_TH:
            self.state = SpeedLimitAssistState.adapting

        # ADAPTING
        elif self.state == SpeedLimitAssistState.adapting:
          if self.v_cruise_cluster_changed:
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

        # INACTIVE
        elif self.state == SpeedLimitAssistState.inactive:
          pass

    # DISABLED
    elif self.state == SpeedLimitAssistState.disabled:
      if self.long_enabled and self.enabled:
        # start or reset preActive timer if initially enabled or manual set speed change detected
        if not self.long_enabled_prev or self.v_cruise_cluster_changed:
          self.long_engaged_timer = int(DISABLED_GUARD_PERIOD / DT_MDL)

        elif self.long_engaged_timer <= 0:
          if self.initial_max_set_confirmed():
            if self._speed_limit > 0:
              if self.v_offset < LIMIT_SPEED_OFFSET_TH:
                self.state = SpeedLimitAssistState.adapting
              else:
                self.state = SpeedLimitAssistState.active
            else:
              self.state = SpeedLimitAssistState.pending
          else:
            self.state = SpeedLimitAssistState.preActive
            self.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD / DT_MDL)

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES

    return enabled, active

  def update_events(self, events_sp: EventsSP) -> None:
    if self.state == SpeedLimitAssistState.preActive and self._state_prev != SpeedLimitAssistState.preActive:
      events_sp.add(EventNameSP.speedLimitPreActive)
    elif self.is_active:
      if self._state_prev not in ACTIVE_STATES:
        events_sp.add(EventNameSP.speedLimitActive)
      elif self.speed_limit_changed and self._speed_limit > 0:
        if self.speed_limit_prev <= 0:
          events_sp.add(EventNameSP.speedLimitActive)
        else:
          events_sp.add(EventNameSP.speedLimitChanged)

  def update(self, long_enabled: bool, long_override: bool, v_ego: float, a_ego: float, v_cruise_cluster: float,
             speed_limit: float, speed_limit_offset: float, distance: float, events_sp: EventsSP) -> None:
    self.long_enabled = long_enabled
    self.v_ego = v_ego
    self.a_ego = a_ego

    self._speed_limit = speed_limit
    self._speed_limit_offset = speed_limit_offset
    self._distance = distance

    self.update_params()
    self.update_calculations(v_cruise_cluster)
    self.is_enabled, self.is_active = self.update_state_machine()
    self.update_events(events_sp)

    # Update change tracking variables
    self.speed_limit_prev = self._speed_limit
    self.v_cruise_cluster_prev = self.v_cruise_cluster
    self.long_enabled_prev = self.long_enabled

    self.output_v_target = self.get_v_target_from_control()
    self.output_a_target = self.get_a_target_from_control()

    self.frame += 1
