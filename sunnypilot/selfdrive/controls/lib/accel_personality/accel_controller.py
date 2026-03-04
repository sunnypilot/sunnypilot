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
  AccelPersonality.eco:       [1.85, 1.80, 1.55, 0.94, 0.72, 0.58, 0.34, 0.11, 0.08, 0.07],
  AccelPersonality.normal:    [2.00, 1.95, 1.60, 1.06, 0.81, 0.69, 0.42, 0.13, 0.09, 0.08],
  AccelPersonality.sport:     [2.00, 1.99, 1.65, 1.38, 1.10, 0.82, 0.53, 0.18, 0.10, 0.09],
}
MAX_ACCEL_BREAKPOINTS =       [0.0,  3.0,  5.0,  8.0,  12.0, 18.0, 24.0, 32.0, 42.0, 55.0]

MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:       [-0.0022, -0.0600, -0.0060, -0.007, -0.16, -0.30, -1.20],
  AccelPersonality.normal:    [-0.0023, -0.0700, -0.0070, -0.008, -0.17, -0.31, -1.25],
  AccelPersonality.sport:     [-0.0024, -0.0800, -0.0080, -0.009, -0.18, -0.32, -1.30],
}
MIN_ACCEL_BREAKPOINTS =       [2.0,     4.0,    5.0,     10.0,  16.0,  22.0,  40.0]

ACCEL_ALPHA_BASE = 0.30   # responsive for small corrections
ACCEL_ALPHA_MAX = 0.85    # smooth for big transitions
ACCEL_ALPHA_SCALE = 0.8   # How fast alpha grows with error


DECEL_ALPHA_BASE = 0.85   # smooth even for small changes
DECEL_ALPHA_MIN = 0.15    # responsive
DECEL_ALPHA_SCALE = -1.0  # decel gets more responsive as error grows

MAX_DECEL_INCREASE_RATE = 0.5  # slow brake onset for coast feel (m/s² per second)
MAX_DECEL_DECREASE_RATE = 0.8  # faster brake release (m/s² per second)

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
    self.set_accel_personality(next_personality)  # BUG FIX: was self.set_personality()
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
