from dataclasses import dataclass, fields
import math

import numpy as np

from openpilot.selfdrive.controls.lib.drive_helpers import MAX_CURVATURE


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_HORIZON = 7.0
_CURVATURE_RATE_HORIZONS = (3.5, 5.0, 7.0)
_FAST_POSE_CURVATURE_BAND = (0.009, 0.012)
_CURVATURE_NOISE_FLOOR = 0.0005
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


def _curvature_rate(path: tuple[list[float], list[float], list[float]]) -> float:
  distance, _, heading = path
  rates = []
  for requested_horizon in _CURVATURE_RATE_HORIZONS:
    horizon = min(requested_horizon, distance[-1])
    start = _sample(0.0, distance, heading)
    midpoint = _sample(0.5 * horizon, distance, heading)
    end = _sample(horizon, distance, heading)
    rates.append(4.0 * (start - 2.0 * midpoint + end) / horizon ** 2)

  magnitude = sum(abs(rate) for rate in rates)
  if magnitude == 0.0:
    return 0.0
  return sorted(rates)[1] * abs(sum(rates)) / magnitude


def _encode_path(model, desired_curvature: float, v_ego: float, current_curvature: float | None) -> FordPath:
  path = _model_path(model)
  if path is None:
    return FordPath()

  model_curvature_rate = _curvature_rate(path)
  action_curvature = _finite(desired_curvature)
  measured_curvature = float(np.clip(_finite(current_curvature), -MAX_CURVATURE, MAX_CURVATURE)) \
    if current_curvature is not None else 0.0

  future_curvature = action_curvature + model_curvature_rate * max(_finite(v_ego), _PATH_HORIZON)
  sustained_curvature = 0.0
  if action_curvature * future_curvature > 0.0 and abs(future_curvature) > _CURVATURE_NOISE_FLOOR:
    sustained_curvature = math.copysign(min(abs(action_curvature), abs(future_curvature)), action_curvature)
  maneuver_share = float(np.interp(abs(action_curvature), _FAST_POSE_CURVATURE_BAND, (0.0, 1.0)))
  centering_curvature = sustained_curvature * (1.0 - maneuver_share)
  fast_curvature = (action_curvature - centering_curvature) + (action_curvature - measured_curvature)
  path_offset = 0.5 * fast_curvature * _PATH_HORIZON ** 2
  path_angle = fast_curvature * _PATH_HORIZON

  return FordPath(
    valid=True,
    path_offset=float(np.clip(path_offset, *DBC_OFFSET)),
    path_angle=float(np.clip(path_angle, *DBC_ANGLE)),
    curvature=float(np.clip(centering_curvature, *DBC_CURVATURE)),
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

  def update(self, model, desired_curvature: float, *, v_ego: float = 0.0, active: bool = True,
             current_curvature: float | None = None) -> FordPath:
    if not active:
      self._last_path = FordPath(valid=True)
      return FordPath()
    if model is None:
      return self._limit(FordPath(valid=True))
    return self._limit(_encode_path(model, desired_curvature, v_ego, current_curvature))
