"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

LANE_WIDTH_DEFAULT = 3.7  # m
LANE_WIDTH_CLIP = (2.8, 4.5)  # m
LOOKAHEAD_TIME = 1.5  # s
MIN_LOOKAHEAD = 10.0  # m
MAX_ERROR = 1.0  # m, cap on how far laneful can pull
MIN_SPEED = 9.0  # m/s
SMOOTH_TAU = 0.3  # s
YIELD = (0.5, 1.0)  # m
LINE_STD = (0.15, 0.4)
POINT_STD = 0.1
X_IDXS = np.array(ModelConstants.X_IDXS)


class Laneful:
  def __init__(self):
    self.lane_width = FirstOrderFilter(LANE_WIDTH_DEFAULT, 10.0, DT_MDL)
    self.correction = FirstOrderFilter(0.0, SMOOTH_TAU, DT_MDL) # correcting over .3s reduces jerk
    self.curvature = 0.0

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, active: bool, model_curvature: float) -> float:
    if not active or v_ego < MIN_SPEED or 'lane_lines' not in model_output:
      self.curvature = self.correction.x = 0.0
      return 0.0

    lookahead = max(v_ego * LOOKAHEAD_TIME, MIN_LOOKAHEAD)
    lines = model_output['lane_lines'][0, :, :, 0]
    stds = model_output['lane_lines_stds'][0, :, :, 0]

    probs = model_output['lane_lines_prob'][0, 1::2]
    l_prob = float(probs[1] * np.interp(np.interp(lookahead, X_IDXS, stds[1]), LINE_STD, [1.0, 0.0]))
    r_prob = float(probs[2] * np.interp(np.interp(lookahead, X_IDXS, stds[2]), LINE_STD, [1.0, 0.0]))
    lane_trust = l_prob + r_prob - l_prob * r_prob
    if lane_trust <= 0.0:
      self.curvature = self.correction.x = 0.0
      return 0.0

    if l_prob * r_prob > 0.5:
      width = np.interp(lookahead, X_IDXS, lines[2]) - np.interp(lookahead, X_IDXS, lines[1])
      self.lane_width.update(float(np.clip(width, *LANE_WIDTH_CLIP)))
    half_width = self.lane_width.x / 2

    win = (X_IDXS >= 0.5 * lookahead) & (X_IDXS <= 1.5 * lookahead)
    x = X_IDXS[win]
    l_var = stds[1, win] ** 2 / max(l_prob, 1e-4)
    r_var = stds[2, win] ** 2 / max(r_prob, 1e-4)
    center = (r_var * (lines[1, win] + half_width) + l_var * (lines[2, win] - half_width)) / (l_var + r_var)
    weight = 1.0 / (l_var * r_var / (l_var + r_var) + POINT_STD ** 2)

    # Fit curvature to place the plant in center: e ~ dk x^2 / 2
    error = np.clip(center - model_curvature * x ** 2 / 2, -MAX_ERROR, MAX_ERROR)
    dk = 2.0 * np.sum(weight * error * x ** 2) / np.sum(weight * x ** 4)

    # A model planning to end up further off center than the plant is now is likely going around something
    center_now = (l_prob * (lines[1, 0] + half_width) + r_prob * (lines[2, 0] - half_width)) / (l_prob + r_prob)
    plan_y = np.interp(lookahead, model_output['plan'][0, :, 0], model_output['plan'][0, :, 1])
    away = abs(plan_y - np.interp(lookahead, x, center)) - abs(center_now)
    lane_trust *= np.interp(away, YIELD, [1.0, 0.0])
    self.curvature = float(self.correction.update(lane_trust * dk))
    return self.curvature
