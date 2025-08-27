import numpy as np
import time

from cereal import messaging, custom
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V, \
  PARAMS_UPDATE_PERIOD, LIMIT_SPEED_OFFSET_TH, SpeedLimitControlState, PRE_ACTIVE_GUARD_PERIOD, REQUIRED_INITIAL_CRUISE_SPEED, \
  CRUISE_SPEED_TOLERANCE, FALLBACK_CRUISE_SPEED
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Policy, Engage, OffsetType
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.helpers import description_for_state, debug
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.selfdrive.modeld.constants import ModelConstants

EventNameSP = custom.OnroadEventSP.EventName

ACTIVE_STATES = (SpeedLimitControlState.active, SpeedLimitControlState.adapting)
ENABLED_STATES = (SpeedLimitControlState.preActive, SpeedLimitControlState.pending, *ACTIVE_STATES)


class SpeedLimitController:
  _speed_limit: float
  _distance: float
  _source: Source
  _v_ego: float
  _a_ego: float
  _v_offset: float

  def __init__(self, CP):
    self.params = Params()
    self._CP = CP
    self._policy = self.params.get("SpeedLimitControlPolicy", return_default=True)
    self._resolver = SpeedLimitResolver(self._policy)
    self._last_params_update = 0.0
    self._last_op_engaged_time = 0.0
    self._is_metric = self.params.get_bool("IsMetric")
    self._enabled = self.params.get_bool("SpeedLimitControl")
    self._op_engaged = False
    self._op_engaged_prev = False
    self._v_ego = 0.
    self._a_ego = 0.
    self._v_offset = 0.
    self._v_cruise_setpoint = 0.
    self._v_cruise_setpoint_prev = 0.
    self._v_cruise_setpoint_changed = False
    self._initial_max_set = False
    self._speed_limit = 0.
    self._speed_limit_prev = 0.
    self._speed_limit_changed = False
    self._last_valid_speed_limit_offsetted = 0.
    self._distance = 0.
    self._source = Source.none
    self._state = SpeedLimitControlState.inactive
    self._state_prev = SpeedLimitControlState.inactive
    self._pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self._offset_type = OffsetType(self.params.get("SpeedLimitWarningValueOffset", return_default=True))
    self._offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
    self._warning_type = self.params.get("SpeedLimitWarningType", return_default=True)
    self._warning_offset_type = OffsetType(self.params.get("SpeedLimitWarningOffsetType", return_default=True))
    self._warning_offset_value = self.params.get("SpeedLimitWarningValueOffset", return_default=True)
    self._engage_type = self._read_engage_type_param()
    self._current_time = 0.
    self._v_cruise_rounded = 0.
    self._v_cruise_prev_rounded = 0.
    self._speed_limit_offsetted_rounded = 0.
    self._speed_limit_warning_offsetted_rounded = 0.
    self._speed_factor = CV.MS_TO_KPH if self._is_metric else CV.MS_TO_MPH

    # Mapping functions to state transitions
    self.state_transition_strategy = {
      SpeedLimitControlState.inactive: self.transition_state_from_inactive,
      SpeedLimitControlState.preActive: self.transition_state_from_preactive,
      SpeedLimitControlState.pending: self.transition_state_from_pending,
      SpeedLimitControlState.adapting: self.transition_state_from_adapting,
      SpeedLimitControlState.active: self.transition_state_from_active,
    }

    # Solution functions mapped to respective states  
    self.acceleration_solutions = {
      SpeedLimitControlState.inactive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.preActive: self.get_current_acceleration_as_target,
      SpeedLimitControlState.pending: self.get_current_acceleration_as_target,
      SpeedLimitControlState.adapting: self.get_adapting_state_target_acceleration,
      SpeedLimitControlState.active: self.get_active_state_target_acceleration,
    }

  @property
  def state(self) -> SpeedLimitControlState:
    return self._state

  @state.setter
  def state(self, value) -> None:
    if value != self._state:
      debug(f'Speed Limit Controller state: {description_for_state(value)}')
    self._state = value

  @property
  def is_enabled(self) -> bool:
    return self.state in ENABLED_STATES and self._enabled

  @property
  def is_active(self) -> bool:
    return self.state in ACTIVE_STATES and self._enabled

  @property
  def speed_limit_offseted(self) -> float:
    # If we have a current valid speed limit, use it
    if self._speed_limit > 0:
      current_offsetted = self._speed_limit + self.speed_limit_offset
      self._last_valid_speed_limit_offsetted = current_offsetted
      return current_offsetted

    # If no current speed limit but we have a last valid one, use that
    if self._last_valid_speed_limit_offsetted > 0:
      return self._last_valid_speed_limit_offsetted

    # Fallback
    return FALLBACK_CRUISE_SPEED

  @property
  def speed_limit_offset(self) -> float:
    return self._get_offset(self._offset_type, self._offset_value)

  @property
  def speed_limit_warning_offset(self) -> float:
    return self._get_offset(self._warning_offset_type, self._warning_offset_value)

  @property
  def speed_limit(self) -> float:
    return self._speed_limit

  @property
  def distance(self) -> float:
    return self._distance

  @property
  def source(self) -> Source:
    return self._source

  def _get_offset(self, offset_type: OffsetType, offset_value: int) -> float:
    if offset_type == OffsetType.default:
      return float(np.interp(self._speed_limit, LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V) * self._speed_limit)
    elif offset_type == OffsetType.fixed:
      return offset_value * (CV.KPH_TO_MS if self._is_metric else CV.MPH_TO_MS)
    elif offset_type == OffsetType.percentage:
      return offset_value * 0.01 * self._speed_limit
    else:
      raise NotImplementedError("Offset not supported")

  def _update_v_cruise_setpoint_prev(self) -> None:
    self._v_cruise_setpoint_prev = self._v_cruise_setpoint

  def _update_params(self) -> None:
    if self._current_time > self._last_params_update + PARAMS_UPDATE_PERIOD:
      self._enabled = self.params.get_bool("SpeedLimitControl")
      self._offset_type = OffsetType(self.params.get("SpeedLimitWarningValueOffset", return_default=True))
      self._offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
      self._warning_type = self.params.get("SpeedLimitWarningType", return_default=True)
      self._warning_offset_type = OffsetType(self.params.get("SpeedLimitWarningOffsetType", return_default=True))
      self._warning_offset_value = self.params.get("SpeedLimitWarningValueOffset", return_default=True)
      self._policy = Policy(self.params.get("SpeedLimitControlPolicy", return_default=True))
      self._is_metric = self.params.get_bool("IsMetric")
      self._speed_factor = CV.MS_TO_KPH if self._is_metric else CV.MS_TO_MPH
      self._resolver.change_policy(self._policy)
      self._engage_type = self._read_engage_type_param()

      self._last_params_update = self._current_time

  @staticmethod
  def _read_engage_type_param() -> Engage:
    return Engage.auto

  def _initial_max_set_confirmed(self) -> bool:
    return abs(self._v_cruise_setpoint - REQUIRED_INITIAL_CRUISE_SPEED) <= CRUISE_SPEED_TOLERANCE

  def _detect_manual_cruise_change(self) -> bool:
    if not self.is_active:
      return False

    # If cruise speed changed and it's not what SLC would set
    if self._v_cruise_setpoint_changed:
      expected_cruise = self.speed_limit_offseted
      return abs(self._v_cruise_setpoint - expected_cruise) > CRUISE_SPEED_TOLERANCE

    return False

  def _update_calculations(self, v_ego: float, a_ego: float, v_cruise_setpoint: float) -> None:
    self._v_cruise_setpoint = v_cruise_setpoint if not np.isnan(v_cruise_setpoint) else 0.0
    self._v_ego = v_ego
    self._a_ego = a_ego

    # Update current velocity offset (error)
    self._v_offset = self.speed_limit_offseted - self._v_ego

    # Track the time op becomes active to prevent going to tempInactive right away after
    # op enabling since controlsd will change the cruise speed every time on enabling and this will
    # cause a temp inactive transition if the controller is updated before controlsd sets actual cruise
    # speed.
    if not self._op_engaged_prev and self._op_engaged:
      self._last_op_engaged_time = self._current_time

    # Update change tracking variables
    self._speed_limit_changed = self._speed_limit != self._speed_limit_prev
    self._v_cruise_setpoint_changed = self._v_cruise_setpoint != self._v_cruise_setpoint_prev
    self._speed_limit_prev = self._speed_limit
    self._update_v_cruise_setpoint_prev()  # always for Engage.auto
    self._op_engaged_prev = self._op_engaged

    self._v_cruise_rounded = int(round(self._v_cruise_setpoint * self._speed_factor))
    self._v_cruise_prev_rounded = int(round(self._v_cruise_setpoint_prev * self._speed_factor))
    self._speed_limit_offsetted_rounded = 0 if self._speed_limit == 0 else int(round((self._speed_limit + self.speed_limit_offset) * self._speed_factor))
    self._speed_limit_warning_offsetted_rounded = 0 if self._speed_limit == 0 else \
                                                  int(round((self._speed_limit + self.speed_limit_warning_offset) * self._speed_factor))

  def transition_state_from_inactive(self) -> None:
    self.state = SpeedLimitControlState.preActive
    self._initial_max_set = False

  def transition_state_from_preactive(self) -> None:
    if self._initial_max_set_confirmed():
      self._initial_max_set = True
      if self._speed_limit > 0:
        if self._v_offset < LIMIT_SPEED_OFFSET_TH:
          self.state = SpeedLimitControlState.adapting
        else:
          self.state = SpeedLimitControlState.active
      else:
        self.state = SpeedLimitControlState.pending
    elif self._v_cruise_setpoint_changed and self._current_time > (self._last_op_engaged_time + PRE_ACTIVE_GUARD_PERIOD):
      # User set cruise to something other than 80 MPH, permanently disable for this session
      self.state = SpeedLimitControlState.inactive

  def transition_state_from_pending(self) -> None:
    if self._speed_limit > 0:
      if self._v_offset < LIMIT_SPEED_OFFSET_TH:
        self.state = SpeedLimitControlState.adapting
      else:
        self.state = SpeedLimitControlState.active

  def transition_state_from_adapting(self) -> None:
    if self._detect_manual_cruise_change():
      self.state = SpeedLimitControlState.inactive
    elif self._v_offset >= LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.active

  def transition_state_from_active(self) -> None:
    if self._detect_manual_cruise_change():
      self.state = SpeedLimitControlState.inactive
    elif self._speed_limit > 0 and self._v_offset < LIMIT_SPEED_OFFSET_TH:
      self.state = SpeedLimitControlState.adapting

  def _state_transition(self) -> None:
    self._state_prev = self._state

    # If op is disabled or SLC is disabled, go inactive
    if not self._op_engaged or not self._enabled:
      self.state = SpeedLimitControlState.inactive
      self._initial_max_set = False
      return

    self.state_transition_strategy[self.state]()

  def get_current_acceleration_as_target(self) -> float:
    return self._a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    if self.distance > 0:
      return (self.speed_limit_offseted ** 2 - self._v_ego ** 2) / (2. * self.distance)

    return self._v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def get_active_state_target_acceleration(self) -> float:
    return self._v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def _update_events(self, events_sp: EventsSP) -> None:
    if self.is_active:
      if self.state == SpeedLimitControlState.preActive:
        events_sp.add(EventNameSP.speedLimitPreActive)
      elif self._state_prev not in ACTIVE_STATES:
        events_sp.add(EventNameSP.speedLimitActive)
      elif self._speed_limit_changed:
        events_sp.add(EventNameSP.speedLimitValueChange)

  def update(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise_setpoint: float, events_sp: EventsSP) -> float:
    self._op_engaged = sm['carControl'].longActive
    self._current_time = time.monotonic()

    self._speed_limit, self._distance, self._source = self._resolver.resolve(v_ego, self.speed_limit, sm)

    self._update_params()
    self._update_calculations(v_ego, a_ego, v_cruise_setpoint)
    self._state_transition()
    self._update_events(events_sp)

    return self.speed_limit_offseted
