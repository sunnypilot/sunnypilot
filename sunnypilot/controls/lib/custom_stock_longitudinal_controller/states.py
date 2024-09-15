from abc import ABC, abstractmethod
from random import randint

from cereal import custom

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

INACTIVE_TIMER = 40
RESET_COUNT = 5
HOLD_TIME = 7
HOLD_TIME_IMPERIAL = [3, 5]
HOLD_TIME_METRIC = [0, 2]


class ButtonStateBase(ABC):
  def __init__(self, controller, car_state):
    self.controller = controller
    self.car_state = car_state
    self.button_count = 0
    self.timer = INACTIVE_TIMER
    self.hold_time = HOLD_TIME
    self.hold_time_custom = HOLD_TIME

  def __call__(self) -> int | None:
    if self.controller.is_ready:
      hold_time_offset = HOLD_TIME_METRIC if self.car_state.params_list.is_metric else HOLD_TIME_IMPERIAL
      self.hold_time = randint(self.hold_time_custom + hold_time_offset[0], self.hold_time_custom + hold_time_offset[1])
    else:
      if self.controller.is_ready_prev:
        self.controller.button_state = ButtonControlState.inactive
        return None

    return self.handle()

  @abstractmethod
  def handle(self) -> int | None:
    pass


class InactiveState(ButtonStateBase):
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

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
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

  def handle(self) -> None:
    if self.controller.target_speed > self.controller.v_cruise:
      self.controller.button_state = ButtonControlState.accelerating
    elif self.controller.target_speed < self.controller.v_cruise and self.controller.v_cruise > self.controller.v_cruise_min:
      self.controller.button_state = ButtonControlState.decelerating
    else:
      self.controller.button_state = ButtonControlState.holding
    return None


class AcceleratingState(ButtonStateBase):
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.target_speed <= self.controller.v_cruise or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.accel_button


class DeceleratingState(ButtonStateBase):
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

  def handle(self) -> int | None:
    self.button_count += 1
    if self.controller.target_speed >= self.controller.v_cruise or self.controller.v_cruise <= self.controller.v_cruise_min or self.button_count > RESET_COUNT:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.holding
      return None
    return self.controller.decel_button


class HoldingState(ButtonStateBase):
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

  def handle(self) -> None:
    self.button_count += 1
    if self.button_count > self.hold_time:
      self.button_count = 0
      self.controller.button_state = ButtonControlState.resetting
    return None


class ResettingState(ButtonStateBase):
  def __init__(self, controller, car_state):
    super().__init__(controller, car_state)

  def handle(self) -> None:
    self.controller.button_state = ButtonControlState.loading
    return None
