"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest
from cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.sunnypilot.selfdrive.controls.lib.relc import RoadEdgeLaneChangeController, EDGE_REACTION_TIME

@pytest.fixture
def relc_controller(mocker):
  mock_params = mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.relc.Params")
  mock_params.return_value.get_bool.return_value = True

  DH = DesireHelper()
  relc = RoadEdgeLaneChangeController(DH)
  relc.set_enabled(True)
  return relc


def test_disable_resets_state(relc_controller):
  relc = relc_controller
  relc.left_edge_detected = True
  relc.right_edge_detected = True
  relc.left_edge_timer = 5.0
  relc.right_edge_timer = 5.0

  relc.set_enabled(False)

  assert not relc.left_edge_detected
  assert not relc.right_edge_detected
  assert relc.left_edge_timer == 0.0
  assert relc.right_edge_timer == 0.0


def test_lane_change_blocked_left(relc_controller):
  relc = relc_controller
  relc.left_edge_detected = True
  assert relc.is_lane_change_blocked(log.LaneChangeDirection.left)


def test_lane_change_blocked_right(relc_controller):
  relc = relc_controller
  relc.right_edge_detected = True
  assert relc.is_lane_change_blocked(log.LaneChangeDirection.right)


def test_lane_change_not_blocked_opposite_side(relc_controller):
  relc = relc_controller
  relc.left_edge_detected = True
  assert not relc.is_lane_change_blocked(log.LaneChangeDirection.right)

  relc.left_edge_detected = False
  relc.right_edge_detected = True
  assert not relc.is_lane_change_blocked(log.LaneChangeDirection.left)


def test_lane_change_not_blocked_when_disabled(relc_controller):
  relc = relc_controller
  relc.set_enabled(False)
  relc.left_edge_detected = True
  relc.right_edge_detected = True

  assert not relc.is_lane_change_blocked(log.LaneChangeDirection.left)
  assert not relc.is_lane_change_blocked(log.LaneChangeDirection.right)


def test_can_change_lane_left(relc_controller):
  relc = relc_controller
  assert relc.can_change_lane_left()

  relc.left_edge_detected = True
  assert not relc.can_change_lane_left()


def test_can_change_lane_right(relc_controller):
  relc = relc_controller
  assert relc.can_change_lane_right()

  relc.right_edge_detected = True
  assert not relc.can_change_lane_right()


def test_can_change_lane_when_disabled(relc_controller):
  relc = relc_controller
  relc.set_enabled(False)
  relc.left_edge_detected = True
  relc.right_edge_detected = True

  assert relc.can_change_lane_left()
  assert relc.can_change_lane_right()


def test_edge_detected_property(relc_controller):
  relc = relc_controller
  assert not relc.edge_detected

  relc.left_edge_detected = True
  assert relc.edge_detected

  relc.left_edge_detected = False
  relc.right_edge_detected = True
  assert relc.edge_detected

  relc.left_edge_detected = True
  assert relc.edge_detected


def test_should_trigger_lane_change(relc_controller):
  relc = relc_controller
  should_trigger, direction = relc.should_trigger_lane_change(None, True)
  assert not should_trigger
  assert direction == log.LaneChangeDirection.none


def test_update_increments_frame(relc_controller):
  relc = relc_controller
  initial = relc._frame
  relc.update([0.5, 0.5], [0.5, 0.5, 0.5, 0.5])
  assert relc._frame == initial + 1


def test_left_edge_detection(relc_controller):
  relc = relc_controller
  road_edge_stds = [0.0, 0.9]
  lane_line_probs = [0.0, 0.8, 0.8, 0.8]

  num_updates = int(EDGE_REACTION_TIME / DT_MDL) + 5
  for _ in range(num_updates):
    relc.update(road_edge_stds, lane_line_probs)

  assert relc.left_edge_detected


def test_right_edge_detection(relc_controller):
  relc = relc_controller
  road_edge_stds = [0.9, 0.0]
  lane_line_probs = [0.8, 0.8, 0.8, 0.0]

  num_updates = int(EDGE_REACTION_TIME / DT_MDL) + 5
  for _ in range(num_updates):
    relc.update(road_edge_stds, lane_line_probs)

  assert relc.right_edge_detected


def test_edge_detection_requires_time(relc_controller):
  relc = relc_controller
  road_edge_stds = [0.0, 0.9]
  lane_line_probs = [0.0, 0.8, 0.8, 0.8]

  num_updates = int(EDGE_REACTION_TIME / DT_MDL) - 1
  for _ in range(num_updates):
    relc.update(road_edge_stds, lane_line_probs)

  assert not relc.left_edge_detected


def test_edge_detection_clears(relc_controller):
  relc = relc_controller
  road_edge_stds = [0.0, 0.9]
  lane_line_probs = [0.0, 0.8, 0.8, 0.8]

  num_updates = int(EDGE_REACTION_TIME / DT_MDL) + 5
  for _ in range(num_updates):
    relc.update(road_edge_stds, lane_line_probs)
  assert relc.left_edge_detected

  road_edge_stds = [0.9, 0.9]
  relc.update(road_edge_stds, lane_line_probs)

  assert not relc.left_edge_detected
  assert relc.left_edge_timer == 0.0


def test_both_edges_detected(relc_controller):
  relc = relc_controller
  road_edge_stds = [0.0, 0.0]
  lane_line_probs = [0.0, 0.8, 0.8, 0.0]

  num_updates = int(EDGE_REACTION_TIME / DT_MDL) + 5
  for _ in range(num_updates):
    relc.update(road_edge_stds, lane_line_probs)

  assert relc.left_edge_detected
  assert relc.right_edge_detected
