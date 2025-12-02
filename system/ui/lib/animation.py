import time


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
