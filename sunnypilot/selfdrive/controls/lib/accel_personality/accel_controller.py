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
  AccelPersonality.eco:       [1.85, 1.65, 1.40, 0.98, 0.68, 0.56, 0.34, 0.09, 0.07],
  AccelPersonality.normal:    [2.00, 2.00, 1.70, 1.18, 0.85, 0.68, 0.40, 0.12, 0.08],
  AccelPersonality.sport:     [2.00, 2.00, 2.00, 1.60, 1.20, 0.95, 0.56, 0.16, 0.10],
}
MAX_ACCEL_BREAKPOINTS =       [0.0,  3.0,  5.0,  8.0,  12.0, 18.0, 24.0, 32.0, 42.0]

# Decel profiles
MIN_ACCEL_BREAKPOINTS =       [0.0,   1.0,   2.0,   4.0,   7.0,   11.0,  16.0,  22.0,  25.0]
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:       [-0.001,-0.001,-0.08, -0.18, -0.25, -0.30, -0.35, -0.40, -0.44],
  AccelPersonality.normal:    [-0.001,-0.001,-0.10, -0.21, -0.29, -0.35, -0.41, -0.47, -0.51],
  AccelPersonality.sport:     [-0.002,-0.002,-0.13, -0.25, -0.34, -0.41, -0.47, -0.53, -0.58],
}

ACCEL_ALPHA_BASE = 0.75
ACCEL_ALPHA_MAX  = 0.92
ACCEL_ALPHA_SCALE = 0.9
DECEL_ALPHA_BASE  = 0.78
DECEL_ALPHA_MIN   = 0.60
DECEL_ALPHA_SCALE = -0.4
MAX_DECEL_INCREASE_RATE = 0.07   # m/s³
MAX_DECEL_DECREASE_RATE = 0.50   # m/s³

_MIN_MAX_GAP = 0.05  # m/s²


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
    if self.frame % max(1, int(1.0 / DT_MDL)) == 0:
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
    idx = ACCEL_PERSONALITY_OPTIONS.index(current) if current in ACCEL_PERSONALITY_OPTIONS else 0
    next_personality = ACCEL_PERSONALITY_OPTIONS[(idx + 1) % len(ACCEL_PERSONALITY_OPTIONS)]
    self.set_accel_personality(next_personality)
    return int(next_personality)

  @staticmethod
  def _adaptive_alpha(current: float, target: float, base: float, limit: float, scale: float) -> float:
    error = abs(target - current)
    raw = base + error * scale
    lo, hi = (base, limit) if limit >= base else (limit, base)
    return float(np.clip(raw, lo, hi))

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    v_ego = max(0.0, v_ego)
    target_max = float(np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality]))
    target_min = float(np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality]))

    if self.first_run:
      self.last_max_accel = target_max
      self.last_min_accel = target_min
      self.first_run = False
      return float(target_min), float(target_max)

    # Adaptive accel smoothing
    accel_alpha = self._adaptive_alpha(self.last_max_accel, target_max, ACCEL_ALPHA_BASE, ACCEL_ALPHA_MAX, ACCEL_ALPHA_SCALE)
    self.last_max_accel = accel_alpha * self.last_max_accel + (1.0 - accel_alpha) * target_max

    # Adaptive decel smoothing
    decel_alpha = self._adaptive_alpha(self.last_min_accel, target_min, DECEL_ALPHA_BASE, DECEL_ALPHA_MIN, DECEL_ALPHA_SCALE)
    smoothed_decel = decel_alpha * self.last_min_accel + (1.0 - decel_alpha) * target_min

    raw_change = smoothed_decel - self.last_min_accel
    limit_per_step = (MAX_DECEL_INCREASE_RATE if raw_change < 0 else MAX_DECEL_DECREASE_RATE) * DT_MDL
    self.last_min_accel += float(np.clip(raw_change, -limit_per_step, limit_per_step))

    self.last_min_accel = min(self.last_min_accel, self.last_max_accel - _MIN_MAX_GAP)

    return float(self.last_min_accel), float(self.last_max_accel)

  def get_min_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[0]

  def get_max_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[1]

  def is_enabled(self) -> bool:
    return self._enabled

  def set_enabled(self, enabled: bool):
    self._enabled = bool(enabled)
    self.params.put_bool('AccelPersonalityEnabled', self._enabled)

  def toggle_enabled(self) -> bool:
    self.set_enabled(not self._enabled)
    return self._enabled

  def reset(self, personality: int = None):
    new_personality = personality if personality in ACCEL_PERSONALITY_OPTIONS else AccelPersonality.normal
    self._accel_personality = new_personality
    self.params.put('AccelPersonality', new_personality)
    self.frame = 0
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
