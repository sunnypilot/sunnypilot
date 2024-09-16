from cereal import car
from openpilot.selfdrive.car.mazda.values import Buttons
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan
from openpilot.sunnypilot.selfdrive.car.mazda.custom_stock_longitudinal_controller import helpers

ButtonType = car.CarState.ButtonEvent.Type


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = Buttons.SET_PLUS
    self.decel_button = Buttons.SET_MINUS
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0,
                           ButtonType.resumeCruise: 0, ButtonType.setCruise: 0}

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []

    if self.cruise_button is not None:
      if self.car_controller.frame % 10 == 0:
        can_sends.append(helpers.create_button_cmd(self.car_controller.packer, self.CP, self.car_controller.frame // 10, self.cruise_button))

    return can_sends
