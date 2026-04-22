"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import unittest
from dataclasses import dataclass, field

from opendbc.car import structs
from opendbc.car.chrysler.values import CAR
from opendbc.sunnypilot.car.chrysler.brake_hold import (
  ACC_ACCEL_THRESHOLD,
  ACC_DECEL_THRESHOLD,
  DEFAULT_BRAKE_HOLD_DECEL,
  BrakeHold,
)
from opendbc.sunnypilot.car.chrysler.values_ext import ChryslerFlagsSP

GearShifter = structs.CarState.GearShifter


@dataclass
class CruiseState:
  enabled: bool = False
  available: bool = True


@dataclass
class FakeCS:
  """Minimal CarState surface the BrakeHold state machine reads."""
  standstill: bool = True
  gearShifter: int = GearShifter.drive
  gasPressed: bool = False
  brakePressed: bool = False
  cruiseState: CruiseState = field(default_factory=CruiseState)


@dataclass
class FakeCP:
  carFingerprint: str = CAR.JEEP_GRAND_CHEROKEE_2019


@dataclass
class FakeCPSP:
  flags: int = ChryslerFlagsSP.BRAKE_HOLD.value  # user has opted in


def _decel_accel(acc_decel: float):
  """Convert a raw ACC_DECEL value into the (decelerating, accelerating) pair
  that carstate_ext computes, matching the thresholds the real module uses."""
  return acc_decel < ACC_DECEL_THRESHOLD, acc_decel > ACC_ACCEL_THRESHOLD


class TestBrakeHoldStateMachine(unittest.TestCase):

  def setUp(self):
    self.bh = BrakeHold(FakeCP(), FakeCPSP())
    self.cs = FakeCS()
    self.cs.cruiseState.enabled = True
    self.cs.cruiseState.available = True
    self.counter = 0

  def _step(self, acc_decel: float):
    """Advance the state machine one tick."""
    dec, acc = _decel_accel(acc_decel)
    self.counter = (self.counter + 1) % 16
    return self.bh.update_state(self.cs, dec, acc, self.counter, acc_decel)

  # --- activation ---

  def test_does_not_activate_when_param_disabled(self):
    self.bh.enabled_by_param = False
    self.assertFalse(self._step(-2.0))

  def test_does_not_activate_while_moving(self):
    self.cs.standstill = False
    self.assertFalse(self._step(-2.0))

  def test_does_not_activate_out_of_drive(self):
    self.cs.gearShifter = GearShifter.neutral
    self.assertFalse(self._step(-2.0))

  def test_does_not_activate_with_gas(self):
    self.cs.gasPressed = True
    self.assertFalse(self._step(-2.0))

  def test_does_not_activate_with_brake(self):
    self.cs.brakePressed = True
    self.assertFalse(self._step(-2.0))

  def test_does_not_activate_when_acc_not_decelerating(self):
    # ACC active at standstill but no decel request (coasting / already stopped
    # without a decel assertion) — not the condition we want to latch on.
    self.assertFalse(self._step(0.0))

  def test_does_not_activate_when_acc_off(self):
    self.cs.cruiseState.enabled = False
    self.assertFalse(self._step(-2.0))

  def test_activates_on_decel_at_standstill(self):
    self.assertTrue(self._step(-2.0))

  # --- hold & decel tracking ---

  def test_tracks_minimum_decel(self):
    # jvePilot-style: brake_hold_decel becomes the most-negative ACC_DECEL
    # observed while ACC was active. Start at default (-2.0), tighten to -3.0.
    self._step(-1.0)
    self.assertEqual(self.bh.brake_hold_decel, DEFAULT_BRAKE_HOLD_DECEL)  # -1.0 is not more negative than -2.0
    self._step(-3.0)
    self.assertAlmostEqual(self.bh.brake_hold_decel, -3.0, places=3)
    self._step(-1.5)  # weaker decel should not relax the hold pressure
    self.assertAlmostEqual(self.bh.brake_hold_decel, -3.0, places=3)

  def test_stays_active_across_zero_decel_frames(self):
    # Once activated, transient frames with small ACC_DECEL (e.g. DASM slack)
    # must not release the hold. Only the hard deactivation conditions do.
    self.assertTrue(self._step(-2.0))
    for _ in range(100):
      self.assertTrue(self._step(-0.1))

  # --- deactivation ---

  def test_deactivates_on_gas(self):
    self.assertTrue(self._step(-2.0))
    self.cs.gasPressed = True
    self.assertFalse(self._step(-2.0))

  def test_deactivates_on_brake(self):
    self.assertTrue(self._step(-2.0))
    self.cs.brakePressed = True
    self.assertFalse(self._step(-2.0))

  def test_deactivates_on_gear_change(self):
    self.assertTrue(self._step(-2.0))
    self.cs.gearShifter = GearShifter.neutral
    self.assertFalse(self._step(-2.0))

  def test_deactivates_on_vehicle_moving(self):
    # The car rolled (e.g. a hill). We release immediately so stock ACC can
    # take over.
    self.assertTrue(self._step(-2.0))
    self.cs.standstill = False
    self.assertFalse(self._step(-2.0))

  def test_deactivates_on_cruise_main_off(self):
    self.assertTrue(self._step(-2.0))
    self.cs.cruiseState.available = False
    self.assertFalse(self._step(-2.0))

  def test_deactivates_on_acc_accelerating(self):
    # Lead departed and ACC is commanding positive accel again — hand off.
    self.assertTrue(self._step(-2.0))
    self.assertFalse(self._step(+1.0))

  def test_resets_decel_tracking_on_deactivate(self):
    self._step(-3.0)
    self.assertAlmostEqual(self.bh.brake_hold_decel, -3.0, places=3)
    self.cs.gasPressed = True
    self._step(-3.0)
    self.assertEqual(self.bh.brake_hold_decel, DEFAULT_BRAKE_HOLD_DECEL)

  # --- re-activation after driver intervention ---

  def test_can_reactivate_after_release(self):
    # Driver brakes, ACC re-engages, comes to a stop behind a lead again —
    # brake hold should latch the second time just like the first.
    self.assertTrue(self._step(-2.0))
    self.cs.brakePressed = True
    self.assertFalse(self._step(-2.0))
    self.cs.brakePressed = False
    self.assertTrue(self._step(-2.0))


if __name__ == "__main__":
  unittest.main()
