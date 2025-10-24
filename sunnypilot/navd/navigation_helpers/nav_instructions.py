from openpilot.common.constants import CV
from openpilot.common.params import Params

from openpilot.sunnypilot.navd.helpers import Coordinate, string_to_direction


class NavigationInstructions:
  def __init__(self):
    self.coord = Coordinate(0, 0)
    self.params = Params()
    self._cached_route = None
    self._route_loaded = False
    self._no_route = False

  def get_route_progress(self, current_lat, current_lon) -> dict | None:
    route = self.get_current_route()
    if not route or not route['geometry'] or not route['steps']:
      return None

    self.coord.latitude = current_lat
    self.coord.longitude = current_lon

    # Find the closest point on the route relative to self
    closest_idx, min_distance = min(((idx, self.coord.distance_to(coord)) for idx, coord in enumerate(route['geometry'])), key=lambda x: x[1])
    closest_cumulative = route['cumulative_distances'][closest_idx]

    # Find the current step index, which is the HIGHEST idx where the step location cumulative less/equal closest cumulative
    current_step_idx = max((idx for idx, step in enumerate(route['steps']) if step['cumulative_distance'] <= closest_cumulative), default=-1)
    current_step = route['steps'][current_step_idx if current_step_idx >= 0 else 0]

    # The next turn is the next step relative to our cumulative index
    next_turn_idx = current_step_idx + 1
    next_turn = route['steps'][next_turn_idx] if 0 <= next_turn_idx < len(route['steps']) else None

    current_maxspeed = current_step['maxspeed']

    distance_to_end_of_step = max(0, current_step['distance'] - (closest_cumulative - current_step['cumulative_distance']))

    all_maneuvers: list = []
    max_maneuvers = 2
    for idx in range(current_step_idx, min(current_step_idx + max_maneuvers, len(route['steps']))):
      step = route['steps'][idx]
      if idx == current_step_idx:
        distance = distance_to_end_of_step
      else:
        distance = step['cumulative_distance'] - closest_cumulative
      all_maneuvers.append({'distance': distance, 'type': step['maneuver'], 'modifier': step['modifier'], 'instruction': step['instruction']})

    return {
      'distance_from_route': min_distance,
      'current_step': current_step,
      'next_turn': next_turn,
      'current_maxspeed': current_maxspeed,
      'all_maneuvers': all_maneuvers,
      'current_step_idx': current_step_idx,
      'distance_to_end_of_step': distance_to_end_of_step,
    }

  def get_current_route(self):
    if self._route_loaded and self._cached_route is not None:
      return self._cached_route
    if self._no_route:
      return None

    param_value = self.params.get('MapboxSettings')
    route = param_value['navData']['route'] if param_value else None
    if not route:
      self._no_route = True
      return None

    geometry = [Coordinate(coord['latitude'], coord['longitude']) for coord in route['geometry']]
    cumulative_distances = [0.0]
    cumulative_distances.extend(cumulative_distances[-1] + geometry[step - 1].distance_to(geometry[step]) for step in range(1, len(geometry)))
    maxspeed = [(speed['speed'], speed['unit']) for speed in route['maxspeed']]
    steps = []
    for step in route['steps']:
      location = Coordinate(step['location']['latitude'], step['location']['longitude'])
      closest_idx = min(range(len(geometry)), key=lambda i: location.distance_to(geometry[i]))
      steps.append({
        'bannerInstructions': step['bannerInstructions'],
        'distance': step['distance'],
        'duration': step['duration'],
        'maneuver': step['maneuver'],
        'location': location,
        'cumulative_distance': cumulative_distances[closest_idx],
        'maxspeed': maxspeed[min(closest_idx, len(maxspeed) - 1)],
        'modifier': string_to_direction(step['modifier']),
        'instruction': step['instruction'],
      })
    self._cached_route = {
      'steps': steps,
      'total_distance': route['totalDistance'],
      'total_duration': route['totalDuration'],
      'geometry': geometry,
      'cumulative_distances': cumulative_distances,
      'maxspeed': maxspeed,
    }
    self._route_loaded = True
    return self._cached_route

  def clear_route_cache(self):
    self._cached_route = None
    self._route_loaded = False
    self._no_route = False

  def get_upcoming_turn_from_progress(self, progress, current_lat, current_lon) -> str:
    if progress and progress['next_turn']:
      self.coord.latitude = current_lat
      self.coord.longitude = current_lon
      distance = self.coord.distance_to(progress['next_turn']['location'])
      if distance <= 100:
        modifier = progress['next_turn']['modifier']
        return str(modifier)
    return 'none'

  @staticmethod
  def get_current_speed_limit_from_progress(progress, is_metric: bool) -> int:
    if progress and progress['current_maxspeed']:
      speed, _ = progress['current_maxspeed']
      if is_metric:
        return int(speed)
      else:
        return int(round(speed * CV.KPH_TO_MPH))
    return 0
