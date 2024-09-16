from abc import ABC, abstractmethod
from random import randint

from cereal import custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

INACTIVE_TIMER = 40
RESET_COUNT = 5
HOLD_TIME = 7


class ButtonStateBase(ABC):
  def __init__(self, controller):
    self.controller = controller
    self.button_count = 0
    self.timer = INACTIVE_TIMER

  def __call__(self) -> int | None:
    if self.controller.is_ready:
      # TODO-SP: Validate different hold time intervals for different platforms to prevent temporary cruise fault
      pass
    else:
      if self.controller.is_ready_prev:
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
    if self.controller.v_target > self.controller.v_cruise_cluster:
      self.controller.button_state = ButtonControlState.accelerating
    elif self.controller.v_target < self.controller.v_cruise_cluster and self.controller.v_cruise_cluster > self.controller.v_cruise_min:
      self.controller.button_state = ButtonControlState.decelerating
    else:
      self.controller.button_state = ButtonControlState.holding
    return None


class AcceleratingState(ButtonStateBase):
  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.v_target <= self.controller.v_cruise_cluster or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.accel_button


class DeceleratingState(ButtonStateBase):
  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.v_target >= self.controller.v_cruise_cluster or self.controller.v_cruise_cluster <= self.controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.decel_button


class HoldingState(ButtonStateBase):
  def handle(self) -> None:
    self.button_count += 1
    if self.button_count > HOLD_TIME:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.loading
    return None
