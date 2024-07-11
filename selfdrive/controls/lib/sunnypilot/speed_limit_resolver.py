import time
import numpy as np

from openpilot.selfdrive.controls.lib.drive_helpers import LIMIT_MAX_MAP_DATA_AGE, LIMIT_ADAPT_ACC
from openpilot.selfdrive.controls.lib.sunnypilot.common import Source, Policy
from openpilot.selfdrive.controls.lib.sunnypilot.helpers import debug


class SpeedLimitResolver:
  def __init__(self, policy=Policy.nav_priority):
    self._limit_solutions = {}  # Store for speed limit solutions from different sources
    self._distance_solutions = {}  # Store for distance to current speed limit start for different sources

    self._policy = policy
    self._policy_to_sources_map = {
      Policy.car_state_only: [Source.car_state],
      Policy.car_state_priority: [Source.car_state, Source.nav, Source.map_data],
      Policy.map_data_priority: [Source.map_data, Source.nav, Source.car_state],
      Policy.nav_priority: [Source.nav, Source.map_data, Source.car_state],
      Policy.map_data_only: [Source.map_data],
      Policy.combined: [Source.car_state, Source.nav, Source.map_data],
      Policy.nav_only: [Source.nav]
    }
    for source in Source:
      self._reset_limit_sources(source)

  def change_policy(self, policy: Policy):
    self._policy = policy

  def _reset_limit_sources(self, source):
    self._limit_solutions[source] = 0.
    self._distance_solutions[source] = 0.

  def _is_sock_updated(self, sock):
    return self._sm.alive[sock] and self._sm.updated[sock]

  def resolve(self, v_ego, current_speed_limit, sm):
    self._v_ego = v_ego
    self._current_speed_limit = current_speed_limit
    self._sm = sm

    self._resolve_limit_sources()
    return self._consolidate()

  def _resolve_limit_sources(self):
    """Get limit solutions from each data source"""
    self._get_from_car_state()
    self._get_from_nav()
    self._get_from_map_data()

  def _get_from_car_state(self):
    if not self._is_sock_updated('carState'):
      debug('SL: No carState instruction for speed limit')
      return

    self._reset_limit_sources(Source.car_state)
    self._limit_solutions[Source.car_state] = self._sm['carState'].cruiseState.speedLimit
    self._distance_solutions[Source.car_state] = 0.

  def _get_from_nav(self):
    if not self._is_sock_updated('navInstruction'):
      debug('SL: No nav instruction for speed limit')
      return

    # Load limits from nav instruction
    self._reset_limit_sources(Source.nav)
    self._limit_solutions[Source.nav] = self._sm['navInstruction'].speedLimit
    self._distance_solutions[Source.nav] = 0.

  def _get_from_map_data(self):
    sock = 'liveMapDataSP'

    if not self._is_sock_updated(sock):
      debug('SL: No map data for speed limit')
      return

    # Load limits from map_data
    self._reset_limit_sources(Source.map_data)
    self._process_map_data(self._sm[sock])

  def _process_map_data(self, map_data):
    gps_fix_age = time.time() - map_data.lastGpsTimestamp * 1e-3
    if gps_fix_age > LIMIT_MAX_MAP_DATA_AGE:
      debug(f'SL: Ignoring map data as is too old. Age: {gps_fix_age}')
      return

    speed_limit = map_data.speedLimit if map_data.speedLimitValid else 0.
    next_speed_limit = map_data.speedLimitAhead if map_data.speedLimitAheadValid else 0.

    self._calculate_map_data_limits(speed_limit, next_speed_limit, map_data)

  def _calculate_map_data_limits(self, speed_limit, next_speed_limit, map_data):
    distance_since_fix = self._v_ego * (time.time() - map_data.lastGpsTimestamp * 1e-3)
    distance_to_speed_limit_ahead = max(0., map_data.speedLimitAheadDistance - distance_since_fix)

    self._limit_solutions[Source.map_data] = speed_limit
    self._distance_solutions[Source.map_data] = 0.

    if 0. < next_speed_limit < self._v_ego:
      adapt_time = (next_speed_limit - self._v_ego) / LIMIT_ADAPT_ACC
      adapt_distance = self._v_ego * adapt_time + 0.5 * LIMIT_ADAPT_ACC * adapt_time**2

      if distance_to_speed_limit_ahead <= adapt_distance:
        self._limit_solutions[Source.map_data] = next_speed_limit
        self._distance_solutions[Source.map_data] = distance_to_speed_limit_ahead

  def _consolidate(self):
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
          return source

    limits = np.array([self._limit_solutions[source] for source in sources_for_policy], dtype=float)
    sources = np.array([source.value for source in sources_for_policy], dtype=int)

    if len(limits) > 0:
      min_idx = np.argmin(limits)
      return sources[min_idx]

    return None
