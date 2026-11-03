"""Discover a router-validated next street turn; never issue a driving command.

The ahead/exit probe points are API queries only. A target requires a separate
route proving its actual first turn. Map data is not a curb, signal-phase or
physical-clearance oracle. Callers own localization freshness and target expiry.
"""
from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
import time
from types import MappingProxyType

import requests

EARTH_RADIUS_M = 6371008.8
PROBE_DISTANCE_M = 500.
PROBE_ENDPOINT_RADIUS_M = 100.
PROBE_FALLBACK_ENDPOINT_RADIUS_M = 300.
MAX_TARGET_DISTANCE_M = 300.
EXIT_QUERY_DISTANCE_M = 45.
MIN_EXIT_DISTANCE_M = 20.
SOURCE_RADIUS_M = 20.
EXIT_RADIUS_M = 15.
JUNCTION_TOLERANCE_M = 2.
BEARING_TOLERANCE_DEG = 25.
MIN_TURN_DEG = 35.
MAX_TURN_DEG = 145.
TIMEOUT = (2., 3.)
FORBIDDEN_CLASSES = {'restricted', 'motorway', 'ferry'}
STREET_CLASSES = {'trunk', 'primary', 'secondary', 'tertiary', 'street', 'residential', 'unclassified'}
UNSUPPORTED_MANEUVERS = {'roundabout', 'rotary', 'roundabout turn', 'exit roundabout', 'exit rotary', 'on ramp', 'off ramp', 'merge', 'fork'}


class NextTurnError(Exception):
  """A fixed reason code, containing no request URL, token or response body."""
  def __init__(self, reason):
    self.reason = reason
    super().__init__(reason)


def _freeze(value):
  if isinstance(value, dict):
    return MappingProxyType({key: _freeze(item) for key, item in value.items()})
  if isinstance(value, list):
    return tuple(_freeze(item) for item in value)
  return value


def _thaw(value):
  if isinstance(value, (dict, MappingProxyType)):
    return {key: _thaw(item) for key, item in value.items()}
  if isinstance(value, tuple):
    return [_thaw(item) for item in value]
  return value


@dataclass(frozen=True)
class NextTurnTarget:
  junction: tuple[float, float]
  distance_m: float
  incoming_bearing_deg: float
  exit_bearing_deg: float
  direction: str
  name: str
  road_class: str
  geometry: tuple
  steps: tuple
  approach_geometry: tuple
  approach_distance_m: float
  turn_step_index: int
  junction_geometry_index: int
  origin: tuple[float, float]
  discovered_at: float
  probe_uuid: str
  validation_uuid: str
  classification_uuid: str | None
  provenance: MappingProxyType

  def to_dict(self):
    return {field.name: _thaw(getattr(self, field.name)) for field in fields(self)}


def _point(value):
  if not isinstance(value, (list, tuple)) or len(value) != 2:
    raise NextTurnError('invalid_coordinates')
  if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in value):
    raise NextTurnError('invalid_coordinates')
  lon, lat = map(float, value)
  if not (-180 <= lon <= 180 and -85 < lat < 85):
    raise NextTurnError('invalid_coordinates')
  return lon, lat


def distance(a, b):
  lon0, lat0, lon1, lat1 = map(math.radians, (*a, *b))
  h = math.sin((lat1 - lat0) / 2)**2 + math.cos(lat0) * math.cos(lat1) * math.sin((lon1 - lon0) / 2)**2
  return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(1., max(0., h))))


def bearing(a, b):
  lon0, lat0, lon1, lat1 = map(math.radians, (*a, *b))
  return math.degrees(math.atan2(math.sin(lon1-lon0) * math.cos(lat1),
                               math.cos(lat0) * math.sin(lat1) - math.sin(lat0) * math.cos(lat1) * math.cos(lon1-lon0))) % 360


def offset(point, heading, meters):
  lon, lat = map(math.radians, point)
  heading, arc = math.radians(heading), meters / EARTH_RADIUS_M
  lat1 = math.asin(math.sin(lat)*math.cos(arc) + math.cos(lat)*math.sin(arc)*math.cos(heading))
  lon1 = lon + math.atan2(math.sin(heading)*math.sin(arc)*math.cos(lat), math.cos(arc)-math.sin(lat)*math.sin(lat1))
  return (math.degrees(lon1)+180) % 360 - 180, math.degrees(lat1)


def _delta(before, after):
  return (after - before + 180) % 360 - 180


def _length(points):
  return sum(distance(a, b) for a, b in zip(points[:-1], points[1:], strict=True))


def _initial_bearing(points):
  for point in points[1:]:
    if distance(points[0], point) >= .5:
      return bearing(points[0], point)
  raise NextTurnError('insufficient_approach')


def _number(value):
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
    raise NextTurnError('missing_metadata')
  return float(value)


def _parse_route(body, position, heading, endpoint, endpoint_radius):
  if not isinstance(body, dict) or body.get('code') != 'Ok':
    raise NextTurnError('no_route')
  if not isinstance(body.get('uuid'), str) or not body['uuid']:
    raise NextTurnError('missing_request_id')
  routes = body.get('routes')
  if not isinstance(routes, list) or not routes or not isinstance(routes[0], dict):
    raise NextTurnError('invalid_response')
  route = routes[0]
  waypoints = body.get('waypoints', route.get('waypoints'))
  if not isinstance(waypoints, list) or len(waypoints) != 2:
    raise NextTurnError('missing_metadata')
  snapped_start, snapped_end = (_point(value['location']) for value in waypoints)
  if distance(position, snapped_start) > SOURCE_RADIUS_M or distance(endpoint, snapped_end) > endpoint_radius:
    raise NextTurnError('snapping_mismatch')
  geometry = route.get('geometry')
  if not isinstance(geometry, dict) or geometry.get('type') != 'LineString':
    raise NextTurnError('missing_metadata')
  points = tuple(_point(point) for point in geometry.get('coordinates', []))
  if not 2 <= len(points) <= 10000 or distance(points[0], snapped_start) > 3 or distance(points[-1], snapped_end) > 3:
    raise NextTurnError('invalid_geometry')
  if abs(_delta(heading, _initial_bearing(points))) > BEARING_TOLERANCE_DEG:
    raise NextTurnError('incoming_heading_mismatch')
  legs = route.get('legs')
  if not isinstance(legs, list) or len(legs) != 1 or not isinstance(legs[0], dict):
    raise NextTurnError('missing_metadata')
  leg = legs[0]
  if leg.get('annotation', {}).get('closure') or any(item.get('type') == 'closure' for item in leg.get('incidents', [])):
    raise NextTurnError('closed_route')
  if any(item.get('type') == 'violation' for item in route.get('notifications', [])):
    raise NextTurnError('route_violation')
  steps = leg.get('steps')
  if not isinstance(steps, list) or not steps:
    raise NextTurnError('missing_metadata')
  cumulative = [0.]
  for a, b in zip(points[:-1], points[1:], strict=True):
    cumulative.append(cumulative[-1] + distance(a, b))
  intersections = []
  for step_index, step in enumerate(steps):
    if not isinstance(step, dict) or not isinstance(step.get('maneuver'), dict) or not isinstance(step.get('intersections'), list):
      raise NextTurnError('missing_metadata')
    kind = step['maneuver'].get('type')
    if not isinstance(kind, str) or not step.get('geometry', {}).get('coordinates'):
      raise NextTurnError('missing_metadata')
    if step.get('mode') != 'driving':
      raise NextTurnError('unsupported_road')
    for intersection in step['intersections']:
      if not isinstance(intersection, dict):
        raise NextTurnError('missing_metadata')
      if 'in' not in intersection or 'out' not in intersection:
        location = _point(intersection.get('location'))
        if kind == 'depart' and 'in' not in intersection and distance(location, points[0]) <= 3:
          continue
        if kind == 'arrive' and 'out' not in intersection and distance(location, points[-1]) <= 3:
          continue
        raise NextTurnError('missing_metadata')
      bearings, entry = intersection.get('bearings'), intersection.get('entry')
      if not isinstance(bearings, list) or not isinstance(entry, list) or len(bearings) != len(entry) or not 2 <= len(entry) <= 16:
        raise NextTurnError('missing_metadata')
      if any(type(flag) is not bool for flag in entry):
        raise NextTurnError('missing_metadata')
      bearings = [_number(value) for value in bearings]
      if any(not 0 <= value <= 360 for value in bearings):
        raise NextTurnError('missing_metadata')
      # Actual Directions responses sometimes encode north as 360 rather than 0.
      bearings = [value % 360 for value in bearings]
      incoming, outgoing, index = intersection['in'], intersection['out'], intersection.get('geometry_index')
      if any(type(value) is not int for value in (incoming, outgoing, index)):
        raise NextTurnError('missing_metadata')
      if not (0 <= incoming < len(entry) and 0 <= outgoing < len(entry) and 0 <= index < len(points)):
        raise NextTurnError('missing_metadata')
      location = _point(intersection.get('location'))
      if distance(location, points[index]) > JUNCTION_TOLERANCE_M or not entry[outgoing]:
        raise NextTurnError('inconsistent_intersection')
      before = (bearings[incoming]+180) % 360
      # A fixed long chord can cross the preceding corner at close junctions.
      prior = next((p for p in reversed(points[:index]) if distance(p, location) >= .5), None)
      if prior is None or abs(_delta(bearing(prior, location), before)) > BEARING_TOLERANCE_DEG:
        raise NextTurnError('incoming_heading_mismatch')
      intersections.append({'raw': intersection, 'location': location, 'bearings': bearings, 'entry': entry,
                            'incoming': before, 'outgoing': bearings[outgoing], 'out': outgoing,
                            'index': index, 'distance': cumulative[index], 'step': step_index, 'kind': kind})
  return {'body': body, 'route': route, 'steps': steps, 'points': points, 'intersections': sorted(intersections, key=lambda i:i['index']),
          'uuid': body['uuid'], 'responseSha256': hashlib.sha256(json.dumps(body, sort_keys=True, allow_nan=False).encode()).hexdigest()}


def _choose_branch(route, direction):
  for item in route['intersections']:
    if item['distance'] > MAX_TARGET_DISTANCE_M:
      break
    if item['kind'] in UNSUPPORTED_MANEUVERS:
      raise NextTurnError('unsupported_junction')
    maneuver = route['steps'][item['step']]['maneuver']
    explicit_turn = ((item['kind'] in ('turn', 'end of road') or maneuver.get('modifier') == 'uturn')
                     and distance(_point(maneuver.get('location')), item['location']) <= JUNCTION_TOLERANCE_M)
    has_branch = len(item['bearings']) >= 3
    candidates = []
    for heading, allowed in zip(item['bearings'], item['entry'], strict=True):
      delta = _delta(item['incoming'], heading)
      side = 'right' if delta > 0 else 'left'
      continuing_bend = heading == item['outgoing'] and not explicit_turn
      if allowed and not continuing_bend and side == direction and MIN_TURN_DEG <= abs(delta) <= MAX_TURN_DEG:
        candidates.append(heading)
    if len(candidates) > 1:
      raise NextTurnError('ambiguous_branch')
    if candidates and item['distance'] >= 2:
      return {**item, 'exit': candidates[0]}
    if not has_branch and not explicit_turn:
      continue
    if explicit_turn:
      # Only a maneuver at this intersection proves the probe left the approach;
      # a continuing main road can bend even where a minor branch joins it.
      break
  raise NextTurnError('no_matching_turn')


def _validate_turn(route, candidate, direction):
  matched = None
  truncate = False
  for item in route['intersections']:
    if matched is not None and item['distance'] >= matched['distance'] + MIN_EXIT_DISTANCE_M:
      # A query endpoint can require a further turn beyond the local exit. Its
      # later route is irrelevant only after this first turn is proven below.
      if abs(_delta(item['incoming'], item['outgoing'])) >= MIN_TURN_DEG or item['kind'] in UNSUPPORTED_MANEUVERS:
        truncate = True
        break
    near = distance(item['location'], candidate['location']) <= JUNCTION_TOLERANCE_M
    turn = abs(_delta(item['incoming'], item['outgoing'])) >= MIN_TURN_DEG
    if item['kind'] in UNSUPPORTED_MANEUVERS:
      raise NextTurnError('unsupported_junction')
    if near and turn:
      if (abs(_delta(candidate['incoming'], item['incoming'])) > BEARING_TOLERANCE_DEG
          or abs(_delta(candidate['exit'], item['outgoing'])) > BEARING_TOLERANCE_DEG
          or ('right' if _delta(item['incoming'], item['outgoing']) > 0 else 'left') != direction
          or abs(_delta(item['incoming'], item['outgoing'])) > MAX_TURN_DEG):
        raise NextTurnError('target_mismatch')
      if abs(item['distance'] - candidate['distance']) > max(12., candidate['distance'] * .15):
        raise NextTurnError('approach_detour')
      if matched is None:
        matched = item
    elif turn:
      raise NextTurnError('earlier_or_additional_turn')
  if matched is None:
    raise NextTurnError('target_not_reached')
  for index, step in enumerate(route['steps']):
    if index != matched['step'] and step['maneuver']['type'] not in ('depart', 'arrive', 'continue', 'new name'):
      location = _point(step['maneuver'].get('location'))
      point_index = min(range(len(route['points'])), key=lambda i: distance(route['points'][i], location))
      along = _length(route['points'][:point_index+1])
      if (index <= matched['step'] or distance(route['points'][point_index], location) > JUNCTION_TOLERANCE_M
          or along < matched['distance'] + MIN_EXIT_DISTANCE_M):
        raise NextTurnError('earlier_or_additional_turn')
      truncate = True
  if truncate:
    route = _local_exit_scope(route, matched)
  points = route['points']
  if (_length(points[matched['index']:]) < MIN_EXIT_DISTANCE_M - 1e-6
      or (not route.get('targetScopeTruncated') and distance(matched['location'], points[-1]) < MIN_EXIT_DISTANCE_M - 1e-6)
      or abs(_delta(candidate['exit'], bearing(matched['location'], points[-1]))) > BEARING_TOLERANCE_DEG):
    raise NextTurnError('insufficient_exit')
  chosen_class = matched['raw'].get('mapbox_streets_v8', {}).get('class')
  for item in route['intersections']:
    if item['index'] >= matched['index']:
      if set(item['raw'].get('classes', [])) & FORBIDDEN_CLASSES:
        raise NextTurnError('unsupported_road')
      known_class = item['raw'].get('mapbox_streets_v8', {}).get('class')
      if known_class is not None and known_class not in STREET_CLASSES:
        raise NextTurnError('unsupported_road')
  if chosen_class is not None and chosen_class not in STREET_CLASSES:
    raise NextTurnError('unsupported_road')
  return matched, chosen_class, route


def _local_exit_scope(route, matched):
  """Return an explicit prefix of real geometry, ending before any later turn."""
  points = list(route['points'][:matched['index']+1])
  remaining = MIN_EXIT_DISTANCE_M
  for point in route['points'][matched['index']+1:]:
    length = distance(points[-1], point)
    if length >= remaining:
      points.append(offset(points[-1], bearing(points[-1], point), remaining))
      break
    points.append(point)
    remaining -= length
  else:
    raise NextTurnError('insufficient_exit')
  cutoff = matched['distance'] + MIN_EXIT_DISTANCE_M
  steps = json.loads(json.dumps(route['steps'][:matched['step']+1]))
  steps[-1]['geometry'] = {'type': 'LineString', 'coordinates': points[matched['index']:]}
  steps[-1]['intersections'] = [item['raw'] for item in route['intersections']
                                if item['step'] == matched['step'] and item['distance'] <= cutoff]
  return {**route, 'points': tuple(points), 'steps': steps,
          'intersections': [item for item in route['intersections'] if item['distance'] <= cutoff],
          'targetScopeTruncated': True}


def coherent_route_steps(route):
  """Require a complete actual Directions leg, including its arrival step.

  A clipped discovery prefix is not a new route: its old distances/banners no
  longer describe its geometry. It must be rerouted to the real exit endpoint.
  """
  if route.get('targetScopeTruncated'):
    raise NextTurnError('incomplete_navigation_route')
  steps = json.loads(json.dumps(route['steps']))
  if not steps or steps[-1]['maneuver']['type'] != 'arrive':
    raise NextTurnError('incomplete_navigation_route')
  for step in steps:
    points = [_point(point) for point in step['geometry']['coordinates']]
    distance_m, duration = _number(step.get('distance')), _number(step.get('duration'))
    if not points or distance_m < 0 or duration < 0:
      raise NextTurnError('incomplete_navigation_route')
    if abs(_length(points)-distance_m) > max(5., distance_m*.2):
      raise NextTurnError('inconsistent_navigation_distance')
    step.setdefault('bannerInstructions', [])
  for before, after in zip(steps[:-1], steps[1:], strict=True):
    if distance(_point(before['geometry']['coordinates'][-1]), _point(after['geometry']['coordinates'][0])) > 3.:
      raise NextTurnError('disconnected_navigation_route')
  return steps


class MapboxNextTurnClient:
  def __init__(self, token):
    if not isinstance(token, str) or not re.fullmatch(r'[ps]k\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', token):
      raise NextTurnError('invalid_token')
    self._token = token

  def _request(self, position, heading, endpoint, *, profile, endpoint_radius):
    coords = ';'.join(f'{lon:.7f},{lat:.7f}' for lon,lat in (position,endpoint))
    params = {'access_token': self._token, 'geometries': 'geojson', 'overview': 'full', 'steps': 'true',
              'alternatives': 'false', 'banner_instructions': 'true', 'bearings': f'{heading:.0f},30;',
              'radiuses': f'{SOURCE_RADIUS_M:.0f};{endpoint_radius:.0f}', 'depart_at': 'now',
              'exclude': 'ferry,motorway'}
    if profile == 'driving-traffic':
      params.update(annotations='closure', snapping_include_closures='false;false', snapping_include_static_closures='false;false')
    try:
      response = requests.get(f'https://api.mapbox.com/directions/v5/mapbox/{profile}/{coords}', params=params, timeout=TIMEOUT)
      response.raise_for_status()
      if len(response.content) > 2 * 1024 * 1024:
        raise NextTurnError('oversized_response')
      body = response.json()
    except requests.RequestException:
      raise NextTurnError('request_failed') from None
    except (ValueError, TypeError):
      raise NextTurnError('invalid_response') from None
    return _parse_route(body, position, heading, endpoint, endpoint_radius)

  def discover(self, position, bearing_deg, direction):
    started = time.monotonic()
    position = _point(position)
    heading = _number(bearing_deg) % 360
    if direction not in ('left','right'):
      raise NextTurnError('invalid_direction')
    try:
      probe_endpoint = offset(position, heading, PROBE_DISTANCE_M)
      probe_radius = PROBE_ENDPOINT_RADIUS_M
      probe_fallback_used = False
      try:
        probe = self._request(position, heading, probe_endpoint, profile='driving-traffic', endpoint_radius=probe_radius)
      except NextTurnError as error:
        if error.reason != 'no_route':
          raise
        # This point is only a discovery probe, not the turn destination. A
        # straight500m projection can land over100m from any road. Retry once
        # with the same origin, heading and endpoint; actual exit validation
        # below keeps its own strict radius and first-turn/legality checks.
        probe_radius = PROBE_FALLBACK_ENDPOINT_RADIUS_M
        probe_fallback_used = True
        probe = self._request(position, heading, probe_endpoint, profile='driving-traffic', endpoint_radius=probe_radius)
      candidate = _choose_branch(probe, direction)
      query_endpoint = offset(candidate['location'], candidate['exit'], EXIT_QUERY_DISTANCE_M)
      validated = self._request(position, heading, query_endpoint, profile='driving-traffic', endpoint_radius=EXIT_RADIUS_M)
      matched, road_class, validated = _validate_turn(validated, candidate, direction)
      request_count = 2+int(probe_fallback_used)
      if validated.get('targetScopeTruncated'):
        # Query an actual endpoint on the validated receiving road. Keep the
        # complete new leg/arrival rather than turning a clipped preview into
        # model navigation data with stale step distances and instructions.
        query_endpoint = validated['points'][-1]
        validated = self._request(position, heading, query_endpoint, profile='driving-traffic', endpoint_radius=3.)
        matched, road_class, validated = _validate_turn(validated, candidate, direction)
        request_count += 1
      classification = None
      if road_class is None:
        request_count += 1
        classification = self._request(position, heading, query_endpoint, profile='driving', endpoint_radius=EXIT_RADIUS_M)
        _, road_class, classification = _validate_turn(classification, candidate, direction)
      if road_class is None:
        raise NextTurnError('missing_road_class')
      complete_steps = coherent_route_steps(validated)
      approach = tuple(validated['points'][:matched['index']]) + (matched['location'],)
      turn_step = validated['steps'][matched['step']]
      provenance = {'method': 'router intersection discovery plus separately validated first-turn route',
                    'requestedPosition': position, 'requestedBearingDeg': heading, 'requestedDirection': direction,
                    'probeResponseSha256': probe['responseSha256'], 'validationResponseSha256': validated['responseSha256'],
                    'classificationResponseSha256': classification['responseSha256'] if classification else None,
                    'requestCount': request_count,
                    'probeEndpointRadiusM': probe_radius, 'probeFallbackUsed': probe_fallback_used,
                    'probeFallbackOriginalReason': 'no_route' if probe_fallback_used else None,
                    'targetScopeTruncated': validated.get('targetScopeTruncated', False),
                    'targetExitDistanceM': _length(validated['points'][matched['index']:]),
                    'fullValidationResponsePreservedByHash': True,
                    'requestStartedAt': started, 'requestCompletedAt': time.monotonic(),
                    'probeEndpointIsTarget': False, 'steeringCommandIssued': False}
      provenance['coherentNavigationRoute'] = True
      return NextTurnTarget(junction=matched['location'], distance_m=matched['distance'],
        incoming_bearing_deg=matched['incoming'], exit_bearing_deg=matched['outgoing'], direction=direction,
        name=str(turn_step.get('name') or 'Unnamed road'), road_class=road_class,
        geometry=tuple(validated['points']), steps=_freeze(complete_steps), approach_geometry=approach,
        approach_distance_m=_length(approach), turn_step_index=matched['step'], junction_geometry_index=matched['index'],
        origin=position, discovered_at=started, probe_uuid=probe['uuid'], validation_uuid=validated['uuid'],
        classification_uuid=classification['uuid'] if classification else None, provenance=_freeze(provenance))
    except NextTurnError:
      raise
    except (KeyError, TypeError, ValueError, OverflowError, IndexError, AttributeError):
      raise NextTurnError('invalid_response') from None
