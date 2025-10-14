"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
from cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

NEARSIDE_PROB = 0.2
EDGE_PROB = 0.35
EDGE_REACTION_TIME = 1.0

class RoadEdgeLaneChangeController:
  def __init__(self, desire_helper):
    self.desire_helper = desire_helper
    self.params = Params()
    self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0
    self._frame = 0

  def set_enabled(self, enabled):
    self.enabled = enabled
    if not enabled:
      self._reset_state()

  def _read_params(self) -> None:
    if self._frame % int(1. / DT_MDL) == 0:
      self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")

  def _reset_state(self):
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0

  def _update_edge_detection(self, road_edge_stds, lane_line_probs):
    if not self.enabled:
      return

    left_road_edge_prob = np.clip(1.0 - road_edge_stds[0], 0.0, 1.0)
    right_road_edge_prob = np.clip(1.0 - road_edge_stds[1], 0.0, 1.0)

    # Lane line probabilities: [left_outer, left_inner, right_inner, right_outer]
    left_lane_nearside_prob = lane_line_probs[0] if len(lane_line_probs) > 0 else 0.0
    right_lane_nearside_prob = lane_line_probs[3] if len(lane_line_probs) > 3 else 0.0

    left_edge_conditions = (
          left_road_edge_prob > EDGE_PROB and
          left_lane_nearside_prob < NEARSIDE_PROB and
          (len(lane_line_probs) <= 3 or right_lane_nearside_prob >= left_lane_nearside_prob)
    )
    right_edge_conditions = (
          right_road_edge_prob > EDGE_PROB and
          right_lane_nearside_prob < NEARSIDE_PROB and
          (len(lane_line_probs) <= 0 or left_lane_nearside_prob >= right_lane_nearside_prob)
    )

    if left_edge_conditions:
      self.left_edge_timer += DT_MDL
      self.left_edge_detected = self.left_edge_timer > EDGE_REACTION_TIME
    else:
      self.left_edge_timer = 0.0
      self.left_edge_detected = False

    if right_edge_conditions:
      self.right_edge_timer += DT_MDL
      self.right_edge_detected = self.right_edge_timer > EDGE_REACTION_TIME
    else:
      self.right_edge_timer = 0.0
      self.right_edge_detected = False

  def update(self, road_edge_stds, lane_line_probs):
    self._read_params()

    if not self.enabled:
      self._frame += 1
      return

    self._update_edge_detection(road_edge_stds, lane_line_probs)
    self._frame += 1

  def should_trigger_lane_change(self, carstate, lateral_active):
    if not self.enabled:
      return False, log.LaneChangeDirection.none
    return False, log.LaneChangeDirection.none

  def is_lane_change_blocked(self, direction):
    if not self.enabled:
      return False

    if direction == log.LaneChangeDirection.left:
      return self.left_edge_detected
    elif direction == log.LaneChangeDirection.right:
      return self.right_edge_detected

    return False

  def can_change_lane_left(self):
    return not self.left_edge_detected if self.enabled else True

  def can_change_lane_right(self):
    return not self.right_edge_detected if self.enabled else True

  @property
  def edge_detected(self):
    return self.left_edge_detected or self.right_edge_detected
