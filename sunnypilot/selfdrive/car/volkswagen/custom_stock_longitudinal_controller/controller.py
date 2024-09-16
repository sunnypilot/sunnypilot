from cereal import car, custom
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.controllers import CustomStockLongitudinalControllerBase, \
  SendCan

ButtonType = car.CarState.ButtonEvent.Type
ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState
# TODO-SP: Handle this better in the base class
ACCEL_BUTTON = 1
DECEL_BUTTON = 2
RESUME_CRUISE = 3
SET_CRUISE = 4

ACC_TYPE_BUTTONS = {
  0: {1: ACCEL_BUTTON, 2: DECEL_BUTTON},  # accel, decel
  1: {1: RESUME_CRUISE, 2: SET_CRUISE}    # resume, set
}


class CustomStockLongitudinalController(CustomStockLongitudinalControllerBase):
  def __init__(self, car, car_controller, car_state, CP):
    super().__init__(car, car_controller, car_state, CP)
    self.accel_button = ACCEL_BUTTON
    self.decel_button = DECEL_BUTTON
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0,
                           ButtonType.resumeCruise: 0, ButtonType.setCruise: 0}

    self.last_v_cruise_cluster = 0
    self.last_cruise_button = False

    self.acc_type = -1
    self.button_frame = 0

    self.initial_v_target = 0
    self.initial_v_cruise_cluster = 0

  def update_checks(self) -> None:
    if self.button_state > ButtonControlState.inactive:
      self.button_frame += 1
      if self.button_frame == 1:
        self.initial_v_target = self.v_target
        self.initial_v_cruise_cluster = self.v_cruise_cluster

      self.set_acc_type()
    else:
      self.button_frame = 0
      self.initial_v_target = 0
      self.initial_v_cruise_cluster = 0

  def set_acc_type(self):
    current_v_cruise_diff = abs(self.v_target - self.v_cruise_cluster)
    initial_v_cruise_diff = abs(self.initial_v_target - self.initial_v_cruise_cluster)

    if self.last_v_cruise_cluster != self.v_cruise_cluster and current_v_cruise_diff != initial_v_cruise_diff:
      if self.acc_type == -1:
        v_cruise_diff = abs(self.v_cruise_cluster - self.last_v_cruise_cluster)

        if v_cruise_diff >= 10 and self.last_cruise_button in (ACCEL_BUTTON, DECEL_BUTTON):
          self.acc_type = 1
        else:
          self.acc_type = 0

      if self.cruise_button is not None:
        self.cruise_button = ACC_TYPE_BUTTONS.get(self.acc_type, {}).get(self.cruise_button, self.cruise_button)

  def create_mock_button_messages(self) -> list[SendCan]:
    can_sends = []

    self.update_checks()

    if self.cruise_button is not None:
      if self.car_state.gra_stock_values["COUNTER"] != self.car_controller.gra_acc_counter_last:
        can_sends.append(self.car_controller.CCS.create_acc_buttons_control(self.car_controller.packer_pt, self.car_controller.ext_bus, self.car_state.gra_stock_values, buttons=self.cruise_button))

    self.last_cruise_button = self.cruise_button
    self.last_v_cruise_cluster = self.v_cruise_cluster

    return can_sends
