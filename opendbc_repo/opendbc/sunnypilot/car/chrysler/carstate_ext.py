
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import StrEnum

from opendbc.car import Bus, structs
from opendbc.can.parser import CANParser
from opendbc.car.chrysler.values import CUSW_CARS, RAM_CARS, RAM_HD
from opendbc.sunnypilot.car.chrysler.brake_hold import (
  ACC_ACCEL_THRESHOLD,
  ACC_DECEL_THRESHOLD,
  BrakeHold,
)
from opendbc.sunnypilot.car.chrysler.values_ext import BUTTONS, ChryslerFlagsSP


class CarStateExt:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.button_events = []
    self.button_states = {button.event_type: False for button in BUTTONS}

    # Brake hold state (Jeep only; constructed unconditionally, gated by flag internally).
    self.brake_hold = BrakeHold(CP, CP_SP)
    self.acc_decelerating = False
    self.acc_accelerating = False

  def update(self, ret: structs.CarState, ret_sp: structs.CarStateSP, can_parsers: dict[StrEnum, CANParser]):
    cp = can_parsers[Bus.pt]
    cp_cam = can_parsers[Bus.cam]

    button_events = []
    for button in BUTTONS:
      state = (cp.vl[button.can_addr][button.can_msg] in button.values)
      if self.button_states[button.event_type] != state:
        event = structs.CarState.ButtonEvent.new_message()
        event.type = button.event_type
        event.pressed = state
        button_events.append(event)
      self.button_states[button.event_type] = state
    self.button_events = button_events

    if self.CP.carFingerprint in RAM_HD:
      ret.steeringAngleDeg = cp.vl["STEERING"]["STEERING_ANGLE"]

    # Brake hold: only meaningful on non-CUSW, non-RAM platforms where DAS_3
    # is on bus 0 and we've gated by JEEPS in the interface layer.
    if self.CP_SP.flags & ChryslerFlagsSP.BRAKE_HOLD and self.CP.carFingerprint not in (CUSW_CARS | RAM_CARS):
      cp_cruise = cp_cam if self.CP.carFingerprint in RAM_CARS else cp
      acc_decel = cp_cruise.vl["DAS_3"]["ACC_DECEL"]
      das_3_counter = int(cp_cruise.vl["DAS_3"]["COUNTER"])

      self.acc_decelerating = acc_decel < ACC_DECEL_THRESHOLD
      self.acc_accelerating = acc_decel > ACC_ACCEL_THRESHOLD

      active = self.brake_hold.update_state(ret, self.acc_decelerating, self.acc_accelerating,
                                             das_3_counter, acc_decel)
      ret.brakeHoldActive = active
      if active:
        ret.cruiseState.enabled = True
        ret.cruiseState.standstill = True
    else:
      ret.brakeHoldActive = False
