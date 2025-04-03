import math
import numpy as np
from openpilot.common.params_pyx import Params

from cereal import log
from openpilot.selfdrive.controls.lib.latcontrol import LatControl

STEER_ANGLE_SATURATION_THRESHOLD = 2.5  # Degrees

class LatControlAngle(LatControl):
  def __init__(self, CP, CP_SP, CI):
    super().__init__(CP, CP_SP, CI)
    self.params = Params()
    self.sat_check_min_speed = 5.0
    # Initialize the filtered curvature to zero (or an appropriate initial value)
    self.filtered_curvature = 0.0
    # Filter coefficient: adjust between 0 (very smooth) and 1 (no filtering)
    self.filter_speed_matrox = [0, 8.5, 11, 13.8, 22.22]
    self.filter_alpha_matrix = [0.05, 0.1, 0.3, 0.6, 1]
    self.count = 0
    self.smoothing_factor_incr = 0.

  def update(self, active, CS, VM, params, steer_limited_by_controls, desired_curvature, calibrated_pose, curvature_limited):
    # self.count += 1
    # if self.count % 25 == 0 and (smoothingFactorParam := self.params.get("HkgTuningAngleSmoothingFactor")):
    #   self.count = 0
    #   self.smoothing_factor_incr = float(smoothingFactorParam) / 10.0

    angle_log = log.ControlsState.LateralAngleState.new_message()

    if not active:
      angle_log.active = False
      angle_steers_des = float(CS.steeringAngleDeg)
    else:
      angle_log.active = True
      # Apply exponential smoothing to the curvature
      adjusted_alpha = max(float(np.interp(CS.vEgo, self.filter_speed_matrox, self.filter_alpha_matrix)) + self.smoothing_factor_incr, 1)
      self.filtered_curvature = (adjusted_alpha * desired_curvature + (1 - adjusted_alpha) * self.filtered_curvature)
      # Convert the smoothed curvature to a steering angle
      angle_steers_des = math.degrees(VM.get_steer_from_curvature(-self.filtered_curvature, CS.vEgo, params.roll))
      angle_steers_des += params.angleOffsetDeg

    angle_control_saturated = abs(angle_steers_des - CS.steeringAngleDeg) > STEER_ANGLE_SATURATION_THRESHOLD
    angle_log.saturated = bool(self._check_saturation(angle_control_saturated, CS, False, curvature_limited))
    angle_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    angle_log.steeringAngleDesiredDeg = float(angle_steers_des)
    return 0, float(angle_steers_des), angle_log
