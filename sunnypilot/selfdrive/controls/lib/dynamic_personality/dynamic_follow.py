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

# Follow distance profiles mapped to LongPersonality
FOLLOW_PROFILES = {
  LongPersonality.relaxed:    [1.55, 1.65, 1.65, 1.80],
  LongPersonality.standard:   [1.45, 1.45, 1.45, 1.55],
  LongPersonality.aggressive: [1.20, 1.25, 1.28, 1.35],
}
FOLLOW_BREAKPOINTS = [0., 6., 18., 36.]


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.personality = LongPersonality.standard

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return
    self.personality = int(self.params.get('LongitudinalPersonality'))

  def is_enabled(self) -> bool:
    return self.params.get_bool('DynamicFollow')

  def toggle(self) -> bool:
    enabled = self.is_enabled()
    self.params.put_bool('DynamicFollow', not enabled)
    return not enabled

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    self._update_from_params()
    return float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.personality]))

  def update(self):
    self.frame += 1