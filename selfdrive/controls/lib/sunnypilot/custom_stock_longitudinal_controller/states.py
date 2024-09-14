from abc import ABC, abstractmethod

from cereal import car, custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

RESET_COUNT = 5
T_INTERNAL = 7


class ButtonStateBase(ABC):
  def __init__(self):
    self.button_count = 0

  def __call__(self, controller, CS: car.CarState) -> int | None:
    return self.handle(controller, CS)

  @abstractmethod
  def handle(self, controller, CS: car.CarState) -> int | None:
    pass


class InactiveState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> None:
    self.button_count = 0

    if controller.target_speed > controller.v_cruise or \
        controller.target_speed < controller.v_cruise and controller.v_cruise > controller.v_cruise_min:
      controller.button_state = ButtonControlState.loading
    return None


class LoadingState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> None:
    if not controller.is_active or controller.get_set_speed_buttons(CS):
      controller.timer = 40
    elif controller.timer > 0:
      controller.timer -= 1
    else:
      if controller.target_speed > controller.v_cruise:
        controller.button_state = ButtonControlState.accelerating
      elif controller.target_speed < controller.v_cruise and controller.v_cruise > controller.v_cruise_min:
        controller.button_state = ButtonControlState.decelerating
      else:
        controller.button_state = ButtonControlState.holding
    return None


class AcceleratingState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> int:
    self.button_count += 1
    if controller.target_speed <= controller.v_cruise or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return controller.accel_button


class DeceleratingState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> int:
    self.button_count += 1
    if controller.target_speed >= controller.v_cruise or controller.v_cruise <= controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return controller.decel_button


class HoldingState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> None:
    self.button_count += 1
    if self.button_count > T_INTERNAL:
      controller.button_state = ButtonControlState.resetting
    return None


class ResettingState(ButtonStateBase):
  def handle(self, controller, CS: car.CarState) -> None:
    controller.button_state = ButtonControlState.inactive
    return None
