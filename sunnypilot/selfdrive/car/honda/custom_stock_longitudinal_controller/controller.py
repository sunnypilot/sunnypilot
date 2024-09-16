from cereal import car
from openpilot.selfdrive.car.honda import hondacan
from openpilot.selfdrive.car.honda.values import CruiseButtons
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan
from openpilot.sunnypilot.selfdrive.car.honda.custom_stock_longitudinal_controller import helpers

ButtonType = car.CarState.ButtonEvent.Type


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = CruiseButtons.RES_ACCEL
    self.decel_button = CruiseButtons.DECEL_SET
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0,
                           ButtonType.altButton3: 0, ButtonType.cancel: 0}

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []

    if self.cruise_button is not None:
      can_sends.append(hondacan.spam_buttons_command(self.car_controller.packer, self.car_controller.CAN, self.cruise_button, self.CP.carFingerprint))

    return can_sends
