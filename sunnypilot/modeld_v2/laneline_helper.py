"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan


def plan_x_idxs_helper(plan_output) -> list[float]:
  # times at X_IDXS according to plan.
  LINE_T_IDXS = [np.nan] * ModelConstants.IDX_N
  LINE_T_IDXS[0] = 0.0
  plan_x = plan_output['plan'][0, :, Plan.POSITION][:, 0].tolist()
  for xidx in range(1, ModelConstants.IDX_N):
    tidx = 0
    # increment tidx until we find an element that's further away than the current xidx
    while tidx < ModelConstants.IDX_N - 1 and plan_x[tidx + 1] < ModelConstants.X_IDXS[xidx]:
      tidx += 1
    if tidx == ModelConstants.IDX_N - 1:
      # if the Plan doesn't extend far enough, set plan_t to the max value (10s), then break
      LINE_T_IDXS[xidx] = ModelConstants.T_IDXS[ModelConstants.IDX_N - 1]
      break
    # interpolate to find `t` for the current xidx
    current_x_val = plan_x[tidx]
    next_x_val = plan_x[tidx + 1]
    p = (ModelConstants.X_IDXS[xidx] - current_x_val) / (next_x_val - current_x_val) if abs(
      next_x_val - current_x_val) > 1e-9 else float('nan')
    LINE_T_IDXS[xidx] = p * ModelConstants.T_IDXS[tidx + 1] + (1 - p) * ModelConstants.T_IDXS[tidx]
  return LINE_T_IDXS
