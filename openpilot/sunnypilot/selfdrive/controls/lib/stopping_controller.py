"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState


class StoppingController:
  """Optional terminal-stop policy applied after stock LongControl.update()."""

  STOPPING_DECEL_RATE = 0.3  # m/s^2/s
  STANDSTILL_HOLD_RATE = 0.5  # m/s^2/s
  STANDSTILL_HOLD_DELAY_LEAD = 0.6  # s
  STANDSTILL_HOLD_DELAY_NO_LEAD = 0.9  # s
  STOPPING_FREEZE_MAX = 2.0  # s
  STOPPING_EXIT_DEBOUNCE = 0.2  # s
  STOPPING_FOLLOW_MIN = -0.10  # m/s^2
  STOPPING_FOLLOW_RATE = 2.0  # m/s^3
  CREEP_V_MIN = 0.03  # m/s
  CREEP_RATE_GROWTH = 1.5  # m/s^2/s per second of creep
  CREEP_RATE_MAX = 1.0  # m/s^2/s

  def __init__(self, stop_accel):
    self.stop_accel = stop_accel
    self.standstill_t = 0.0
    self.stopping_t = 0.0
    self.go_t = 0.0
    self.stopped_once = False
    self.creep_t = 0.0

  def update(self, prev_state, state, CS, a_target, prev_accel, stock_accel, accel_limits, has_lead=False):
    if prev_state == LongCtrlState.stopping and state == LongCtrlState.pid and CS.standstill:
      self.go_t += DT_CTRL
      if self.go_t < self.STOPPING_EXIT_DEBOUNCE:
        state = LongCtrlState.stopping
    else:
      self.go_t = 0.0

    self.standstill_t = self.standstill_t + DT_CTRL if CS.standstill else 0.0
    self.stopping_t = self.stopping_t + DT_CTRL if state == LongCtrlState.stopping else 0.0
    if state != LongCtrlState.stopping:
      self.stopped_once = False
    elif CS.standstill:
      self.stopped_once = True

    creeping = self.stopped_once and not CS.standstill and CS.vEgo > self.CREEP_V_MIN
    self.creep_t = self.creep_t + DT_CTRL if creeping else 0.0

    if state != LongCtrlState.stopping:
      return state, stock_accel

    output_accel = prev_accel
    if output_accel > self.stop_accel:
      output_accel = min(output_accel, 0.0)
      if not CS.standstill and not self.stopped_once and a_target < self.STOPPING_FOLLOW_MIN and a_target > output_accel:
        output_accel = min(a_target, output_accel + self.STOPPING_FOLLOW_RATE * DT_CTRL)

      hold_delay = self.STANDSTILL_HOLD_DELAY_LEAD if has_lead else self.STANDSTILL_HOLD_DELAY_NO_LEAD
      if self.standstill_t >= hold_delay:
        rate = self.STANDSTILL_HOLD_RATE
      elif creeping:
        rate = min(self.STOPPING_DECEL_RATE + self.CREEP_RATE_GROWTH * self.creep_t, self.CREEP_RATE_MAX)
      elif self.stopping_t >= self.STOPPING_FREEZE_MAX:
        rate = self.STOPPING_DECEL_RATE
      else:
        rate = 0.0
      output_accel -= rate * DT_CTRL

    return state, float(np.clip(output_accel, accel_limits[0], accel_limits[1]))
