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
  STANDSTILL_HOLD_RATE = 1.0  # m/s^2/s
  STANDSTILL_HOLD_DELAY_LEAD = 0.2  # s
  STANDSTILL_HOLD_DELAY_NO_LEAD = 0.2  # s
  STOPPING_FREEZE_MAX = 2.0  # s
  STOPPING_EXIT_DEBOUNCE = 0.2  # s
  STOPPING_FOLLOW_MIN = -0.10  # m/s^2
  STOPPING_FOLLOW_RATE = 2.0  # m/s^3
  CREEP_V_MIN = 0.03  # m/s
  CREEP_RATE_GROWTH = 1.5  # m/s^2/s per second of creep
  CREEP_RATE_MAX = 1.0  # m/s^2/s

  BLEND_V = 10.0 / 3.6  # m/s
  BLEND_POW = 1.0
  END_REQUEST = -0.30  # m/s^2, softer terminal support to avoid a brake jab
  END_PLAN_MIN = -0.25  # m/s^2
  END_RATE = 1.0  # m/s^3, ease the terminal request in more gradually

  def __init__(self, stop_accel):
    self.stop_accel = stop_accel
    self.standstill_t = 0.0
    self.stopping_t = 0.0
    self.go_t = 0.0
    self.stopped_once = False
    self.creep_t = 0.0
    self.end_active = False
    self.a_entry = self.END_REQUEST

  def _blend(self, v_ego):
    x = float(np.clip(v_ego / self.BLEND_V, 0.0, 1.0))
    return self.END_REQUEST + (self.a_entry - self.END_REQUEST) * x ** self.BLEND_POW

  def _end_request(self, a_target, prev_accel, v_ego):
    target = min(a_target, self._blend(v_ego))  # the firmer of the plan and the line
    step = self.END_RATE * DT_CTRL
    return float(np.clip(target, prev_accel - step, prev_accel + step))

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

    rolling = not CS.standstill and not self.stopped_once
    if state == LongCtrlState.off or not rolling or CS.vEgo >= self.BLEND_V or a_target > 0.0:
      self.end_active = False
    elif not self.end_active and a_target <= self.END_PLAN_MIN:
      self.end_active = True
      self.a_entry = min(prev_accel, self.END_REQUEST)

    if state != LongCtrlState.stopping:
      if self.end_active:
        return state, float(np.clip(self._end_request(a_target, prev_accel, CS.vEgo), accel_limits[0], accel_limits[1]))
      return state, stock_accel

    output_accel = prev_accel
    if output_accel > self.stop_accel:
      output_accel = min(output_accel, 0.0)
      if not CS.standstill and not self.stopped_once and a_target < self.STOPPING_FOLLOW_MIN and a_target > output_accel:
        output_accel = min(a_target, output_accel + self.STOPPING_FOLLOW_RATE * DT_CTRL)
      if self.end_active:
        output_accel = self._end_request(a_target, prev_accel, CS.vEgo)

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
