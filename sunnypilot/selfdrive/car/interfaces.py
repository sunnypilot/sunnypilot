from abc import ABC

from opendbc.car import structs


class CarStateBaseSP(ABC):
  def __init__(self, CP: structs.CarParams):
    self.alt_button = 0
    self.mads_enabled_toggle = True  # TODO-SP: Apply with toggle
    self.button_events: list[structs.CarState.ButtonEvent] = []
