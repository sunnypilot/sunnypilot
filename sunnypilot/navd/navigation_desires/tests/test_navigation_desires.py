import pytest
import types

from cereal import log
from openpilot.common.constants import CV

from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.sunnypilot.navd.navigation_desires.navigation_desires import NavigationDesires


def make_car(vEgo=0, leftBlinker=False, rightBlinker=False, leftBlindspot=False, rightBlindspot=False, steeringPressed=False, steeringTorque=0):
  return types.SimpleNamespace(
    vEgo=vEgo, leftBlinker=leftBlinker, rightBlinker=rightBlinker,
    leftBlindspot=leftBlindspot, rightBlindspot=rightBlindspot,
    steeringPressed=steeringPressed, steeringTorque=steeringTorque
  )

NAVIGATION_PARAMS: list[tuple] = [
  ('slightLeft', make_car(), log.Desire.keepLeft),
  ('slightRight', make_car(), log.Desire.keepRight),
  ('slightLeft', make_car(vEgo=9, leftBlindspot=True), log.Desire.none),
  ('slightRight', make_car(vEgo=9, rightBlindspot=True), log.Desire.none),
  ('left', make_car(vEgo=5, leftBlinker=True, rightBlinker=False, leftBlindspot=False), log.Desire.turnLeft),
  ('left', make_car(vEgo=5, leftBlinker=False), log.Desire.none),
  ('right', make_car(vEgo=6, rightBlinker=True, leftBlindspot=False), log.Desire.turnRight),
  ('right', make_car(vEgo=6, rightBlinker=True, rightBlindspot=True), log.Desire.none),
  ('left', make_car(vEgo=9, leftBlinker=True), log.Desire.none),
]

INTEGRATION_PARAMS: list[tuple] = [(carstate, upcoming, log.Desire.none, expected) for upcoming, carstate, expected in NAVIGATION_PARAMS] + [
  (make_car(vEgo=9, leftBlinker=True, steeringPressed=True, steeringTorque=1), 'slightLeft', log.Desire.turnLeft, log.Desire.keepLeft),
  (make_car(vEgo=9, rightBlinker=True, steeringPressed=True, steeringTorque=-1), 'slightRight', log.Desire.turnRight, log.Desire.keepRight),
  (make_car(vEgo=9, leftBlinker=True), 'slightLeft', log.Desire.laneChangeLeft, log.Desire.laneChangeLeft),
  (make_car(vEgo=9, rightBlinker=True), 'slightRight', log.Desire.laneChangeRight, log.Desire.laneChangeRight),
  (make_car(vEgo=9), 'none', log.Desire.none, log.Desire.none),
]

def make_nav_msg(valid=False, upcoming='none'):
  return types.SimpleNamespace(valid=valid, upcomingTurn=upcoming)

@pytest.fixture
def nav_desires(mocker):
  mock_sm = mocker.Mock()
  mock_sm.__getitem__ = mocker.Mock(return_value=make_nav_msg(valid=False))
  mocker.patch('cereal.messaging.SubMaster', return_value=mock_sm)
  return NavigationDesires()

def test_navigation_desires_init(nav_desires):
  assert nav_desires.desire == log.Desire.none
  assert nav_desires.update_counter == -1
  assert nav_desires.turn_speed_limit == 20 * CV.MPH_TO_MS

@pytest.mark.parametrize("upcoming, carstate, expected", NAVIGATION_PARAMS)
def test_navigation_desires_update(nav_desires, mocker, upcoming, carstate, expected):
  nav_desires.sm.__getitem__ = mocker.Mock(return_value=make_nav_msg(valid=True, upcoming=upcoming))
  nav_desires.update_counter = 5  # next update will call update, as 6 % 6 == 0 remainders
  nav_desires.update(carstate, True)
  assert nav_desires.desire == expected

@pytest.mark.parametrize("msg_valid,lateral_active", [
  (False, True),
  (True, False),
], ids=["invalid msg", "lateral inactive"])
def test_navigation_desires_invalid_or_inactive(nav_desires, mocker, msg_valid, lateral_active):
  nav_desires.sm.__getitem__ = mocker.Mock(return_value=make_nav_msg(valid=msg_valid, upcoming='slightLeft'))
  nav_desires.update_counter = 5
  nav_desires.update(make_car(), lateral_active)
  assert nav_desires.desire == log.Desire.none

def test_navigation_desires_get_desire(nav_desires):
  nav_desires.desire = log.Desire.keepLeft
  assert nav_desires.get_desire() == log.Desire.keepLeft

@pytest.mark.parametrize("carstate, upcoming, current_desire, expected", INTEGRATION_PARAMS)
def test_desire_helper_navigation_integration(mocker, carstate, upcoming, current_desire, expected):
  mock_sm = mocker.patch('cereal.messaging.SubMaster')
  mock_sm_instance = mocker.Mock()
  mock_sm.return_value = mock_sm_instance
  mock_sm_instance.__getitem__ = mocker.Mock(return_value=make_nav_msg(valid=True, upcoming=upcoming))

  dh = DesireHelper()
  dh.navigation_desires.update_counter = 11  # same thing as above, different number :)
  dh.desire = current_desire

  if current_desire == log.Desire.laneChangeLeft:
    dh.lane_change_state = log.LaneChangeState.laneChangeStarting
    dh.lane_change_direction = log.LaneChangeDirection.left
  elif current_desire == log.Desire.laneChangeRight:
    dh.lane_change_state = log.LaneChangeState.laneChangeStarting
    dh.lane_change_direction = log.LaneChangeDirection.right

  dh.update(carstate, True, 1.0)
  assert dh.desire == expected
