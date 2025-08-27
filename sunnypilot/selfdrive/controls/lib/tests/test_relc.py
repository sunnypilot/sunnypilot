"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest
from cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.relc import RoadEdgeLaneChangeController


class DummyParams:
  """Mock Params object for testing"""
  def __init__(self, enabled=True):
    self._enabled = enabled

  def get_bool(self, key):
    return self._enabled


@pytest.fixture
def controller(monkeypatch):
  # Replace Params with DummyParams
  monkeypatch.setattr(
    "openpilot.sunnypilot.selfdrive.controls.lib.relc.Params",
    lambda: DummyParams(True),
  )
  return RoadEdgeLaneChangeController(desire_helper=None)


def test_init_and_enable_disable(controller):
  assert controller.enabled is True
  controller.set_enabled(False)
  assert controller.enabled is False
  assert not controller.edge_detected
  assert controller.left_edge_timer == 0.0
  assert controller.right_edge_timer == 0.0


def test_update_params_reads_enabled(monkeypatch):
  monkeypatch.setattr(
    "openpilot.sunnypilot.selfdrive.controls.lib.relc.Params",
    lambda: DummyParams(False),
  )
  c = RoadEdgeLaneChangeController(desire_helper=None)
  c.param_check_counter = 0
  c.update_params()
  assert c.enabled is False


def test_left_edge_detection(controller):
  road_edge_stds = [0.5, 1.0]  # left std low → higher prob
  lane_line_probs = [0.0, 0.5, 0.5, 0.8]  # left_nearside low
  # Run until EDGE_REACTION_TIME passes
  for _ in range(int(1.0 / DT_MDL) + 1):
    controller._update_edge_detection(road_edge_stds, lane_line_probs)
  assert controller.left_edge_detected
  assert controller.can_change_lane_left() is False


def test_right_edge_detection(controller):
  road_edge_stds = [1.0, 0.5]  # right std low → higher prob
  lane_line_probs = [0.8, 0.5, 0.5, 0.0]  # right_nearside low
  for _ in range(int(1.0 / DT_MDL) + 1):
    controller._update_edge_detection(road_edge_stds, lane_line_probs)
  assert controller.right_edge_detected
  assert controller.can_change_lane_right() is False


def test_reset_edge_detection(controller):
  road_edge_stds = [0.5, 1.0]
  lane_line_probs = [0.0, 0.5, 0.5, 0.8]
  for _ in range(int(1.0 / DT_MDL) + 1):
    controller._update_edge_detection(road_edge_stds, lane_line_probs)
  assert controller.left_edge_detected
  controller._reset_state()
  assert not controller.left_edge_detected
  assert not controller.right_edge_detected


def test_is_lane_change_blocked(controller):
  controller.left_edge_detected = True
  controller.right_edge_detected = False
  assert controller.is_lane_change_blocked(log.LaneChangeDirection.left) is True
  assert controller.is_lane_change_blocked(log.LaneChangeDirection.right) is False
  assert controller.is_lane_change_blocked(log.LaneChangeDirection.none) is False


def test_should_trigger_lane_change(controller):
  result = controller.should_trigger_lane_change(carstate=None, lateral_active=True)
  assert result == (False, log.LaneChangeDirection.none)


def test_disabled_controller(monkeypatch):
  monkeypatch.setattr(
    "openpilot.sunnypilot.selfdrive.controls.lib.relc.Params",
    lambda: DummyParams(False),
  )
  c = RoadEdgeLaneChangeController(desire_helper=None)
  road_edge_stds = [0.5, 0.5]
  lane_line_probs = [0.0, 0.0, 0.0, 0.0]
  c.update(road_edge_stds, lane_line_probs)
  assert not c.edge_detected
  assert c.can_change_lane_left() is True
  assert c.can_change_lane_right() is True

