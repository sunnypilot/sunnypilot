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
  LongPersonality.relaxed:    [1.60, 1.62, 1.64, 1.65, 1.75, 1.75, 1.80, 1.85, 1.87, 1.90],
  LongPersonality.standard:   [1.40, 1.42, 1.44, 1.45, 1.45, 1.45, 1.45, 1.50, 1.52, 1.54],
  LongPersonality.aggressive: [0.85, 0.87, 1.12, 1.12, 1.17, 1.22, 1.26, 1.28, 1.30, 1.32],
}

FOLLOW_BREAKPOINTS =          [0.,   5.,   5.5,  15.,  20.,  25.,  30.,  36.,  42.,  50.]

PERSONALITY_CHANGE_COOLDOWN_S = 2.0


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.personality = LongPersonality.standard
    self.personality_change_cooldown = 0
    self.personality_cooldown_frames = int(PERSONALITY_CHANGE_COOLDOWN_S / DT_MDL)
    self._load_personality()

  def _load_personality(self):
    try:
      saved = self.params.get('LongitudinalPersonality')
      if saved is not None:
        val = int(saved)
        if val in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
          self.personality = val
    except (ValueError, TypeError):
      pass

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return

    if self.personality_change_cooldown > 0:
      self.personality_change_cooldown -= 1
      return

    try:
      param = self.params.get('LongitudinalPersonality')
      if param is not None:
        val = int(param)
        if val in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
          if val != self.personality:
            self.personality = val
            self.personality_change_cooldown = self.personality_cooldown_frames
    except (ValueError, TypeError):
      pass

  def is_enabled(self) -> bool:
    return self.params.get_bool('DynamicFollow')

  def set_enabled(self, enabled: bool):
    self.params.put_bool('DynamicFollow', enabled)

  def toggle(self) -> bool:
    enabled = self.is_enabled()
    self.set_enabled(not enabled)
    return not enabled

  def get_personality(self) -> int:
    self._update_from_params()
    return int(self.personality)

  def set_personality(self, personality: int):
    if personality not in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      return

    self.personality = personality
    self.params.put('LongitudinalPersonality', str(personality))
    self.personality_change_cooldown = self.personality_cooldown_frames

  def cycle_personality(self) -> int:
    personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
    current_idx = personalities.index(self.personality)
    next_personality = personalities[(current_idx + 1) % len(personalities)]
    self.set_personality(next_personality)
    return int(next_personality)

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    self._update_from_params()
    v_ego = max(0.0, v_ego)
    multiplier = float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.personality]))
    return multiplier

  def reset(self):
    self.personality = LongPersonality.standard
    self.frame = 0
    self.personality_change_cooldown = 0

  def update(self):
    self.frame += 1
    self._update_from_params()