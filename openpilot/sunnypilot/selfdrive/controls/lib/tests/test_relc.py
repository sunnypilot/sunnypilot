"""
Copyright (c) 2021-, rav4kumar, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.relc import (
  RoadEdgeLaneChangeController, EDGE_REACTION_TIME, EDGE_CLEAR_TIME, MIN_SPEED,
  VEHICLE_EDGE_MARGIN, EDGE_CLEARANCE,
)

V_HIGH = MIN_SPEED + 2.0
V_LOW = MIN_SPEED - 1.0


class MockEdge:
  def __init__(self, y_val):
    self.y = [y_val] * 33


def edges(left_y, right_y):
  return [MockEdge(left_y), MockEdge(right_y)]


CLOSE_EDGES = edges(-2.0, 1.5)
FAR_EDGES = edges(-10.0, 10.0)


@pytest.fixture
def relc(mocker):
  mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.relc.Params")
  controller = RoadEdgeLaneChangeController()
  controller.enabled = True
  return controller


def drive(controller, road_edge_stds, lane_line_probs, seconds, v_ego=V_HIGH, road_edges=CLOSE_EDGES):
  for _ in range(int(seconds / DT_MDL) + 1):
    controller.update(road_edge_stds, lane_line_probs, v_ego, road_edges)


@pytest.mark.parametrize("road_edge_stds,lane_line_probs,attr", [
  ([0.0, 0.9], [0.0, 0.8, 0.8, 0.8], "left_edge_detected"),
  ([0.9, 0.0], [0.8, 0.8, 0.8, 0.0], "right_edge_detected"),
])
def test_edge_detection(relc, road_edge_stds, lane_line_probs, attr):
  drive(relc, road_edge_stds, lane_line_probs, EDGE_REACTION_TIME + 0.1)
  assert getattr(relc, attr)


def test_edge_detection_requires_time(relc):
  drive(relc, [0.0, 0.9], [0.0, 0.8, 0.8, 0.8], EDGE_REACTION_TIME - 0.05)
  assert not relc.left_edge_detected


def test_both_edges_detected(relc):
  drive(relc, [0.0, 0.0], [0.0, 0.8, 0.8, 0.0], EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected
  assert relc.right_edge_detected


def test_noise_doesnt_clear(relc):
  edge = ([0.0, 0.9], [0.0, 0.8, 0.8, 0.8])
  clear = ([0.9, 0.9], [0.8, 0.8, 0.8, 0.8])

  drive(relc, *edge, EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected

  relc.update(*clear, V_HIGH, CLOSE_EDGES)
  relc.update(*edge, V_HIGH, CLOSE_EDGES)
  assert relc.left_edge_detected


def test_clears_after_window(relc):
  edge = ([0.0, 0.9], [0.0, 0.8, 0.8, 0.8])
  clear = ([0.9, 0.9], [0.8, 0.8, 0.8, 0.8])

  drive(relc, *edge, EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected

  drive(relc, *clear, EDGE_CLEAR_TIME + 0.05)
  assert not relc.left_edge_detected
  assert relc.left_edge_timer == 0.0


def test_low_speed_skips(relc):
  drive(relc, [0.0, 0.9], [0.0, 0.8, 0.8, 0.8], EDGE_REACTION_TIME + 0.1, v_ego=V_LOW)
  assert not relc.left_edge_detected
  assert relc.left_edge_timer == 0.0


def test_speed_drop_resets(relc):
  drive(relc, [0.0, 0.9], [0.0, 0.8, 0.8, 0.8], EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected

  relc.update([0.0, 0.9], [0.0, 0.8, 0.8, 0.8], V_LOW, CLOSE_EDGES)
  assert not relc.left_edge_detected


def test_param_off_resets(relc):
  drive(relc, [0.0, 0.9], [0.0, 0.8, 0.8, 0.8], EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected

  relc.params.get_bool.return_value = False
  relc.read_params()
  relc.update([0.0, 0.9], [0.0, 0.8, 0.8, 0.8], V_HIGH, CLOSE_EDGES)
  assert not relc.left_edge_detected
  assert not relc.right_edge_detected


def test_lane_line_prevents_detection(relc):
  drive(relc, [0.0, 0.9], [0.8, 0.8, 0.8, 0.8], EDGE_REACTION_TIME + 0.1)
  assert not relc.left_edge_detected


def test_one_side_blocks_other_allows(relc):
  drive(relc, [0.9, 0.0], [0.8, 0.8, 0.8, 0.0], EDGE_REACTION_TIME + 0.1)
  assert relc.right_edge_detected
  assert not relc.left_edge_detected


def test_disabled_no_detection(relc):
  relc.enabled = False
  relc.params.get_bool.return_value = False
  drive(relc, [0.0, 0.0], [0.0, 0.8, 0.8, 0.0], EDGE_REACTION_TIME + 0.1)
  assert not relc.left_edge_detected
  assert not relc.right_edge_detected


def test_far_edge_no_block(relc):
  drive(relc, [0.0, 0.9], [0.05, 0.5, 0.5, 0.08], EDGE_REACTION_TIME + 0.1, road_edges=FAR_EDGES)
  assert not relc.left_edge_detected


def test_close_edge_blocks(relc):
  drive(relc, [0.9, 0.0], [0.05, 0.8, 0.8, 0.05], EDGE_REACTION_TIME + 0.1,
        road_edges=edges(-8.0, 1.5))
  assert relc.right_edge_detected
  assert not relc.left_edge_detected


def test_wide_road_no_lines_no_block(relc):
  drive(relc, [0.0, 0.0], [0.05, 0.4, 0.4, 0.05], EDGE_REACTION_TIME + 0.1,
        road_edges=edges(-8.0, 8.0))
  assert not relc.left_edge_detected
  assert not relc.right_edge_detected


def test_narrow_road_both_block(relc):
  drive(relc, [0.0, 0.0], [0.02, 0.4, 0.4, 0.02], EDGE_REACTION_TIME + 0.1,
        road_edges=edges(-2.5, 2.5))
  assert relc.left_edge_detected
  assert relc.right_edge_detected


def test_clearance_boundary(relc):
  boundary = VEHICLE_EDGE_MARGIN + EDGE_CLEARANCE  # 4.78m
  drive(relc, [0.0, 0.9], [0.05, 0.5, 0.5, 0.08], EDGE_REACTION_TIME + 0.1,
        road_edges=edges(-(boundary - 0.1), 10.0))
  assert relc.left_edge_detected

  relc.reset()

  drive(relc, [0.0, 0.9], [0.05, 0.5, 0.5, 0.08], EDGE_REACTION_TIME + 0.1,
        road_edges=edges(-(boundary + 0.1), 10.0))
  assert not relc.left_edge_detected
