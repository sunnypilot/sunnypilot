"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.sunnypilot.selfdrive.controls.lib.relc import (
  RoadEdgeLaneChangeController, EDGE_REACTION_TIME, EDGE_CLEAR_TIME, MIN_SPEED,
)

V_HIGH = MIN_SPEED + 2.0
V_LOW = MIN_SPEED - 1.0


@pytest.fixture
def relc(mocker):
  mock_params = mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.relc.Params")
  mock_params.return_value.get_bool.return_value = True
  controller = RoadEdgeLaneChangeController(DesireHelper())
  controller.enabled = True
  return controller


def drive(controller, road_edge_stds, lane_line_probs, seconds, v_ego=V_HIGH):
  for _ in range(int(seconds / DT_MDL) + 1):
    controller.update(road_edge_stds, lane_line_probs, v_ego)


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

  relc.update(*clear, V_HIGH)
  relc.update(*edge, V_HIGH)
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

  relc.update([0.0, 0.9], [0.0, 0.8, 0.8, 0.8], V_LOW)
  assert not relc.left_edge_detected


def test_param_off_resets(relc):
  drive(relc, [0.0, 0.9], [0.0, 0.8, 0.8, 0.8], EDGE_REACTION_TIME + 0.1)
  assert relc.left_edge_detected

  relc.params.get_bool.return_value = False
  relc.read_params()
  relc.update([0.0, 0.9], [0.0, 0.8, 0.8, 0.8], V_HIGH)
  assert not relc.left_edge_detected
  assert not relc.right_edge_detected
