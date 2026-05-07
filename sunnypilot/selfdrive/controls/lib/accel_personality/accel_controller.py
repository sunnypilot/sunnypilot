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

MAX_ACCEL_BP =             [0.0, 4.0, 8.0, 16., 40.0]  # m/s

MAX_ACCEL_V = {
  AccelPersonality.eco:    [2.00, 1.75, 1.20, 0.50, 0.11],
  AccelPersonality.normal: [2.00, 1.75, 1.35, 0.65, 0.22],
  AccelPersonality.sport:  [2.00, 1.75, 1.40, 0.80, 0.33],
}

JERK_ACCEL_BP = [0.0,  40.0]  # m/s
JERK_ACCEL_V  = {
  AccelPersonality.eco:    [1.50, 0.55],
  AccelPersonality.normal: [1.50, 0.80],
  AccelPersonality.sport:  [1.50, 1.00],
}

COAST_WINDOW_BP = [0.0, 10.0, 20.0, 35.0]  # m/s
COAST_WINDOW_V  = [0.30, 0.55, 0.80, 1.30]  # m/s excess before braking starts

EXCESS_SCALE_BP = [0.0, 10.0, 20.0, 35.0]  # m/s
EXCESS_SCALE_V  = [1.2,  2.5,  4.5,  7.0]

FULL_BRAKE_FLOOR_BP =      [0.0,    5.0,    10.0,   40.0]  # m/s

FULL_BRAKE_FLOOR_V = {
  AccelPersonality.eco:    [-0.001, -0.002, -0.001, -0.30],
  AccelPersonality.normal: [-0.001, -0.003, -0.001, -0.40],
  AccelPersonality.sport:  [-0.002, -0.003, -0.002, -0.55],
}

COAST_FLOOR = {
  AccelPersonality.eco:    -0.02,
  AccelPersonality.normal: -0.04,
  AccelPersonality.sport:  -0.18,
}

JERK_DECEL_BP    = [0.0,  35.0]  # m/s
JERK_DECEL_ONSET = [0.06, 0.03]  # m/s³
JERK_DECEL_EASE  = [0.18, 0.07]  # m/s³
EASE_FEATHER     = 0.60

_RAMP_OFF_START = 5.0   # m/s below cruise where ramp begins
_MIN_MAX_GAP    = 0.05
_PARAM_REFRESH_FRAMES = max(1, int(1.0 / DT_MDL))


class AccelPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.first_run = True

    self._last_max: float = 1.80
    self._last_min: float = -0.03

    self._cache_v: float | None = None
    self._cache_cruise: float | None = None
    self._cache_min: float = -0.03
    self._cache_max: float = 1.80

    val = self.params.get('AccelPersonality')
    self._accel_personality = val if val is not None else AccelPersonality.normal
    self._enabled = self.params.get_bool('AccelPersonalityEnabled')

    self._v_cruise: float = 0.0

  def update(self, sm=None):
    self.frame += 1
    self._cache_v = None
    self._cache_cruise = None

    if sm is not None:
      try:
        self._v_cruise = float(sm['carState'].vCruise) * (1000.0 / 3600.0)
      except Exception:
        pass

    if self.frame % _PARAM_REFRESH_FRAMES == 0:
      val = self.params.get('AccelPersonality')
      self._accel_personality = val if val is not None else AccelPersonality.normal
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
    next_p = ACCEL_PERSONALITY_OPTIONS[(idx + 1) % len(ACCEL_PERSONALITY_OPTIONS)]
    self.set_accel_personality(next_p)
    return int(next_p)

  def _ramp_off_factor(self, v_ego: float) -> float:
    if self._v_cruise <= 0.0:
      return 1.0
    return float(np.clip((self._v_cruise - v_ego) / _RAMP_OFF_START, 0.0, 1.0))

  def _compute_target_min(self, v_ego: float) -> float:
    coast_floor  = COAST_FLOOR[self._accel_personality]
    full_floor   = float(np.interp(v_ego, FULL_BRAKE_FLOOR_BP, FULL_BRAKE_FLOOR_V[self._accel_personality]))
    excess       = max(0.0, v_ego - self._v_cruise)
    coast_window = float(np.interp(v_ego, COAST_WINDOW_BP, COAST_WINDOW_V))

    preload_zone = coast_window * 0.5
    if excess <= preload_zone:
      # continuous ramp from 0 drag at no excess to coast_floor at preload_zone
      t = excess / max(preload_zone, 0.1)
      return coast_floor * t

    if excess <= coast_window:
      return coast_floor

    excess_scale = float(np.interp(v_ego, EXCESS_SCALE_BP, EXCESS_SCALE_V))
    t = float(np.clip((excess - coast_window) / max(excess_scale - coast_window, 0.1), 0.0, 1.0)) ** 2
    return coast_floor + t * (full_floor - coast_floor)

  def _step(self, v_ego: float) -> tuple[float, float]:
    ramp_factor = self._ramp_off_factor(v_ego)
    target_max  = float(np.interp(v_ego, MAX_ACCEL_BP, MAX_ACCEL_V[self._accel_personality])) * ramp_factor

    if v_ego < 5.0 and self._v_cruise > 2.0:
      target_max += 0.25 * (5.0 - v_ego) / 5.0

    target_min = self._compute_target_min(v_ego)

    if self.first_run:
      self._last_max = target_max
      self._last_min = target_min
      self.first_run = False
      return target_min, target_max

    a_rate = float(np.interp(v_ego, JERK_ACCEL_BP, JERK_ACCEL_V[self._accel_personality])) * DT_MDL
    if target_max > self._last_max:
      a_rate *= 0.9
    new_max = float(np.clip(target_max, self._last_max - a_rate, self._last_max + a_rate))

    onset = float(np.interp(v_ego, JERK_DECEL_BP, JERK_DECEL_ONSET))
    ease  = float(np.interp(v_ego, JERK_DECEL_BP, JERK_DECEL_EASE)) * EASE_FEATHER
    delta = target_min - self._last_min
    blend = float(np.clip(abs(delta) / 0.5, 0.0, 1.0))
    d_rate = (onset * blend + ease * (1.0 - blend)) * DT_MDL

    new_min = float(np.clip(target_min, self._last_min - d_rate, self._last_min + d_rate))

    if target_min > self._last_min:
      new_min *= 0.95

    new_min = min(new_min, new_max - _MIN_MAX_GAP)

    self._last_max = new_max
    self._last_min = new_min
    return new_min, new_max

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    v_ego = max(0.0, v_ego)
    if (self._cache_v is not None
        and abs(self._cache_v - v_ego) < 0.01
        and self._cache_cruise == self._v_cruise):
      return self._cache_min, self._cache_max
    self._cache_min, self._cache_max = self._step(v_ego)
    self._cache_v = v_ego
    self._cache_cruise = self._v_cruise
    return self._cache_min, self._cache_max

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
    new_p = personality if personality in ACCEL_PERSONALITY_OPTIONS else AccelPersonality.normal
    self._accel_personality = new_p
    self.params.put('AccelPersonality', new_p)
    self.frame = 0
    self._last_max = 1.80
    self._last_min = -0.03
    self._cache_v = None
    self._cache_cruise = None
    self.first_run = True
