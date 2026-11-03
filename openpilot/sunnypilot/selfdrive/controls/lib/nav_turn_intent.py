"""Keep a signal's route prepared through completed lane changes and a turn."""
import math
import time


def turn_route_ready(context, session, direction, now):
  if not isinstance(context, dict):
    return False
  updated, generation, distance = context.get('updatedAt'), context.get('routeGeneration'), context.get('distanceM')
  return (context.get('session') == session and context.get('direction') == direction and
          context.get('status') == 'ready' and context.get('routeOwner') == 'signal' and
          context.get('locationValid') is True and context.get('headingValid') is True and
          isinstance(generation, int) and not isinstance(generation, bool) and generation > 0 and
          isinstance(updated, (int, float)) and not isinstance(updated, bool) and math.isfinite(updated) and
          math.isfinite(now) and 0. <= now-updated <= .35 and
          isinstance(distance, (int, float)) and not isinstance(distance, bool) and math.isfinite(distance) and distance > 0.)


class NavTurnIntent:
  def __init__(self, params, session_clock=time.monotonic_ns):
    self.params = params
    self.session_clock = session_clock
    self.direction = None
    self.session = None
    self.physical_direction = None
    self.mode = None
    self._supported, self._active = False, False
    self._published = None
    self.params.remove('MapboxTurnIntent')

  def update(self, direction, enabled, model_supported, lateral_active):
    physical = direction if enabled and direction in ('left', 'right') else None
    if physical != self.physical_direction:
      self.physical_direction = physical
      self.mode = 'pending' if physical else None
    self._supported, self._active = bool(model_supported), bool(lateral_active)
    self._publish()

  def commit(self, mode):
    if self.mode != 'pending' or self.physical_direction is None or mode not in ('turn', 'lane_change'):
      return False
    self.mode = mode
    self._publish()
    return True

  def resume_after_lane_change(self):
    """Called only for the helper's normal completion, never for a speed drop."""
    if self.mode != 'lane_change' or self.physical_direction is None or not self._active or not self._supported:
      return False
    self.mode = 'pending'
    self._publish()
    return True

  def _publish(self):
    # LC keeps the same session and route warm; its mode never authorizes map
    # inputs. Normal completion can then use the route without another lookup.
    direction = self.physical_direction if self._active and self.mode in ('pending', 'lane_change', 'turn') else None
    if direction != self.direction:
      self.direction = direction
      self.session = str(self.session_clock()) if direction else None
    value = {'session': self.session, 'direction': direction, 'mode': self.mode,
             'modelSupportsNavigation': self._supported, 'lateralActive': True} if direction else None
    if value != self._published:
      if value is None:
        self.params.remove('MapboxTurnIntent')
      else:
        # This event is rare. Persist it before a synchronous cancel/remove can
        # race a queued write and resurrect a retired signal session.
        self.params.put('MapboxTurnIntent', value, block=True)
      self._published = value
