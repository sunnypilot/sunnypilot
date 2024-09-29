from abc import ABC

from opendbc.car import structs

ButtonType = structs.CarState.ButtonEvent.Type


class CarInterfaceBaseSP(ABC):
  def __init__(self, CP: structs.CarParams, CarController, CarState):
    self.CP = CP

    self.CS: CarStateBaseSP = CarState(CP)
    self.cp = self.CS.get_can_parser(CP)
    self.cp_cam = self.CS.get_cam_can_parser(CP)
    self.cp_adas = self.CS.get_adas_can_parser(CP)
    self.cp_body = self.CS.get_body_can_parser(CP)
    self.cp_loopback = self.CS.get_loopback_can_parser(CP)
    self.can_parsers = (self.cp, self.cp_cam, self.cp_adas, self.cp_body, self.cp_loopback)

    dbc_name = "" if self.cp is None else self.cp.dbc_name
    self.CC: CarControllerBaseSP = CarController(dbc_name, CP)

    self.mads_enabled_toggle = False
    self.mads_enabled = False

  def update_prevs(self):
    self.CS.mads_enabled_toggle = self.mads_enabled_toggle
    self.CS.mads_enabled = self.mads_enabled


class CarStateBaseSP(ABC):
  def __init__(self, CP: structs.CarParams):
    self.CP = CP

    self.alt_button = 0
    self.mads_enabled_toggle = False
    self.mads_enabled = False
    self.button_events: list[structs.CarState.ButtonEvent] = []

  @staticmethod
  def get_can_parser(CP):
    return None

  @staticmethod
  def get_cam_can_parser(CP):
    return None

  @staticmethod
  def get_adas_can_parser(CP):
    return None

  @staticmethod
  def get_body_can_parser(CP):
    return None

  @staticmethod
  def get_loopback_can_parser(CP):
    return None


class CarControllerBaseSP(ABC):
  def __init__(self, dbc_name: str, CP: structs.CarParams):
    self.CP = CP
    self.frame = 0
