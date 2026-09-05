"""C2-free curvature requests with bounded yaw tracking for the Lightning RL38 PSCM.

The historical Virtual Angle name/key is retained for settings compatibility.
C0/C1 remain path geometry, never a fitted wheel-angle or torque command.
"""
from collections import deque
from dataclasses import dataclass
import math
import struct
import numpy as np

from openpilot.selfdrive.controls.lib.ford_path import FordPath, _model_path, _relative_pose, _predicted_pose
from opendbc.car.ford.values import CarControllerParams, FordFlags


FEEDBACK_MIN_SPEED = 2.0
HEADING_RESOLUTION = .0005


def _packed(value, resolution, offset):
  """Mirror Float32 carControlSP and sign-reversed CANPacker rounding."""
  value = struct.unpack("f", struct.pack("f", value))[0]
  return -(math.floor((-value - offset) / resolution + 0.5) * resolution + offset)


@dataclass(frozen=True)
class PathTuning:
  filter_time: float = 0.3
  offset_horizon: float = 8.0
  heading_horizon: float = 7.0
  heading_time: float = 1.0
  offset_rate: float = 4.0
  heading_rate: float = 0.5
  feedback_gain: float = 1.0


@dataclass(frozen=True)
class PscmStatus:
  timestamp: float
  lateral_state: int
  limit: int
  capability: int
  denied: bool
  valid: bool = True

  def invalid_reason(self, now):
    if not self.valid or not math.isfinite(self.timestamp) or any(v not in (0, 1, 2, 3) for v in (
      self.lateral_state, self.limit, self.capability,
    )):
      return 'invalid_pscm'
    if not -.005 <= now - self.timestamp <= .15:
      return 'stale_pscm'
    if self.denied or self.lateral_state != 2 or self.capability not in (1, 2):
      return 'unavailable_pscm'
    return None


class HeadingFeedback:
  """Bound a heading correction using measured yaw error, not an EPS gain fit.

  The nominal response interval, integration gain and low-speed policy remain
  experimental. A downstream limit report cannot identify motor effort from
  the sign of C1 while C0 and the PSCM's own controller are also acting.
  """
  def __init__(self, delay, tuning):
    self.delay, self.tuning = delay, tuning
    self.reset()

  def reset(self, status='inactive'):
    self.history = deque()
    self.bias = 0.
    self.previous_base = None
    self.last_measurement_time = self.last_pscm_time = None
    self.diagnostics = {'heading_bias': 0., 'feedback_status': status, 'feedback_reference_time': None,
                        'feedback_reference_curvature': None, 'feedback_yaw_error': None}

  def update(self, base, desired, *, yaw_rate, speed, now, measurement_time, dt, previous_command, heading_horizon, driver_override, pscm_status):
    reason = ('missing_pscm' if pscm_status is None else pscm_status.invalid_reason(now))
    if reason is None and self.last_pscm_time is not None and pscm_status.timestamp < self.last_pscm_time:
      reason = 'pscm_timing'
    if reason is None:
      reason = ('driver_override' if driver_override or pscm_status.limit == 3 else 'low_speed' if speed < FEEDBACK_MIN_SPEED else
                'zero_request' if base == 0. else 'disabled' if self.tuning.feedback_gain == 0. else None)
    if reason is not None:
      self.reset(reason)
      return base

    if self.previous_base is not None and base * self.previous_base < 0.:
      self.reset('reversal')
    elif self.previous_base and abs(base) < abs(self.previous_base):
      # Releasing a clipped base, rather than raw curvature, avoids increasing
      # total C1 by shrinking a negative correction while the base stays capped.
      self.bias *= abs(base / self.previous_base)
    self.previous_base = base
    self.last_pscm_time = pscm_status.timestamp
    self.history.append((now, desired))
    while len(self.history) > 2 and self.history[1][0] < now - self.delay - .25:
      self.history.popleft()

    status = 'no_new_measurement'
    reference_time = reference_curvature = yaw_error = None
    if measurement_time != self.last_measurement_time:
      measurement_dt = 0. if self.last_measurement_time is None else measurement_time - self.last_measurement_time
      self.last_measurement_time = measurement_time
      target_time = measurement_time - self.delay
      # Use the command actually held at the historical instant. Interpolating
      # toward a later publication would compare against a different request.
      reference = next((sample for sample in reversed(self.history) if sample[0] <= target_time), None)
      if reference is None:
        status = 'history'
      elif not .002 <= measurement_dt <= .1:
        status = 'measurement_timing'
      else:
        reference_time, reference_curvature = reference
        yaw_error = speed * reference_curvature - yaw_rate
        releasing = reference_curvature * desired <= 0. or (abs(reference_curvature) - abs(desired)) * heading_horizon > HEADING_RESOLUTION
        if releasing:
          status = 'release'
        elif pscm_status.limit >= 2:
          # Freeze all integration: C1 direction is not measured motor effort.
          # Base-driven release still removes stored demand as the action eases.
          status = 'pscm_limit'
        else:
          increment = self.tuning.feedback_gain * yaw_error * measurement_dt
          proposed = base + self.bias + increment
          field_limited = float(np.clip(proposed, -.5, .5))
          host_limited = previous_command + float(np.clip(field_limited - previous_command,
                                                          -self.tuning.heading_rate * dt, self.tuning.heading_rate * dt))
          # Admit the reachable portion of an outward increment, rather than
          # freezing forever when a large/batched error exceeds one tick's slew.
          # A base transition must not fabricate a correction opposite the error.
          if yaw_error * (proposed - host_limited) > 1e-12:
            self.bias += float(np.clip(host_limited - (base + self.bias), min(0., increment), max(0., increment)))
            status = 'host_limit'
          else:
            self.bias += increment
            status = 'integrating'
    self.bias = float(np.clip(self.bias, -.5 - base, .5 - base))
    self.diagnostics = {'heading_bias': self.bias, 'feedback_status': status, 'feedback_reference_time': reference_time,
                        'feedback_reference_curvature': reference_curvature, 'feedback_yaw_error': yaw_error}
    return float(np.clip(base + self.bias, -.5, .5))


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
  """Encode the same absolute planned curvature as C0 and C1.

  The former spatial-heading reference is retained for diagnostic comparison
  and the existing input-validity gates. A bounded yaw-error integral corrects
  C1 when fresh PSCM status permits; no fixed EPS gain is assumed.
  """
  def __init__(self, response_delay=.2, tuning: PathTuning | None = None):
    self.tuning = tuning if tuning is not None else PathTuning()
    if not math.isfinite(response_delay) or not .05 <= response_delay <= .5:
      raise ValueError("response delay must be within 0.05..0.5 seconds")
    if not all(math.isfinite(v) and v >= 0 for v in vars(self.tuning).values()) or min(
      self.tuning.offset_horizon, self.tuning.heading_horizon, self.tuning.heading_time, self.tuning.offset_rate, self.tuning.heading_rate,
    ) <= 0:
      raise ValueError("invalid path tuning")
    self.delay = response_delay
    self.reference = PathReference(self.tuning)
    self.feedback = HeadingFeedback(self.delay, self.tuning)
    self.reset()

  def reset(self):
    self.reference.reset()
    self.feedback.reset()
    self.command = FordPath()
    self.last_time = None
    self.last_measurement_time = None
    self.offset_request = self.heading_request = 0.0
    self.diagnostics = {'status': 'inactive', 'hypothesis': 'curvature-c0-c1-feedback-v5', 'command': (0., 0., 0., 0.),
                        **self.feedback.diagnostics}

  def update(self, model, desired_curvature, *, yaw_rate, speed, now, measurement_time, model_time, reference_time,
             active, valid=True, steering_pressed=False, steering_torque=0., pscm_status: PscmStatus | None = None):
    finite = all(math.isfinite(v) for v in (desired_curvature, yaw_rate, speed, now, measurement_time, model_time, reference_time))
    fresh = finite and all(-.005 <= now - timestamp <= .15 for timestamp in (measurement_time, model_time, reference_time))
    if not active or not valid or model is None or not fresh or not .3 <= speed <= 55 or abs(yaw_rate) > 3 or abs(desired_curvature) > 1:
      self.reset()
      self.diagnostics['status'] = 'inactive' if not active else 'invalid_input'
      self.diagnostics['reason'] = ('inactive' if not active else 'invalid_service' if not valid else 'missing_model' if model is None else
                                    'nonfinite' if not finite else 'stale_input' if not fresh else 'speed' if not .3 <= speed <= 55 else
                                    'yaw_rate' if abs(yaw_rate) > 3 else 'desired_curvature')
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
    offset_horizon = max(self.tuning.offset_horizon, speed * self.tuning.heading_time)
    heading_horizon = max(speed * self.tuning.heading_time, self.tuning.heading_horizon)
    model_heading_horizon = min(heading_horizon, max(path[0][-1] - advance, 0.0))
    ego = _predicted_pose(advance, current_curvature, 0.)
    _, model_heading = _relative_pose(advance + model_heading_horizon, path, ego)
    # The selected action already contains the planner's steering correction and
    # upstream delay handling. Encode absolute curvature as a virtual parabolic
    # displacement; measured curvature must not erase a sustained turn request.
    # This preview sets command scale, not a model of the PSCM's wheel response.
    offset = .5 * desired_curvature * offset_horizon ** 2
    target_offset = float(np.clip(offset, -5.11, 5.11))
    # Absolute feedforward retains sustained turn demand. Measured tracking can
    # add or subtract a bounded correction; model geometry remains diagnostic.
    base_heading = float(np.clip(desired_curvature * heading_horizon, -.5, .5))
    driver_override = steering_pressed or not math.isfinite(steering_torque) or abs(steering_torque) > CarControllerParams.STEER_DRIVER_ALLOWANCE
    target_heading = self.feedback.update(base_heading, desired_curvature, yaw_rate=yaw_rate, speed=speed, now=now,
                                          measurement_time=measurement_time, dt=dt, previous_command=self.heading_request,
                                          heading_horizon=heading_horizon, driver_override=driver_override, pscm_status=pscm_status)
    delta_offset = target_offset - self.offset_request
    delta_heading = target_heading - self.heading_request
    # A slow C1 transition must not hold a C0 correction after action releases it.
    offset_scale = min(1., self.tuning.offset_rate * dt / abs(delta_offset)) if delta_offset else 1.
    heading_scale = min(1., self.tuning.heading_rate * dt / abs(delta_heading)) if delta_heading else 1.
    self.offset_request += offset_scale * delta_offset
    self.heading_request += heading_scale * delta_heading
    offset = _packed(self.offset_request, .01, -5.12)
    heading = _packed(self.heading_request, .0005, -.5)
    self.command = FordPath(True, offset, heading, 0., 0.)
    self.diagnostics = {'status': 'driver_override' if driver_override else 'active', 'hypothesis': 'curvature-c0-c1-feedback-v5',
                        'desired_curvature': desired_curvature, 'offset_target': target_offset, 'heading_target': target_heading,
                        'heading_base': base_heading, 'feedback_gain': self.tuning.feedback_gain, 'feedback_min_speed': FEEDBACK_MIN_SPEED,
                        'steering_torque': steering_torque if math.isfinite(steering_torque) else None,
                        'pscm_valid': pscm_status.valid if pscm_status is not None else False,
                        'pscm_timestamp': pscm_status.timestamp if pscm_status is not None and math.isfinite(pscm_status.timestamp) else None,
                        'pscm_age': now - pscm_status.timestamp if pscm_status is not None and math.isfinite(pscm_status.timestamp) else None,
                        'pscm_limit': pscm_status.limit if pscm_status is not None else None,
                        'pscm_capability': pscm_status.capability if pscm_status is not None else None,
                        'pscm_lateral_state': pscm_status.lateral_state if pscm_status is not None else None,
                        'pscm_denied': pscm_status.denied if pscm_status is not None else None,
                        **self.feedback.diagnostics,
                        'model_heading_target': float(np.clip(model_heading, -.5, .5)), 'model_heading_horizon': model_heading_horizon,
                        'offset_slew_scale': offset_scale, 'heading_slew_scale': heading_scale,
                        'measurement_age': now - measurement_time, 'model_age': now - model_time, 'reference_age': now - reference_time,
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
