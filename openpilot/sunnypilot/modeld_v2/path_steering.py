"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

# Slow-turn path steering. The big models' action, and the plan's curvature at action_t on its time axis, assume the
# speed the model expects: in a crawl turn that is FSD-like acceleration out of the corner. Driven slower than that
# (route af, ff_turns_600: pulling away from ~2 m/s), the plan expected 4-6 m/s a second later while the car did
# 2.5-3.5, and the action asked 0.209/0.248 1/m (~440 deg) where FSD and the driver use a median 282 deg. Taking the
# plan's heading at the arc length the car itself covers in action_t gave 0.143/0.162 there (~300/285 deg), the same
# as the action at 5+ m/s, and more than Light Speed 2's under-committed action on its slow turns (route b0).
# Below FULL_SPEED the command follows the plan's line that way; it blends back to the normal command by BLEND_END.
PARAM = "TurnInHold"  # reuses the removed late turn-in toggle's key, so the prebuilt params library needs no rebuild
FULL_SPEED = 4.5  # m/s
BLEND_END = 7.0  # m/s
MIN_DISTANCE = 1.0  # m: the plan's heading over a shorter stretch is mostly noise
MIN_SPEED = 0.3  # m/s


def path_curvature(position_x: np.ndarray, position_y: np.ndarray, yaws: np.ndarray, yaw_rate: float,
                   v_ego: float, a_ego: float, action_t: float) -> float:
  """Curvature that reaches the plan's heading at the arc length the car covers in action_t at its own speed and
  acceleration (as get_curvature_from_plan does at action_t on the plan's time axis). Same sign as the plan."""
  arc = np.concatenate([[0.], np.cumsum(np.hypot(np.diff(position_x), np.diff(position_y)))])
  distance = max(v_ego * action_t + 0.5 * a_ego * action_t ** 2, MIN_DISTANCE)
  v = max(v_ego, MIN_SPEED)
  return float(2. * np.interp(distance, arc, yaws) / distance - yaw_rate / v)


def path_weight(v_ego: float) -> float:
  """1 below FULL_SPEED, 0 from BLEND_END, linear between."""
  return float(np.interp(v_ego, [FULL_SPEED, BLEND_END], [1., 0.]))


def apply_path_steering(command: float, path: float, v_ego: float) -> float:
  """The command (action, with the turn plan floor) blended toward the plan's line at the car's own speed."""
  weight = path_weight(v_ego)
  return weight * path + (1. - weight) * command
