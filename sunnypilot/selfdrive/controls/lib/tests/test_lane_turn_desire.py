import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.lane_turn_desire import LaneTurnController, LANE_CHANGE_SPEED_MIN


class TurnDirection:
    none = 0
    turnLeft = 1
    turnRight = 2

@pytest.mark.parametrize("left_blinker,right_blinker,v_ego,blindspot_left,blindspot_right,expected", [
    (True, False, 5, False, False, TurnDirection.turnLeft),
    (False, True, 6, False, False, TurnDirection.turnRight),
    (True, False, 9, False, False, TurnDirection.none),
    (True, False, 7, True, False, TurnDirection.none),
    (False, True, 6, False, True, TurnDirection.none),
    (False, False, 5, False, False, TurnDirection.none),
    (True, True, 5, False, False, TurnDirection.none),
])
def test_lane_turn_desire_conditions(left_blinker, right_blinker, v_ego, blindspot_left, blindspot_right, expected):
    dh = object()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(blindspot_left, blindspot_right, left_blinker, right_blinker, v_ego)
    assert controller.get_turn_direction() == expected

def test_lane_turn_desire_disabled():
    dh = object()
    controller = LaneTurnController(dh)
    controller.enabled = False
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(False, False, True, False, 7)
    assert controller.get_turn_direction() == TurnDirection.none

def test_lane_turn_overrides_lane_change():
    dh = object()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    # left turn desire
    controller.update_lane_turn(False, False, True, False, 5)
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    # right turn desire
    controller.update_lane_turn(False, False, False, True, 6)
    assert controller.get_turn_direction() == TurnDirection.turnRight
    # no turn
    controller.update_lane_turn(False, False, False, False, 7)
    assert controller.get_turn_direction() == TurnDirection.none

@pytest.mark.parametrize("v_ego,expected", [
    (8.93, TurnDirection.turnLeft),   # just below threshold
    (8.96, TurnDirection.none),       # above threshold
    (8.95, TurnDirection.none),       # just above threshold
])
def test_lane_turn_desire_speed_boundary(v_ego, expected):
    dh = object()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(False, True, True, False, v_ego)
    assert controller.get_turn_direction() == expected
