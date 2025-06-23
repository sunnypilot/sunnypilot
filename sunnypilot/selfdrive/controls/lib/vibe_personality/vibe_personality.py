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
    'x_vel':  [0.,   8.3, 14.5, 19.7, 22.2, 40.],
    'y_dist': [1.22, 1.22, 1.80, 1.80, 1.90, 1.90]
  },
  LongPersonality.standard: {
    'x_vel':  [0.,   2.,   6.,   14.,  14.5, 19.7, 22.2, 40.],
    'y_dist': [1.20, 1.20, 1.31, 1.31, 1.37, 1.37, 1.45, 1.60]
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

    print(f"[VibePersonalityController] Initializing with personality: {self.personality}")

    # Precompute slopes for acceleration profiles for efficiency
    self.max_accel_slopes = {}
    self.min_accel_slopes = {}
    self.follow_distance_slopes = {}

    for personality in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      print(f"[VibePersonalityController] Precomputing slopes for personality: {personality}")

      # Acceleration slopes
      self.max_accel_slopes[personality] = self._compute_symmetric_slopes(
        MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[personality]
      )
      self.min_accel_slopes[personality] = self._compute_symmetric_slopes(
        MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[personality]
      )

      # Following distance slopes
      profile = FOLLOW_DISTANCE_PROFILES[personality]
      self.follow_distance_slopes[personality] = self._compute_symmetric_slopes(
        profile['x_vel'], profile['y_dist']
      )

    print("[VibePersonalityController] Initialization complete")

  def _update_personality_from_params(self):
    if self.frame % int(1. / DT_MDL) == 0:
      personality_str = self.params.get("LongitudinalPersonality", encoding='utf-8')
      print(f"[VibePersonalityController] Reading personality param: {personality_str} (frame: {self.frame})")

      if personality_str is not None:
        try:
          personality_int = int(personality_str)
          if personality_int in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
            if personality_int != self.personality:
              print(f"[VibePersonalityController] Personality changed: {self.personality} -> {personality_int}")
            self.personality = personality_int
          else:
            print(f"[VibePersonalityController] Invalid personality value: {personality_int}, keeping current: {self.personality}")
        except (ValueError, TypeError):
          print(f"[VibePersonalityController] Failed to parse personality param: {personality_str}, keeping current: {self.personality}")
          # Keep current personality if parameter is invalid
          pass

  def get_accel_limits(self, v_ego: float, default_accel_limits: list[float] = None) -> tuple[float, float]:
    self._update_personality_from_params()

    if default_accel_limits is None:
      default_accel_limits = [-1.2, 2.0]

    try:
      max_accel = self._hermite_interpolate(
        v_ego,
        MAX_ACCEL_BREAKPOINTS,
        MAX_ACCEL_PROFILES[self.personality],
        self.max_accel_slopes[self.personality]
      )
      min_accel = self._hermite_interpolate(
        v_ego,
        MIN_ACCEL_BREAKPOINTS,
        MIN_ACCEL_PROFILES[self.personality],
        self.min_accel_slopes[self.personality]
      )

      print(f"[VibePersonalityController] Calculated accel limits: min={min_accel:.3f}, max={max_accel:.3f} m/s²")
      return (float(min_accel), float(max_accel))
    except (KeyError, IndexError) as e:
      print(f"[VibePersonalityController] Error calculating accel limits: {e}, using defaults: {default_accel_limits}")
      # Fallback to default limits if personality not found or interpolation fails
      return (default_accel_limits[0], default_accel_limits[1])

  def get_follow_distance_multiplier(self, v_ego: float) -> float:
    """
    Get dynamic follow distance multiplier based on current personality and speed.

    Args:
        v_ego: Current vehicle speed (m/s)

    Returns:
        float: Follow distance multiplier (1.0 = base following distance)
    """
    self._update_personality_from_params()

    try:
      profile = FOLLOW_DISTANCE_PROFILES[self.personality]
      result = self._hermite_interpolate(
        v_ego,
        profile['x_vel'],
        profile['y_dist'],
        self.follow_distance_slopes[self.personality]
      )

      print(f"[VibePersonalityController] Calculated follow distance multiplier: {result:.3f}")
      return float(result)
    except (KeyError, IndexError) as e:
      print(f"[VibePersonalityController] Error calculating follow distance, using standard fallback: {e}")
      # Fallback to standard profile
      profile = FOLLOW_DISTANCE_PROFILES[LongPersonality.standard]
      slopes = self._compute_symmetric_slopes(profile['x_vel'], profile['y_dist'])
      result = self._hermite_interpolate(v_ego, profile['x_vel'], profile['y_dist'], slopes)
      print(f"[VibePersonalityController] Fallback follow distance multiplier: {result:.3f}")
      return float(result)

  def get_max_accel(self, v_ego: float) -> float:
    """
    Get maximum acceleration limit for current speed and personality.

    Args:
        v_ego: Current vehicle speed (m/s)

    Returns:
        float: Maximum acceleration in m/s²
    """
    _, max_accel = self.get_accel_limits(v_ego)
    return max_accel

  def get_min_accel(self, v_ego: float) -> float:
    """
    Get minimum acceleration (maximum deceleration) limit for current speed and personality.

    Args:
        v_ego: Current vehicle speed (m/s)

    Returns:
        float: Minimum acceleration (negative value) in m/s²
    """
    min_accel, _ = self.get_accel_limits(v_ego)
    return min_accel

  def _compute_symmetric_slopes(self, x, y):
    """
    Compute slopes for Hermite interpolation using symmetric difference method.

    Args:
        x: x-coordinates (breakpoints)
        y: y-coordinates (values)

    Returns:
        numpy.ndarray: Computed slopes
    """
    n = len(x)
    if n < 2:
      raise ValueError("At least two points are required to compute slopes.")

    m = np.zeros(n)
    for i in range(n):
      if i == 0:
        # Forward difference for first point
        m[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
      elif i == n-1:
        # Backward difference for last point
        m[i] = (y[i] - y[i-1]) / (x[i] - x[i-1])
      else:
        # Central difference for interior points
        m[i] = ((y[i+1] - y[i]) / (x[i+1] - x[i]) + (y[i] - y[i-1]) / (x[i] - x[i-1])) / 2
    return m

  def _hermite_interpolate(self, x, xp, yp, slopes):
    """
    Perform cubic Hermite interpolation.

    Args:
        x: Point to interpolate at
        xp: x-coordinates of data points
        yp: y-coordinates of data points
        slopes: Precomputed slopes at data points

    Returns:
        float: Interpolated value
    """
    # Clamp x to the domain
    x = np.clip(x, xp[0], xp[-1])

    # Find the segment
    idx = np.searchsorted(xp, x) - 1
    idx = np.clip(idx, 0, len(slopes) - 2)

    # Get segment endpoints and slopes
    x0, x1 = xp[idx], xp[idx+1]
    y0, y1 = yp[idx], yp[idx+1]
    m0, m1 = slopes[idx], slopes[idx+1]

    # Compute normalized parameter t
    t = (x - x0) / (x1 - x0)

    # Hermite basis functions
    h00 = 2*t**3 - 3*t**2 + 1      # (1+2t)(1-t)²
    h10 = t**3 - 2*t**2 + t        # t(1-t)²
    h01 = -2*t**3 + 3*t**2         # t²(3-2t)
    h11 = t**3 - t**2              # t²(t-1)

    # Compute interpolated value
    return (h00 * y0) + (h10 * (x1 - x0) * m0) + (h01 * y1) + (h11 * (x1 - x0) * m1)

  def get_personality_info(self) -> dict:
    self._update_personality_from_params()

    personality_names = {
      LongPersonality.relaxed: "Relaxed",
      LongPersonality.standard: "Standard",
      LongPersonality.aggressive: "Aggressive"
    }

    personality_descriptions = {
      LongPersonality.relaxed: "Gentle acceleration, longer following distances, comfort-focused driving",
      LongPersonality.standard: "Balanced acceleration and following distance for normal driving",
      LongPersonality.aggressive: "Quick acceleration, shorter following distances, performance-focused driving"
    }

    return {
      "personality": personality_names.get(self.personality, "Unknown"),
      "personality_int": self.personality,
      "description": personality_descriptions.get(self.personality, "Standard behavior"),
      "frame": self.frame
    }

  def get_current_personality(self) -> int:
    self._update_personality_from_params()
    return self.personality

  def is_personality_enabled(self) -> bool:
    self._update_personality_from_params()
    return self.personality != LongPersonality.standard

  def reset(self):
    self.personality = LongPersonality.standard
    self.frame = 0

  def update(self):
    self.frame += 1

    # Prevent frame counter overflow
    if self.frame > 1000000:
      self.frame = 0