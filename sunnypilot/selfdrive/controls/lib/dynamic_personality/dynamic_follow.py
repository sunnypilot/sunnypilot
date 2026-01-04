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
  LongPersonality.relaxed:    [1.70, 1.70, 1.75, 1.75, 1.80, 1.80, 1.80],
  LongPersonality.standard:   [1.40, 1.40, 1.45, 1.45, 1.50, 1.50, 1.50],
  LongPersonality.aggressive: [1.05, 1.05, 1.15, 1.15, 1.20, 1.20, 1.20],
}

FOLLOW_BREAKPOINTS =          [0.,   3.,    6.,  30.,  40.,  50.,  60.]

SMOOTHING_BASE = 0.55  # Base smoothing factor (higher = smoother)
SMOOTHING_RANGE = 0.20  # Additional smoothing at high speeds
SMOOTHING_SPEED_THRESHOLD = 36.0  # m/s (~80 mph) for max smoothing
PERSONALITY_CHANGE_COOLDOWN_S = 2.0


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.personality = LongPersonality.standard
    self.current_multiplier = None
    self.first_run = True
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

  def _get_smoothing_factor(self, v_ego: float) -> float:
    speed_factor = np.clip(v_ego / SMOOTHING_SPEED_THRESHOLD, 0.3, 1.0)
    return SMOOTHING_BASE + (SMOOTHING_RANGE * speed_factor)

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
    target = float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.personality]))

    if self.first_run:
      self.current_multiplier = target
      self.first_run = False
      return self.current_multiplier

    #exponential smoothing with speedadaptive factor
    alpha = self._get_smoothing_factor(v_ego)
    self.current_multiplier = alpha * self.current_multiplier + (1.0 - alpha) * target
    return self.current_multiplier

  def reset(self):
    self.personality = LongPersonality.standard
    self.frame = 0
    self.current_multiplier = None
    self.first_run = True
    self.personality_change_cooldown = 0

  def update(self):
    self.frame += 1
    self._update_from_params()
