"""C2-free spatial path tracking for the Lightning RL38 PSCM.

The historical Virtual Angle name/key is retained for settings compatibility.
C0/C1 remain path geometry, never a fitted wheel-angle or torque command.
"""
from dataclasses import dataclass
import math
import struct
import numpy as np

from openpilot.selfdrive.controls.lib.ford_path import FordPath, _model_path, _relative_pose, _predicted_pose
from opendbc.car.ford.values import FordFlags


def _packed(value, resolution, offset):
  """Mirror Float32 carControlSP and sign-reversed CANPacker rounding."""
  value = struct.unpack("f", struct.pack("f", value))[0]
  return -(math.floor((-value - offset) / resolution + 0.5) * resolution + offset)


@dataclass(frozen=True)
class PathTuning:
  filter_time: float = 0.3
  offset_horizon: float = 7.0
  heading_time: float = 1.0
  offset_rate: float = 4.0
  heading_rate: float = 0.5


class PathReference:
  """Retain model geometry in the current ego frame between model messages."""
  def __init__(self, tuning):
    self.tuning = tuning
    self.path = None
    self.model_time = None

  def reset(self):
    self.path = None
    self.model_time = None

  @staticmethod
  def advance(path, distance, curvature):
    stations, x, y, heading = path
    dx, dy, yaw = _predicted_pose(distance, curvature, 0.0)
    cosine, sine = math.cos(yaw), math.sin(yaw)
    return stations - distance, cosine * (x - dx) + sine * (y - dy), -sine * (x - dx) + cosine * (y - dy), heading - yaw

  def update(self, model, *, model_time, now, dt, speed, curvature):
    if self.path is not None:
      self.path = self.advance(self.path, speed * dt, curvature)
    if model_time == self.model_time:
      return self.path
    raw = _model_path(model)
    if raw is None or not all(np.isfinite(a).all() for a in raw):
      self.reset()
      return None
    new = self.advance(tuple(np.array(a) for a in raw), speed * max(now - model_time, 0.0), curvature)
    if self.path is not None:
      # Both paths now describe the same ego frame and traveled arc. Only the
      # model innovation is filtered; measured ego motion is accounted for at
      # every control tick. Never average two unaligned vehicle-frame paths.
      elapsed = model_time - self.model_time
      alpha = elapsed / (self.tuning.filter_time + elapsed)
      old = self.path
      values = [new[0]]
      for index in (1, 2, 3):
        prior = np.interp(new[0], old[0], old[index])
        delta = new[index] - prior
        if index == 3:
          delta = (delta + np.pi) % (2 * np.pi) - np.pi
        values.append(prior + alpha * delta)
      # Do not invent reference history beyond the previous path's coverage.
      outside = (new[0] < old[0][0]) | (new[0] > old[0][-1])
      for index in (1, 2, 3):
        values[index][outside] = new[index][outside]
      new = tuple(values)
    self.path = new
    self.model_time = model_time
    return self.path


class FordVirtualAngleController:
  """Supply spatial path offsets/headings to the PSCM's own controller.

  Measured CAN yaw rate is used only to move the reference between ego frames
  and align its preview with the response interval. No EPS gain is assumed.
  """
  def __init__(self, response_delay=.2, tuning: PathTuning | None = None):
    self.tuning = tuning if tuning is not None else PathTuning()
    if not math.isfinite(response_delay) or not .05 <= response_delay <= .5:
      raise ValueError("response delay must be within 0.05..0.5 seconds")
    if not all(math.isfinite(v) and v >= 0 for v in vars(self.tuning).values()) or min(
      self.tuning.offset_horizon, self.tuning.heading_time, self.tuning.offset_rate, self.tuning.heading_rate,
    ) <= 0:
      raise ValueError("invalid path tuning")
    self.delay = response_delay
    self.reference = PathReference(self.tuning)
    self.reset()

  def reset(self):
    self.reference.reset()
    self.command = FordPath()
    self.last_time = None
    self.last_measurement_time = None
    self.offset_request = self.heading_request = 0.0
    self.diagnostics = {'status': 'inactive', 'hypothesis': 'spatial-path-v2', 'command': (0., 0., 0., 0.)}

  def update(self, model, *, yaw_rate, speed, now, measurement_time, model_time, active, valid=True, steering_pressed=False):
    finite = all(math.isfinite(v) for v in (yaw_rate, speed, now, measurement_time, model_time))
    fresh = finite and -.005 <= now - measurement_time <= .15 and -.005 <= now - model_time <= .15
    if not active or not valid or model is None or not fresh or not .3 <= speed <= 55 or abs(yaw_rate) > 3:
      self.reset()
      self.diagnostics['status'] = 'inactive' if not active else 'invalid_input'
      self.diagnostics['reason'] = ('inactive' if not active else 'invalid_service' if not valid else 'missing_model' if model is None else
                                    'nonfinite' if not finite else 'stale_input' if not fresh else 'speed' if not .3 <= speed <= 55 else 'yaw_rate')
      return self.command
    dt = .01 if self.last_time is None else now - self.last_time
    if not .002 <= dt <= .1 or (self.last_measurement_time is not None and measurement_time < self.last_measurement_time) or (
      self.reference.model_time is not None and model_time < self.reference.model_time
    ):
      self.reset()
      self.diagnostics['status'] = 'timing_reset'
      return self.command
    current_curvature = yaw_rate / speed
    self.last_time = now
    self.last_measurement_time = measurement_time
    path = self.reference.update(model, model_time=model_time, now=now, dt=dt, speed=speed, curvature=current_curvature)
    if path is None or path[0][-1] <= 0:
      self.reset()
      self.diagnostics['status'] = 'invalid_path'
      return self.command
    advance = min(speed * self.delay, path[0][-1])
    offset_horizon = min(self.tuning.offset_horizon, max(path[0][-1] - advance, 0.0))
    heading_horizon = min(max(speed * self.tuning.heading_time, self.tuning.offset_horizon), max(path[0][-1] - advance, 0.0))
    ego = _predicted_pose(advance, current_curvature, 0.)
    offset, _ = _relative_pose(advance + offset_horizon, path, ego)
    _, heading = _relative_pose(advance + heading_horizon, path, ego)
    # Keep the complete lateral/heading error in the predicted ego frame.
    # Subtracting the model's own initial pose would erase centering offsets.
    heading_limited = float(np.clip(heading, -.5, .5))
    offset += (heading - heading_limited) * offset_horizon
    target_offset = float(np.clip(offset, -5.11, 5.11))
    target_heading = heading_limited
    delta_offset = target_offset - self.offset_request
    delta_heading = target_heading - self.heading_request
    scale = min(1., self.tuning.offset_rate * dt / abs(delta_offset) if delta_offset else 1.,
                self.tuning.heading_rate * dt / abs(delta_heading) if delta_heading else 1.)
    self.offset_request += scale * delta_offset
    self.heading_request += scale * delta_heading
    offset = _packed(self.offset_request, .01, -5.12)
    heading = _packed(self.heading_request, .0005, -.5)
    self.command = FordPath(True, offset, heading, 0., 0.)
    self.diagnostics = {'status': 'driver_override' if steering_pressed else 'active', 'hypothesis': 'spatial-path-v2',
                        'offset_target': target_offset, 'heading_target': target_heading, 'slew_scale': scale,
                        'measurement_age': now - measurement_time, 'model_age': now - model_time,
                        'response_delay': self.delay, 'reference_filter_time': self.tuning.filter_time, 'yaw_rate': yaw_rate,
                        'offset_horizon': offset_horizon, 'heading_horizon': heading_horizon,
                        'command': (offset, heading, 0., 0.)}
    return self.command


def select_virtual_angle_controller(CP, enabled, previous_controller):
  # The source route analysis covers only this vehicle/firmware.
  compatible = CP.brand == 'ford' and CP.flags & FordFlags.CANFD and CP.carFingerprint == 'FORD_F_150_LIGHTNING_MK1'
  firmware = compatible and any(str(fw.ecu) == 'eps' and bytes(fw.fwVersion).rstrip(b'\0') == b'RL38-14D003-AA' for fw in CP.carFw)
  if enabled and firmware:
    return FordVirtualAngleController(CP.steerActuatorDelay)
  return previous_controller
