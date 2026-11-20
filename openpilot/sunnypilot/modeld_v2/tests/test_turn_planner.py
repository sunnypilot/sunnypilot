"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan
from openpilot.sunnypilot.modeld_v2.turn_planner import TurnPlanner, compute_plan_peak_curv


def make_plan(curv: float, speed: float = 4.0) -> dict[str, np.ndarray]:
  """Build a synthetic model_output dict with a constant-curvature arc plan."""
  t = np.array(ModelConstants.T_IDXS, dtype=np.float32)
  s = speed * t
  plan = np.zeros((1, len(t), ModelConstants.PLAN_WIDTH), dtype=np.float32)
  if abs(curv) < 1e-6:
    plan[0, :, Plan.POSITION][:, 0] = s
    plan[0, :, Plan.POSITION][:, 1] = 0.0
    plan[0, :, Plan.T_FROM_CURRENT_EULER][:, 2] = 0.0
  else:
    r = 1.0 / curv
    theta = s * curv
    plan[0, :, Plan.POSITION][:, 0] = r * np.sin(theta)
    plan[0, :, Plan.POSITION][:, 1] = r * (1.0 - np.cos(theta))
    plan[0, :, Plan.T_FROM_CURRENT_EULER][:, 2] = theta
  return {'plan': plan}


class TestTurnPlanner(OpenpilotTestCase):
  def test_plan_peak_curv_extraction(self):
    assert abs(compute_plan_peak_curv(make_plan(0.0, 5.0))) < 1e-5
    pk = compute_plan_peak_curv(make_plan(0.12, 4.0))
    assert abs(pk - 0.12) < 0.01
    pk_l = compute_plan_peak_curv(make_plan(-0.15, 4.0))
    assert abs(pk_l + 0.15) < 0.01
    assert compute_plan_peak_curv({}) == 0.0

  def test_untouched_at_highway_speed(self):
    tp = TurnPlanner(wheelbase=2.89)
    for i in range(60):
      k = 0.01 * math.sin(i * 0.1)
      out = tp.update(make_plan(k, 25.0), v_ego=25.0, actual_curv=k, active=True, is_rhd=False, model_curv=k)
      assert out == k

  def test_untouched_on_gentle_low_speed_curve(self):
    tp = TurnPlanner(wheelbase=2.89)
    for i in range(80):
      k = 0.025 * min(1.0, i / 20.0)
      out = tp.update(make_plan(k, 6.0), v_ego=6.0, actual_curv=k, active=True, is_rhd=False, model_curv=k)
      assert out == k

  def test_sign_preservation_and_magnitude_bound_under_jitter(self):
    """Output must never oppose model_curv or exceed |model_curv|, even after entry jitter."""
    tp = TurnPlanner(wheelbase=2.89)
    # Reproduces a5 seg31 Turn 1: brief negative jitter then sharp positive right turn
    ks = [-0.015] * 15 + [0.016, 0.05, 0.11, 0.14, 0.17, 0.18, 0.14, 0.08, 0.02, -0.01]
    plan_right = make_plan(0.15, 3.0)
    for k in ks:
      out = tp.update(plan_right, v_ego=3.0, actual_curv=k * 0.7, active=True, is_rhd=False, model_curv=k)
      assert abs(out) <= abs(k) + 1e-9
      if k > 0:
        assert out >= 0.0
      elif k < 0:
        assert out <= 0.0

  def test_zero_lag_on_turn_exit_unwinding(self):
    tp = TurnPlanner(wheelbase=2.89)
    plan_tight = make_plan(0.14, 4.0)
    # Ramp up entry and hold through apex so buffer is at peak curvature
    for i in range(25):
      k = 0.14 * (i / 25.0)
      tp.update(plan_tight, v_ego=4.0, actual_curv=k * 0.8, active=True, is_rhd=False, model_curv=k)
    for _ in range(15):
      tp.update(plan_tight, v_ego=4.0, actual_curv=0.14, active=True, is_rhd=False, model_curv=0.14)
    # Now unwind monotonically: output must equal model_curv with zero lag
    for i in range(1, 20):
      k = max(0.0, 0.14 * (1.0 - i / 15.0))
      out = tp.update(make_plan(k, 4.0), v_ego=4.0, actual_curv=k + 0.01, active=True, is_rhd=False, model_curv=k)
      assert abs(out - k) < 1e-9

  def test_standstill_launch_and_mid_turn_pause(self):
    tp = TurnPlanner(wheelbase=2.89)
    # Stopped straight at stop bar, then launches into a sharp right turn
    for _ in range(10):
      tp.update(make_plan(0.12, 0.0), v_ego=0.0, actual_curv=0.0, active=True, is_rhd=False, model_curv=0.002)
    # First few steps of launch should hold back early curvature ramp
    outs = []
    for i in range(1, 20):
      k = 0.006 * i
      outs.append(tp.update(make_plan(0.12, 2.5), v_ego=2.5, actual_curv=0.004 * i, active=True, is_rhd=False, model_curv=k))
    assert outs[10] < 0.006 * 11 - 0.01

    # Pause mid-turn (actual_curv = 0.05) should preserve turn_psi and not dip below 0.05 on resume
    tp.turn_psi = math.radians(30.0)
    tp.update(make_plan(0.08, 0.0), v_ego=0.0, actual_curv=0.05, active=True, is_rhd=False, model_curv=0.05)
    assert tp.turn_psi >= math.radians(29.0)
    resumed = tp.update(make_plan(0.08, 2.0), v_ego=2.0, actual_curv=0.05, active=True, is_rhd=False, model_curv=0.06)
    assert resumed >= 0.05 - 1e-6

  def test_wheelbase_and_rhd_scaling(self):
    tp_short = TurnPlanner(wheelbase=2.4)
    tp_long = TurnPlanner(wheelbase=3.4)
    plan_r = make_plan(0.14, 3.5)
    for _ in range(25):
      tp_short.update(plan_r, 3.5, 0.0, True, False, 0.02)
      tp_long.update(plan_r, 3.5, 0.0, True, False, 0.02)
    assert tp_long.shift_dist > tp_short.shift_dist * 1.3

    # RHD gives larger shift on left turns (k < 0) than right turns (k > 0)
    tp_rhd_l = TurnPlanner(wheelbase=2.89)
    tp_rhd_r = TurnPlanner(wheelbase=2.89)
    for _ in range(25):
      tp_rhd_l.update(make_plan(-0.14, 3.5), 3.5, 0.0, True, True, -0.02)
      tp_rhd_r.update(make_plan(0.14, 3.5), 3.5, 0.0, True, True, 0.02)
    assert tp_rhd_l.shift_dist > tp_rhd_r.shift_dist * 1.2

  def test_closed_loop_90deg_turn_clears_curb_without_oncoming_overshoot(self):
    """Closed-loop Tesla Model Y 90-deg right turn around R=2.5 m curb."""
    L, W_half, x_cam, lane_w, curb_r = 2.89, 0.96, 1.50, 3.60, 2.5
    y_curb = lane_w / 2.0
    x_dest = curb_r + lane_w / 2.0
    x_yellow = x_dest + lane_w / 2.0

    pts = [(x, 0.0) for x in np.linspace(-20, x_dest - 2.0, 200)]
    pts += [(x_dest - 2.0 + 2.0 * math.cos(th), 2.0 + 2.0 * math.sin(th)) for th in np.linspace(-math.pi / 2, 0, 50)]
    pts += [(x_dest, y) for y in np.linspace(2.0, 25.0, 200)]
    ref = np.array(pts)

    def run(use_planner: bool) -> tuple[float, float]:
      X, Y, psi, k_act = -15.0, 0.0, 0.0, 0.0
      v = 3.5
      tp = TurnPlanner(wheelbase=L, dt=DT_MDL) if use_planner else None
      min_clr, max_ovr = 99.0, -99.0
      for _ in range(400):
        xc, yc = X + x_cam * math.cos(psi), Y + x_cam * math.sin(psi)
        i_near = int(np.argmin(np.hypot(ref[:, 0] - xc, ref[:, 1] - yc)))
        i_tgt = i_near
        while i_tgt < len(ref) - 1 and np.hypot(ref[i_tgt, 0] - xc, ref[i_tgt, 1] - yc) < 6.5:
          i_tgt += 1
        dx, dy = ref[i_tgt, 0] - xc, ref[i_tgt, 1] - yc
        lx = dx * math.cos(psi) + dy * math.sin(psi)
        ly = -dx * math.sin(psi) + dy * math.cos(psi)
        k_mod = float(np.clip(2.0 * ly / max(lx**2 + ly**2, 1.0), -0.19, 0.19))
        plan = make_plan(0.14 if (max(0.0, x_dest - xc) < 15.0 and psi < math.radians(75)) else 0.0, v)

        k_cmd = tp.update(plan, v, k_act, True, False, k_mod) if tp is not None else k_mod
        k_act += (float(np.clip(k_cmd, -0.19, 0.19)) - k_act) * (DT_MDL / (0.22 + DT_MDL))

        ds = v * DT_MDL
        psi += k_act * ds
        X += ds * math.cos(psi)
        Y += ds * math.sin(psi)

        x_ir, y_ir = X - W_half * math.sin(psi), Y + W_half * math.cos(psi)
        x_of, y_of = X + L * math.cos(psi) + W_half * math.sin(psi), Y + L * math.sin(psi) - W_half * math.cos(psi)
        if x_ir <= 0.0:
          clr = y_curb - y_ir
        elif y_ir >= y_curb + curb_r:
          clr = x_ir - curb_r
        else:
          clr = math.hypot(x_ir, y_ir - (y_curb + curb_r)) - curb_r
        min_clr = min(min_clr, clr)
        if y_of > 2.0:
          max_ovr = max(max_ovr, x_of - x_yellow)
        if Y > 15.0:
          break
      return min_clr, max_ovr

    base_clr, _ = run(False)
    plan_clr, plan_ovr = run(True)
    assert base_clr < -0.5    # baseline curbs the rear wheel badly
    assert plan_clr > 0.20    # TurnPlanner clears the curb by > 20 cm
    assert plan_ovr < 0.0     # stays inside the oncoming yellow line

  def test_rolling_speed_taper(self):
    """Shift must taper smoothly down at rolling turn speeds (8-13.5 mph) and be 0 at 14+ mph."""
    tp_low = TurnPlanner(wheelbase=2.89)
    tp_mid = TurnPlanner(wheelbase=2.89)
    tp_fast = TurnPlanner(wheelbase=2.89)
    for _ in range(30):
      tp_low.update(make_plan(0.14, 3.0), v_ego=3.0, actual_curv=0.0, active=True, is_rhd=False, model_curv=0.02)
      tp_mid.update(make_plan(0.14, 4.75), v_ego=4.75, actual_curv=0.0, active=True, is_rhd=False, model_curv=0.02)
      tp_fast.update(make_plan(0.14, 6.5), v_ego=6.5, actual_curv=0.0, active=True, is_rhd=False, model_curv=0.02)
    assert tp_low.shift_dist > 1.5
    assert 0.5 < tp_mid.shift_dist < 1.1
    assert tp_fast.shift_dist == 0.0
