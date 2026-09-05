from collections import deque
from dataclasses import dataclass
import math

import numpy as np

from opendbc.car.ford.values import CarControllerParams


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)

DBC_OFFSET_RESOLUTION = 0.01
DBC_ANGLE_RESOLUTION = 0.0005
DBC_CURVATURE_RESOLUTION = 0.00002
DBC_CURVATURE_RATE_RESOLUTION = 0.000001
_PATH_MIN_LOOKAHEAD = 7.0
_POSE_PREDICTION_TIME = 0.1
_POSE_BLEND_CURVATURE = (0.006, 0.012)
_PATH_OFFSET_RATE = 4.0
_PATH_ANGLE_RATE = 1.0

_PSCM_DT = 0.004
_PSCM_C0_RATE = 1.5
_PSCM_C1_RATE = 0.100006103515625
_PSCM_C2_RATE = 0.0030059814453125
_PSCM_SPEED_KPH = (0.0, 15.0, 40.0, 70.0, 100.0, 150.0, 200.0, 250.0)
_PSCM_SPEED_GAIN = (32.0, 32.0, 32.0, 30.0, 30.0, 24.0, 12.0, 0.0)
_PSCM_C0_EFFECTIVE_LIMIT = 1.0
_PSCM_C1_EFFECTIVE_LIMIT = 0.349609375 / 10.0


@dataclass(frozen=True)
class FordPath:
  valid: bool = False
  path_offset: float = 0.0
  path_angle: float = 0.0
  curvature: float = 0.0
  curvature_rate: float = 0.0


@dataclass(frozen=True)
class FordPscmState:
  path_offset: float = 0.0
  path_angle: float = 0.0
  curvature: float = 0.0


@dataclass(frozen=True)
class FordModelPose:
  path_offset: float
  path_angle: float
  offset_horizon: float
  curvature_demand: float
  forward_angle: float


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


def _path_pose(target_distance: float,
               path: tuple[list[float], list[float], list[float], list[float]]) -> tuple[float, float, float]:
  distance, x, y, heading = path
  return (_sample(target_distance, distance, x), _sample(target_distance, distance, y),
          _sample(target_distance, distance, heading))


def _bounded_feedback(feedforward: float, feedback: float, resolution: float, zero_path_limit: float) -> float:
  quantization_threshold = 0.5 * resolution
  limit = max(abs(feedforward) - resolution, 0.0) if abs(feedforward) >= quantization_threshold else zero_path_limit
  return float(np.clip(feedback, -limit, limit))


def _model_pose(path: tuple[list[float], list[float], list[float], list[float]],
                current_curvature: float, curvature_delta: float, v_ego: float) -> FordModelPose:
  distance, _, _, _ = path
  advance = min(v_ego * _POSE_PREDICTION_TIME, distance[-1])
  offset_horizon = min(_PATH_MIN_LOOKAHEAD, distance[-1] - advance)
  angle_horizon = min(max(v_ego, _PATH_MIN_LOOKAHEAD), distance[-1] - advance)

  # Keep the model's remaining path as feedforward. Measured vehicle motion is
  # a separate, short delay-aligned correction, so catching the requested
  # curvature cannot erase a turn that is still present in the model path.
  model_pose = _path_pose(advance, path)
  model_offset, _ = _relative_pose(advance + offset_horizon, path, model_pose)
  _, model_angle = _relative_pose(advance + angle_horizon, path, model_pose)
  vehicle_pose = _predicted_pose(advance, current_curvature, curvature_delta)
  feedback_offset, feedback_angle = _relative_pose(advance, path, vehicle_pose)
  gentle_curvature = _POSE_BLEND_CURVATURE[0]
  feedback_offset = _bounded_feedback(model_offset, feedback_offset, DBC_OFFSET_RESOLUTION,
                                       0.5 * gentle_curvature * advance ** 2)
  feedback_angle = _bounded_feedback(model_angle, feedback_angle, DBC_ANGLE_RESOLUTION,
                                      gentle_curvature * advance)

  offset_curvature = 2.0 * model_offset / max(offset_horizon, 1e-3) ** 2
  angle_curvature = model_angle / max(angle_horizon, 1e-3)
  return FordModelPose(model_offset + feedback_offset, model_angle + feedback_angle, offset_horizon,
                       max(abs(offset_curvature), abs(angle_curvature)), model_angle)


def _encode_pose(pose: FordModelPose, pose_share: float, curvature: float) -> FordPath:
  path_offset = pose_share * pose.path_offset
  path_angle = pose_share * pose.path_angle
  if abs(path_offset) < 0.5 * DBC_OFFSET_RESOLUTION:
    path_offset = 0.0
  if abs(path_angle) < 0.5 * DBC_ANGLE_RESOLUTION:
    path_angle = 0.0
  limited_path_angle = float(np.clip(path_angle, *DBC_ANGLE))
  path_offset += (path_angle - limited_path_angle) * pose.offset_horizon
  return FordPath(
    valid=True,
    path_offset=float(np.clip(path_offset, *DBC_OFFSET)),
    path_angle=limited_path_angle,
    curvature=float(np.clip(curvature, *DBC_CURVATURE)),
    curvature_rate=0.0,
  )


def _encode_path(path: tuple[list[float], list[float], list[float], list[float]], desired_curvature: float,
                 current_curvature: float, curvature_delta: float, v_ego: float) -> FordPath:
  pose = _model_pose(path, current_curvature, curvature_delta, v_ego)
  pose_share = _blend_share(max(pose.curvature_demand, abs(desired_curvature)))

  # Match upstream's C2-only normal driving, then continuously transfer the
  # command to the model pose for larger maneuvers. An opposing/finished model
  # path must unload sticky C2 and retain the fast pose needed to unwind it.
  c2_opposes_path = desired_curvature != 0.0 and desired_curvature * pose.forward_angle <= 0.0
  if c2_opposes_path:
    pose_share = 1.0
    curvature = 0.0
  else:
    curvature = desired_curvature * (1.0 - pose_share)

  return _encode_pose(pose, pose_share, curvature)


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


def _pscm_slew(value: float, target: float, rate: float, ticks: int) -> float:
  step = rate * _PSCM_DT * ticks
  return float(np.clip(target, value - step, value + step))


def _pscm_speed_gain(v_ego: float) -> float:
  return float(np.interp(max(v_ego, 0.0) * 3.6, _PSCM_SPEED_KPH, _PSCM_SPEED_GAIN))


def _wire_path(path: FordPath) -> FordPath:
  return FordPath(
    valid=path.valid,
    path_offset=round(path.path_offset / DBC_OFFSET_RESOLUTION) * DBC_OFFSET_RESOLUTION,
    path_angle=round(path.path_angle / DBC_ANGLE_RESOLUTION) * DBC_ANGLE_RESOLUTION,
    curvature=round(path.curvature / DBC_CURVATURE_RESOLUTION) * DBC_CURVATURE_RESOLUTION,
    curvature_rate=round(path.curvature_rate / DBC_CURVATURE_RATE_RESOLUTION) * DBC_CURVATURE_RATE_RESOLUTION,
  )


def _pscm_contributions(state: FordPscmState, v_ego: float) -> tuple[float, float, float]:
  gain = _pscm_speed_gain(v_ego)
  return (
    float(np.clip(0.5 * gain * state.path_offset, -0.5 * gain, 0.5 * gain)),
    float(np.clip(10.0 * gain * state.path_angle, -0.349609375 * gain, 0.349609375 * gain)),
    float(np.clip(0.30078125 * gain * state.curvature * v_ego ** 2, -0.5 * gain, 0.5 * gain)),
  )


class FordPscmObserver:
  """Mirror the firmware's held-command coefficient states at its 250 Hz step."""

  def __init__(self):
    self.state = FordPscmState()
    self.command = FordPath(valid=True)
    self._phase = 0.0

  def reset(self) -> None:
    self.state = FordPscmState()
    self.command = FordPath(valid=True)
    self._phase = 0.0

  def advance(self, elapsed: float) -> None:
    self._phase += max(elapsed, 0.0)
    ticks = int((self._phase + 1e-12) / _PSCM_DT)
    self._phase -= ticks * _PSCM_DT
    if ticks == 0:
      return
    self.state = FordPscmState(
      _pscm_slew(self.state.path_offset, self.command.path_offset, _PSCM_C0_RATE, ticks),
      _pscm_slew(self.state.path_angle, self.command.path_angle, _PSCM_C1_RATE, ticks),
      _pscm_slew(self.state.curvature, self.command.curvature + 10.0 * self.command.curvature_rate,
                  _PSCM_C2_RATE, ticks),
    )

  def set_command(self, command: FordPath) -> None:
    self.command = _wire_path(command)


class FordPscmObserverPathController:
  """Compensate model-path commands for the PSCM coefficient state it still carries."""

  def __init__(self, dt: float = 0.01):
    self.dt = dt
    self._last_path = FordPath(valid=True)
    self._curvature_history = deque(maxlen=max(round(_POSE_PREDICTION_TIME / dt) + 1, 2))
    self.observer = FordPscmObserver()
    self._sent_c2 = 0.0

  def _reset(self) -> None:
    self._last_path = FordPath(valid=True)
    self._curvature_history.clear()
    self.observer.reset()
    self._sent_c2 = 0.0

  def _command_for_state(self, target: FordPath, v_ego: float) -> FordPath:
    # The target describes the desired fully-settled PSCM contribution. C0 keeps
    # the remaining C1-saturated residual. C1 supplies the primary contribution
    # that the known slow C2 state does not yet provide, without a guessed gain.
    target_state = FordPscmState(target.path_offset, target.path_angle, target.curvature)
    target_contribution = sum(_pscm_contributions(target_state, v_ego))
    _, _, observed_c2 = _pscm_contributions(self.observer.state, v_ego)
    gain = _pscm_speed_gain(v_ego)
    required_fast = target_contribution - observed_c2
    c1_contribution = float(np.clip(required_fast, -0.349609375 * gain, 0.349609375 * gain))
    c0_contribution = required_fast - c1_contribution
    path_offset = c0_contribution / (0.5 * gain) if gain > 0.0 else 0.0
    path_angle = c1_contribution / (10.0 * gain) if gain > 0.0 else 0.0
    return FordPath(
      valid=True,
      path_offset=float(np.clip(path_offset, -_PSCM_C0_EFFECTIVE_LIMIT, _PSCM_C0_EFFECTIVE_LIMIT)),
      path_angle=float(np.clip(path_angle, -_PSCM_C1_EFFECTIVE_LIMIT, _PSCM_C1_EFFECTIVE_LIMIT)),
      curvature=target.curvature,
      curvature_rate=target.curvature_rate,
    )

  def _limit(self, target: FordPath, v_ego_raw: float) -> FordPath:
    path_offset = float(np.clip(target.path_offset,
                                self._last_path.path_offset - _PATH_OFFSET_RATE * self.dt,
                                self._last_path.path_offset + _PATH_OFFSET_RATE * self.dt))
    path_angle = float(np.clip(target.path_angle,
                               self._last_path.path_angle - _PATH_ANGLE_RATE * self.dt,
                               self._last_path.path_angle + _PATH_ANGLE_RATE * self.dt))
    curvature = CarControllerParams.CURVATURE_LIMITS.apply_limits(
      target.curvature, self._sent_c2, v_ego_raw, 0.0, True, CarControllerParams.LMC2_STEP,
    )
    self._sent_c2 = curvature
    self._last_path = FordPath(True, path_offset, path_angle, curvature, target.curvature_rate)
    self.observer.set_command(self._last_path)
    return self._last_path

  def update(self, model, desired_curvature: float, *, current_curvature: float = 0.0,
             v_ego: float = 0.0, v_ego_raw: float = 0.0, active: bool = True) -> FordPath:
    if not active:
      self._reset()
      return FordPath()

    self.observer.advance(self.dt)
    current_curvature = _finite(current_curvature)
    self._curvature_history.append(current_curvature)
    curvature_delta = (current_curvature - self._curvature_history[0]
                       if len(self._curvature_history) == self._curvature_history.maxlen else 0.0)
    path = _model_path(model) if model is not None else None
    if path is None:
      target = FordPath(valid=True)
    else:
      target = _encode_path(path, _finite(desired_curvature), current_curvature, curvature_delta,
                            max(_finite(v_ego), 0.0))
    v_ego_raw = max(_finite(v_ego_raw), 0.0)
    command = self._command_for_state(target, v_ego_raw)
    return self._limit(command, v_ego_raw)
