"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log, custom
import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

LongPersonality = log.LongitudinalPersonality
AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

MAX_ACCEL_PROFILES = {
  AccelPersonality.eco:       [2.0,  1.99,  1.88, 1.10, .500, .292, .15, .10],
  AccelPersonality.normal:    [2.0,  2.00,  1.94, 1.22, .635, .33, .20, .16],
  AccelPersonality.sport:     [2.0,  2.00,  2.00, 1.85, .800, .54, .32, .22],
}
MAX_ACCEL_BREAKPOINTS = [0., 4., 6., 9., 16., 25., 30., 55.]

MIN_ACCEL_PROFILES = {
  LongPersonality.relaxed:    [-.0007, -.0007, -.07, -1.00, -1.00],
  LongPersonality.standard:   [-.0007, -.0007, -.08, -1.10, -1.10],
  LongPersonality.aggressive: [-.0006, -.0007, -.09, -1.20, -1.20],
}
MIN_ACCEL_BREAKPOINTS = [0., 3.0, 11., 22., 50.]


class AccelPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.long_personality = LongPersonality.standard

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return
    accel_bytes = self.params.get('AccelPersonality')
    if accel_bytes:
      self.accel_personality = int(accel_bytes)
    long_bytes = self.params.get('LongitudinalPersonality')
    if long_bytes:
      self.long_personality = int(long_bytes)

  def is_enabled(self) -> bool:
    return self.params.get_bool('VibeAccelPersonalityEnabled') or False

  def set_accel_personality(self, personality: int) -> bool:
    if personality not in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      return False
    self.accel_personality = personality
    self.params.put('AccelPersonality', str(personality))
    return True

  def cycle_accel_personality(self) -> int:
    personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    idx = personalities.index(self.accel_personality)
    next_p = personalities[(idx + 1) % len(personalities)]
    self.set_accel_personality(next_p)
    return int(next_p)

  def get_accel_limits(self, v_ego: float) -> tuple[float, float] | None:
    if not self.is_enabled():
      return None
    self._update_from_params()
    max_a = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
    min_a = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.long_personality])
    return float(min_a), float(max_a)

  def update(self):
    self.frame += 1