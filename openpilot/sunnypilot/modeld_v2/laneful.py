"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Laneful: nudge the model's curvature toward the lane center seen by the lane lines.
The model stays in charge; this only adds a pure-pursuit correction weighted by lane line confidence,
and fades to zero (plain laneless) when the lines are weak.
"""
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan

LANE_WIDTH_DEFAULT = 3.7  # m
LANE_WIDTH_CLIP = (2.8, 4.5)  # m
LOOKAHEAD_TIME = 1.5  # s
MIN_LOOKAHEAD = 10.0  # m
MAX_ERROR = 0.5  # m, cap on how far laneful can pull
MIN_SPEED = 9.0  # m/s


class Laneful:
  def __init__(self):
    self.lane_width = FirstOrderFilter(LANE_WIDTH_DEFAULT, 10.0, DT_MDL)

  def update(self, model_output: dict[str, np.ndarray], v_ego: float, strength: float, desire_active: bool) -> float:
    """Returns a curvature offset to add to the model's raw desired curvature."""
    if strength <= 0.0 or desire_active or v_ego < MIN_SPEED or 'lane_lines' not in model_output:
      return 0.0

    lookahead = max(v_ego * LOOKAHEAD_TIME, MIN_LOOKAHEAD)
    lines = model_output['lane_lines'][0, :, :, 0]
    left_y = np.interp(lookahead, ModelConstants.X_IDXS, lines[1])
    right_y = np.interp(lookahead, ModelConstants.X_IDXS, lines[2])

    # line confidence, discounted when the model is unsure where the line is
    probs = model_output['lane_lines_prob'][0, 1::2]
    stds = model_output['lane_lines_stds'][0, :, 0, 0]
    l_prob = float(probs[1] * np.interp(stds[1], [0.15, 0.3], [1.0, 0.0]))
    r_prob = float(probs[2] * np.interp(stds[2], [0.15, 0.3], [1.0, 0.0]))

    if l_prob * r_prob > 0.5:
      self.lane_width.update(float(np.clip(right_y - left_y, *LANE_WIDTH_CLIP)))
    half_width = self.lane_width.x / 2

    # one weak line -> hug the strong one at half a lane width
    center_y = (l_prob * (left_y + half_width) + r_prob * (right_y - half_width)) / (l_prob + r_prob + 1e-4)
    lane_trust = l_prob + r_prob - l_prob * r_prob

    plan = model_output['plan'][0, :, Plan.POSITION]
    plan_y = np.interp(lookahead, plan[:, 0], plan[:, 1])

    error = np.clip(center_y - plan_y, -MAX_ERROR, MAX_ERROR)
    return float(strength * lane_trust * 2.0 * error / lookahead ** 2)


if __name__ == "__main__":
  def fake_output(left_y, right_y, prob=0.9, std=0.1, plan_y=0.0):
    x = np.array(ModelConstants.X_IDXS)
    lines = np.zeros((1, 4, len(x), 2), dtype=np.float32)
    lines[0, 1, :, 0], lines[0, 2, :, 0] = left_y, right_y
    plan = np.zeros((1, len(x), 15), dtype=np.float32)
    plan[0, :, 0], plan[0, :, 1] = x, plan_y
    return {'lane_lines': lines, 'plan': plan,
            'lane_lines_prob': np.full((1, 8), prob, dtype=np.float32),
            'lane_lines_stds': np.full((1, 4, len(x), 2), std, dtype=np.float32)}

  lf = Laneful()
  assert abs(lf.update(fake_output(-1.85, 1.85), 25.0, 1.0, False)) < 1e-6, "centered -> no nudge"
  assert lf.update(fake_output(-1.0, 2.7), 25.0, 1.0, False) > 0, "lane center to the +y side -> nudge toward +y"
  assert lf.update(fake_output(-2.7, 1.0), 25.0, 1.0, False) < 0, "lane center to the -y side -> nudge toward -y"
  assert lf.update(fake_output(-1.0, 2.7), 25.0, 1.0, True) == 0.0, "off during lane change/turn"
  assert lf.update(fake_output(-1.0, 2.7, std=0.5), 25.0, 1.0, False) == 0.0, "blurry lines -> laneless"
  assert lf.update(fake_output(-1.0, 2.7), 25.0, 0.0, False) == 0.0, "strength 0 -> off"
  assert lf.update(fake_output(-1.0, 2.7), 25.0, 0.5, False) < lf.update(fake_output(-1.0, 2.7), 25.0, 1.0, False)
  print("laneful self-check ok")
