"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math

import numpy as np

from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState


STOP_LEVEL_V = 0.4  # m/s
STOP_LEVEL_TAU = 0.2  # s
STOP_CONFIRM_RISE = 0.2  # m/s^2
STOP_CONFIRM_DELAY = 0.2  # s


class StopConfirm:
  def __init__(self):
    self.reset()

  def reset(self):
    self.level: float | None = None
    self.collapsed = False
    self.confirmed_t = -1.0

  def update(self, standstill: bool, v_ego: float, a_long: float | None) -> bool:
    """returns True once the stop is confirmed and STOP_CONFIRM_DELAY has passed"""
    if a_long is None or not math.isfinite(a_long):
      self.reset()
      return False
    if v_ego > STOP_LEVEL_V and not standstill:
      alpha = DT_CTRL / (STOP_LEVEL_TAU + DT_CTRL)
      self.level = a_long if self.level is None else self.level + alpha * (a_long - self.level)
      self.collapsed = False
      self.confirmed_t = -1.0
      return False
    if self.level is not None and a_long >= self.level + STOP_CONFIRM_RISE:
      self.collapsed = True
    if standstill and self.collapsed:
      self.confirmed_t = 0.0 if self.confirmed_t < 0.0 else self.confirmed_t + DT_CTRL
    elif not standstill:
      self.confirmed_t = -1.0
    return self.confirmed_t >= STOP_CONFIRM_DELAY - 1e-9


class StoppingController:
  """Optional terminal-stop policy applied after stock LongControl.update()."""

  STOPPING_DECEL_RATE = 0.3  # m/s^2/s
  STANDSTILL_HOLD_RATE = 1.0  # m/s^2/s
  STANDSTILL_HOLD_DELAY_LEAD = 1.0  # s
  STANDSTILL_HOLD_DELAY_NO_LEAD = 1.0  # s
  STOPPING_FREEZE_MAX = 2.0  # s
  STOPPING_EXIT_DEBOUNCE = 0.2  # s
  ENGAGE_STANDSTILL_GRACE = 0.6  # s
  STOPPING_FOLLOW_MIN = -0.10  # m/s^2
  STOPPING_FOLLOW_RATE = 2.0  # m/s^3
  CREEP_V_MIN = 0.03  # m/s
  CREEP_RATE_GROWTH = 1.5  # m/s^2/s
  CREEP_RATE_MAX = 1.0  # m/s^2/s

  BLEND_V = 10.0 / 3.6  # m/s
  END_V_HI = 5.0 / 3.6  # m/s
  END_HI = -0.65  # m/s^2
  END_LO = -0.35  # m/s^2

  END_CURVE_V = [0.0, 1.0 / 3.6, 2.0 / 3.6, 3.0 / 3.6, 4.0 / 3.6, 5.0 / 3.6]  # m/s
  END_CURVE_A = [END_LO, END_LO, -0.56, -0.60, -0.65, END_HI]  # m/s^2
  END_PLAN_MIN = -0.25  # m/s^2
  END_RATE = 2.0  # m/s^3

  RELEASE_FAST = 4.0  # m/s^3
  RELEASE_SLOW = 1.5  # m/s^3
  RELEASE_BAND_LO = -0.6  # m/s^2
  RELEASE_BAND_HI = 0.4  # m/s^2

  REROLL_ACCEL = -0.6  # m/s^2
  REROLL_JERK = 6.0  # m/s^3

  FLAT_HOLD_ACCEL = -1.2  # m/s^2
  FLAT_PITCH_DEG = 1.0  # deg
  SLOPE_PITCH_DEG = 2.0  # deg

  CF_WINDOW = 10.0  # s
  CF_V_MAX = 8.0 / 3.6  # m/s
  CF_TRIGGER = -0.15  # m/s^2
  CF_END = -0.24  # m/s^2
  CF_PLAN_SOFT = -0.45  # m/s^2
  CF_PLAN_FIRM = -0.70  # m/s^2
  CF_RATE = 0.9  # m/s^3

  CF_SETTLE_ACCEL = -0.6  # m/s^2
  CF_SETTLE_JERK = 0.72  # m/s^3
  CF_HOLD_RATE = 0.3  # m/s^2/s

  def __init__(self, stop_accel):
    self.stop_accel = stop_accel
    self.stop_confirm = StopConfirm()
    self.cf_t: float | None = None
    self.cf_vmax = 0.0
    self.cf_stopping = False
    self.cf_stopped = False
    self.standstill_t = 0.0
    self.stopping_t = 0.0
    self.go_t = 0.0
    self.engaged_t = 0.0
    self.stopped_once = False
    self.creep_t = 0.0
    self.end_active = False
    self.a_entry = self.END_HI
    self.releasing = False

  def _blend(self, v_ego):
    if v_ego < self.END_V_HI:
      return float(np.interp(max(v_ego, 0.0), self.END_CURVE_V, self.END_CURVE_A))
    return float(np.interp(v_ego, [self.END_V_HI, self.BLEND_V], [self.END_HI, self.a_entry]))

  def _end_request(self, a_target, prev_accel, v_ego):
    target = min(a_target, self._blend(v_ego))  # the firmer of the plan and the line
    step = self.END_RATE * DT_CTRL
    return float(np.clip(target, prev_accel - step, prev_accel + step))

  def _hold_floor(self, pitch, creeping):
    if creeping or pitch is None or not math.isfinite(pitch):
      return self.stop_accel
    if abs(math.degrees(pitch) - self.FLAT_PITCH_DEG) >= self.SLOPE_PITCH_DEG:
      return self.stop_accel
    return max(self.stop_accel, self.FLAT_HOLD_ACCEL)

  def _cf_request(self, a_target, prev_accel):
    target = float(np.interp(a_target, [self.CF_PLAN_FIRM, self.CF_PLAN_SOFT], [self.CF_PLAN_FIRM, self.CF_END]))
    target = min(target, a_target) if a_target < self.CF_PLAN_FIRM else target
    if target < prev_accel:
      return max(target, min(prev_accel, 0.0) - self.CF_RATE * DT_CTRL)
    return min(target, prev_accel + self.END_RATE * DT_CTRL)

  def _update_creep_follow(self, state, CS, a_target):
    if state == LongCtrlState.off:
      self.cf_t, self.cf_stopping, self.cf_stopped = None, False, False
      return False
    if CS.standstill:
      if self.cf_stopping:
        self.cf_stopped = True
      self.cf_t = 0.0 if self.standstill_t > 0.5 else self.cf_t
      self.cf_vmax, self.cf_stopping = 0.0, False
      return False
    self.cf_stopped = False
    if self.cf_t is None:
      return False
    self.cf_t += DT_CTRL
    self.cf_vmax = max(self.cf_vmax, CS.vEgo)
    if self.cf_t > self.CF_WINDOW or self.cf_vmax >= self.CF_V_MAX or a_target > 0.0 and self.cf_stopping:
      self.cf_t, self.cf_stopping = None, False
      return False
    if a_target <= self.CF_TRIGGER:
      self.cf_stopping = True
    return self.cf_stopping

  def update(self, prev_state, state, CS, a_target, prev_accel, stock_accel, accel_limits, has_lead=False, pitch=None,
             a_long=None):
    if prev_state == LongCtrlState.stopping and state == LongCtrlState.pid and CS.standstill:
      self.go_t += DT_CTRL
      if self.go_t < self.STOPPING_EXIT_DEBOUNCE:
        state = LongCtrlState.stopping
    else:
      self.go_t = 0.0

    self.standstill_t = self.standstill_t + DT_CTRL if CS.standstill else 0.0
    self.engaged_t = 0.0 if state == LongCtrlState.off else self.engaged_t + DT_CTRL
    self.stopping_t = self.stopping_t + DT_CTRL if state == LongCtrlState.stopping else 0.0
    if state != LongCtrlState.stopping:
      self.stopped_once = False
    elif CS.standstill:
      self.stopped_once = True

    creeping = self.stopped_once and not CS.standstill and CS.vEgo > self.CREEP_V_MIN
    self.creep_t = self.creep_t + DT_CTRL if creeping else 0.0
    cf_stop = self._update_creep_follow(state, CS, a_target)
    stop_confirmed = self.stop_confirm.update(CS.standstill, CS.vEgo, a_long)

    rolling = not CS.standstill and not self.stopped_once
    if state == LongCtrlState.off or not rolling or CS.vEgo >= self.BLEND_V or a_target > 0.0:
      self.end_active = False
    elif not self.end_active and a_target <= self.END_PLAN_MIN:
      self.end_active = True
      self.a_entry = min(prev_accel, self.END_HI)

    if state != LongCtrlState.stopping:
      if cf_stop:
        return state, float(np.clip(self._cf_request(a_target, prev_accel), accel_limits[0], accel_limits[1]))
      if self.end_active:
        return state, float(np.clip(self._end_request(a_target, prev_accel, CS.vEgo), accel_limits[0], accel_limits[1]))
      if prev_state == LongCtrlState.stopping and state == LongCtrlState.pid and prev_accel < self.RELEASE_BAND_HI:
        self.releasing = True
      if self.releasing:
        if stock_accel <= prev_accel or prev_accel >= self.RELEASE_BAND_HI or state == LongCtrlState.off:
          self.releasing = False
          return state, stock_accel
        rate = self.RELEASE_FAST if prev_accel < self.RELEASE_BAND_LO else self.RELEASE_SLOW
        return state, float(min(stock_accel, prev_accel + rate * DT_CTRL))
      return state, stock_accel

    output_accel = prev_accel
    hold_floor = self._hold_floor(pitch, creeping)
    if output_accel > hold_floor:
      output_accel = min(output_accel, 0.0)
      if not CS.standstill and not self.stopped_once and a_target < self.STOPPING_FOLLOW_MIN and a_target > output_accel:
        output_accel = min(a_target, output_accel + self.STOPPING_FOLLOW_RATE * DT_CTRL)
      if cf_stop:
        output_accel = self._cf_request(a_target, prev_accel)
      elif self.end_active:
        output_accel = self._end_request(a_target, prev_accel, CS.vEgo)

      hold_delay = self.STANDSTILL_HOLD_DELAY_LEAD if has_lead else self.STANDSTILL_HOLD_DELAY_NO_LEAD
      if CS.standstill and not has_lead and self.engaged_t < self.ENGAGE_STANDSTILL_GRACE:
        rate = 0.0
      elif self.cf_stopped and CS.standstill and output_accel > self.CF_SETTLE_ACCEL:
        output_accel = max(self.CF_SETTLE_ACCEL, output_accel - self.CF_SETTLE_JERK * DT_CTRL)
        rate = 0.0
      elif self.cf_stopped and CS.standstill:
        rate = self.CF_HOLD_RATE  # H: then the rest of the hold, slowly
      elif self.standstill_t >= hold_delay or stop_confirmed:
        rate = self.STANDSTILL_HOLD_RATE
      elif creeping and output_accel > self.REROLL_ACCEL:
        output_accel = max(self.REROLL_ACCEL, output_accel - self.REROLL_JERK * DT_CTRL)
        rate = 0.0
      elif creeping:
        rate = min(self.STOPPING_DECEL_RATE + self.CREEP_RATE_GROWTH * self.creep_t, self.CREEP_RATE_MAX)
      elif self.stopping_t >= self.STOPPING_FREEZE_MAX:
        rate = self.STOPPING_DECEL_RATE
      else:
        rate = 0.0
      if hold_floor != self.stop_accel:
        output_accel = max(output_accel - rate * DT_CTRL, min(hold_floor, output_accel))
      else:
        output_accel -= rate * DT_CTRL

    return state, float(np.clip(output_accel, accel_limits[0], accel_limits[1]))
