#!/usr/bin/env python3
"""Offline evaluation of Ford's native four-field path polynomial.

The experiment deliberately does not alter the live controller. It rebases the
model path into the vehicle pose expected at actuation time, fits one cubic over
the remaining short path, and converts the cubic into the LMC2 C0/C1/C2/C3
signals. A first-order C2 response envelope is included to expose commands that
would look good only if the PSCM curvature channel were instantaneous.
"""

import argparse
from collections import defaultdict
from dataclasses import dataclass
import glob
import math
from pathlib import Path

import numpy as np

from openpilot.tools.lib.logreader import LogReader


DBC_OFFSET = (-5.12, 5.11)
DBC_ANGLE = (-0.5, 0.5235)
DBC_CURVATURE = (-0.02, 0.02)
DBC_CURVATURE_RATE = (-0.001024, 0.001023)
MAX_LATERAL_ACCEL = 3.0 + 9.81 * 0.06
MAX_LATERAL_JERK = 3.0 + 9.81 * 0.06
@dataclass(frozen=True)
class ModelPath:
  x: np.ndarray
  y: np.ndarray
  heading: np.ndarray
  distance: np.ndarray


@dataclass(frozen=True)
class Sample:
  route: str
  time: float
  speed: float
  curvature: float
  steering_pressed: bool
  path: ModelPath
  sent_c0: float
  sent_c1: float
  sent_c2: float
  sent_c3: float
@dataclass(frozen=True)
class NativePath:
  c0: float
  c1: float
  c2: float
  c3: float
  fit_rmse: float
  path_rms: float


def _model_path(model) -> ModelPath | None:
  try:
    x = np.asarray(model.position.x, dtype=float)
    y = np.asarray(model.position.y, dtype=float)
    heading = np.unwrap(np.asarray(model.orientation.z, dtype=float))
  except (AttributeError, TypeError, ValueError):
    return None
  if len(x) < 4 or len(x) != len(y) or len(x) != len(heading):
    return None
  if not np.isfinite(np.concatenate((x, y, heading))).all():
    return None
  distance = np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))))
  unique_distance, unique = np.unique(distance, return_index=True)
  if len(unique_distance) < 4 or unique_distance[-1] <= 0.0:
    return None
  return ModelPath(x[unique], y[unique], heading[unique], unique_distance)


def _arc_pose(distance: float, curvature: float) -> tuple[float, float, float]:
  heading = curvature * distance
  if abs(curvature) < 1e-9:
    return distance, 0.0, 0.0
  return math.sin(heading) / curvature, (1.0 - math.cos(heading)) / curvature, heading


def _relative_points(path: ModelPath, vehicle_pose: tuple[float, float, float], start: float,
                     horizon: float, count: int = 25) -> tuple[np.ndarray, np.ndarray]:
  sample_distance = np.linspace(start, min(start + horizon, path.distance[-1]), count)
  desired_x = np.interp(sample_distance, path.distance, path.x)
  desired_y = np.interp(sample_distance, path.distance, path.y)
  vehicle_x, vehicle_y, vehicle_heading = vehicle_pose
  dx = desired_x - vehicle_x
  dy = desired_y - vehicle_y
  cosine = math.cos(vehicle_heading)
  sine = math.sin(vehicle_heading)
  return cosine * dx + sine * dy, -sine * dx + cosine * dy


def _fit_points(path: ModelPath, speed: float, current_curvature: float, delay: float,
                horizon: float) -> tuple[np.ndarray, np.ndarray] | None:
  advance = min(max(speed, 0.0) * delay, path.distance[-1])
  available = min(horizon, path.distance[-1] - advance)
  if available <= 0.25:
    return None
  x, y = _relative_points(path, _arc_pose(advance, current_curvature), advance, available)
  forward = (x >= -0.25) & (x <= horizon)
  x = x[forward]
  y = y[forward]
  if len(x) < 4 or np.ptp(x) <= 0.25:
    return None
  return x, y


def _wire_coefficients(c0: float, c1: float, c2: float, c3: float) -> tuple[float, float, float, float]:
  slope = math.tan(c1)
  slope_norm = 1.0 + slope ** 2
  a2 = 0.5 * c2 * slope_norm ** 1.5
  a3 = (c3 + 12.0 * slope * a2 ** 2 / slope_norm ** 3) * slope_norm ** 2 / 6.0
  return c0, slope, a2, a3


def _wire_rmse(command: tuple[float, float, float, float], x: np.ndarray, y: np.ndarray) -> float:
  a0, a1, a2, a3 = _wire_coefficients(*command)
  reconstructed = a0 + a1 * x + a2 * x ** 2 + a3 * x ** 3
  return float(np.sqrt(np.mean((reconstructed - y) ** 2)))


def fit_native_path(path: ModelPath, speed: float, current_curvature: float, *, delay: float,
                    horizon: float) -> NativePath:
  """Fit the delay-aligned path and return physical LMC2 fields.

  C2 and C3 are curvature and curvature rate at the vehicle-frame origin, not
  the raw quadratic and cubic polynomial coefficients.
  """
  points = _fit_points(path, speed, current_curvature, delay, horizon)
  if points is None:
    return NativePath(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
  x, y = points

  # Scaling x before the least-squares solve keeps tight-turn fits well
  # conditioned while preserving an ordinary cubic in vehicle coordinates.
  scale = max(float(np.max(np.abs(x))), 1.0)
  normalized_x = x / scale
  design = np.column_stack((np.ones(len(x)), normalized_x, normalized_x ** 2, normalized_x ** 3))
  scaled, *_ = np.linalg.lstsq(design, y, rcond=None)
  a0, a1, a2, a3 = (float(scaled[index] / scale ** index) for index in range(4))
  slope = a1
  slope_norm = 1.0 + slope ** 2
  curvature = 2.0 * a2 / slope_norm ** 1.5
  curvature_rate = 6.0 * a3 / slope_norm ** 2 - 12.0 * slope * a2 ** 2 / slope_norm ** 3
  command = (float(np.clip(a0, *DBC_OFFSET)),
             float(np.clip(math.atan(slope), *DBC_ANGLE)),
             float(np.clip(curvature, *DBC_CURVATURE)),
             float(np.clip(curvature_rate, *DBC_CURVATURE_RATE)))
  return NativePath(
    *command,
    _wire_rmse(command, x, y),
    float(np.sqrt(np.mean(y ** 2))),
  )


def fit_c2_aware_path(path: ModelPath, speed: float, current_curvature: float, *, delay: float,
                      horizon: float, target_c2: float, effective_c2: float,
                      use_c3: bool = True) -> NativePath:
  """Fit fast fields around the C2 curvature the PSCM is expected to realize."""
  points = _fit_points(path, speed, current_curvature, delay, horizon)
  if points is None:
    return NativePath(0.0, 0.0, target_c2, 0.0, 0.0, 0.0)
  x, y = points

  slope = 0.0
  a0 = a1 = a3 = 0.0
  for _ in range(3):
    a2 = 0.5 * effective_c2 * (1.0 + slope ** 2) ** 1.5
    design = np.column_stack((np.ones(len(x)), x, x ** 3))
    (a0, a1, a3), *_ = np.linalg.lstsq(design, y - a2 * x ** 2, rcond=None)
    slope = float(a1)

  slope_norm = 1.0 + slope ** 2
  c3 = 6.0 * float(a3) / slope_norm ** 2 - 12.0 * slope * a2 ** 2 / slope_norm ** 3
  c3 = float(np.clip(c3, *DBC_CURVATURE_RATE)) if use_c3 else 0.0
  # Once C2 and C3 are fixed to what the hardware can realize, refit C0/C1 so
  # their fast feedback preserves as much of the same path as possible.
  _, _, fixed_a2, fixed_a3 = _wire_coefficients(0.0, math.atan(slope), effective_c2, c3)
  (a0, a1), *_ = np.linalg.lstsq(np.column_stack((np.ones(len(x)), x)),
                                  y - fixed_a2 * x ** 2 - fixed_a3 * x ** 3, rcond=None)
  c0 = float(np.clip(a0, *DBC_OFFSET))
  c1 = float(np.clip(math.atan(float(a1)), *DBC_ANGLE))
  effective_command = (c0, c1, effective_c2, c3)
  return NativePath(c0, c1, target_c2, c3, _wire_rmse(effective_command, x, y),
                    float(np.sqrt(np.mean(y ** 2))))


def _route(path: str) -> str:
  return Path(path).name.split("--", 1)[0]


def load_samples(paths: list[str], stride: int = 2) -> list[Sample]:
  grouped: dict[str, list[str]] = defaultdict(list)
  for path in paths:
    grouped[_route(path)].append(path)

  samples = []
  for route, route_paths in sorted(grouped.items()):
    events = []
    for path in sorted(route_paths):
      events.extend(LogReader(path))
    events.sort(key=lambda event: event.logMonoTime)
    if not events:
      continue
    start_time = events[0].logMonoTime
    model_path = None
    curvature = 0.0
    lat_active = path_valid = False
    sent = (0.0, 0.0, 0.0, 0.0)
    car_state_count = 0
    for event in events:
      which = event.which()
      if which == "modelV2":
        model_path = _model_path(event.modelV2)
      elif which == "controlsState":
        curvature = float(event.controlsState.curvature)
      elif which == "carControl":
        lat_active = bool(event.carControl.latActive)
      elif which == "carControlSP":
        command = event.carControlSP.fordLateralPath
        path_valid = bool(command.valid)
        sent = (float(command.pathOffset), float(command.pathAngle),
                float(command.curvature), float(command.curvatureRate))
      elif which == "carState" and lat_active and path_valid and model_path is not None:
        car_state_count += 1
        if car_state_count % stride:
          continue
        samples.append(Sample(
          route, (event.logMonoTime - start_time) * 1e-9, float(event.carState.vEgo), curvature,
          bool(event.carState.steeringPressed), model_path, *sent,
        ))
  return samples


def _percentile(values: np.ndarray, percentile: float, mask: np.ndarray | None = None) -> float:
  selected = values if mask is None else values[mask]
  return float(np.percentile(np.abs(selected), percentile)) if len(selected) else math.nan


def _route_rate(samples: list[Sample], values: np.ndarray) -> np.ndarray:
  rate = np.zeros(len(values))
  for index in range(1, len(values)):
    dt = samples[index].time - samples[index - 1].time
    if samples[index].route == samples[index - 1].route and 0.005 <= dt <= 0.2:
      rate[index] = (values[index] - values[index - 1]) / dt
  return rate


def _c2_response(samples: list[Sample], target: np.ndarray, tau_load: float,
                 tau_unload: float) -> np.ndarray:
  effective = np.zeros(len(target))
  previous_route = None
  previous_time = 0.0
  state = 0.0
  for index, sample in enumerate(samples):
    if sample.route != previous_route:
      state = 0.0
      previous_time = sample.time
    dt = float(np.clip(sample.time - previous_time, 0.005, 0.2))
    loading = target[index] * state >= 0.0 and abs(target[index]) > abs(state)
    tau = tau_load if loading else tau_unload
    state += (1.0 - math.exp(-dt / tau)) * (target[index] - state)
    effective[index] = state
    previous_route, previous_time = sample.route, sample.time
  return effective


def _limit_c2_command(samples: list[Sample], target: np.ndarray) -> np.ndarray:
  """Mirror the CAN-FD Ford curvature acceleration/jerk limiter."""
  limited = np.zeros(len(target))
  previous_route = None
  previous_time = 0.0
  previous = 0.0
  for index, sample in enumerate(samples):
    if sample.route != previous_route:
      previous = 0.0
      previous_time = sample.time
    dt = float(np.clip(sample.time - previous_time, 0.005, 0.2))
    speed = max(sample.speed, 1.0)
    value = float(np.clip(target[index], -MAX_LATERAL_ACCEL / speed ** 2,
                          MAX_LATERAL_ACCEL / speed ** 2))
    step = MAX_LATERAL_JERK / speed ** 2 * dt
    value = float(np.clip(value, previous - step, previous + step))
    limited[index] = float(np.clip(value, *DBC_CURVATURE))
    previous = limited[index]
    previous_route, previous_time = sample.route, sample.time
  return limited


def _limit_fast_fields(samples: list[Sample], c0_target: np.ndarray,
                       c1_target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
  c0 = np.zeros(len(samples))
  c1 = np.zeros(len(samples))
  previous_route = None
  previous_time = 0.0
  previous_c0 = previous_c1 = 0.0
  for index, sample in enumerate(samples):
    if sample.route != previous_route:
      previous_c0 = previous_c1 = 0.0
      previous_time = sample.time
    dt = float(np.clip(sample.time - previous_time, 0.005, 0.2))
    c0[index] = np.clip(c0_target[index], previous_c0 - 4.0 * dt, previous_c0 + 4.0 * dt)
    c1[index] = np.clip(c1_target[index], previous_c1 - 1.0 * dt, previous_c1 + 1.0 * dt)
    previous_c0, previous_c1 = c0[index], c1[index]
    previous_route, previous_time = sample.route, sample.time
  return c0, c1


def evaluate(samples: list[Sample], *, delay: float, horizon: float,
             tau_load: float, tau_unload: float, horizon_time: float = 0.0,
             assumed_tau_load: float | None = None, assumed_tau_unload: float | None = None,
             use_c3: bool = True, c2_limit: float = DBC_CURVATURE[1]) -> dict[str, float]:
  horizons = np.asarray([float(np.clip(sample.speed * horizon_time, 1.0, horizon))
                         if horizon_time > 0.0 else horizon for sample in samples])
  commands = [fit_native_path(sample.path, sample.speed, sample.curvature,
                              delay=delay, horizon=sample_horizon)
              for sample, sample_horizon in zip(samples, horizons, strict=True)]
  c0 = np.asarray([command.c0 for command in commands])
  c1 = np.asarray([command.c1 for command in commands])
  raw_c2 = np.asarray([command.c2 for command in commands])
  c2 = np.clip(raw_c2, -c2_limit, c2_limit)
  c3 = np.asarray([command.c3 for command in commands])
  fit_rmse = np.asarray([command.fit_rmse for command in commands])
  path_rms = np.asarray([command.path_rms for command in commands])
  transmitted_c2 = _limit_c2_command(samples, c2)
  effective_c2 = _c2_response(samples, transmitted_c2, tau_load, tau_unload)
  estimated_c2 = _c2_response(samples, transmitted_c2,
                              tau_load if assumed_tau_load is None else assumed_tau_load,
                              tau_unload if assumed_tau_unload is None else assumed_tau_unload)
  compensated = [fit_c2_aware_path(sample.path, sample.speed, sample.curvature,
                                   delay=delay, horizon=sample_horizon, target_c2=target,
                                   effective_c2=estimated, use_c3=use_c3)
                 for sample, sample_horizon, target, estimated in
                 zip(samples, horizons, c2, estimated_c2, strict=True)]
  compensated_c0 = np.asarray([command.c0 for command in compensated])
  compensated_c1 = np.asarray([command.c1 for command in compensated])
  compensated_c3 = np.asarray([command.c3 for command in compensated])
  limited_c0, limited_c1 = _limit_fast_fields(samples, compensated_c0, compensated_c1)
  estimated_compensated_rmse = np.asarray([command.fit_rmse for command in compensated])
  compensated_rmse = []
  for sample, sample_horizon, command, effective in zip(samples, horizons, compensated, effective_c2, strict=True):
    points = _fit_points(sample.path, sample.speed, sample.curvature, delay, sample_horizon)
    compensated_rmse.append(0.0 if points is None else _wire_rmse(
      (command.c0, command.c1, effective, command.c3), *points))
  compensated_rmse = np.asarray(compensated_rmse)
  limited_compensated_rmse = []
  for sample, sample_horizon, c0_value, c1_value, c3_value, effective in \
      zip(samples, horizons, limited_c0, limited_c1, compensated_c3, effective_c2, strict=True):
    points = _fit_points(sample.path, sample.speed, sample.curvature, delay, sample_horizon)
    limited_compensated_rmse.append(0.0 if points is None else _wire_rmse(
      (c0_value, c1_value, effective, c3_value), *points))
  limited_compensated_rmse = np.asarray(limited_compensated_rmse)
  missing_c2 = transmitted_c2 - effective_c2
  # Compare channels by their lateral contribution at the fit horizon. This
  # includes C3: treating it as zero would incorrectly blame C0/C1 for a
  # curvature transition the native polynomial assigns to curvature rate.
  fast = (2.0 * compensated_c0 / horizons ** 2 +
          2.0 * np.tan(compensated_c1) / horizons +
          compensated_c3 * horizons / 3.0)
  lagging = np.abs(missing_c2) > 0.0005
  unloading = lagging & (np.abs(c2) < 0.75 * np.abs(effective_c2))
  pressed = np.asarray([sample.steering_pressed for sample in samples])
  speed = np.asarray([sample.speed for sample in samples])
  sent_c2 = np.asarray([sample.sent_c2 for sample in samples])
  sent_transmitted_c2 = _limit_c2_command(samples, sent_c2)
  sent_effective_c2 = _c2_response(samples, sent_transmitted_c2, tau_load, tau_unload)
  sent_lpf_rmse = []
  for sample, sample_horizon, effective in zip(samples, horizons, sent_effective_c2, strict=True):
    points = _fit_points(sample.path, sample.speed, sample.curvature, delay, sample_horizon)
    sent_lpf_rmse.append(0.0 if points is None else _wire_rmse(
      (sample.sent_c0, sample.sent_c1, effective, sample.sent_c3), *points))
  sent_lpf_rmse = np.asarray(sent_lpf_rmse)
  raw_c2_rate = _route_rate(samples, c2)
  c2_rate = _route_rate(samples, transmitted_c2)
  sent_c2_rate = _route_rate(samples, sent_c2)
  compensated_c0_rate = _route_rate(samples, compensated_c0)
  compensated_c1_rate = _route_rate(samples, compensated_c1)
  compensated_c3_rate = _route_rate(samples, compensated_c3)
  normalized_fit = np.divide(fit_rmse, path_rms, out=np.zeros_like(fit_rmse), where=path_rms > 1e-4)
  return {
    "samples": float(len(samples)),
    "delay": delay,
    "horizon": horizon,
    "horizon_time": horizon_time,
    "assumed_tau_load": tau_load if assumed_tau_load is None else assumed_tau_load,
    "assumed_tau_unload": tau_unload if assumed_tau_unload is None else assumed_tau_unload,
    "use_c3": float(use_c3),
    "c2_limit": c2_limit,
    "actual_horizon_p50": _percentile(horizons, 50),
    "actual_horizon_p95": _percentile(horizons, 95),
    "fit_rmse_p50": _percentile(fit_rmse, 50),
    "fit_rmse_p95": _percentile(fit_rmse, 95),
    "normalized_fit_p95": _percentile(normalized_fit, 95),
    "c2_aware_rmse_p50": _percentile(compensated_rmse, 50),
    "c2_aware_rmse_p95": _percentile(compensated_rmse, 95),
    "c2_aware_estimated_rmse_p95": _percentile(estimated_compensated_rmse, 95),
    "c2_aware_limited_rmse_p95": _percentile(limited_compensated_rmse, 95),
    "sent_lpf_rmse_p50": _percentile(sent_lpf_rmse, 50),
    "sent_lpf_rmse_p95": _percentile(sent_lpf_rmse, 95),
    "c0_p95": _percentile(c0, 95),
    "c1_p95": _percentile(c1, 95),
    "c2_p95": _percentile(c2, 95),
    "c3_p95": _percentile(c3, 95),
    "c0_clip_rate": float(np.mean((c0 <= DBC_OFFSET[0]) | (c0 >= DBC_OFFSET[1]))),
    "c1_clip_rate": float(np.mean((c1 <= DBC_ANGLE[0]) | (c1 >= DBC_ANGLE[1]))),
    "c2_clip_rate": float(np.mean((c2 <= DBC_CURVATURE[0]) | (c2 >= DBC_CURVATURE[1]))),
    "c3_clip_rate": float(np.mean((c3 <= DBC_CURVATURE_RATE[0]) | (c3 >= DBC_CURVATURE_RATE[1]))),
    "c2_aware_c0_p95": _percentile(compensated_c0, 95),
    "c2_aware_c1_p95": _percentile(compensated_c1, 95),
    "c2_aware_c3_p95": _percentile(compensated_c3, 95),
    "c2_aware_c0_rate_p95": _percentile(compensated_c0_rate, 95),
    "c2_aware_c1_rate_p95": _percentile(compensated_c1_rate, 95),
    "c2_aware_c0_rate_limit_rate": float(np.mean(np.abs(compensated_c0_rate) > 4.0)),
    "c2_aware_c1_rate_limit_rate": float(np.mean(np.abs(compensated_c1_rate) > 1.0)),
    "c2_aware_c3_rate_p95": _percentile(compensated_c3_rate, 95),
    "raw_c2_rate_p95": _percentile(raw_c2_rate, 95),
    "c2_rate_p95": _percentile(c2_rate, 95),
    "sent_c2_rate_p95": _percentile(sent_c2_rate, 95),
    "c2_lag_p95": _percentile(missing_c2, 95),
    "lag_samples": float(np.count_nonzero(lagging)),
    "lag_fast_support_rate": float(np.mean(fast[lagging] * missing_c2[lagging] > 0.0)) if np.any(lagging) else math.nan,
    "lag_fast_coverage_p50": _percentile(np.divide(fast, missing_c2, out=np.zeros_like(fast),
                                                    where=np.abs(missing_c2) > 1e-6), 50, lagging),
    "unload_samples": float(np.count_nonzero(unloading)),
    "unload_fast_counter_rate": float(np.mean(fast[unloading] * effective_c2[unloading] < 0.0)) if np.any(unloading) else math.nan,
    "unload_residual_c2_p95": _percentile(effective_c2 - c2, 95, unloading),
    "pressed_c0_p95": _percentile(c0, 95, pressed),
    "pressed_c1_p95": _percentile(c1, 95, pressed),
    "low_speed_fit_p95": _percentile(fit_rmse, 95, speed < 5.0),
    "road_speed_fit_p95": _percentile(fit_rmse, 95, speed >= 15.0),
  }


def _expand(patterns: list[str]) -> list[str]:
  return sorted({path for pattern in patterns for path in glob.glob(pattern)})


def _self_test() -> None:
  distance = np.linspace(0.0, 20.0, 81)
  coefficients = (0.2, 0.03, 0.004, -0.00005)
  y = sum(coefficient * distance ** power for power, coefficient in enumerate(coefficients))
  slope = coefficients[1] + 2.0 * coefficients[2] * distance + 3.0 * coefficients[3] * distance ** 2
  heading = np.arctan(slope)
  path = ModelPath(distance, y, heading, np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(distance), np.diff(y))))))
  command = fit_native_path(path, 0.0, 0.0, delay=0.1, horizon=7.0)
  assert abs(command.c0 - coefficients[0]) < 2e-3
  assert abs(command.c1 - math.atan(coefficients[1])) < 2e-3
  expected_c2 = 2.0 * coefficients[2] / (1.0 + coefficients[1] ** 2) ** 1.5
  assert abs(command.c2 - expected_c2) < 2e-4
  assert command.fit_rmse < 1e-4


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--logs", action="append", help="rlog glob", default=[])
  parser.add_argument("--delay", type=float, default=0.1)
  parser.add_argument("--horizon", type=float, action="append")
  parser.add_argument("--time-horizon", type=float, default=0.0,
                      help="if nonzero, use clamp(speed * seconds, 1 m, --horizon)")
  parser.add_argument("--tau-load", type=float, default=0.75)
  parser.add_argument("--tau-unload", type=float, default=1.3)
  parser.add_argument("--assumed-tau-load", type=float)
  parser.add_argument("--assumed-tau-unload", type=float)
  parser.add_argument("--zero-c3", action="store_true")
  parser.add_argument("--c2-limit", type=float, action="append",
                      help="C2 cap to test; defaults to gentle 0.006 and full 0.02")
  parser.add_argument("--self-test", action="store_true")
  args = parser.parse_args()
  if args.self_test:
    _self_test()
  paths = _expand(args.logs)
  if not paths:
    if args.self_test:
      return 0
    parser.error("at least one usable --logs glob is required")
  samples = load_samples(paths)
  if not samples:
    parser.error("logs contain no active Ford path samples")
  print(f"loaded_logs={len(paths)} samples={len(samples)} tau_load={args.tau_load} tau_unload={args.tau_unload}")
  for horizon in args.horizon or [3.5, 5.0, 7.0, 10.0]:
    for c2_limit in args.c2_limit or [0.006, DBC_CURVATURE[1]]:
      result = evaluate(samples, delay=args.delay, horizon=horizon,
                        tau_load=args.tau_load, tau_unload=args.tau_unload,
                        horizon_time=args.time_horizon,
                        assumed_tau_load=args.assumed_tau_load,
                        assumed_tau_unload=args.assumed_tau_unload,
                        use_c3=not args.zero_c3,
                        c2_limit=c2_limit)
      print(" ".join(f"{key}={value:.8g}" for key, value in result.items()))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
