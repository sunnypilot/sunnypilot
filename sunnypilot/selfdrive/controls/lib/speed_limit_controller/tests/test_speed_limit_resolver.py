import random
import time

import pytest
from pytest_mock import MockerFixture

from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import LIMIT_MAX_MAP_DATA_AGE

# from selfdrive.controls.lib.speed_limit_controller_tbd import SpeedLimitResolver as OriginalSpeedLimitResolver
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver as RefactoredSpeedLimitResolver
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Policy


def create_mock(properties, mocker: MockerFixture):
  mock = mocker.MagicMock()
  for _property, value in properties.items():
    setattr(mock, _property, value)
  return mock


def setup_sm_mock(mocker: MockerFixture):
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
    'unixTimestampMillis': time.time() * 1e3,
  }, mocker)
  sm_mock = mocker.MagicMock()
  sm_mock.__getitem__.side_effect = lambda key: {
    'carState': car_state,
    'liveMapDataSP': live_map_data,
    'carStateSP': car_state_sp,
    'gpsLocation': gps_data,
  }[key]
  return sm_mock


parametrized_policies = pytest.mark.parametrize(
  "policy, sm_key, function_key", [
    (Policy.car_state_only, 'carStateSP', 'car_state'),
    (Policy.car_state_priority, 'carStateSP', 'car_state'),
    (Policy.map_data_only, 'liveMapDataSP', 'map_data'),
    (Policy.map_data_priority, 'liveMapDataSP', 'map_data'),
  ],
  ids=lambda val: val.name if hasattr(val, 'name') else str(val)
)


@pytest.mark.parametrize("resolver_class", [RefactoredSpeedLimitResolver], ids=["Refactored"])
class TestSpeedLimitResolverValidation:

  @pytest.mark.parametrize("policy", list(Policy), ids=lambda policy: policy.name)
  def test_initial_state(self, resolver_class, policy):
    resolver = resolver_class(policy)
    for source in Source:
      if source in resolver._limit_solutions:
        assert resolver._limit_solutions[source] == 0.
        assert resolver._distance_solutions[source] == 0.

  @parametrized_policies
  def test_resolver(self, resolver_class, policy, sm_key, function_key, mocker: MockerFixture):
    resolver = resolver_class(policy)
    sm_mock = setup_sm_mock(mocker)
    source_speed_limit = sm_mock[sm_key].speedLimit

    # Assert the resolver
    speed_limit, _, source = resolver.resolve(source_speed_limit, 0, sm_mock)
    assert speed_limit == source_speed_limit
    assert source == Source[function_key]

  def test_resolver_combined(self, resolver_class, mocker: MockerFixture):
    resolver = resolver_class(Policy.combined)
    sm_mock = setup_sm_mock(mocker)
    socket_to_source = {'carStateSP': Source.car_state, 'liveMapDataSP': Source.map_data}
    minimum_key, minimum_speed_limit = min(
      ((key, sm_mock[key].speedLimit) for key in
       socket_to_source.keys()), key=lambda x: x[1])

    # Assert the resolver
    speed_limit, _, source = resolver.resolve(minimum_speed_limit, 0, sm_mock)
    assert speed_limit == minimum_speed_limit
    assert source == socket_to_source[minimum_key]

  @parametrized_policies
  def test_parser(self, resolver_class, policy, sm_key, function_key, mocker: MockerFixture):
    resolver = resolver_class(policy)
    sm_mock = setup_sm_mock(mocker)
    source_speed_limit = sm_mock[sm_key].speedLimit

    # Assert the parsing
    speed_limit, _, source = resolver.resolve(source_speed_limit, 0, sm_mock)
    assert resolver._limit_solutions[Source[function_key]] == source_speed_limit
    assert resolver._distance_solutions[Source[function_key]] == 0.

  @pytest.mark.parametrize("policy", list(Policy), ids=lambda policy: policy.name)
  def test_resolve_interaction_in_update(self, resolver_class, policy, mocker: MockerFixture):
    v_ego = 50
    resolver = resolver_class(policy)

    sm_mock = setup_sm_mock(mocker)
    _speed_limit, _distance, _source = resolver.resolve(v_ego, 0, sm_mock)

    # After resolution
    assert _speed_limit is not None
    assert _distance is not None
    assert _source is not None

  @pytest.mark.parametrize("policy", list(Policy), ids=lambda policy: policy.name)
  def test_old_map_data_ignored(self, resolver_class, policy, mocker: MockerFixture):
    resolver = resolver_class(policy)
    sm_mock = mocker.MagicMock()
    sm_mock['gpsLocation'].unixTimestampMillis = (time.time() - 2 * LIMIT_MAX_MAP_DATA_AGE) * 1e3
    resolver._get_from_map_data(sm_mock)
    assert resolver._limit_solutions[Source.map_data] == 0.
    assert resolver._distance_solutions[Source.map_data] == 0.
