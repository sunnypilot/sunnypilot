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
  LongPersonality.relaxed:    [1.50, 1.35, 1.60, 1.80, 1.90],
  LongPersonality.standard:   [1.35, 1.25, 1.40, 1.55, 1.65],
  LongPersonality.aggressive: [1.00, 0.85, 1.05, 1.25, 1.35],
}
FOLLOW_BREAKPOINTS = [0., 14., 25., 36., 50.]

SMOOTHING_BASE = 0.70  # Base smoothing factor (higher = smoother)
SMOOTHING_RANGE = 0.25  # Additional smoothing at high speeds
SMOOTHING_SPEED_THRESHOLD = 36.0  # m/s (~80 mph) for max smoothing
PERSONALITY_CHANGE_COOLDOWN_S = 2.0


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.personality = LongPersonality.standard
    self.current_multiplier = 1.40
    self.target_multiplier = self.current_multiplier
    self.personality_change_cooldown = 0
    self.personality_cooldown_frames = int(PERSONALITY_CHANGE_COOLDOWN_S / DT_MDL)

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return

    if self.personality_change_cooldown > 0:
      self.personality_change_cooldown -= 1
      return

    new_personality = int(self.params.get('LongitudinalPersonality'))
    if new_personality != self.personality:
      self.personality = new_personality
      self.personality_change_cooldown = self.personality_cooldown_frames

  def _get_smoothing_factor(self, v_ego: float) -> float:
    speed_factor = np.clip(v_ego / SMOOTHING_SPEED_THRESHOLD, 0.3, 1.0)
    return SMOOTHING_BASE + (SMOOTHING_RANGE * speed_factor)

  def is_enabled(self) -> bool:
    return self.params.get_bool('DynamicFollow')

  def toggle(self) -> bool:
    enabled = self.is_enabled()
    self.params.put_bool('DynamicFollow', not enabled)
    return not enabled

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    self._update_from_params()
    self.target_multiplier = float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.personality]))

    #exponential smoothing with speedadaptive factor
    smoothing_factor = self._get_smoothing_factor(v_ego)
    self.current_multiplier = (smoothing_factor * self.current_multiplier + (1.0 - smoothing_factor) * self.target_multiplier)
    return self.current_multiplier

  def update(self):
    self.frame += 1