import math
import numpy as np

from cereal import log
from opendbc.car.interfaces import LatControlInputs
from opendbc.car.vehicle_model import ACCELERATION_DUE_TO_GRAVITY
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params # Added import

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt

# At higher speeds (25+mph) we can assume:
# Lateral acceleration achieved by a specific car correlates to
# torque applied to the steering rack. It does not correlate to
# wheel slip, or to speed.

# This controller applies torque to achieve desired lateral
# accelerations. To compensate for the low speed effects we
# use a LOW_SPEED_FACTOR in the error. Additionally, there is
# friction in the steering wheel that needs to be overcome to
# move it at all, this is compensated for too.

LOW_SPEED_X = [0, 10, 20, 30]
LOW_SPEED_Y = [15, 13, 10, 5]


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI):
    super().__init__(CP, CP_SP, CI) # This stores self.CP_SP = CP_SP and self.CP = CP
    self.torque_params = CP.lateralTuning.torque.as_builder()
    # self.pid is initialized in super().__init__ (LatControl) using CP.lateralTuning.pid.
    # For LatControlTorque, we re-initialize self.pid with torque controller specific gains.
    self.pid = PIDController(CP.lateralTuning.torque.kp, CP.lateralTuning.torque.ki,
                             k_f=CP.lateralTuning.torque.kf, pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.use_steering_angle = self.torque_params.useSteeringAngle
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.extension = LatControlTorqueExt(self, CP, CP_SP)
    try:
      self.enhanced_steering_enabled = not Params().get_bool("dp_disable_dynamic_steering") # Changed line
    except Exception: # To cover cases where Params might not be available (e.g. tests)
      self.enhanced_steering_enabled = False


  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction

  def update(self, active, CS, VM, params, steer_limited_by_controls, desired_curvature, calibrated_pose, curvature_limited):
    pid_log = log.ControlsState.LateralTorqueState.new_message()

    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.pid.reset()
    else:
      # Determine current steering parameters based on speed and toggle
      active_steering_profile_str = "city_defaults" # Default if enhanced_steering_enabled is true but no profile matches

      if self.enhanced_steering_enabled:
        speed = CS.vEgo
        PARKING_SPEED_THRESHOLD = 5.0 * CV.MPH_TO_MS
        HIGHWAY_SPEED_THRESHOLD = 35.0 * CV.MPH_TO_MS

        current_kp = self.CP.lateralTuning.torque.kp
        current_ki = self.CP.lateralTuning.torque.ki
        current_kf = self.CP.lateralTuning.torque.kf
        current_steer_max = self.CP.maxSteeringAngleDeg

        if self.CP_SP is not None:
          if speed < PARKING_SPEED_THRESHOLD:
            if hasattr(self.CP_SP, 'spDynamicSteeringParkingLot') and self.CP_SP.spDynamicSteeringParkingLot is not None:
              parking_params = self.CP_SP.spDynamicSteeringParkingLot
              current_kp = parking_params.kp
              current_ki = parking_params.ki
              current_kf = parking_params.kf
              current_steer_max = parking_params.steerMax
              active_steering_profile_str = "parking"
          elif speed > HIGHWAY_SPEED_THRESHOLD:
            if hasattr(self.CP_SP, 'spDynamicSteeringHighway') and self.CP_SP.spDynamicSteeringHighway is not None:
              highway_params = self.CP_SP.spDynamicSteeringHighway
              current_kp = highway_params.kp
              current_ki = highway_params.ki
              current_kf = highway_params.kf
              current_steer_max = highway_params.steerMax
              active_steering_profile_str = "highway"
          else:
            active_steering_profile_str = "city" # Default for enhanced mode, mid-speed range

        self.pid.k_p = current_kp
        self.pid.k_i = current_ki
        self.pid.k_f = current_kf
        self.pid.pos_limit = current_steer_max
        self.pid.neg_limit = -current_steer_max
        self.steer_max = current_steer_max
      else:
        # Enhanced steering is disabled, ensure default/fixed parameters from CP are used
        self.pid.k_p = self.CP.lateralTuning.torque.kp
        self.pid.k_i = self.CP.lateralTuning.torque.ki
        self.pid.k_f = self.CP.lateralTuning.torque.kf
        self.pid.pos_limit = self.CP.maxSteeringAngleDeg
        self.pid.neg_limit = -self.CP.maxSteeringAngleDeg
        self.steer_max = self.CP.maxSteeringAngleDeg
        active_steering_profile_str = "disabled_defaults"

      # Log active steering parameters
      pid_log.activeSteeringProfile = active_steering_profile_str
      pid_log.activeKp = self.pid.k_p
      pid_log.activeKi = self.pid.k_i
      pid_log.activeKf = self.pid.k_f
      pid_log.activeSteerMax = self.pid.pos_limit

      # Original LatControlTorque logic continues here
      actual_curvature_vm = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
      roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY
      if self.use_steering_angle:
        actual_curvature = actual_curvature_vm
        curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
      else:
        assert calibrated_pose is not None
        actual_curvature_pose = calibrated_pose.angular_velocity.yaw / CS.vEgo
        actual_curvature = np.interp(CS.vEgo, [2.0, 5.0], [actual_curvature_vm, actual_curvature_pose])
        curvature_deadzone = 0.0
      desired_lateral_accel = desired_curvature * CS.vEgo ** 2

      actual_lateral_accel = actual_curvature * CS.vEgo ** 2
      lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2

      low_speed_factor = np.interp(CS.vEgo, LOW_SPEED_X, LOW_SPEED_Y)**2
      setpoint = desired_lateral_accel + low_speed_factor * desired_curvature
      measurement = actual_lateral_accel + low_speed_factor * actual_curvature
      gravity_adjusted_lateral_accel = desired_lateral_accel - roll_compensation

      torque_from_setpoint = self.torque_from_lateral_accel(LatControlInputs(setpoint, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
                                                            setpoint, lateral_accel_deadzone, friction_compensation=False, gravity_adjusted=False)
      torque_from_measurement = self.torque_from_lateral_accel(LatControlInputs(measurement, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
                                                               measurement, lateral_accel_deadzone, friction_compensation=False, gravity_adjusted=False)
      pid_log.error = float(torque_from_setpoint - torque_from_measurement)
      ff = self.torque_from_lateral_accel(LatControlInputs(gravity_adjusted_lateral_accel, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
                                          desired_lateral_accel - actual_lateral_accel, lateral_accel_deadzone, friction_compensation=True,
                                          gravity_adjusted=True)

      # Lateral acceleration torque controller extension updates
      ff, pid_log = self.extension.update(CS, VM, params, ff, pid_log, setpoint, measurement, calibrated_pose, roll_compensation,
                                          desired_lateral_accel, actual_lateral_accel, lateral_accel_deadzone, gravity_adjusted_lateral_accel,
                                          desired_curvature, actual_curvature)

      freeze_integrator = steer_limited_by_controls or CS.steeringPressed or CS.vEgo < 5
      output_torque = self.pid.update(pid_log.error,
                                      feedforward=ff,
                                      speed=CS.vEgo,
                                      freeze_integrator=freeze_integrator)

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque)
      pid_log.actualLateralAccel = float(actual_lateral_accel)
      pid_log.desiredLateralAccel = float(desired_lateral_accel)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_controls, curvature_limited))

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log
