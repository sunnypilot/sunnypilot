"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

STOPPING_DISTANCE = 1.5
STOPPED_SPEED = 0.02
STOPPING_TIME = 2.5
MIN_STOPPING_HOLD_ACCEL = -0.2
STOPPING_DECEL_RATE = 0.3
STOPPED_DECEL_RATE = 0.05


class LongControlSP:
  def should_hold_stopping(self, CS, a_target: float) -> bool:
    return (self.last_output_accel <= MIN_STOPPING_HOLD_ACCEL and a_target >= self.last_output_accel and CS.vEgo > STOPPED_SPEED and CS.aEgo < 0.0
            and CS.vEgo <= -CS.aEgo * STOPPING_TIME and CS.vEgo ** 2 <= -2.0 * CS.aEgo * STOPPING_DISTANCE)

  @staticmethod
  def stopping_decel_rate(v_ego: float) -> float:
    return float(np.interp(v_ego, [0.0, 0.5, 1.5], [STOPPED_DECEL_RATE, 0.15, STOPPING_DECEL_RATE]))
