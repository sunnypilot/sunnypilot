import time
import pyray as rl


def clamp01(value: float) -> float:
  """Clamp a float to the [0, 1] range."""
  return max(0.0, min(1.0, value))


def ease_out_cubic(t: float) -> float:
  """Standard cubic ease-out used across Tizi UI transitions."""
  t = clamp01(t)
  return 1 - pow(1 - t, 3)


def elapsed_progress(start_time: float, duration: float, now: float | None = None) -> float:
  """
  Convert a start timestamp and duration into a 0..1 progress value.
  Useful for animations that store a start time instead of last frame time.
  """
  if now is None:
    now = time.monotonic()
  if duration <= 0:
    return 1.0
  return clamp01((now - start_time) / duration)


def advance_progress(progress: float, last_time: float | None, duration: float, direction: float,
                     now: float | None = None) -> tuple[float, float]:
  """
  Advance a progress accumulator using delta time.
  Returns the updated (progress, last_time).
  direction should be +1 for forward and -1 for reverse.
  """
  if now is None:
    now = time.monotonic()
  if last_time is None or duration <= 0:
    return progress, now

  delta = direction * (now - last_time) / duration
  return clamp01(progress + delta), now


def smooth_towards(current: float, target: float, speed: float, dt: float) -> float:
  """
  Smoothly approach `target` from `current` using a simple exponential decay.
  `speed` is a multiplier controlling how quickly it converges; `dt` is delta time in seconds.
  """
  if dt <= 0 or speed <= 0:
    return target if dt > 0 else current
  return current + (target - current) * clamp01(speed * dt)


def scale_from_center(rect, scale: float, draw_fn):
  """
  Utility to temporarily scale rendering around the center of `rect`.
  `draw_fn` will be called while the transform is active.
  """
  if scale == 1.0:
    draw_fn()
    return

  cx = rect.x + rect.width / 2
  cy = rect.y + rect.height / 2
  rl.rl_push_matrix()
  rl.rl_translatef(cx, cy, 0)
  rl.rl_scalef(scale, scale, 1)
  rl.rl_translatef(-cx, -cy, 0)
  draw_fn()
  rl.rl_pop_matrix()


def fade_color(color: rl.Color, alpha: float) -> rl.Color:
  """Apply multiplier alpha to a color's alpha channel. Accepts rl.Color or (r,g,b[,a]) tuples."""
  if hasattr(color, "r"):
    r, g, b, a = color.r, color.g, color.b, color.a
  else:
    try:
      r, g, b = int(color[0]), int(color[1]), int(color[2])
      a = int(color[3]) if len(color) > 3 else 255
    except Exception:
      # fallback to white if unexpected input
      r, g, b, a = 255, 255, 255, 255
  return rl.Color(r, g, b, int(a * clamp01(alpha)))


class LinearAnimation:
  """
  Small helper to manage simple linear progress animations.
  Call start('in'|'out') to begin, then step() each frame to advance.
  """
  def __init__(self, duration: float, initial_progress: float = 0.0):
    self.duration = duration
    self.progress = clamp01(initial_progress)
    self.last_time: float | None = None
    self.direction = 1.0
    self.active = False

  def start(self, direction: str):
    self.direction = 1.0 if direction == 'in' else -1.0
    self.active = True
    self.last_time = None
    self.progress = 0.0 if self.direction > 0 else 1.0

  def step(self, now: float | None = None) -> float:
    """Advance animation; returns current progress."""
    if not self.active:
      return self.progress

    self.progress, self.last_time = advance_progress(self.progress, self.last_time, self.duration, self.direction, now)

    if (self.direction > 0 and self.progress >= 1.0) or (self.direction < 0 and self.progress <= 0.0):
      self.active = False
    return self.progress

  def direction_str(self) -> str:
    return 'in' if self.direction > 0 else 'out'
