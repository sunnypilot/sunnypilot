"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from collections import deque
import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import Plan

# Rear-axle protected turn-in shaping parameters.
# Models operating on cropped forward-looking views plan front/camera-centric
# trajectories and initiate tight turns early, causing the rear axle to off-track
# inside the front path by ~L^2 / (2R) and clip the inside curb.
SHIFT_WHEELBASE_RATIO = 0.60  # fraction of wheelbase to delay turn-in (~1.73 m for 2.89 m WB)
WHEELBASE_CLIP = (2.0, 4.0)   # m
OPPOSITE_SIDE_WEIGHT = 0.75   # slightly lighter shift for non-curb-side turns

SPEED_TAPER = (8.0, 13.0)     # m/s (~18-29 mph): full below 8 m/s, off above 13 m/s
CURV_GATE = (0.04, 0.09)      # 1/m (R=25 m -> R=11 m): ignores gentle curves, full on tight turns
PHASE_RELEASE_DEG = (20.0, 45.0)  # deg of turn heading completed: fade shift to 0 through apex

SHIFT_TAU = 0.15              # s, smooths shift distance transitions
BUFFER_MAX_DIST = 4.5         # m, distance history retained for spatial lookup
MIN_MOVE_SPEED = 0.3          # m/s
MID_TURN_CURV_THRESH = 0.02   # 1/m, threshold to recognize a pause mid-turn
PLAN_S_RANGE = (1.0, 18.0)    # m, lookahead window for upcoming turn peak curvature
PLAN_MIN_SEG_DS = 0.8         # m, minimum 2-step arc length to suppress knot noise


def compute_plan_peak_curv(model_output: dict[str, np.ndarray]) -> float:
  """Estimate peak upcoming curvature within PLAN_S_RANGE from model_output['plan']."""
  plan_arr = model_output.get('plan')
  if plan_arr is None or plan_arr.ndim < 3 or plan_arr.shape[1] < 3:
    return 0.0

  plan = plan_arr[0]
  pos = plan[:, Plan.POSITION]
  yaws = plan[:, Plan.T_FROM_CURRENT_EULER][:, 2]
  ds = np.hypot(np.diff(pos[:, 0]), np.diff(pos[:, 1]))
  s = np.concatenate(([0.0], np.cumsum(ds)))

  peak_k = 0.0
  n = len(yaws)
  for i in range(n - 2):
    if s[i] < PLAN_S_RANGE[0]:
      continue
    if s[i] > PLAN_S_RANGE[1]:
      break
    seg_ds = s[i + 2] - s[i]
    if seg_ds < PLAN_MIN_SEG_DS:
      continue
    k = float((yaws[i + 2] - yaws[i]) / seg_ds)
    if abs(k) > abs(peak_k):
      peak_k = k
  return float(np.clip(peak_k, -0.25, 0.25))


class TurnPlanner:
  """
  Asymmetric spatial turn-in shaper that protects the inside rear wheel during tight turns.

  During turn entry of sharp low-speed turns, delays curvature buildup by a
  wheelbase-proportional distance so the rear axle advances deeper into the
  intersection before curving in.
  - Asymmetric: only delays curvature buildup; unwinding (exit) and sign reversals
    pass through with zero lag.
  - Phase-aware: smoothly releases the spatial shift as accumulated turn heading
    passes the corner apex, allowing crisp destination-lane alignment.
  - Strictly bounded: output always shares the sign of model_curv and never
    exceeds |model_curv|.
  """

  def __init__(self, wheelbase: float = 2.7, dt: float = DT_MDL):
    self.wheelbase = float(np.clip(wheelbase, *WHEELBASE_CLIP))
    self.dt = dt
    self.s = 0.0
    self.buf_s: deque[float] = deque()
    self.buf_k: deque[float] = deque()
    self.turn_sign = 0.0
    self.turn_psi = 0.0
    self.shift_dist = 0.0
    self.plan_peak_curv = 0.0

  def reset(self) -> None:
    self.s = 0.0
    self.buf_s.clear()
    self.buf_k.clear()
    self.turn_sign = 0.0
    self.turn_psi = 0.0
    self.shift_dist = 0.0
    self.plan_peak_curv = 0.0

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, actual_curv: float,
             active: bool, is_rhd: bool, model_curv: float, enabled: bool = True) -> float:
    if not enabled or not active:
      self.reset()
      return model_curv

    if v_ego < MIN_MOVE_SPEED:
      # Stopped straight (e.g., at a stop bar): reset turn phase so launch gets full protection.
      # Stopped mid-turn (e.g., yielding to a pedestrian): preserve turn_psi so resume doesn't re-delay.
      if abs(actual_curv) < MID_TURN_CURV_THRESH:
        self.turn_psi = 0.0
        self.turn_sign = 0.0
        self.shift_dist = 0.0
      self.buf_s.clear()
      self.buf_k.clear()
      self.buf_s.append(self.s)
      self.buf_k.append(float(actual_curv))
      return model_curv

    ds = v_ego * self.dt
    self.s += ds
    self.buf_s.append(self.s)
    self.buf_k.append(float(model_curv))
    while len(self.buf_s) > 2 and (self.s - self.buf_s[0]) > BUFFER_MAX_DIST:
      self.buf_s.popleft()
      self.buf_k.popleft()

    speed_w = float(np.interp(v_ego, SPEED_TAPER, [1.0, 0.0]))
    if speed_w <= 0.0 and self.shift_dist < 1e-3:
      self.turn_psi = 0.0
      self.turn_sign = 0.0
      self.plan_peak_curv = 0.0
      return model_curv

    plan_peak = compute_plan_peak_curv(model_output)
    self.plan_peak_curv = plan_peak

    tightness = max(abs(model_curv), abs(plan_peak))
    curv_w = float(np.interp(tightness, CURV_GATE, [0.0, 1.0]))

    ref_k = model_curv if abs(model_curv) > 0.015 else plan_peak
    if abs(ref_k) > 0.035 and speed_w > 0.05:
      new_sign = 1.0 if ref_k > 0.0 else -1.0
      if new_sign != self.turn_sign:
        self.turn_sign = new_sign
        self.turn_psi = 0.0
      self.turn_psi = max(0.0, self.turn_psi + actual_curv * self.turn_sign * ds)
    else:
      self.turn_psi = max(0.0, self.turn_psi - 0.5 * self.dt)
      if self.turn_psi < 0.02:
        self.turn_sign = 0.0

    psi_deg = math.degrees(self.turn_psi)
    phase_w = float(np.interp(psi_deg, PHASE_RELEASE_DEG, [1.0, 0.0]))

    # In LHD (not is_rhd), right turns (curv > 0) hug the near-side curb; in RHD, left turns (curv < 0) do.
    is_curb_side = (ref_k < 0.0) if is_rhd else (ref_k > 0.0)
    side_w = 1.0 if is_curb_side else OPPOSITE_SIDE_WEIGHT

    target_shift = SHIFT_WHEELBASE_RATIO * self.wheelbase * speed_w * curv_w * phase_w * side_w
    alpha = self.dt / (SHIFT_TAU + self.dt)
    self.shift_dist += (target_shift - self.shift_dist) * alpha

    if self.shift_dist < 0.05 or len(self.buf_s) < 2:
      return model_curv

    k_delayed = float(np.interp(self.s - self.shift_dist, self.buf_s, self.buf_k))

    # Hard invariant: same sign as model_curv (or 0) and |out_k| <= |model_curv|.
    # Holds back curvature buildup on entry, passes unwinding/exit through with zero lag.
    if model_curv >= 0.0:
      return float(np.clip(k_delayed, 0.0, model_curv))
    return float(np.clip(k_delayed, model_curv, 0.0))
