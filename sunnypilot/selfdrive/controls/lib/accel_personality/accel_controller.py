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
  AccelPersonality.eco:       [2.0,  1.99,  1.92, .850, .500, .33, .23, .125],
  AccelPersonality.normal:    [2.0,  1.99,  1.92, .850, .500, .33, .23, .125],
  AccelPersonality.sport:     [2.0,  2.00,  1.97, 1.00, .635, .48, .31, .165],
}
MAX_ACCEL_BREAKPOINTS =       [0.,   4.,   6.,   9.,   16.,  25.,  30., 55.]

# Braking Profiles
MIN_ACCEL_PROFILES = {
  AccelPersonality.eco:    [-0.0000002, -0.0000002, -0.24, -1.20],
  AccelPersonality.normal: [-0.0000002, -0.0000002, -0.26, -1.20],
  AccelPersonality.sport:  [-0.0000003, -0.0000003, -0.28, -1.20],
}
MIN_ACCEL_BREAKPOINTS =    [0.,    5.,    8.,      25.]

DECEL_SMOOTH_ALPHA = 0.08  # Very aggressive smoothing for decel (lower = smoother)
ACCEL_SMOOTH_ALPHA = 0.20  # Less aggressive for accel (higher = more responsive)
MAX_DECEL_RATE = 0.15      # Maximum change in decel per timestep (m/s²)


class AccelPersonalityController:

  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.accel_personality = AccelPersonality.normal
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True
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
    v_ego = max(0.0, v_ego)
    target_max_accel = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
    target_min_accel = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.accel_personality])

    if self.first_run:
      self.last_max_accel = target_max_accel
      self.last_min_accel = target_min_accel
      self.first_run = False
      return float(target_min_accel), float(target_max_accel)

    # exponential smoothing to max accel
    self.last_max_accel = (ACCEL_SMOOTH_ALPHA * target_max_accel + (1 - ACCEL_SMOOTH_ALPHA) * self.last_max_accel)
    # VERY aggressive smoothing to min accel for ultra-smooth braking
    # Also add rate limiting as a safety net
    smoothed_decel = (DECEL_SMOOTH_ALPHA * target_min_accel + (1 - DECEL_SMOOTH_ALPHA) * self.last_min_accel)
    # Rate limit decel changes and/or prevent sudden jerks
    max_change_per_step = MAX_DECEL_RATE * DT_MDL
    decel_change = smoothed_decel - self.last_min_accel
    decel_change = np.clip(decel_change, -max_change_per_step, max_change_per_step)

    self.last_min_accel = self.last_min_accel + decel_change

    if self.last_min_accel > self.last_max_accel:
      self.last_min_accel = self.last_max_accel - 0.1

    return float(self.last_min_accel), float(self.last_max_accel)

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
    self.last_max_accel = 2.0
    self.last_min_accel = -0.01
    self.first_run = True

  def update(self):
    self.frame += 1
    self._update_from_params()