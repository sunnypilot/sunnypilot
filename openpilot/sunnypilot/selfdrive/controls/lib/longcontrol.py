"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

STOPPING_DISTANCE = 0.75
STOPPED_SPEED = 0.02
STOPPING_TIME = 2.5


class LongControlSP:
  def should_hold_stopping(self, CS, a_target: float) -> bool:
    return (self.last_output_accel <= 0.0 and a_target >= self.last_output_accel and CS.vEgo > STOPPED_SPEED and CS.aEgo < 0.0
            and CS.vEgo <= -CS.aEgo * STOPPING_TIME and CS.vEgo ** 2 <= -2.0 * CS.aEgo * STOPPING_DISTANCE)
