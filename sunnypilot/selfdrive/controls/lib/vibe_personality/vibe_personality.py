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

# Acceleration Profiles mapped to AccelPersonality (eco/normal/sport)
MAX_ACCEL_PROFILES = {
  AccelPersonality.eco:       [2.00, 2.0,  1.80, 1.35, 0.83, .57,  .46, .28, .13, .088],  # eco
  AccelPersonality.normal:    [2.00, 2.0,  1.90, 1.55, 1.20, .63,  .54, .33, .22, .13],   # normal
  AccelPersonality.sport:     [2.00, 2.0,  1.98, 1.75, 1.50, .80,  .70, .52, .34, .2],   # sport
}
MAX_ACCEL_BREAKPOINTS =       [0.,   4.,   6.,   9.,   11.,  16.,  20., 25., 30., 55.]

# Braking profiles mapped to LongPersonality (relaxed/standard/aggressive)
MIN_ACCEL_PROFILES = {
  LongPersonality.relaxed:    [-.23, -.24, -.33, -1.10],  # gentler braking
  LongPersonality.standard:   [-.24, -.25, -.35, -1.15],  # normal braking
  LongPersonality.aggressive: [-.25, -.26, -.37, -1.20],  # more aggressive braking
}
MIN_ACCEL_BREAKPOINTS =       [0.,   1.,   2.,   50.]

# Following Distance Profiles mapped to LongPersonality (relaxed/standard/aggressive)
FOLLOW_DISTANCE_PROFILES = {
  LongPersonality.relaxed: {
    'x_vel':  [0.,   10.,   40.],
    'y_dist': [1.20, 1.20, 1.75]  # longer following distance
  },
  # 'x_vel':  [0.,  5.5,   8.3,  13.9, 16.4, 22.2, 25., 40.],
  #'y_dist': [1.15, 1.15, 1.30, 1.30, 1.50, 1.50, 1.75, 1.75]  # longer following distance
  # },
  LongPersonality.standard: {
    'x_vel':  [0.,   10.,  40.],
    'y_dist': [1.015, 1.00, 1.50]  # longer following distance
  },
  #'x_vel':  [0.,   16.4, 22.2, 40.],
  #'y_dist': [1.03, 1.03, 1.50, 1.50]  # normal following distance
  # },
  LongPersonality.aggressive: {
    'x_vel':  [0.,   10.,  40.],
    'y_dist': [0.93, 0.90, 1.30]  # longer following distance
  },
  #'x_vel':  [0.,   16.4, 22.2, 40.],
  #'y_dist': [0.90, 0.90, 1.30, 1.30]  # shorter following distance
  # }
}
class VibePersonalityController:
  """
  Controller for managing separated acceleration and distance controls:
  - AccelPersonality controls acceleration behavior (eco, normal, sport)
  - LongPersonality controls braking and following distance (relaxed, standard, aggressive)
  """

  def __init__(self):
    self.params = Params()
    self.frame = 0

    # Separate personalities for acceleration and distance control
    self.accel_personality = AccelPersonality.normal
    self.long_personality = LongPersonality.standard

    # Parameter keys
    self.param_keys = {
      'accel_personality': 'AccelPersonality',        # eco=0, normal=1, sport=2
      'long_personality': 'LongitudinalPersonality',  # relaxed=0, standard=1, aggressive=2
      'enabled': 'VibePersonalityEnabled',
      'accel_enabled': 'VibeAccelPersonalityEnabled',
      'follow_enabled': 'VibeFollowPersonalityEnabled'
    }

  def _update_from_params(self):
    """Update personalities from params (rate limited)"""
    if self.frame % int(1. / DT_MDL) != 0:
      return

    # Update AccelPersonality
    try:
      accel_personality_str = self.params.get(self.param_keys['accel_personality'], encoding='utf-8')
      if accel_personality_str:
        accel_personality_int = int(accel_personality_str)
        if accel_personality_int in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
          self.accel_personality = accel_personality_int
    except (ValueError, TypeError):
      pass

    # Update LongPersonality
    try:
      long_personality_str = self.params.get(self.param_keys['long_personality'], encoding='utf-8')
      if long_personality_str:
        long_personality_int = int(long_personality_str)
        if long_personality_int in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
          self.long_personality = long_personality_int
    except (ValueError, TypeError):
      pass

  def _get_toggle_state(self, key: str, default: bool = True) -> bool:
    """Get toggle state with default fallback"""
    return self.params.get_bool(self.param_keys.get(key, key)) if key in self.param_keys else default

  def _set_toggle_state(self, key: str, value: bool):
    """Set toggle state in params"""
    if key in self.param_keys:
      self.params.put_bool(self.param_keys[key], value)

  # AccelPersonality Management (for acceleration)
  def set_accel_personality(self, personality: int) -> bool:
    """Set AccelPersonality (eco=0, normal=1, sport=2)"""
    if personality in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      self.accel_personality = personality
      self.params.put(self.param_keys['accel_personality'], str(personality))
      return True
    return False

  def cycle_accel_personality(self) -> int:
    """Cycle through AccelPersonality: eco -> normal -> sport -> eco"""
    personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    current_idx = personalities.index(self.accel_personality)
    next_personality = personalities[(current_idx + 1) % len(personalities)]
    self.set_accel_personality(next_personality)
    return int(next_personality)

  def get_accel_personality(self) -> int:
    """Get current AccelPersonality"""
    self._update_from_params()
    return int(self.accel_personality)

  # LongPersonality Management (for braking and following distance)
  def set_long_personality(self, personality: int) -> bool:
    """Set LongPersonality (relaxed=0, standard=1, aggressive=2)"""
    if personality in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      self.long_personality = personality
      self.params.put(self.param_keys['long_personality'], str(personality))
      return True
    return False

  def cycle_long_personality(self) -> int:
    """Cycle through LongPersonality: relaxed -> standard -> aggressive -> relaxed"""
    personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
    current_idx = personalities.index(self.long_personality)
    next_personality = personalities[(current_idx + 1) % len(personalities)]
    self.set_long_personality(next_personality)
    return int(next_personality)

  def get_long_personality(self) -> int:
    """Get current LongPersonality"""
    self._update_from_params()
    return int(self.long_personality)

  # Toggle Functions
  def toggle_personality(self): return self._toggle_flag('enabled')
  def toggle_accel_personality(self): return self._toggle_flag('accel_enabled')
  def toggle_follow_distance_personality(self): return self._toggle_flag('follow_enabled')

  def _toggle_flag(self, key):
    current = self._get_toggle_state(key)
    self._set_toggle_state(key, not current)
    return not current

  def set_personality_enabled(self, enabled: bool): self._set_toggle_state('enabled', enabled)

  # Feature-specific enable checks
  def is_accel_enabled(self) -> bool:
    self._update_from_params()
    return self._get_toggle_state('enabled') and self._get_toggle_state('accel_enabled')

  def is_follow_enabled(self) -> bool:
    self._update_from_params()
    return self._get_toggle_state('enabled') and self._get_toggle_state('follow_enabled')

  def is_enabled(self) -> bool:
    self._update_from_params()
    return (self._get_toggle_state('enabled') and
            (self._get_toggle_state('accel_enabled') or self._get_toggle_state('follow_enabled')))

  def get_accel_limits(self, v_ego: float) -> tuple[float, float] | None:
    """
    Get acceleration limits based on current personalities.
    - Max acceleration from AccelPersonality (eco/normal/sport)
    - Min acceleration (braking) from LongPersonality (relaxed/standard/aggressive)
    Returns None if controller is disabled.
    """
    self._update_from_params()
    if not self.is_accel_enabled():
      return None

    try:
      # Max acceleration from AccelPersonality
      max_a = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])

      # Min acceleration (braking) from LongPersonality
      min_a = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.long_personality])

      return float(min_a), float(max_a)
    except (KeyError, IndexError):
      return None

  def get_follow_distance_multiplier(self, v_ego: float) -> float | None:
    """Get following distance multiplier based on LongPersonality only"""
    self._update_from_params()
    if not self.is_follow_enabled():
      return None

    try:
      profile = FOLLOW_DISTANCE_PROFILES[self.long_personality]
      multiplier = float(np.interp(v_ego, profile['x_vel'], profile['y_dist']))
      return multiplier
    except (KeyError, IndexError):
      return None



  def get_min_accel(self, v_ego: float) -> float | None:
    """Get minimum acceleration (braking) from distance mode"""
    limits = self.get_accel_limits(v_ego)
    return limits[0] if limits else None

  def get_max_accel(self, v_ego: float) -> float | None:
    """Get maximum acceleration from drive mode"""
    limits = self.get_accel_limits(v_ego)
    return limits[1] if limits else None

  def reset(self):
    """Reset to default modes"""
    self.accel_personality = AccelPersonality.normal
    self.long_personality = LongPersonality.standard
    self.frame = 0

  def update(self):
    """Update frame counter"""
    self.frame += 1
