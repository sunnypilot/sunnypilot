from abc import ABC

from opendbc.car import structs

ButtonType = structs.CarState.ButtonEvent.Type


class CarInterfaceBaseSP(ABC):
  def __init__(self, CP: structs.CarParams, CarController, CarState):
    self.mads_enabled_toggle = False
    self.mads_enabled = False

  def update_prevs(self, CS):
    CS.mads_enabled_toggle = self.mads_enabled_toggle
    CS.mads_enabled = self.mads_enabled


class CarStateBaseSP(ABC):
  def __init__(self, CP: structs.CarParams):
    self.alt_button = 0
    self.mads_enabled_toggle = False
    self.mads_enabled = False
    self.button_events: list[structs.CarState.ButtonEvent] = []
