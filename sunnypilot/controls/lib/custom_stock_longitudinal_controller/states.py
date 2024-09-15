from abc import ABC, abstractmethod

from cereal import custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

RESET_COUNT = 5
T_INTERNAL = 7
INACTIVE_TIMER = 40


class ButtonStateBase(ABC):
  def __init__(self, controller):
    self.controller = controller
    self.button_count = 0
    self.timer = INACTIVE_TIMER

  def __call__(self) -> int | None:
    if not self.controller.is_ready and self.controller.is_ready_prev:
      self.controller.button_state = ButtonControlState.inactive
      return None

    return self.handle()

  @abstractmethod
  def handle(self) -> int | None:
    pass


class InactiveState(ButtonStateBase):
  def handle(self) -> None:
    self.button_count = 0

    if not self.controller.is_ready:
      self.timer = INACTIVE_TIMER
    elif self.timer > 0:
      self.timer -= 1
    else:
      self.controller.button_state = ButtonControlState.loading
    return None


class LoadingState(ButtonStateBase):
  def handle(self) -> None:
    if self.controller.target_speed > self.controller.v_cruise:
      self.controller.button_state = ButtonControlState.accelerating
    elif self.controller.target_speed < self.controller.v_cruise and self.controller.v_cruise > self.controller.v_cruise_min:
      self.controller.button_state = ButtonControlState.decelerating
    else:
      self.controller.button_state = ButtonControlState.holding
    return None


class AcceleratingState(ButtonStateBase):
  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.target_speed <= self.controller.v_cruise or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.accel_button


class DeceleratingState(ButtonStateBase):
  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.target_speed >= self.controller.v_cruise or self.controller.v_cruise <= self.controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.decel_button


class HoldingState(ButtonStateBase):
  def handle(self) -> None:
    self.button_count += 1
    if self.button_count > T_INTERNAL:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.resetting
    return None


class ResettingState(ButtonStateBase):
  def handle(self) -> None:
    self.controller.button_state = ButtonControlState.loading
    return None
