"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState


class LongControlSP(LongControl):
  def update(self, active, CS, a_target, should_stop, accel_limits):
    prev_output_accel = self.last_output_accel
    output_accel = super().update(active, CS, a_target, should_stop, accel_limits)

    if self.long_control_state == LongCtrlState.stopping and self.CP_SP.smoothStopDecelRate > 0.0:
      output_accel = self.stopping_accel(prev_output_accel, accel_limits)
      self.last_output_accel = output_accel

    return float(output_accel)

  def stopping_accel(self, accel, accel_limits):
    if accel > self.CP.stopAccel:
      accel = min(accel, 0.0) - self.CP_SP.smoothStopDecelRate * DT_CTRL
    return float(np.clip(accel, *accel_limits))
