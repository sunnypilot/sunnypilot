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


def confirm_ahead(resolver, sm, v_ego):
  resolver.v_ego = v_ego
  stamp = sm.logMonoTime['liveMapDataSP'] * 1e-9
  data = sm['liveMapDataSP']
  resolver._confirm_map_ahead(data.speedLimitAhead, data.speedLimitAheadDistance + 2. * v_ego, stamp - 2.)
  resolver._confirm_map_ahead(data.speedLimitAhead, data.speedLimitAheadDistance, stamp)


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

    confirm_ahead(resolver, sm_mock, 15.)
    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 20.
    assert resolver.source == SpeedLimitSource.map
    assert 99. < resolver.distance <= 100.
    assert resolver.lower_lookahead_active

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

    confirm_ahead(resolver, sm_mock, 15.)
    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 30.
    assert resolver.source == SpeedLimitSource.map
    assert 99. < resolver.distance <= 100.
    assert not resolver.lower_lookahead_active

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

    confirm_ahead(resolver, sm_mock, 10.)
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

    confirm_ahead(resolver, sm_mock, 10.)
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

    confirm_ahead(resolver, sm_mock, 15.)
    resolver.update(15., sm_mock)

    assert resolver.speed_limit == 20.
    assert 99. < resolver.distance <= 100.
    assert resolver.lower_lookahead_active

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
    assert not resolver.lower_lookahead_active

  def test_lower_lookahead_active_requires_map_source_selection(self, resolver_class, mocker):
    resolver = resolver_class()
    resolver.policy = Policy.combined
    resolver.lookahead_lower_limits = True
    resolver.lookahead_speed_factor_down = 1.0
    sm_mock = setup_sm_mock(mocker)
    sm_mock['carStateSP'].speedLimit = 10.
    sm_mock['liveMapDataSP'].speedLimit = 30.
    sm_mock['liveMapDataSP'].speedLimitAhead = 20.
    sm_mock['liveMapDataSP'].speedLimitAheadValid = True
    sm_mock['liveMapDataSP'].speedLimitAheadDistance = 100.

    resolver.update(15., sm_mock)

    assert resolver.source == SpeedLimitSource.car
    assert resolver.speed_limit == 10.
    assert not resolver.lower_lookahead_active


  @parameterized.expand([(30., 20.), (20., 30.)], names=['current', 'upcoming'])
  def test_ahead_confirmed_before_planning_range(self, resolver_class, mocker, current, upcoming):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker, current, upcoming)
    for second, distance in [(100., 150.), (101., 140.), (102., 130.), (105., 100.)]:
      # Use fresh observations throughout, including before entering lookahead.
      if second == 105.:
        for intermediate in [103., 104.]:
          self.observe(resolver, sm, clock, intermediate, 150. - (intermediate - 100.) * 10.)
      self.observe(resolver, sm, clock, second, distance)
      assert resolver.speed_limit == (upcoming if distance == 100. else current)
    assert resolver.distance == 100.
    assert resolver.source == SpeedLimitSource.map

  def ahead_scenario(self, resolver_class, mocker, current=30., upcoming=20.):
    resolver = resolver_class()
    mocker.patch.object(resolver, 'update_params')
    resolver.policy = Policy.car_state_priority
    resolver.lookahead_lower_limits = True
    resolver.lookahead_speed_factor_down = 1.
    resolver.lookahead_speed_factor_up = 1.
    sm = setup_sm_mock(mocker)
    sm['carStateSP'].speedLimit = current
    sm['liveMapDataSP'].speedLimit = current
    sm['liveMapDataSP'].speedLimitAhead = upcoming
    sm['liveMapDataSP'].speedLimitAheadValid = True
    clock = mocker.patch('openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_resolver.time.monotonic', return_value=100.)
    return resolver, sm, clock

  def observe(self, resolver, sm, clock, second, distance, v_ego=10.):
    clock.return_value = second
    sm.logMonoTime['liveMapDataSP'] = int(second * 1e9)
    sm['liveMapDataSP'].speedLimitAheadDistance = distance
    resolver.update(v_ego, sm)

  @parameterized.expand([(30., 20.), (20., 30.)], names=['current', 'upcoming'])
  def test_brief_upcoming_limit_does_not_change_target(self, resolver_class, mocker, current, upcoming):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker, current, upcoming)
    self.observe(resolver, sm, clock, 100., 100.)
    assert resolver.speed_limit == current
    self.observe(resolver, sm, clock, 100.5, 95.)
    assert resolver.speed_limit == current
    sm['liveMapDataSP'].speedLimitAheadValid = False
    self.observe(resolver, sm, clock, 101., 90.)
    assert resolver.speed_limit == current
    assert not resolver.lower_lookahead_active
    sm['liveMapDataSP'].speedLimitAheadValid = True
    self.observe(resolver, sm, clock, 102., 80.)
    assert resolver.speed_limit == current

  def test_cached_message_cannot_confirm_ahead(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    self.observe(resolver, sm, clock, 100., 100.)
    clock.return_value = 102.
    resolver.update(10., sm)
    assert resolver.speed_limit == 30.
    assert not resolver._ahead_confirmed

  @parameterized.expand([(101., 200., 20.), (103., 70., 20.), (101., 90., 15.)],
                        names=['second', 'distance', 'limit'])
  def test_changed_boundary_or_observation_gap_restarts_confirmation(self, resolver_class, mocker, second, distance, limit):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    self.observe(resolver, sm, clock, 100., 100.)
    sm['liveMapDataSP'].speedLimitAhead = limit
    self.observe(resolver, sm, clock, second, distance)
    assert not resolver._ahead_confirmed
    assert resolver._ahead_since == second

  def test_current_limits_apply_immediately_in_both_directions(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    sm['liveMapDataSP'].speedLimitAheadValid = False
    for policy in [Policy.car_state_priority, Policy.map_data_only]:
      resolver.policy = policy
      for limit in [30., 20., 30.]:
        sm['carStateSP'].speedLimit = limit
        sm['liveMapDataSP'].speedLimit = limit
        self.observe(resolver, sm, clock, 100., 0.)
        assert resolver.speed_limit == limit

  def test_late_restriction_does_not_wait_when_braking_needed(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    self.observe(resolver, sm, clock, 100., 100., v_ego=30.)
    assert resolver.speed_limit == 20.
    assert not resolver._ahead_confirmed

  def test_boundary_crossing_applies_current_map_limit_without_wait(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    resolver.policy = Policy.map_data_only
    self.observe(resolver, sm, clock, 100., 50.)
    assert resolver.speed_limit == 30.
    sm['liveMapDataSP'].speedLimit = 20.
    sm['liveMapDataSP'].speedLimitAheadValid = False
    self.observe(resolver, sm, clock, 101., 0.)
    assert resolver.speed_limit == 20.
    assert resolver.distance == 0.
    assert not resolver.lower_lookahead_active

  def test_stale_map_clears_confirmation(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    for second in [100., 101., 102.]:
      self.observe(resolver, sm, clock, second, 100. - (second - 100.) * 10.)
    assert resolver.speed_limit == 20.
    clock.return_value = 102. + LIMIT_MAX_MAP_DATA_AGE + 1.
    resolver.update(10., sm)
    assert resolver.speed_limit == 30.
    assert not resolver._ahead_confirmed

  def test_imminent_higher_boundary_does_not_wait(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker, 20., 30.)
    self.observe(resolver, sm, clock, 100., 10.)
    assert resolver.speed_limit == 30.
    assert not resolver._ahead_confirmed

  def test_disappearing_confirmed_boundary_clears_idle_distance(self, resolver_class, mocker):
    resolver, sm, clock = self.ahead_scenario(resolver_class, mocker)
    for second in [100., 101., 102.]:
      self.observe(resolver, sm, clock, second, 100. - (second - 100.) * 10.)
    assert resolver.speed_limit == 20.
    assert resolver.lower_lookahead_active
    sm['liveMapDataSP'].speedLimitAheadValid = False
    self.observe(resolver, sm, clock, 103., 70.)
    assert resolver.speed_limit == 30.
    assert resolver.distance == 0.
    assert not resolver.lower_lookahead_active
