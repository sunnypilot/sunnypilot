"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import cereal.messaging as messaging
from cereal import car, log
from openpilot.common.constants import CV
from openpilot.common.params import Params


class NavigationDesires:
  def __init__(self):
    self.sm = messaging.SubMaster(['navigationd'])
    self.desire = log.Desire.none
    self._turn_speed_limit = 20 * CV.MPH_TO_MS
    self._params = Params()
    self.param_counter = -1
    self.nav_allowed: bool = False

  def update_params(self):
    self.param_counter += 1
    if self.param_counter % 60 == 0:  # every 3 seconds at 20hz
      self.nav_allowed = self._params.get("NavAllowed", return_default=True)

  def update(self, CS: car.CarState, lateral_active: bool):
    self.update_params()
    self.sm.update(0)
    nav_msg = self.sm['navigationd']
    self.desire = log.Desire.none
    if self.nav_allowed and nav_msg.valid and lateral_active:
      upcoming = nav_msg.upcomingTurn
      if upcoming == 'slightLeft' and (not CS.leftBlindspot or CS.vEgo < self._turn_speed_limit):
        self.desire = log.Desire.keepLeft
      elif upcoming == 'slightRight' and (not CS.rightBlindspot or CS.vEgo < self._turn_speed_limit):
        self.desire = log.Desire.keepRight
      elif upcoming == 'left' and not CS.rightBlinker and not CS.leftBlindspot and CS.vEgo < self._turn_speed_limit:
        self.desire = log.Desire.turnLeft
      elif upcoming == 'right' and not CS.leftBlinker and not CS.rightBlindspot and CS.vEgo < self._turn_speed_limit:
        self.desire = log.Desire.turnRight

  def get_desire(self) -> log.Desire:
    return self.desire
