import unittest
from unittest.mock import patch

from opendbc.car import structs
from opendbc.sunnypilot.car.toyota.auto_brake_hold import AutoBrakeHoldCarController, BRAKE_HOLD_ALLOWED_TIMER, pcs_is_active
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP

GearShifter = structs.CarState.GearShifter


def make_car_params_sp(enabled: bool = True) -> structs.CarParamsSP:
  cp_sp = structs.CarParamsSP()
  cp_sp.flags = ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD if enabled else 0
  return cp_sp


class FakeCarState:
  def __init__(self, standstill=True, cruise_enabled=False, cruise_available=True, gas_pressed=False,
               gear=GearShifter.drive, brake_pressed=False, pre_collision_2=None):
    self.out = structs.CarState()
    self.out.standstill = standstill
    self.out.cruiseState.enabled = cruise_enabled
    self.out.cruiseState.available = cruise_available
    self.out.gasPressed = gas_pressed
    self.out.gearShifter = gear
    self.out.brakePressed = brake_pressed
    self.pre_collision_2 = pre_collision_2 if pre_collision_2 is not None else {}


@patch("opendbc.sunnypilot.car.toyota.auto_brake_hold.toyotacan.create_brake_hold_command")
class TestAutoBrakeHoldCarController(unittest.TestCase):
  def _make(self):
    return AutoBrakeHoldCarController(structs.CarParams(), make_car_params_sp())

  def test_enabled_reflects_flag(self, mock_create):
    for value in range(256):
      with self.subTest(flags=value):
        cp_sp = structs.CarParamsSP()
        cp_sp.flags = value
        ctrl = AutoBrakeHoldCarController(structs.CarParams(), cp_sp)
        self.assertEqual(ctrl.enabled, bool(value & ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD))

  def test_does_not_engage_before_timer(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    for i in range(BRAKE_HOLD_ALLOWED_TIMER):
      ctrl.update(cs, i, None)
      self.assertFalse(ctrl.active)

  def test_engages_after_timer_once_brake_released(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    for i in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, i, None)
    self.assertTrue(ctrl.active)

  def test_brake_still_down_from_the_stop_does_not_block_engagement(self, mock_create):
    # the driver's foot is normally still on the brake on the very frame standstill is reached -
    # that must not count as a "fresh press" release, or the feature could never engage
    ctrl = self._make()
    # decelerating into the stop with the brake held continuously
    cs = FakeCarState(standstill=False, brake_pressed=True)
    for i in range(30):
      ctrl.update(cs, i, None)
    # reaches standstill, foot stays down for a while, then lifts
    cs.out.standstill = True
    for i in range(30, 50):
      ctrl.update(cs, i, None)
      self.assertFalse(ctrl.active, "must not engage while the original stopping press is still held")
    cs.out.brakePressed = False
    for i in range(50, 50 + BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, i, None)
    self.assertTrue(ctrl.active, "should engage once the stopping press is released and the timer elapses")

  def test_fresh_brake_press_mid_hold_releases_and_stays_released(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    frame = 0
    for _ in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, frame, None)
      frame += 1
    self.assertTrue(ctrl.active)

    cs.out.brakePressed = True
    ctrl.update(cs, frame, None)
    frame += 1
    self.assertFalse(ctrl.active, "a fresh press should release immediately")

    for _ in range(20):
      ctrl.update(cs, frame, None)
      frame += 1
      self.assertFalse(ctrl.active, "must stay released for the rest of the episode while continuously held")

    cs.out.brakePressed = False
    for _ in range(20):
      ctrl.update(cs, frame, None)
      frame += 1
      self.assertFalse(ctrl.active, "must stay released for the rest of the episode even after lifting off again")

  def test_drive_off_and_restop_rearms(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    frame = 0
    for _ in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, frame, None)
      frame += 1
    cs.out.brakePressed = True
    ctrl.update(cs, frame, None)
    frame += 1
    self.assertFalse(ctrl.active)

    # drives off - leaves the standstill episode entirely
    cs.out.standstill = False
    ctrl.update(cs, frame, None)
    frame += 1

    # stops again
    cs.out.standstill = True
    cs.out.brakePressed = False
    for _ in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, frame, None)
      frame += 1
    self.assertTrue(ctrl.active, "should re-arm and engage again at the next stop")

  def test_cruise_engaged_blocks_hold(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(cruise_enabled=True, brake_pressed=False)
    for i in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, i, None)
    self.assertFalse(ctrl.active, "must not hold while ACC is engaged - that's the point of the constraint")

  def test_gas_pressed_blocks_hold(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(gas_pressed=True, brake_pressed=False)
    for i in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, i, None)
    self.assertFalse(ctrl.active)

  def test_park_and_reverse_block_hold(self, mock_create):
    for gear in (GearShifter.park, GearShifter.reverse):
      with self.subTest(gear=gear):
        ctrl = self._make()
        cs = FakeCarState(gear=gear, brake_pressed=False)
        for i in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
          ctrl.update(cs, i, None)
        self.assertFalse(ctrl.active)

  def test_yields_to_live_pcs_without_dropping_active_state(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    frame = 0
    for _ in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
      ctrl.update(cs, frame, None)
      frame += 1
    self.assertTrue(ctrl.active)
    mock_create.reset_mock()

    # a real PCS event shows up on the live signal
    cs.pre_collision_2 = {"PCSALM": 1}
    # advance to the next even frame the message is actually built on
    while frame % 2 != 0:
      frame += 1
    ctrl.update(cs, frame, None)
    override_arg = mock_create.call_args.args[-1]
    self.assertTrue(ctrl.active, "internal hold state should not be cleared by a live PCS event")
    self.assertFalse(override_arg, "must not override PRE_COLLISION_2 while PCS is genuinely active")

    # once PCS goes quiet again, override resumes on our own signal, not stale PCS state
    frame += 2
    cs.pre_collision_2 = {}
    ctrl.update(cs, frame, None)
    override_arg = mock_create.call_args.args[-1]
    self.assertTrue(override_arg)

  def test_message_only_built_every_other_frame(self, mock_create):
    ctrl = self._make()
    cs = FakeCarState(brake_pressed=False)
    for i in range(10):
      ctrl.update(cs, i, None)
    self.assertEqual(mock_create.call_count, 5)

  def test_no_message_sent_outside_relay_blocked_window(self, mock_create):
    # outside relay_blocked, toyota_fwd_hook lets the real PRE_COLLISION_2 relay through on its own -
    # our passthrough copy would just be redundant traffic panda rejects, so it must not be sent at all
    cases = [
      dict(cruise_enabled=True),
      dict(gas_pressed=True),
      dict(cruise_available=False),
    ]
    for kwargs in cases:
      with self.subTest(kwargs=kwargs):
        ctrl = self._make()
        cs = FakeCarState(brake_pressed=False, **kwargs)
        for i in range(10):
          ctrl.update(cs, i, None)
        mock_create.assert_not_called()

  def test_message_still_sent_in_park_or_reverse(self, mock_create):
    # relay_blocked has no gear check, matching toyota_fwd_hook - park/reverse must not open a gap
    # in the PRE_COLLISION_2 relay even though hold can never engage there (this was a real
    # regression: gating the send on hold_allowed's gear check left bus 0 with nothing at this
    # address while parked, which is what tripped a genuine PCS dash fault on-road)
    for gear in (GearShifter.park, GearShifter.reverse):
      with self.subTest(gear=gear):
        ctrl = self._make()
        cs = FakeCarState(gear=gear, brake_pressed=False)
        for i in range(BRAKE_HOLD_ALLOWED_TIMER + 1):
          ctrl.update(cs, i, None)
        self.assertFalse(ctrl.active, "must never actually hold in park/reverse")
        self.assertGreater(mock_create.call_count, 0, "must still relay PRE_COLLISION_2 in park/reverse")
        override_arg = mock_create.call_args.args[-1]
        self.assertFalse(override_arg, "never override while gear disallows an actual hold")


class TestPcsIsActive(unittest.TestCase):
  def test_all_zero_is_not_active(self):
    self.assertFalse(pcs_is_active({}))
    self.assertFalse(pcs_is_active({"PCSALM": 0, "DSS1GDRV": 0}))

  def test_any_trigger_field_is_active(self):
    for field in ("PCSALM", "IBTRGR", "PBATRGR", "PREFILL", "AVSTRGR", "PBRTRGR", "PPTRGR"):
      with self.subTest(field=field):
        self.assertTrue(pcs_is_active({field: 1}))

  def test_nonzero_force_signal_is_active(self):
    self.assertTrue(pcs_is_active({"DSS1GDRV": -5}))
    self.assertFalse(pcs_is_active({"DSS1GDRV": 0}))


if __name__ == "__main__":
  unittest.main()
