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

MAX_ACCEL_BREAKPOINTS = [0., 3., 12., 16.67, 19.44, 22.22, 24., 36.]  # m/s
MAX_ACCEL_PROFILES = {
  AccelProfile.eco:    [1.70, 1.38, 0.40, 0.30, 0.245, 0.19, 0.15, 0.10],
  AccelProfile.normal: [1.80, 1.55, 0.55, 0.48, 0.43, 0.39, 0.36, 0.25],
  AccelProfile.sport:  [2.00, 2.00, 1.20, 1.00, 0.89, 0.78, 0.70, 0.50],
}

ECO_ENGINE_OFF_MAX_ACCEL = [1.70, 1.38, 0.40, 0.25, 0.16, 0.12, 0.08, 0.06]
ECO_NO_LEAD_FACTOR_BP = [3.0, 8.0]  # m/s
ECO_NO_LEAD_FACTOR_V = [1.0, 0.85]

CRUISE_DECEL_RESPONSE_TIME = {
  AccelProfile.normal: 3.5,
  AccelProfile.sport: 3.0,
}
CRUISE_DECEL_ACCEL = {  # m/s^2;
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
    self._cruise_decel_profile: int | None = None
    self.update()

  def update(self) -> None:
    self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  @property
  def profile(self) -> int:
    return self._profile

  def is_enabled(self) -> bool:
    return self._enabled

  def get_max_accel(self, v_ego: float, engine_off: bool = False, has_lead: bool = True) -> float:
    profile = ECO_ENGINE_OFF_MAX_ACCEL if (engine_off and self._profile == AccelProfile.eco) else MAX_ACCEL_PROFILES[self._profile]
    max_accel = float(np.interp(max(0.0, v_ego), MAX_ACCEL_BREAKPOINTS, profile))
    if self._profile == AccelProfile.eco and not has_lead:
      max_accel *= float(np.interp(v_ego, ECO_NO_LEAD_FACTOR_BP, ECO_NO_LEAD_FACTOR_V))
    return max_accel

  def get_cruise_target(self, v_ego: float, v_target: float, accel_coast: float | None = None) -> float:
    if not np.isfinite(v_target) or v_target <= 0.0 or v_target >= v_ego:
      self._cruise_decel = None
      self._cruise_decel_target = None
      self._cruise_decel_profile = None
      return v_target

    target_delta = v_target - v_ego
    if self._profile == AccelProfile.eco:
      decel = float(np.interp(v_ego, ECO_CRUISE_DECEL_BP, ECO_CRUISE_DECEL_V))
      if accel_coast is not None and np.isfinite(accel_coast) and accel_coast < 0.0:
        coast = float(np.clip(accel_coast, ECO_COAST_MIN, ECO_COAST_MAX))
        w = float(np.interp(v_ego, ECO_COAST_BLEND_BP, [0.0, 1.0]))
        decel = (1.0 - w) * ECO_CRUISE_DECEL_V[1] + w * coast
    else:
      if (self._cruise_decel is None or self._cruise_decel_target != v_target
          or self._cruise_decel_profile != self._profile):
        self._cruise_decel = min(CRUISE_DECEL_ACCEL[self._profile], target_delta / CRUISE_DECEL_RESPONSE_TIME[self._profile])
        self._cruise_decel_target = v_target
        self._cruise_decel_profile = self._profile
      decel = self._cruise_decel

    # Both values are negative; max selects the gentler taper as the target approaches.
    decel = max(decel, target_delta / CRUISE_DECEL_TAPER_TIME)
    return float(v_ego + decel)
