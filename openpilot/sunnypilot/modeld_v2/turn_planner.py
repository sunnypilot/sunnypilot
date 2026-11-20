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

# Two-stage rear-axle protected turn planner:
#   Stage 1 (Entry): wheelbase-scaled spatial delay on curvature buildup so the
#     inside rear tire clears the corner curb instead of off-tracking over it.
#     Capped in time (MAX_SHIFT_TIME) so crawl-speed starts never feel stalled.
#   Stage 2 (Apex & Exit): once past initial corner entry, smoothly blends
#     action curvature with the model's own 1-second path curvature so tight
#     apexes don't under-steer/go wide and exits unwind cleanly.
SHIFT_WHEELBASE_RATIO = 0.58  # fraction of wheelbase to delay turn-in (~1.68 m for 2.89 m WB)
WHEELBASE_CLIP = (2.0, 4.0)   # m
OPPOSITE_SIDE_WEIGHT = 0.70   # lighter shift for non-curb-side turns
MAX_SHIFT_TIME = 0.48         # s, caps entry delay at crawl speeds (2-5 mph)

TURN_SPEED_TAPER = (7.5, 10.5)            # m/s (~17-23.5 mph): overall active window
SHIFT_SPEED_BP = (3.5, 6.0, 8.5)          # m/s (~7.8, 13.4, 19.0 mph)
SHIFT_SPEED_V = (1.0, 0.35, 0.0)          # full from stop, light on rolling turns, 0 above 19 mph
CURV_GATE = (0.04, 0.09)                  # 1/m (R=25 m -> R=11 m): ignores gentle curves

ENTRY_PHASE_RELEASE_DEG = (8.0, 22.0)     # deg: release entry shift crisply once rotating
APEX_BLEND_PHASE_DEG = (10.0, 25.0)       # deg: ramp in 1s-path blend through apex & exit
APEX_PATH_BLEND_MAX = 0.65                # max weight on 1s path curvature during apex/exit
APEX_PATH_BOOST_CAP = 1.35                # max ratio vs |model_curv| for safety
PATH_AVG_HORIZON_S = 1.0                  # s, horizon for average path curvature

SHIFT_BUILD_TAU = 0.15        # s
SHIFT_RELEASE_TAU = 0.07      # s
APEX_BLEND_TAU = 0.12         # s
BUFFER_MAX_DIST = 4.5         # m
MIN_MOVE_SPEED = 0.3          # m/s
MID_TURN_CURV_THRESH = 0.02   # 1/m
PLAN_S_RANGE = (1.0, 18.0)    # m
PLAN_MIN_SEG_DS = 0.8         # m

T_IDXS = np.array(ModelConstants.T_IDXS, dtype=np.float32)


def compute_plan_metrics(model_output: dict[str, np.ndarray]) -> tuple[float, float]:
  """Return (peak_upcoming_curv, avg_1s_path_curv) from model_output['plan']."""
  plan_arr = model_output.get('plan')
  if plan_arr is None or plan_arr.ndim < 3 or plan_arr.shape[1] < 3:
    return 0.0, 0.0

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
  peak_k = float(np.clip(peak_k, -0.25, 0.25))

  if len(yaws) == len(T_IDXS):
    s_1s = float(np.interp(PATH_AVG_HORIZON_S, T_IDXS, s))
    yaw_1s = float(np.interp(PATH_AVG_HORIZON_S, T_IDXS, yaws))
    path_k_1s = float(np.clip(yaw_1s / s_1s, -0.25, 0.25)) if s_1s >= PLAN_MIN_SEG_DS else 0.0
  else:
    path_k_1s = 0.0

  return peak_k, path_k_1s


def compute_plan_peak_curv(model_output: dict[str, np.ndarray]) -> float:
  return compute_plan_metrics(model_output)[0]


class TurnPlanner:
  """
  Two-stage rear-axle protected turn planner for tight low-speed turns.

  Stage 1 (Entry): delays curvature buildup by a wheelbase-proportional distance
  (time-capped at MAX_SHIFT_TIME) so the rear axle clears the inside curb.
  Stage 2 (Apex & Exit): blends action curvature with the model's 1-second path
  curvature once past entry, preventing wide apexes and exit hang-ups.
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
    self.apex_blend = 0.0
    self.plan_peak_curv = 0.0
    self.path_curv_1s = 0.0

  def reset(self) -> None:
    self.s = 0.0
    self.buf_s.clear()
    self.buf_k.clear()
    self.turn_sign = 0.0
    self.turn_psi = 0.0
    self.shift_dist = 0.0
    self.apex_blend = 0.0
    self.plan_peak_curv = 0.0
    self.path_curv_1s = 0.0

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
        self.apex_blend = 0.0
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

    turn_speed_w = float(np.interp(v_ego, TURN_SPEED_TAPER, [1.0, 0.0]))
    if turn_speed_w <= 0.0 and self.shift_dist < 1e-3 and self.apex_blend < 1e-3:
      self.turn_psi = 0.0
      self.turn_sign = 0.0
      self.plan_peak_curv = 0.0
      self.path_curv_1s = 0.0
      return model_curv

    plan_peak, path_k_1s = compute_plan_metrics(model_output)
    self.plan_peak_curv = plan_peak
    self.path_curv_1s = path_k_1s

    tightness = max(abs(model_curv), abs(plan_peak))
    curv_w = float(np.interp(tightness, CURV_GATE, [0.0, 1.0]))

    ref_k = model_curv if abs(model_curv) > 0.015 else plan_peak
    if abs(ref_k) > 0.035 and turn_speed_w > 0.05:
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

    # Stage 1: Entry rear-axle spatial shift (time-capped so crawl-speed starts stay responsive)
    shift_speed_w = float(np.interp(v_ego, SHIFT_SPEED_BP, SHIFT_SPEED_V))
    entry_phase_w = float(np.interp(psi_deg, ENTRY_PHASE_RELEASE_DEG, [1.0, 0.0]))
    is_curb_side = (ref_k < 0.0) if is_rhd else (ref_k > 0.0)
    side_w = 1.0 if is_curb_side else OPPOSITE_SIDE_WEIGHT

    raw_shift = SHIFT_WHEELBASE_RATIO * self.wheelbase * shift_speed_w * curv_w * entry_phase_w * side_w
    target_shift = min(raw_shift, v_ego * MAX_SHIFT_TIME)
    tau = SHIFT_RELEASE_TAU if target_shift < self.shift_dist else SHIFT_BUILD_TAU
    self.shift_dist += (target_shift - self.shift_dist) * (self.dt / (tau + self.dt))

    out_k = model_curv
    if self.shift_dist >= 0.05 and len(self.buf_s) >= 2:
      k_delayed = float(np.interp(self.s - self.shift_dist, self.buf_s, self.buf_k))
      # Same sign as model_curv (or 0), never exceeds |model_curv|, zero lag on unwind.
      if model_curv >= 0.0:
        out_k = float(np.clip(k_delayed, 0.0, model_curv))
      else:
        out_k = float(np.clip(k_delayed, model_curv, 0.0))

    # Stage 2: Apex & Exit 1s-path blend (prevents wide apexes and exit hang-ups)
    apex_phase_w = float(np.interp(psi_deg, APEX_BLEND_PHASE_DEG, [0.0, 1.0]))
    target_blend = APEX_PATH_BLEND_MAX * turn_speed_w * curv_w * apex_phase_w
    self.apex_blend += (target_blend - self.apex_blend) * (self.dt / (APEX_BLEND_TAU + self.dt))

    if self.apex_blend > 0.01 and out_k * path_k_1s > 0.0:
      # Through the apex, boost when 1s path asks for tighter curvature than action (prevents wide turns).
      # Only pull curvature down toward 1s path late in the turn (psi > 60 deg) to prevent exit hang-ups.
      if abs(path_k_1s) > abs(out_k) or psi_deg > 60.0:
        max_boosted = abs(model_curv) * APEX_PATH_BOOST_CAP
        target_k = float(np.clip(path_k_1s, -max_boosted, max_boosted))
        out_k = (1.0 - self.apex_blend) * out_k + self.apex_blend * target_k

    return out_k
