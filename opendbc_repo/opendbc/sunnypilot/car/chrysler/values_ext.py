"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections import namedtuple
from enum import IntFlag

from opendbc.car import structs

ButtonType = structs.CarState.ButtonEvent.Type
Button = namedtuple('Button', ['event_type', 'can_addr', 'can_msg', 'values'])


def get_buttons(cruise_btns_msg="CRUISE_BUTTONS"):
  return [
    Button(ButtonType.accelCruise, cruise_btns_msg, "ACC_Accel", [1]),
    Button(ButtonType.decelCruise, cruise_btns_msg, "ACC_Decel", [1]),
    Button(ButtonType.cancel, cruise_btns_msg, "ACC_Cancel", [1]),
    Button(ButtonType.resumeCruise, cruise_btns_msg, "ACC_Resume", [1]),
  ]


class ChryslerSafetyFlagsSP:
  RAM_HD_ALT_BUTTONS = 1


class ChryslerFlagsSP(IntFlag):
  NO_MIN_STEERING_SPEED = 1
  RAM_HD_ALT_BUTTONS = 2
