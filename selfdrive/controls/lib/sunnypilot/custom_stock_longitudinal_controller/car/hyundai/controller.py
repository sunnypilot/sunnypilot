from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car import DT_CTRL
from openpilot.selfdrive.car.hyundai import hyundaicanfd, hyundaican
from openpilot.selfdrive.car.hyundai.values import HyundaiFlags, Buttons, CANFD_CAR, LEGACY_SAFETY_MODE_CAR
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan

ButtonType = car.CarState.ButtonEvent.Type


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, CP):
    super().__init__(car, car_controller, CP)
    self.accel_button = Buttons.RES_ACCEL
    self.decel_button = Buttons.SET_DECEL
    self.initialize_button_mapping()

    self.set_speed_buttons = (ButtonType.accelCruise, ButtonType.decelCruise)

  def get_set_point(self, is_metric: bool) -> float:
    return 30 if is_metric else int(20 * CV.MPH_TO_KPH)

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
