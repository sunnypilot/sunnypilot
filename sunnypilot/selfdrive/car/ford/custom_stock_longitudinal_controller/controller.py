from cereal import car
from openpilot.selfdrive.car.ford.values import CarControllerParams
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan
from openpilot.sunnypilot.selfdrive.car.ford.custom_stock_longitudinal_controller import fordcan

ButtonType = car.CarState.ButtonEvent.Type
# TODO-SP: Handle this better in the base class
ACCEL_BUTTON = 1
DECEL_BUTTON = 2


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = ACCEL_BUTTON
    self.decel_button = DECEL_BUTTON
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0, ButtonType.gapAdjustCruise: 0,
                           ButtonType.resumeCruise: 0, ButtonType.setCruise: 0}

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []

    if self.cruise_button is not None and (self.car_controller.frame % CarControllerParams.BUTTONS_STEP) == 0:
      can_sends.append(fordcan.create_button_msg(self.car_controller.packer, self.car_controller.CAN.camera, self.car_state.buttons_stock_values, buttons=self.cruise_button))
      can_sends.append(fordcan.create_button_msg(self.car_controller.packer, self.car_controller.CAN.main, self.car_state.buttons_stock_values, buttons=self.cruise_button))

    return can_sends
