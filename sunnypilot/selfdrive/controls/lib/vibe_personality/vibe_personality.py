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
  AccelPersonality.eco:       [1.50, 1.5,  1.20, 1.0, 0.4,  .40, .25, .13, .068],  # eco
  AccelPersonality.normal:    [2.00, 2.00, 1.42, 1.10, .65,  .56, .43, .36, .12],   # normal
  AccelPersonality.sport:     [2.00, 2.00, 1.52, 1.40, .80,  .70, .53, .46, .20],   # sport
}
MAX_ACCEL_BREAKPOINTS =       [0.,   6.,   9.,   11.,  16.,  20., 25., 30., 55.]

# Braking profiles mapped to LongPersonality (relaxed/standard/aggressive)
MIN_ACCEL_PROFILES = {
  LongPersonality.relaxed:    [-0.08, -0.08, -0.08, -0.5],  # gentler braking
  LongPersonality.standard:   [-1.05, -1.15, -1.30, -1.30],  # normal braking
  LongPersonality.aggressive: [-1.10, -1.25, -1.40, -1.40],  # more aggressive braking
}
MIN_ACCEL_BREAKPOINTS =       [0., 10., 25., 50.]

# Following Distance Profiles mapped to LongPersonality (relaxed/standard/aggressive)
FOLLOW_DISTANCE_PROFILES = {
  LongPersonality.relaxed: {
    'x_vel':  [0.,   19.7, 22.2, 40.],
    'y_dist': [1.25, 1.60, 1.85, 2.2]  # longer following distance
  },
  LongPersonality.standard: {
    'x_vel':  [0.,   19.7, 22.2, 40.],
    'y_dist': [1.35, 1.35, 1.40, 1.40]  # normal following distance
  },
  LongPersonality.aggressive: {
    'x_vel':  [0.,   19.7, 22.2, 40.],
    'y_dist': [1.20, 1.20, 1.30, 1.30]  # shorter following distance
  }
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

    # Precompute slopes for all personalities
    self._precompute_slopes()

  def _precompute_slopes(self):
    """Precompute all interpolation slopes for efficiency"""
    self.max_accel_slopes = {}
    self.min_accel_slopes = {}
    self.follow_distance_slopes = {}

    # Precompute for AccelPersonality (acceleration)
    for personality in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      if personality in MAX_ACCEL_PROFILES:
        self.max_accel_slopes[personality] = self._compute_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[personality])

    # Precompute for LongPersonality (braking and following)
    for personality in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      if personality in MIN_ACCEL_PROFILES:
        self.min_accel_slopes[personality] = self._compute_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[personality])

      if personality in FOLLOW_DISTANCE_PROFILES:
        profile = FOLLOW_DISTANCE_PROFILES[personality]
        self.follow_distance_slopes[personality] = self._compute_slopes(profile['x_vel'], profile['y_dist'])

  def _update_from_params(self):
    """Update personalities from params (rate limited)"""
    if self.frame % int(1. / DT_MDL) != 0:
      return

    # Update AccelPersonality
    try:
      accel_personality_str = self.params.get(self.param_keys['accel_personality'])
      if accel_personality_str:
        accel_personality_int = int(accel_personality_str)
        if accel_personality_int in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
          self.accel_personality = accel_personality_int
    except (ValueError, TypeError):
      pass

    # Update LongPersonality
    try:
      long_personality_str = self.params.get(self.param_keys['long_personality'])
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
      max_a = self._interpolate(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality],
                                self.max_accel_slopes[self.accel_personality])

      # Min acceleration (braking) from LongPersonality
      min_a = self._interpolate(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.long_personality],
                                self.min_accel_slopes[self.long_personality])

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
      multiplier = float(self._interpolate(v_ego, profile['x_vel'], profile['y_dist'],
                                           self.follow_distance_slopes[self.long_personality]))
      return multiplier
    except (KeyError, IndexError):
      return None

  def get_personality_info(self) -> dict:
    """Get comprehensive info about current personalities and settings"""
    self._update_from_params()

    accel_names = {AccelPersonality.eco: "Eco", AccelPersonality.normal: "Normal", AccelPersonality.sport: "Sport"}
    long_names = {LongPersonality.relaxed: "Relaxed", LongPersonality.standard: "Standard", LongPersonality.aggressive: "Aggressive"}

    info = {
      "accel_personality": accel_names.get(self.accel_personality, "Unknown"),
      "accel_personality_int": self.accel_personality,
      "long_personality": long_names.get(self.long_personality, "Unknown"),
      "long_personality_int": self.long_personality,
      "enabled": self._get_toggle_state('enabled'),
      "accel_enabled": self._get_toggle_state('accel_enabled'),
      "follow_enabled": self._get_toggle_state('follow_enabled'),
      "accel_description": f"Acceleration: {accel_names.get(self.accel_personality, 'Unknown')}",
      "long_description": f"Following/Braking: {long_names.get(self.long_personality, 'Unknown')}",
    }

    return info

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
    self.frame = (self.frame + 1) % 1000000

  def _compute_slopes(self, x, y):
    """Compute slopes for Hermite interpolation using symmetric difference method."""
    n = len(x)
    if n < 2:
      raise ValueError("At least two points required")

    m = np.zeros(n)
    for i in range(n):
      if i == 0:
        m[i] = (y[1] - y[0]) / (x[1] - x[0])
      elif i == n-1:
        m[i] = (y[i] - y[i-1]) / (x[i] - x[i-1])
      else:
        m[i] = ((y[i+1] - y[i]) / (x[i+1] - x[i]) + (y[i] - y[i-1]) / (x[i] - x[i-1])) / 2
    return m

  def _interpolate(self, x, xp, yp, slopes):
    """Perform cubic Hermite interpolation."""
    x = np.clip(x, xp[0], xp[-1])
    idx = np.clip(np.searchsorted(xp, x) - 1, 0, len(slopes) - 2)

    x0, x1 = xp[idx], xp[idx+1]
    y0, y1 = yp[idx], yp[idx+1]
    m0, m1 = slopes[idx], slopes[idx+1]

    t = (x - x0) / (x1 - x0)
    h = [2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2]

    return h[0]*y0 + h[1]*(x1 - x0)*m0 + h[2]*y1 + h[3]*(x1 - x0)*m1
