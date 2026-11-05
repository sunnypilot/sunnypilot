"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan
from openpilot.sunnypilot.modeld_v2.constants import Plan

# Longitudinal half of comma's plan-long experiment (commaai/openpilot plan-long, 1193b78db..1c2df3b3f, Shane Smiskol).
# The action head is on-policy but slow to see stops and curves coming; the plan sees them seconds ahead but is
# off-policy and runs above the speed the road needs. So the action sets the speed level and the plan adds early slowing.
PLAN_OFFSET_RC = 3.0  # s, how fast the plan's accel level is pulled to the action's
HORIZON_START_T = 2.0  # s, plan points from here on can ask for early slowing
X_STD_SLACK = 1.5  # plan position stds the car may run past where the plan expects it


def get_accel_from_plan_horizon(a_now, speeds, accels, x, y, x_stds, t_idxs, action_t):
  # distance along the path, x alone is short in curves
  dist = x[0] + np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))))
  ahead = t_idxs >= HORIZON_START_T
  t = t_idxs[ahead]
  # where we get to if the current accel holds until the new one acts after action_t
  x_hold = speeds[0] * t + accels[0] * action_t * (t - action_t / 2)
  # slow down early enough to not pass where the plan expects to be, with its uncertainty as slack
  a_slow = min(np.min(2 * (dist[ahead] + X_STD_SLACK * x_stds[ahead] - x_hold) / (t - action_t) ** 2), 0.0)
  # stop accelerating first if the plan slows down later
  return float(max(a_now, 0.0) * np.interp(-a_slow, [0.0, 0.3], [1.0, 0.0]) + min(a_now, a_slow))


class PlanLong:
  def __init__(self):
    self.plan_offset = FirstOrderFilter(0.0, PLAN_OFFSET_RC, DT_MDL)

  def reset(self):
    self.plan_offset.x = 0.0

  def update(self, plan, plan_stds, t_idxs, action_t, action_accel=None) -> float:
    t_idxs = np.asarray(t_idxs)
    speeds, accels = plan[:, Plan.VELOCITY][:, 0], plan[:, Plan.ACCELERATION][:, 0]
    a_plan = get_accel_from_plan(speeds, accels, t_idxs, action_t=action_t)
    if action_accel is not None:
      # keep the plan's changes, but the action's level
      a_plan -= self.plan_offset.update(a_plan - action_accel)
    return get_accel_from_plan_horizon(a_plan, speeds, accels, plan[:, Plan.POSITION][:, 0], plan[:, Plan.POSITION][:, 1],
                                       plan_stds[:, Plan.POSITION][:, 0], t_idxs, action_t)
