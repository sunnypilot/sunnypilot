from dataclasses import dataclass
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_MIN_LOOKAHEAD = 7.0
_POSE_BLEND_CURVATURE = (0.006, 0.012)
_PATH_OFFSET_RATE = 4.0
_PATH_ANGLE_RATE = 1.0


@dataclass(frozen=True)
class FordPath:
  valid: bool = False
  path_offset: float = 0.0
  path_angle: float = 0.0
  curvature: float = 0.0
  curvature_rate: float = 0.0


def _sample(distance: float, distances: list[float], values: list[float]) -> float:
  return float(np.interp(distance, distances, values))


def _blend_share(demand: float) -> float:
  lower, upper = _POSE_BLEND_CURVATURE
  return float(np.clip((demand - lower) / (upper - lower), 0.0, 1.0))


def _model_path(model) -> tuple[list[float], list[float], list[float], list[float]] | None:
  try:
    x = [float(value) for value in model.position.x]
    y = [float(value) for value in model.position.y]
    heading = [float(value) for value in model.orientation.z]
  except (AttributeError, TypeError, ValueError):
    return None
  if len(x) < 2 or len(x) != len(y) or len(x) != len(heading):
    return None
  if not all(math.isfinite(value) for values in (x, y, heading) for value in values):
    return None

  distance = [0.0]
  for i in range(1, len(x)):
    distance.append(distance[-1] + math.hypot(x[i] - x[i - 1], y[i] - y[i - 1]))
  if distance[-1] <= 0.0:
    return None

  unwrapped_heading = [heading[0]]
  for value in heading[1:]:
    delta = (value - unwrapped_heading[-1] + math.pi) % (2.0 * math.pi) - math.pi
    unwrapped_heading.append(unwrapped_heading[-1] + delta)
  return distance, x, y, unwrapped_heading


def _encode_path(path: tuple[list[float], list[float], list[float], list[float]]) -> FordPath:
  distance, _, y, heading = path
  target_distance = min(_PATH_MIN_LOOKAHEAD, distance[-1])
  horizon = max(target_distance, 1e-3)

  model_offset = _sample(target_distance, distance, y)
  model_angle = _sample(target_distance, distance, heading)
  start_heading = _sample(0.0, distance, heading)
  midpoint_heading = _sample(0.5 * horizon, distance, heading)
  target_heading = _sample(target_distance, distance, heading)
  near_curvature = 2.0 * (midpoint_heading - start_heading) / horizon
  far_curvature = 2.0 * (target_heading - midpoint_heading) / horizon
  model_curvature = 0.5 * (near_curvature + far_curvature)

  offset_curvature = 2.0 * model_offset / horizon ** 2
  angle_curvature = model_angle / horizon
  magnitude_share = _blend_share(max(abs(offset_curvature), abs(angle_curvature), abs(model_curvature)))
  curvature_sum = abs(near_curvature) + abs(far_curvature)
  change_share = min(abs(far_curvature - near_curvature) / curvature_sum, 1.0) if curvature_sum > 0.0 else 0.0
  pose_share = 1.0 - (1.0 - magnitude_share) * (1.0 - change_share)

  # All fields describe the same current-frame rolling model path. C2 carries
  # steady gentle curvature; changing or larger remaining poses transfer
  # continuously to the faster C0/C1 fields.
  path_offset = pose_share * model_offset
  path_angle = pose_share * model_angle
  limited_path_angle = float(np.clip(path_angle, *DBC_ANGLE))
  path_offset += (path_angle - limited_path_angle) * horizon
  curvature = model_curvature * (1.0 - pose_share)
  return FordPath(
    valid=True,
    path_offset=float(np.clip(path_offset, *DBC_OFFSET)),
    path_angle=limited_path_angle,
    curvature=float(np.clip(curvature, *DBC_CURVATURE)),
    curvature_rate=0.0,
  )


class FordPathController:
  """Encode one current-frame rolling model path as C0/C1/C2."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)

  def _limit(self, target: FordPath) -> FordPath:
    offset_delta = target.path_offset - self._last_path.path_offset
    angle_delta = target.path_angle - self._last_path.path_angle
    scale = min(
      1.0,
      _PATH_OFFSET_RATE * self.dt / abs(offset_delta) if offset_delta else 1.0,
      _PATH_ANGLE_RATE * self.dt / abs(angle_delta) if angle_delta else 1.0,
    )
    self._last_path = FordPath(
      True,
      self._last_path.path_offset + scale * offset_delta,
      self._last_path.path_angle + scale * angle_delta,
      self._last_path.curvature + scale * (target.curvature - self._last_path.curvature),
      0.0,
    )
    return self._last_path

  def update(self, model, *, active: bool = True) -> FordPath:
    if not active:
      self._last_path = FordPath(valid=True)
      return FordPath()
    path = _model_path(model) if model is not None else None
    if path is None:
      return self._limit(FordPath(valid=True))
    return self._limit(_encode_path(path))
