"""Experimental Ford C2-free controller using one shared model-path point.

The one-second preview and seven-metre minimum are engineering choices,
not identified Ford reference points or PSCM calibration.
"""
import math
import struct

import numpy as np

from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, _model_path


MIN_STATION_M = 7.0
PREVIEW_TIME_S = 1.0
CALIBRATION_APPROVED = False


def _packed(value, resolution, offset):
  """Mirror Float32 carControlSP and sign-reversed CANPacker rounding."""
  value = struct.unpack("f", struct.pack("f", value))[0]
  return -(math.floor((-value - offset) / resolution + 0.5) * resolution + offset)


def _finite(*values):
  try:
    return all(math.isfinite(value) for value in values)
  except (TypeError, ValueError, OverflowError):
    return False


def encode_model_action(model, desired_curvature, speed):
  """Sample model lateral position and heading at the same arc station.

  Use the model's distance at one second, with a seven-metre minimum and an
  endpoint hold. Selected curvature remains a health/diagnostic input; it does
  not reconstruct heading or rotate the model geometry in this experiment.
  """
  if not _finite(desired_curvature, speed) or not .3 <= speed <= 55 or abs(desired_curvature) > 1:
    return FordPath()
  try:
    path = _model_path(model)
    times = [float(t) for t in model.position.t]
    heading_times = [float(t) for t in model.orientation.t]
  except (AttributeError, TypeError, ValueError, OverflowError):
    return FordPath()
  if path is None or not all(_finite(*values) for values in path):
    return FordPath()
  station, _, lateral, heading = path
  if (len(times) != len(station) or not times or times[0] != 0. or times != heading_times or
      not _finite(*times) or any(b <= a for a, b in zip(times, times[1:], strict=False))):
    return FordPath()
  sample_station = min(station[-1], max(MIN_STATION_M, float(np.interp(PREVIEW_TIME_S, times, station))))
  c0 = float(np.interp(sample_station, station, lateral))
  c1 = float(np.interp(sample_station, station, heading))
  return FordPath(True, c0, c1, 0., 0.) if _finite(c0, c1) else FordPath()


class ModelActionController:
  """Only two states: independently slewed C0/C1 model-point requests."""
  __slots__ = ('c0', 'c1')

  def __init__(self):
    self.reset()

  def reset(self):
    self.c0 = self.c1 = 0.

  def update(self, model, desired_curvature, *, speed, dt, yaw_rate=0., active=True, valid=True):
    # Raw Ford yaw remains an input-health check, not a pose measurement.
    if not active or not valid or not _finite(dt, yaw_rate) or not .002 <= dt <= .1 or abs(yaw_rate) > 3:
      self.reset()
      return FordPath()
    target = encode_model_action(model, desired_curvature, speed)
    if not target.valid:
      self.reset()
      return FordPath()
    c0 = float(np.clip(target.path_offset, -5.11, 5.11))
    c1 = float(np.clip(target.path_angle, -.5, .5))
    self.c0 += float(np.clip(c0-self.c0, -4.*dt, 4.*dt))
    self.c1 += float(np.clip(c1-self.c1, -.5*dt, .5*dt))
    return FordPath(True, _packed(self.c0, .01, -5.12), _packed(self.c1, .0005, -.5), 0., 0.)


class FordModelActionController:
  """Freshness, engagement and reference checks for model-point tracking.

  Scalar-only maneuver references cannot supply this controller's model pose.
  Reject them explicitly rather than silently following a different reference.
  Measured yaw checks input health only; it never modifies valid geometry.
  """
  def __init__(self):
    self.core = ModelActionController()
    self.reset()

  def reset(self, status='inactive'):
    self.core.reset()
    self.last_time = self.last_measurement_time = self.last_model_time = None
    self.diagnostics = {'status': status, 'hypothesis': 'model-pose-one-second-v7',
                        'calibration_approved': CALIBRATION_APPROVED, 'command': (0., 0., 0., 0.)}

  def update(self, model, desired_curvature, *, yaw_rate, speed, now, measurement_time, model_time, reference_time,
             active, valid=True, reference_source="modelV2"):
    reason = None
    if not active:
      reason = 'inactive'
    elif reference_source != 'modelV2':
      reason = 'unsupported_reference'
    elif not valid:
      reason = 'invalid_service'
    elif not _finite(desired_curvature, yaw_rate, speed, now, measurement_time, model_time, reference_time):
      reason = 'nonfinite'
    elif not all(-.005 <= now - timestamp <= .15 for timestamp in (measurement_time, model_time, reference_time)):
      reason = 'stale_input'
    elif not .3 <= speed <= 55 or abs(yaw_rate) > 3 or abs(desired_curvature) > 1:
      reason = 'input_range'
    if reason is not None:
      self.reset(reason)
      return FordPath()

    dt = .01 if self.last_time is None else now - self.last_time
    if not .002 <= dt <= .1 or (self.last_measurement_time is not None and measurement_time < self.last_measurement_time) or (
      self.last_model_time is not None and model_time < self.last_model_time
    ):
      self.reset('timing_reset')
      return FordPath()
    command = self.core.update(model, desired_curvature, speed=speed, dt=dt, yaw_rate=yaw_rate)
    if not command.valid:
      self.reset('invalid_path')
      return command
    self.last_time, self.last_measurement_time, self.last_model_time = now, measurement_time, model_time
    self.diagnostics = {'status': 'active', 'hypothesis': 'model-pose-one-second-v7',
                        'calibration_approved': CALIBRATION_APPROVED, 'desired_curvature': desired_curvature,
                        'yaw_rate': yaw_rate, 'pose_source': 'model',
                        'preview_time_s': PREVIEW_TIME_S, 'minimum_station_m': MIN_STATION_M,
                        'model_age': now - model_time, 'measurement_age': now - measurement_time, 'reference_age': now - reference_time,
                        'dt': dt, 'offset_request': self.core.c0, 'heading_request': self.core.c1,
                        'command': (command.path_offset, command.path_angle, 0., 0.)}
    return command


def select_model_action_controller(CP, enabled, previous_controller):
  """The separate default-off toggle takes priority on the CAN FD Lightning."""
  compatible = CP.brand == 'ford' and CP.flags & FordFlags.CANFD and CP.carFingerprint == 'FORD_F_150_LIGHTNING_MK1'
  if enabled and compatible:
    return FordModelActionController()
  return previous_controller
