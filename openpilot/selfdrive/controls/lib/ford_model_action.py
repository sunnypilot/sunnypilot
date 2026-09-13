"""Opt-in Ford C2-free model mapping with measured-curvature PI feedback.

C0 samples a desired-curvature arc at 7 m, including base-heading overflow. C1
combines the selected curvature's heading with proportional and integrated
tracking error. Reference distance and gains are explicit trial choices.
"""
import math
import struct

import numpy as np

from opendbc.car.ford.values import CarControllerParams, FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, _model_path


OFFSET_STATION_M = 7.0
HEADING_TIME_S = 1.0
C1_PROPORTIONAL_GAIN = 0.50  # Drive-trial gains, not a learned calibration.
C1_INTEGRAL_GAIN = 0.25
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
  """Encode a 7 m circular-arc offset and max(7, v*1s)*selected curvature.

  The arc starts at zero lateral position and heading. Original model geometry
  remains a health gate; selected curvature supplies both path commands.
  """
  if not _finite(desired_curvature, speed) or not .3 <= speed <= 55 or abs(desired_curvature) > 1:
    return FordPath()
  try:
    path = _model_path(model)
  except OverflowError:
    return FordPath()
  if path is None or not all(_finite(*values) for values in path):
    return FordPath()
  # (1-cos(S*k))/k, using sinc to avoid cancellation near zero curvature.
  half_heading = .5*OFFSET_STATION_M*desired_curvature
  sinc = math.sin(half_heading)/half_heading if half_heading else 1.
  c0 = .5*desired_curvature*OFFSET_STATION_M**2*sinc**2
  c1 = max(OFFSET_STATION_M, speed*HEADING_TIME_S)*desired_curvature
  return FordPath(True, c0, c1, 0., 0.) if _finite(c0, c1) else FordPath()


class ModelActionController:
  """Only C0 slew, C1 slew and integrated tracking error carry control history.

  Freshness, measurement cadence and driver/PSCM arbitration belong to the caller.
  """
  __slots__ = ('c0', 'c1', 'correction', 'proportional_gain', 'integral_gain', 'proportional', 'feedback_curvature')

  def __init__(self, proportional_gain=C1_PROPORTIONAL_GAIN, integral_gain=C1_INTEGRAL_GAIN):
    if not _finite(proportional_gain, integral_gain) or min(proportional_gain, integral_gain) < 0.:
      raise ValueError('PI gains must be finite and nonnegative')
    self.proportional_gain, self.integral_gain = float(proportional_gain), float(integral_gain)
    self.reset()

  def reset(self):
    self.c0 = self.c1 = self.correction = self.proportional = self.feedback_curvature = 0.

  def update(self, model, desired_curvature, *, current_curvature, speed, dt, active=True, valid=True,
             feedback_dt=None, feedback_enabled=True, pscm_limited=False, feedback_curvature=None):
    feedback_dt = dt if feedback_dt is None else feedback_dt
    reference = desired_curvature if feedback_curvature is None else feedback_curvature
    if (not active or not valid or not _finite(dt, feedback_dt, current_curvature, reference) or not .002 <= dt <= .1
        or not 0. <= feedback_dt <= .15 or abs(current_curvature) > 1. or abs(reference) > 1.):
      self.reset()
      return FordPath()
    target = encode_model_action(model, desired_curvature, speed)
    if not target.valid:
      self.reset()
      return FordPath()
    self.feedback_curvature = reference
    error = reference-current_curvature
    self.proportional = self.proportional_gain*max(OFFSET_STATION_M, speed*HEADING_TIME_S)*error if feedback_enabled else 0.
    if not _finite(self.proportional):
      self.reset()
      return FordPath()
    base = float(np.clip(target.path_angle, -.5, .5))
    offset = float(np.clip(target.path_offset+OFFSET_STATION_M*(target.path_angle-base), -5.11, 5.11))
    self.c0 += float(np.clip(offset-self.c0, -4.*dt, 4.*dt))
    lower, upper = max(-.5, self.c1-.5*dt), min(.5, self.c1+.5*dt)
    if feedback_enabled:
      increment = self.integral_gain*error*speed*feedback_dt
      if not _finite(increment):
        self.reset()
        return FordPath()
      direction = current_curvature if current_curvature else self.c1
      if pscm_limited and increment*direction > 0.:
        increment = float(np.clip(increment, min(-self.correction, 0.), max(-self.correction, 0.)))
      # Retire existing I before limiting new accumulation; never cross zero
      # through this step. The final command still obeys amplitude and slew.
      relief = float(np.clip(increment, min(-self.correction, 0.), max(-self.correction, 0.)))
      self.correction += relief
      increment -= relief
      request = base+self.proportional+self.correction
      self.correction += float(np.clip(increment, min(lower-request, 0.), max(upper-request, 0.)))
    else:
      self.correction = 0.
    request = float(np.clip(base+self.proportional+self.correction, -.5, .5))
    self.c1 += float(np.clip(request-self.c1, -.5*dt, .5*dt))
    return FordPath(True, _packed(self.c0, .01, -5.12), _packed(self.c1, .0005, -.5), 0., 0.)


class FordModelActionController:
  """Input adapter for the opt-in selected-action controller.

  controlsd owns upstream selection/limiting and service health. This adapter
  checks ages and clock order, then supplies elapsed time to the core.
  Feedback advances once per fresh steering measurement; repeated samples
  can still advance output slew. Raw model geometry is checked on every cycle.

  CAN yaw remains a health gate, not the feedback measurement. Driver override
  clears the correction. Fresh PSCM limits only inhibit outward integration;
  neither a limit nor a repeated measurement freezes the model request.
  """
  def __init__(self, proportional_gain=C1_PROPORTIONAL_GAIN, integral_gain=C1_INTEGRAL_GAIN):
    self.core = ModelActionController(proportional_gain=proportional_gain, integral_gain=integral_gain)
    self.hypothesis = 'model-action-curvature-c0-pi-v8'
    self.reset()

  def reset(self, status='inactive'):
    self.core.reset()
    self.last_time = self.last_measurement_time = self.last_model_time = None
    self.diagnostics = {'status': status, 'hypothesis': self.hypothesis,
                        'calibration_approved': CALIBRATION_APPROVED, 'command': (0., 0., 0., 0.)}

  def update(self, model, desired_curvature, *, current_curvature, yaw_rate, speed, now, measurement_time, model_time,
             reference_time, active, valid=True, driver_pressed=False, driver_torque=0., pscm_status=None,
             feedback_curvature=None):
    reason = None
    if not active:
      reason = 'inactive'
    elif not valid:
      reason = 'invalid_service'
    elif not _finite(desired_curvature, current_curvature, yaw_rate, speed, now, measurement_time, model_time, reference_time):
      reason = 'nonfinite'
    elif not all(-.005 <= now - timestamp <= .15 for timestamp in (measurement_time, model_time, reference_time)):
      reason = 'stale_input'
    elif not .3 <= speed <= 55 or abs(yaw_rate) > 3 or abs(desired_curvature) > 1 or abs(current_curvature) > 1:
      reason = 'input_range'
    if reason is not None:
      self.reset(reason)
      return FordPath()

    dt = .01 if self.last_time is None else now - self.last_time
    feedback_dt = 0. if self.last_measurement_time is None else measurement_time-self.last_measurement_time
    if not .002 <= dt <= .1 or not 0. <= feedback_dt <= .15 or (
      self.last_model_time is not None and model_time < self.last_model_time
    ):
      self.reset('timing_reset')
      return FordPath()
    status_fresh = (pscm_status is not None and pscm_status.valid and pscm_status.canMonoTime > 0
                    and -.005 <= now-pscm_status.canMonoTime*1e-9 <= .15)
    pscm_limited = bool(status_fresh and pscm_status.limit == 2)
    driver_override = bool(driver_pressed or not _finite(driver_torque)
                           or abs(driver_torque) > CarControllerParams.STEER_DRIVER_ALLOWANCE
                           or (status_fresh and pscm_status.limit == 3))
    feedback_enabled = not (driver_override or (status_fresh and (pscm_status.denied or pscm_status.lateralState != 2)))
    command = self.core.update(model, desired_curvature, current_curvature=current_curvature, speed=speed, dt=dt,
                               feedback_dt=feedback_dt, feedback_enabled=feedback_enabled, pscm_limited=pscm_limited,
                               feedback_curvature=feedback_curvature)
    if not command.valid:
      self.reset('invalid_path')
      return command
    self.last_time, self.last_measurement_time, self.last_model_time = now, measurement_time, model_time
    raw_heading = max(OFFSET_STATION_M, speed*HEADING_TIME_S)*desired_curvature
    base_heading = float(np.clip(raw_heading, -.5, .5))
    self.diagnostics = {'status': 'active', 'hypothesis': self.hypothesis,
                        'calibration_approved': CALIBRATION_APPROVED, 'desired_curvature': desired_curvature,
                        'model_age': now - model_time, 'measurement_age': now - measurement_time, 'reference_age': now - reference_time,
                        'dt': dt, 'offset_request': self.core.c0, 'heading_request': self.core.c1,
                        'curvature_error': desired_curvature-current_curvature, 'feedback_dt': feedback_dt,
                        'heading_feedforward': base_heading,
                        'offset_overflow': OFFSET_STATION_M*(raw_heading-base_heading),
                        'heading_correction': self.core.correction, 'feedback_enabled': feedback_enabled,
                        'heading_proportional': self.core.proportional, 'proportional_gain': self.core.proportional_gain,
                        'integral_gain': self.core.integral_gain, 'feedback_curvature': self.core.feedback_curvature,
                        'feedback_error': self.core.feedback_curvature-current_curvature,
                        'driver_override': driver_override, 'pscm_limited': pscm_limited, 'pscm_status_fresh': bool(status_fresh),
                        'command': (command.path_offset, command.path_angle, 0., 0.)}
    return command


def select_model_action_controller(CP, enabled):
  """Only opt-in Ford CAN FD vehicles override upstream curvature control."""
  compatible = CP.brand == 'ford' and CP.flags & FordFlags.CANFD
  if enabled and compatible:
    return FordModelActionController(proportional_gain=C1_PROPORTIONAL_GAIN, integral_gain=C1_INTEGRAL_GAIN)
  return None
