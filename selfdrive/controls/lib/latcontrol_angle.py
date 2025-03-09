import math
import numpy as np

from cereal import log
from openpilot.selfdrive.controls.lib.latcontrol import LatControl

STEER_ANGLE_SATURATION_THRESHOLD = 2.5  # Degrees

# Define a speed-based scaling factor similar to low_speed_factor
LOW_SPEED_X = [0, 10, 20, 30]   # Speed breakpoints
LOW_SPEED_Y = [0.67, 0.77, 0.91, 1.0]  # Factor reducing influence at low speeds

class LatControlAngle(LatControl):
  def __init__(self, CP, CP_SP, CI):
    super().__init__(CP, CP_SP, CI)
    self.sat_check_min_speed = 5.

  def update(self, active, CS, VM, params, steer_limited_by_controls, desired_curvature, calibrated_pose, curvature_limited):
    angle_log = log.ControlsState.LateralAngleState.new_message()

    if not active:
      angle_log.active = False
      angle_steers_des = float(CS.steeringAngleDeg)
    else:
      angle_log.active = True

      # Compute the base desired steering angle
      base_angle_steers_des = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))
      base_angle_steers_des += params.angleOffsetDeg

      # Apply a low-speed factor to reduce aggressive changes at low speeds
      low_speed_factor = np.interp(CS.vEgo, LOW_SPEED_X, LOW_SPEED_Y)
      angle_steers_des = CS.steeringAngleDeg + low_speed_factor * (base_angle_steers_des - CS.steeringAngleDeg)

    angle_control_saturated = abs(angle_steers_des - CS.steeringAngleDeg) > STEER_ANGLE_SATURATION_THRESHOLD
    angle_log.saturated = bool(self._check_saturation(angle_control_saturated, CS, False, curvature_limited))
    angle_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    angle_log.steeringAngleDesiredDeg = float(angle_steers_des)

    return 0, float(angle_steers_des), angle_log
