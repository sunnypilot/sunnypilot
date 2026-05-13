"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# Toyota PCM switches between regen (positive torque) and friction brake when
# commanded accel crosses zero. At trivial magnitudes the mode switch itself is
# felt at the wheels even when the planner's ramp through zero is smooth.
#
# Hysteresis: while commanded accel sits in a tight band around zero, hold at
# coast (0.0) so PCM does not flip modes for sub-noise-floor commands. Allow
# crossing only when the new-side magnitude clearly exceeds the band.
DEAD_BAND = 0.15  # m/s^2, half-width of the hold-at-coast region


class GasBrakeHysteresis:
  def __init__(self):
    self.prev: float = 0.0

  def update(self, accel: float) -> float:
    if abs(accel) <= DEAD_BAND and self.prev * accel < 0.0:
      # Crossing sign in the dead band — hold at coast so PCM does not flip
      # gas/brake modes for sub-noise-floor commands.
      self.prev = 0.0
      return 0.0
    self.prev = accel
    return accel
