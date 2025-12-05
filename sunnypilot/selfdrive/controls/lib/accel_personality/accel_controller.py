"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom
import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

# Acceleration Profiles
MAX_ACCEL_PROFILES = {
  AccelPersonality.eco:      [1.20, 1.15, 1.05, 0.90, 0.70, 0.52, 0.40, 0.30, 0.20, 0.12],
  AccelPersonality.normal:   [1.80, 1.70, 1.40, 1.24, 1.00, 0.71, 0.58, 0.45, 0.30, 0.17],
  AccelPersonality.sport:    [2.00, 1.95, 1.80, 1.50, 1.25, 1.00, 0.78, 0.58, 0.38, 0.22],
}
MAX_ACCEL_BREAKPOINTS =      [0.,   3.,   5.,   8.,   12.,  18.,  24.,  32.,  42.,  55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-0.50, -0.50, -0.46, -1.20],
  AccelPersonality.normal: [-0.55, -0.55, -0.50, -1.30],
  AccelPersonality.sport:  [-0.54, -0.60, -0.54, -1.40],
}
MIN_ACCEL_BREAKPOINTS =    [0.,    5.,    14.,   25.]


class AccelPersonalityController:

  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.param_keys = {
      'personality': 'AccelPersonality',
      'enabled': 'AccelPersonalityEnabled'
    }
    self._load_personality_from_params()

  def _load_personality_from_params(self):
    try:
      saved = self.params.get(self.param_keys['personality'])
      if saved is not None:
        personality_value = int(saved)
        if personality_value in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
          self.accel_personality = personality_value
        else:
          self.accel_personality = AccelPersonality.normal
    except (ValueError, TypeError):
      self.accel_personality = AccelPersonality.normal

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return
    self._load_personality_from_params()

  def get_accel_personality(self) -> int:
    self._update_from_params()
    return int(self.accel_personality)

  def set_accel_personality(self, personality: int):
    if personality not in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      return

    self.accel_personality = personality
    self.params.put(self.param_keys['personality'], str(personality))

  def cycle_accel_personality(self) -> int:
    personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    current_idx = personalities.index(self.accel_personality)
    next_personality = personalities[(current_idx + 1) % len(personalities)]
    self.set_accel_personality(next_personality)
    return int(next_personality)

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    v_ego = max(0.0, v_ego)

    max_accel = float(np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality]))
    min_accel = float(np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality]))

    return min_accel, max_accel

  def get_min_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[0]

  def get_max_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[1]

  def is_enabled(self) -> bool:
    return self.params.get_bool(self.param_keys['enabled'])

  def set_enabled(self, enabled: bool):
    self.params.put_bool(self.param_keys['enabled'], enabled)

  def toggle_enabled(self) -> bool:
    current = self.is_enabled()
    self.set_enabled(not current)
    return not current

  def reset(self):
    self.accel_personality = AccelPersonality.normal
    self.frame = 0

  def update(self):
    self.frame += 1
    self._update_from_params()
