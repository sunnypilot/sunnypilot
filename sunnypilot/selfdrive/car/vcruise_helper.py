"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from cereal import car
from opendbc.car import structs
from openpilot.selfdrive.car.cruise import VCruiseHelper, IMPERIAL_INCREMENT, CRUISE_LONG_PRESS, CRUISE_NEAREST_FUNC, CV, \
                                            V_CRUISE_MIN, V_CRUISE_MAX, CRUISE_INTERVAL_SIGN

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type


class VCruiseHelperSP(VCruiseHelper):

  def __init__(self, CP: structs.CarParams) -> None:
    super().__init__(CP)
    self.custom_acc_enabled = False
    self.short_increment = 0
    self.long_increment = 0

  def update_v_cruise_sp(self, CS, enabled, is_metric, custom_acc: tuple[bool, int, int]) -> None:
    super().update_v_cruise(CS, enabled, is_metric)
    self.custom_acc_enabled = custom_acc[0]
    self.short_increment = custom_acc[1]
    self.long_increment = custom_acc[2]

  def _update_v_cruise_non_pcm(self, CS: car.CarState, enabled: bool, is_metric: bool) -> None:
    if not enabled:
      return

    long_press = False
    button_type = None

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers and not b.pressed:
        if self.button_timers[b.type.raw] > CRUISE_LONG_PRESS:
          return  # end long press
        button_type = b.type.raw
        break
    else:
      for k, timer in self.button_timers.items():
        if timer and timer % CRUISE_LONG_PRESS == 0:
          button_type = k
          long_press = True
          break

    if button_type is None:
      return

    # Don't adjust speed when pressing resume to exit standstill
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Don't adjust speed if we've enabled since the button was depressed (some ports enable on rising edge)
    if not self.button_change_states[button_type]["enabled"]:
      return

    self.v_cruise_kph = self.adjust_cruise_speed(button_type, long_press, is_metric)

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), V_CRUISE_MIN, V_CRUISE_MAX)

  def adjust_cruise_speed(self, button_type: car.CarState.ButtonEvent.Type, long_press: bool, is_metric: bool) -> float:
    """
    Adjust cruise control speed based on button inputs with customizable increments.
    Parameters:
    - button_type: Type of button pressed (affects direction and rounding)
    - long_press: Whether button is being held down
    - is_metric: Check if the system is using metric units
    """
    # Base increment value based on unit system
    base_increment = 1. if is_metric else IMPERIAL_INCREMENT

    # Apply user-specified multipliers to the base increment if custom enabled
    short_increment = self.short_increment if self.custom_acc_enabled and 1 <= self.short_increment <= 10 else 1
    long_increment = self.long_increment if self.custom_acc_enabled and 1 <= self.long_increment <= 10 else 10 if is_metric else 5

    # Determine which increment to use based on press type
    adjusted_delta = long_increment if long_press else short_increment
    v_cruise = self.v_cruise_kph / base_increment

    # Check if we need to align to interval boundaries
    if adjusted_delta in [5, 10] and v_cruise % adjusted_delta != 0:
      rounded_value = CRUISE_NEAREST_FUNC[button_type](v_cruise / adjusted_delta)
      v_cruise = rounded_value * adjusted_delta
    else:
      direction = CRUISE_INTERVAL_SIGN[button_type]  # +1 or -1 based on button type
      v_cruise += adjusted_delta * direction

    self.v_cruise_kph = v_cruise * base_increment
    return float(self.v_cruise_kph)
