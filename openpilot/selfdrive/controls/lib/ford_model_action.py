"""Experimental Ford C2-free controller with measured-curvature C1 feedback.

Selected only by its explicit toggle. The 7 m station and one-second scale are
engineering choices. Feeding integrated heading mismatch into C1 at 1:1 is an
explicit feedback-strength choice, not an identified PSCM model or calibration.
Opposed correction may be released when both path commands confirm the turn.
"""
import math
import struct

import numpy as np

from opendbc.car.ford.values import CarControllerParams, FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, _model_path


OFFSET_STATION_M = 7.0
HEADING_TIME_S = 1.0
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
  """Encode y(7) and max(7, v*1s)*selected limited curvature.

  Preserve the reviewed core's endpoint hold when the path ends before 7 m.
  This samples the available geometry; it does not extrapolate an unseen path.
  """
  if not _finite(desired_curvature, speed) or not .3 <= speed <= 55 or abs(desired_curvature) > 1:
    return FordPath()
  try:
    path = _model_path(model)
  except OverflowError:
    return FordPath()
  if path is None or not all(_finite(*values) for values in path):
    return FordPath()
  station, _, lateral, _ = path
  c0 = float(np.interp(min(OFFSET_STATION_M, station[-1]), station, lateral))
  c1 = max(OFFSET_STATION_M, speed*HEADING_TIME_S)*desired_curvature
  return FordPath(True, c0, c1, 0., 0.) if _finite(c0, c1) else FordPath()


class ModelActionController:
  """Unquantized C0/C1 slew positions and one C1 feedback correction.

  Feedback integrates requested minus measured curvature over traveled distance.
  Freshness, measurement cadence and driver/PSCM arbitration belong to the caller.
  """
  __slots__ = ('c0', 'c1', 'correction', 'carryover_release_count')

  def __init__(self):
    self.reset()

  def reset(self):
    self.c0 = self.c1 = self.correction = 0.
    self.carryover_release_count = 0  # Diagnostic only; never feeds the command law.

  def update(self, model, desired_curvature, *, current_curvature, speed, dt, active=True, valid=True,
             feedback_dt=None, feedback_enabled=True, pscm_limited=False):
    feedback_dt = dt if feedback_dt is None else feedback_dt
    if (not active or not valid or not _finite(dt, feedback_dt, current_curvature) or not .002 <= dt <= .1
        or not 0. <= feedback_dt <= .15 or abs(current_curvature) > 1.):
      self.reset()
      return FordPath()
    target = encode_model_action(model, desired_curvature, speed)
    if not target.valid:
      self.reset()
      return FordPath()
    c0 = float(np.clip(target.path_offset, -5.11, 5.11))
    self.c0 += float(np.clip(c0-self.c0, -4.*dt, 4.*dt))
    base_c1 = float(np.clip(target.path_angle, -.5, .5))
    lower = max(-.5, self.c1-.5*dt)
    upper = min(.5, self.c1+.5*dt)
    if not feedback_enabled:
      self.correction = 0.
    else:
      direction = math.copysign(1., base_c1)
      # Release only correction that prevents C1 from requesting the direction
      # shared by target C0, slewed C0 and base C1, while measured steering is
      # still opposite. One DBC step confirms each request is nonzero. Matched
      # steering, neutral/conflicting centering and duplicate samples retain I.
      if (feedback_dt > 0. and abs(base_c1) >= .0005 and current_curvature*direction < 0.
          and min(c0*direction, self.c0*direction) >= .01
          and (base_c1+self.correction)*direction <= 0.):
        self.correction = 0.
        self.carryover_release_count += 1
      increment = (desired_curvature-current_curvature)*speed*feedback_dt
      # LimitReached inhibits only extra demand in the measured turn direction.
      # Opposing correction and changes to the model request remain available.
      direction = current_curvature if current_curvature else self.c1
      if pscm_limited and increment*direction > 0.:
        # An old opposing correction may return to zero; don't trap it below
        # the base request just because the PSCM now reports a limit.
        increment = float(np.clip(increment, min(-self.correction, 0.), max(-self.correction, 0.)))
      # Integrate only as far as this cycle's amplitude/slew envelope permits.
      # If the base moved outside that envelope, allow increments toward it;
      # never rewrite existing correction merely because the base changed.
      request = base_c1+self.correction
      self.correction += float(np.clip(increment, min(lower-request, 0.), max(upper-request, 0.)))
    c1 = float(np.clip(base_c1+self.correction, -.5, .5))
    self.c1 += float(np.clip(c1-self.c1, -.5*dt, .5*dt))
    return FordPath(True, _packed(self.c0, .01, -5.12), _packed(self.c1, .0005, -.5), 0., 0.)


class FordModelActionController:
  """Input adapter for the opt-in selected-action controller.

  controlsd owns upstream selection/limiting and service health. This adapter
  checks ages and clock order, then supplies elapsed time to the three-state
  core. Feedback advances once per fresh steering measurement; repeated samples
  can still advance output slew. Raw model geometry is checked on every cycle.

  CAN yaw remains a health gate, not the feedback measurement. Driver override
  clears the correction. Fresh PSCM limits only inhibit outward integration;
  neither a limit nor a repeated measurement freezes the model request.
  """
  def __init__(self):
    self.core = ModelActionController()
    self.reset()

  def reset(self, status='inactive'):
    self.core.reset()
    self.last_time = self.last_measurement_time = self.last_model_time = None
    self.diagnostics = {'status': status, 'hypothesis': 'model-action-c1-feedback-v2',
                        'calibration_approved': CALIBRATION_APPROVED, 'command': (0., 0., 0., 0.)}

  def update(self, model, desired_curvature, *, current_curvature, yaw_rate, speed, now, measurement_time, model_time,
             reference_time, active, valid=True, driver_pressed=False, driver_torque=0., pscm_status=None):
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
                               feedback_dt=feedback_dt, feedback_enabled=feedback_enabled, pscm_limited=pscm_limited)
    if not command.valid:
      self.reset('invalid_path')
      return command
    self.last_time, self.last_measurement_time, self.last_model_time = now, measurement_time, model_time
    self.diagnostics = {'status': 'active', 'hypothesis': 'model-action-c1-feedback-v2',
                        'calibration_approved': CALIBRATION_APPROVED, 'desired_curvature': desired_curvature,
                        'model_age': now - model_time, 'measurement_age': now - measurement_time, 'reference_age': now - reference_time,
                        'dt': dt, 'offset_request': self.core.c0, 'heading_request': self.core.c1,
                        'curvature_error': desired_curvature-current_curvature, 'feedback_dt': feedback_dt,
                        'heading_feedforward': float(np.clip(max(OFFSET_STATION_M, speed*HEADING_TIME_S)*desired_curvature, -.5, .5)),
                        'heading_correction': self.core.correction, 'feedback_enabled': feedback_enabled,
                        'carryover_release_count': self.core.carryover_release_count,
                        'driver_override': driver_override, 'pscm_limited': pscm_limited, 'pscm_status_fresh': bool(status_fresh),
                        'command': (command.path_offset, command.path_angle, 0., 0.)}
    return command


def select_model_action_controller(CP, enabled, previous_controller):
  """The separate default-off toggle takes priority on the CAN FD Lightning."""
  compatible = CP.brand == 'ford' and CP.flags & FordFlags.CANFD and CP.carFingerprint == 'FORD_F_150_LIGHTNING_MK1'
  if enabled and compatible:
    return FordModelActionController()
  return previous_controller
