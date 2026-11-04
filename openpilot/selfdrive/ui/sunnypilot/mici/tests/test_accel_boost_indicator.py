"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import log
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.accel_boost_indicator import (
  get_boost_style, get_boost_fraction, lighten,
  AGGRESSIVE_COLOR, RELAXED_COLOR, STANDARD_COLOR,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import ACCEL_BOOST_MAX


class TestAccelBoostIndicator(OpenpilotTestCase):
  def test_profile_styles_match_controller_caps(self):
    for personality, color, max_boost in (
        (log.LongitudinalPersonality.aggressive, AGGRESSIVE_COLOR, ACCEL_BOOST_MAX[0]),
        (log.LongitudinalPersonality.standard, STANDARD_COLOR, ACCEL_BOOST_MAX[1]),
        (log.LongitudinalPersonality.relaxed, RELAXED_COLOR, ACCEL_BOOST_MAX[2])):
      style_color, style_max = get_boost_style(personality)
      assert style_color == color
      assert style_max == max_boost

  def test_wire_personality_picks_the_right_profile(self):
    msg = log.SelfdriveState.new_message()
    msg.personality = log.LongitudinalPersonality.aggressive
    color, max_boost = get_boost_style(msg.personality)
    assert color == AGGRESSIVE_COLOR
    assert max_boost == ACCEL_BOOST_MAX[0]

  def test_bar_fills_at_the_active_profile_cap(self):
    for cap in ACCEL_BOOST_MAX:
      assert get_boost_fraction(0.0, cap) == 0.0
      assert get_boost_fraction(cap * 0.5, cap) == 0.5
      assert get_boost_fraction(cap, cap) == 1.0

    # A boost beyond the current cap (e.g. after switching to a shorter profile) still fills the bar
    assert get_boost_fraction(max(ACCEL_BOOST_MAX), min(ACCEL_BOOST_MAX)) == 1.0
    assert get_boost_fraction(0.0, 0.0) == 0.0

  def test_cap_lighten_keeps_the_profile_hue(self):
    # An HSV blend towards white sweeps relaxed blue through pink, so the fill lightens in RGB instead
    relaxed = lighten(RELAXED_COLOR, 0.45)
    aggressive = lighten(AGGRESSIVE_COLOR, 0.45)
    assert relaxed.b > relaxed.r
    assert relaxed.b >= relaxed.g
    assert aggressive.r > aggressive.b
    # lighter in RGB means the dimmest channel came up towards white
    assert relaxed.r > RELAXED_COLOR.r
    assert aggressive.g > AGGRESSIVE_COLOR.g
