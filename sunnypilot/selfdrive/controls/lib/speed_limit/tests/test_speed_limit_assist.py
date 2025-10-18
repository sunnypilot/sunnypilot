"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom

from opendbc.car.car_helpers import interfaces
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import PCM_LONG_REQUIRED_MAX_SET_SPEED
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist, \
  PRE_ACTIVE_GUARD_PERIOD, ACTIVE_STATES
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState

ALL_STATES = tuple(SpeedLimitAssistState.schema.enumerants.values())

SPEED_LIMITS = {
  'residential': 25 * CV.MPH_TO_MS,  # 25 mph
  'city': 35 * CV.MPH_TO_MS,         # 35 mph
  'highway': 65 * CV.MPH_TO_MS,      # 65 mph
  'freeway': 80 * CV.MPH_TO_MS,      # 80 mph
}


class TestSpeedLimitAssist:

  def setup_method(self):
    self.params = Params()
    self.reset_custom_params()
    self.events_sp = EventsSP()
    CI = self._setup_platform(TOYOTA.TOYOTA_RAV4_TSS2)
    self.sla = SpeedLimitAssist(CI.CP)
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
    sunnypilot_interfaces.setup_interfaces(CI, self.params)
    return CI

  def reset_custom_params(self):
    self.params.put("SpeedLimitMode", int(Mode.assist))
    self.params.put_bool("IsMetric", False)
    self.params.put("SpeedLimitOffsetType", 0)
    self.params.put("SpeedLimitValueOffset", 0)

  def reset_state(self):
    self.sla.state = SpeedLimitAssistState.disabled
    self.sla.frame = -1
    self.sla.last_op_engaged_frame = 0
    self.sla.op_engaged = False
    self.sla.op_engaged_prev = False
    self.sla._speed_limit = 0.
    self.sla.speed_limit_prev = 0.
    self.sla.last_valid_speed_limit_offsetted = 0.
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

  def test_transition_disabled_to_pending_no_speed_limit_not_max_initial_set_speed(self):
    for _ in range(int(3. / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['highway'], 0, SPEED_LIMITS['city'], 0, 0, False, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.pending
    assert self.sla.is_enabled and not self.sla.is_active

  def test_preactive_to_active_with_max_speed_confirmation(self):
    self.sla.state = SpeedLimitAssistState.preActive
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, SPEED_LIMITS['highway'],
                    SPEED_LIMITS['highway'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.active
    assert self.sla.is_enabled and self.sla.is_active
    assert self.sla.output_v_target == SPEED_LIMITS['highway']

  def test_preactive_timeout_to_inactive(self):
    self.sla.state = SpeedLimitAssistState.preActive
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)

    for _ in range(int(PRE_ACTIVE_GUARD_PERIOD[self.sla.pcm_op_long] / DT_MDL)):
      self.sla.update(True, False, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.inactive

  def test_preactive_to_pending_no_speed_limit(self):
    self.sla.state = SpeedLimitAssistState.preActive
    self.sla.update(True, False, SPEED_LIMITS['highway'], 0, self.pcm_long_max_set_speed, 0, 0, False, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.pending
    assert self.sla.is_enabled and not self.sla.is_active

  def test_pending_to_active_when_speed_limit_available(self):
    self.sla.state = SpeedLimitAssistState.pending
    self.sla.v_cruise_cluster_prev = self.pcm_long_max_set_speed
    self.sla.prev_v_cruise_cluster_conv = round(self.pcm_long_max_set_speed * self.speed_conv)

    self.sla.update(True, False, SPEED_LIMITS['highway'], 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['highway'], SPEED_LIMITS['highway'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.active

  def test_pending_to_adapting_when_below_speed_limit(self):
    self.sla.state = SpeedLimitAssistState.pending
    self.sla.v_cruise_cluster_prev = self.pcm_long_max_set_speed
    self.sla.prev_v_cruise_cluster_conv = round(self.pcm_long_max_set_speed * self.speed_conv)

    self.sla.update(True, False, SPEED_LIMITS['highway'] + 5, 0, self.pcm_long_max_set_speed,
                    SPEED_LIMITS['highway'], SPEED_LIMITS['highway'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.adapting
    assert self.sla.is_enabled and self.sla.is_active

  def test_active_to_adapting_transition(self):
    self.initialize_active_state(self.pcm_long_max_set_speed)

    self.sla.update(True, False, SPEED_LIMITS['highway'] + 2, 0, self.pcm_long_max_set_speed, SPEED_LIMITS['highway'],
                    SPEED_LIMITS['highway'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.adapting

  def test_adapting_to_active_transition(self):
    self.sla.state = SpeedLimitAssistState.adapting
    self.sla.v_cruise_cluster_prev = self.pcm_long_max_set_speed
    self.sla.prev_v_cruise_cluster_conv = round(self.pcm_long_max_set_speed * self.speed_conv)

    self.sla.update(True, False, SPEED_LIMITS['city'], 0, self.pcm_long_max_set_speed, SPEED_LIMITS['highway'],
                    SPEED_LIMITS['highway'], True, 0, self.events_sp)
    assert self.sla.state == SpeedLimitAssistState.active

  def test_manual_cruise_change_detection(self):
    self.sla.state = SpeedLimitAssistState.active
    expected_cruise = SPEED_LIMITS['highway']
    self.sla.v_cruise_cluster_prev = expected_cruise

    different_cruise = SPEED_LIMITS['highway'] + 5
    self.sla.update(True, False, SPEED_LIMITS['city'], 0, different_cruise, SPEED_LIMITS['city'], SPEED_LIMITS['city'], True, 0, self.events_sp)
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
