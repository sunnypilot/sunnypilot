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

# Last updated: July 1, 2024

from cereal import custom
from openpilot.common.numpy_fast import interp

AccelPersonality = custom.AccelerationPersonality

# accel personality by @arne182 modified by cgw and kumar
_DP_CRUISE_MIN_V =       [-0.04, -0.04, -0.16, -0.16, -0.26, -0.26, -0.46, -0.46,  -0.74]
_DP_CRUISE_MIN_V_ECO =   [-0.03, -0.03, -0.15, -0.15, -0.25, -0.25, -0.45, -0.45,  -0.72]
_DP_CRUISE_MIN_V_SPORT = [-0.05, -0.05, -0.17, -0.17, -0.27, -0,27, -0.47, -0.47,  -0.76]
_DP_CRUISE_MIN_BP =      [0.,    3.0,   3.01,  11.1,  11.11, 20.,   20.01, 30.,    30.01]

#_DP_CRUISE_MIN_V =       [-0.045, -0.045, -0.201,  -0.201,  -0.430,  -0.430,  -0.66,  -0.66,  -0.82]
#_DP_CRUISE_MIN_V_ECO =   [-0.04,  -0.04,  -0.200,  -0.200,  -0.425,  -0.425,  -0.64,  -0.64,  -0.80]
#_DP_CRUISE_MIN_V_SPORT = [-0.05,  -0.05,  -0.204,  -0.204,  -0.445,  -0.445,  -0.68,  -0.68,  -0.84]
#_DP_CRUISE_MIN_BP =      [0.,     5.00,   5.01,    17.,     17.01,   27.77,   27.78,  33.,    33.01]
_DP_CRUISE_MAX_V =       [2.0, 2.0, 2.0, 1.68, 1.07, .72,  .53,  .42,  .13]
_DP_CRUISE_MAX_V_ECO =   [2.0, 2.0, 2.0, 1.38, 0.91, .53,  .42,  .31,  .085]
_DP_CRUISE_MAX_V_SPORT = [2.0, 2.0, 2.0, 2.00, 1.34, .96,  .78,  .60,  .4]
_DP_CRUISE_MAX_BP =      [0.,  1.,  6.,  8.,   11.,  20.,  25.,  30.,  55.]


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
