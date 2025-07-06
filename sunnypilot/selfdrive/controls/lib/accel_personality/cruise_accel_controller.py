"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom
from numpy import interp
from openpilot.common.params import Params

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

class CruiseAccelController:
  """
  Controls dynamic cruise minimum acceleration based on vehicle speed and driving personality.
  """

  def __init__(self):
    #TODO-SP: fix me. Speed breakpoints (m/s)
    self.speed_breakpoints =     [0.,     0.3,    1.,    27.,   40.]

    # Minimum allowed accelerations (m/s²) for each personality
    self.min_accel_vals_stock  = [-0.02, -0.03, -0.07, -0.6, -0.8]
    self.min_accel_vals_normal = [-0.02, -0.025, -0.06, -0.5, -0.7]
    self.min_accel_vals_eco    = [-0.015, -0.02, -0.05, -0.4, -0.6]
    self.min_accel_vals_sport  = [-0.03, -0.04, -0.08, -0.7, -0.9]
    # Default personality is stock
    self._personality = AccelPersonality.stock
    self._params = Params()
    # self._last_read_time = 0  # Uncomment if implementing timed caching

  def _read_params(self):
    """
    Reads the acceleration personality from Params.
    """
    # Refresh every time (or use a timer to throttle reads)
    # now = sec_since_boot()
    # if now - self._last_read_time < 5.0:
    #   return
    # self._last_read_time = now
    personality_str = self._params.get("AccelPersonality", encoding='utf-8')
    if personality_str is not None:
      try:
        personality_int = int(personality_str)
        if personality_int in [AccelPersonality.stock, AccelPersonality.normal, AccelPersonality.eco, AccelPersonality.sport]:
          self._personality = personality_int
      except ValueError:
        print("AccelPersonality param not a valid integer. Defaulting to stock.")
    else:
      print("AccelPersonality param missing. Defaulting to stock.")

  def get_min_accel(self, v_ego):
    """
    Interpolates and returns the minimum allowed cruise acceleration based on vehicle speed and personality.

    :param v_ego: Vehicle speed in m/s
    :return: Minimum acceleration (m/s²)
    """
    # Read the parameters to ensure the personality is up to date
    self._read_params()

    # Clamp speed to valid range
    v_ego = max(self.speed_breakpoints[0], min(v_ego, self.speed_breakpoints[-1]))

    if self._personality == AccelPersonality.eco:
      min_accel_vals = self.min_accel_vals_eco
    elif self._personality == AccelPersonality.sport:
      min_accel_vals = self.min_accel_vals_sport
    elif self._personality == AccelPersonality.normal:
      min_accel_vals = self.min_accel_vals_normal
    else:
      min_accel_vals = self.min_accel_vals_stock

    return interp(v_ego, self.speed_breakpoints, min_accel_vals)
