"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math

import numpy as np

from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState


# Confirmed stop. Owner 2026-10-08: "can the brake be added 0.2 s
# after the stop, but only when it is 100% certain the car has stopped?". The wheel-pulse standstill flag alone is not
# certain: on 2 of 30 engaged stops (route 00000100 18:59:09, 19:37:50) the pulse counter still stepped 0.06 s after
# it (~0.2 m). The body's own signature is: while the car still rolls it decelerates; at the real stop the deceleration
# collapses (the body pitches back). Using BOTH - the flag AND the longitudinal acceleration (calibrated pose) risen
# STOP_CONFIRM_RISE above the braking level it had above STOP_LEVEL_V - no wheel pulse followed in any of the 30 stops
# (routes fe..118). The hold then starts STOP_CONFIRM_DELAY later instead of after the 1.0 s hold delay; without a
# confirmation (a very light stop, no pitch-back) the 1.0 s delay applies as before.
STOP_LEVEL_V = 0.4  # m/s (~1.4 km/h): above this the braking level is tracked
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
  # once the wheels really stand (wheel pulse) and the hold delay has passed, press on firmly to stopAccel: the driver
  # presses to 1000-2400 N within 1-2 s of stopping (owner 2026-10-02: the car must not be able to move again, also on
  # a slope). 1.0 m/s^2/s reaches the default -2.0 (~2900 N) in ~1.9 s; the old 0.5 took ~3.7 s.
  STANDSTILL_HOLD_RATE = 1.0  # m/s^2/s
  # The standstill flag is the real wheel stop (wheel pulse counter). Driver 2026-10-05, after a slope stop at 15:53
  # where "at the last moment the hold locked early with a jerk": "let the car sit at -0.25 a while longer, then add the
  # parking force" -> 1.0 s at the end value before the ramp to stopAccel (was 0.2 s; the 10-03 "never more than 0.2 s"
  # was about the auto hold under a pedal, not this ramp). If the car creeps on a slope during that second the creep
  # path below raises the request on its own (CREEP_RATE_GROWTH), so the wait costs nothing on the flat and is bounded
  # on a hill.
  STANDSTILL_HOLD_DELAY_LEAD = 1.0  # s
  STANDSTILL_HOLD_DELAY_NO_LEAD = 1.0  # s
  STOPPING_FREEZE_MAX = 2.0  # s
  STOPPING_EXIT_DEBOUNCE = 0.2  # s
  # Engaging at a standstill (driver 2026-10-06, route 0000010a 23:58:49: "pulling away with no lead, just before the car
  # really moves there is a very short hard brake, then it goes"). The car stood in the auto hold (1360 N); engaging
  # dropped the hold to 0 N, the plan's first frame still said stop, so the stopping state started the standstill hold
  # ramp at once (it had stood long past the hold delay) - -0.21 m/s^2 within 0.2 s, which the PCM turned into a
  # 1600 N brake pulse (IMU +0.6 m/s^2 jolt) before the launch 0.4 s later. For ENGAGE_STANDSTILL_GRACE after engaging
  # at a standstill with no lead the request stays at zero instead: the launch follows straight away; if the plan
  # really wants to stay stopped, the hold ramp starts after the grace.
  ENGAGE_STANDSTILL_GRACE = 0.6  # s
  STOPPING_FOLLOW_MIN = -0.10  # m/s^2
  STOPPING_FOLLOW_RATE = 2.0  # m/s^3
  CREEP_V_MIN = 0.03  # m/s
  CREEP_RATE_GROWTH = 1.5  # m/s^2/s per second of creep
  CREEP_RATE_MAX = 1.0  # m/s^2/s

  # The end of the stop. First road test of the template rule (route 000000ec, 2026-10-03, four op stops): holding
  # END_REQUEST -0.15 (~660 N) from 3 km/h was a STEP - the plan was at -0.63..-0.78 (1160-1560 N) when the car crossed
  # 3 km/h and the request fell to -0.15 within 0.3 s; the force dropped to 280-520 N, the car sped UP again (+0.1..+0.3
  # m/s^2, 1.7 -> 2.5 km/h) on its creep torque and then needed 3.4-4.3 s and 760-1000 N (-0.2..-0.25 m/s^2) to stop.
  # The driver felt exactly that: "at 3 km/h the brake suddenly lightens - wrong - there must be a smooth hand-over".
  # The driver's own hard stop that night (23:45:04, 36 km/h, 4880 N peak) still ended smoothly because the pedal came
  # off CONTINUOUSLY: -aEgo ~ 1.6 + 0.25 v (r 0.86), -3.4 m/s^2 at 27 km/h, -2.6 at 10, -1.4 at 3, -1.0 at 1 km/h -
  # the decel falls roughly linearly with speed to the wheel stop, never a step, and does not go light at the end.
  # So below BLEND_V the request follows a line in speed from the request it had at BLEND_V (a_entry) down to
  # END_REQUEST at 0 km/h: blend(v) = END_REQUEST + (a_entry - END_REQUEST) * (v / BLEND_V) ** BLEND_POW. It is a FLOOR
  # on the plan: the firmer of the plan and the line is sent, so the planner's own curve still wins while it is braking
  # harder (a late-seen lead), and the line takes over only where the planner eases off. A plan that wants to go
  # (a_target > 0, the lead moved off) releases it; after standstill the hold ramp to stopAccel applies unchanged.
  # END_REQUEST -0.50 (~1080 N by BF ~ 480 + 1200 * |req|) is the lightest request that still decelerates under ACC:
  # on this route 760-1000 N gave only -0.2..-0.25 m/s^2 (the pedal is not pressed, so the hybrid keeps its creep
  # torque), while -0.63..-0.78 gave -0.6..-1.07 at 3 km/h. The driver's template ends at 0.5-0.7 m/s^2.
  # Driver 2026-10-03 afternoon, after the -0.50 / -0.40 / -0.35 flat ends: "from 5 km/h to 0 use a formula: -0.5 at
  # 5 km/h, -0.3 at 0 km/h, interpolated - firmer at 5 km/h, then easing as the car comes to rest". So the line is
  # now piecewise linear through (BLEND_V, a_entry) -> (END_V_HI, END_HI) -> (0, END_LO); a_entry is at least END_HI.
  BLEND_V = 10.0 / 3.6  # m/s: the line starts here, at the request the car had at that moment
  END_V_HI = 5.0 / 3.6  # m/s
  END_HI = -0.65  # m/s^2 at END_V_HI (~1200 N); -0.60 -> -0.65 2026-10-08, see END_CURVE_A
  END_LO = -0.30  # m/s^2 at 0-1 km/h; driver 2026-10-04: -0.30 "closer to perfect", -0.25 the threshold; 2026-10-06 back to -0.30
  # Driver 2026-10-04 (route 000000f2): "between 5 and 0 km/h not linear but parabolic: steeper from 5 to 2, flat from
  # 2 to 0" -> x^2 parabola -0.50/-0.41/-0.34/-0.29/-0.26/-0.25 ("closer to perfect"). An S-shaped table
  # (-0.50/-0.47/-0.40/-0.29/-0.25/-0.24) was "not better" and reverted. Then the driver gave his own points, close to
  # the parabola but a touch lighter in the middle: 4 km/h -0.40, 3 -0.33, 2 -0.27, 1 -0.25, 0 -0.25. Held as a table,
  # linearly interpolated at the actual speed every 10 ms (continuous curve).
  END_CURVE_V = [0.0, 1.0 / 3.6, 2.0 / 3.6, 3.0 / 3.6, 4.0 / 3.6, 5.0 / 3.6]  # m/s
  # Driver 2026-10-06 (route 00000100, seven manual stops 19:45-19:59, averages 5->2 km/h 0.83, 2->0.3 km/h 0.45 m/s^2;
  # the lightest steady one, 19:56:19, 0.56 / 0.37): "the manual stops are still a touch heavy; give 5-2 km/h a little
  # more, but already be light at 1 km/h, or reaching -0.25 only at 0 km/h may still nod; keep 1-0 as it was". So a
  # parabola with its flat top at 5 km/h (END_HI) that bends down to END_LO by 1 km/h, then flat END_LO to the stop:
  # a = END_LO + (END_HI - END_LO) * (1 - ((5 - v) / 4)^2) -> -0.60/-0.58/-0.51/-0.40/-0.25/-0.25 at 5..0 km/h.
  # Driver 2026-10-06 night: "the end of the stop is not ideal, make 1-0 -0.3": END_LO -0.30, same parabola above it
  # -> -0.60/-0.58/-0.53/-0.43/-0.30/-0.30.
  # Driver 2026-10-08 (routes 00000112-00000116): "just before the stop, around 4-2 km/h, the brake feels released a little
  # too much". Since the low-speed PID hold (c14c0dbae1) the integrator no longer adds its catch-up there, and the car
  # delivered -0.44 / -0.55 / -0.49 / -0.45 at 5-4 / 4-3 / 3-2 / 2-1 km/h (BRAKE 0xA6 870-1010 N) against ~-0.7 / -0.7 /
  # -0.6 before. Driver chose the table 5 km/h -0.65, 4 -0.65, 3 -0.60, 2 -0.48, 1-0 -0.30 unchanged (expected delivered
  # ~-0.61 / -0.55 / -0.48 at 4-3 / 3-2 / 2-1 km/h). Was -0.60/-0.58/-0.53/-0.43/-0.30/-0.30.
  END_CURVE_A = [END_LO, END_LO, -0.48, -0.60, -0.65, END_HI]  # m/s^2
  END_PLAN_MIN = -0.25  # m/s^2: the plan must be braking this much at BLEND_V to count as stopping (a crawl-follow hovers near 0)
  END_RATE = 2.0  # m/s^3: how fast the request may move toward the line

  # Leaving the standstill hold (driver 2026-10-04, route 000000fa 14:43:32: "the brake release at launch is a jerk, as
  # if let go suddenly; make it linear and slow"). There the request went from the -2.0 hold (3960 N) to +0.7 in 0.5 s
  # at the Toyota windup limit: the PCM bled 3960 -> 0 N in 0.6 s while the gas request was already +0.6, and the car
  # lurched at +1.7 m/s^2 for the first 0.1 s. The brake pressure cannot move the car while the request is well below
  # zero, so the release keeps the fast rate down there and goes LINEAR AND SLOW only through the hand-over band where
  # the clamp falls off and the creep torque takes over: RELEASE_FAST up to RELEASE_BAND_LO, RELEASE_SLOW from there
  # up to RELEASE_BAND_HI, then the plan again. The first motion comes ~0.1 s later than before, the lurch is gone.
  RELEASE_FAST = 4.0  # m/s^3 (the stock windup limit)
  RELEASE_SLOW = 1.5  # m/s^3
  RELEASE_BAND_LO = -0.6  # m/s^2
  RELEASE_BAND_HI = 0.4  # m/s^2

  # The tnpb2 additions below run on every car.
  # B - re-roll at a standstill. Route 0000010e 17:38:48: the car stood behind the lead at the
  # end request -0.30 (BRAKE 0xA6 640 N, less than the ~760-800 N the hybrid's creep torque needs); 0.9 s later, still
  # inside the 1.0 s hold delay, all four wheel speeds read 0.8 km/h for 1.1 s (the pulse counter did not step: < 0.2 m)
  # while the creep path raised the request only at 0.3 -> 1.0 m/s^2/s; it stood again once the force reached ~1300 N
  # (-0.8). Now, once the car moves again after it has stood (creeping), the request steps down to REROLL_ACCEL at
  # REROLL_JERK (0.05 s from -0.30), then continues on the creep / hold path. A car that stays still is not affected.
  REROLL_ACCEL = -0.6  # m/s^2 (~1100 N or more)
  REROLL_JERK = 6.0  # m/s^3
  # C - lighter standstill hold on the flat. The launch from a standstill takes 2.1 s
  # (median, routes fc..10e) from the lead moving to the wheels moving, against 1.7 s before 2026-10-04; most of the
  # wait is the PCM bleeding the -2.0 hold (3240 N, BRAKE 0xA6) - 1.1 s from 3240 N to 0 on route 0000010d 23:56:58.
  # On the flat the hold now stops at FLAT_HOLD_ACCEL (~2000 N, still 2.5x the creep torque and above the 1360 N the
  # auto brake hold uses on the flat); on a slope (|pitch - FLAT_PITCH_DEG| >= SLOPE_PITCH_DEG, as in auto_brake_hold)
  # or without a pitch, or while the car creeps, the stock stopAccel applies.
  FLAT_HOLD_ACCEL = -1.2  # m/s^2
  FLAT_PITCH_DEG = 1.0  # deg, what this car reports standing on the flat
  SLOPE_PITCH_DEG = 2.0  # deg away from flat that counts as a slope
  # H - creep-follow stop. Owner 2026-10-07: "at a standstill the lead moves a little, we
  # follow and stop again - still not soft; release smoothly, roll forward, then stop smoothly with -0.24". Route
  # 0000010d 23:56:59: after the release the plan turned to -0.4 within 0.2 s, but the command stayed positive for
  # ~0.7 s (soft-onset shaper + a PID integral left from the launch), the end-of-stop line asked -0.48 at 2.5 km/h, and
  # the brake bit 0 -> 1640 N in 0.4 s (aEgo +0.36 -> -0.88). Now, when the car has left a standstill less than
  # CF_WINDOW ago and has not gone faster than CF_V_MAX, a stop asked by the plan (a_target <= CF_TRIGGER) is made with
  # CF_END to the wheel stop: any positive request is dropped at once, the braking side is entered at CF_RATE (below the
  # onset shaper's threshold, so it passes unshaped), and the end-of-stop line is not used. The plan still wins when it
  # needs more: from CF_PLAN_SOFT the request blends to the plan, which it follows below CF_PLAN_FIRM (a lead that
  # brakes, or the gap closing because -0.24 is too little). A plan that wants to go (a_target > 0) ends it.
  CF_WINDOW = 10.0  # s
  CF_V_MAX = 8.0 / 3.6  # m/s
  CF_TRIGGER = -0.15  # m/s^2
  CF_END = -0.24  # m/s^2
  CF_PLAN_SOFT = -0.45  # m/s^2
  CF_PLAN_FIRM = -0.70  # m/s^2
  CF_RATE = 0.9  # m/s^3
  # ... and once the wheels stop after such a creep-follow stop (owner 2026-10-07, route 00000112 23:16:57: "stopped
  # with -0.24, then the hold came as a second brake"; there the request sat at -0.24 (~650 N, less than the creep
  # torque) for the 1.0 s hold delay, then ramped to -1.2 within ~1 s - two separate pushes. Owner: "if it stops with
  # -0.24, just add a little brake after the stop"): the brake is added straight away and smoothly, CF_SETTLE_ACCEL
  # within ~0.5 s (CF_SETTLE_JERK), enough to hold the creep torque, then the rest of the hold very slowly
  # (CF_HOLD_RATE) - one continuous motion, no hold delay. A re-roll still goes through B.
  CF_SETTLE_ACCEL = -0.6  # m/s^2 (~1100 N)
  CF_SETTLE_JERK = 0.72  # m/s^3: -0.24 -> -0.6 in 0.5 s
  CF_HOLD_RATE = 0.3  # m/s^2/s: -0.6 -> -1.2 in 2 s

  def __init__(self, stop_accel):
    self.stop_accel = stop_accel
    self.stop_confirm = StopConfirm()
    self.cf_t: float | None = None  # time since leaving a standstill (creep-follow window)
    self.cf_vmax = 0.0
    self.cf_stopping = False
    self.cf_stopped = False  # the wheels stopped at the end of a creep-follow stop
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

    # end-of-stop window: rolling below BLEND_V with a plan that is braking to a stop
    rolling = not CS.standstill and not self.stopped_once
    if state == LongCtrlState.off or not rolling or CS.vEgo >= self.BLEND_V or a_target > 0.0:
      self.end_active = False
    elif not self.end_active and a_target <= self.END_PLAN_MIN:
      self.end_active = True
      self.a_entry = min(prev_accel, self.END_HI)  # the line starts where the request is now, at least END_HI

    if state != LongCtrlState.stopping:
      if cf_stop:
        return state, float(np.clip(self._cf_request(a_target, prev_accel), accel_limits[0], accel_limits[1]))
      if self.end_active:
        return state, float(np.clip(self._end_request(a_target, prev_accel, CS.vEgo), accel_limits[0], accel_limits[1]))
      # coming off the hold: linear, slow through the hand-over band (see RELEASE_*)
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
        # still rolling inside the end window: the line (or the plan where it is firmer), never the eased-off curve
        output_accel = self._end_request(a_target, prev_accel, CS.vEgo)

      hold_delay = self.STANDSTILL_HOLD_DELAY_LEAD if has_lead else self.STANDSTILL_HOLD_DELAY_NO_LEAD
      if CS.standstill and not has_lead and self.engaged_t < self.ENGAGE_STANDSTILL_GRACE:
        rate = 0.0  # just engaged at a standstill: no brake pulse before the launch
      elif self.cf_stopped and CS.standstill and output_accel > self.CF_SETTLE_ACCEL:
        output_accel = max(self.CF_SETTLE_ACCEL, output_accel - self.CF_SETTLE_JERK * DT_CTRL)  # H: a little brake now
        rate = 0.0
      elif self.cf_stopped and CS.standstill:
        rate = self.CF_HOLD_RATE  # H: then the rest of the hold, slowly
      elif self.standstill_t >= hold_delay or stop_confirmed:
        rate = self.STANDSTILL_HOLD_RATE
      elif creeping and output_accel > self.REROLL_ACCEL:
        output_accel = max(self.REROLL_ACCEL, output_accel - self.REROLL_JERK * DT_CTRL)  # B: moving again - hold now
        rate = 0.0
      elif creeping:
        rate = min(self.STOPPING_DECEL_RATE + self.CREEP_RATE_GROWTH * self.creep_t, self.CREEP_RATE_MAX)
      elif self.stopping_t >= self.STOPPING_FREEZE_MAX:
        rate = self.STOPPING_DECEL_RATE
      else:
        rate = 0.0
      if hold_floor != self.stop_accel:
        output_accel = max(output_accel - rate * DT_CTRL, min(hold_floor, output_accel))  # C: stop at the flat hold
      else:
        output_accel -= rate * DT_CTRL

    return state, float(np.clip(output_accel, accel_limits[0], accel_limits[1]))
