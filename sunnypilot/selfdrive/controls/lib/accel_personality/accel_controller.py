# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Last updated: August 12, 2024

from cereal import custom
from openpilot.common.numpy_fast import interp
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params
#from openpilot.selfdrive.controls.lib.longitudinal_planner import limit_accel_in_turns
from opendbc.car.interfaces import ACCEL_MIN

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

# Acceleration Profiles
_DP_CRUISE_MIN_V = {
  AccelPersonality.eco:    [-0.015, -0.015, -1.2,  -1.2,  -1.2,  -1.2,  -1.2,  -1.2],
  AccelPersonality.normal: [-0.018, -0.018, -1.2,  -1.2,  -1.2,  -1.2,  -1.2,  -1.2],
  AccelPersonality.sport:  [-0.020, -0.020, -1.2,  -1.2,  -1.2,  -1.2,  -1.2,  -1.2],
}
_DP_CRUISE_MAX_V = {
  AccelPersonality.eco:    [1.60, 1.60, 1.58, 1.58, 0.86, .532, .432, .32,  .28,  .085],
  AccelPersonality.normal: [1.80, 1.80, 1.75, 1.75, 0.92, .65,  .56,  .36,  .30,  .12],
  AccelPersonality.sport:  [2.00, 2.00, 2.00, 2.00, 1.05, .79,  .61,  .42,  .333, .2],
}
_DP_CRUISE_MIN_BP = [0.,     2.0,    2.01,   15.,   15.01, 20.,   20.01, 40.]
_DP_CRUISE_MAX_BP = [0.,   1.,   6.,   8.,   11.,  16,   20.,  25.,  30.,  55.]


class AccelController:
  def __init__(self):
    self._params = Params()
    self._personality = AccelPersonality.stock
    self._frame = 0

  def _read_params(self):
    """ Reads the acceleration personality setting from persistent storage. """
    if self._frame % int(1. / DT_MDL) == 0:
      personality_str = self._params.get("AccelPersonality", encoding='utf-8')
      if personality_str is not None:
        personality_int = int(personality_str)
        if personality_int in _DP_CRUISE_MIN_V:
          self._personality = personality_int
          # Print the current mode being used
          print(f"Current Acceleration Personality Mode: {self._personality}")

  def compute_accel_limits(self, v_ego: float, sm, CP) -> tuple[list[float], list[float]]:
    """ Computes acceleration limits based on personality, turns, and DEC mode. """
    self._read_params()
    # Print the current mode being used
    print(f"Current Acceleration Personality Mode: {self._personality}")

    if self._personality == AccelPersonality.eco:
      min_v = _DP_CRUISE_MIN_V[AccelPersonality.eco]
      max_v = _DP_CRUISE_MAX_V[AccelPersonality.eco]
      print("eco")
    elif self._personality == AccelPersonality.sport:
      min_v = _DP_CRUISE_MIN_V[AccelPersonality.sport]
      max_v = _DP_CRUISE_MAX_V[AccelPersonality.sport]
      print("sport")
    else:
      min_v = _DP_CRUISE_MIN_V[AccelPersonality.normal]
      max_v = _DP_CRUISE_MAX_V[AccelPersonality.normal]
      print("normal")

    a_cruise_min = interp(v_ego, _DP_CRUISE_MIN_BP, min_v)
    a_cruise_max = interp(v_ego, _DP_CRUISE_MAX_BP, max_v)

    # Determine acceleration mode
    accel_limits = [ACCEL_MIN, a_cruise_max] if CP.radarUnavailable else [a_cruise_min, a_cruise_max]

    # Adjust acceleration for turns
    #steer_angle = sm['carState'].steeringAngleDeg - sm['liveParameters'].angleOffsetDeg
    # Ensure accel_limits_turns is a valid list/tuple here
    accel_limits_turns = accel_limits  # This is temporary if limit_accel_in_turns is not defined

    return accel_limits, accel_limits_turns



  def is_enabled(self) -> bool:
    """ Returns True if AccelController is actively modifying acceleration limits. """
    return bool(self._personality != AccelPersonality.stock)

  def update(self):
    """ Updates the internal frame counter. """
    self._frame += 1
