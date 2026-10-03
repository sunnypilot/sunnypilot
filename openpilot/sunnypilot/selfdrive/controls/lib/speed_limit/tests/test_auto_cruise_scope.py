import math
import unittest
from unittest.mock import patch

from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.sunnypilot.selfdrive.car import cruise_ext
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.automatic_set import AutomaticSet


class TestAutoCruiseScope(unittest.TestCase):
  def helper(self, pcm_speed):
    helper = cruise_ext.VCruiseHelperSP.__new__(cruise_ext.VCruiseHelperSP)
    helper.CP = car.CarParams.new_message(brand='toyota', carFingerprint='SYNTHETIC_NON_PCM',
                                          openpilotLongitudinalControl=True, pcmCruise=False)
    helper.CP_SP = custom.CarParamsSP.new_message(pcmCruiseSpeed=pcm_speed)
    helper.auto_set = AutomaticSet()
    helper.auto_button_timers = dict.fromkeys(cruise_ext.CRUISE_BUTTON_TIMER, 0)
    helper.enable_button_timers = dict.fromkeys(cruise_ext.CRUISE_BUTTON_TIMER, 0)
    helper.enabled_prev = False
    helper.speed_limit_mode = 4
    helper.auto_target = 80.
    helper.auto_control_ok = True
    helper.v_cruise_kph = 50
    helper.get_minimum_set_speed(True)
    return helper

  def state(self):
    cs = car.CarState.new_message(canValid=True)
    cs.cruiseState.available = True
    return cs

  def tick(self, helper, cs, now, enabled=True):
    with patch.object(cruise_ext.time, 'monotonic', return_value=now):
      helper.update_enabled_state(cs, enabled)
      helper.update_automatic_set(cs, enabled)
    return helper.v_cruise_kph

  def arm(self, helper, cs):
    for now in (100., 100.1, 100.7):
      self.tick(helper, cs, now)
    self.assertEqual(helper.v_cruise_kph, 80.)

  def test_brand_and_fingerprint_do_not_restrict_eligible_set_updates(self):
    for brand in ('honda', 'toyota', 'hyundai', 'subaru', 'ford', 'volkswagen'):
      with self.subTest(brand=brand):
        helper, cs = self.helper(False), self.state()
        helper.CP.brand = brand
        self.arm(helper, cs)
        helper.auto_target = 40.
        self.assertEqual(self.tick(helper, cs, 101.), 40.)

  def test_engagement_button_must_be_released_for_both_cruise_configurations(self):
    for pcm_speed in (False, True):
      with self.subTest(pcm_speed=pcm_speed):
        helper, cs = self.helper(pcm_speed), self.state()
        cs.buttonEvents = [{'type': 'resumeCruise', 'pressed': True}]
        self.assertEqual(self.tick(helper, cs, 100.), 50)
        cs.buttonEvents = []
        for now in (100.2, 100.8, 103.):
          self.assertEqual(self.tick(helper, cs, now), 50)
        cs.buttonEvents = [{'type': 'resumeCruise', 'pressed': False}]
        self.assertEqual(self.tick(helper, cs, 103.1), 50)
        cs.buttonEvents = []
        self.assertEqual(self.tick(helper, cs, 103.2), 50)
        self.assertEqual(self.tick(helper, cs, 103.6), 50)
        self.assertEqual(self.tick(helper, cs, 103.8), 80.)

  def test_manual_press_latches_until_new_engagement_for_both_configurations(self):
    for pcm_speed in (False, True):
      with self.subTest(pcm_speed=pcm_speed):
        helper, cs = self.helper(pcm_speed), self.state()
        self.arm(helper, cs)
        helper.auto_target = 40.
        cs.buttonEvents = [{'type': 'decelCruise', 'pressed': True}]
        self.assertEqual(self.tick(helper, cs, 101.), 80.)
        cs.buttonEvents = []
        self.assertEqual(self.tick(helper, cs, 103.), 80.)
        cs.buttonEvents = [{'type': 'decelCruise', 'pressed': False}]
        self.assertEqual(self.tick(helper, cs, 104.), 80.)
        cs.buttonEvents = []
        self.tick(helper, cs, 105., enabled=False)
        for now in (106., 106.1, 106.7):
          self.tick(helper, cs, now)
        self.assertEqual(helper.v_cruise_kph, 40.)

  def test_platform_minimum_is_preserved_in_metric_and_imperial_modes(self):
    for pcm_speed in (False, True):
      for metric in (False, True):
        with self.subTest(pcm_speed=pcm_speed, metric=metric):
          helper, cs = self.helper(pcm_speed), self.state()
          helper.get_minimum_set_speed(metric)
          minimum = 8 if pcm_speed else (30 if metric else 20)
          self.assertEqual(helper.v_cruise_min, minimum)
          self.arm(helper, cs)
          helper.auto_target = math.nextafter(float(minimum), 0.)
          self.assertEqual(self.tick(helper, cs, 101.), 80.)
          helper.auto_target = float(minimum)
          self.assertEqual(self.tick(helper, cs, 101.1), minimum)

  def test_pedals_cancel_and_invalid_control_preserve_current_set(self):
    for pcm_speed in (False, True):
      for event in ('gasPressed', 'brakePressed', 'cancel', 'control'):
        with self.subTest(pcm_speed=pcm_speed, event=event):
          helper, cs = self.helper(pcm_speed), self.state()
          self.arm(helper, cs)
          helper.auto_target = 40.
          if event == 'cancel':
            cs.buttonEvents = [{'type': 'cancel', 'pressed': True}]
          elif event == 'control':
            helper.auto_control_ok = False
          else:
            setattr(cs, event, True)
          self.assertEqual(self.tick(helper, cs, 101.), 80.)
          if event != 'control':
            self.assertTrue(helper.auto_set.takeover)


if __name__ == '__main__':
  unittest.main()

