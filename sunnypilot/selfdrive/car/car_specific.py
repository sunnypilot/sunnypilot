from cereal import car, log
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
