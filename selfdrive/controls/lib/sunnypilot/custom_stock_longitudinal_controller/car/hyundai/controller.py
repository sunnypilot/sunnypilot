from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car import DT_CTRL
from openpilot.selfdrive.car.hyundai import hyundaicanfd, hyundaican
from openpilot.selfdrive.car.hyundai.values import HyundaiFlags, Buttons, CANFD_CAR, LEGACY_SAFETY_MODE_CAR
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan

ButtonType = car.CarState.ButtonEvent.Type
SET_SPEED_BUTTONS = (ButtonType.accelCruise, ButtonType.decelCruise)

HYUNDAI_BUTTON_MAPPINGS = {'type_1': Buttons.RES_ACCEL, 'type_2': Buttons.SET_DECEL}
HYUNDAI_V_CRUISE_MIN = {True: 30, False: int(20 * CV.MPH_TO_KPH)}


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car_controller, CP):
    super().__init__(car_controller, CP)

  def get_set_point(self, is_metric: bool) -> float:
    return HYUNDAI_V_CRUISE_MIN[is_metric]

  def get_set_speed_buttons(self, CS: car.CarState) -> bool:
    return any(be.type in SET_SPEED_BUTTONS for be in CS.out.buttonEvents)

  def get_button_mappings(self) -> dict[str, int]:
    return HYUNDAI_BUTTON_MAPPINGS

  def create_can_mock_button_messages(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    can_sends = []
    if not (CC.cruiseControl.cancel or CC.cruiseControl.resume) and CS.out.cruiseState.enabled:
      self.cruise_button = self.get_cruise_buttons(CS, CC.vCruise)
      if self.cruise_button is not None:
        if self.CP.carFingerprint in LEGACY_SAFETY_MODE_CAR:
          send_freq = 1
          if not (self.v_tsc_state != 0 or self.m_tsc_state > 1) and abs(self.target_speed - self.v_set_dis) <= 2:
            send_freq = 5
          # send resume at a max freq of 10Hz
          if (self.car_controller.frame - self.car_controller.last_button_frame) * DT_CTRL > 0.1 * send_freq:
            # send 25 messages at a time to increases the likelihood of cruise buttons being accepted
            can_sends.extend([hyundaican.create_clu11(self.car_controller.packer, self.car_controller.frame, CS.clu11, self.cruise_button, self.CP)] * 25)
            if (self.car_controller.frame - self.car_controller.last_button_frame) * DT_CTRL >= 0.15 * send_freq:
              self.car_controller.last_button_frame = self.car_controller.frame
        elif self.car_controller.frame % 2 == 0:
          can_sends.extend([hyundaican.create_clu11(self.car_controller.packer, (self.car_controller.frame // 2) + 1, CS.clu11, self.cruise_button, self.CP)] * 25)

    return can_sends

  def create_canfd_mock_button_messages(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    can_sends = []
    if not (CC.cruiseControl.cancel or CC.cruiseControl.resume) and CS.out.cruiseState.enabled:
      if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
        # TODO: resume for alt button cars
        pass
      else:
        self.cruise_button = self.get_cruise_buttons(CS, CC.vCruise)
        if self.cruise_button is not None:
          if self.car_controller.frame % 2 == 0:
            can_sends.append(hyundaicanfd.create_buttons(self.car_controller.packer, self.CP, self.car_controller.CAN, ((self.car_controller.frame // 2) + 1) % 0x10, self.cruise_button))

    return can_sends

  def create_mock_button_messages(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    can_sends = []
    if self.CP.carFingerprint in CANFD_CAR:
      can_sends.extend(self.create_canfd_mock_button_messages(CS, CC))
    else:
      can_sends.extend(self.create_can_mock_button_messages(CS, CC))

    return can_sends
