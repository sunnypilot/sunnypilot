"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log
import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

LongPersonality = log.LongitudinalPersonality

FOLLOW_PROFILES = {
  LongPersonality.relaxed:    [1.55, 1.65, 1.65, 1.80, 1.80],
  LongPersonality.standard:   [1.35, 1.45, 1.45, 1.55, 1.55],
  LongPersonality.aggressive: [1.05, 1.10, 1.10, 1.25, 1.35],
}
FOLLOW_BREAKPOINTS = [0., 6., 18., 20., 36.]


class FollowPersonalityController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.long_personality = LongPersonality.standard

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return
    long_bytes = self.params.get('LongitudinalPersonality')
    if long_bytes:
      self.long_personality = int(long_bytes)

  def is_enabled(self) -> bool:
    return self.params.get_bool('VibeFollowPersonalityEnabled') or False

  def get_follow_distance_multiplier(self, v_ego: float) -> float | None:
    if not self.is_enabled():
      return None
    self._update_from_params()
    return float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.long_personality]))

  def update(self):
    self.frame += 1