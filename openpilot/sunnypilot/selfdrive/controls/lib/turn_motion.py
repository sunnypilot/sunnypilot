"""Read predicted travel from an existing model trajectory, without altering it."""
from bisect import bisect_right
import math
from numbers import Real


def predicted_travel(position, start=1., end=2.):
  """XY arc length over model time [start,end], or None for invalid input.

  Travel follows the planned curve rather than only forward x, so an ordinary
  corner does not falsely look stationary. This is a motion forecast, not a
  traffic permission or a curb-clearance estimate.
  """
  try:
    times, xs, ys = list(position.t), list(position.x), list(position.y)
    if not 2 <= len(times) == len(xs) == len(ys) <= 256:
      return None
    if not all(math.isfinite(v) for values in (times, xs, ys) for v in values):
      return None
    if not times[0] <= start < end <= times[-1] or any(b <= a for a, b in zip(times[:-1], times[1:], strict=True)):
      return None

    def point(t):
      index = min(bisect_right(times, t)-1, len(times)-2)
      ratio = (t-times[index])/(times[index+1]-times[index])
      return (xs[index]+ratio*(xs[index+1]-xs[index]), ys[index]+ratio*(ys[index+1]-ys[index]))

    samples = [point(start), *((x, y) for t, x, y in zip(times, xs, ys, strict=True) if start < t < end), point(end)]
    return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(samples[:-1], samples[1:], strict=True))
  except (AttributeError, TypeError, ValueError, IndexError, OverflowError):
    return None


class TurnMotionReadiness:
  """Require a continuous forecast predicate within one valid map session.

  Pass the current native model frame's timestamp and motion forecast. The
  timestamp checks detect missing/out-of-order updates, not geometry reused by
  a caller with an invented newer timestamp. This class grants no actuator or
  traffic permission and does not inspect current vehicle speed.
  """
  MAX_NATIVE_GAP = .075
  TIME_TOLERANCE = 1e-9

  def __init__(self, threshold=1.5, persistence=.2):
    threshold, persistence = self._scalar(threshold), self._scalar(persistence)
    if threshold is None or threshold <= 0. or persistence is None or persistence < 0.:
      raise ValueError('Motion threshold must be positive and persistence nonnegative; both must be finite numbers')
    self.threshold, self.persistence = threshold, persistence
    self.reset()

  @staticmethod
  def _scalar(value):
    if isinstance(value, bool) or not isinstance(value, Real):
      return None
    try:
      return float(value) if math.isfinite(value) else None
    except (TypeError, ValueError, OverflowError):
      return None

  def reset(self):
    self.session = None
    self.last_time = None
    self.last_motion_m = None
    self.since = None

  def update(self, session, now, spatial_allowed, motion_m):
    now, motion = self._scalar(now), self._scalar(motion_m)
    if not isinstance(session, str) or not session or now is None or spatial_allowed is not True or motion is None or motion < 0.:
      self.reset()
      return False
    if session != self.session:
      self.reset()
    if self.last_time is not None and (now <= self.last_time or now-self.last_time > self.MAX_NATIVE_GAP+self.TIME_TOLERANCE):
      self.since = None
    self.session, self.last_time, self.last_motion_m = session, now, motion
    if motion < self.threshold:
      self.since = None
      return False
    if self.since is None:
      self.since = now
    return now-self.since >= self.persistence-self.TIME_TOLERANCE
