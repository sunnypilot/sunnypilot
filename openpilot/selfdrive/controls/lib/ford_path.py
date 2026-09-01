from dataclasses import dataclass, fields
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_LOOKAHEAD_TIME = 0.5
_PATH_MIN_LOOKAHEAD = 7.0
_FAST_POSE_CURVATURE_BAND = (0.009, 0.012)
_PATH_RATES = (4.0, 1.0, math.inf, math.inf)


@dataclass(frozen=True)
class FordPath:
  valid: bool = False
  path_offset: float = 0.0
  path_angle: float = 0.0
  curvature: float = 0.0
  curvature_rate: float = 0.0


def _finite(value: float) -> float:
  return float(value) if math.isfinite(value) else 0.0


def _sample(distance: float, distances: list[float], values: list[float]) -> float:
  return float(np.interp(distance, distances, values))


def _model_path(model) -> tuple[list[float], list[float], list[float]] | None:
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
  return distance, y, unwrapped_heading


def _encode_path(model, desired_curvature: float, v_ego: float) -> FordPath:
  path = _model_path(model)
  if path is None:
    return FordPath()

  distance, offset, heading = path
  lookahead = min(max(_finite(v_ego) * _PATH_LOOKAHEAD_TIME, _PATH_MIN_LOOKAHEAD), distance[-1])
  model_offset = _sample(lookahead, distance, offset)
  model_angle = _sample(lookahead, distance, heading)
  action_curvature = _finite(desired_curvature)
  model_demand = max(abs(2.0 * model_offset / lookahead ** 2), abs(model_angle / lookahead))
  maneuver_share = float(np.interp(max(abs(action_curvature), model_demand), _FAST_POSE_CURVATURE_BAND, (0.0, 1.0)))

  return FordPath(
    valid=True,
    path_offset=float(np.clip(model_offset * maneuver_share, *DBC_OFFSET)),
    path_angle=float(np.clip(model_angle * maneuver_share, *DBC_ANGLE)),
    curvature=float(np.clip(action_curvature, *DBC_CURVATURE)) * (1.0 - maneuver_share),
    curvature_rate=0.0,
  )


class FordPathController:
  """Convert the model path directly into one vehicle-independent Ford path command."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)

  def _limit(self, target: FordPath) -> FordPath:
    values = []
    for field, rate in zip(fields(FordPath)[1:], _PATH_RATES, strict=True):
      previous = getattr(self._last_path, field.name)
      value = getattr(target, field.name)
      values.append(float(np.clip(value, previous - rate * self.dt, previous + rate * self.dt)))
    self._last_path = FordPath(True, *values)
    return self._last_path

  def update(self, model, desired_curvature: float, *, v_ego: float = 0.0, active: bool = True) -> FordPath:
    if not active:
      self._last_path = FordPath(valid=True)
      return FordPath()
    if model is None:
      return self._limit(FordPath(valid=True))
    return self._limit(_encode_path(model, desired_curvature, v_ego))
