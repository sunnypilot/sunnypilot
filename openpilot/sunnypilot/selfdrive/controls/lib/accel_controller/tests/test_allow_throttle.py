"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelController


class TestAllowThrottle(OpenpilotTestCase):
  def setUp(self):
    self.controller = AccelController()

  def update(self, throttle_prob: float, low_speed_override: bool = False) -> bool:
    return self.controller.update_allow_throttle(throttle_prob, low_speed_override=low_speed_override, threshold=0.4)

  def test_short_probability_dips_do_not_toggle(self):
    self.assertTrue(self.update(1.0))
    for _ in range(4):
      self.assertTrue(self.update(0.0))

  def test_probability_chatter_preserves_schmitt_state(self):
    self.assertTrue(self.update(1.0))
    for _ in range(100):
      self.assertTrue(self.update(0.39))
      self.assertTrue(self.update(0.46))

    self.controller = AccelController()
    self.assertFalse(self.update(0.0))
    for _ in range(100):
      self.assertFalse(self.update(0.39))
      self.assertFalse(self.update(0.46))

  def test_sustained_low_probability_disables(self):
    self.assertTrue(self.update(1.0))
    states = [self.update(0.0) for _ in range(6)]
    self.assertEqual(states, [True, True, True, True, False, False])

  def test_sustained_high_probability_reenables(self):
    self.assertFalse(self.update(0.0))
    states = [self.update(1.0) for _ in range(3)]
    self.assertEqual(states, [False, False, True])

  def test_threshold_boundaries(self):
    self.assertFalse(self.update(0.4))

    self.controller._throttle_prob_filter.initialized = False
    self.assertFalse(self.update(0.45))

    self.controller._throttle_prob_filter.initialized = False
    self.assertTrue(self.update(math.nextafter(0.45, math.inf)))

  def test_low_speed_override_is_immediate(self):
    self.assertTrue(self.update(0.0, True))
    self.assertFalse(self.update(0.0))

  def test_nonfinite_probability_fails_safe_without_poisoning_filter(self):
    self.assertTrue(self.update(1.0))
    self.assertTrue(self.update(math.nan))
    self.assertTrue(math.isfinite(self.controller._throttle_prob_filter.x))

    for value in (math.inf, -math.inf, math.nan):
      self.update(value)
      self.assertTrue(math.isfinite(self.controller._throttle_prob_filter.x))
    self.assertFalse(self.update(math.nan))
    self.assertTrue(self.update(1.0))

  def test_filter_updates_once_per_call(self):
    self.assertTrue(self.update(1.0))
    self.assertTrue(self.update(0.0))
    self.assertAlmostEqual(self.controller._throttle_prob_filter.x, 0.8)

  def test_filter_remains_active_when_accel_profiles_are_disabled(self):
    Params().put_bool("AccelPersonalityEnabled", False, block=True)
    self.controller = AccelController()
    self.assertFalse(self.controller.is_enabled())

    self.assertTrue(self.update(1.0))
    for _ in range(4):
      self.assertTrue(self.update(0.0))
    self.assertFalse(self.update(0.0))
