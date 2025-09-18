import time
import numpy as np

import cereal.messaging as messaging
from cereal import custom
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_assist import LIMIT_MAX_MAP_DATA_AGE, LIMIT_ADAPT_ACC, PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_assist.common import Policy

SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimitSource

ALL_SOURCES = tuple(SpeedLimitSource.schema.enumerants.values())


class SpeedLimitResolver:
  _limit_solutions: dict[custom.LongitudinalPlanSP.SpeedLimitSource, float]
  _distance_solutions: dict[custom.LongitudinalPlanSP.SpeedLimitSource, float]
  _v_ego: float
  speed_limit: float
  distance: float
  source: custom.LongitudinalPlanSP.SpeedLimitSource

  def __init__(self):
    self.params = Params()
    self.frame = -1

    self._gps_location_service = get_gps_location_service(self.params)
    self._limit_solutions = {}  # Store for speed limit solutions from different sources
    self._distance_solutions = {}  # Store for distance to current speed limit start for different sources

    self.policy = self.params.get("SpeedLimitPolicy", return_default=True)
    self._policy_to_sources_map = {
      Policy.car_state_only: [SpeedLimitSource.car],
      Policy.car_state_priority: [SpeedLimitSource.car, SpeedLimitSource.map],
      Policy.map_data_priority: [SpeedLimitSource.map, SpeedLimitSource.car],
      Policy.map_data_only: [SpeedLimitSource.map],
      Policy.combined: [SpeedLimitSource.car, SpeedLimitSource.map],
    }
    for source in ALL_SOURCES:
      self._reset_limit_sources(source)

  def update_params(self):
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.policy = Policy(self.params.get("SpeedLimitPolicy", return_default=True))
      self.change_policy(self.policy)

  def change_policy(self, policy: Policy) -> None:
    self.policy = policy

  def _reset_limit_sources(self, source: custom.LongitudinalPlanSP.SpeedLimitSource) -> None:
    self._limit_solutions[source] = 0.
    self._distance_solutions[source] = 0.

  def _resolve_limit_sources(self, sm: messaging.SubMaster) -> None:
    """Get limit solutions from each data source"""
    self._get_from_car_state(sm)
    self._get_from_map_data(sm)

  def _get_from_car_state(self, sm: messaging.SubMaster) -> None:
    self._reset_limit_sources(SpeedLimitSource.car)
    self._limit_solutions[SpeedLimitSource.car] = sm['carStateSP'].speedLimit
    self._distance_solutions[SpeedLimitSource.car] = 0.

  def _get_from_map_data(self, sm: messaging.SubMaster) -> None:
    self._reset_limit_sources(SpeedLimitSource.map)
    self._process_map_data(sm)

  def _process_map_data(self, sm: messaging.SubMaster) -> None:
    gps_data = sm[self._gps_location_service]
    map_data = sm['liveMapDataSP']

    gps_fix_age = time.monotonic() - gps_data.unixTimestampMillis * 1e-3
    if gps_fix_age > LIMIT_MAX_MAP_DATA_AGE:
      return

    speed_limit = map_data.speedLimit if map_data.speedLimitValid else 0.
    next_speed_limit = map_data.speedLimitAhead if map_data.speedLimitAheadValid else 0.

    self._calculate_map_data_limits(sm, speed_limit, next_speed_limit)

  def _calculate_map_data_limits(self, sm: messaging.SubMaster, speed_limit: float, next_speed_limit: float) -> None:
    gps_data = sm[self._gps_location_service]
    map_data = sm['liveMapDataSP']

    distance_since_fix = self._v_ego * (time.monotonic() - gps_data.unixTimestampMillis * 1e-3)
    distance_to_speed_limit_ahead = max(0., map_data.speedLimitAheadDistance - distance_since_fix)

    self._limit_solutions[SpeedLimitSource.map] = speed_limit
    self._distance_solutions[SpeedLimitSource.map] = 0.

    if 0. < next_speed_limit < self._v_ego:
      adapt_time = (next_speed_limit - self._v_ego) / LIMIT_ADAPT_ACC
      adapt_distance = self._v_ego * adapt_time + 0.5 * LIMIT_ADAPT_ACC * adapt_time ** 2

      if distance_to_speed_limit_ahead <= adapt_distance:
        self._limit_solutions[SpeedLimitSource.map] = next_speed_limit
        self._distance_solutions[SpeedLimitSource.map] = distance_to_speed_limit_ahead

  def _consolidate(self) -> tuple[float, float, custom.LongitudinalPlanSP.SpeedLimitSource]:
    source = self._get_source_solution_according_to_policy()
    speed_limit = self._limit_solutions[source] if source else 0.
    distance = self._distance_solutions[source] if source else 0.

    return speed_limit, distance, source

  def _get_source_solution_according_to_policy(self) -> custom.LongitudinalPlanSP.SpeedLimitSource:
    sources_for_policy = self._policy_to_sources_map[self.policy]

    if self.policy != Policy.combined:
      # They are ordered in the order of preference, so we pick the first that's non zero
      for source in sources_for_policy:
        return source if self._limit_solutions[source] > 0. else SpeedLimitSource.none

    limits = np.array([self._limit_solutions[source] for source in sources_for_policy], dtype=float)
    sources = np.array(sources_for_policy, dtype=int)

    if len(limits) > 0:
      min_idx = np.argmin(limits)
      return sources[min_idx]

    return SpeedLimitSource.none

  def update(self, v_ego: float, sm: messaging.SubMaster) -> None:
    self._v_ego = v_ego
    self.update_params()
    self._resolve_limit_sources(sm)

    self.speed_limit, self.distance, self.source = self._consolidate()

    self.frame += 1
