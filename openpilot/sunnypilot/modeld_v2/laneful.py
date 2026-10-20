"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

LANE_WIDTH_DEFAULT = 3.2914  # m (averaged narrow lane in downtown streets, ~10.8ft usable)
LANE_WIDTH_CLIP = (2.8, 4.5)  # m
LOOKAHEAD_TIME = 1.5  # s
MIN_LOOKAHEAD = 10.0  # m
MIN_SPEED = 5.0  # m/s
LINE_STD = (0.2, 0.6)
POINT_STD = 0.1
MAX_ERROR = 1.0
X_IDXS = np.array(ModelConstants.X_IDXS)


class Laneful: # TODO-SP: Rename this to blendful or something similar because it is not pure laneful anymore.
  def __init__(self):
    self.lane_width = FirstOrderFilter(LANE_WIDTH_DEFAULT, 10.0, DT_MDL)
    self.line_gone = FirstOrderFilter(np.zeros(2), 2.0, DT_MDL)
    self.line_probs_slow = FirstOrderFilter(np.zeros(2), 3.0, DT_MDL)
    self.line_probs = FirstOrderFilter(np.zeros(2), 0.5, DT_MDL)
    self.curvature = 0.0
    self.trust = 0.0
    self.l_prob = 0.0
    self.r_prob = 0.0

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, active: bool, model_curvature: float) -> float:
    self.trust = self.l_prob = self.r_prob = 0.0
    if not active:
      self.curvature = 0.0
      return 0.0
    target = self._target(model_output, v_ego, model_curvature)
    releasing = abs(target) < abs(self.curvature) or target * self.curvature < 0
    step = (2.0 if releasing else 0.5) / max(v_ego, 1.0) ** 2 * DT_MDL  # jerk over 1 second
    self.curvature = float(np.clip(target, self.curvature - step, self.curvature + step))
    return self.curvature

  def _target(self, model_output: dict[str, np.ndarray], v_ego: float, model_curvature: float) -> float:
    if v_ego < MIN_SPEED or 'lane_lines' not in model_output:
      return 0.0

    lookahead = max(v_ego * LOOKAHEAD_TIME, MIN_LOOKAHEAD)
    lines = model_output['lane_lines'][0, :, :, 0]
    stds = model_output['lane_lines_stds'][0, :, :, 0]

    probs = self.line_probs.update(model_output['lane_lines_prob'][0, 1::2][1:3])
    gone = self.line_gone.update((model_output['lane_lines_prob'][0, 1::2][1:3] < 0.3).astype(float))
    dropping = bool(np.any(probs < 0.6 * self.line_probs_slow.update(model_output['lane_lines_prob'][0, 1::2][1:3])))
    l_prob = float(probs[0] * np.interp(np.interp(0.5 * lookahead, X_IDXS, stds[1]), LINE_STD, [1.0, 0.0]))
    r_prob = float(probs[1] * np.interp(np.interp(0.5 * lookahead, X_IDXS, stds[2]), LINE_STD, [1.0, 0.0]))
    # one line steadily on its own still centers at half say conf. a line that is disappearing gives control back to laneless
    if gone[1] > 0.8 and l_prob > 0.5:
      lane_trust = l_prob / 2
    elif gone[0] > 0.8 and r_prob > 0.5:
      lane_trust = r_prob / 2
    elif dropping:
      lane_trust = min(l_prob, r_prob)
    else:
      lane_trust = l_prob + r_prob - l_prob * r_prob
    self.l_prob, self.r_prob = l_prob, r_prob
    if lane_trust <= 0.0:
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
    plan_x = np.interp(x, model_output['plan'][0, :, 0], model_output['plan'][0, :, 1])
    plan_share = np.interp(abs(model_curvature) * lookahead ** 2 / 2, [0.5, 2.0], [0.3, 0.5]) # blending up to 50% plan with action during sharp curvature
    error = np.clip(center - ((1 - plan_share) * model_curvature * x ** 2 / 2 + plan_share * plan_x), -1.0, 1.0)
    dk = 2.0 * np.sum(weight * error * x ** 2) / np.sum(weight * x ** 4)

    # A model planning to end up further off center than the plant is now is likely going around something
    center_now = (l_prob * (lines[1, 0] + half_width) + r_prob * (lines[2, 0] - half_width)) / (l_prob + r_prob)
    plan_y = np.interp(lookahead, model_output['plan'][0, :, 0], model_output['plan'][0, :, 1])
    away = abs(plan_y - np.interp(lookahead, x, center)) - abs(center_now) - 0.25 * abs(model_curvature) * lookahead ** 2 / 2
    lane_trust *= np.interp(away, (0.5, 1.0), [1.0, 0.0])
    self.trust = float(lane_trust)
    return float(lane_trust * dk)
