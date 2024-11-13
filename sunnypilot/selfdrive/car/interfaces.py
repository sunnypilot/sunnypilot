from abc import ABC

from opendbc.car import structs

from openpilot.sunnypilot.mads.mads import MadsParams


class CarStateBaseSP(ABC):
  def __init__(self, CP: structs.CarParams):
    self.alt_button = 0
    self.mads_enabled_toggle = MadsParams().read_enabled_param()
