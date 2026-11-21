"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import custom
from opendbc.car.structs import car, CarParamsSP

from openpilot.common.params import Params
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.selfdrived.always_on_bsm import AlwaysOnBsm
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName

# (leftBlindspot, leftBlinker, rightBlindspot, rightBlinker) -> alert expected
BSM_CASES = [
  (False, False, False, False, False),
  (True, False, False, False, False),   # car in left blind spot, no blinker
  (False, True, False, False, False),   # left blinker, left blind spot clear
  (True, True, False, False, True),     # left blinker into occupied left blind spot
  (False, False, True, False, False),   # car in right blind spot, no blinker
  (False, False, False, True, False),   # right blinker, right blind spot clear
  (False, False, True, True, True),     # right blinker into occupied right blind spot
  (True, False, False, True, False),    # left occupied, but signaling right
  (False, True, True, False, False),    # right occupied, but signaling left
  (True, True, True, True, False),      # hazards
]
ALERTING_CASES = [case[:-1] for case in BSM_CASES if case[-1]]


def bsm_helper(bsm_supported: bool = True) -> AlwaysOnBsm:
  # use tesla if bsm_supported is true to ensure has_bsm always returns true
  return AlwaysOnBsm(car.CarParams(brand="tesla" if bsm_supported else ""), CarParamsSP())


def cs_helper(left_bsm=False, left_blinker=False, right_bsm=False, right_blinker=False) -> car.CarState:
  return car.CarState(leftBlindspot=left_bsm, leftBlinker=left_blinker, rightBlindspot=right_bsm, rightBlinker=right_blinker)


class TestAlwaysOnBsm(OpenpilotTestCase):
  def setup_method(self):
    self.params = Params()
    self.params.put_bool("AlwaysOnBsm", True, block=True)
    self.helper = bsm_helper()
    self.events_sp = EventsSP()

  def teardown_method(self):
    self.params.remove("AlwaysOnBsm")

  def _update(self, CS, lane_change_blocked: bool = False) -> bool:
    self.events_sp.clear()
    self.helper.update(CS, self.events_sp, lane_change_blocked)
    return self.events_sp.has(EventNameSP.blindSpotAlert)

  @parameterized.expand(BSM_CASES)
  def test_alert(self, left_bsm, left_blinker, right_bsm, right_blinker, expected):
    CS = cs_helper(left_bsm, left_blinker, right_bsm, right_blinker)
    assert self._update(CS) == expected

  @parameterized.expand(ALERTING_CASES)
  def test_lane_change_blocked_suppresses_alert(self, left_bsm, left_blinker, right_bsm, right_blinker):
    # laneChangeBlocked already alerts, avoid a duplicate
    CS = cs_helper(left_bsm, left_blinker, right_bsm, right_blinker)
    assert self._update(CS)
    assert not self._update(CS, lane_change_blocked=True)

  def test_disabled_by_param(self):
    self.params.put_bool("AlwaysOnBsm", False, block=True)
    self.helper = bsm_helper()
    assert not self._update(cs_helper(left_bsm=True, left_blinker=True))

  def test_no_alert_without_bsm_support(self):
    self.helper = bsm_helper(bsm_supported=False)
    assert not self._update(cs_helper(left_bsm=True, left_blinker=True))
