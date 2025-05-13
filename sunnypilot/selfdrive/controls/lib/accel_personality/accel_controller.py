"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
from cereal import custom
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.accel_profiles import (
  MAX_ACCEL_ECO, MAX_ACCEL_NORMAL, MAX_ACCEL_SPORT,
  MIN_ACCEL_ECO, MIN_ACCEL_NORMAL, MIN_ACCEL_SPORT, MIN_ACCEL_STOCK,
  MAX_ACCEL_BREAKPOINTS, MIN_ACCEL_BREAKPOINTS
)


AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

def compute_symmetric_slopes(x, y):
  n = len(x)
  m = np.zeros(n)
  for i in range(n):
    if i == 0:
      m[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
    elif i == n-1:
      m[i] = (y[i] - y[i-1]) / (x[i] - x[i-1])
    else:
      m[i] = ((y[i+1] - y[i]) / (x[i+1] - x[i]) + (y[i] - y[i-1]) / (x[i] - x[i-1])) / 2
  return m

def hermite_interpolate(x, xp, yp, slopes):
  x = np.clip(x, xp[0], xp[-1])
  idx = np.searchsorted(xp, x) - 1
  idx = np.clip(idx, 0, len(slopes) - 2)

  x0, x1 = xp[idx], xp[idx+1]
  y0, y1 = yp[idx], yp[idx+1]
  m0, m1 = slopes[idx], slopes[idx+1]

  t = (x - x0) / (x1 - x0)
  h00 = 2*t**3 - 3*t**2 + 1
  h10 = t**3 - 2*t**2 + t
  h01 = -2*t**3 + 3*t**2
  h11 = t**3 - t**2

  return (h00 * y0) + (h10 * (x1 - x0) * m0) + (h01 * y1) + (h11 * (x1 - x0) * m1)

def clamp(val: float, lower: float, upper: float) -> float:
  return max(lower, min(val, upper))

class AccelController:
  def __init__(self):
    self.params = Params()
    self.personality = AccelPersonality.stock
    self.frame = 0

    # Pre-compute slopes for smoother interpolation
    self.max_accel_slopes = {
      'eco': compute_symmetric_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_ECO),
      'normal': compute_symmetric_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_NORMAL),
      'sport': compute_symmetric_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_SPORT)
    }

    self.min_accel_slopes = {
      'eco': compute_symmetric_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_ECO),
      'normal': compute_symmetric_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_NORMAL),
      'sport': compute_symmetric_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_SPORT),
      'stock': compute_symmetric_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_STOCK)
    }

  def _update_personality_from_param(self):
    if self.frame % int(1. / DT_MDL) == 0:
      personality_str = self.params.get("AccelPersonality", encoding='utf-8')
      if personality_str is not None:
        personality_int = int(personality_str)
        if personality_int in [AccelPersonality.stock, AccelPersonality.normal, AccelPersonality.eco, AccelPersonality.sport]:
          self.personality = personality_int

  def _get_max_accel_for_speed(self, v_ego: float) -> float:
    self._update_personality_from_param()

    # Clamp v_ego to valid interpolation range
    v_ego = clamp(v_ego, MAX_ACCEL_BREAKPOINTS[0], MAX_ACCEL_BREAKPOINTS[-1])

    if self.personality == AccelPersonality.eco:
      accel_profile = MAX_ACCEL_ECO
      slopes = self.max_accel_slopes['eco']
    elif self.personality == AccelPersonality.sport:
      accel_profile = MAX_ACCEL_SPORT
      slopes = self.max_accel_slopes['sport']
    else:
      accel_profile = MAX_ACCEL_NORMAL
      slopes = self.max_accel_slopes['normal']

    return float(hermite_interpolate(v_ego, MAX_ACCEL_BREAKPOINTS, accel_profile, slopes))

  def _get_min_accel_for_speed(self, v_ego: float) -> float:
    self._update_personality_from_param()

    # Clamp v_ego to valid interpolation range
    v_ego = clamp(v_ego, MIN_ACCEL_BREAKPOINTS[0], MIN_ACCEL_BREAKPOINTS[-1])

    if self.personality == AccelPersonality.eco:
      accel_profile = MIN_ACCEL_ECO
      slopes = self.min_accel_slopes['eco']
    elif self.personality == AccelPersonality.sport:
      accel_profile = MIN_ACCEL_SPORT
      slopes = self.min_accel_slopes['sport']
    elif self.personality == AccelPersonality.normal:
      accel_profile = MIN_ACCEL_NORMAL
      slopes = self.min_accel_slopes['normal']
    else:
      accel_profile = MIN_ACCEL_STOCK
      slopes = self.min_accel_slopes['stock']

    return float(hermite_interpolate(v_ego, MIN_ACCEL_BREAKPOINTS, accel_profile, slopes))

  def get_accel_limits(self, v_ego: float, accel_limits: list[float]) -> tuple[float, float]:
    self._update_personality_from_param()

    if self.personality == AccelPersonality.stock:
      return (accel_limits[0], accel_limits[1])
    else:
      max_accel = self._get_max_accel_for_speed(v_ego)
      return (accel_limits[0], max_accel)

  def is_personality_enabled(self, accel_personality: int = AccelPersonality.stock) -> bool:
    self.personality = accel_personality
    self._update_personality_from_param()
    return bool(self.personality != AccelPersonality.stock)

  def update(self):
    self.frame += 1
