"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from collections import deque
import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan

T_IDXS = np.array(ModelConstants.T_IDXS, dtype=np.float32)
X_IDXS = np.array(ModelConstants.X_IDXS, dtype=np.float32)

# Physical geometry constants
SHIFT_WB_RATIO = 0.55    # windshield-camera-to-rear-axle fraction of wheelbase
REAR_KEEPOUT = 1.35      # m: half car width (~1.0 m) + curb safety margin (~0.35 m)
TURN_LAT_ACCEL = 1.8     # m/s^2: comfortable lat accel target for rolling-turn pre-slowing
LANE_HALF_W = 1.8        # m: standard half lane width for nearest-lane exit targeting
MIN_EXTRA_LANE_W = 2.7   # m: distinguishes a real adjacent lane from a shoulder/bike lane
EXIT_LAT_ACCEL_MAX = 0.8 # m/s^2: gentle cap for nearest-lane exit pull


def _plan_stats(model_output: dict[str, np.ndarray]) -> tuple[float, float, float]:
  """Return (peak_curv_18m, avg_curv_1s, yaw_18m) from model_output['plan']."""
  plan_arr = model_output.get('plan')
  if plan_arr is None or plan_arr.ndim < 3 or plan_arr.shape[1] < 3:
    return 0.0, 0.0, 0.0

  plan = plan_arr[0]
  pos = plan[:, Plan.POSITION]
  yaws = plan[:, Plan.T_FROM_CURRENT_EULER][:, 2]
  s = np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(pos[:, 0]), np.diff(pos[:, 1])))))

  peak_k = 0.0
  for i in range(len(yaws) - 2):
    if s[i] < 1.0:
      continue
    if s[i] > 18.0:
      break
    seg_ds = s[i + 2] - s[i]
    if seg_ds >= 0.8:
      k = float((yaws[i + 2] - yaws[i]) / seg_ds)
      if abs(k) > abs(peak_k):
        peak_k = k
  peak_k = float(np.clip(peak_k, -0.25, 0.25))

  path_k_1s = 0.0
  if len(yaws) == len(T_IDXS):
    s1 = float(np.interp(1.0, T_IDXS, s))
    if s1 >= 0.8:
      path_k_1s = float(np.clip(np.interp(1.0, T_IDXS, yaws) / s1, -0.25, 0.25))

  yaw_18m = float(np.interp(18.0, s, yaws)) if s[-1] >= 1.0 else 0.0
  return peak_k, path_k_1s, yaw_18m


class TurnPlanner:
  """
  Geometry-first turn planner for tight low-speed turns:
    1. 2D odometry curb memory + exact rear-tire clearance circle (even after curb exits FOV).
    2. Wheelbase viewpoint shift from windshield camera back toward rear axle (zero exit lag).
    3. 1-second path blend through apex & exit (prevents wide apexes and exit hang-ups).
    4. Nearest-lane exit lock (finishes turns in the lane closest to the turn direction).
    5. Rolling-turn pre-slowing so rolling turns get stop-bar steering headroom.
  """

  def __init__(self, wheelbase: float = 2.7, dt: float = DT_MDL):
    self.wb = float(np.clip(wheelbase, 2.0, 4.0))
    self.dt = dt
    self.s = 0.0
    self.buf_s: deque[float] = deque()
    self.buf_k: deque[float] = deque()
    self.turn_sign = 0.0
    self.turn_psi = 0.0
    self.exit_sign = 0.0
    self.exit_timer = 0.0
    # Remembered curb corner in rear-axle frame: (cx, cy, sign, live, k_live)
    self.curb: tuple[float, float, float, bool, float] | None = None

  def reset(self) -> None:
    self.s = 0.0
    self.buf_s.clear()
    self.buf_k.clear()
    self.turn_sign = 0.0
    self.turn_psi = 0.0
    self.exit_sign = 0.0
    self.exit_timer = 0.0
    self.curb = None

  def _nearest_lane_dk(self, model_output: dict[str, np.ndarray], sign: float, is_rhd: bool,
                       v_ego: float, blindspot: bool) -> float:
    """Gentle curvature pull to finish a turn in the lane closest to the turn direction."""
    if blindspot or sign == 0.0:
      return 0.0
    plan_arr = model_output.get('plan')
    edges = model_output.get('road_edges')
    edge_stds = model_output.get('road_edges_stds')
    lanes = model_output.get('lane_lines')
    lane_probs = model_output.get('lane_lines_prob')
    if any(x is None for x in (plan_arr, edges, edge_stds, lanes, lane_probs)):
      return 0.0
    if edges.ndim < 4 or edge_stds.ndim < 4 or lanes.ndim < 4 or edges.shape[1] < 2 or lanes.shape[1] < 4:
      return 0.0

    pos = plan_arr[0, :, Plan.POSITION]
    dx = np.diff(pos[:, 0])
    stop_i = int(np.argmax(dx <= 0.0)) + 1 if np.any(dx <= 0.0) else len(pos)
    if stop_i < 2 or float(pos[stop_i - 1, 0]) < 8.0:
      return 0.0
    x_look = min(12.0, float(pos[stop_i - 1, 0]))
    plan_y = float(np.interp(x_look, pos[:stop_i, 0], pos[:stop_i, 1]))
    probs = lane_probs[0, 1::2]
    if len(probs) < 4:
      return 0.0
    max_dk = EXIT_LAT_ACCEL_MAX / max(v_ego, 3.0) ** 2
    curb_side = (sign < 0.0) if is_rhd else (sign > 0.0)

    if curb_side:
      re_idx, ll_idx = (1, 2) if sign > 0.0 else (0, 1)
      if float(edge_stds[0, re_idx, 0, 0]) >= 1.2:
        return 0.0
      re_x = float(np.interp(x_look, X_IDXS, edges[0, re_idx, :, 0])) * sign
      ll_x = float(np.interp(x_look, X_IDXS, lanes[0, ll_idx, :, 0])) * sign
      # Only pull if a full driving lane exists between us and the curb (never into a bike lane/shoulder)
      if float(probs[ll_idx]) > 0.25:
        if (re_x - ll_x) < MIN_EXTRA_LANE_W:
          return 0.0
      elif (re_x - plan_y * sign) < (LANE_HALF_W + MIN_EXTRA_LANE_W):
        return 0.0
      target_y = (re_x - LANE_HALF_W) * sign
    else:
      # Non-curb-side turn (e.g. left turn in LHD): anchor to inside lane line, NEVER crossing it
      ll_idx = 1 if sign < 0.0 else 2
      if float(probs[ll_idx]) < 0.25:
        return 0.0
      ll_x = float(np.interp(x_look, X_IDXS, lanes[0, ll_idx, :, 0])) * sign
      target_y = (ll_x - LANE_HALF_W) * sign

    err = (target_y - plan_y) * sign
    if err <= 0.35:
      return 0.0
    return float(np.clip(2.0 * err / (x_look * x_look), 0.0, max_dk)) * sign

  def _update_curb(self, model_output: dict[str, np.ndarray], ds: float, dpsi: float) -> None:
    # Propagate remembered curb corner through ego motion (exact 2D rigid transform)
    if self.curb is not None:
      cx, cy, csign, _, _ = self.curb
      dx, dy = cx - ds, cy
      c, sn = math.cos(dpsi), math.sin(dpsi)
      cx, cy = dx * c + dy * sn, -dx * sn + dy * c
      if cx < -0.3 or cy * csign < -0.5 or (self.turn_sign != 0.0 and csign != self.turn_sign):
        self.curb = None
      else:
        self.curb = (cx, cy, csign, False, 0.0)

    edges = model_output.get('road_edges')
    stds = model_output.get('road_edges_stds')
    if self.turn_sign == 0.0 or edges is None or stds is None or edges.ndim < 4 or edges.shape[1] < 2:
      return

    idx = 1 if self.turn_sign > 0.0 else 0
    edge_y = edges[0, idx, :, 0]
    if len(edge_y) != len(X_IDXS) or float(stds[0, idx, 0, 0]) >= 0.80:
      return

    e0 = float(edge_y[0]) * self.turn_sign
    flare = float(np.interp(5.0, X_IDXS, edge_y)) * self.turn_sign - e0
    if 0.5 < e0 < 3.0 and flare < 0.65:
      k_live = max(0.0, 2.0 * flare / 25.0) + 0.005
      self.curb = (SHIFT_WB_RATIO * self.wb + 2.0, e0 * self.turn_sign, self.turn_sign, True, k_live)

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, actual_curv: float,
             active: bool, is_rhd: bool, model_curv: float, model_accel: float = 0.0,
             left_blindspot: bool = False, right_blindspot: bool = False,
             enabled: bool = True) -> tuple[float, float]:
    if not enabled or not active:
      self.reset()
      return model_curv, model_accel

    if v_ego < 0.3:
      if abs(actual_curv) < 0.02:
        self.turn_psi = 0.0
        self.turn_sign = 0.0
        self.exit_sign = 0.0
        self.exit_timer = 0.0
        self.curb = None
      self.buf_s = deque([self.s])
      self.buf_k = deque([float(actual_curv)])
      return model_curv, model_accel

    ds = v_ego * self.dt
    self.s += ds
    self.buf_s.append(self.s)
    self.buf_k.append(float(model_curv))
    while len(self.buf_s) > 2 and (self.s - self.buf_s[0]) > 4.5:
      self.buf_s.popleft()
      self.buf_k.popleft()

    speed_w = float(np.interp(v_ego, [7.5, 10.5], [1.0, 0.0]))
    if speed_w <= 0.0:
      self.turn_psi = 0.0
      self.turn_sign = 0.0
      self.exit_sign = 0.0
      self.exit_timer = 0.0
      self.curb = None
      return model_curv, model_accel

    plan_peak, path_k_1s, yaw_18m = _plan_stats(model_output)
    curv_w = float(np.interp(max(abs(model_curv), abs(plan_peak)), [0.04, 0.09], [0.0, 1.0]))

    ref_k = model_curv if abs(model_curv) > 0.015 else plan_peak
    if abs(ref_k) > 0.035:
      new_sign = 1.0 if ref_k > 0.0 else -1.0
      if new_sign != self.turn_sign:
        self.turn_sign = new_sign
        self.turn_psi = 0.0
      self.turn_psi = max(0.0, self.turn_psi + actual_curv * self.turn_sign * ds)
    else:
      self.turn_psi = max(0.0, self.turn_psi - 0.5 * self.dt)
      if self.turn_psi < 0.02:
        self.turn_sign = 0.0

    self._update_curb(model_output, ds, actual_curv * ds)

    out_k = model_curv
    out_a = model_accel
    psi_deg = math.degrees(self.turn_psi)

    # 1) Entry protection: odometry curb memory (live curb wall + frozen rear-tire circle)
    curb_limited = False
    if self.curb is not None and out_k * self.curb[2] > 0.0 and psi_deg < 25.0:
      cx, cy, csign, live, k_live = self.curb
      if live:
        k_lim = k_live
      elif cx > 0.0:
        cy_s = cy * csign
        k_lim = max(0.0, 2.0 * (cy_s - REAR_KEEPOUT) / max(cx * cx + cy_s * cy_s - REAR_KEEPOUT ** 2, 0.25))
      else:
        k_lim = 1.0
      if abs(out_k) > k_lim:
        out_k = math.copysign(k_lim, out_k)
        curb_limited = True

    # 2) Entry protection: wheelbase viewpoint shift (works even with no visible curb; zero exit lag)
    entry_w = float(np.interp(psi_deg, [8.0, 22.0], [1.0, 0.0]))
    shift_spd = float(np.interp(v_ego, [3.5, 6.0, 8.5], [1.0, 0.35, 0.0]))
    side_w = 1.0 if ((ref_k < 0.0) if is_rhd else (ref_k > 0.0)) else 0.70
    shift = min(SHIFT_WB_RATIO * self.wb * shift_spd * curv_w * entry_w * side_w, v_ego * 0.45)
    if shift >= 0.05 and len(self.buf_s) >= 2:
      k_del = float(np.interp(self.s - shift, self.buf_s, self.buf_k))
      k_sh = float(np.clip(k_del, 0.0, model_curv)) if model_curv >= 0.0 else float(np.clip(k_del, model_curv, 0.0))
      if abs(k_sh) < abs(out_k):
        out_k = k_sh

    # 3) Apex & exit: blend with model's 1-second path curvature once past corner entry
    apex_w = 0.65 * speed_w * curv_w * float(np.interp(psi_deg, [10.0, 25.0], [0.0, 1.0]))
    if apex_w > 0.01 and out_k * path_k_1s > 0.0 and not curb_limited:
      if abs(path_k_1s) > abs(out_k) or psi_deg > 60.0:
        cap = abs(model_curv) * 1.35
        out_k = (1.0 - apex_w) * out_k + apex_w * float(np.clip(path_k_1s, -cap, cap))

    # 4) Nearest-lane exit lock: finish turns in the lane closest to the turn (active psi>=35 deg + 1.5s fade)
    if psi_deg >= 35.0 and self.turn_sign != 0.0:
      self.exit_sign = self.turn_sign
      self.exit_timer = 1.5
    elif self.exit_timer > 0.0:
      self.exit_timer = max(0.0, self.exit_timer - self.dt)
      if self.exit_timer <= 0.0:
        self.exit_sign = 0.0

    if self.exit_timer > 0.0 and not curb_limited:
      bs = right_blindspot if self.exit_sign > 0.0 else left_blindspot
      exit_w = min(1.0, self.exit_timer / 0.5) * speed_w
      out_k += exit_w * self._nearest_lane_dk(model_output, self.exit_sign, is_rhd, v_ego, bs)

    # 5) Rolling-turn pre-slowing: slow to comfortable turn speed before sharp corners
    if abs(plan_peak) > 0.06 and abs(yaw_18m) > math.radians(35.0):
      v_turn = math.sqrt(TURN_LAT_ACCEL / abs(plan_peak))
      if v_ego > v_turn:
        out_a = min(out_a, float(np.clip((v_turn - v_ego) * 0.8, -1.8, 0.0)))

    return out_k, out_a
