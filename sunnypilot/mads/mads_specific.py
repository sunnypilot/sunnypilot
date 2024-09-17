from opendbc.car import structs
from openpilot.selfdrive.selfdrived.events import Events


class ModifiedAssistDrivingSystemEvents:
  def __init__(self, car_events: Event, CP: structs.CarParams):
    self.car_events = car_events
    self.CP = CP

  def update(self):
    pass
