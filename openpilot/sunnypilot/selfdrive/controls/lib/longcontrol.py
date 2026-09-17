"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.common.realtime import DT_CTRL

STOPPING_DISTANCE = 1.5
STOPPED_SPEED = 0.02
STOPPING_TIME = 2.5
MIN_STOPPING_HOLD_ACCEL = -0.2
STOPPING_DECEL_RATE = 0.3
STOPPED_DECEL_RATE = 0.05
STOP_EXIT_ACCEL = 0.1


class LongControlSP:
  @staticmethod
  def should_exit_stopping(was_stopping: bool, is_pid: bool, a_target: float) -> bool:
    return not (was_stopping and is_pid and a_target <= STOP_EXIT_ACCEL)

  @staticmethod
  def limit_stop_release(last_output_accel: float, output_accel: float) -> float:
    if last_output_accel < 0.0 and output_accel > last_output_accel:
      return min(output_accel, last_output_accel + STOPPING_DECEL_RATE * DT_CTRL)
    return output_accel

  def should_hold_stopping(self, CS, a_target: float) -> bool:
    return (self.last_output_accel <= MIN_STOPPING_HOLD_ACCEL and a_target >= self.last_output_accel and CS.vEgo > STOPPED_SPEED and CS.aEgo < 0.0
            and CS.vEgo <= -CS.aEgo * STOPPING_TIME and CS.vEgo ** 2 <= -2.0 * CS.aEgo * STOPPING_DISTANCE)

  @staticmethod
  def stopping_decel_rate(v_ego: float) -> float:
    return float(np.interp(v_ego, [0.0, 0.5, 1.5], [STOPPED_DECEL_RATE, 0.15, STOPPING_DECEL_RATE]))
