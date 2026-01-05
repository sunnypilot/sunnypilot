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
ACCEL_PERSONALITY_OPTIONS = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]

# Acceleration Profiles
MAX_ACCEL_PROFILES = {
  AccelPersonality.eco:      [1.30, 1.25, 1.15, 0.69, 0.58, 0.52, 0.28, 0.107, 0.08, 0.06],
  AccelPersonality.normal:   [1.85, 1.80, 1.55, 0.94, 0.72, 0.58, 0.34, 0.120, 0.09, 0.07],
  AccelPersonality.sport:    [2.00, 1.95, 1.80, 1.06, 0.81, 0.69, 0.42, 0.160, 0.10, 0.08],
}
MAX_ACCEL_BREAKPOINTS =      [0.,   3.,   5.,   8.,   12.,  18.,  24.,  32.,  42.,  55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-.003, -0.4, -0.6, -0.5, -1.2, -1.2],
  AccelPersonality.normal: [-.004, -0.5, -0.7, -0.6, -1.2, -1.3],
  AccelPersonality.sport:  [-0.50, -0.6, -0.8, -0.7, -1.3, -1.4],
}
MIN_ACCEL_BREAKPOINTS =    [3,     5.,   7.,   9.,   14.,   25]


DECEL_SMOOTH_ALPHA = 0.20  # Very aggressive smoothing for decel (lower = smoother)
ACCEL_SMOOTH_ALPHA = 0.75  # Less aggressive for accel (higher = more responsive)

# Asymmetric rate limiting
MAX_DECEL_INCREASE_RATE = 1.3  # When braking harder (m/s² per second)
MAX_DECEL_DECREASE_RATE = 1.0  # When releasing brake (m/s² per second)


class AccelPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
    self._accel_personality = self.params.get('AccelPersonality') or AccelPersonality.normal
    self._enabled = self.params.get_bool('AccelPersonalityEnabled')

  def update(self, sm=None):
    self.frame += 1
    if self.frame % int(1.0 / DT_MDL) == 0:
      self._accel_personality = self.params.get('AccelPersonality') or AccelPersonality.normal
      self._enabled = self.params.get_bool('AccelPersonalityEnabled')

  @property
  def accel_personality(self) -> int:
    return self._accel_personality

  def get_accel_personality(self) -> int:
    return int(self._accel_personality)

  def set_accel_personality(self, personality: int):
    if personality in ACCEL_PERSONALITY_OPTIONS:
      self._accel_personality = personality
      self.params.put('AccelPersonality', personality)

  def cycle_accel_personality(self) -> int:
    current = self._accel_personality
    next_personality = ACCEL_PERSONALITY_OPTIONS[(ACCEL_PERSONALITY_OPTIONS.index(current) + 1) % len(ACCEL_PERSONALITY_OPTIONS)]
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
    self.last_max_accel = ACCEL_SMOOTH_ALPHA * target_max + (1 - ACCEL_SMOOTH_ALPHA) * self.last_max_accel
    smoothed_decel = DECEL_SMOOTH_ALPHA * target_min + (1 - DECEL_SMOOTH_ALPHA) * self.last_min_accel

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
    return self._enabled

  def set_enabled(self, enabled: bool):
    self._enabled = enabled
    self.params.put_bool('AccelPersonalityEnabled', enabled)

  def toggle_enabled(self) -> bool:
    current = self._enabled
    self.set_enabled(not current)
    return not current

  def reset(self):
    self._accel_personality = AccelPersonality.normal
    self.params.put('AccelPersonality', AccelPersonality.normal)
    self.frame = 0
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
