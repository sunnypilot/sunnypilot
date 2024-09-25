#!/usr/bin/env python3
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

AccelPersonality = custom.AccelerationPersonality

# accel personality by @arne182 modified by cgw and kumar
_DP_CRUISE_MIN_V =       [-0.20, -0.20, -0.20, -0.20, -0.20, -0.20, -0.32, -0.32, -0.52, -0.52, -0.72, -0.72, -1.0,  -1.0,  -1.15]
_DP_CRUISE_MIN_V_ECO =   [-0.19, -0.19, -0.19, -0.19, -0.19, -0.19, -0.30, -0.30, -0.50, -0.50, -0.70, -0.70, -1.0,  -1.0,  -1.10]
_DP_CRUISE_MIN_V_SPORT = [-0.21, -0.21, -0.21, -0.21, -0.21, -0.21, -0.34, -0.34, -0.54, -0.54, -0.74, -0.74, -1.0,  -1.0,  -1.20]
_DP_CRUISE_MIN_BP =      [0.,     0.08,  0.09, 2.77,  2.78,  8.33,  8.34,  13.88, 13.89, 19.44, 19.45, 25.00, 25.01, 30.55, 30.56]
#_DP_CRUISE_MIN_BP in kph[0.,     0.3,   0.3,  10,    10,    30,    30,    50,    50,    70,    70,    90,    90,    110,   >110]

#_DP_CRUISE_MIN_V =       [-1.0, -0.88]
#_DP_CRUISE_MIN_V_ECO =   [-1.0, -0.76]
#_DP_CRUISE_MIN_V_SPORT = [-1.0, -1.0]
#_DP_CRUISE_MIN_BP =      [0., 40.]

_DP_CRUISE_MAX_V =       [2.0, 2.0,  1.75, 0.96, .65,  .53,  .38,  .17]
_DP_CRUISE_MAX_V_ECO =   [2.0, 1.98, 1.67, 0.92, .58,  .47,  .32,  .09]
_DP_CRUISE_MAX_V_SPORT = [2.0, 2.0,  1.95, 1.15, .84,  .70,  .50,  .30]
_DP_CRUISE_MAX_BP =      [0.,  6.0,  8.,   11.,  20.,  25.,  30.,  40.]



class AccelController:
  def __init__(self):
    self._personality = AccelPersonality.stock

  def _dp_calc_cruise_accel_limits(self, v_ego: float) -> tuple[float, float]:
    if self._personality == AccelPersonality.eco:
      min_v = _DP_CRUISE_MIN_V_ECO
      max_v = _DP_CRUISE_MAX_V_ECO
    elif self._personality == AccelPersonality.sport:
      min_v = _DP_CRUISE_MIN_V_SPORT
      max_v = _DP_CRUISE_MAX_V_SPORT
    else:
      min_v = _DP_CRUISE_MIN_V
      max_v = _DP_CRUISE_MAX_V

    a_cruise_min = interp(v_ego, _DP_CRUISE_MIN_BP, min_v)
    a_cruise_max = interp(v_ego, _DP_CRUISE_MAX_BP, max_v)

    return a_cruise_min, a_cruise_max

  def get_accel_limits(self, v_ego: float, accel_limits: list[float]) -> tuple[float, float]:
    return accel_limits if self._personality == AccelPersonality.stock else self._dp_calc_cruise_accel_limits(v_ego)

  def is_enabled(self, accel_personality: int = AccelPersonality.stock) -> bool:
    self._personality = accel_personality
    return self._personality != AccelPersonality.stock
