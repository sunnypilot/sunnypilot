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


A_MAX_BP = [0.0, 4.0, 8.0, 16.0, 40.0]
A_MAX_V = {
  AccelPersonality.eco:    [1.80, 1.80, 1.20, 0.40, 0.08],
  AccelPersonality.normal: [1.80, 1.80, 1.35, 0.50, 0.15],
  AccelPersonality.sport:  [1.80, 1.80, 1.50, 0.70, 0.25],
}

COAST_DRAG_BP = [0.0, 10.0, 25.0, 40.0]
COAST_DRAG_V = {
  AccelPersonality.eco:    [-0.03, -0.05, -0.08, -0.12],
  AccelPersonality.normal: [-0.04, -0.07, -0.12, -0.18],
  AccelPersonality.sport:  [-0.06, -0.10, -0.18, -0.28],
}

A_MIN_FLOOR_BP = [0.0, 5.0, 15.0, 40.0]
A_MIN_FLOOR_V = {
  AccelPersonality.eco:    [-0.20, -0.35, -0.55, -0.50],
  AccelPersonality.normal: [-0.25, -0.45, -0.75, -0.65],
  AccelPersonality.sport:  [-0.35, -0.65, -1.00, -0.95],
}

DEFICIT_TO_FLOOR = 8.5
COAST_DEADBAND = 1.0
RAMP_OFF_RANGE = 5.0

A_MIN_TIGHTEN_RATE = 1.5
A_MIN_RELAX_RATE = 0.6
A_MAX_RATE = 0.8

MIN_MAX_GAP = 0.05

PARAM_REFRESH_FRAMES = max(1, int(1.0 / DT_MDL))


class AccelPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self._first = True

    val = self.params.get('AccelPersonality')
    self._personality = val if val is not None else AccelPersonality.normal
    self._enabled = self.params.get_bool('AccelPersonalityEnabled')

    self._v_cruise = 0.0
    self._a_min = -0.05
    self._a_max = 1.50

    self._cache_v: float | None = None
    self._cache_v_cruise: float | None = None
    self._cache_a_min = self._a_min
    self._cache_a_max = self._a_max

  def update(self, sm=None):
    self.frame += 1
    self._cache_v = None
    self._cache_v_cruise = None

    if sm is not None:
      try:
        self._v_cruise = float(sm['carState'].vCruise) * (1000.0 / 3600.0)
      except Exception:
        pass

    if self.frame % PARAM_REFRESH_FRAMES == 0:
      val = self.params.get('AccelPersonality')
      self._personality = val if val is not None else AccelPersonality.normal
      self._enabled = self.params.get_bool('AccelPersonalityEnabled')

  @property
  def accel_personality(self) -> int:
    return self._personality

  def get_accel_personality(self) -> int:
    return int(self._personality)

  def set_accel_personality(self, personality: int):
    if personality in ACCEL_PERSONALITY_OPTIONS:
      self._personality = personality
      self.params.put('AccelPersonality', personality)

  def cycle_accel_personality(self) -> int:
    idx = ACCEL_PERSONALITY_OPTIONS.index(self._personality) if self._personality in ACCEL_PERSONALITY_OPTIONS else 0
    nxt = ACCEL_PERSONALITY_OPTIONS[(idx + 1) % len(ACCEL_PERSONALITY_OPTIONS)]
    self.set_accel_personality(nxt)
    return int(nxt)

  def is_enabled(self) -> bool:
    return self._enabled

  def set_enabled(self, enabled: bool):
    self._enabled = bool(enabled)
    self.params.put_bool('AccelPersonalityEnabled', self._enabled)

  def toggle_enabled(self) -> bool:
    self.set_enabled(not self._enabled)
    return self._enabled

  def reset(self, personality: int | None = None):
    if personality is None or personality not in ACCEL_PERSONALITY_OPTIONS:
      personality = AccelPersonality.normal
    self._personality = personality
    self.params.put('AccelPersonality', self._personality)
    self.frame = 0
    self._first = True
    self._a_min = -0.05
    self._a_max = 1.50
    self._cache_v = None
    self._cache_v_cruise = None

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    v_ego = max(0.0, v_ego)
    if (self._cache_v is not None
        and abs(self._cache_v - v_ego) < 0.01
        and self._cache_v_cruise == self._v_cruise):
      return self._cache_a_min, self._cache_a_max
    self._cache_a_min, self._cache_a_max = self._step(v_ego)
    self._cache_v = v_ego
    self._cache_v_cruise = self._v_cruise
    return self._cache_a_min, self._cache_a_max

  def get_min_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[0]

  def get_max_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[1]

  def _ramp_off(self, v_ego: float) -> float:
    if self._v_cruise <= 0.0:
      return 1.0
    return float(np.clip((self._v_cruise - v_ego) / RAMP_OFF_RANGE, 0.0, 1.0))

  def _target_max(self, v_ego: float) -> float:
    base = float(np.interp(v_ego, A_MAX_BP, A_MAX_V[self._personality]))
    return base * self._ramp_off(v_ego)

  def _target_min(self, v_ego: float) -> float:
    coast = float(np.interp(v_ego, COAST_DRAG_BP, COAST_DRAG_V[self._personality]))
    if self._v_cruise <= 0.0 or v_ego >= self._v_cruise:
      return coast
    floor = float(np.interp(v_ego, A_MIN_FLOOR_BP, A_MIN_FLOOR_V[self._personality]))
    deficit = self._v_cruise - v_ego
    t = float(np.clip(deficit / DEFICIT_TO_FLOOR, 0.0, 1.0)) ** 1.5
    return coast + t * (floor - coast)

  def _apply_coast_deadband(self, v_ego: float, t_min: float, t_max: float) -> tuple[float, float]:
    if self._v_cruise <= 0.0 or abs(v_ego - self._v_cruise) >= COAST_DEADBAND:
      return t_min, t_max
    coast = float(np.interp(v_ego, COAST_DRAG_BP, COAST_DRAG_V[self._personality]))
    return coast, max(0.05, t_max * 0.25)

  def _rate_limit(self, last: float, target: float, rate_down: float, rate_up: float) -> float:
    rate = rate_up if target > last else rate_down
    step = rate * DT_MDL
    return float(np.clip(target, last - step, last + step))

  def _step(self, v_ego: float) -> tuple[float, float]:
    t_max = self._target_max(v_ego)
    t_min = self._target_min(v_ego)
    t_min, t_max = self._apply_coast_deadband(v_ego, t_min, t_max)

    if self._first:
      self._a_min, self._a_max = t_min, t_max
      self._first = False
      return self._a_min, self._a_max

    new_min = self._rate_limit(self._a_min, t_min, rate_down=A_MIN_TIGHTEN_RATE, rate_up=A_MIN_RELAX_RATE)
    new_max = self._rate_limit(self._a_max, t_max, rate_down=A_MAX_RATE, rate_up=A_MAX_RATE)

    new_min = min(new_min, new_max - MIN_MAX_GAP)

    self._a_min, self._a_max = new_min, new_max
    return self._a_min, self._a_max
