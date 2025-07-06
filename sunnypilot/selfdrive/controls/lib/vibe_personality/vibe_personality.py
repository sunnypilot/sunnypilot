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

# Acceleration Profiles mapped to both personality types
MAX_ACCEL_PROFILES = {
  # LongPersonality mappings
  LongPersonality.relaxed:    [2.00, 2.00, 1.72, 0.99, .572, .455, .365, .32, .10],  # eco-like
  LongPersonality.standard:   [2.00, 2.00, 1.84, 1.45, .64,  .55, .42, .37, .15],   # normal
  LongPersonality.aggressive: [2.00, 2.00, 2.00, 1.65, .80,  .72, .53, .46, .25],   # sport-like

  # AccelPersonality mappings
  AccelPersonality.eco:       [2.00, 2.00, 1.72, 0.99, .572, .455, .365, .32, .10],  # eco
  AccelPersonality.normal:    [2.00, 2.00, 1.84, 1.45, .64,  .55, .42, .37, .15],   # normal
  AccelPersonality.sport:     [2.00, 2.00, 2.00, 1.65, .80,  .72, .53, .46, .25],   # sport
}
MAX_ACCEL_BREAKPOINTS =       [0.,   7.,   9.,   11.,  16.,  20., 25., 30., 55.]

MIN_ACCEL_PROFILES = {
  # LongPersonality mappings
  LongPersonality.relaxed:    [-.007, -.07155, -.07155, -1.4, -1.4],  # eco-like
  LongPersonality.standard:   [-.008, -.07165, -.07165, -1.5, -1.5],  # normal
  LongPersonality.aggressive: [-.009, -.07175, -.07175, -1.6, -1.6],  # sport-like

  # AccelPersonality mappings
  AccelPersonality.eco:       [-.007, -.07155, -.07155, -1.4, -1.4],  # eco
  AccelPersonality.normal:    [-.008, -.07165, -.07165, -1.5, -1.5],  # normal
  AccelPersonality.sport:     [-.009, -.07175, -.07175, -1.6, -1.6],  # sport
}
MIN_ACCEL_BREAKPOINTS =       [0.,   2.,   13.,    22.2, 40.]

# Following Distance Profiles
FOLLOW_DISTANCE_PROFILES = {
  # LongPersonality mappings
  LongPersonality.relaxed: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.35, 1.35,  1.70, 1.70]
  },
  LongPersonality.standard: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.30, 1.30,  1.45, 1.45]
  },
  LongPersonality.aggressive: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.25, 1.25,  1.35, 1.35]
  },

  # AccelPersonality mappings (using similar logic)
  AccelPersonality.eco: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.35, 1.35,  1.70, 1.70]
  },
  AccelPersonality.normal: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.30, 1.30,  1.45, 1.45]
  },
  AccelPersonality.sport: {
    'x_vel':  [0.,   19.7,  22.2, 40.],
    'y_dist': [1.25, 1.25,  1.35, 1.35]
  }
}

class VibePersonalityController:
  """
  Controller for managing vibe-based longitudinal personality behavior including
  acceleration limits and following distances that adapt based on vehicle
  speed and selected driving personality.

  Supports both LongPersonality and AccelPersonality enum types.
  """

  def __init__(self):
    self.params = Params()
    self.personality = LongPersonality.standard
    self.frame = 0

    # Determine which personality type to use
    self.personality_type = self._get_personality_type()
    print(f"[VIBE_DEBUG] Initializing with personality type: {self.personality_type}")

    # Get available personalities based on type
    self.available_personalities = self._get_available_personalities()
    print(f"[VIBE_DEBUG] Available personalities: {self.available_personalities}")

    # Set default personality
    self.personality = self.available_personalities[1] if len(self.available_personalities) > 1 else self.available_personalities[0]
    print(f"[VIBE_DEBUG] Default personality set to: {self.personality}")

    # Parameter mappings for cleaner access
    self.param_keys = {
      'personality': 'LongitudinalPersonality' if self.personality_type == 'LongPersonality' else 'AccelPersonality',
      'personality_type': 'VibePersonalityType',  # 'LongPersonality' or 'AccelPersonality'
      'enabled': 'VibePersonalityEnabled',
      'accel_enabled': 'VibeAccelPersonalityEnabled',
      'follow_enabled': 'VibeFollowPersonalityEnabled'
    }

    # Precompute slopes for all personalities
    self._precompute_slopes()

  def _get_personality_type(self) -> str:
    """Get the personality type from params or default to LongPersonality"""
    use_accel_personality = self.params.get_bool('VibePersonalityType')
    personality_type = 'AccelPersonality' if use_accel_personality else 'LongPersonality'
    print(f"[VIBE_DEBUG] _get_personality_type returning: {personality_type}")
    return personality_type

  def _get_available_personalities(self) -> list:
    """Get available personalities based on the selected type"""
    if self.personality_type == 'AccelPersonality':
      personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
      print(f"[VIBE_DEBUG] Using AccelPersonality personalities: {personalities}")
      return personalities
    else:
      personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
      print(f"[VIBE_DEBUG] Using LongPersonality personalities: {personalities}")
      return personalities

  def _precompute_slopes(self):
    """Precompute all interpolation slopes for efficiency"""
    self.max_accel_slopes = {}
    self.min_accel_slopes = {}
    self.follow_distance_slopes = {}

    # Precompute for both personality types
    all_personalities = (
          [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive] +
          [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
    )

    for personality in all_personalities:
      if personality in MAX_ACCEL_PROFILES:
        self.max_accel_slopes[personality] = self._compute_slopes(MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[personality])
        self.min_accel_slopes[personality] = self._compute_slopes(MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[personality])

        if personality in FOLLOW_DISTANCE_PROFILES:
          profile = FOLLOW_DISTANCE_PROFILES[personality]
          self.follow_distance_slopes[personality] = self._compute_slopes(profile['x_vel'], profile['y_dist'])

  def _update_from_params(self):
    """Update personality and toggle states from params (rate limited)"""
    if self.frame % int(1. / DT_MDL) != 0:
      return

    # Update personality type
    new_personality_type = self._get_personality_type()
    if new_personality_type != self.personality_type:
      print(f"[VIBE_DEBUG] Personality type changed from {self.personality_type} to {new_personality_type}")
      self.personality_type = new_personality_type
      self.available_personalities = self._get_available_personalities()
      self.personality = self.available_personalities[1] if len(self.available_personalities) > 1 else self.available_personalities[0]
      self.param_keys['personality'] = 'LongitudinalPersonality' if self.personality_type == 'LongPersonality' else 'AccelPersonality'
      print(f"[VIBE_DEBUG] Updated personality to: {self.personality}")

    # Update personality
    try:
      personality_str = self.params.get(self.param_keys['personality'], encoding='utf-8')
      if personality_str:
        personality_int = int(personality_str)
        if personality_int in self.available_personalities:
          if personality_int != self.personality:
            print(f"[VIBE_DEBUG] Personality changed from {self.personality} to {personality_int} (type: {self.personality_type})")
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

  # Personality Type Management
  def set_personality_type(self, use_accel_personality: bool) -> bool:
    """Set the personality type (False=LongPersonality, True=AccelPersonality)"""
    old_type = self.personality_type
    self.params.put_bool('VibePersonalityType', use_accel_personality)
    self.personality_type = 'AccelPersonality' if use_accel_personality else 'LongPersonality'
    print(f"[VIBE_DEBUG] set_personality_type: {old_type} -> {self.personality_type}")
    self.available_personalities = self._get_available_personalities()
    self.personality = self.available_personalities[1] if len(self.available_personalities) > 1 else self.available_personalities[0]
    self.param_keys['personality'] = 'LongitudinalPersonality' if self.personality_type == 'LongPersonality' else 'AccelPersonality'
    print(f"[VIBE_DEBUG] New personality set to: {self.personality}")
    return True

  def get_personality_type(self) -> str:
    """Get current personality type"""
    return self.personality_type

  def toggle_personality_type(self) -> str:
    """Toggle between LongPersonality and AccelPersonality"""
    current_is_accel = self.params.get_bool('VibePersonalityType')
    print(f"[VIBE_DEBUG] toggle_personality_type: current_is_accel={current_is_accel}, toggling to {not current_is_accel}")
    self.set_personality_type(not current_is_accel)
    return self.personality_type

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
    """Cycle through available personalities based on current type"""
    current_idx = self.available_personalities.index(self.personality)
    next_personality = self.available_personalities[(current_idx + 1) % len(self.available_personalities)]
    print(f"[VIBE_DEBUG] cycle_personality: {self.personality} -> {next_personality} (type: {self.personality_type})")
    self.personality = next_personality
    self.params.put(self.param_keys['personality'], str(next_personality))
    return next_personality

  def set_personality(self, personality: int) -> bool:
    """Set personality if it's valid for current type"""
    if personality in self.available_personalities:
      old_personality = self.personality
      self.personality = personality
      self.params.put(self.param_keys['personality'], str(personality))
      print(f"[VIBE_DEBUG] set_personality: {old_personality} -> {personality} (type: {self.personality_type})")
      return True
    print(f"[VIBE_DEBUG] set_personality: Invalid personality {personality} for type {self.personality_type}")
    return False

  # Feature-specific Params checks
  def is_accel_enabled(self) -> bool:
    self._update_from_params()
    enabled = self._get_toggle_state('enabled') and self._get_toggle_state('accel_enabled')
    if enabled:
      print(f"[VIBE_DEBUG] is_accel_enabled: TRUE using {self.personality_type} personality {self.personality}")
    return enabled

  def is_follow_enabled(self) -> bool:
    self._update_from_params()
    enabled = self._get_toggle_state('enabled') and self._get_toggle_state('follow_enabled')
    if enabled:
      print(f"[VIBE_DEBUG] is_follow_enabled: TRUE using {self.personality_type} personality {self.personality}")
    return enabled

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
      print(f"[VIBE_DEBUG] get_accel_limits: Using {self.personality_type} personality {self.personality} at speed {v_ego:.2f}")
      max_a = self._interpolate(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.personality], self.max_accel_slopes[self.personality])
      min_a = self._interpolate(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.personality], self.min_accel_slopes[self.personality])
      print(f"[VIBE_DEBUG] get_accel_limits: min_a={min_a:.3f}, max_a={max_a:.3f}")
      return float(min_a), float(max_a)
    except (KeyError, IndexError):
      print(f"[VIBE_DEBUG] get_accel_limits: ERROR - KeyError/IndexError for personality {self.personality}")
      return None

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    self._update_from_params()

    try:
      print(f"[VIBE_DEBUG] get_follow_distance_multiplier: Using {self.personality_type} personality {self.personality} at speed {v_ego:.2f}")
      profile = FOLLOW_DISTANCE_PROFILES[self.personality]
      multiplier = float(self._interpolate(v_ego, profile['x_vel'], profile['y_dist'],
                                           self.follow_distance_slopes[self.personality]))
      print(f"[VIBE_DEBUG] get_follow_distance_multiplier: multiplier={multiplier:.3f}")
      return multiplier
    except (KeyError, IndexError):
      # Fallback to normal/standard based on personality type
      fallback_personality = LongPersonality.standard if self.personality_type == 'LongPersonality' else AccelPersonality.normal
      print(f"[VIBE_DEBUG] get_follow_distance_multiplier: ERROR - falling back to {fallback_personality}")
      try:
        profile = FOLLOW_DISTANCE_PROFILES[fallback_personality]
        slopes = self._compute_slopes(profile['x_vel'], profile['y_dist'])
        multiplier = float(self._interpolate(v_ego, profile['x_vel'], profile['y_dist'], slopes))
        print(f"[VIBE_DEBUG] get_follow_distance_multiplier: fallback multiplier={multiplier:.3f}")
        return multiplier
      except (KeyError, IndexError):
        print(f"[VIBE_DEBUG] get_follow_distance_multiplier: ERROR - fallback also failed")
        return None  # Let caller handle fallback

  def get_personality_info(self) -> dict:
    self._update_from_params()

    if self.personality_type == 'LongPersonality':
      names = {LongPersonality.relaxed: "Relaxed", LongPersonality.standard: "Standard", LongPersonality.aggressive: "Aggressive"}
      descs = {
        LongPersonality.relaxed: "Gentle acceleration, longer following distances",
        LongPersonality.standard: "Balanced acceleration and following distance",
        LongPersonality.aggressive: "Quick acceleration, shorter following distances"
      }
    else:  # AccelPersonality
      names = {AccelPersonality.eco: "Eco", AccelPersonality.normal: "Normal", AccelPersonality.sport: "Sport"}
      descs = {
        AccelPersonality.eco: "Efficient acceleration, longer following distances",
        AccelPersonality.normal: "Balanced acceleration and following distance",
        AccelPersonality.sport: "Performance acceleration, shorter following distances"
      }

    info = {
      "personality": names.get(self.personality, "Unknown"),
      "personality_int": self.personality,
      "personality_type": self.personality_type,
      "description": descs.get(self.personality, "Standard behavior"),
      "enabled": self._get_toggle_state('enabled'),
      "accel_enabled": self._get_toggle_state('accel_enabled'),
      "follow_enabled": self._get_toggle_state('follow_enabled'),
      "available_personalities": [names.get(p, str(p)) for p in self.available_personalities]
    }

    print(f"[VIBE_DEBUG] get_personality_info: {info}")
    return info

  def get_min_accel(self, v_ego: float) -> float:
    limits = self.get_accel_limits(v_ego)
    return limits[0] if limits else None

  def get_max_accel(self, v_ego: float) -> float:
    limits = self.get_accel_limits(v_ego)
    return limits[1] if limits else None

  def get_current_personality(self) -> int:
    self._update_from_params()
    return self.personality

  def reset(self):
    print(f"[VIBE_DEBUG] reset: Resetting personality to default")
    self.personality = self.available_personalities[1] if len(self.available_personalities) > 1 else self.available_personalities[0]
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