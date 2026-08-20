"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math
from typing import cast

from opendbc.car import DT_CTRL

STOPPING_DISTANCE = 0.75
STOPPING_TIME = 2.5
STOPPING_ACCEL_TOLERANCE = 0.1
STOPPING_SPEED_TOLERANCE = 0.05
STOPPING_SETTLE_FRAMES = 30
STOPPING_HOLD_ACCEL = -1.2
STOPPING_HOLD_MARGIN = 0.6
STOPPING_HOLD_SPEED_TOLERANCE = 0.01


class LongControlSP:
  def __init__(self):
    self._stopping_settle_frames: int | None = None
    self._stopping_hold_accel: float | None = None

  def _hold_supported(self) -> bool:
    return self.CP.openpilotLongitudinalControl and not self.CP.notCar and self.CP.stopAccel < 0.0

  def update_state(self, stopping: bool, active: bool, CS) -> None:
    if not active:
      self._stopping_settle_frames = None
      self._stopping_hold_accel = None
      return

    invalid_speed = not all(math.isfinite(speed) for speed in (CS.vEgo, CS.vEgoRaw))
    moving = max(abs(CS.vEgo), abs(CS.vEgoRaw)) > STOPPING_SPEED_TOLERANCE
    if invalid_speed or (not stopping and moving):
      self._stopping_hold_accel = None
    elif (self._hold_supported() and math.isfinite(self.last_output_accel)
          and self.last_output_accel <= self.CP.stopAccel):
      previous_hold = self._stopping_hold_accel if self._stopping_hold_accel is not None else self.last_output_accel
      self._stopping_hold_accel = min(self.last_output_accel, previous_hold)
    if not stopping:
      self._stopping_settle_frames = None
      if self._stopping_hold_accel is not None and math.isfinite(self.last_output_accel):
        self._stopping_hold_accel = min(self.last_output_accel, self._stopping_hold_accel)

  def stopping_accel(self, output_accel: float, CS) -> float:
    if self._stopping_hold_accel is not None and math.isfinite(CS.vEgo) and abs(CS.vEgo) <= STOPPING_SPEED_TOLERANCE:
      return min(output_accel, self._stopping_hold_accel)
    return output_accel

  def stopping_decel_rate(self, CS, a_target: float, output_accel: float) -> float:
    if not all(math.isfinite(value) for value in (output_accel, a_target, CS.vEgo, CS.vEgoRaw, CS.aEgo)):
      return 1.0
    hold_supported = self._hold_supported()
    preserving_hold = self._stopping_hold_accel is not None
    can_hold = output_accel <= 0.0 and a_target >= output_accel
    terminal_speed = (0.0 <= CS.vEgo <= STOPPING_SPEED_TOLERANCE
                      or CS.standstill and abs(CS.vEgo) <= STOPPING_SPEED_TOLERANCE)
    positive_stop_entry = self.last_output_accel > 0.0 and output_accel == 0.0
    if output_accel > 0.0 or positive_stop_entry or CS.vEgo < 0.0 and not terminal_speed:
      return 1.0
    if terminal_speed and self._stopping_settle_frames is None:
      if not preserving_hold and (not can_hold or output_accel > -STOPPING_ACCEL_TOLERANCE or CS.aEgo >= -STOPPING_ACCEL_TOLERANCE):
        return 1.0
      self._stopping_settle_frames = 0

    time_decel = 0.0 if self._stopping_settle_frames is not None else CS.vEgo / STOPPING_TIME
    required_decel = max(time_decel, CS.vEgo ** 2 / (2.0 * STOPPING_DISTANCE), 1e-3)
    adequacy = min(max(-CS.aEgo / required_decel, 0.0), 1.0)
    planner_need = min(max((output_accel - a_target) / max(required_decel, STOPPING_ACCEL_TOLERANCE), 0.0), 1.0)
    if not terminal_speed and self._stopping_settle_frames is None and can_hold and adequacy >= 1.0:
      self._stopping_settle_frames = 0
      if hold_supported:
        self._stopping_hold_accel = output_accel

    motion_need = 1.0 - adequacy ** 2
    terminal_need = 0.0
    if terminal_speed or self._stopping_settle_frames not in (None, 0):
      settle_frames = cast(int, self._stopping_settle_frames)
      self._stopping_settle_frames = min(settle_frames + 1, STOPPING_SETTLE_FRAMES)
      terminal_need = (self._stopping_settle_frames / STOPPING_SETTLE_FRAMES) ** 2

    if preserving_hold and self._stopping_hold_accel is not None:
      self._stopping_hold_accel = min(output_accel, self._stopping_hold_accel)
      if terminal_speed:
        minimum_hold = min(STOPPING_HOLD_ACCEL, self.CP.stopAccel + STOPPING_HOLD_MARGIN)
        hold_target = max(self.CP.stopAccel, min(minimum_hold, self._stopping_hold_accel))
        if CS.aEgo > STOPPING_ACCEL_TOLERANCE or abs(CS.vEgoRaw) > STOPPING_HOLD_SPEED_TOLERANCE:
          return 1.0
        hold_rate = max(planner_need, terminal_need)
        if CS.vEgoRaw == 0.0 and abs(CS.vEgo) <= STOPPING_HOLD_SPEED_TOLERANCE:
          if output_accel <= hold_target:
            return planner_need
          hold_rate = max(planner_need, min(hold_rate, (output_accel - hold_target) / DT_CTRL))
        return hold_rate

    return max(motion_need, planner_need, terminal_need)
