import pytest
import numpy as np
from cereal import custom, log
from openpilot.common.params import Params

from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.sunnypilot.selfdrive.controls.lib.lane_turn_desire import LaneTurnController, LANE_CHANGE_SPEED_MIN, TURN_STATE
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeMode


@pytest.mark.parametrize("left_blinker,right_blinker,v_ego,blindspot_left,blindspot_right,expected", [
    (True, False, 5, False, False, custom.TurnDirection.turnLeft),
    (False, True, 6, False, False, custom.TurnDirection.turnRight),
    (True, False, 26, False, False, custom.TurnDirection.none),
    (True, False, 7, True, False, custom.TurnDirection.none),
    (False, True, 6, False, True, custom.TurnDirection.none),
    (False, False, 5, False, False, custom.TurnDirection.none),
    (True, True, 5, False, False, custom.TurnDirection.none),
], ids=["left blinker", "right blinker", "left blinkers but over speed", "left blindspot w/ left blinker", "right blindspot w/ left blinker",
        "no blinkers", "both blinkers"])
def test_lane_turn_desire_conditions(left_blinker, right_blinker, v_ego, blindspot_left, blindspot_right, expected):
    controller = LaneTurnController()
    controller.lane_turn_type = TURN_STATE['NUDGELESS']
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = custom.TurnDirection.none
    controller.update_lane_turn(blindspot_left, blindspot_right, left_blinker, right_blinker, v_ego)
    assert np.equal(controller.turn_direction, expected), f"Expected {expected}, speed {v_ego}, got {controller.turn_direction}"


def test_lane_turn_desire_disabled():
    controller = LaneTurnController()
    controller.lane_turn_type = TURN_STATE['OFF']
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = custom.TurnDirection.none
    controller.update_lane_turn(False, False, True, False, 6)
    assert np.equal(controller.turn_direction , custom.TurnDirection.none), f"Expected no turn desire, got {controller.turn_direction}"


def test_lane_turn_overrides_lane_change():
    controller = LaneTurnController()
    controller.lane_turn_type = TURN_STATE['NUDGELESS']
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = custom.TurnDirection.none
    controller.update_lane_turn(False, False, True, False, 5)
    assert np.equal(controller.turn_direction, custom.TurnDirection.turnLeft), f"Expected left turn desire, got {controller.turn_direction}"

    controller.update_lane_turn(False, False, False, True, 6)
    assert np.equal(controller.turn_direction, custom.TurnDirection.turnRight), f"Expected right turn desire, got {controller.turn_direction}"

    controller.update_lane_turn(False, False, False, False, 7)
    assert np.equal(controller.turn_direction, custom.TurnDirection.none), f"Expected no turn desire, got {controller.turn_direction}"


@pytest.mark.parametrize("v_ego,expected", [
    (8.93, custom.TurnDirection.turnLeft),   # just below threshold
    (24.0, custom.TurnDirection.none),       # above threshold
    (25.95, custom.TurnDirection.none),       # just above threshold
], ids=["below threshold", "above threshold", "just above threshold"])
def test_lane_turn_desire_speed_boundary(v_ego, expected):
    controller = LaneTurnController()
    controller.lane_turn_type = TURN_STATE['NUDGELESS']
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = custom.TurnDirection.none
    controller.update_lane_turn(False, True, True, False, v_ego)
    assert np.equal(controller.turn_direction, expected), f"Expected {expected} at speed {v_ego}, got {controller.turn_direction}"


class DummyCarState:
    def __init__(self, vEgo=0, leftBlinker=False, rightBlinker=False, leftBlindspot=False, rightBlindspot=False,
                 steeringPressed=False, steeringTorque=0, brakePressed=False):
        self.vEgo = vEgo
        self.leftBlinker = leftBlinker
        self.rightBlinker = rightBlinker
        self.leftBlindspot = leftBlindspot
        self.rightBlindspot = rightBlindspot
        self.steeringPressed = steeringPressed
        self.steeringTorque = steeringTorque
        self.brakePressed = brakePressed


def nudgeless_params():
    params = Params()
    params.put("LaneTurnDesire", TURN_STATE['NUDGELESS'])
    params.put("LaneTurnValue", 20.0)
    params.put("AutoLaneChangeTimer", AutoLaneChangeMode.NUDGELESS)

def nudge_params():
    params = Params()
    params.put("LaneTurnDesire", TURN_STATE['NUDGE'])
    params.put("LaneTurnValue", 20.0)
    params.put("AutoLaneChangeTimer", AutoLaneChangeMode.NUDGE)


@pytest.mark.parametrize("carstate, expected_desire", [
    (DummyCarState(vEgo=5, leftBlinker=True, rightBlinker=False, leftBlindspot=False, rightBlindspot=False), log.Desire.turnLeft),
    (DummyCarState(vEgo=7, leftBlinker=False, rightBlinker=True, leftBlindspot=False, rightBlindspot=False), log.Desire.turnRight),
    (DummyCarState(vEgo=5, leftBlinker=False, rightBlinker=False, leftBlindspot=False, rightBlindspot=False), log.Desire.none),
    (DummyCarState(vEgo=5, leftBlinker=True, rightBlinker=True, leftBlindspot=False, rightBlindspot=False), log.Desire.none),
], ids=["nudgeless left turn", "nudgeless right turn", "no blinkers", "both blinkers"])
def test_lane_turn_nudgeless(carstate, expected_desire):
    nudgeless_params()
    dh = DesireHelper()
    dh.update(carstate, True, 1.0)
    assert np.equal(dh.desire, expected_desire), f"Expected {expected_desire}, got {dh.desire}"


@pytest.mark.parametrize("carstate, expected_desire", [
    (DummyCarState(vEgo=5, leftBlinker=True, rightBlinker=False, leftBlindspot=False, rightBlindspot=False,
                   steeringPressed=True, steeringTorque=1), log.Desire.turnLeft),
    (DummyCarState(vEgo=7, leftBlinker=False, rightBlinker=True, leftBlindspot=False, rightBlindspot=False,
                   steeringPressed=True, steeringTorque=-1), log.Desire.turnRight),
    (DummyCarState(vEgo=5, leftBlinker=True, rightBlinker=False, leftBlindspot=False, rightBlindspot=False), log.Desire.none),
    (DummyCarState(vEgo=7, leftBlinker=False, rightBlinker=True, leftBlindspot=False, rightBlindspot=False), log.Desire.none),
], ids=["nudge left turn with input", "nudge right turn with input", "nudge left turn no input", "nudge right turn no input"])
def test_lane_turn_nudge(carstate, expected_desire):
    nudge_params()
    dh = DesireHelper()
    dh.update(carstate, True, 1.0)
    assert np.equal(dh.desire, expected_desire), f"Expected {expected_desire}, got {dh.desire}"
