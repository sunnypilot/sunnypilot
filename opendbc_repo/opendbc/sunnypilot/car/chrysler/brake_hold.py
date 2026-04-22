"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Jeep Brake Hold
---------------
Jeeps cancel ACC after ~3s at standstill. This module detects when ACC
is decelerating to a stop and then asserts a brake request via DAS_3 to
keep the vehicle stationary until either:
  - the lead vehicle departs (openpilot re-engages ACC normally), or
  - the driver intervenes (gas / brake / cancel / gear change).

Approach mirrors jvePilot's implementation:
  - Activate: ACC active + decelerating (ACC_DECEL < -0.5 m/s^2) + standstill
  - Track: minimum observed ACC_DECEL while ACC active (brake_hold_decel)
  - Emit: DAS_3 @ 50 Hz with ACC_ACTIVE=1 + the tracked decel + ACC_BRK_PREP=1
  - Deactivate: gas / brake / cancel / gear out of Drive / vehicle moves
"""

from opendbc.car import structs
from opendbc.car.can_definitions import CanData
from opendbc.car.chrysler.values import RAM_CARS
from opendbc.sunnypilot.car.chrysler.values_ext import ChryslerFlagsSP

GearShifter = structs.CarState.GearShifter

# DAS_3 is normally emitted by the car's DASM at 50 Hz.
# We match that cadence when asserting brake hold.
BRAKE_HOLD_STEP = 2  # 50 Hz at DT_CTRL=0.01

# Thresholds for decel detection (m/s^2)
ACC_DECEL_THRESHOLD = -0.5
ACC_ACCEL_THRESHOLD = 0.5

# Minimum decel to assert while holding. jvePilot initializes to -2.0 m/s^2
# and tracks the minimum (most-negative) ACC_DECEL seen during the approach,
# which becomes the hold pressure. This avoids the brake release that would
# happen if we used 0 or a small value.
DEFAULT_BRAKE_HOLD_DECEL = -2.0


class BrakeHold:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.enabled_by_param = bool(CP_SP.flags & ChryslerFlagsSP.BRAKE_HOLD)

    # State
    self.active = False
    self.brake_hold_decel = DEFAULT_BRAKE_HOLD_DECEL
    self.last_das_3_counter = 0
    self.last_sent_das_3_counter = -1

  def update_state(self, CS, acc_decelerating: bool, acc_accelerating: bool,
                   das_3_counter: int, das_3_acc_decel: float) -> bool:
    """
    Update the brake hold state machine. Called from CarStateExt.update()
    so the state is stable before any consumers (CarController, selfdrived)
    read it. Returns the current active flag.
    """
    self.last_das_3_counter = das_3_counter

    if not self.enabled_by_param:
      self.active = False
      self.brake_hold_decel = DEFAULT_BRAKE_HOLD_DECEL
      return False

    standstill = CS.standstill
    in_drive = CS.gearShifter == GearShifter.drive
    acc_active = CS.cruiseState.enabled
    acc_available = CS.cruiseState.available
    driver_override = CS.gasPressed or CS.brakePressed

    # Track the minimum (most-negative) ACC decel observed while ACC is active.
    # This gives us the brake pressure the car was already holding when it
    # reached a stop; we replay that same pressure.
    if acc_active and das_3_acc_decel < self.brake_hold_decel:
      self.brake_hold_decel = das_3_acc_decel

    if self.active:
      # Deactivation conditions (match jvePilot):
      #  - driver touches pedals
      #  - gear leaves Drive
      #  - vehicle starts moving
      #  - cruise main turned off
      #  - ACC is trying to accelerate (lead departed, normal ACC takes over)
      if driver_override or not in_drive or not standstill or not acc_available or acc_accelerating:
        self.active = False
        self.brake_hold_decel = DEFAULT_BRAKE_HOLD_DECEL
    else:
      # Activation: ACC active, not accelerating, at standstill, in Drive, no driver input.
      # The strict decel requirement is removed since the PID can taper off request right at 0mph.
      if acc_active and not acc_accelerating and standstill and in_drive and not driver_override:
        self.active = True

    return self.active

  def send(self, packer, frame: int) -> list[CanData]:
    """
    Emit the DAS_3 brake hold message reactively on upstream counter increment.
    RAM has DAS_3 on bus 2, but we gate BRAKE_HOLD to JEEPS only so bus 0 is
    correct. The RAM_CARS check is defensive in case JEEPS is expanded later.
    """
    if not self.active:
      return []

    # Reactive transmission: only transmit our offset message immediately after
    # receiving a new upstream DAS_3 message to perfectly interleave and prevent
    # CAN collisions with the car's 50Hz DASM broadcasts.
    if self.last_das_3_counter == self.last_sent_das_3_counter:
      return []

    self.last_sent_das_3_counter = self.last_das_3_counter

    das_bus = 2 if self.CP.carFingerprint in RAM_CARS else 0

    # jvePilot sends DAS_3 with counter offset 2 from the last observed
    # upstream DAS_3 counter. Emitting immediately after the incoming message
    # prevents our messages from colliding with DASM.
    # The car accepts whichever of the two consecutive counters arrives first.
    offset = 3 if self.CP_SP.flags & ChryslerFlagsSP.BRAKE_HOLD_OFFSET_3 else 2
    counter = (self.last_das_3_counter + offset) % 16

    values = {
      "COUNTER": counter,
      "ACC_AVAILABLE": 1,
      "ACC_ACTIVE": 1,
      "ACC_DECEL": self.brake_hold_decel,
      "ACC_BRK_PREP": 1,
      # Leave all other fields at 0/default — we are specifically not
      # asserting ACC_STANDSTILL or overriding the gear request, which
      # could cause the car to re-engage ACC against our wishes.
    }
    return [packer.make_can_msg("DAS_3", das_bus, values)]
