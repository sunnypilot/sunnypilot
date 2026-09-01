from dataclasses import dataclass
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_LOOKAHEAD_TIME = 1.0
_PATH_MIN_LOOKAHEAD = 7.0
_MANEUVER_ENTER_CURVATURE = 0.018
_MANEUVER_EXIT_CURVATURE = 0.012
_PATH_OFFSET_RATE = 4.0
_PATH_ANGLE_RATE = 1.0


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


def _encode_path(model_offset: float, model_angle: float, desired_curvature: float, maneuver: bool) -> FordPath:
  action_curvature = _finite(desired_curvature)

  return FordPath(
    valid=True,
    path_offset=float(np.clip(model_offset, *DBC_OFFSET)) if maneuver else 0.0,
    path_angle=float(np.clip(model_angle, *DBC_ANGLE)) if maneuver else 0.0,
    curvature=0.0 if maneuver else float(np.clip(action_curvature, *DBC_CURVATURE)),
    curvature_rate=0.0,
  )


class FordPathController:
  """Convert the model path directly into one vehicle-independent Ford path command."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)
    self._maneuver = False

  def _limit(self, target: FordPath) -> FordPath:
    path_offset = float(np.clip(target.path_offset,
                                self._last_path.path_offset - _PATH_OFFSET_RATE * self.dt,
                                self._last_path.path_offset + _PATH_OFFSET_RATE * self.dt))
    path_angle = float(np.clip(target.path_angle,
                               self._last_path.path_angle - _PATH_ANGLE_RATE * self.dt,
                               self._last_path.path_angle + _PATH_ANGLE_RATE * self.dt))
    # Never stack the normal C2 path on a maneuver pose while C0/C1 are slewing out.
    curvature = target.curvature if path_offset == 0.0 and path_angle == 0.0 else 0.0
    self._last_path = FordPath(True, path_offset, path_angle, curvature, 0.0)
    return self._last_path

  def update(self, model, desired_curvature: float, *, v_ego: float = 0.0, active: bool = True) -> FordPath:
    if not active:
      self._last_path = FordPath(valid=True)
      self._maneuver = False
      return FordPath()
    path = _model_path(model) if model is not None else None
    if path is None:
      self._maneuver = False
      return self._limit(FordPath(valid=True))

    distance, offset, heading = path
    lookahead = min(max(_finite(v_ego) * _PATH_LOOKAHEAD_TIME, _PATH_MIN_LOOKAHEAD), distance[-1])
    model_offset = _sample(lookahead, distance, offset)
    model_angle = _sample(lookahead, distance, heading)
    demand = max(abs(_finite(desired_curvature)), abs(model_angle / lookahead))
    if self._maneuver:
      self._maneuver = demand >= _MANEUVER_EXIT_CURVATURE
    else:
      self._maneuver = demand >= _MANEUVER_ENTER_CURVATURE

    return self._limit(_encode_path(model_offset, model_angle, desired_curvature, self._maneuver))
