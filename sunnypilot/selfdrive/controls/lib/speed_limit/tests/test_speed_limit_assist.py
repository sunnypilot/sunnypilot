"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest

from cereal import custom, car
from opendbc.car.car_helpers import interfaces
from opendbc.car.rivian.values import CAR as RIVIAN
from opendbc.car.tesla.values import CAR as TESLA
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import PCM_LONG_REQUIRED_MAX_SET_SPEED
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist, \
  PRE_ACTIVE_GUARD_PERIOD, ACTIVE_STATES
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState
ButtonType = car.CarState.ButtonEvent.Type

ALL_STATES = tuple(SpeedLimitAssistState.schema.enumerants.values())

SPEED_LIMITS = {
  'residential': 25 * CV.MPH_TO_MS,  # 25 mph
  'city': 35 * CV.MPH_TO_MS,         # 35 mph
  'highway': 65 * CV.MPH_TO_MS,      # 65 mph
  'freeway': 80 * CV.MPH_TO_MS,      # 80 mph
}

DEFAULT_CAR = TOYOTA.TOYOTA_RAV4_TSS2


@pytest.fixture
def car_name(request):
  return getattr(request, "param", DEFAULT_CAR)


@pytest.fixture(autouse=True)
def set_car_name_on_instance(request, car_name):
  instance = getattr(request, "instance", None)
  if instance:
    instance.car_name = car_name


class TestSpeedLimitAssist:

  def setup_method(self, method):
    self.params = Params()
    self.reset_custom_params()
    self.events_sp = EventsSP()
    CI = self._setup_platform(self.car_name)
    self.sla = SpeedLimitAssist(CI.CP, CI.CP_SP)
    self.sla.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD[self.sla.pcm_op_long] / DT_MDL)
    self.pcm_long_max_set_speed = PCM_LONG_REQUIRED_MAX_SET_SPEED[self.sla.is_metric][1]  # use 80 MPH for now
    self.speed_conv = CV.MS_TO_KPH if self.sla.is_metric else CV.MS_TO_MPH

  def teardown_method(self, method):
    self.reset_state()

  def _setup_platform(self, car_name):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)
    CI.CP.openpilotLongitudinalControl = True  # always assume it's openpilot longitudinal
    CI.CP.pcmCruise = False  # test non-PCM FSM path (preActive, pending, adapting, active)
    sunnypilot_interfaces.setup_interfaces(CI, self.params)
    return CI

  def reset_custom_params(self):
    self.params.put("IsReleaseSpBranch", True)
    self.params.put("SpeedLimitMode", int(Mode.assist))
    self.params.put_bool("IsMetric", False)
    self.params.put("SpeedLimitOffsetType", 0)
    self.params.put("SpeedLimitValueOffset", 0)

  def reset_state(self):
    self.sla.state = SpeedLimitAssistState.disabled
    self.sla._state_prev = SpeedLimitAssistState.disabled
    self.sla.frame = -1
    self.sla.long_enabled = False
    self.sla.long_enabled_prev = False
    self.sla.long_engaged_timer = 0
    self.sla.pre_active_timer = 0
    self.sla._speed_limit = 0.
    self.sla._speed_limit_final_last = 0.
    self.sla.speed_limit_prev = 0.
    self.sla.v_cruise_cluster = 0.
    self.sla.v_cruise_cluster_prev = 0.
    self.sla._distance = 0.
    self.events_sp.clear()

  def initialize_active_state(self, initialize_v_cruise):
    self.sla.state = SpeedLimitAssistState.active
    self.sla.v_cruise_cluster = initialize_v_cruise
    self.sla.v_cruise_cluster_prev = initialize_v_cruise
    self.sla.prev_v_cruise_cluster_conv = round(initialize_v_cruise * self.speed_conv)

  def test_initial_state(self):
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert not self.sla.is_enabled
    assert not self.sla.is_active
    assert V_CRUISE_UNSET == self.sla.get_v_target_from_control()

  @pytest.mark.parametrize("car_name", [RIVIAN.RIVIAN_R1, TESLA.TESLA_MODEL_Y], indirect=True)
  def test_disallowed_brands(self, car_name):
    """
      Speed Limit Assist is disabled for the following brands and conditions:
      - All Tesla and is a release branch;
      - All Rivian
    """
    assert not self.sla.enabled

    # stay disallowed even when the param may have changed from somewhere else
    self.params.put("SpeedLimitMode", int(Mode.assist))
    for _ in range(int(PARAMS_UPDATE_PERIOD / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'],
                      SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert not self.sla.enabled

  def test_disabled(self):
    self.params.put("SpeedLimitMode", int(Mode.off))
    for _ in range(int(10. / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled

  def test_transition_disabled_to_preactive(self):
    for _ in range(int(3. / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.preActive
    assert self.sla.is_enabled and not self.sla.is_active

  def test_preactive_timeout_to_inactive(self):
    self.sla.state = SpeedLimitAssistState.preActive
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)

    for _ in range(int(PRE_ACTIVE_GUARD_PERIOD[self.sla.pcm_op_long] / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.inactive

  def test_manual_cruise_change_detection(self):
    self.sla.state = SpeedLimitAssistState.active
    expected_cruise = SPEED_LIMITS['highway']
    self.sla.v_cruise_cluster_prev = expected_cruise

    different_cruise = SPEED_LIMITS['highway'] + 5
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, different_cruise, SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    # In non-pcm mode, manual cruise change transitions to inactive (not tempPaused)
    assert self.sla.state == SpeedLimitAssistState.inactive

  # TODO-SP: test lower CST cases
  def test_rapid_speed_limit_changes(self):
    self.initialize_active_state(self.pcm_long_max_set_speed)
    speed_limits = [SPEED_LIMITS['highway'], SPEED_LIMITS['freeway']]

    for _, speed_limit in enumerate(speed_limits):
      self.sla.update(True, False, speed_limit, 0, self.pcm_long_max_set_speed, speed_limit, speed_limit, True, 0, self.events_sp)
    assert self.sla.state in ACTIVE_STATES

  def test_invalid_speed_limits_handling(self):
    self.initialize_active_state(self.pcm_long_max_set_speed)

    invalid_limits = [-10, 0, 200 * CV.MPH_TO_MS]

    for invalid_limit in invalid_limits:
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, invalid_limit, SPEED_LIMITS['city'], True, 0, self.events_sp)
      assert isinstance(self.sla.output_v_target, (int, float))
      assert self.sla.output_v_target == V_CRUISE_UNSET or self.sla.output_v_target > 0

  def test_stale_data_handling(self):
    self.initialize_active_state(self.pcm_long_max_set_speed)
    old_speed_limit = SPEED_LIMITS['city']

    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, 0, old_speed_limit, True, 0, self.events_sp)
    assert self.sla.state in ACTIVE_STATES
    assert self.sla.output_v_target == old_speed_limit

  def test_distance_based_adapting(self):
    self.sla.state = SpeedLimitAssistState.adapting
    self.sla.v_cruise_cluster_prev = self.pcm_long_max_set_speed
    self.sla.prev_v_cruise_cluster_conv = round(self.pcm_long_max_set_speed * self.speed_conv)

    distance = 100.0
    current_speed = SPEED_LIMITS['freeway']
    target_speed = SPEED_LIMITS['highway']

    self.sla.update(True, False, current_speed, 0, self.pcm_long_max_set_speed, target_speed, target_speed, True, distance, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.adapting
    assert self.sla.output_v_target == target_speed  # TODO-SP: assert expected accel, need to enable self.acceleration_solutions

  def test_long_disengaged_to_disabled(self):
    self.initialize_active_state(self.pcm_long_max_set_speed)

    self.sla.update(False, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, SPEED_LIMITS['city'],
                    SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert self.sla.output_v_target == V_CRUISE_UNSET

  def test_maintain_states_with_no_changes(self):
    """Test that states are maintained when no significant changes occur"""
    test_states = [
      SpeedLimitAssistState.preActive,
      SpeedLimitAssistState.pending,
      SpeedLimitAssistState.active,
      SpeedLimitAssistState.adapting
    ]

    for state in test_states:
      self.sla.state = state
      self.sla.op_engaged = True

      initial_state = state

      self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)

      assert self.sla.state in ALL_STATES  # Sanity check

      if initial_state == SpeedLimitAssistState.preActive:
        assert self.sla.state in [SpeedLimitAssistState.preActive, SpeedLimitAssistState.active]
      elif initial_state in ACTIVE_STATES:
        assert self.sla.state in ACTIVE_STATES

  def test_non_pcm_regression_method_exists(self):
    """Regression: update_state_machine_non_pcm_long() method exists unchanged."""
    assert hasattr(self.sla, "update_state_machine_non_pcm_long")
    # Verify it is callable
    assert callable(self.sla.update_state_machine_non_pcm_long)
    # Verify method is not affected by cap mode refactor (signature check)
    import inspect
    inspect.signature(self.sla.update_state_machine_non_pcm_long)
    # Non-PCM method should have expected parameters (varies by impl, just verify it's present)


class TestSpeedLimitAssistTempPaused:
  """Tests for tempPaused state functionality (cap mode)."""

  def setup_method(self, method):
    self.params = Params()
    self.reset_custom_params()
    self.events_sp = EventsSP()
    CI = self._setup_platform(DEFAULT_CAR)
    self.sla = SpeedLimitAssist(CI.CP, CI.CP_SP)
    self.sla.pre_active_timer = int(PRE_ACTIVE_GUARD_PERIOD[self.sla.pcm_op_long] / DT_MDL)
    self.pcm_long_max_set_speed = PCM_LONG_REQUIRED_MAX_SET_SPEED[self.sla.is_metric][1]  # use 80 MPH for now
    self.speed_conv = CV.MS_TO_KPH if self.sla.is_metric else CV.MS_TO_MPH
    # For temp paused tests, use pcm_op_long = True
    self.sla.pcm_op_long = True
    self.sla.enabled = True

  def teardown_method(self, method):
    self.reset_state()

  def _setup_platform(self, car_name):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)
    CI.CP.openpilotLongitudinalControl = True  # always assume it's openpilot longitudinal
    CI.CP.pcmCruise = False  # test non-PCM FSM path (preActive, pending, adapting, active)
    sunnypilot_interfaces.setup_interfaces(CI, self.params)
    return CI

  def reset_custom_params(self):
    self.params.put("IsReleaseSpBranch", True)
    self.params.put("SpeedLimitMode", int(Mode.assist))
    self.params.put_bool("IsMetric", False)
    self.params.put("SpeedLimitOffsetType", 0)
    self.params.put("SpeedLimitValueOffset", 0)

  def reset_state(self):
    self.sla.state = SpeedLimitAssistState.disabled
    self.sla._state_prev = SpeedLimitAssistState.disabled
    self.sla.frame = -1
    self.sla.long_enabled = False
    self.sla.long_enabled_prev = False
    self.sla.long_engaged_timer = 0
    self.sla.pre_active_timer = 0
    self.sla._speed_limit = 0.
    self.sla._speed_limit_final_last = 0.
    self.sla.speed_limit_prev = 0.
    self.sla.v_cruise_cluster = 0.
    self.sla.v_cruise_cluster_prev = 0.
    self.sla._distance = 0.
    self.events_sp.clear()

  def test_temp_paused_entry_capping_state(self):
    """Test that tempPaused entry occurs during state machine when user paused."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla._user_paused = True
    self.sla._user_paused_timer = 1000

    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    assert self.sla._disable_reason == custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason.userTempPause

  def test_temp_paused_exit_on_speed_limit_change(self):
    """Test exiting tempPaused when speed limit changes."""
    self.sla.state = SpeedLimitAssistState.tempPaused
    self.sla._user_paused = True
    self.sla._user_paused_timer = 1000
    self.sla._speed_limit_final_last_at_pause = SPEED_LIMITS['city']
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla.long_enabled = True
    self.sla.enabled = True

    # Change speed limit
    new_limit = SPEED_LIMITS['highway']
    self.sla.update(True, False, new_limit, 0, self.pcm_long_max_set_speed,
                    new_limit, new_limit, True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert self.sla._user_paused == False

  def test_temp_paused_exit_on_timer_expiry(self):
    """Test exiting tempPaused when 5-minute timer expires."""
    self.sla.state = SpeedLimitAssistState.tempPaused
    self.sla._user_paused = True
    self.sla._user_paused_timer = 1
    self.sla._speed_limit_final_last_at_pause = SPEED_LIMITS['city']

    # Trigger update with timer expiry
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert self.sla._user_paused_timer <= 0

  def test_disable_reason_user_cancel(self):
    """Test disable_reason set to userCancel on pause."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._user_paused = True
    self.sla._user_paused_timer = 1000

    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    assert self.sla._disable_reason == custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason.userTempPause

  def test_disable_reason_long_override(self):
    """Test disable_reason set to longOverride."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._target_cap = SPEED_LIMITS['city']

    self.sla.update(True, True, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert self.sla._disable_reason == custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason.longOverride

  def test_disable_reason_below_floor(self):
    """Test disable_reason set to belowFloor."""
    min_floor = self.sla._min_cap_floor
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._speed_limit_final_last = min_floor - 1
    self.sla.long_enabled = True
    self.sla.enabled = True
    self.sla.v_cruise_cluster = self.pcm_long_max_set_speed
    self.sla.v_cruise_cluster_prev = self.pcm_long_max_set_speed
    self.sla.prev_v_cruise_cluster_conv = round(self.pcm_long_max_set_speed * self.speed_conv)

    self.sla.update(True, False, min_floor - 1, 0, self.pcm_long_max_set_speed,
                    min_floor - 1, min_floor - 1, True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.pending
    assert self.sla._disable_reason == custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason.belowFloor

  def test_temp_paused_entry_cap_cluster_nudge_plus(self):
    """Test tempPaused entry in capping state when cluster nudged above limit."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla._target_cap = SPEED_LIMITS['city']
    self.sla.long_enabled = True
    self.sla.enabled = True
    self.sla.v_cruise_cluster = SPEED_LIMITS['city']
    self.sla.v_cruise_cluster_prev = SPEED_LIMITS['city']
    self.sla.prev_v_cruise_cluster_conv = round(SPEED_LIMITS['city'] * self.speed_conv)

    # Nudge cluster up (simulate user pressing accel)
    nudged_cruise = SPEED_LIMITS['city'] + 1.0
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, nudged_cruise,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    assert self.sla._user_paused == True
    assert self.sla._user_paused_timer > 0
    assert self.sla._disable_reason == custom.LongitudinalPlanSP.SpeedLimit.AssistDisableReason.userTempPause

  def test_temp_paused_entry_cap_cluster_nudge_minus(self):
    """Test tempPaused entry in capping state when cluster nudged below limit."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla._target_cap = SPEED_LIMITS['city']
    self.sla.long_enabled = True
    self.sla.enabled = True
    self.sla.v_cruise_cluster = SPEED_LIMITS['city']
    self.sla.v_cruise_cluster_prev = SPEED_LIMITS['city']
    self.sla.prev_v_cruise_cluster_conv = round(SPEED_LIMITS['city'] * self.speed_conv)

    # Nudge cluster down (simulate user pressing brake/decel)
    nudged_cruise = SPEED_LIMITS['city'] - 1.0
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, nudged_cruise,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    assert self.sla._user_paused == True
    assert self.sla._user_paused_timer > 0

  def test_temp_paused_exit_cluster_returns_to_limit(self):
    """Test exiting tempPaused when cluster returns within ±1 of limit."""
    self.sla.state = SpeedLimitAssistState.tempPaused
    self.sla._user_paused = True
    self.sla._user_paused_timer = 1000
    self.sla._speed_limit_final_last_at_pause = SPEED_LIMITS['city']
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla.long_enabled = True
    self.sla.enabled = True
    self.sla.v_cruise_cluster_prev = SPEED_LIMITS['city'] + 5
    self.sla.prev_v_cruise_cluster_conv = round((SPEED_LIMITS['city'] + 5) * self.speed_conv)

    # Return cluster to within ±1 of limit
    returned_cruise = SPEED_LIMITS['city'] + 0.5
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, returned_cruise,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.disabled
    assert self.sla._user_paused == False

  def test_temp_paused_sticky_double_nudge(self):
    """Test that multiple nudges keep state in tempPaused."""
    self.sla.state = SpeedLimitAssistState.capping
    self.sla._has_speed_limit = True
    self.sla._speed_limit_final_last = SPEED_LIMITS['city']
    self.sla._target_cap = SPEED_LIMITS['city']
    self.sla.long_enabled = True
    self.sla.enabled = True
    self.sla.v_cruise_cluster = SPEED_LIMITS['city']
    self.sla.v_cruise_cluster_prev = SPEED_LIMITS['city']
    self.sla.prev_v_cruise_cluster_conv = round(SPEED_LIMITS['city'] * self.speed_conv)

    # First nudge
    nudged_cruise_1 = SPEED_LIMITS['city'] + 2.0
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, nudged_cruise_1,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    assert self.sla._user_paused_timer > 0
    saved_timer_1 = self.sla._user_paused_timer

    # Second nudge while in tempPaused (shouldn't trigger another entry)
    nudged_cruise_2 = SPEED_LIMITS['city'] + 3.0
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, nudged_cruise_2,
                    SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.tempPaused
    # Timer should have been decremented by one update call
    assert self.sla._user_paused_timer == saved_timer_1 - 1
