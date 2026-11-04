"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import log
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.accel_boost_indicator import (
  CAP_BLEND_START, COLOR_FILL, get_boost_color, get_boost_fraction,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import ACCEL_BOOST_MAX, get_boost_max


class TestAccelBoostIndicator(OpenpilotTestCase):
  def test_bar_fills_at_the_active_profile_cap(self):
    for personality in (log.LongitudinalPersonality.aggressive, log.LongitudinalPersonality.standard,
                        log.LongitudinalPersonality.relaxed):
      cap = get_boost_max(personality)
      assert get_boost_fraction(0.0, cap) == 0.0
      assert get_boost_fraction(cap * 0.5, cap) == 0.5
      assert get_boost_fraction(cap, cap) == 1.0

    assert get_boost_fraction(max(ACCEL_BOOST_MAX), min(ACCEL_BOOST_MAX)) == 1.0
    assert get_boost_fraction(0.0, 0.0) == 0.0
    assert get_boost_fraction(-1.0, get_boost_max()) == 0.0

  def test_fill_lightens_as_boost_builds(self):
    base = get_boost_color(0.0)
    assert (base.r, base.g, base.b) == (COLOR_FILL.r, COLOR_FILL.g, COLOR_FILL.b)
    assert (get_boost_color(CAP_BLEND_START).r, get_boost_color(CAP_BLEND_START).b) == (COLOR_FILL.r, COLOR_FILL.b)

    full = get_boost_color(1.0)
    assert full.r > base.r
    assert full.b > base.b
    assert full.g > full.r and full.g > full.b
