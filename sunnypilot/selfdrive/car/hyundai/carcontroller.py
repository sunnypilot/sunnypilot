from abc import abstractmethod
from collections import namedtuple

from opendbc.car import DT_CTRL, structs
from opendbc.car.can_definitions import CanData
from opendbc.car.interfaces import CarStateBase, CarControllerBase

MadsDataSP = namedtuple("MadsDataSP",
                        ["enabled_toggle", "lat_active", "disengaging", "paused"])


class CarControllerSP(CarControllerBase):
  def __init__(self, dbc_name: str, CP: structs.CarParams):
    super().__init__(dbc_name, CP)
    self.lat_disengage_blink = 0
    self.lat_disengage_init = False
    self.prev_lat_active = False

  # display LFA "white_wheel" and LKAS "White car + lanes" when not CC.latActive
  def mads_status_update(self, CS: CarStateBase, CC: structs.CarControl) -> MadsDataSP:
    if CC.latActive:
      self.lat_disengage_init = False
    elif self.prev_lat_active:
      self.lat_disengage_init = True

    if not self.lat_disengage_init:
      self.lat_disengage_blink = self.frame

    paused = CC.madsActive and not CC.latActive
    disengaging = (self.frame - self.lat_disengage_blink) * DT_CTRL < 1.0 if self.lat_disengage_init else False

    self.prev_lat_active = CC.latActive

    return MadsDataSP(CS.mads_enabled_toggle, CC.latActive, disengaging, paused)

  @abstractmethod
  def update(self, CC: structs.CarControl, CS: CarStateBase, now_nanos: int) -> tuple[structs.CarControl.Actuators, list[CanData]]:
    pass
