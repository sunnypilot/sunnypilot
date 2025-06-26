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

# Acceleration Profiles mapped to LongitudinalPersonality
MAX_ACCEL_PROFILES = {
  LongPersonality.relaxed:    [2.00, 2.00, 1.72, 0.83, .572, .455, .365, .32, .10],  # eco-like
  LongPersonality.standard:   [2.00, 2.00, 1.84, 1.00, .64,  .55, .42, .37, .15],   # normal
  LongPersonality.aggressive: [2.00, 2.00, 1.95, 1.25, .78,  .67, .50, .43, .20],   # sport-like
}
MAX_ACCEL_BREAKPOINTS = [0., 7., 9., 11., 16., 20., 25., 30., 55.]

MIN_ACCEL_PROFILES = {
  LongPersonality.relaxed:    [-.071143, -.07132, -.0713, -.07155, -1.4, -1.4],  # eco-like
  LongPersonality.standard:   [-.071143, -.07142, -.0714, -.07165, -1.5, -1.5],  # normal
  LongPersonality.aggressive: [-.071143, -.07152, -.0715, -.07175, -1.6, -1.6],  # sport-like
}
MIN_ACCEL_BREAKPOINTS =       [0.,       1.2,     8.,     13.,    22.2, 40.]

# Following Distance Profiles
FOLLOW_DISTANCE_PROFILES = {
  LongPersonality.relaxed: {
    'x_vel':  [0.,   8.3, 11.1, 19.7, 22.2, 40.],
    'y_dist': [1.18, 1.18, 1.80, 1.80, 1.90, 1.90]
  },
  LongPersonality.standard: {
    'x_vel':  [0.,   2.,   6.,   14.,  14.5, 19.7, 22.2, 40.],
    'y_dist': [1.18, 1.18, 1.31, 1.31, 1.37, 1.37, 1.60, 1.60]
  },
  LongPersonality.aggressive: {
    'x_vel':  [0.,   1.,    5.,   14.,  14.5, 19.7, 22.2, 40.],
    'y_dist': [1.18, 1.18,  1.30, 1.30, 1.35, 1.35, 1.45, 1.45]
  }
}

class VibePersonalityController:
  """
  Controller for managing vibe-based longitudinal personality behavior including
  acceleration limits and following distances that adapt based on vehicle
  speed and selected driving personality.
  """

  def __init__(self):
    self.params = Params()
    self.personality = LongPersonality.standard
    self.frame = 0
    self.available_personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]

    # Parameter mappings for cleaner access
    self.param_keys = {
      'personality': 'LongitudinalPersonality',
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

    for personality in self.available_personalities:
      self.max_accel_slopes[personality] = self._compute_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[personality])
      self.min_accel_slopes[personality] = self._compute_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[personality])

      profile = FOLLOW_DISTANCE_PROFILES[personality]
      self.follow_distance_slopes[personality] = self._compute_slopes(profile['x_vel'], profile['y_dist'])

  def _update_from_params(self):
    """Update personality and toggle states from params (rate limited)"""
    if self.frame % int(1. / DT_MDL) != 0:
      return

    # Update personality
    try:
      personality_str = self.params.get(self.param_keys['personality'], encoding='utf-8')
      if personality_str:
        personality_int = int(personality_str)
        if personality_int in self.available_personalities:
          self.personality = personality_int
    except (ValueError, TypeError):
      pass

  def _get_toggle_state(self, key: str, default: bool = True) -> bool:
    """Get toggle state with default fallback"""
    return self.params.get_bool(self.param_keys.get(key, key)) if key in self.param_keys else default

  def _set_toggle_state(self, key: str, value: bool):
    """Set toggle state in params"""
    if key in self.param_keys:
      self.params.put_bool(self.param_keys[key], value)

  # Individual Params
  def toggle_personality(self): return self._toggle_flag('enabled')
  def toggle_accel_personality(self): return self._toggle_flag('accel_enabled')
  def toggle_follow_distance_personality(self): return self._toggle_flag('follow_enabled')

  def _toggle_flag(self, key):
    current = self._get_toggle_state(key)
    self._set_toggle_state(key, not current)
    return not current

  def set_personality_enabled(self, enabled: bool): self._set_toggle_state('enabled', enabled)

  def cycle_personality(self) -> int:
    current_idx = self.available_personalities.index(self.personality)
    next_personality = self.available_personalities[(current_idx + 1) % len(self.available_personalities)]
    self.personality = next_personality
    self.params.put(self.param_keys['personality'], str(next_personality))
    return next_personality

  def set_personality(self, personality: int) -> bool:
    if personality in self.available_personalities:
      self.personality = personality
      self.params.put(self.param_keys['personality'], str(personality))
      return True
    return False

  # Feature-specific Params checks
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
    Get acceleration limits based on current personality and speed.
    Returns None if controller is disabled (reverts to stock behavior).
    """
    self._update_from_params()
    if not self.is_accel_enabled():
      return None

    try:
      max_a = self._interpolate(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.personality], self.max_accel_slopes[self.personality])
      min_a = self._interpolate(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.personality], self.min_accel_slopes[self.personality])
      return float(min_a), float(max_a)
    except (KeyError, IndexError):
      return None

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    self._update_from_params()

    try:
      profile = FOLLOW_DISTANCE_PROFILES[self.personality]
      return float(self._interpolate(v_ego, profile['x_vel'], profile['y_dist'],
                                     self.follow_distance_slopes[self.personality]))
    except (KeyError, IndexError):
      # Fallback to standard
      profile = FOLLOW_DISTANCE_PROFILES[LongPersonality.standard]
      slopes = self._compute_slopes(profile['x_vel'], profile['y_dist'])
      return float(self._interpolate(v_ego, profile['x_vel'], profile['y_dist'], slopes))

  def get_personality_info(self) -> dict:
    self._update_from_params()
    names = {LongPersonality.relaxed: "Relaxed", LongPersonality.standard: "Standard", LongPersonality.aggressive: "Aggressive"}
    descs = {
      LongPersonality.relaxed: "Gentle acceleration, longer following distances",
      LongPersonality.standard: "Balanced acceleration and following distance",
      LongPersonality.aggressive: "Quick acceleration, shorter following distances"
    }
    return {
      "personality": names.get(self.personality, "Unknown"),
      "personality_int": self.personality,
      "description": descs.get(self.personality, "Standard behavior"),
      "enabled": self._get_toggle_state('enabled'),
      "accel_enabled": self._get_toggle_state('accel_enabled'),
      "follow_enabled": self._get_toggle_state('follow_enabled')
    }

  def get_min_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[0]

  def get_max_accel(self, v_ego: float) -> float:
    return self.get_accel_limits(v_ego)[1]

  def get_current_personality(self) -> int:
    self._update_from_params()
    return self.personality

  def reset(self):
    self.personality = LongPersonality.standard
    self.frame = 0

  def update(self):
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
