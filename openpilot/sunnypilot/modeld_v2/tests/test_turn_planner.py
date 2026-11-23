"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import functools
import math
import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan
from openpilot.sunnypilot.modeld_v2.turn_planner import TurnPlanner

X = np.array(ModelConstants.X_IDXS, dtype=np.float32)


def make_plan(curv: float, speed: float = 4.0) -> dict[str, np.ndarray]:
  t = np.array(ModelConstants.T_IDXS, dtype=np.float32)
  s = speed * t
  plan = np.zeros((1, len(t), ModelConstants.PLAN_WIDTH), dtype=np.float32)
  if abs(curv) < 1e-6:
    plan[0, :, Plan.POSITION][:, 0] = s
  else:
    r = 1.0 / curv
    th = s * curv
    plan[0, :, Plan.POSITION][:, 0] = r * np.sin(th)
    plan[0, :, Plan.POSITION][:, 1] = r * (1.0 - np.cos(th))
    plan[0, :, Plan.T_FROM_CURRENT_EULER][:, 2] = th
  return {'plan': plan}


def with_curb(plan_dict: dict[str, np.ndarray], e0: float = 2.4, flare_5m: float = 0.1, std: float = 0.4) -> dict[str, np.ndarray]:
  edges = np.zeros((1, 2, len(X), 2), dtype=np.float32)
  edges[0, 0, :, 0] = -5.0
  edges[0, 1, :, 0] = e0 + (flare_5m / 25.0) * (X ** 2)
  stds = np.full((1, 2, len(X), 2), std, dtype=np.float32)
  return {**plan_dict, 'road_edges': edges, 'road_edges_stds': stds}


def with_lanes_and_edges(plan_dict: dict[str, np.ndarray], re_l: float = -5.0, re_r: float = 5.4,
                         ll1: float = -1.8, ll2: float = 1.9, p1: float = 0.8, p2: float = 0.8,
                         std_l: float = 0.5, std_r: float = 0.5, plan_y_end: float | None = None) -> dict[str, np.ndarray]:
  out = {**plan_dict}
  if plan_y_end is not None:
    plan = plan_dict['plan'].copy()
    x = plan[0, :, Plan.POSITION][:, 0]
    plan[0, :, Plan.POSITION][:, 1] = plan_y_end * np.clip(x / 12.0, 0.0, 1.0)
    out['plan'] = plan
  edges = np.zeros((1, 2, len(X), 2), dtype=np.float32)
  edges[0, 0, :, 0] = re_l
  edges[0, 1, :, 0] = re_r
  stds = np.zeros((1, 2, len(X), 2), dtype=np.float32)
  stds[0, 0, :, 0] = std_l
  stds[0, 1, :, 0] = std_r
  lanes = np.zeros((1, 4, len(X), 2), dtype=np.float32)
  lanes[0, 0, :, 0] = ll1 - 3.6
  lanes[0, 1, :, 0] = ll1
  lanes[0, 2, :, 0] = ll2
  lanes[0, 3, :, 0] = ll2 + 3.6
  probs = np.zeros((1, 8), dtype=np.float32)
  probs[0, 3] = p1
  probs[0, 5] = p2
  out.update({'road_edges': edges, 'road_edges_stds': stds, 'lane_lines': lanes, 'lane_lines_prob': probs})
  return out


class TestTurnPlanner(OpenpilotTestCase):
  def test_untouched_highway_and_gentle_curves(self):
    tp = TurnPlanner(wheelbase=2.89)
    for i in range(60):
      k = 0.01 * math.sin(i * 0.1)
      out_k, out_a = tp.update(make_plan(k, 25.0), 25.0, k, True, False, k, 0.2)
      assert out_k == k and out_a == 0.2
    for i in range(60):
      k = 0.025 * min(1.0, i / 20.0)
      out_k, out_a = tp.update(make_plan(k, 6.0), 6.0, k, True, False, k, 0.2)
      assert out_k == k and out_a == 0.2

  def test_sign_preservation_and_magnitude_bounds(self):
    tp = TurnPlanner(wheelbase=2.89)
    ks = [-0.015] * 15 + [0.016, 0.05, 0.11, 0.14, 0.17, 0.18, 0.14, 0.08, 0.02, -0.01]
    plan_r = make_plan(0.15, 3.0)
    for k in ks:
      out_k, _ = tp.update(plan_r, 3.0, k * 0.7, True, False, k, 0.0)
      assert abs(out_k) <= abs(k) * 1.35 + 1e-9
      if k > 0:
        assert out_k >= 0.0
      elif k < 0:
        assert out_k <= 0.0

  def test_zero_lag_on_turn_exit_unwinding(self):
    tp = TurnPlanner(wheelbase=2.89)
    plan_tight = make_plan(0.14, 4.0)
    for i in range(25):
      k = 0.14 * (i / 25.0)
      tp.update(plan_tight, 4.0, k * 0.8, True, False, k)
    for _ in range(15):
      tp.update(plan_tight, 4.0, 0.14, True, False, 0.14)
    for i in range(1, 20):
      k = max(0.0, 0.14 * (1.0 - i / 15.0))
      out_k, _ = tp.update(make_plan(k, 4.0), 4.0, k + 0.01, True, False, k)
      assert abs(out_k - k) < 1e-3

  def test_standstill_launch_and_mid_turn_pause(self):
    tp = TurnPlanner(wheelbase=2.89)
    for _ in range(10):
      tp.update(make_plan(0.12, 0.0), 0.0, 0.0, True, False, 0.002)
    outs = [tp.update(make_plan(0.12, 2.5), 2.5, 0.004 * i, True, False, 0.006 * i)[0] for i in range(1, 20)]
    assert outs[10] < 0.006 * 11 - 0.01

    tp.turn_psi = math.radians(30.0)
    tp.update(make_plan(0.08, 0.0), 0.0, 0.05, True, False, 0.05)
    assert tp.turn_psi >= math.radians(29.0)
    resumed, _ = tp.update(make_plan(0.08, 2.0), 2.0, 0.05, True, False, 0.06)
    assert resumed >= 0.05 - 1e-6

  def test_odometry_curb_memory_and_rear_tire_clearance(self):
    tp = TurnPlanner(wheelbase=2.89)
    # 1) Live straight curb beside car holds early turn-in down
    mo_curb = with_curb(make_plan(0.08, 5.0), e0=2.0, flare_5m=0.05, std=0.4)
    out_live, _ = tp.update(mo_curb, 5.0, 0.0, True, False, 0.05)
    assert tp.curb is not None and tp.curb[3] is True
    assert out_live < 0.015

    # 2) Curb exits cropped FOV (std=2.0): odometry remembers frozen corner and keeps protecting rear tire
    mo_blind = with_curb(make_plan(0.14, 5.0), e0=4.0, flare_5m=1.5, std=2.0)
    out_frozen, _ = tp.update(mo_blind, 5.0, 0.02, True, False, 0.14)
    assert tp.curb is not None and tp.curb[3] is False
    assert out_frozen < 0.14

    # 3) Advance ~4.5 m so rear axle clears the remembered corner -> curb memory releases!
    for _ in range(25):
      tp.update(mo_blind, 5.0, 0.08, True, False, 0.12)
    assert tp.curb is None

    # 4) Normal curved road (curb curves with the road at k=0.03) passes untouched
    tp2 = TurnPlanner(wheelbase=2.89)
    mo_curve = with_curb(make_plan(0.03, 6.7), e0=2.4, flare_5m=0.375, std=0.4)
    out_curve, _ = tp2.update(mo_curve, 6.7, 0.03, True, False, 0.03)
    assert abs(out_curve - 0.03) < 1e-6

  def test_apex_1s_path_boost_and_exit_unwind(self):
    tp = TurnPlanner(wheelbase=2.89)
    for _ in range(35):
      tp.update(make_plan(0.14, 4.0), 4.0, 0.12, True, False, 0.10)
    apex_out, _ = tp.update(make_plan(0.14, 4.0), 4.0, 0.12, True, False, 0.10)
    assert apex_out > 0.115
    for _ in range(20):
      tp.update(make_plan(0.14, 4.0), 4.0, 0.12, True, False, 0.14)
    exit_out, _ = tp.update(make_plan(0.10, 4.0), 4.0, 0.15, True, False, 0.20)
    assert exit_out < 0.15

  def test_rolling_turn_pre_slowing(self):
    tp = TurnPlanner(wheelbase=2.89)
    # Approaching a tight R=8 m corner (k=0.125) at 14 mph (6.3 m/s) -> pre-slows smoothly
    _, a_slow = tp.update(make_plan(0.125, 6.3), 6.3, 0.0, True, False, 0.02, model_accel=0.2)
    assert a_slow < -0.5
    # Already slow at 7 mph (3.1 m/s) -> does not brake
    _, a_ok = tp.update(make_plan(0.125, 3.1), 3.1, 0.0, True, False, 0.02, model_accel=0.2)
    assert a_ok == 0.2

  def test_closed_loop_90deg_stop_and_rolling_turns(self):
    L, W_half, x_cam, lane_w, curb_r = 2.89, 0.96, 1.50, 3.60, 2.5
    y_curb = lane_w / 2.0
    x_dest = curb_r + lane_w / 2.0
    x_yellow = x_dest + lane_w / 2.0

    pts = [(x, 0.0) for x in np.linspace(-25, x_dest - 2.0, 250)]
    pts += [(x_dest - 2.0 + 2.0 * math.cos(th), 2.0 + 2.0 * math.sin(th)) for th in np.linspace(-math.pi / 2, 0, 50)]
    pts += [(x_dest, y) for y in np.linspace(2.0, 25.0, 250)]
    ref = np.array(pts)

    def run(v_init: float, use_planner: bool) -> tuple[float, float]:
      X_p, Y_p, psi, k_act, k_ctl = -18.0, 0.0, 0.0, 0.0, 0.0
      v = v_init
      tp = TurnPlanner(wheelbase=L, dt=DT_MDL) if use_planner else None
      min_clr, max_ovr = 99.0, -99.0
      for _ in range(500):
        xc, yc = X_p + x_cam * math.cos(psi), Y_p + x_cam * math.sin(psi)
        i_near = int(np.argmin(np.hypot(ref[:, 0] - xc, ref[:, 1] - yc)))
        i_tgt = i_near
        while i_tgt < len(ref) - 1 and np.hypot(ref[i_tgt, 0] - xc, ref[i_tgt, 1] - yc) < 6.5:
          i_tgt += 1
        dx, dy = ref[i_tgt, 0] - xc, ref[i_tgt, 1] - yc
        lx = dx * math.cos(psi) + dy * math.sin(psi)
        ly = -dx * math.sin(psi) + dy * math.cos(psi)
        k_mod = float(np.clip(2.0 * ly / max(lx**2 + ly**2, 1.0), -0.19, 0.19))
        plan = make_plan(0.14 if (max(0.0, x_dest - xc) < 16.0 and psi < math.radians(75)) else 0.0, max(v, 1.0))

        k_des, a_des = tp.update(plan, v, k_act, True, False, k_mod, 0.0) if tp else (k_mod, 0.0)
        v = max(2.5, v + a_des * DT_MDL)
        max_rate = 5.0 / max(v, 1.0) ** 2
        k_ctl = float(np.clip(k_des, k_ctl - max_rate * DT_MDL, k_ctl + max_rate * DT_MDL))
        k_ctl = float(np.clip(k_ctl, -min(0.2, 3.0 / max(v, 1.0) ** 2), min(0.2, 3.0 / max(v, 1.0) ** 2)))
        k_act += (k_ctl - k_act) * (DT_MDL / (0.22 + DT_MDL))

        ds = v * DT_MDL
        psi += k_act * ds
        X_p += ds * math.cos(psi)
        Y_p += ds * math.sin(psi)

        x_ir, y_ir = X_p - W_half * math.sin(psi), Y_p + W_half * math.cos(psi)
        x_of, y_of = X_p + L * math.cos(psi) + W_half * math.sin(psi), Y_p + L * math.sin(psi) - W_half * math.cos(psi)
        if x_ir <= 0.0:
          clr = y_curb - y_ir
        elif y_ir >= y_curb + curb_r:
          clr = x_ir - curb_r
        else:
          clr = math.hypot(x_ir, y_ir - (y_curb + curb_r)) - curb_r
        min_clr = min(min_clr, clr)
        if y_of > 2.0:
          max_ovr = max(max_ovr, x_of - x_yellow)
        if Y_p > 15.0:
          break
      return min_clr, max_ovr

    # Low-speed turn clears curb with margin and stays in lane
    base_clr, _ = run(3.5, False)
    plan_clr, plan_ovr = run(3.5, True)
    assert base_clr < -0.5 and plan_clr > 0.20 and plan_ovr < 0.0

    # Rolling 11 mph turn: baseline blows wide into oncoming lane; TurnPlanner pre-slows, clears curb, stays in lane
    _, roll_base_ovr = run(4.9, False)
    roll_plan_clr, roll_plan_ovr = run(4.9, True)
    assert roll_base_ovr > 0.5 and roll_plan_clr > 0.15 and roll_plan_ovr < 0.0

  def test_nearest_lane_exit_lock(self):
    def finish_turn(sign: float, is_rhd: bool = False) -> TurnPlanner:
      tp = TurnPlanner(wheelbase=2.89)
      for _ in range(30):
        tp.update(make_plan(0.12 * sign, 5.0), 5.0, 0.10 * sign, True, is_rhd, 0.10 * sign)
      assert tp.exit_timer > 0.0 and tp.exit_sign == sign
      return tp

    # 1) Right turn exiting into lane 2 (full 3.5 m lane to right of ll2) -> pulls right into lane 1
    tp_r = finish_turn(+1.0)
    mo_lane2 = with_lanes_and_edges(make_plan(0.0, 6.0), re_r=5.4, ll2=1.9, p2=0.7)
    out_r, _ = tp_r.update(mo_lane2, 6.0, 0.0, True, False, 0.0)
    assert out_r > 0.008

    # 2) Right turn beside 2.1 m bike lane/shoulder -> zero pull (never pulls into shoulder/bike lane)
    tp_bike = finish_turn(+1.0)
    mo_bike = with_lanes_and_edges(make_plan(0.0, 6.0), re_r=4.0, ll2=1.9, p2=0.9)
    out_bike, _ = tp_bike.update(mo_bike, 6.0, 0.0, True, False, 0.0)
    assert out_bike == 0.0

    # 3) Right blindspot occupied -> suppressed
    tp_bs = finish_turn(+1.0)
    fn_bs = functools.partial(tp_bs.update, mo_lane2, 6.0, 0.0, True, False,
                              left_blindspot=False, right_blindspot=True)
    out_bs, _ = fn_bs(0.0, 0.0)
    assert out_bs == 0.0

    # 4) Left turn drifting right of ll1 -> pulls left back to ll1 + 1.8 m, never crosses ll1 into oncoming
    tp_l = finish_turn(-1.0)
    mo_l_drift = with_lanes_and_edges(make_plan(0.0, 6.0), ll1=-1.5, p1=0.7, plan_y_end=+1.2)
    out_l_drift, _ = tp_l.update(mo_l_drift, 6.0, 0.0, True, False, 0.0)
    assert out_l_drift < -0.008

    tp_l_ok = finish_turn(-1.0)
    mo_l_ok = with_lanes_and_edges(make_plan(0.0, 6.0), ll1=-1.5, p1=0.7, plan_y_end=0.0)
    out_l_ok, _ = tp_l_ok.update(mo_l_ok, 6.0, 0.0, True, False, 0.0)
    assert out_l_ok == 0.0

    # 5) RHD symmetry: left turn is curb-side -> pulls left when full lane exists to the left
    tp_rhd = finish_turn(-1.0, is_rhd=True)
    mo_rhd = with_lanes_and_edges(make_plan(0.0, 6.0), re_l=-5.4, ll1=-1.9, p1=0.7)
    out_rhd, _ = tp_rhd.update(mo_rhd, 6.0, 0.0, True, True, 0.0)
    assert out_rhd < -0.008
