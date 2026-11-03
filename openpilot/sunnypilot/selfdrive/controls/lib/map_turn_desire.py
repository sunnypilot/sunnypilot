"""Legacy cue-experiment helpers; live signal navigation uses nav_turn_intent."""
from dataclasses import dataclass
import math
import time

from openpilot.sunnypilot.selfdrive.controls.lib.turn_motion import TurnMotionReadiness, predicted_travel


@dataclass(frozen=True)
class MapTurnDecision:
  allowed: bool
  reason: str
  distance_m: float | None = None


def evaluate_map_turn(context, session, direction, now, speed, lead_m, allow_stationary=False):
  """Check a fresh, session-matched approach. Distance is not curb clearance."""
  def reject(reason):
    return MapTurnDecision(False, reason)

  if not isinstance(context, dict) or not session or direction not in ('left', 'right'):
    return reject('no_target')
  if context.get('session') != session or context.get('direction') != direction:
    return reject('different_signal')
  if context.get('status') != 'ready' or context.get('locationValid') is not True or context.get('headingValid') is not True:
    return reject('target_unavailable')
  names = ('updatedAt', 'gpsAgeSeconds', 'gpsHorizontalAccuracyM', 'crossTrackM', 'distanceM')
  values = [context.get(name) for name in names]
  if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (*values, now, speed, lead_m)):
    return reject('invalid_measurement')
  updated, gps_age, accuracy, cross_track, distance = values
  age = now - updated
  if not -.05 <= age <= .35 or not 0. <= gps_age <= .5 or max(age, 0.) + gps_age > .5:
    return reject('stale_location')
  if not 0. < accuracy <= 3. or not 0. <= cross_track <= 6.:
    return reject('uncertain_location')
  if not 4. <= lead_m <= 30.:
    return reject('invalid_lead')
  if allow_stationary is not True and speed <= .3:
    return reject('not_moving')
  # The publisher projects the last GPS fix, not a predicted position. Limit
  # extrapolation to the short freshness interval; never extend past junction.
  distance -= speed * (max(age, 0.) + gps_age)
  if distance <= 0.:
    return MapTurnDecision(False, 'junction_passed', distance)
  if distance > lead_m:
    return MapTurnDecision(False, 'approaching', distance)
  return MapTurnDecision(True, 'cue', distance)


class MapTurnGate:
  """Own one intent identifier per physical signal; navd owns map requests."""
  def __init__(self, params, clock=time.monotonic, session_clock=time.monotonic_ns, use_motion=True, motion_threshold=1.5):
    self.params, self.clock, self.session_clock = params, clock, session_clock
    self.enabled = False
    self.session = None
    self.direction = None
    self.lead_m = 20.
    self.use_motion = bool(use_motion)
    self.motion = TurnMotionReadiness(threshold=motion_threshold)
    self.last_mode = None
    self.last_decision = MapTurnDecision(False, 'disabled')
    # A model-process restart retires the previous process's physical intent.
    self.params.remove('MapboxTurnIntent')

  def configure(self, enabled, lead_m):
    self.enabled = bool(enabled)
    self.lead_m = lead_m

  def update_signal(self, direction, assist_enabled):
    direction = direction if self.enabled and assist_enabled else None
    if direction == self.direction:
      return
    self.direction = direction
    self.motion.reset()
    self.session = str(self.session_clock()) if direction else None
    if direction:
      self.params.put('MapboxTurnIntent', {'session': self.session, 'direction': direction})
    else:
      self.params.remove('MapboxTurnIntent')
    self.last_decision = MapTurnDecision(False, 'searching' if direction else 'disabled')

  def reset_motion(self):
    self.motion.reset()

  def ready(self, speed, model_position=None, lateral_active=True):
    now = self.clock()
    self.last_mode = None
    if lateral_active is not True:
      self.motion.reset()
      self.last_decision = MapTurnDecision(False, 'lateral_inactive')
      return False
    spatial = evaluate_map_turn(self.params.get('MapboxTurnContext'), self.session,
                                self.direction, now, speed, self.lead_m, allow_stationary=self.use_motion)
    self.last_decision = spatial
    if not spatial.allowed:
      self.motion.reset()
      return False
    movement = predicted_travel(model_position, start=2., end=3.) if self.use_motion else None
    if self.use_motion and movement is None:
      self.motion.reset()
      self.last_decision = MapTurnDecision(False, 'model_movement_unavailable', spatial.distance_m)
      return False
    if not self.use_motion or speed > 1.6:
      self.motion.reset()
      self.last_mode = 'moving'
      return True
    if not self.motion.update(self.session, now, True, movement):
      self.last_decision = MapTurnDecision(False, 'model_movement_pending', spatial.distance_m)
      return False
    self.last_mode = 'forecast_movement'
    return True

  def record_cue(self):
    self.params.put('MapboxTurnCue', {'session': self.session, 'direction': self.direction,
      'cueAt': self.clock(), 'distanceM': self.last_decision.distance_m, 'leadM': self.lead_m,
      'cueMode': self.last_mode, 'forecastTravelM': self.motion.last_motion_m,
      'forecastTravelThresholdM': self.motion.threshold, 'forecastIntervalSeconds': [2., 3.]})
