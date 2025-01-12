"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log
from opendbc.car import structs

from openpilot.selfdrive.selfdrived.events import Events

EventName = log.OnroadEvent.EventName


class CarSpecificEventsSP:
  def __init__(self, CP: structs.CarParams, params):
    self.CP = CP
    self.params = params

    self.hyundai_radar_points = self.params.get_bool("HyundaiRadarPoints")
    self.hyundai_radar_points_confirmed = self.params.get_bool("HyundaiRadarPointsConfirmed")

  def update(self):
    events = Events()
    if self.CP.carName == 'hyundai':
      if self.hyundai_radar_points and not self.hyundai_radar_points_confirmed:
        events.add(EventName.hyundaiRadarTracksConfirmed)

    return events
