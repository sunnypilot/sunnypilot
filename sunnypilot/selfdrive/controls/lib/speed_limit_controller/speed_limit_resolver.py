import time
import numpy as np

from cereal import messaging, custom

from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import LIMIT_MAX_MAP_DATA_AGE, LIMIT_ADAPT_ACC
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source, Policy
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.helpers import debug


class SpeedLimitResolver:
  _sm: messaging.SubMaster
  _limit_solutions: dict[Source, float]  # Store for speed limit solutions from different sources
  _distance_solutions: dict[Source, float]  # Store for distance to current speed limit start for different sources
  _v_ego: float
  _current_speed_limit: float

  def __init__(self, policy: Policy):
    self._limit_solutions = {}
    self._distance_solutions = {}

    self._policy = policy
    self._policy_to_sources_map = {
      Policy.car_state_only: [Source.car_state],
      Policy.car_state_priority: [Source.car_state, Source.map_data],
      Policy.map_data_priority: [Source.map_data, Source.car_state],
      Policy.map_data_only: [Source.map_data],
      Policy.combined: [Source.car_state, Source.map_data],
    }
    for source in Source:
      self._reset_limit_sources(source)

  def change_policy(self, policy: Policy) -> None:
    self._policy = policy

  def _reset_limit_sources(self, source: Source) -> None:
    self._limit_solutions[source] = 0.
    self._distance_solutions[source] = 0.

  def _is_sock_updated(self, sock: str) -> bool:
    return self._sm.alive[sock] and self._sm.updated[sock]

  def resolve(self, v_ego: float, current_speed_limit: float, sm: messaging.SubMaster) -> tuple[float, float, Source]:
    self._v_ego = v_ego
    self._current_speed_limit = current_speed_limit
    self._sm = sm

    self._resolve_limit_sources()
    return self._consolidate()

  def _resolve_limit_sources(self) -> None:
    """Get limit solutions from each data source"""
    self._get_from_car_state()
    self._get_from_map_data()

  def _get_from_car_state(self) -> None:
    if not self._is_sock_updated('carStateSP'):
      debug('SL: No carStateSP instruction for speed limit')
      return

    self._reset_limit_sources(Source.car_state)
    self._limit_solutions[Source.car_state] = self._sm['carStateSP'].speedLimit
    self._distance_solutions[Source.car_state] = 0.

  def _get_from_map_data(self) -> None:
    if not self._is_sock_updated("liveMapDataSP"):
      debug('SL: No map data for speed limit')
      return

    # Load limits from map_data
    self._reset_limit_sources(Source.map_data)
    self._process_map_data(self._sm["liveMapDataSP"])

  def _process_map_data(self, map_data: custom.LiveMapDataSP) -> None:
    gps_fix_age = time.time() - map_data.lastGpsTimestamp * 1e-3
    if gps_fix_age > LIMIT_MAX_MAP_DATA_AGE:
      debug(f'SL: Ignoring map data as is too old. Age: {gps_fix_age}')
      return

    speed_limit = map_data.speedLimit if map_data.speedLimitValid else 0.
    next_speed_limit = map_data.speedLimitAhead if map_data.speedLimitAheadValid else 0.

    self._calculate_map_data_limits(speed_limit, next_speed_limit, map_data)

  def _calculate_map_data_limits(self, speed_limit: float, next_speed_limit: float, map_data: custom.LiveMapDataSP) -> None:
    distance_since_fix = self._v_ego * (time.time() - map_data.lastGpsTimestamp * 1e-3)
    distance_to_speed_limit_ahead = max(0., map_data.speedLimitAheadDistance - distance_since_fix)

    self._limit_solutions[Source.map_data] = speed_limit
    self._distance_solutions[Source.map_data] = 0.

    if 0. < next_speed_limit < self._v_ego:
      adapt_time = (next_speed_limit - self._v_ego) / LIMIT_ADAPT_ACC
      adapt_distance = self._v_ego * adapt_time + 0.5 * LIMIT_ADAPT_ACC * adapt_time ** 2

      if distance_to_speed_limit_ahead <= adapt_distance:
        self._limit_solutions[Source.map_data] = next_speed_limit
        self._distance_solutions[Source.map_data] = distance_to_speed_limit_ahead

  def _consolidate(self) -> tuple[float, float, Source]:
    source = self._get_source_solution_according_to_policy()
    self.speed_limit = self._limit_solutions[source] if source else 0.
    self.distance = self._distance_solutions[source] if source else 0.
    self.source = source or Source.none

    debug(f'SL: *** Speed Limit set: {self.speed_limit}, distance: {self.distance}, source: {self.source}')
    return self.speed_limit, self.distance, self.source

  def _get_source_solution_according_to_policy(self) -> Source | None:
    sources_for_policy = self._policy_to_sources_map[self._policy]

    if self._policy != Policy.combined:
      # They are ordered in the order of preference, so we pick the first that's non zero
      for source in sources_for_policy:
        if self._limit_solutions[source] > 0.:
          return Source(source)

    limits = np.array([self._limit_solutions[source] for source in sources_for_policy], dtype=float)
    sources = np.array([source.value for source in sources_for_policy], dtype=int)

    if len(limits) > 0:
      min_idx = np.argmin(limits)
      return Source(sources[min_idx])

    return None
