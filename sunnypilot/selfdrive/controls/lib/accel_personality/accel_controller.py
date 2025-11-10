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
  AccelPersonality.eco:      [1.96, 1.96, 1.68, .660, .540, .32, .23, .110],
  AccelPersonality.normal:   [1.98, 1.98, 1.78, .730, .570, .38, .27, .155],
  AccelPersonality.sport:    [2.00, 2.00, 1.90, .960, .800, .60, .40, .200],
}
MAX_ACCEL_BREAKPOINTS =      [0.,  4.,   6.,   9.,   16.,  25., 30., 55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-0.02, -1.20, -1.20],
  AccelPersonality.normal: [-0.03, -1.30, -1.30],
  AccelPersonality.sport:  [-1.20, -1.40, -1.40],
}
MIN_ACCEL_BREAKPOINTS =    [5.,    14.,   36.]


DECEL_SMOOTH_ALPHA = 0.03  # Very aggressive smoothing for decel (lower = smoother)
ACCEL_SMOOTH_ALPHA = 0.50  # Less aggressive for accel (higher = more responsive)

# Asymmetric rate limiting
MAX_DECEL_INCREASE_RATE = 0.1  # When braking harder (m/s² per second)
MAX_DECEL_DECREASE_RATE = 0.30  # When releasing brake (m/s² per second)


class AccelPersonalityController:

  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
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
    target_max_accel = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
    target_min_accel = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality])

    if self.first_run:
      self.last_max_accel = target_max_accel
      self.last_min_accel = target_min_accel
      self.first_run = False
      return float(target_min_accel), float(target_max_accel)

    # exponential smoothing to max accel
    self.last_max_accel = (ACCEL_SMOOTH_ALPHA * target_max_accel + (1 - ACCEL_SMOOTH_ALPHA) * self.last_max_accel)

    # VERY aggressive smoothing to min accel for ultra-smooth braking
    smoothed_decel = (DECEL_SMOOTH_ALPHA * target_min_accel + (1 - DECEL_SMOOTH_ALPHA) * self.last_min_accel)

    # asymmetric rate limiting
    decel_change = smoothed_decel - self.last_min_accel
    if decel_change < 0:
      max_change_per_step = MAX_DECEL_INCREASE_RATE * DT_MDL
    else:
      max_change_per_step = MAX_DECEL_DECREASE_RATE * DT_MDL

    decel_change = np.clip(decel_change, -max_change_per_step, max_change_per_step)
    self.last_min_accel = self.last_min_accel + decel_change

    if self.last_min_accel > self.last_max_accel:
      self.last_min_accel = self.last_max_accel - 0.1

    return float(self.last_min_accel), float(self.last_max_accel)

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
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True

  def update(self):
    self.frame += 1
    self._update_from_params()