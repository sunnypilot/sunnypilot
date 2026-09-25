"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.sunnypilot import get_sanitize_int_param

AccelProfile = custom.LongitudinalPlanSP.AccelController.Profile

MAX_ACCEL_BREAKPOINTS = [0., 3., 5., 10., 20., 25., 40.]  # m/s
MAX_ACCEL_PROFILES = {
  AccelProfile.eco:    [1.60, 1.48, 1.22, 0.86, 0.66, 0.52, 0.40],
  AccelProfile.normal: [1.90, 1.70, 1.42, 0.99, 0.80, 0.66, 0.52],
  AccelProfile.sport:  [2.00, 2.00, 1.86, 1.30, 1.02, 0.86, 0.72],
}
CRUISE_DECEL_RESPONSE_TIME = {  # seconds
  AccelProfile.eco: 4.0,
  AccelProfile.normal: 3.5,
  AccelProfile.sport: 3.0,
}
CRUISE_DECEL_ACCEL = {  # m/s^2; comfort-first cruise deceleration target
  AccelProfile.eco: -0.35,
  AccelProfile.normal: -0.50,
  AccelProfile.sport: -0.65,
}


class AccelController:
  def __init__(self):
    self.params = Params()
    self.update()

  def update(self) -> None:
    self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  @property
  def profile(self) -> int:
    return self._profile

  def is_enabled(self) -> bool:
    return self._enabled

  def get_max_accel(self, v_ego: float) -> float:
    return float(np.interp(max(0.0, v_ego), MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self._profile]))

  def get_cruise_target(self, v_ego: float, v_target: float) -> float:
    if not np.isfinite(v_target) or v_target <= 0.0 or v_target >= v_ego:
      return v_target

    response_time = CRUISE_DECEL_RESPONSE_TIME[self._profile]
    target_delta = v_target - v_ego
    if target_delta < CRUISE_DECEL_ACCEL[self._profile] * response_time * 2.0:
      return v_target
    return float(v_ego + target_delta / response_time)
