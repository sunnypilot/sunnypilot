"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from cereal import car
from openpilot.common.params import Params

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

  def update_v_cruise_delta(self, long_press: bool, v_cruise_delta: float) -> tuple[bool, float]:
    if not self.custom_acc_enabled:
      v_cruise_delta = v_cruise_delta * (5 if long_press else 1)
      return long_press, v_cruise_delta

    # Apply user-specified multipliers to the base increment
    short_increment = np.clip(self.short_increment, 1, 10)
    long_increment = np.clip(self.long_increment, 1, 10)

    actual_increment = long_increment if long_press else short_increment
    round_to_nearest = actual_increment in (5, 10)
    v_cruise_delta = v_cruise_delta * actual_increment

    return round_to_nearest, v_cruise_delta
