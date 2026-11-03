"""Inputs for comma's pinned nav-model-integration driving model.

The map raster and maneuver encoding follow afbf2e547e9319e2eb9f515e1e4330af63705cec.
They condition the trained driving network; they do not issue a steering command
or fabricate a turn desire. Missing/stale context clears both conditioning inputs.
"""

import math
from collections.abc import Mapping

import numpy as np

NAV_MAP_SIZE = 256
NAVIGATION_SIZE = 47
MAP_MAX_AGE = 0.5
INSTRUCTION_MAX_AGE = 2.0
VALHALLA_SIDED_TYPES = {
  'depart': (1, 2, 3), 'arrive': (4, 5, 6),
  'on ramp': (17, 18, 19), 'off ramp': (20, 20, 21), 'fork': (22, 23, 24),
  'roundabout': (26, 26, 26), 'rotary': (26, 26, 26), 'roundabout turn': (26, 26, 26),
  'exit roundabout': (27, 27, 27), 'exit rotary': (27, 27, 27), 'notification': (28, 28, 28),
}
VALHALLA_TURN_TYPES = {'straight': 8, 'slight right': 9, 'right': 10, 'sharp right': 11, 'uturn': 13,
                       'sharp left': 14, 'left': 15, 'slight left': 16}


def _field(value, name, default=None):
  return value.get(name, default) if isinstance(value, Mapping) else getattr(value, name, default)


def valhalla_type(maneuver_type: str, modifier: str) -> int | None:
  if maneuver_type == 'merge':
    return None
  if maneuver_type in VALHALLA_SIDED_TYPES:
    straight, right, left = VALHALLA_SIDED_TYPES[maneuver_type]
    return right if 'right' in modifier else left if 'left' in modifier else straight
  return VALHALLA_TURN_TYPES.get(modifier, 8)


def navigation_input(maneuvers, traveled: float = 0.) -> np.ndarray:
  """The next non-depart/arrive Valhalla command plus distance in100m units."""
  result = np.zeros(NAVIGATION_SIZE, dtype=np.float32)
  if not math.isfinite(traveled) or traveled < 0:
    return result
  for maneuver in maneuvers:
    maneuver_type, modifier = _field(maneuver, 'type', ''), _field(maneuver, 'modifier', '')
    distance = _field(maneuver, 'distance')
    if (not isinstance(maneuver_type, str) or not isinstance(modifier, str) or
        isinstance(distance, bool) or not isinstance(distance, (int, float, np.floating)) or not math.isfinite(distance)):
      continue
    command, remaining = valhalla_type(maneuver_type, modifier), distance - traveled
    if command is not None and command > 6 and remaining >= 0:
      result[command], result[-1] = 1, remaining / 100
      break
  return result


def supports_navigation(numpy_inputs) -> bool:
  """Fail closed on CTV3/small fallback or an incompatible nav tensor contract."""
  expected = {'nav_map': (1, 1, NAV_MAP_SIZE, NAV_MAP_SIZE), 'navigation': (1, NAVIGATION_SIZE)}
  return all(name in numpy_inputs and numpy_inputs[name].shape == shape and numpy_inputs[name].dtype == np.float32
             for name, shape in expected.items())


def navigation_capability(numpy_inputs, bundle, *, native: bool):
  if not supports_navigation(numpy_inputs):
    return False, 'model_unsupported'
  if bundle is None:
    return False, 'model_bundle_required'
  if not native or bundle.generation != 12 or not bundle.is20hz:
    return False, 'model_bundle_incompatible'
  return True, 'supported'


def destination_route_context(destination, context, now):
  """An explicit destination must own the exact map generation, including at boot."""
  missing = {'ready': False, 'reason': 'destination_route_unavailable'}
  if not isinstance(destination, dict) or not isinstance(context, dict):
    return missing
  snapshot = context.get('destination')
  updated, generation = context.get('updatedAt'), context.get('routeGeneration')
  if (context.get('routeOwner') != 'destination' or context.get('status') != 'ready' or
      not isinstance(snapshot, dict) or isinstance(updated, bool) or not isinstance(updated, (int, float)) or
      not math.isfinite(updated) or not 0 <= now - updated <= .35 or
      isinstance(generation, bool) or not isinstance(generation, int) or generation <= 0):
    return missing
  for name in ('latitude', 'longitude'):
    value = destination.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or snapshot.get(name) != value:
      return missing
  return {'ready': True, 'reason': 'ready', 'routeGeneration': generation}


class NavigationInputBuffer:
  """Latest real map frame with bounded capture and instruction ages."""

  def __init__(self):
    self.map = None
    self.map_received_at = 0.
    self.map_captured_at = 0.
    self.route_generation = None
    self.reason = 'map_missing'

  def observe_map(self, data, width: int, height: int, *, timestamp_ns: int, received_at: float,
                  route_generation: int | None = None) -> bool:
    # A newly received invalid/black-with-zero-timestamp frame must invalidate
    # the preceding map rather than make its old geometry appear fresh.
    self.map = None
    self.route_generation = None
    self.reason = 'map_invalid'
    if (width != NAV_MAP_SIZE or height != NAV_MAP_SIZE or timestamp_ns <= 0 or
        not math.isfinite(received_at) or received_at < 0):
      return False
    captured_at = timestamp_ns / 1e9
    if not 0 <= received_at - captured_at <= MAP_MAX_AGE:
      return False
    try:
      pixels = np.frombuffer(data, dtype=np.uint8, count=NAV_MAP_SIZE * NAV_MAP_SIZE)
    except (TypeError, ValueError):
      return False
    # The verified nav ONNX expects float32 raw raster values0..255, not a
    # normalized camera image. Assignment in comma's runner performs this cast.
    self.map = pixels.astype(np.float32).reshape(1, 1, NAV_MAP_SIZE, NAV_MAP_SIZE)
    self.map_received_at, self.map_captured_at = received_at, captured_at
    self.route_generation = route_generation
    self.reason = 'ready'
    return True

  def prepare(self, *, now: float, enabled: bool, instruction, instruction_valid: bool,
              instruction_received_at: float, speed: float, instruction_published_ns: int | None = None,
              expected_route_generation: int | None = None):
    zero = {'nav_map': np.zeros((1, 1, NAV_MAP_SIZE, NAV_MAP_SIZE), dtype=np.float32),
            'navigation': np.zeros((1, NAVIGATION_SIZE), dtype=np.float32)}
    if not enabled:
      self.reason = 'disabled'
      return zero
    if self.map is None:
      self.reason = 'map_missing'
      return zero
    if not all(math.isfinite(value) for value in (now, instruction_received_at, speed)):
      self.reason = 'invalid_time_or_speed'
      return zero
    if not (0 <= now - self.map_received_at < MAP_MAX_AGE and 0 <= now - self.map_captured_at < MAP_MAX_AGE):
      self.reason = 'map_stale'
      return zero
    if (not isinstance(self.route_generation, int) or self.route_generation <= 0 or
        not isinstance(instruction_published_ns, int) or instruction_published_ns < self.route_generation or
        (expected_route_generation is not None and self.route_generation != expected_route_generation)):
      self.reason = 'route_generation_mismatch'
      return zero
    elapsed = now - instruction_received_at
    if not instruction_valid or not 0 <= elapsed < INSTRUCTION_MAX_AGE:
      self.reason = 'instruction_stale'
      return zero
    vector = navigation_input(_field(instruction, 'allManeuvers', []), max(speed, 0.) * elapsed)
    self.reason = 'ready'
    return {'nav_map': self.map, 'navigation': vector.reshape(1, NAVIGATION_SIZE)}


class SignalRouteGuard:
  """Bind automatic inputs to the current signal and exact rendered route.

  The sole remembered identifier is a route this model actually consumed. It
  permits the router's explicitly bounded outgoing continuation after normal
  signal auto-cancel; a first-time retained route or another session is rejected.
  No timing, steering, maneuver selection or route-completion policy lives here.
  """

  def __init__(self):
    self.last_consumed = None

  def reset(self):
    self.last_consumed = None

  def consumed(self, session, route_generation):
    self.last_consumed = (session, route_generation)

  def check(self, *, now, enabled, lateral_active, left_blinker, right_blinker, intent, context):
    def unavailable(reason, *, retire=False):
      if retire:
        self.reset()
      return {'ready': False, 'reason': reason}

    if not enabled or not lateral_active:
      return unavailable('signal_navigation_disabled', retire=True)
    if isinstance(intent, dict) and self.last_consumed is not None and intent.get('session') != self.last_consumed[0]:
      self.reset()
    if not isinstance(context, dict):
      return unavailable('route_context_missing')
    updated = context.get('updatedAt')
    generation, session = context.get('routeGeneration'), context.get('session')
    direction = context.get('direction')
    if context.get('status') in ('passed', 'completed', 'arrived', 'cancelled', 'idle', 'disabled'):
      return unavailable('route_context_unavailable', retire=True)
    if self.last_consumed is not None and ((session is not None and session != self.last_consumed[0]) or
                                          (generation is not None and generation != self.last_consumed[1])):
      self.reset()
    if (context.get('status') != 'ready' or context.get('routeOwner') != 'signal' or
        context.get('locationValid') is not True or context.get('headingValid') is not True or
        isinstance(updated, bool) or not isinstance(updated, (int, float)) or not math.isfinite(updated) or
        not 0 <= now - updated <= .35 or isinstance(generation, bool) or not isinstance(generation, int) or generation <= 0 or
        not isinstance(session, str) or not session or direction not in ('left', 'right')):
      return unavailable('route_context_unavailable')
    physical_direction = 'left' if left_blinker and not right_blinker else 'right' if right_blinker and not left_blinker else None
    matches = (isinstance(intent, dict) and intent.get('session') == session and intent.get('direction') == direction and
               intent.get('mode') == 'turn' and intent.get('modelSupportsNavigation') is True and intent.get('lateralActive') is True)
    held_signal = matches and physical_direction == direction
    retained = (not left_blinker and not right_blinker and intent is None and
                context.get('retainedAfterSignalCancel') is True and self.last_consumed == (session, generation))
    if not (held_signal or retained):
      # The camera loop can see auto-cancel before navd's next10Hz decision.
      # With neither indicator, hold only the identity (never the inputs) until
      # the router explicitly retains or cancels that same owned route.
      return unavailable('signal_session_mismatch', retire=bool(left_blinker or right_blinker))
    return {'ready': True, 'reason': 'ready', 'session': session, 'routeGeneration': generation}


class NavigationStatePublisher:
  """Runtime capability and consumed-input status, without a control claim."""

  def __init__(self, params):
    self.params = params
    self.last_published = float('-inf')

  def publish(self, *, now: float, supported: bool, active: bool, reason: str, model_name: str = '', force: bool = False,
              session=None, route_generation=None):
    if not force and now - self.last_published < .1:
      return False
    value = {'updatedAt': now, 'supported': bool(supported), 'active': bool(supported and active), 'reason': reason}
    if model_name:
      value['modelName'] = model_name
    if session is not None:
      value.update(session=session, routeGeneration=route_generation)
    self.params.put('NavModelState', value)
    self.last_published = now
    return True
