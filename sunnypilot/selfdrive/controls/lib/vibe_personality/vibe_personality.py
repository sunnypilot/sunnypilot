"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log, custom
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.accel_personality import AccelPersonalityController
from openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.follow_personality import FollowPersonalityController

LongPersonality = log.LongitudinalPersonality
AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality


class VibePersonalityController:
  def __init__(self):
    self.accel = AccelPersonalityController()
    self.follow = FollowPersonalityController()
    self.params = Params()

  @property
  def frame(self):
    return self.accel.frame

  @frame.setter
  def frame(self, value):
    self.accel.frame = self.follow.frame = value

  @property
  def accel_personality(self):
    return self.accel.accel_personality

  @property
  def long_personality(self):
    return self.accel.long_personality

  @long_personality.setter
  def long_personality(self, value):
    self.accel.long_personality = self.follow.long_personality = value

  def set_accel_personality(self, personality: int) -> bool:
    return self.accel.set_accel_personality(personality)

  def cycle_accel_personality(self) -> int:
    return self.accel.cycle_accel_personality()

  def set_long_personality(self, personality: int) -> bool:
    if personality not in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      return False
    self.long_personality = personality
    self.params.put('LongitudinalPersonality', str(personality))
    return True

  def cycle_long_personality(self) -> int:
    personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
    idx = personalities.index(self.long_personality)
    next_p = personalities[(idx + 1) % len(personalities)]
    self.set_long_personality(next_p)
    return int(next_p)

  def is_enabled(self) -> bool:
    main_enabled = self.params.get_bool('VibePersonalityEnabled') or False
    return main_enabled and (self.accel.is_enabled() or self.follow.is_enabled())

  def get_accel_limits(self, v_ego: float) -> tuple[float, float] | None:
    main_enabled = self.params.get_bool('VibePersonalityEnabled') or False
    if not (main_enabled and self.accel.is_enabled()):
      return None
    return self.accel.get_accel_limits(v_ego)

  def get_follow_distance_multiplier(self, v_ego: float) -> float | None:
    main_enabled = self.params.get_bool('VibePersonalityEnabled') or False
    if not (main_enabled and self.follow.is_enabled()):
      return None
    return self.follow.get_follow_distance_multiplier(v_ego)

  def update(self):
    self.accel.update()
    self.follow.update()