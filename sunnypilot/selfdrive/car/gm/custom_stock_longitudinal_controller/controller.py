from cereal import car
from openpilot.selfdrive.car.gm import gmcan
from openpilot.selfdrive.car.gm.values import CanBus, CruiseButtons
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan

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
      if self.car_controller.frame % 12 < 6:  # thanks to mochi86420 for the magic numbers
        can_sends.extend([gmcan.create_buttons(self.car_controller.packer_pt, CanBus.CAMERA, (self.car_state.buttons_counter + 2) % 4, self.cruise_button)] * 3)

    return can_sends
