"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from opendbc.safety.tests.libsafety import libsafety_py


class RxChecksSafetyTestBase(unittest.TestCase):
  safety: libsafety_py.LibSafety

  def _ignore_frequency_check_msgs(self):
    return []

  def test_ignore_frequency_check(self):
    msgs = self._ignore_frequency_check_msgs()
    self.assertEqual(len(msgs), self.safety.get_ignore_frequency_check_count())

    for msg in msgs:
      self.assertTrue(self._rx(msg))
      self.assertTrue(self.safety.get_rx_check_ignore_frequency(msg[0].addr, msg[0].bus))

    self.safety.set_unseen_rx_checks_valid()
    self.safety.set_controls_allowed(True)
    self.safety.safety_tick()
    self.assertTrue(self.safety.get_controls_allowed())
