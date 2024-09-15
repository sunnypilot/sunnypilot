from abc import ABC, abstractmethod

from cereal import car, custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

RESET_COUNT = 5
T_INTERNAL = 7
INACTIVE_TIMER = 40


class ButtonStateBase(ABC):
  def __init__(self):
    self.button_count = 0
    self.timer = INACTIVE_TIMER

  def __call__(self, controller) -> int | None:
    if not controller.is_ready:
      self.timer = INACTIVE_TIMER
      controller.button_state = ButtonControlState.inactive

    return self.handle(controller)

  @abstractmethod
  def handle(self, controller) -> int | None:
    pass


class InactiveState(ButtonStateBase):
  def handle(self, controller) -> None:
    self.button_count = 0

    if controller.is_ready:
      if self.timer > 0:
        self.timer -= 1
      else:
        controller.button_state = ButtonControlState.loading
    return None


class LoadingState(ButtonStateBase):
  def handle(self, controller) -> None:
    if controller.target_speed > controller.v_cruise:
      controller.button_state = ButtonControlState.accelerating
    elif controller.target_speed < controller.v_cruise and controller.v_cruise > controller.v_cruise_min:
      controller.button_state = ButtonControlState.decelerating
    else:
      controller.button_state = ButtonControlState.holding
    return None


class AcceleratingState(ButtonStateBase):
  def handle(self, controller) -> int:
    self.button_count += 1
    if controller.target_speed <= controller.v_cruise or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return controller.accel_button


class DeceleratingState(ButtonStateBase):
  def handle(self, controller) -> int:
    self.button_count += 1
    if controller.target_speed >= controller.v_cruise or controller.v_cruise <= controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      controller.button_state = ButtonControlState.holding
    return controller.decel_button


class HoldingState(ButtonStateBase):
  def handle(self, controller) -> None:
    self.button_count += 1
    if self.button_count > T_INTERNAL:
      controller.button_state = ButtonControlState.resetting
    return None


class ResettingState(ButtonStateBase):
  def handle(self, controller) -> None:
    if controller.is_ready:
      controller.button_state = ButtonControlState.loading
    else:
      controller.button_state = ButtonControlState.inactive
    return None
