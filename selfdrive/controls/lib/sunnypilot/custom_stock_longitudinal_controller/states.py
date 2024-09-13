from abc import ABC, abstractmethod

from cereal import custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

RESET_COUNT = 5
T_INTERNAL = 7


class ButtonState(ABC):
  def __init__(self):
    self.button_count = 0

  @abstractmethod
  def handle(self, controller) -> int | None:
    pass


class InactiveState(ButtonState):
  def handle(self, controller) -> None:
    self.button_count = 0

    if controller.target_speed > controller.v_set_dis:
      controller.button_state = ButtonControlState.accelerating
    elif controller.target_speed < controller.v_set_dis and controller.v_set_dis > controller.v_cruise_min:
      controller.button_state = ButtonControlState.decelerating
    return None


class AcceleratingState(ButtonState):
  def handle(self, controller) -> int:
    cruise_button = controller.button_mappings['accelerating']
    self.button_count += 1
    if controller.target_speed <= controller.v_set_dis or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return cruise_button


class DeceleratingState(ButtonState):
  def handle(self, controller) -> int:
    cruise_button = controller.button_mappings['decelerating']
    self.button_count += 1
    if controller.target_speed >= controller.v_set_dis or controller.v_set_dis <= controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return cruise_button


class HoldingState(ButtonState):
  def handle(self, controller) -> None:
    self.button_count += 1
    if self.button_count > T_INTERNAL:
      controller.button_state = ButtonControlState.resetting
    return None


class ResettingState(ButtonState):
  def handle(self, controller) -> None:
    controller.button_state = ButtonControlState.inactive
    return None
