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
    self.CP = CP
    self.policy = self.params.get("SpeedLimitControlPolicy", return_default=True)
    self.resolver = SpeedLimitResolver(self.policy)
    self.last_params_update = 0.0
    self.last_op_engaged_time = 0.0
    self.is_metric = self.params.get_bool("IsMetric")
    self.enabled = self.params.get_bool("SpeedLimitControl")
    self.op_engaged = False
    self.op_engaged_prev = False
    self.v_ego = 0.
    self.a_ego = 0.
    self.v_offset = 0.
    self.v_cruise_setpoint = 0.
    self.v_cruise_setpoint_prev = 0.
    self.v_cruise_setpoint_changed = False
    self.initial_max_set = False
    self._speed_limit = 0.
    self.speed_limit_prev = 0.
    self.speed_limit_changed = False
    self.last_valid_speed_limit_offsetted = 0.
    self._distance = 0.
    self._source = Source.none
    self.state = SpeedLimitControlState.inactive
    self.state_prev = SpeedLimitControlState.inactive
    self.pcm_cruise_op_long = CP.openpilotLongitudinalControl and CP.pcmCruise

    self.offset_type = OffsetType(self.params.get("SpeedLimitWarningValueOffset", return_default=True))
    self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
    self.warning_type = self.params.get("SpeedLimitWarningType", return_default=True)
    self.warning_offset_type = OffsetType(self.params.get("SpeedLimitWarningOffsetType", return_default=True))
    self.warning_offset_value = self.params.get("SpeedLimitWarningValueOffset", return_default=True)
    self.engage_type = self.read_engage_type_param()
    self.current_time = 0.
    self.v_cruise_rounded = 0.
    self.v_cruise_prev_rounded = 0.
    self.speed_limit_offsetted_rounded = 0.
    self.speed_limit_warning_offsetted_rounded = 0.
    self.speed_factor = CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH

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
    return self.state

  @state.setter
  def state(self, value) -> None:
    if value != self.state:
      debug(f'Speed Limit Controller state: {description_for_state(value)}')
    self.state = value

  @property
  def is_enabled(self) -> bool:
    return self.state in ENABLED_STATES and self.enabled

  @property
  def is_active(self) -> bool:
    return self.state in ACTIVE_STATES and self.enabled

  @property
  def speed_limit_offseted(self) -> float:
    # If we have a current valid speed limit, use it
    if self._speed_limit > 0:
      current_offsetted = self._speed_limit + self.speed_limit_offset
      self.last_valid_speed_limit_offsetted = current_offsetted
      return current_offsetted

    # If no current speed limit but we have a last valid one, use that
    if self.last_valid_speed_limit_offsetted > 0:
      return self.last_valid_speed_limit_offsetted

    # Fallback
    return FALLBACK_CRUISE_SPEED

  @property
  def speed_limit_offset(self) -> float:
    return self.get_offset(self.offset_type, self.offset_value)

  @property
  def speed_limit_warning_offset(self) -> float:
    return self.get_offset(self.warning_offset_type, self.warning_offset_value)

  @property
  def speed_limit(self) -> float:
    return self._speed_limit

  @property
  def distance(self) -> float:
    return self._distance

  @property
  def source(self) -> Source:
    return self._source

  def get_offset(self, offset_type: OffsetType, offset_value: int) -> float:
    if offset_type == OffsetType.default:
      return float(np.interp(self._speed_limit, LIMIT_PERC_OFFSET_BP, LIMIT_PERC_OFFSET_V) * self._speed_limit)
    elif offset_type == OffsetType.fixed:
      return offset_value * (CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS)
    elif offset_type == OffsetType.percentage:
      return offset_value * 0.01 * self._speed_limit
    else:
      raise NotImplementedError("Offset not supported")

  def update_v_cruise_setpoint_prev(self) -> None:
    self.v_cruise_setpoint_prev = self.v_cruise_setpoint

  def update_params(self) -> None:
    if self.current_time > self.last_params_update + PARAMS_UPDATE_PERIOD:
      self.enabled = self.params.get_bool("SpeedLimitControl")
      self.offset_type = OffsetType(self.params.get("SpeedLimitWarningValueOffset", return_default=True))
      self.offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
      self.warning_type = self.params.get("SpeedLimitWarningType", return_default=True)
      self.warning_offset_type = OffsetType(self.params.get("SpeedLimitWarningOffsetType", return_default=True))
      self.warning_offset_value = self.params.get("SpeedLimitWarningValueOffset", return_default=True)
      self.policy = Policy(self.params.get("SpeedLimitControlPolicy", return_default=True))
      self.is_metric = self.params.get_bool("IsMetric")
      self.speed_factor = CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH
      self.resolver.change_policy(self.policy)
      self.engage_type = self.read_engage_type_param()

      self.last_params_update = self.current_time

  @staticmethod
  def read_engage_type_param() -> Engage:
    return Engage.auto

  def initial_max_set_confirmed(self) -> bool:
    return abs(self.v_cruise_setpoint - REQUIRED_INITIAL_CRUISE_SPEED) <= CRUISE_SPEED_TOLERANCE

  def detect_manual_cruise_change(self) -> bool:
    if not self.is_active:
      return False

    # If cruise speed changed and it's not what SLC would set
    if self.v_cruise_setpoint_changed:
      expected_cruise = self.speed_limit_offseted
      return abs(self.v_cruise_setpoint - expected_cruise) > CRUISE_SPEED_TOLERANCE

    return False

  def update_calculations(self, v_ego: float, a_ego: float, v_cruise_setpoint: float) -> None:
    self.v_cruise_setpoint = v_cruise_setpoint if not np.isnan(v_cruise_setpoint) else 0.0
    self.v_ego = v_ego
    self.a_ego = a_ego

    # Update current velocity offset (error)
    self.v_offset = self.speed_limit_offseted - self.v_ego

    # Track the time op becomes active to prevent going to tempInactive right away after
    # op enabling since controlsd will change the cruise speed every time on enabling and this will
    # cause a temp inactive transition if the controller is updated before controlsd sets actual cruise
    # speed.
    if not self.op_engaged_prev and self.op_engaged:
      self.last_op_engaged_time = self.current_time

    # Update change tracking variables
    self.speed_limit_changed = self._speed_limit != self.speed_limit_prev
    self.v_cruise_setpoint_changed = self.v_cruise_setpoint != self.v_cruise_setpoint_prev
    self.speed_limit_prev = self._speed_limit
    self.update_v_cruise_setpoint_prev()  # always for Engage.auto
    self.op_engaged_prev = self.op_engaged

    self.v_cruise_rounded = int(round(self.v_cruise_setpoint * self.speed_factor))
    self.v_cruise_prev_rounded = int(round(self.v_cruise_setpoint_prev * self.speed_factor))
    self.speed_limit_offsetted_rounded = 0 if self._speed_limit == 0 else int(round((self._speed_limit + self.speed_limit_offset) * self.speed_factor))
    self.speed_limit_warning_offsetted_rounded = 0 if self._speed_limit == 0 else \
                                                  int(round((self._speed_limit + self.speed_limit_warning_offset) * self.speed_factor))

  def transition_state_from_inactive(self) -> None:
    self.state = SpeedLimitControlState.preActive
    self.initial_max_set = False

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
    elif self.v_cruise_setpoint_changed and self.current_time > (self.last_op_engaged_time + PRE_ACTIVE_GUARD_PERIOD):
      # User set cruise to something other than 80 MPH, permanently disable for this session
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
    self.state_prev = self.state

    # If op is disabled or SLC is disabled, go inactive
    if not self.op_engaged or not self.enabled:
      self.state = SpeedLimitControlState.inactive
      self.initial_max_set = False
      return

    self.state_transition_strategy[self.state]()

  def get_current_acceleration_as_target(self) -> float:
    return self.a_ego

  def get_adapting_state_target_acceleration(self) -> float:
    if self._distance > 0:
      return (self.speed_limit_offseted ** 2 - self.v_ego ** 2) / (2. * self._distance)

    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def get_active_state_target_acceleration(self) -> float:
    return self.v_offset / float(ModelConstants.T_IDXS[CONTROL_N])

  def update_events(self, events_sp: EventsSP) -> None:
    if self.is_active:
      if self.state == SpeedLimitControlState.preActive:
        events_sp.add(EventNameSP.speedLimitPreActive)
      elif self.state_prev not in ACTIVE_STATES:
        events_sp.add(EventNameSP.speedLimitActive)
      elif self.speed_limit_changed:
        events_sp.add(EventNameSP.speedLimitValueChange)

  def update(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise_setpoint: float, events_sp: EventsSP) -> float:
    self.op_engaged = sm['carControl'].longActive
    self.current_time = time.monotonic()

    self._speed_limit, self._distance, self._source = self.resolver.resolve(v_ego, self._speed_limit, sm)

    self.update_params()
    self.update_calculations(v_ego, a_ego, v_cruise_setpoint)
    self.state_control()
    self.update_events(events_sp)

    return self.speed_limit_offseted
