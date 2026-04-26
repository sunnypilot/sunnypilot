import math
import numpy as np
from collections import deque

from cereal import log
from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt

# At higher speeds (25+mph) we can assume:
# Lateral acceleration achieved by a specific car correlates to
# torque applied to the steering rack. It does not correlate to
# wheel slip, or to speed.

# This controller applies torque to achieve desired lateral
# accelerations. To compensate for the low speed effects the
# proportional gain is increased at low speeds by the PID controller.
# Additionally, there is friction in the steering wheel that needs
# to be overcome to move it at all, this is compensated for too.

INTERP_SPEEDS = [1, 1.5, 2.0, 3.0, 5, 7.5, 10, 15, 30]
KP_INTERP = [150.0, 100.0, 30.0, 6.0, 2.0, 1.5, 1.2, 0.8, 0.5]
KI_INTERP = [0.06, 0.06, 0.06, 0.08, 0.08, 0.10, 0.12, 0.14, 0.16]
JERK_INTERP = [0.25, 0.25, 0.25, 0.23, 0.20, 0.18, 0.16, 0.15, 0.15]
MEAS_FILTER_TAU_INTERP = [0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06, 0.05, 0.01]
INTEGRATOR_DECAY_INTERP = [0.990, 0.990, 0.990, 0.992, 0.993, 0.995, 0.996, 0.998, 0.999]
INTEGRATOR_DECAY_FRAMES = 20
STRAIGHT_DAMP_THRESHOLD_INTERP = [0.03, 0.03, 0.03, 0.03, 0.03, 0.05, 0.05, 0.2, 0.2]
STRAIGHT_DAMP_MIN_INTERP = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
STRAIGHT_DAMP_TAU = 0.5

LP_FILTER_CUTOFF_HZ = 1.2
JERK_LOOKAHEAD_SECONDS = 0.30
LAT_ACCEL_REQUEST_BUFFER_SECONDS = 1.0
VERSION = 1

class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)
    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()
    self.pid = PIDController([INTERP_SPEEDS, KP_INTERP], [INTERP_SPEEDS, KI_INTERP], rate=1/self.dt)
    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg
    self.lat_accel_request_buffer_len = int(LAT_ACCEL_REQUEST_BUFFER_SECONDS / self.dt)
    self.lat_accel_request_buffer = deque([0.] * self.lat_accel_request_buffer_len , maxlen=self.lat_accel_request_buffer_len)
    self.lookahead_frames = int(JERK_LOOKAHEAD_SECONDS / self.dt)
    self.jerk_filter = FirstOrderFilter(0.0, 1 / (2 * np.pi * LP_FILTER_CUTOFF_HZ), self.dt)
    self.measurement_filter = FirstOrderFilter(0.0, 0.04, self.dt)
    self.integrator_decay_counter = 0
    self.straight_damp_filter = FirstOrderFilter(1.0, STRAIGHT_DAMP_TAU, self.dt)

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction
    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(self.lateral_accel_from_torque(self.steer_max, self.torque_params),
                        self.lateral_accel_from_torque(-self.steer_max, self.torque_params))

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, calibrated_pose, curvature_limited, lat_delay):
    # Override torque params from extension
    if self.extension.update_override_torque_params(self.torque_params):
      self.update_limits()

    pid_log = log.ControlsState.LateralTorqueState.new_message()
    pid_log.version = VERSION
    measured_curvature = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
    meas_tau = float(np.interp(CS.vEgo, INTERP_SPEEDS, MEAS_FILTER_TAU_INTERP))
    self.measurement_filter.update_alpha(meas_tau)
    measurement = self.measurement_filter.update(measured_curvature * CS.vEgo ** 2)
    future_desired_lateral_accel = desired_curvature * CS.vEgo ** 2
    self.lat_accel_request_buffer.append(future_desired_lateral_accel)

    roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY
    curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
    lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

    delay_frames = int(np.clip(lat_delay / self.dt + 1, 1, self.lat_accel_request_buffer_len))
    expected_lateral_accel = self.lat_accel_request_buffer[-delay_frames]
    setpoint = expected_lateral_accel
    raw_error = setpoint - measurement
    damp_min = float(np.interp(CS.vEgo, INTERP_SPEEDS, STRAIGHT_DAMP_MIN_INTERP))
    damp_threshold = float(np.interp(CS.vEgo, INTERP_SPEEDS, STRAIGHT_DAMP_THRESHOLD_INTERP))
    damp_target = max(damp_min, min(1.0, abs(setpoint) / damp_threshold))
    damp_factor = self.straight_damp_filter.update(damp_target)
    error = raw_error * damp_factor

    lookahead_idx = int(np.clip(-delay_frames + self.lookahead_frames, -self.lat_accel_request_buffer_len+1, -2))
    raw_lateral_jerk = (self.lat_accel_request_buffer[lookahead_idx+1] - self.lat_accel_request_buffer[lookahead_idx-1]) / (2 * self.dt)
    desired_lateral_jerk = self.jerk_filter.update(raw_lateral_jerk)
    gravity_adjusted_future_lateral_accel = future_desired_lateral_accel - roll_compensation
    ff = gravity_adjusted_future_lateral_accel
    # latAccelOffset corrects roll compensation bias from device roll misalignment relative to car roll
    ff -= self.torque_params.latAccelOffset
    jerk_gain = float(np.interp(CS.vEgo, INTERP_SPEEDS, JERK_INTERP))
    ff += get_friction(error + jerk_gain * desired_lateral_jerk, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)

    if not active:
      output_torque = 0.0
      pid_log.active = False
    else:
      # do error correction in lateral acceleration space, convert at end to handle non-linear torque responses correctly
      pid_log.error = float(error)

      freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
      output_lataccel = self.pid.update(pid_log.error, speed=CS.vEgo, feedforward=ff, freeze_integrator=freeze_integrator)

      error_opposes_integrator = (self.pid.i > 0 and pid_log.error < 0) or (self.pid.i < 0 and pid_log.error > 0)
      if error_opposes_integrator:
        self.integrator_decay_counter = min(self.integrator_decay_counter + 1, INTEGRATOR_DECAY_FRAMES + 10)
      else:
        self.integrator_decay_counter = 0
      if self.integrator_decay_counter >= INTEGRATOR_DECAY_FRAMES:
        self.pid.i *= float(np.interp(CS.vEgo, INTERP_SPEEDS, INTEGRATOR_DECAY_INTERP))

      output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

      # Lateral acceleration torque controller extension updates
      # Overrides pid_log.error and output_torque
      pid_log, output_torque = self.extension.update(CS, VM, self.pid, params, ff, pid_log, setpoint, measurement, calibrated_pose, roll_compensation,
                                                     future_desired_lateral_accel, measurement, lateral_accel_deadzone, gravity_adjusted_future_lateral_accel,
                                                     desired_curvature, measured_curvature, steer_limited_by_safety, output_torque)

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque) # TODO: log lat accel?
      pid_log.actualLateralAccel = float(measurement)
      pid_log.desiredLateralAccel = float(setpoint)
      pid_log.desiredLateralJerk = float(desired_lateral_jerk)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited))

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log
