"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from opendbc.car.nissan.values import CAR

LEAF_CRUISE_THROTTLE_SIGNALS = [
  "GAS_PEDAL",
  "GAS_PEDAL_INVERTED",
  "unsure2",
  "CRUISE_AVAILABLE",
  "unsure1",
  "PROPILOT_BUTTON",
  "CANCEL_BUTTON",
  "FOLLOW_DISTANCE_BUTTON",
  "SET_BUTTON",
  "RES_BUTTON",
  "NO_BUTTON_PRESSED",
  "unsure3",
  "COUNTER",
  "USER_BRAKE_PRESSED",
  "unsure5",
  "unsure6",
  "unsure7",
]

XTRAIL_CRUISE_THROTTLE_SIGNALS = [
  "COUNTER",
  "PROPILOT_BUTTON",
  "CANCEL_BUTTON",
  "GAS_PEDAL_INVERTED",
  "SET_BUTTON",
  "RES_BUTTON",
  "FOLLOW_DISTANCE_BUTTON",
  "NO_BUTTON_PRESSED",
  "GAS_PEDAL",
  "USER_BRAKE_PRESSED",
  "USER_BRAKE_PRESSED_INVERTED",
  "NEW_SIGNAL_2",
  "GAS_PRESSED_INVERTED",
  "unsure1",
  "unsure2",
  "unsure3",
]


def create_cruise_throttle_msg(packer, car_fingerprint, cruise_throttle_msg, frame, button_name=None):
  signals = LEAF_CRUISE_THROTTLE_SIGNALS if car_fingerprint in (CAR.NISSAN_LEAF, CAR.NISSAN_LEAF_IC) else XTRAIL_CRUISE_THROTTLE_SIGNALS
  values = {s: cruise_throttle_msg[s] for s in signals}

  can_bus = 1 if car_fingerprint == CAR.NISSAN_ALTIMA else 2

  values["COUNTER"] = (frame // 2) % 4

  if (button_name is not None) and (not values["CANCEL_BUTTON"]):
    values["NO_BUTTON_PRESSED"] = 0
    values["PROPILOT_BUTTON"] = 0
    values["SET_BUTTON"] = 0
    values["RES_BUTTON"] = 0
    values["FOLLOW_DISTANCE_BUTTON"] = 0
    values["CANCEL_BUTTON"] = 0
    values[button_name] = 1

  return packer.make_can_msg("CRUISE_THROTTLE", can_bus, values)
