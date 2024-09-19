from random import choices

from cereal import car
from openpilot.common.numpy_fast import interp
from openpilot.selfdrive.car.hyundai import hyundaicanfd
from openpilot.selfdrive.car.hyundai.values import HyundaiFlags, Buttons, CANFD_CAR
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan
from openpilot.sunnypilot.selfdrive.car.hyundai.custom_stock_longitudinal_controller import helpers

ButtonType = car.CarState.ButtonEvent.Type

BUTTON_COPIES = 2
BUTTON_COPIES_TIME = 7
BUTTON_COPIES_TIME_IMPERIAL = [BUTTON_COPIES_TIME + 3, 70]
BUTTON_COPIES_TIME_METRIC = [BUTTON_COPIES_TIME, 40]
POPULATION = [0, 1]
WEIGHTS = [0.51, 0.49]


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = Buttons.RES_ACCEL
    self.decel_button = Buttons.SET_DECEL
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0, ButtonType.gapAdjustCruise: 0}

  def create_can_mock_button_messages(self) -> list[SendCan]:
    can_sends = []
    if self.cruise_button is not None:
      copies_xp = BUTTON_COPIES_TIME_METRIC if self.car_state.params_list.is_metric else BUTTON_COPIES_TIME_IMPERIAL
      copies = int(interp(BUTTON_COPIES_TIME, copies_xp, [1, BUTTON_COPIES]))
      can_sends.extend([helpers.create_clu11(self.car_controller.packer, self.car_state.clu11, self.cruise_button, self.CP)] * copies)

    return can_sends

  def create_canfd_mock_button_messages(self) -> list[SendCan]:
    can_sends = []
    if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
      # TODO: resume for alt button cars
      pass
    else:
      if self.cruise_button is not None:
        for _ in range(BUTTON_COPIES):
          can_sends.append(hyundaicanfd.create_buttons(self.car_controller.packer, self.CP, self.car_controller.CAN,
                                                       self.car_state.buttons_counter + choices(POPULATION, WEIGHTS)[0],
                                                       self.cruise_button))

    return can_sends

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []
    if self.CP.carFingerprint in CANFD_CAR:
      can_sends.extend(self.create_canfd_mock_button_messages())
    else:
      can_sends.extend(self.create_can_mock_button_messages())

    return can_sends
