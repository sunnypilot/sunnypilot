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
  AccelPersonality.eco:      [1.30, 1.25, 1.15, 0.83, 0.65, 0.51, 0.30, 0.12, 0.08, 0.06],
  AccelPersonality.normal:   [1.80, 1.76, 1.48, 0.88, 0.73, 0.58, 0.40, 0.15, 0.09, 0.07],
  AccelPersonality.sport:    [2.00, 1.95, 1.80, 0.93, 0.81, 0.69, 0.50, 0.21, 0.10, 0.08],
}
MAX_ACCEL_BREAKPOINTS =      [0.,   3.,   5.,   8.,   12.,  18.,  24.,  32.,  42.,  55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-.68, -1.20],
  AccelPersonality.normal: [-.74, -1.30],
  AccelPersonality.sport:  [-.80, -1.40],
}
MIN_ACCEL_BREAKPOINTS =    [7.5,    18.]


DECEL_SMOOTH_ALPHA = 0.55  # Very aggressive smoothing for decel (lower = smoother)
ACCEL_SMOOTH_ALPHA = 0.65  # Less aggressive for accel (higher = more responsive)

# Asymmetric rate limiting
MAX_DECEL_INCREASE_RATE = 1.5  # When braking harder (m/s² per second)
MAX_DECEL_DECREASE_RATE = 0.5  # When releasing brake (m/s² per second)

class AccelPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
    self.param_keys = {'personality': 'AccelPersonality', 'enabled': 'AccelPersonalityEnabled'}
    self._load_personality_from_params()

  def _load_personality_from_params(self):
    try:
      saved = self.params.get(self.param_keys['personality'])
      if saved is not None:
        val = int(saved)
        if val in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
          self.accel_personality = val
    except (ValueError, TypeError):
      pass

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) == 0:
      self._load_personality_from_params()

  def update(self, sm=None):
    self.frame += 1
    self._update_from_params()

  def get_accel_personality(self) -> int:
    self._update_from_params()
    return int(self.accel_personality)

  def set_accel_personality(self, personality: int):
    if personality in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      self.accel_personality = personality
      self.params.put(self.param_keys['personality'], str(personality))

  def cycle_accel_personality(self) -> int:
    personality = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    next_personality = personality[(personality.index(self.accel_personality) + 1) % len(personality)]
    self.set_accel_personality(next_personality)
    return int(next_personality)

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    v_ego = max(0.0, v_ego)
    target_max = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
    target_min = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality])

    if self.first_run:
      self.last_max_accel, self.last_min_accel = target_max, target_min
      self.first_run = False
      return float(target_min), float(target_max)

    # Smoothing
    self.last_max_accel = (ACCEL_SMOOTH_ALPHA * target_max + (1 - ACCEL_SMOOTH_ALPHA) * self.last_max_accel)
    smoothed_decel = (DECEL_SMOOTH_ALPHA * target_min + (1 - DECEL_SMOOTH_ALPHA) * self.last_min_accel)

    # Rate Limiting (Asymmetric)
    raw_change = smoothed_decel - self.last_min_accel

    if raw_change < 0:
      limit = MAX_DECEL_INCREASE_RATE * DT_MDL
      decel_change = np.clip(raw_change, -limit, limit)
    else:
      limit = MAX_DECEL_DECREASE_RATE * DT_MDL
      decel_change = np.clip(raw_change, -limit, limit)

    self.last_min_accel += decel_change

    # Dynamic Safety Corridor: Ensure min is always strictly less than max.
    # We maintain a gap of at least 0.1, or 5% of the current max acceleration.
    # This scaling gap prevents solver crashes at high acceleration values.
    gap = max(0.1, abs(self.last_max_accel) * 0.05)

    if self.last_min_accel > self.last_max_accel - gap:
      self.last_min_accel = self.last_max_accel - gap

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
