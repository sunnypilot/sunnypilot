"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom
import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

# Acceleration Profiles
MAX_ACCEL_PROFILES = {
  AccelPersonality.eco:       [2.0,  1.99,  1.92, 1.10, .500, .33, .23, .125],   # eco
  AccelPersonality.normal:    [2.0,  2.00,  1.97, 1.25, .635, .48, .31, .165],   # normal
  AccelPersonality.sport:     [2.0,  2.00,  2.00, 1.85, .800, .60, .42, .251],    # sport
}
MAX_ACCEL_BREAKPOINTS =       [0.,   4.,   6.,   9.,   16.,  25.,  30., 55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-.0006, -.0006, -.010,  -.30,  -1.20],  # gentler braking
  AccelPersonality.normal: [-.0007, -.0007, -.012,  -.35,  -1.20],  # normal braking
  AccelPersonality.sport:  [-.0020, -.0008, -.014,  -.40,  -1.20],  # more aggressive braking
}
MIN_ACCEL_BREAKPOINTS =    [0.,   3.0,    11.,    14,  50.]


class AccelPersonalityController:

  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.param_keys = {
      'personality': 'AccelPersonality',
      'enabled': 'AccelPersonalityEnabled'
    }
    self._load_personality_from_params()

  def _load_personality_from_params(self):
    try:
      saved = self.params.get(self.param_keys['personality'])
      if saved is not None:
        personality_value = int(saved)
        if personality_value in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
          self.accel_personality = personality_value
        else:
          cloudlog.warning(f"Invalid personality value {personality_value}, using normal")
          self.accel_personality = AccelPersonality.normal
    except (ValueError, TypeError) as e:
      cloudlog.warning(f"Failed to load personality from params: {e}")
      self.accel_personality = AccelPersonality.normal

  def _update_from_params(self):
    if self.frame % int(1. / DT_MDL) != 0:
      return
    self._load_personality_from_params()

  def get_accel_personality(self) -> int:
    self._update_from_params()
    return int(self.accel_personality)

  def set_accel_personality(self, personality: int):
    if personality not in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      cloudlog.error(f"Invalid personality {personality}, ignoring")
      return

    self.accel_personality = personality
    self.params.put(self.param_keys['personality'], str(personality))
    cloudlog.info(f"Accel personality set to {personality}")

  def cycle_accel_personality(self) -> int:
    personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    current_idx = personalities.index(self.accel_personality)
    next_personality = personalities[(current_idx + 1) % len(personalities)]
    self.set_accel_personality(next_personality)
    return int(next_personality)

  def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
    max_a = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
    min_a = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality])
    return float(min_a), float(max_a)

  def get_min_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[0]

  def get_max_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[1]

  def is_enabled(self) -> bool:
    return self.params.get_bool(self.param_keys['enabled'])

  def set_enabled(self, enabled: bool):
    self.params.put_bool(self.param_keys['enabled'], enabled)
    cloudlog.info(f"Accel personality controller {'enabled' if enabled else 'disabled'}")

  def toggle_enabled(self) -> bool:
    current = self.is_enabled()
    self.set_enabled(not current)
    return not current

  def reset(self):
    self.accel_personality = AccelPersonality.normal
    self.frame = 0

  def update(self):
    self.frame += 1
    self._update_from_params()