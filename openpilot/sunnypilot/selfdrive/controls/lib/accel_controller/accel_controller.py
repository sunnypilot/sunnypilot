"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot import get_sanitize_int_param

AccelProfile = custom.LongitudinalPlanSP.AccelController.Profile

MAX_ACCEL_PROFILES = {
  AccelProfile.eco:    [1.45, 1.40, 1.20, 0.85, 0.62, 0.36, 0.22, 0.085, 0.055, 0.045],
  AccelProfile.normal: [2.00, 1.95, 1.80, 1.06, 0.81, 0.69, 0.42, 0.160, 0.10, 0.08],
  AccelProfile.sport:  [2.00, 1.99, 1.95, 1.45, 1.10, 0.82, 0.53, 0.240, 0.13, 0.09],
}
MAX_ACCEL_BREAKPOINTS = [0., 3., 5., 8., 12., 18., 24., 32., 42., 55.]

MIN_ACCEL_PROFILES = {
  AccelProfile.eco:    [-0.90, -0.95, -1.00, -1.10, -1.2],
  AccelProfile.normal: [-1.00, -1.05, -1.10, -1.20, -1.3],
  AccelProfile.sport:  [-1.10, -1.15, -1.20, -1.30, -1.4],
}
MIN_ACCEL_BREAKPOINTS = [3., 4.5, 7., 9., 25.]

ACCEL_SMOOTH_ALPHA = 0.90
DECEL_SMOOTH_ALPHA = 0.40

class AccelController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
    self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  def update(self, sm=None) -> None:
    self.frame += 1
    if self.frame % int(1.0 / DT_MDL) == 0:
      self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
      self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  @property
  def profile(self) -> int:
    return self._profile

  def is_enabled(self) -> bool:
    return self._enabled

  def get_max_accel(self, v_ego: float) -> float:
    v_ego = max(0.0, v_ego)
    target_max = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self._profile])

    if self.first_run:
      self.last_max_accel = target_max
      self.first_run = False
      return float(target_max)

    self.last_max_accel = ACCEL_SMOOTH_ALPHA * target_max + (1 - ACCEL_SMOOTH_ALPHA) * self.last_max_accel
    return float(self.last_max_accel)

  def get_min_accel(self, v_ego: float) -> float:
    v_ego = max(0.0, v_ego)
    target_min = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self._profile])
    self.last_min_accel = DECEL_SMOOTH_ALPHA * target_min + (1 - DECEL_SMOOTH_ALPHA) * self.last_min_accel
    self.last_min_accel = min(self.last_min_accel, self.last_max_accel - 0.1)
    return float(self.last_min_accel)
