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

# Last update: June 5, 2024

from openpilot.common.numpy_fast import interp

DP_ACCEL_STOCK = 0
DP_ACCEL_ECO = 1
DP_ACCEL_NORMAL = 2
DP_ACCEL_SPORT = 3

# accel profile by @arne182 modified by cgw
_DP_CRUISE_MIN_V =       [-1.00,  -1.00,  -0.99,  -0.90,  -0.90,  -0.88,  -0.88,  -0.82]
_DP_CRUISE_MIN_V_ECO =   [-1.00,  -1.00,  -0.98,  -0.88,  -0.88,  -0.86,  -0.86,  -0.80]
_DP_CRUISE_MIN_V_SPORT = [-1.01,  -1.01,  -1.00,  -0.92,  -0.92,  -0.90,  -0.90,  -0.84]
_DP_CRUISE_MIN_BP =      [0.,     0.05,    0.4,    0.5,    8.33,   16.,   30.,   40.]

_DP_CRUISE_MAX_V =       [2.4, 2.4, 2.4, 1.60, 1.05, .81,  .625, .42,  .348, .12]
_DP_CRUISE_MAX_V_ECO =   [1.6, 1.6, 1.6, 1.0, .60, .50, .40, .25, .15, .05]
_DP_CRUISE_MAX_V_SPORT = [3.5, 3.5, 2.8, 2.4,  1.4,  1.0,  .89,  .75,  .50,  .2]
_DP_CRUISE_MAX_BP =      [0.,  1.,  6.,  8.,   11.,  15.,  20.,  25.,  30.,  55.]


class AccelController:

    def __init__(self):
        # self._params = Params()
        self._profile = DP_ACCEL_STOCK

    def set_profile(self, profile):
        try:
            self._profile = int(profile) if int(profile) in [DP_ACCEL_STOCK, DP_ACCEL_ECO, DP_ACCEL_NORMAL, DP_ACCEL_SPORT] else DP_ACCEL_STOCK
        except:
            self._profile = DP_ACCEL_STOCK

    def _dp_calc_cruise_accel_limits(self, v_ego):
        if self._profile == DP_ACCEL_ECO:
            min_v = _DP_CRUISE_MIN_V_ECO
            max_v = _DP_CRUISE_MAX_V_ECO
        elif self._profile == DP_ACCEL_SPORT:
            min_v = _DP_CRUISE_MIN_V_SPORT
            max_v = _DP_CRUISE_MAX_V_SPORT
        else:
            min_v = _DP_CRUISE_MIN_V
            max_v = _DP_CRUISE_MAX_V

        a_cruise_min = interp(v_ego, _DP_CRUISE_MIN_BP, min_v)
        a_cruise_max = interp(v_ego, _DP_CRUISE_MAX_BP, max_v)
        return a_cruise_min, a_cruise_max

    def get_accel_limits(self, v_ego, accel_limits):
        return accel_limits if self._profile == DP_ACCEL_STOCK else self._dp_calc_cruise_accel_limits(v_ego)

    def is_enabled(self):
        return self._profile != DP_ACCEL_STOCK
