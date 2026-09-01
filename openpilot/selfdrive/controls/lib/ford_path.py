from collections import deque
from dataclasses import dataclass
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_MIN_LOOKAHEAD = 7.0
_POSE_PREDICTION_TIME = 0.1
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


def _finite(value: float) -> float:
  return float(value) if math.isfinite(value) else 0.0


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


def _predicted_pose(distance: float, current_curvature: float,
                    curvature_delta: float) -> tuple[float, float, float]:
  curvature = current_curvature + 0.5 * curvature_delta
  heading = curvature * distance
  if abs(curvature) < 1e-9:
    return distance, 0.0, 0.0
  return math.sin(heading) / curvature, (1.0 - math.cos(heading)) / curvature, heading


def _relative_pose(target_distance: float, path: tuple[list[float], list[float], list[float], list[float]],
                   vehicle_pose: tuple[float, float, float]) -> tuple[float, float]:
  distance, x, y, heading = path
  vehicle_x, vehicle_y, vehicle_heading = vehicle_pose
  dx = _sample(target_distance, distance, x) - vehicle_x
  dy = _sample(target_distance, distance, y) - vehicle_y
  cosine = math.cos(vehicle_heading)
  sine = math.sin(vehicle_heading)
  offset = -sine * dx + cosine * dy
  angle = math.atan2(math.sin(_sample(target_distance, distance, heading) - vehicle_heading),
                     math.cos(_sample(target_distance, distance, heading) - vehicle_heading))
  return offset, angle


def _encode_path(path: tuple[list[float], list[float], list[float], list[float]], desired_curvature: float,
                 current_curvature: float, curvature_delta: float, v_ego: float) -> FordPath:
  distance, _, _, _ = path
  advance = min(v_ego * _POSE_PREDICTION_TIME, distance[-1])
  offset_horizon = min(_PATH_MIN_LOOKAHEAD, distance[-1] - advance)
  angle_horizon = min(max(v_ego, _PATH_MIN_LOOKAHEAD), distance[-1] - advance)
  vehicle_pose = _predicted_pose(advance, current_curvature, curvature_delta)
  model_offset, _ = _relative_pose(advance + offset_horizon, path, vehicle_pose)
  _, model_angle = _relative_pose(advance + angle_horizon, path, vehicle_pose)

  offset_curvature = 2.0 * model_offset / max(offset_horizon, 1e-3) ** 2
  angle_curvature = model_angle / max(angle_horizon, 1e-3)
  pose_share = _blend_share(max(abs(offset_curvature), abs(angle_curvature), abs(desired_curvature)))
  curvature = desired_curvature * (1.0 - pose_share)
  if curvature * model_angle < 0.0:
    curvature = 0.0
    pose_share = 1.0

  # C2 owns normal path following. As model pose demand grows, transfer the
  # same delay-aligned path continuously to the faster C0/C1 fields.
  path_offset = pose_share * model_offset
  path_angle = pose_share * model_angle
  limited_path_angle = float(np.clip(path_angle, *DBC_ANGLE))
  path_offset += (path_angle - limited_path_angle) * offset_horizon
  return FordPath(
    valid=True,
    path_offset=float(np.clip(path_offset, *DBC_OFFSET)),
    path_angle=limited_path_angle,
    curvature=float(np.clip(curvature, *DBC_CURVATURE)),
    curvature_rate=0.0,
  )


class FordPathController:
  """Blend normal C2 following into the model's forward C0/C1 pose."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)
    self._curvature_history = deque(maxlen=max(round(_POSE_PREDICTION_TIME / dt) + 1, 2))

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

  def update(self, model, desired_curvature: float, *, current_curvature: float = 0.0,
             v_ego: float = 0.0, active: bool = True) -> FordPath:
    if not active:
      self._last_path = FordPath(valid=True)
      self._curvature_history.clear()
      return FordPath()
    current_curvature = _finite(current_curvature)
    self._curvature_history.append(current_curvature)
    curvature_delta = (current_curvature - self._curvature_history[0]
                       if len(self._curvature_history) == self._curvature_history.maxlen else 0.0)
    path = _model_path(model) if model is not None else None
    if path is None:
      return self._limit(FordPath(valid=True))
    return self._limit(_encode_path(path, _finite(desired_curvature), current_curvature, curvature_delta,
                                    max(_finite(v_ego), 0.0)))
