"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from types import SimpleNamespace

from openpilot.common.realtime import DT_CTRL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.sunnypilot.selfdrive.controls.lib.stopping_controller import StoppingController

LIMITS = (-3.5, 2.0)
PID, STOPPING, OFF = LongCtrlState.pid, LongCtrlState.stopping, LongCtrlState.off
END_LO, END_HI = StoppingController.END_LO, StoppingController.END_HI


def cs(v_kph, standstill=False):
  return SimpleNamespace(vEgo=v_kph / 3.6, standstill=standstill)


def run(sc, state, car, a_target, prev, secs, stock=None):
  """step the controller for secs with a fixed plan; returns the last output"""
  out = prev
  for _ in range(int(secs / DT_CTRL)):
    _, out = sc.update(state, state, car, a_target, out, a_target if stock is None else stock, LIMITS, has_lead=True)
  return out


def blend(sc, v_kph):
  return sc._blend(v_kph / 3.6)


class TestEndOfStop(OpenpilotTestCase):
  def test_the_line_runs_from_the_entry_request_through_5kph_to_the_rest_value(self):
    sc = StoppingController(-2.0)
    out = run(sc, PID, cs(9.9), -1.20, -1.20, 0.2)
    assert sc.end_active and abs(sc.a_entry - (-1.20)) < 1e-6
    # 7.5 km/h: halfway between the entry request and END_HI; the planner has eased to -0.30, the line is sent
    out = run(sc, PID, cs(7.5), -0.30, out, 0.6)
    assert abs(blend(sc, 7.5) - (-1.20 + (END_HI - -1.20) * 0.5)) < 1e-6
    assert abs(out - blend(sc, 7.5)) < 1e-6
    # 5 km/h: END_HI; below it a parabola: steep first, flat toward the rest value; the wheel stop: END_LO
    out = run(sc, PID, cs(5.0), -0.20, out, 0.4)
    assert abs(out - END_HI) < 1e-6
    out = run(sc, PID, cs(2.5), -0.20, out, 0.4)
    assert abs(out - (-0.48 + -0.60) / 2) < 1e-6
    assert abs(blend(sc, 4.0) - (-0.65)) < 1e-6 and abs(blend(sc, 1.0) - (-0.30)) < 1e-6
    assert abs(blend(sc, 0.5) - (-0.30)) < 1e-6   # 1-0 km/h unchanged
    out = run(sc, PID, cs(0.0), -0.20, out, 0.4)
    assert abs(out - END_LO) < 1e-6

  def test_the_line_is_a_floor_a_firmer_plan_still_passes(self):
    sc = StoppingController(-2.0)
    out = run(sc, PID, cs(9.9), -1.20, -1.20, 0.2)
    out = run(sc, PID, cs(5.0), -1.10, out, 0.5)
    assert abs(out - (-1.10)) < 1e-6
    out = run(sc, PID, cs(2.5), -1.8, out, 0.6)
    assert abs(out - (-1.8)) < 1e-6

  def test_a_light_plan_at_entry_starts_the_line_at_end_hi(self):
    sc = StoppingController(-2.0)
    light = END_HI + 0.1
    out = run(sc, PID, cs(7.0), light, light, 0.5)
    assert abs(sc.a_entry - END_HI) < 1e-6
    assert abs(out - END_HI) < 1e-6
    # the planner's own curve eases off below 5 km/h: the request follows the line, never the plan
    out = run(sc, PID, cs(2.5), -0.10, out, 0.5)
    assert abs(out - blend(sc, 2.5)) < 1e-6

  def test_entry_is_rate_limited(self):
    sc = StoppingController(-2.0)
    light = END_HI + 0.2
    _, out = sc.update(PID, PID, cs(7.0), light, light, light, LIMITS, has_lead=True)
    assert out > END_HI
    assert abs(out - (light - StoppingController.END_RATE * DT_CTRL)) < 1e-6

  def test_an_emergency_plan_still_passes(self):
    sc = StoppingController(-2.0)
    out = run(sc, PID, cs(2.5), -1.8, -0.40, 0.8)
    assert abs(out - (-1.8)) < 1e-6

  def test_crawl_follow_is_untouched(self):
    sc = StoppingController(-2.0)
    out = run(sc, PID, cs(2.0), -0.10, -0.10, 0.5)
    assert abs(out - (-0.10)) < 1e-6
    assert not sc.end_active

  def test_above_blend_v_nothing_changes(self):
    sc = StoppingController(-2.0)
    out = run(sc, PID, cs(12.0), -0.40, -0.40, 0.5)
    assert abs(out - (-0.40)) < 1e-6
    assert not sc.end_active

  def test_lead_moving_off_releases_the_hold(self):
    sc = StoppingController(-2.0)
    run(sc, PID, cs(2.0), -0.60, -0.60, 0.5)
    assert sc.end_active
    _, out = sc.update(PID, PID, cs(1.5), 0.50, END_LO, 0.50, LIMITS, has_lead=True)
    assert not sc.end_active and abs(out - 0.50) < 1e-6

  def test_stopping_state_keeps_the_line_until_the_wheels_stop_then_holds(self):
    sc = StoppingController(-1.0)
    run(sc, PID, cs(2.0), END_HI, END_HI, 0.5)
    # 1 km/h, stopping state, the planner's curve has eased to -0.10: Kumar's lighter-follow would ease the request
    out = run(sc, STOPPING, cs(1.0), -0.10, blend(sc, 2.0), 0.4)
    assert abs(out - blend(sc, 1.0)) < 1e-6
    # wheels stop: the last value of the line is held until the hold delay, then ramps to stopAccel at the hold rate
    out_at_stop = run(sc, STOPPING, cs(0.0, standstill=True), -0.10, out, 0.9)
    assert abs(out_at_stop - out) < 1e-6 and END_HI < out_at_stop <= END_LO + 1e-6
    out_held = run(sc, STOPPING, cs(0.0, standstill=True), -0.10, out_at_stop, 1.0)
    assert out_held < out_at_stop - 0.3
    assert out_held >= -1.0 - 1e-6


class TestHoldRelease(OpenpilotTestCase):
  """2026-10-04 14:43: leaving the hold is fast while the request is far below zero, then linear and slow through the
  hand-over band, and the plan is never exceeded."""

  def test_release_is_slow_through_the_handover_band(self):
    sc = StoppingController(-2.0)
    out = -2.0
    t = 0.0
    t_lo = t_hi = None
    state = STOPPING  # controlsd feeds the returned state back as prev_state (the 0.2 s exit debounce lives there)
    for _ in range(300):
      state, out = sc.update(state, PID, cs(0.0, standstill=True), 0.8, out, 0.8, LIMITS, has_lead=True)
      t += DT_CTRL
      if t_lo is None and out >= StoppingController.RELEASE_BAND_LO:
        t_lo = t
      if t_hi is None and out >= StoppingController.RELEASE_BAND_HI:
        t_hi = t
      assert out <= 0.8 + 1e-9
    assert t_lo is not None and t_lo < 0.6           # 0.2 s debounce, then -2.0 -> -0.6 at the fast rate (0.35 s)
    assert t_hi is not None and 1.15 < t_hi < 1.3    # then -0.6 -> +0.4 at 1.5 m/s^3 (0.67 s)
    assert abs(out - 0.8) < 1e-9 and not sc.releasing

  def test_a_plan_that_drops_again_ends_the_release(self):
    sc = StoppingController(-2.0)
    state, out = STOPPING, -2.0
    for _ in range(30):  # through the exit debounce
      state, out = sc.update(state, PID, cs(0.0, standstill=True), 0.5, out, 0.5, LIMITS, has_lead=True)
    assert sc.releasing and -2.0 < out < 0.5
    _, out = sc.update(state, PID, cs(0.0, standstill=True), -2.0, out, -2.0, LIMITS, has_lead=True)
    assert abs(out - (-2.0)) < 1e-9 and not sc.releasing


class TestEngageAtStandstill(OpenpilotTestCase):
  def _engage(self, has_lead, secs):
    sc = StoppingController(-2.0)
    car = cs(0.0, standstill=True)
    for _ in range(300):  # standing in the auto hold, openpilot not engaged
      sc.update(OFF, OFF, car, 0.0, 0.0, 0.0, LIMITS, has_lead=has_lead)
    out = 0.0
    for _ in range(int(secs / DT_CTRL)):
      _, out = sc.update(STOPPING, STOPPING, car, 0.0, out, 0.0, LIMITS, has_lead=has_lead)
    return out, sc

  def test_no_brake_pulse_right_after_engaging_without_lead(self):
    # route 0000010a 23:58:49: the hold ramp reached -0.21 in 0.2 s and the PCM braked 1600 N before the launch
    out, sc = self._engage(False, 0.5)
    assert out == 0.0

  def test_the_hold_ramp_follows_after_the_grace(self):
    out, sc = self._engage(False, StoppingController.ENGAGE_STANDSTILL_GRACE + 0.3)
    assert out < -0.2

  def test_with_a_lead_the_hold_starts_at_once(self):
    out, _ = self._engage(True, 0.3)
    assert out < -0.2


def stand(sc, secs, out=StoppingController.END_LO, pitch=None, a_target=-0.1):
  state = STOPPING
  for _ in range(int(secs / DT_CTRL)):
    state, out = sc.update(state, STOPPING, cs(0.0, standstill=True), a_target, out, a_target, LIMITS, has_lead=True, pitch=pitch)
  return out


FLAT = math.radians(1.0)
SLOPE = math.radians(-4.0)


class TestRerollHold(OpenpilotTestCase):
  """route 0000010e 17:38:48: stood at -0.30, rolled at 0.8 km/h for 1.1 s inside the hold delay"""

  def _reroll(self, sc):
    out = stand(sc, 0.9)
    state = STOPPING
    outs = []
    for _ in range(20):
      state, out = sc.update(state, STOPPING, cs(0.8), -0.05, out, -0.05, LIMITS, has_lead=True)
      outs.append(out)
    return outs

  def test_steps_to_the_reroll_request_within_0_1s(self):
    outs = self._reroll(StoppingController(-2.0))
    assert outs[4] <= StoppingController.REROLL_ACCEL + 1e-9   # 0.05 s
    assert all(b - a >= -StoppingController.REROLL_JERK * DT_CTRL - 1e-9 for a, b in zip(outs, outs[1:], strict=False))


class TestFlatHold(OpenpilotTestCase):
  def test_flat_hold_stops_at_minus_1_2(self):
    out = stand(StoppingController(-2.0), 4.0, pitch=FLAT)
    assert abs(out - StoppingController.FLAT_HOLD_ACCEL) < 1e-9

  def test_slope_or_no_pitch_keeps_stop_accel(self):
    assert stand(StoppingController(-2.0), 4.0, pitch=SLOPE) <= -2.0 + 1e-6
    assert stand(StoppingController(-2.0), 4.0, pitch=None) <= -2.0 + 1e-6

  def test_a_creep_on_the_flat_hold_goes_deeper(self):
    sc = StoppingController(-2.0)
    out = stand(sc, 4.0, pitch=FLAT)
    state = STOPPING
    for _ in range(150):
      state, out = sc.update(state, STOPPING, cs(0.8), -0.1, out, -0.1, LIMITS, has_lead=True, pitch=FLAT)
    assert out < StoppingController.FLAT_HOLD_ACCEL - 0.5


class TestCreepFollowStop(OpenpilotTestCase):
  """route 0000010d 23:56:59: lead moved ~2 m, the car followed at 2.5 km/h and the brake bit at -0.88"""

  def _creep(self, sc, plan, v_kph=2.0, secs=2.0, out=0.4):
    stand(sc, 2.0)
    outs = []
    for _ in range(int(secs / DT_CTRL)):
      _, out = sc.update(PID, PID, cs(v_kph), plan, out, plan, LIMITS, has_lead=True)
      outs.append(out)
    return outs

  def test_stops_with_minus_0_24_not_the_end_line(self):
    outs = self._creep(StoppingController(-2.0), -0.40)
    assert outs[0] <= 0.0                       # a positive request is dropped at once
    assert abs(outs[-1] - StoppingController.CF_END) < 1e-9
    steps = [a - b for a, b in zip(outs, outs[1:], strict=False)]
    assert max(steps) <= StoppingController.CF_RATE * DT_CTRL + 1e-9

  def test_a_firm_plan_still_wins(self):
    outs = self._creep(StoppingController(-2.0), -1.0)
    assert abs(outs[-1] - (-1.0)) < 1e-9

  def test_light_plan_keeps_minus_0_24_to_the_stop(self):
    sc = StoppingController(-2.0)
    outs = self._creep(sc, -0.40, secs=1.0)
    _, out = sc.update(PID, PID, cs(1.0), -0.10, outs[-1], -0.10, LIMITS, has_lead=True)
    assert abs(out - StoppingController.CF_END) < 1e-9

  def test_not_after_a_real_launch(self):
    sc = StoppingController(-2.0)
    stand(sc, 2.0)
    out = 0.5
    for _ in range(300):
      _, out = sc.update(PID, PID, cs(15.0), 0.3, out, 0.3, LIMITS, has_lead=True)
    _, out = sc.update(PID, PID, cs(6.0), -0.40, out, -0.40, LIMITS, has_lead=True)
    assert sc.cf_t is None

  def test_lead_moving_off_ends_it(self):
    sc = StoppingController(-2.0)
    outs = self._creep(sc, -0.40, secs=0.5)
    _, out = sc.update(PID, PID, cs(2.0), 0.5, outs[-1], 0.5, LIMITS, has_lead=True)
    assert out == 0.5 and not sc.cf_stopping

  def test_after_the_creep_stop_a_little_brake_at_once_then_the_hold_slowly(self):
    """route 00000112 23:16:57: -0.24 for the 1.0 s hold delay, then -1.2 within ~1 s felt like a second brake"""
    sc = StoppingController(-2.0)
    outs = self._creep(sc, -0.40)
    out, state, trace = outs[-1], STOPPING, []
    for _ in range(300):
      state, out = sc.update(state, STOPPING, cs(0.0, standstill=True), -0.05, out, -0.05, LIMITS, has_lead=True,
                             pitch=FLAT)
      trace.append(out)
    assert trace[50] <= StoppingController.CF_SETTLE_ACCEL + 1e-9          # -0.6 within 0.5 s, no hold delay
    assert trace[10] > StoppingController.CF_SETTLE_ACCEL                    # but gradually
    assert abs(trace[150] - (StoppingController.CF_SETTLE_ACCEL - 1.0 * StoppingController.CF_HOLD_RATE)) < 0.02
    assert abs(trace[-1] - StoppingController.FLAT_HOLD_ACCEL) < 1e-9       # the flat hold after ~2.5 s
    steps = [a - b for a, b in zip(trace, trace[1:], strict=False)]
    assert max(steps) <= StoppingController.CF_SETTLE_JERK * DT_CTRL + 1e-9

  def test_an_ordinary_stop_keeps_the_hold_delay(self):
    sc = StoppingController(-2.0)
    out = stand(sc, 0.9, pitch=FLAT)
    assert abs(out - END_LO) < 1e-9


class TestConfirmedStopEarlyHold(OpenpilotTestCase):
  """hold 0.2 s after a CONFIRMED stop (standstill flag + the body's deceleration collapsing), else the 1.0 s delay"""

  def _stop(self, sc, collapse):
    out, state = -0.40, PID
    for k in range(100):  # rolling to the stop at -0.45 m/s^2 (body)
      state, out = sc.update(state, STOPPING, cs(2.0 - 0.019 * k), -0.3, out, -0.3, LIMITS, has_lead=True, pitch=FLAT, a_long=-0.45)
    trace = []
    for k in range(150):  # standing: the body pitches back (deceleration collapses) after 0.1 s, or not
      a = -0.05 if (collapse and k >= 10) else -0.45
      state, out = sc.update(state, STOPPING, cs(0.0, True), -0.05, out, -0.05, LIMITS, has_lead=True, pitch=FLAT, a_long=a)
      trace.append(out)
    return trace

  def test_confirmed_stop_holds_after_0_2s(self):
    sc = StoppingController(-2.0)
    tr = self._stop(sc, True)
    assert tr[25] == tr[0]                 # 0.1 s to the pitch-back + 0.2 s: nothing yet at 0.25 s
    assert tr[40] < tr[0] - 0.05           # holding by 0.4 s

  def test_no_confirmation_keeps_the_1s_delay(self):
    sc = StoppingController(-2.0)
    tr = self._stop(sc, False)
    assert tr[90] == tr[0] and tr[110] < tr[0]

  def test_no_pose_keeps_the_1s_delay(self):
    sc = StoppingController(-2.0)
    assert not sc.stop_confirm.update(True, 0.0, None)
