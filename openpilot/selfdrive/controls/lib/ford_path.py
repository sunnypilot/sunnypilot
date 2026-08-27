from dataclasses import dataclass, replace
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_FIT_DISTANCE_M = 7.0
_COMMITTED_DISTANCE_M = 0.0
_REFERENCE_SAMPLES = 17
_C2_CURVATURE_LIMIT = 0.008
_C2_CENTERING_LIMIT = 0.003
_CURVATURE_REVERSAL_START = 0.0001
_CURVATURE_REVERSAL_FULL = 0.0003
_CURVATURE_RESIDUAL_DISTANCE_M = 4.0
_CURVATURE_ERROR_DISTANCE_M = 2.0
_CURVATURE_ERROR_LIMIT = 0.02
_PATH_ANGLE_RATE_LIMIT = 1.0
_MAX_MEASURED_YAW_RATE = 1.0


@dataclass(frozen=True)
class FordPath:
  valid: bool = False
  path_offset: float = 0.0
  path_angle: float = 0.0
  curvature: float = 0.0
  curvature_rate: float = 0.0


def _finite(value: float) -> float:
  return float(value) if math.isfinite(value) else 0.0


def _opposition_weight(requested_curvature: float, other_curvature: float) -> float:
  if requested_curvature * other_curvature >= 0.0:
    return 0.0
  return float(np.clip((abs(requested_curvature) - _CURVATURE_REVERSAL_START) /
                       (_CURVATURE_REVERSAL_FULL - _CURVATURE_REVERSAL_START), 0.0, 1.0))


def _model_path(model) -> tuple[np.ndarray, np.ndarray] | None:
  try:
    x = np.asarray(model.position.x, dtype=float)
    y = np.asarray(model.position.y, dtype=float)
  except (AttributeError, TypeError, ValueError):
    return None
  if len(x) < 3 or len(y) != len(x) or not np.isfinite(np.concatenate((x, y))).all():
    return None

  # LMC2 is y(x), so retain only the forward, monotonic part of a tight turn.
  end = 1
  while end < len(x) and x[end] > x[end - 1]:
    end += 1
  x = x[:end]
  y = y[:end]
  if len(x) < 3 or x[-1] - x[0] < 1.0:
    return None
  return x - x[0], y


def _advance_path(x: np.ndarray, y: np.ndarray, speed: float, yaw_rate: float,
                  dt: float) -> tuple[np.ndarray, np.ndarray]:
  distance = max(speed, 0.0) * dt
  yaw = yaw_rate * dt
  if abs(yaw_rate) < 1e-9:
    vehicle_x, vehicle_y = distance, 0.0
  else:
    radius = max(speed, 0.0) / yaw_rate
    vehicle_x = radius * math.sin(yaw)
    vehicle_y = radius * (1.0 - math.cos(yaw))
  cosine = math.cos(yaw)
  sine = math.sin(yaw)
  relative_x = x - vehicle_x
  relative_y = y - vehicle_y
  return cosine * relative_x + sine * relative_y, -sine * relative_x + cosine * relative_y


def _polynomial_reference(path: FordPath) -> tuple[np.ndarray, np.ndarray]:
  x = np.linspace(0.0, 2.0 * _FIT_DISTANCE_M, _REFERENCE_SAMPLES)
  y = (path.path_offset + math.tan(path.path_angle) * x + 0.5 * path.curvature * x ** 2 +
       path.curvature_rate * x ** 3 / 6.0)
  return x, y


def _merge_reference(old: tuple[np.ndarray, np.ndarray], fresh: tuple[np.ndarray, np.ndarray],
                     fallback: FordPath | None = None) -> tuple[np.ndarray, np.ndarray]:
  old_x, old_y = old
  fresh_x, fresh_y = fresh
  old_end = 1
  while old_end < len(old_x) and old_x[old_end] > old_x[old_end - 1] + 1e-3:
    old_end += 1
  old_x = old_x[:old_end]
  old_y = old_y[:old_end]
  if (len(old_x) < 2 or old_x[-1] < 1.0) and fallback is not None:
    old_x, old_y = _polynomial_reference(fallback)
  old_length = float(old_x[-1])
  length = min(float(fresh_x[-1]), 2.0 * _FIT_DISTANCE_M)
  if length < 1.0:
    return fresh

  x = np.linspace(0.0, length, _REFERENCE_SAMPLES)
  old_sample_y = np.interp(x, old_x, old_y)
  fresh_sample_y = np.interp(x, fresh_x, fresh_y)
  blend_span = max(_FIT_DISTANCE_M - _COMMITTED_DISTANCE_M, 1e-3)
  progress = np.clip((x - _COMMITTED_DISTANCE_M) / blend_span, 0.0, 1.0)
  weight = progress * progress * (3.0 - 2.0 * progress)
  weight[x > old_length] = 1.0
  return x, old_sample_y + weight * (fresh_sample_y - old_sample_y)


def _forward_prefix(path: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
  x, y = path
  end = 1
  while end < len(x) and x[end] > x[end - 1] + 1e-3:
    end += 1
  return x[:end], y[:end]


def _local_geometry(path: tuple[np.ndarray, np.ndarray]) -> tuple[float, float] | None:
  x, y = _forward_prefix(path)
  forward = (x >= -0.25) & (x <= _FIT_DISTANCE_M)
  x = x[forward]
  y = y[forward]
  if len(x) < 4 or x[-1] < 1.0:
    return None
  length = min(float(x[-1]), _FIT_DISTANCE_M)
  sample_x = np.linspace(0.0, length, _REFERENCE_SAMPLES)
  sample_y = np.interp(sample_x, x, y)
  slopes = np.gradient(sample_y, sample_x, edge_order=2)
  station = np.cumsum(np.hypot(np.diff(sample_x, prepend=sample_x[0]), np.diff(sample_y, prepend=sample_y[0])))
  heading = np.unwrap(np.arctan(slopes))
  geometry_samples = min(7, len(station))
  heading_fit = np.polynomial.polynomial.polyfit(station[:geometry_samples], heading[:geometry_samples], 2)
  geometric_curvature = float(heading_fit[1])
  geometric_curvature_rate = float(2.0 * heading_fit[2])
  return geometric_curvature, geometric_curvature_rate


def _fit_path(reference: tuple[np.ndarray, np.ndarray], desired_curvature: float | None = None,
              current_curvature: float | None = None) -> FordPath | None:
  x, y = _forward_prefix(reference)
  forward = (x >= -0.25) & (x <= _FIT_DISTANCE_M)
  x = x[forward]
  y = y[forward]
  if len(x) < 4 or x[-1] < 1.0:
    return None
  length = min(float(x[-1]), _FIT_DISTANCE_M)
  sample_x = np.linspace(0.0, length, _REFERENCE_SAMPLES)
  sample_y = np.interp(sample_x, x, y)
  slopes = np.gradient(sample_y, sample_x, edge_order=2)
  local_geometry = _local_geometry(reference)
  if local_geometry is None:
    return None
  geometric_curvature, geometric_curvature_rate = local_geometry
  curvature = float(np.clip(geometric_curvature, -_C2_CURVATURE_LIMIT, _C2_CURVATURE_LIMIT))
  curvature_rate = geometric_curvature_rate if abs(geometric_curvature) < _C2_CURVATURE_LIMIT else 0.0
  tracking_curvature = geometric_curvature
  curvature_error = 0.0
  if desired_curvature is not None:
    requested_curvature = _finite(desired_curvature)
    measured_curvature = _finite(current_curvature) if current_curvature is not None else 0.0
    scale_squared = _C2_CENTERING_LIMIT ** 2

    # Preserve an established rolling arc while the action begins to unwind,
    # but release it progressively as an opposing request clears the curvature noise band.
    arc_agreement = float(np.clip(geometric_curvature * measured_curvature / scale_squared, 0.0, 1.0))
    reversal = _opposition_weight(requested_curvature, measured_curvature)
    rolling_weight = arc_agreement * (1.0 - reversal)
    maneuver_curvature = requested_curvature + rolling_weight * (geometric_curvature - requested_curvature)

    # Retain a small geometric C2 band for centering. Larger maneuver curvature
    # uses C1, and geometry opposing a requested reversal is removed from C2.
    c2_limit = min(_C2_CURVATURE_LIMIT, max(abs(requested_curvature), _C2_CENTERING_LIMIT))
    bounded_curvature = float(np.clip(geometric_curvature, -c2_limit, c2_limit))
    opposition = _opposition_weight(requested_curvature, geometric_curvature)
    curvature = bounded_curvature * (1.0 - opposition)
    if curvature != float(np.clip(geometric_curvature, -_C2_CURVATURE_LIMIT, _C2_CURVATURE_LIMIT)):
      curvature_rate = 0.0

    allocated_curvature = float(np.clip(curvature, min(0.0, maneuver_curvature), max(0.0, maneuver_curvature)))
    tracking_curvature = maneuver_curvature + curvature - allocated_curvature
    if current_curvature is not None:
      curvature_error = float(np.clip(tracking_curvature - measured_curvature,
                                      -_CURVATURE_ERROR_LIMIT, _CURVATURE_ERROR_LIMIT))
  curvature_rate = float(np.clip(curvature_rate, DBC_CURVATURE_RATE[0], DBC_CURVATURE_RATE[1]))

  path_offset = float(np.clip(sample_y[0], DBC_OFFSET[0], DBC_OFFSET[1]))
  local_heading = math.atan(float(slopes[0]))
  # C0/C1 carry the rolling pose error and the fast part of the turn. The
  # curvature error term continuously adds command while the vehicle is behind
  # and countersteers while the PSCM's filtered C2 is draining.
  path_angle = (local_heading + _CURVATURE_RESIDUAL_DISTANCE_M * (tracking_curvature - curvature) +
                _CURVATURE_ERROR_DISTANCE_M * curvature_error)
  return FordPath(
    valid=True,
    path_offset=path_offset,
    path_angle=float(np.clip(path_angle, DBC_ANGLE[0], DBC_ANGLE[1])),
    curvature=curvature,
    curvature_rate=curvature_rate,
  )


def _model_key(model) -> tuple[int, int] | int:
  try:
    frame_id = int(model.frameId)
    timestamp = int(model.timestampEof)
    if frame_id or timestamp:
      return frame_id, timestamp
  except (AttributeError, TypeError, ValueError):
    pass
  return id(model)


class FordPathController:
  """Track one rolling Ford path reference without modeling PSCM actuation."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._reference: tuple[np.ndarray, np.ndarray] | None = None
    self._last_model_key: tuple[int, int] | int | None = None
    self._last_path: FordPath | None = None

  def reset(self) -> None:
    self._reference = None
    self._last_model_key = None
    self._last_path = None

  def _finish(self, path: FordPath, rate_limit: bool) -> FordPath:
    if rate_limit:
      previous_angle = self._last_path.path_angle if self._last_path is not None else 0.0
      max_delta = _PATH_ANGLE_RATE_LIMIT * self.dt
      path = replace(path, path_angle=float(np.clip(path.path_angle, previous_angle - max_delta, previous_angle + max_delta)))
    self._last_path = path
    return path

  def update(self, model, desired_curvature: float | None = None, *, v_ego: float = 0.0, active: bool = True,
             current_curvature: float | None = None, yaw_rate: float = 0.0, actuator_delay: float = 0.0) -> FordPath:
    del actuator_delay
    if not active or model is None:
      self.reset()
      return FordPath()

    measured_yaw_rate = _finite(yaw_rate)
    if abs(measured_yaw_rate) > _MAX_MEASURED_YAW_RATE:
      measured_yaw_rate = 0.0
    if self._reference is not None:
      self._reference = _advance_path(self._reference[0], self._reference[1], max(_finite(v_ego), 0.0),
                                      measured_yaw_rate, self.dt)
    fresh = _model_path(model)
    if fresh is None:
      path = _fit_path(self._reference, desired_curvature, current_curvature) if self._reference is not None else None
      if path is not None:
        return self._finish(path, desired_curvature is not None)
      self.reset()
      return FordPath()

    model_key = _model_key(model)
    if self._reference is None:
      self._reference = fresh
    elif model_key != self._last_model_key:
      self._reference = _merge_reference(self._reference, fresh, self._last_path)
    self._last_model_key = model_key

    path = _fit_path(self._reference, desired_curvature, current_curvature)
    if path is None:
      seed = _polynomial_reference(self._last_path) if self._last_path is not None else fresh
      self._reference = _merge_reference(seed, fresh, self._last_path)
      path = _fit_path(self._reference, desired_curvature, current_curvature)
    if path is None:
      self.reset()
      return FordPath()
    return self._finish(path, desired_curvature is not None)


def encode_ford_path(model, t_prev: float, desired_curvature: float | None = None, *, v_ego: float = 0.0,
                     current_curvature: float | None = None, yaw_rate: float = 0.0, actuator_delay: float = 0.0) -> FordPath:
  """Stateless compatibility helper; live control uses FordPathController."""
  del t_prev
  return FordPathController().update(model, desired_curvature, v_ego=v_ego, current_curvature=current_curvature,
                                     yaw_rate=yaw_rate, actuator_delay=actuator_delay)
