"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import car
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.car import CRUISE_NEAREST_FUNC, CRUISE_INTERVAL_SIGN

ButtonType = car.CarState.ButtonEvent.Type


class VCruiseHelperSP:
  def __init__(self) -> None:
    self.params = Params()

    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.read_int_param("CustomAccShortPressIncrement", 1)
    self.long_increment = self.read_int_param("CustomAccLongPressIncrement", 5)

  def read_int_param(self, key: str, default: int = 0) -> int:
    try:
      return int(self.params.get(key, encoding='utf8'))
    except (ValueError, TypeError):
      return default

  def read_custom_set_speed_params(self) -> None:
    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.read_int_param("CustomAccShortPressIncrement", 1)
    self.long_increment = self.read_int_param("CustomAccLongPressIncrement", 5)

  def custom_v_cruise_kph(self, v_cruise_kph: float, v_cruise_delta: float, button_type: car.CarState.ButtonEvent.Type,
                          long_press: bool, is_metric: bool) -> float:
    """
    Adjust cruise control speed based on button inputs with customizable increments.
    Parameters:
    - button_type: Type of button pressed (affects direction and rounding)
    - long_press: Whether the button is being held down
    - is_metric: Check if the system is using metric units
    """

    # Apply user-specified multipliers to the base increment
    short_increment = self.short_increment if 1 <= self.short_increment <= 10 else 1
    long_increment = self.long_increment if 1 <= self.long_increment <= 10 else 10 if is_metric else 5

    # Determine which increment to use based on the press type
    actual_increment = long_increment if long_press else short_increment
    v_cruise_delta = v_cruise_delta * actual_increment

    # Check if we need to align to interval boundaries
    if actual_increment in (5, 10) and v_cruise_kph % v_cruise_delta != 0:
      v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](v_cruise_kph / v_cruise_delta) * v_cruise_delta
    else:
      v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]  # +1 or -1 based on the button type

    return v_cruise_kph
