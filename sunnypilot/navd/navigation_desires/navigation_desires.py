"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import cereal.messaging as messaging
from cereal import car, log
from openpilot.common.constants import CV


class NavigationDesires:
  def __init__(self):
    self.sm = messaging.SubMaster(['navigationd'])
    self.desire = log.Desire.none
    self.update_counter = -1
    self.turn_speed_limit = 20 * CV.MPH_TO_MS

  def update(self, CS: car.CarState, lateral_active: bool):
    self.update_counter += 1
    if self.update_counter % 6 == 0:  # ~.33 of a second at 20hz I think
      self.sm.update()
      nav_msg = self.sm['navigationd']
      if nav_msg.valid and lateral_active:
        upcoming = nav_msg.upcomingTurn
        if upcoming == 'slightLeft' and (not CS.leftBlindspot or CS.vEgo < self.turn_speed_limit):
          self.desire = log.Desire.keepLeft
        elif upcoming == 'slightRight' and (not CS.rightBlindspot or CS.vEgo < self.turn_speed_limit):
          self.desire = log.Desire.keepRight
        elif upcoming == 'left' and CS.leftBlinker and not CS.rightBlinker and not CS.leftBlindspot and CS.vEgo < self.turn_speed_limit:
          self.desire = log.Desire.turnLeft
        elif upcoming == 'right' and CS.rightBlinker and not CS.leftBlinker and not CS.rightBlindspot and CS.vEgo < self.turn_speed_limit:
          self.desire = log.Desire.turnRight
        else:
          self.desire = log.Desire.none
      else:
        self.desire = log.Desire.none

  def get_desire(self) -> log.Desire:
    return self.desire
