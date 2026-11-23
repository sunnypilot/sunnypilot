"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import numpy as np
from collections import deque

from opendbc.car.interfaces import get_torque_params
from opendbc.car.vehicle_model import VehicleModel
from openpilot.cereal import log
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol import LatControl

# gains are in lateral acceleration, scaled to torque per degree by each car's vehicle model and latAccelFactor
PIDD_VERSION = 2.0
INTERP_SPEEDS = [1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 30.0]
KP_INTERP = [250.0, 120.0, 65.0, 30.0, 11.5, 5.5, 3.5, 2.0, 0.8]
TD_INTERP = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15, 0.2]
HIGH_SPEED_BP = [25.0, 29.0]
TURN_RATE_BP = [5.0, 20.0]
TURN_LAT_ACCEL_BP = [0.18, 0.53]
DESIRED_ANGLE_BUFFER_SECONDS = 1.0
LIVE_LAT_ACCEL_FACTOR_RANGE = [1.0, 2.0]
LIVE_FRICTION_RANGE = [0.5, 2.0]
SWING_CAP_FRICTION = 1.3


def pidd_selected(CP):
  return CP.steerControlType == 'torque' and CP.lateralTuning.which() == 'pid' and len(CP.lateralTuning.pid.kpBP) == 0 and \
    CP.carFingerprint in get_torque_params()


def filter_rc(hz):
  return 1 / (2 * math.pi * hz)


def lat_accel_per_deg(VM, v_ego):
  return VM.calc_curvature(math.radians(1.0), v_ego, 0.0) * v_ego**2


class LatControlPidd(LatControl):
  def __init__(self, CP, CP_SP, CI, dt):
    super().__init__(CP, CP_SP, CI, dt)

    torque_params = get_torque_params()[CP.carFingerprint]
    self.VM = VehicleModel(CP)
    self.pid = PIDController(0.0, 0.0, 0.0, pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.offline_lat_accel_factor, self.offline_friction = float(torque_params['LAT_ACCEL_FACTOR']), float(torque_params['FRICTION'])
    self.lat_accel_factor = self.friction = None
    self.update_torque_parameters(self.offline_lat_accel_factor, 0.0, self.offline_friction)

    self.error_filter = FirstOrderFilter(0.0, filter_rc(1.0), dt)
    self.request_filter = FirstOrderFilter(0.0, filter_rc(3.0), dt, initialized=False)
    self.error_rate_filter = FirstOrderFilter(0.0, 0.0354, dt)
    self.wheel_angle_filter = FirstOrderFilter(0.0, filter_rc(10.0), dt, initialized=False)
    self.wheel_rate_filter = FirstOrderFilter(0.0, 0.005, dt)
    self.request_rate_ref = FirstOrderFilter(0.0, filter_rc(1.0), dt)
    self.break_rate = FirstOrderFilter(0.0, filter_rc(0.5), dt)
    self.break_rate2 = FirstOrderFilter(0.0, filter_rc(0.5), dt)
    self.break_error = FirstOrderFilter(0.0, filter_rc(1.0), dt)
    self.command_slow = FirstOrderFilter(0.0, filter_rc(0.5), dt, initialized=False)
    self.last_error = 0.0
    self.wheel_angle_held = None
    self.swing = 0.0

    buffer_len = int(DESIRED_ANGLE_BUFFER_SECONDS / dt)
    self.desired_angle_buffer = deque([0.0] * buffer_len, maxlen=buffer_len)
    self.delay_frames = int(np.clip(CP.steerActuatorDelay / dt + 1, 1, buffer_len))
    self.rate_span_frames = max(1, int(0.1 / dt))

  def update_torque_parameters(self, latAccelFactor, latAccelOffset, friction):
    # a learned factor below the offline one would raise every gain
    latAccelFactor = float(np.clip(latAccelFactor, *(r * self.offline_lat_accel_factor for r in LIVE_LAT_ACCEL_FACTOR_RANGE)))
    friction = float(np.clip(friction, *(r * self.offline_friction for r in LIVE_FRICTION_RANGE)))
    if (latAccelFactor, friction) == (self.lat_accel_factor, self.friction):
      return
    self.lat_accel_factor, self.friction = latAccelFactor, friction
    self.kp = [kp * lat_accel_per_deg(self.VM, v) / latAccelFactor for kp, v in zip(KP_INTERP, INTERP_SPEEDS, strict=True)]
    self.pid._k_p = (INTERP_SPEEDS, self.kp)
    self.pid._k_i = (INTERP_SPEEDS, [kp / 6.0 for kp in self.kp])
    self.pid._k_d = (INTERP_SPEEDS, [kp * td for kp, td in zip(self.kp, TD_INTERP, strict=True)])

  def reset(self):
    super().reset()
    self.pid.reset()
    self.swing = self.last_error = 0.0
    self.command_slow.initialized = False
    for f in (self.error_filter, self.error_rate_filter, self.wheel_rate_filter, self.request_rate_ref, self.break_error, self.break_rate, self.break_rate2):
      f.x = 0.0

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, calibrated_pose, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)

    high_speed = float(np.interp(CS.vEgo, HIGH_SPEED_BP, [0.0, 1.0]))
    angle_steers_des_no_offset = self.request_filter.update(math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll)))
    angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg

    self.desired_angle_buffer.append(angle_steers_des)
    expected_angle = self.desired_angle_buffer[-self.delay_frames]
    request_rate = (self.desired_angle_buffer[-1] - self.desired_angle_buffer[-1 - self.rate_span_frames]) / (self.rate_span_frames * self.dt)
    request_rate_ref = self.request_rate_ref.update(request_rate)
    break_rate = self.break_rate2.update(self.break_rate.update(request_rate))
    # a 1 Hz error filter lags enough for P to pump a 2 Hz wheel swing, so it opens up only while the request turns the wheel
    error_filter_hz = float(np.interp(abs(request_rate_ref), TURN_RATE_BP, [1.0, 3.0]))
    self.error_filter.update_alpha(filter_rc(float(np.interp(CS.vEgo, HIGH_SPEED_BP, [error_filter_hz, 1.0]))))
    error = self.error_filter.update(expected_angle - CS.steeringAngleDeg)
    # at highway speed, ignore the angle sensor toggling one count
    held = self.wheel_angle_held if self.wheel_angle_held is not None else CS.steeringAngleDeg
    wheel_backlash = 0.08 * high_speed
    self.wheel_angle_held = held = CS.steeringAngleDeg - float(np.clip(CS.steeringAngleDeg - held, -wheel_backlash, wheel_backlash))
    wheel_angle_last = self.wheel_angle_filter.x if self.wheel_angle_filter.initialized else held
    wheel_rate = self.wheel_rate_filter.update((self.wheel_angle_filter.update(held) - wheel_angle_last) / self.dt)

    wheel_swing = 0.0 if CS.steeringPressed else min(abs(wheel_rate - request_rate_ref), 60.0)
    self.swing = max(wheel_swing, self.swing * (1.0 - self.dt))

    pid_log.steeringAngleDesiredDeg = float(angle_steers_des)
    pid_log.angleError = float(error)

    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.reset()
    else:
      error_rate = self.error_rate_filter.update((error - self.last_error) / self.dt)
      self.last_error = error
      error_rate += high_speed * (-wheel_rate - error_rate)
      ff = angle_steers_des_no_offset * lat_accel_per_deg(VM, CS.vEgo) / self.lat_accel_factor
      ff += 0.4 * params.roll * ACCELERATION_DUE_TO_GRAVITY / self.lat_accel_factor

      # break rack friction as soon as the request moves, before the error builds up
      error_deadzone = error - float(np.clip(error, -0.3, 0.3))
      turn_lat_accel = abs(desired_curvature) * max(CS.vEgo, 8.0) ** 2
      friction_scale = float(np.interp(turn_lat_accel, TURN_LAT_ACCEL_BP, [0.6, 1.0]))
      friction = self.friction * (friction_scale + high_speed * (0.1 - friction_scale))
      friction_rate_gain = 0.75 - 0.25 * high_speed
      ff += friction * float(np.tanh((error_deadzone + friction_rate_gain * request_rate) * 0.1887))
      kp = float(np.interp(CS.vEgo, INTERP_SPEEDS, self.kp))
      # damp the wheel toward the request's rate; the rack rings near 2 Hz without it
      wheel_damp = 0.0 if CS.steeringPressed else (1.0 - high_speed) * kp * 0.05 * (wheel_rate - request_rate_ref)
      ff -= wheel_damp
      # half P on a straight, flat road; the cut goes through the feedforward so the integrator still holds a crown
      kp_load = max(float(np.interp(turn_lat_accel, TURN_LAT_ACCEL_BP, [0.0, 1.0])),
                    float(np.interp(abs(params.roll) * ACCELERATION_DUE_TO_GRAVITY, [0.35, 0.7], [0.0, 1.0])))
      kp_scale = 0.5 + 0.5 * kp_load
      ff -= (1.0 - float(np.interp(CS.vEgo, [12.0, 18.0], [kp_scale, 1.0]))) * kp * error
      ff += high_speed * 0.325 * self.friction * float(np.tanh((self.break_error.update(error) + 0.35 * break_rate) / 0.5))

      freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
      error_rate_clean = error_rate - float(np.clip(error_rate, -0.3, 0.3))
      output_torque = self.pid.update(error, error_rate=error_rate_clean, feedforward=ff, speed=CS.vEgo, freeze_integrator=freeze_integrator)

      # a swing the request isn't asking for: pass only the command's slow part
      command = output_torque + wheel_damp
      self.command_slow.update(command)
      if CS.steeringPressed:
        self.command_slow.x = command
      swing_gate = float(np.interp(self.swing, [16.0, 30.0], [0.0, 1.0])) * float(np.interp(CS.vEgo, [3.0, 5.0, 10.0, 14.0], [0.0, 1.0, 1.0, 0.0]))
      swing_gate *= 1.0 - float(np.interp(abs(request_rate_ref), TURN_RATE_BP, [0.0, 1.0]))
      swing_gate *= 1.0 - float(np.interp(turn_lat_accel, TURN_LAT_ACCEL_BP, [0.0, 1.0]))
      swing_gate *= 1.0 - float(np.interp(abs(error), [3.0, 6.0], [0.0, 1.0]))
      if not (CS.steeringPressed or CS.leftBlinker or CS.rightBlinker):
        cap = SWING_CAP_FRICTION * self.friction
        output_torque += swing_gate * float(np.clip(self.command_slow.x - command, -cap, cap))
      output_torque = float(np.clip(output_torque, -self.steer_max, self.steer_max))

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(output_torque)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited))
    return output_torque, angle_steers_des, pid_log
