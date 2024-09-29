from collections import namedtuple

from opendbc.car import DT_CTRL, structs
from opendbc.car.interfaces import CarStateBase

MadsDataSP = namedtuple("MadsDataSP",
                        ["enabled_toggle", "lat_active", "disengaging", "lfa_icon"])


class CarControllerSP:
  def __init__(self, car_controller):
    self.CC = car_controller

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
      self.lat_disengage_blink = self.CC.frame

    paused = CS.mads_enabled and not CC.latActive
    disengaging = (self.CC.frame - self.lat_disengage_blink) * DT_CTRL < 1.0 if self.lat_disengage_init else False

    if CS.mads_enabled_toggle:
      lfa_icon = 2 if CC.latActive else 3 if disengaging else 1 if paused else 0
    else:
      lfa_icon = 2 if CC.enabled else 0

    self.prev_lat_active = CC.latActive

    return MadsDataSP(CS.mads_enabled_toggle, CC.latActive, disengaging, lfa_icon)
