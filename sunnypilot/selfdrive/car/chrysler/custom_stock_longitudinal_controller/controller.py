from cereal import car
from openpilot.selfdrive.car.chrysler.values import RAM_CARS
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan
from openpilot.sunnypilot.selfdrive.car.chrysler.custom_stock_longitudinal_controller import helpers

ButtonType = car.CarState.ButtonEvent.Type
# TODO-SP: Handle this better in the base class
ACCEL_BUTTON = 1
DECEL_BUTTON = 2


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = ACCEL_BUTTON
    self.decel_button = DECEL_BUTTON
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0, ButtonType.resumeCruise: 0}

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []
    ram_cars = self.CP.carFingerprint in RAM_CARS
    das_bus = 2 if self.CP.carFingerprint in RAM_CARS else 0
    button_counter_offset = [1, 1, 0, None][self.car_controller.frame % 4]

    if self.cruise_button is not None:
      if ram_cars:
        can_sends.append(helpers.create_cruise_buttons(self.car_controller.packer, self.car_state.button_counter, das_bus, self.cruise_button))
      elif button_counter_offset is not None:
        can_sends.append(helpers.create_cruise_buttons(self.car_controller.packer, self.car_state.button_counter + button_counter_offset, das_bus, self.cruise_button))

    return can_sends
