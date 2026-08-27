from dataclasses import dataclass, fields
import math

import numpy as np


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

_PATH_OFFSET_DISTANCE = 7.0
_PATH_MIN_LOOKAHEAD = 7.0
_CURVATURE_RATE_HORIZONS = (3.5, 5.0, 7.0)
_CENTERING_CURVATURE_BASEBAND = (0.003, 0.006)
_TRACKING_ERROR_DEADZONE = 0.0005
_TRACKING_ERROR_LIMIT = 0.012
_PATH_RATES = (4.0, 1.0, math.inf, 0.002)


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


def _curvature(path: tuple[list[float], list[float], list[float]]) -> float:
  distance, _, heading = path
  horizon = min(_PATH_MIN_LOOKAHEAD, distance[-1])
  return (_sample(horizon, distance, heading) - _sample(0.0, distance, heading)) / horizon


def _encode_path(model, desired_curvature: float | None, v_ego: float, current_curvature: float | None) -> FordPath:
  path = _model_path(model)
  if path is None:
    return FordPath()

  distance, offset, heading = path
  lookahead = max(_finite(v_ego), _PATH_MIN_LOOKAHEAD)
  path_offset = _sample(_PATH_OFFSET_DISTANCE, distance, offset)
  path_angle = _sample(lookahead, distance, heading)
  model_curvature = _curvature(path)
  model_curvature_rate = _curvature_rate(path)
  action_curvature = model_curvature if desired_curvature is None else _finite(desired_curvature)
  requested_curvature = max((model_curvature, action_curvature), key=abs)
  maneuver_residual = requested_curvature - model_curvature
  path_offset += 0.5 * maneuver_residual * _PATH_OFFSET_DISTANCE ** 2
  path_angle += maneuver_residual * lookahead
  correction = 0.0
  tracking_demand = 0.0
  wheel_beyond_target = False
  if current_curvature is not None:
    target_curvature = action_curvature
    measured_curvature = _finite(current_curvature)
    tracking_error = target_curvature - measured_curvature
    correction = math.copysign(max(abs(tracking_error) - _TRACKING_ERROR_DEADZONE, 0.0), tracking_error)
    tracking_demand = abs(correction)
    wheel_beyond_target = target_curvature * measured_curvature > 0.0 and \
      abs(target_curvature) + _TRACKING_ERROR_DEADZONE < abs(measured_curvature)
    correction_limit = _TRACKING_ERROR_LIMIT
    if correction * target_curvature < 0.0:
      correction_limit = 0.5 * abs(target_curvature)
    correction = float(np.clip(correction, -correction_limit, correction_limit))
    correction_offset = 0.5 * correction * _PATH_OFFSET_DISTANCE ** 2
    correction_angle = correction * lookahead
    if wheel_beyond_target:
      path_offset = correction_offset
      path_angle = correction_angle
    else:
      path_offset += correction_offset
      path_angle += correction_angle

  spatial_demand = abs(model_curvature_rate) * lookahead / 3.0
  overflow_demand = max(abs(requested_curvature) - DBC_CURVATURE[1], 0.0)
  maneuver_demand = max(spatial_demand, overflow_demand, tracking_demand)
  maneuver_share = 1.0 if wheel_beyond_target else \
    float(np.interp(maneuver_demand, _CENTERING_CURVATURE_BASEBAND, (0.0, 1.0)))
  path_offset *= maneuver_share
  path_angle *= maneuver_share
  centering_curvature = action_curvature

  return FordPath(
    valid=True,
    path_offset=float(np.clip(path_offset, *DBC_OFFSET)),
    path_angle=float(np.clip(path_angle, *DBC_ANGLE)),
    curvature=float(np.clip(centering_curvature * (1.0 - maneuver_share), *DBC_CURVATURE)),
    curvature_rate=float(np.clip(model_curvature_rate * maneuver_share, *DBC_CURVATURE_RATE)),
  )


class FordPathController:
  """Convert the model path directly into one vehicle-independent Ford path command."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)

  def reset(self) -> None:
    self._last_path = FordPath(valid=True)

  def _limit(self, target: FordPath) -> FordPath:
    values = []
    for field, rate in zip(fields(FordPath)[1:], _PATH_RATES, strict=True):
      previous = getattr(self._last_path, field.name)
      value = getattr(target, field.name)
      values.append(float(np.clip(value, previous - rate * self.dt, previous + rate * self.dt)))
    self._last_path = FordPath(True, *values)
    return self._last_path

  def update(self, model, desired_curvature: float | None = None, *, v_ego: float = 0.0, active: bool = True,
             current_curvature: float | None = None, yaw_rate: float = 0.0, actuator_delay: float = 0.0) -> FordPath:
    del yaw_rate, actuator_delay
    if not active:
      self.reset()
      return FordPath()
    if model is None:
      return self._limit(FordPath(valid=True))
    return self._limit(_encode_path(model, desired_curvature, v_ego, current_curvature))


def encode_ford_path(model, t_prev: float, desired_curvature: float | None = None, *, v_ego: float = 0.0,
                     current_curvature: float | None = None, yaw_rate: float = 0.0, actuator_delay: float = 0.0) -> FordPath:
  del t_prev, yaw_rate, actuator_delay
  return _encode_path(model, desired_curvature, v_ego, current_curvature)
