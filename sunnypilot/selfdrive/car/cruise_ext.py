"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from cereal import car
from openpilot.common.constants import CV
from openpilot.common.params import Params

ButtonType = car.CarState.ButtonEvent.Type

V_CRUISE_MIN = 8

HYUNDAI_V_CRUISE_MIN = {
  True: 30,
  False: int(20 * CV.MPH_TO_KPH),
}


class VCruiseHelperSP:
  def __init__(self, CP, CP_SP) -> None:
    self.CP = CP
    self.CP_SP = CP_SP
    self.params = Params()
    self.is_metric_prev = False
    self.v_cruise_min = 0

    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.params.get("CustomAccShortPressIncrement", return_default=True)
    self.long_increment = self.params.get("CustomAccLongPressIncrement", return_default=True)

  def read_custom_set_speed_params(self) -> None:
    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.params.get("CustomAccShortPressIncrement", return_default=True)
    self.long_increment = self.params.get("CustomAccLongPressIncrement", return_default=True)

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

  def get_minimum_set_speed(self, is_metric: bool):
    if self.CP_SP.pcmCruiseSpeed:
      self.v_cruise_min = V_CRUISE_MIN
      return

    if is_metric != self.is_metric_prev:
      if self.CP.brand == "hyundai":
        self.v_cruise_min = HYUNDAI_V_CRUISE_MIN[is_metric]
    self.is_metric_prev = is_metric
