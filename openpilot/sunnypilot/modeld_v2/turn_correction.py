"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass

import numpy as np

# Learned turn correction: per model, a small correction on top of its action toward the line FSD and the driver
# took, fitted by openpilot.distill's supervised/fit_turn_correction.py on open-loop frames of driver/FSD turns and
# closed-loop frames of the user's engaged drives (where the driver or FSD was steering, or a turn openpilot steered
# with no push-back), scored leave-one-route-out. It replaces the 0.75 turn plan floor and the path cap for a model
# that has one. With
#   time = the plan's curvature at action_t on its time axis (get_curvature_from_plan)
#   path = the plan's heading at the arc length the car covers in action_t (path_steering.path_curvature)
# command = action + s(v) * (theta_path * (path - action) + theta_time * (time - action)), s = 1 below v_full and 0
# from v_end, and the command stays within the range action..path spans (plus 10%), so it can only move the action
# toward the model's own line, never invent or reverse a turn.
MARGIN = 0.1


@dataclass(frozen=True)
class TurnCorrection:
  name: str
  v_full: float
  v_end: float
  theta_path: float
  theta_time: float


# bundle ref (or a local build's ref prefix ending in '-') -> correction
CORRECTIONS: dict[str, TurnCorrection] = {
  # Nov 9 2026, closed-loop frames of routes 98, 9a, 9e, 9f, b0 (26 turns, 3640 frames). Held out by route, mean
  # |command - driven| 1-3 m/s 0.039 -> 0.021 (0.75 floor 0.029), 3-4.5 m/s 0.028 -> 0.014, 4.5-6 m/s 0.017 -> 0.008,
  # 6-9 m/s 0.006 -> 0.004; peak command / peak driven per turn 0.74 (floor 0.83) -> 1.02 [10-90%: 0.84-1.26].
  'b92fc4828664f8767bce5e92f1630ed319cbe509': TurnCorrection('Light Speed 2', v_full=6.0, v_end=10.0,
                                                            theta_path=0.0554, theta_time=0.8708),
}


def correction_for(ref: str) -> TurnCorrection | None:
  if ref in CORRECTIONS:
    return CORRECTIONS[ref]
  return next((c for key, c in CORRECTIONS.items() if key.endswith('-') and ref.startswith(key)), None)


def apply_turn_correction(correction: TurnCorrection, action: float, time: float, path: float, v_ego: float) -> float:
  weight = float(np.clip((correction.v_end - v_ego) / (correction.v_end - correction.v_full), 0., 1.))
  if weight == 0.:
    return action
  raw = action + weight * (correction.theta_path * (path - action) + correction.theta_time * (time - action))
  lo, hi = min(action, path), max(action, path)
  margin = MARGIN * (hi - lo)
  return float(np.clip(raw, lo - margin, hi + margin))
