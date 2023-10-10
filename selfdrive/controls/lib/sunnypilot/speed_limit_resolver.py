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
      Policy.car_state_priority: [Source.car_state, Source.map_data],
      Policy.map_data_priority: [Source.map_data, Source.car_state],
      Policy.nav_priority: [Source.nav, Source.map_data, Source.car_state],
      Policy.map_data_only: [Source.map_data],
      Policy.combined: [Source.car_state, Source.nav, Source.map_data],
      Policy.nav_only: [Source.nav]
    }
    self._reset_limit_sources()

  def _reset_limit_sources(self):
    self._limit_solutions.clear()
    self._distance_solutions.clear()
    for source in Source:
      self._limit_solutions[source] = 0.
      self._distance_solutions[source] = 0.

  def resolve(self, v_ego, current_speed_limit, sm):
    self._reset_limit_sources()
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
    self._limit_solutions[Source.car_state] = self._sm['carState'].cruiseState.speedLimit
    self._distance_solutions[Source.car_state] = 0.

  def _get_from_nav(self):
    if not self._sm.alive['navInstruction']:
      debug('SL: No nav instruction for speed limit')
      return

    # Load limits from nav instruction
    self._limit_solutions[Source.nav] = self._sm['navInstruction'].speedLimit
    self._distance_solutions[Source.nav] = 0.

  def _get_from_map_data(self):
    sock = 'liveMapDataSP'
    if self._sm.logMonoTime[sock] is None:
      debug('SL: No map data for speed limit')
      return

    # Load limits from map_data
    self._process_map_data(self._sm[sock])

  def _process_map_data(self, map_data):
    speed_limit = map_data.speedLimit if map_data.speedLimitValid else 0.
    next_speed_limit = map_data.speedLimitAhead if map_data.speedLimitAheadValid else 0.

    gps_fix_age = time.time() - map_data.lastGpsTimestamp * 1e-3
    if gps_fix_age > LIMIT_MAX_MAP_DATA_AGE:
      debug(f'SL: Ignoring map data as is too old. Age: {gps_fix_age}')
      return

    self._calculate_map_data_limits(speed_limit, next_speed_limit, map_data)

  def _calculate_map_data_limits(self, speed_limit, next_speed_limit, map_data):
    distance_since_fix = self._v_ego * (time.time() - map_data.lastGpsTimestamp * 1e-3)
    distance_to_speed_limit_ahead = max(0., map_data.speedLimitAheadDistance - distance_since_fix)

    self._limit_solutions[Source.map_data] = speed_limit
    self._distance_solutions[Source.map_data] = 0.

    if next_speed_limit > 0. and next_speed_limit < self._v_ego:
      adapt_time = (next_speed_limit - self._v_ego) / LIMIT_ADAPT_ACC
      adapt_distance = self._v_ego * adapt_time + 0.5 * LIMIT_ADAPT_ACC * adapt_time**2

      if distance_to_speed_limit_ahead <= adapt_distance:
        self._limit_solutions[Source.map_data] = next_speed_limit
        self._distance_solutions[Source.map_data] = distance_to_speed_limit_ahead

  def _consolidate(self):
    solutions = self._get_solutions_according_to_policy()
    limits = solutions['limits']
    distances = solutions['distances']
    sources = solutions['sources']
    extra_sources = []

    # Get all non-zero values and set the minimum if any, otherwise 0.
    mask = limits > 0.
    limits = limits[mask]
    distances = distances[mask]
    sources = sources[mask]

    if len(limits) > 0:
      min_idx = np.argmin(limits)
      self.speed_limit = limits[min_idx]
      self.distance = distances[min_idx]
      self.source = Source(sources[min_idx])
    elif self._policy in [Policy.car_state_priority, Policy.nav_priority, Policy.map_data_priority]:
      # If policy is car_state_priority -> append map data
      if self._policy == Policy.car_state_priority:
        extra_sources = [Source.map_data]
      # If policy is map_data_priority --> append car state
      elif self._policy == Policy.map_data_priority:
        extra_sources = [Source.car_state]
      # If policy is nav_priority -> append map data then car state
      elif self._policy == Policy.nav_priority:
        extra_sources = [Source.map_data, Source.car_state]

      for src in extra_sources:
        if self._limit_solutions[src] > 0:
          # If the speed limit from the source is above 0, then choose this source
          self.speed_limit = self._limit_solutions[src]
          self.distance = self._distance_solutions[src]
          self.source = src
          break
      else:
        self.speed_limit = 0.
        self.distance = 0.
        self.source = Source.none

    else:
      self.speed_limit = 0.
      self.distance = 0.
      self.source = Source.none

    debug(f'SL: *** Speed Limit set: {self.speed_limit}, distance: {self.distance}, source: {self.source}')
    return self.speed_limit, self.distance, self.source

  def _get_solutions_according_to_policy(self):
    source_codes = self._policy_to_sources_map[self._policy]
    limits = np.array([self._limit_solutions[source] for source in source_codes], dtype=float)
    distances = np.array([self._distance_solutions[source] for source in source_codes], dtype=float)
    sources = np.array([source.value for source in source_codes], dtype=int)
    return {'limits': limits, 'distances': distances, 'sources': sources}
