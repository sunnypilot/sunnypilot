"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState

TAPER_JERK = 0.25
TAPER_MAX_DECEL = 1.0
MAX_JERK = 2.0


class LongControlSP(LongControl):
  def __init__(self, CP, CP_SP):
    super().__init__(CP, CP_SP)
    self.was_tapering = False

  def update(self, active, CS, a_target, should_stop, accel_limits):
    prev_output_accel = self.last_output_accel
    smooth_stop = self.CP_SP.smoothStopDecelRate > 0.0

    tapering = smooth_stop and not should_stop and -TAPER_MAX_DECEL < a_target < 0.0
    if tapering:
      accel_limits = (max(accel_limits[0], -float(np.sqrt(2.0 * TAPER_JERK * max(CS.vEgo, 0.0)))), accel_limits[1])

    output_accel = super().update(active, CS, a_target, should_stop, accel_limits)

    if smooth_stop:
      if self.long_control_state == LongCtrlState.stopping:
        output_accel = self.stopping_accel(prev_output_accel, accel_limits)
      elif self.long_control_state == LongCtrlState.pid and (tapering or self.was_tapering):
        max_change = MAX_JERK * DT_CTRL
        output_accel = float(np.clip(output_accel, prev_output_accel - max_change, prev_output_accel + max_change))
      self.last_output_accel = output_accel

    self.was_tapering = tapering
    return float(output_accel)

  def stopping_accel(self, accel, accel_limits):
    if accel > self.CP.stopAccel:
      accel = min(accel, 0.0) - self.CP_SP.smoothStopDecelRate * DT_CTRL
    return float(np.clip(accel, *accel_limits))
