"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

LANE_WIDTH_DEFAULT = 3.6  # m (reseeded to model's lane width upon initialization)
LANE_WIDTH_CLIP = (2.8, 4.5)  # m
LOOKAHEAD_TIME = 1.5  # s
MIN_LOOKAHEAD = 10.0  # m
MIN_SPEED = 5.0  # m/s
LINE_STD = (0.2, 0.6)
POINT_STD = 0.1
MAX_ERROR = 1.0
YIELD = (0.2, 0.45)
X_IDXS = np.array(ModelConstants.X_IDXS)


class Laneful: # TODO-SP: Rename this to blendful or something similar because it is not pure laneful anymore.
  def __init__(self):
    self.lane_width = FirstOrderFilter(LANE_WIDTH_DEFAULT, 10.0, DT_MDL, initialized=False)
    self.line_gone = FirstOrderFilter(np.zeros(2), 2.0, DT_MDL)
    self.line_probs_slow = FirstOrderFilter(np.zeros(2), 3.0, DT_MDL)
    self.line_probs = FirstOrderFilter(np.zeros(2), 0.5, DT_MDL)
    self.usual_offset = FirstOrderFilter(0.0, 10.0, DT_MDL, initialized=False)
    self.going_around = False
    self.trust = 0.0
    self.curvature = 0.0

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, active: bool, model_curvature: float) -> float:
    fading = not active or v_ego < MIN_SPEED
    if fading:
      self.trust = 0.0
      self.usual_offset.initialized = False
      self.lane_width.initialized = False
      self.going_around = False
    target = 0.0 if fading else self._target(model_output, v_ego, model_curvature)
    releasing = not fading and (abs(target) < abs(self.curvature) or target * self.curvature < 0)
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
    if lane_trust <= 0.0:
      self.trust = 0.0
      return 0.0

    win = (X_IDXS >= 0.5 * lookahead) & (X_IDXS <= 1.5 * lookahead)
    x = X_IDXS[win]
    half_width = self.lane_width.x / 2
    if l_prob * r_prob > 0.5:
      width = np.interp(lookahead, X_IDXS, lines[2]) - np.interp(lookahead, X_IDXS, lines[1])
      self.lane_width.update(float(np.clip(width, *LANE_WIDTH_CLIP)))
      half_width = np.clip(lines[2, win] - lines[1, win], *LANE_WIDTH_CLIP) / 2
    l_var = stds[1, win] ** 2 / max(l_prob, 1e-4)
    r_var = stds[2, win] ** 2 / max(r_prob, 1e-4)
    center = (r_var * (lines[1, win] + half_width) + l_var * (lines[2, win] - half_width)) / (l_var + r_var)
    weight = 1.0 / (l_var * r_var / (l_var + r_var) + POINT_STD ** 2)

    # Fit curvature to place the plant in center: e ~ dk x^2 / 2
    plan_x = np.interp(x, model_output['plan'][0, :, 0], model_output['plan'][0, :, 1])
    plan_share = np.interp(abs(model_curvature) * lookahead ** 2 / 2, [0.5, 2.0], [0.3, 0.5]) # blending up to 50% plan with action during sharp curvature
    error = np.clip(center - ((1 - plan_share) * model_curvature * x ** 2 / 2 + plan_share * plan_x), -1.0, 1.0)
    dk = 2.0 * np.sum(weight * error * x ** 2) / np.sum(weight * x ** 4)

    # A model planning to end up further from its usual spot in the lane than the plant is now is likely going around something
    hw_now = np.clip(lines[2, 0] - lines[1, 0], *LANE_WIDTH_CLIP) / 2 if l_prob * r_prob > 0.5 else self.lane_width.x / 2
    center_now = (l_prob * (lines[1, 0] + hw_now) + r_prob * (lines[2, 0] - hw_now)) / (l_prob + r_prob)
    plan_y = np.interp(lookahead, model_output['plan'][0, :, 0], model_output['plan'][0, :, 1])
    offset = plan_y - np.interp(lookahead, x, center)
    usual = self.usual_offset.x if self.usual_offset.initialized else offset
    swerve = abs(offset - usual) - 0.25 * abs(model_curvature) * lookahead ** 2 / 2
    away = swerve - abs(-center_now - usual)
    lane_curvature = 2.0 * np.polyfit(x, center, 2)[0]
    inside_curve = abs(lane_curvature) * lookahead ** 2 / 2 > 0.1 and (offset - usual) * lane_curvature > 0
    if inside_curve:
      self.going_around = False
    elif away > YIELD[0]:
      self.going_around = True
    elif swerve < YIELD[0] / 2:
      self.going_around = False
    self.usual_offset.update_alpha(20.0 if self.going_around else 10.0)
    self.usual_offset.update(offset)
    if inside_curve:
      lane_trust *= np.interp(abs(offset) - abs(center_now) - 0.25 * abs(model_curvature) * lookahead ** 2 / 2, (0.5, 1.0), [1.0, 0.0])
    else:
      lane_trust *= np.interp(swerve, (YIELD[0] / 2, YIELD[0]), [1.0, 0.0]) if self.going_around else np.interp(away, YIELD, [1.0, 0.0])

    self.trust = lane_trust if lane_trust < self.trust else self.trust + (lane_trust - self.trust) * DT_MDL / (1.5 + DT_MDL)
    return float(self.trust * dk)
