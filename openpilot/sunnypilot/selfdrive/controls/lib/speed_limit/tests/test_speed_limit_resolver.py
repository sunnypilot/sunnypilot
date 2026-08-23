"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import random
import time

from openpilot.common.parameterized import parameterized

from openpilot.cereal import custom
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import LIMIT_MAX_MAP_DATA_AGE

from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_resolver import SpeedLimitResolver, ALL_SOURCES
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Policy
from openpilot.common.test import OpenpilotTestCase

SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimit.Source


def create_mock(properties, mocker):
  mock = mocker.MagicMock()
  for _property, value in properties.items():
    setattr(mock, _property, value)
  return mock


def setup_sm_mock(mocker):
  cruise_speed_limit = random.uniform(0, 120)
  live_map_data_limit = random.uniform(0, 120)

  car_state = create_mock({
    'gasPressed': False,
    'brakePressed': False,
    'standstill': False,
  }, mocker)
  car_state_sp = create_mock({
    'speedLimit': cruise_speed_limit,
  }, mocker)
  live_map_data = create_mock({
    'speedLimit': live_map_data_limit,
    'speedLimitValid': True,
    'speedLimitAhead': 0.,
    'speedLimitAheadValid': 0.,
    'speedLimitAheadDistance': 0.,
  }, mocker)
  gps_data = create_mock({
    'unixTimestampMillis': time.monotonic() * 1e3,
  }, mocker)
  sm_mock = mocker.MagicMock()
  sm_mock.__getitem__.side_effect = lambda key: {
    'carState': car_state,
    'liveMapDataSP': live_map_data,
    'carStateSP': car_state_sp,
    'gpsLocation': gps_data,
  }[key]
  sm_mock.logMonoTime = {'liveMapDataSP': time.monotonic_ns()}
  return sm_mock


parametrized_policies = parameterized.expand(
  [
    (Policy.car_state_only, 'carStateSP', SpeedLimitSource.car),
    (Policy.car_state_priority, 'carStateSP', SpeedLimitSource.car),
    (Policy.map_data_only, 'liveMapDataSP', SpeedLimitSource.map),
    (Policy.map_data_priority, 'liveMapDataSP', SpeedLimitSource.map),
  ],
  names=["policy", "sm_key", "function_key"]
)


def resolver_class():
  return SpeedLimitResolver


class TestSpeedLimitResolverValidation(OpenpilotTestCase):

  @parameterized.expand(list(Policy), names=["policy"])
  def test_initial_state(self, resolver_class, policy):
    resolver = resolver_class()
    resolver.policy = policy
    for source in ALL_SOURCES:
      if source in resolver.limit_solutions:
        assert resolver.limit_solutions[source] == 0.
        assert resolver.distance_solutions[source] == 0.

  @parametrized_policies
  def test_resolver(self, resolver_class, policy, sm_key, function_key, mocker):
    resolver = resolver_class()
    resolver.policy = policy
    sm_mock = setup_sm_mock(mocker)
    source_speed_limit = sm_mock[sm_key].speedLimit

    # Assert the resolver
    resolver.update(source_speed_limit, sm_mock)
    assert resolver.speed_limit == source_speed_limit
    assert resolver.source == ALL_SOURCES[function_key]

  def test_resolver_combined(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.combined
    sm_mock = setup_sm_mock(mocker)
    socket_to_source = {'carStateSP': SpeedLimitSource.car, 'liveMapDataSP': SpeedLimitSource.map}
    minimum_key, minimum_speed_limit = min(
      ((key, sm_mock[key].speedLimit) for key in
       socket_to_source.keys()), key=lambda x: x[1])

    # Assert the resolver
    resolver.update(minimum_speed_limit, sm_mock)
    assert resolver.speed_limit == minimum_speed_limit
    assert resolver.source == socket_to_source[minimum_key]

  def test_car_first_prefers_car_over_lower_current_map_limit(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.car_state_priority
    sm_mock = setup_sm_mock(mocker)
    sm_mock['carStateSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimit = 20.

    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 30.
    assert resolver.source == SpeedLimitSource.car

  def test_car_first_uses_lower_upcoming_map_limit(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.car_state_priority
    resolver.lookahead_lower_limits = True
    resolver.lookahead_speed_factor_down = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['carStateSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 100.

    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 20.
    assert resolver.source == SpeedLimitSource.map
    assert 99. < resolver.distance <= 100.

  def test_car_first_uses_higher_upcoming_map_limit(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.car_state_priority
    resolver.lookahead_speed_factor_up = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['carStateSP'].speedLimit = 20.
    sm_mock['liveMapDataSP'].speedLimit = 20.
    sm_mock['liveMapDataSP'].speedLimitAhead = 30.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 100.

    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 30.
    assert resolver.source == SpeedLimitSource.map
    assert 99. < resolver.distance <= 100.

  @parametrized_policies
  def test_parser(self, resolver_class, policy, sm_key, function_key, mocker):
    resolver = resolver_class()
    resolver.policy = policy
    sm_mock = setup_sm_mock(mocker)
    source_speed_limit = sm_mock[sm_key].speedLimit

    # Assert the parsing
    resolver.update(source_speed_limit, sm_mock)
    assert resolver.limit_solutions[ALL_SOURCES[function_key]] == source_speed_limit
    assert resolver.distance_solutions[ALL_SOURCES[function_key]] == 0.

  @parameterized.expand(list(Policy), names=["policy"])
  def test_resolve_interaction_in_update(self, resolver_class, policy, mocker):
    v_ego = 50
    resolver = resolver_class()
    resolver.policy = policy

    sm_mock = setup_sm_mock(mocker)
    resolver.update(v_ego, sm_mock)

    # After resolution
    assert resolver.speed_limit is not None
    assert resolver.distance is not None
    assert resolver.source is not None

  @parameterized.expand(list(Policy), names=["policy"])
  def test_old_map_data_ignored(self, resolver_class, policy, mocker):
    resolver = resolver_class()
    resolver.policy = policy
    sm_mock = setup_sm_mock(mocker)
    sm_mock.logMonoTime['liveMapDataSP'] = int((time.monotonic() - 2 * LIMIT_MAX_MAP_DATA_AGE) * 1e9)
    resolver._get_from_map_data(sm_mock)
    assert resolver.limit_solutions[SpeedLimitSource.map] == 0.
    assert resolver.distance_solutions[SpeedLimitSource.map] == 0.

  def test_map_speed_limit_ahead_distance_ages_from_log_mono_time(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.map_data_only
    resolver.lookahead_speed_factor_up = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock.logMonoTime['liveMapDataSP'] = int((time.monotonic() - 2.) * 1e9)
    sm_mock['liveMapDataSP'].speedLimit = 10.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 70.

    resolver.update(10., sm_mock)

    assert resolver.speed_limit == 20.
    assert 49. < resolver.distance < 51.

  def test_higher_map_speed_limit_ahead_applied_with_up_lookahead(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.map_data_only
    resolver.lookahead_speed_factor_up = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['liveMapDataSP'].speedLimit = 10.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 70.

    resolver.update(10., sm_mock)

    assert resolver.speed_limit == 20.
    assert 69. < resolver.distance <= 70.

  def test_higher_map_speed_limit_ahead_ignored_outside_up_lookahead(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.map_data_only
    resolver.lookahead_speed_factor_up = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['liveMapDataSP'].speedLimit = 10.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 80.

    resolver.update(10., sm_mock)

    assert resolver.speed_limit == 10.
    assert resolver.distance == 0.

  def test_lower_map_speed_limit_ahead_applied_with_down_lookahead(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.map_data_only
    resolver.lookahead_lower_limits = True
    resolver.lookahead_speed_factor_down = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['liveMapDataSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 100.

    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 20.
    assert 99. < resolver.distance <= 100.

  def test_lower_map_speed_limit_ahead_ignored_outside_down_lookahead(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.map_data_only
    resolver.lookahead_lower_limits = True
    resolver.lookahead_speed_factor_down = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['liveMapDataSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 120.

    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 30.
    assert resolver.distance == 0.
