"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
from cereal import log
from openpilot.common.conversions import Conversions as CV
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

NEARSIDE_PROB = 0.2
EDGE_PROB = 0.35
EDGE_LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS
EDGE_REACTION_TIME = 1.0
EDGE_COOLDOWN_TIME = 5.0
MAX_EDGE_DETECTION_TIME = 3.0

class RoadEdgeLaneChangeController:
  def __init__(self, desire_helper):
    self.desire_helper = desire_helper
    self.params = Params()
    self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0
    self.edge_triggered_direction = log.LaneChangeDirection.none
    self.edge_cooldown_timer = 0.0
    self.edge_lane_change_active = False
    self.safe_for_edge_lane_change = False
    self.param_check_counter = 0
    self.PARAM_CHECK_FREQUENCY = 100

  def set_enabled(self, enabled):
    self.enabled = enabled
    if not enabled:
      self._reset_state()

  def read_params(self) -> None:
    self.enabled = self.params.get_bool("RoadEdgeLaneChangeEnabled")

  def update_params(self) -> None:
    if self.param_check_counter % self.PARAM_CHECK_FREQUENCY == 0:
      self.read_params()
    self.param_check_counter += 1

  def _reset_state(self):
    self.left_edge_detected = False
    self.right_edge_detected = False
    self.left_edge_timer = 0.0
    self.right_edge_timer = 0.0
    self.edge_triggered_direction = log.LaneChangeDirection.none
    self.edge_lane_change_active = False

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
    self.update_params()
    if not self.enabled:
      return
    if self.edge_cooldown_timer > 0.0:
      self.edge_cooldown_timer -= DT_MDL
    self._update_edge_detection(road_edge_stds, lane_line_probs)
    if self.left_edge_timer > MAX_EDGE_DETECTION_TIME or self.right_edge_timer > MAX_EDGE_DETECTION_TIME:
      self._reset_state()

  def should_trigger_lane_change(self, carstate, lateral_active):
    if not self.enabled or not (self.left_edge_detected or self.right_edge_detected):
      return False, log.LaneChangeDirection.none
    self._check_safety_conditions(carstate, lateral_active)
    if not self.safe_for_edge_lane_change:
      return False, log.LaneChangeDirection.none
    direction = self._determine_lane_change_direction(carstate)
    if direction != log.LaneChangeDirection.none and not self.edge_lane_change_active:
      return True, direction
    return False, log.LaneChangeDirection.none

  def trigger_edge_lane_change(self, direction):
    if direction == log.LaneChangeDirection.none:
      return False
    self.edge_triggered_direction = direction
    self.edge_lane_change_active = True
    self.edge_cooldown_timer = EDGE_COOLDOWN_TIME
    return True

  def _check_safety_conditions(self, carstate, lateral_active):
    v_ego = carstate.vEgo
    self.safe_for_edge_lane_change = (
          v_ego >= EDGE_LANE_CHANGE_SPEED_MIN and
          lateral_active and
          self.edge_cooldown_timer <= 0.0 and
          self.desire_helper.lane_change_state == log.LaneChangeState.off and
          not (carstate.leftBlindspot or carstate.rightBlindspot) and
          not carstate.brakePressed
    )

  def _determine_lane_change_direction(self, carstate):
    if self.left_edge_detected and not carstate.rightBlindspot:
      return log.LaneChangeDirection.right
    if self.right_edge_detected and not carstate.leftBlindspot:
      return log.LaneChangeDirection.left
    return log.LaneChangeDirection.none

  def update_lane_change_state(self):
    if self.edge_lane_change_active and self.desire_helper.lane_change_state == log.LaneChangeState.off:
      self.edge_lane_change_active = False
      self.edge_triggered_direction = log.LaneChangeDirection.none

  def should_override_blinker(self, carstate):
    if not self.edge_lane_change_active:
      return False, False
    left_blinker = self.edge_triggered_direction == log.LaneChangeDirection.left
    right_blinker = self.edge_triggered_direction == log.LaneChangeDirection.right
    return True, (left_blinker, right_blinker)

  @property
  def edge_detected(self):
    return self.left_edge_detected or self.right_edge_detected
