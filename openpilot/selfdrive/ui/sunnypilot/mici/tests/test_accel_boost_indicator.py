"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.accel_boost import ACCEL_BOOST_MAX
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.accel_boost_indicator import (get_boost_style, get_boost_fraction, lighten,
                                                                                AGGRESSIVE_COLOR, RELAXED_COLOR, STANDARD_COLOR)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost_ext import (SCALE_AGGRESSIVE, SCALE_RELAXED, SCALE_STANDARD,
                                                                        get_accel_boost_max)


class TestAccelBoostIndicator(unittest.TestCase):
  def test_bar_scales_with_following_distance(self):
    for personality, color, scale in (
        (log.LongitudinalPersonality.relaxed, RELAXED_COLOR, SCALE_RELAXED),
        (log.LongitudinalPersonality.standard, STANDARD_COLOR, SCALE_STANDARD),
        (log.LongitudinalPersonality.aggressive, AGGRESSIVE_COLOR, SCALE_AGGRESSIVE)):
      bar_color, full_scale = get_boost_style(personality)
      self.assertEqual(bar_color, color)
      self.assertAlmostEqual(full_scale, ACCEL_BOOST_MAX * (1.0 + scale))

  def test_bar_fills_at_the_active_profile_cap(self):
    caps = [get_accel_boost_max(p) for p in (log.LongitudinalPersonality.relaxed,
                                             log.LongitudinalPersonality.standard,
                                             log.LongitudinalPersonality.aggressive)]
    self.assertEqual(caps, sorted(caps))

    for cap in caps:
      self.assertAlmostEqual(get_boost_fraction(cap, cap), 1.0)
      self.assertAlmostEqual(get_boost_fraction(0.0, cap), 0.0)
      self.assertAlmostEqual(get_boost_fraction(cap * 0.5, cap), 0.5)

    # A boost beyond the current cap (e.g. after switching to a shorter profile) still fills the bar
    self.assertAlmostEqual(get_boost_fraction(caps[2], caps[0]), 1.0)
    self.assertAlmostEqual(get_boost_fraction(0.0, 0.0), 0.0)

  def test_cap_lighten_keeps_the_profile_hue(self):
    # An HSV blend towards white sweeps relaxed blue through pink, so the fill lightens in RGB instead
    relaxed = lighten(RELAXED_COLOR, 0.45)
    aggressive = lighten(AGGRESSIVE_COLOR, 0.45)
    self.assertGreater(relaxed.b, relaxed.r)
    self.assertGreaterEqual(relaxed.b, relaxed.g)
    self.assertGreater(aggressive.r, aggressive.b)
    # lighter in RGB means the dimmest channel came up towards white
    self.assertGreater(relaxed.r, RELAXED_COLOR.r)
    self.assertGreater(aggressive.g, AGGRESSIVE_COLOR.g)

  def test_wire_personality_picks_the_right_profile(self):
    # Over the wire personality is a capnp DynamicEnum, which compares equal to the cereal enum but hashes differently
    msg = log.SelfdriveState.new_message()
    msg.personality = log.LongitudinalPersonality.aggressive
    color, full_scale = get_boost_style(msg.personality)
    self.assertEqual(color, AGGRESSIVE_COLOR)
    self.assertAlmostEqual(full_scale, get_accel_boost_max(log.LongitudinalPersonality.aggressive))
