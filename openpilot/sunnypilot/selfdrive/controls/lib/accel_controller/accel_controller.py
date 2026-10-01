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

MAX_ACCEL_BREAKPOINTS = [0., 3., 12,  24., 36.]  # m/s
MAX_ACCEL_PROFILES = {
  AccelProfile.eco:    [1.85, 1.72, 0.65, 0.32, 0.23],
  AccelProfile.normal: [1.95, 1.80, 0.82, 0.44, 0.31],
  AccelProfile.sport:  [2.00, 2.00, 1.20, 0.70, 0.50],
}
ECO_ENGINE_OFF_BP = [0., 3., 12., 16.67, 19.44, 22.22, 24., 36.]  # m/s
ECO_ENGINE_OFF_MAX_ACCEL = [1.85, 1.55, 0.35, 0.25, 0.16, 0.12, 0.08, 0.06]

CRUISE_DECEL_RESPONSE_TIME = {
  AccelProfile.normal: 3.5,
  AccelProfile.sport: 3.0,
}
CRUISE_DECEL_ACCEL = {
  AccelProfile.normal: -0.50,
  AccelProfile.sport: -0.65,
}
ECO_CRUISE_DECEL_BP = [0., 16.67, 19.44, 25.0, 33.3]  # m/s
ECO_CRUISE_DECEL_V = [-0.40, -0.40, -0.22, -0.30, -0.40]  # m/s^2
ECO_COAST_BLEND_BP = [16.67, 19.44]  # m/s
ECO_COAST_MIN, ECO_COAST_MAX = -1.2, -0.05  # m/s^2
CRUISE_DECEL_TAPER_TIME = 1.0  # s


class AccelController:
  def __init__(self):
    self.params = Params()
    self._cruise_decel: float | None = None
    self._cruise_decel_target: float | None = None
    self.update()

  def update(self) -> None:
    self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  @property
  def profile(self) -> int:
    return self._profile

  def is_enabled(self) -> bool:
    return self._enabled

  def get_max_accel(self, v_ego: float, engine_off: bool = False) -> float:
    if engine_off and self._profile == AccelProfile.eco:
      return float(np.interp(max(0.0, v_ego), ECO_ENGINE_OFF_BP, ECO_ENGINE_OFF_MAX_ACCEL))
    return float(np.interp(max(0.0, v_ego), MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self._profile]))

  def get_cruise_target(self, v_ego: float, v_target: float, accel_coast: float | None = None) -> float:
    if not np.isfinite(v_target) or v_target <= 0.0 or v_target >= v_ego:
      self._cruise_decel = None
      self._cruise_decel_target = None
      return v_target

    target_delta = v_target - v_ego
    if self._profile == AccelProfile.eco:
      decel = float(np.interp(v_ego, ECO_CRUISE_DECEL_BP, ECO_CRUISE_DECEL_V))
      if accel_coast is not None and np.isfinite(accel_coast) and accel_coast < 0.0:
        coast = float(np.clip(accel_coast, ECO_COAST_MIN, ECO_COAST_MAX))
        w = float(np.interp(v_ego, ECO_COAST_BLEND_BP, [0.0, 1.0]))
        decel = (1.0 - w) * ECO_CRUISE_DECEL_V[1] + w * coast
    else:
      if self._cruise_decel is None or self._cruise_decel_target != v_target:
        self._cruise_decel = min(CRUISE_DECEL_ACCEL[self._profile], target_delta / CRUISE_DECEL_RESPONSE_TIME[self._profile])
        self._cruise_decel_target = v_target
      decel = self._cruise_decel

    decel = max(decel, target_delta / CRUISE_DECEL_TAPER_TIME)
    return float(v_ego + decel)
