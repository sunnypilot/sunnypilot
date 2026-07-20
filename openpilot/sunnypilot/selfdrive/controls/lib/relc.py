"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

NEARSIDE_PROB = 0.2
EDGE_PROB = 0.35
EDGE_REACTION_TIME = 1.0
EDGE_CLEAR_TIME = 0.3
MIN_SPEED = 20 * CV.MPH_TO_MS


class RoadEdgeLaneChangeController:
  def __init__(self, desire_helper):
    self.DH = desire_helper
    self.params = Params()
    self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")
    self.param_read_counter = 0
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0
    self.left_clear_timer = 0.0
    self.right_clear_timer = 0.0

  def read_params(self) -> None:
    self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def reset(self) -> None:
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0
    self.left_clear_timer = 0.0
    self.right_clear_timer = 0.0

  def update(self, road_edge_stds, lane_line_probs, v_ego: float) -> None:
    self.update_params()

    if not self.enabled or v_ego < MIN_SPEED:
      self.reset()
      return

    left_edge_prob = np.clip(1.0 - road_edge_stds[0], 0.0, 1.0)
    right_edge_prob = np.clip(1.0 - road_edge_stds[1], 0.0, 1.0)
    left_lane_prob = lane_line_probs[0]
    right_lane_prob = lane_line_probs[3]

    left_cond = left_edge_prob > EDGE_PROB and left_lane_prob < NEARSIDE_PROB and right_lane_prob >= left_lane_prob
    right_cond = right_edge_prob > EDGE_PROB and right_lane_prob < NEARSIDE_PROB and left_lane_prob >= right_lane_prob

    if left_cond:
      self.left_edge_timer = min(self.left_edge_timer + DT_MDL, EDGE_REACTION_TIME + EDGE_CLEAR_TIME)
      self.left_clear_timer = 0.0
      if self.left_edge_timer > EDGE_REACTION_TIME:
        self.left_edge_detected = True
    else:
      self.left_clear_timer += DT_MDL
      if self.left_clear_timer > EDGE_CLEAR_TIME:
        self.left_edge_timer = 0.0
        self.left_edge_detected = False

    if right_cond:
      self.right_edge_timer = min(self.right_edge_timer + DT_MDL, EDGE_REACTION_TIME + EDGE_CLEAR_TIME)
      self.right_clear_timer = 0.0
      if self.right_edge_timer > EDGE_REACTION_TIME:
        self.right_edge_detected = True
    else:
      self.right_clear_timer += DT_MDL
      if self.right_clear_timer > EDGE_CLEAR_TIME:
        self.right_edge_timer = 0.0
        self.right_edge_detected = False
