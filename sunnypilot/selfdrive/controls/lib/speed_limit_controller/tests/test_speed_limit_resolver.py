import random
import time

import pytest
from unittest.mock import MagicMock

from openpilot.selfdrive.controls.lib.drive_helpers import LIMIT_MAX_MAP_DATA_AGE

# from selfdrive.controls.lib.speed_limit_controller_tbd import SpeedLimitResolver as OriginalSpeedLimitResolver
from selfdrive.controls.lib.sunnypilot.speed_limit_resolver import SpeedLimitResolver as RefactoredSpeedLimitResolver
from openpilot.selfdrive.controls.lib.sunnypilot.common import Source
from openpilot.selfdrive.controls.lib.sunnypilot.common import Policy


def create_mock(properties):
  mock = MagicMock()
  for property, value in properties.items():
    setattr(mock, property, value)
  return mock


def setup_sm_mock():
  cruise_speed_limit = random.uniform(0, 120)
  nav_instruction_limit = random.uniform(0, 120)
  live_map_data_limit = random.uniform(0, 120)

  cruise_state = create_mock({'speedLimit': cruise_speed_limit})
  car_state = create_mock({
    'cruiseState': cruise_state,
    'gasPressed': False,
    'brakePressed': False,
    'standstill': False,
  })
  nav_instruction = create_mock({'speedLimit': nav_instruction_limit})
  live_map_data = create_mock({
    'speedLimit': live_map_data_limit,
    'speedLimitValid': True,
    'speedLimitAhead': 0.,
    'speedLimitAheadValid': 0.,
    'speedLimitAheadDistance': 0.,
    'lastGpsTimestamp': time.time() * 1e3,
  })
  sm_mock = MagicMock()
  sm_mock.__getitem__.side_effect = lambda key: {
    'carState': car_state,
    'navInstruction': nav_instruction,
    'liveMapDataSP': live_map_data,
  }[key]
  return sm_mock


parametrized_policies = pytest.mark.parametrize(
  "policy, sm_key, function_key", [
    (Policy.car_state_only, 'carState', 'car_state'),
    (Policy.car_state_priority, 'carState', 'car_state'),
    (Policy.map_data_only, 'liveMapDataSP', 'map_data'),
    (Policy.map_data_priority, 'liveMapDataSP', 'map_data'),
    (Policy.nav_only, 'navInstruction', 'nav'),
    (Policy.nav_priority, 'navInstruction', 'nav'),
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
  def test_resolver(self, resolver_class, policy, sm_key, function_key):
    resolver = resolver_class(policy)
    sm_mock = setup_sm_mock()
    source_speed_limit = sm_mock[sm_key].cruiseState.speedLimit if sm_key == 'carState' else sm_mock[sm_key].speedLimit

    # Assert the resolver
    speed_limit, _, source = resolver.resolve(source_speed_limit, 0, sm_mock)
    assert speed_limit == source_speed_limit
    assert source == Source[function_key]

  def test_resolver_combined(self, resolver_class):
    resolver = resolver_class(Policy.combined)
    sm_mock = setup_sm_mock()
    socket_to_source = {'carState': Source.car_state, 'liveMapDataSP': Source.map_data, 'navInstruction': Source.nav}
    minimum_key, minimum_speed_limit = min(
      ((key, sm_mock[key].cruiseState.speedLimit) if key == 'carState' else (key, sm_mock[key].speedLimit) for key in
       socket_to_source.keys()), key=lambda x: x[1])

    # Assert the resolver
    speed_limit, _, source = resolver.resolve(minimum_speed_limit, 0, sm_mock)
    assert speed_limit == minimum_speed_limit
    assert source == socket_to_source[minimum_key]

  @parametrized_policies
  def test_parser(self, resolver_class, policy, sm_key, function_key):
    resolver = resolver_class(policy)
    sm_mock = setup_sm_mock()
    source_speed_limit = sm_mock[sm_key].cruiseState.speedLimit if sm_key == 'carState' else sm_mock[sm_key].speedLimit

    # Assert the parsing
    speed_limit, _, source = resolver.resolve(source_speed_limit, 0, sm_mock)
    assert resolver._limit_solutions[Source[function_key]] == source_speed_limit
    assert resolver._distance_solutions[Source[function_key]] == 0.

  @pytest.mark.parametrize("policy", list(Policy), ids=lambda policy: policy.name)
  def test_resolve_interaction_in_update(self, resolver_class, policy):
    v_ego = 50
    resolver = resolver_class(policy)

    sm_mock = setup_sm_mock()
    _speed_limit, _distance, _source = resolver.resolve(v_ego, 0, sm_mock)

    # After resolution
    assert _speed_limit is not None
    assert _distance is not None
    assert _source is not None

  @pytest.mark.parametrize("policy", list(Policy), ids=lambda policy: policy.name)
  def test_old_map_data_ignored(self, resolver_class, policy):
    resolver = resolver_class(policy)
    sm_mock = MagicMock()
    sm_mock['liveMapDataSP'].lastGpsTimestamp = (time.time() - 2 * LIMIT_MAX_MAP_DATA_AGE) * 1e3
    resolver._sm = sm_mock
    resolver._get_from_map_data()
    assert resolver._limit_solutions[Source.map_data] == 0.
    assert resolver._distance_solutions[Source.map_data] == 0.
