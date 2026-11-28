"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import itertools
import math
from types import SimpleNamespace

from openpilot.cereal import log
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.display import OnroadBrightness
from openpilot.selfdrive.ui.sunnypilot.ui_state import DeviceSP

BACKLIGHT_MIN = 30
MICI_FLOOR, TIZI_FLOOR = BACKLIGHT_MIN * 0.6, BACKLIGHT_MIN  # upstream's BRIGHTNESS_MIN per device
AlertSize = log.SelfdriveState.AlertSize


def state(setting: int, alert=AlertSize.none, timer: int = 0):
  ss = log.SelfdriveState.new_message(alertSize=alert)
  return SimpleNamespace(started=True, onroad_brightness=setting, onroad_brightness_timer=timer, sm={'selfdriveState': ss})


def manual(percent: int) -> int:
  return percent // 5 + 2  # the setting's 3-22 are 5-100%


class TestOnroadBrightness(OpenpilotTestCase):
  @parameterized.expand([
    (5, True, (30, 1 - 5 / 30)),     # mici: the panel stays at its floor and the UI dims
    (18, True, (30, 0.4)),           # upstream's lowest auto level
    (60, True, (60, 0.0)),
    (5, False, (5, 0.0)),            # tizi: the backlight itself
    (0, True, (0, 0.0)),             # screen off
    (0, False, (0, 0.0)),
  ])
  def test_backlight_and_dim(self, brightness, dims, expected):
    backlight, dim = DeviceSP.backlight_and_dim(brightness, BACKLIGHT_MIN, dims)
    assert backlight == expected[0] and math.isclose(dim, expected[1])

  @parameterized.expand(itertools.product([MICI_FLOOR, TIZI_FLOOR],
                                          [manual(5), manual(15), OnroadBrightness.SCREEN_OFF, OnroadBrightness.AUTO_DARK]))
  def test_alerts_never_show_below_the_auto_floor(self, floor, setting):
    quiet = DeviceSP.set_onroad_brightness(state(setting), True, 10.0, floor, BACKLIGHT_MIN)
    alert = DeviceSP.set_onroad_brightness(state(setting, AlertSize.full), True, 10.0, floor, BACKLIGHT_MIN)
    assert quiet < floor
    assert alert == floor

  def test_alert_keeps_a_brighter_auto_level(self):
    assert DeviceSP.set_onroad_brightness(state(manual(5), AlertSize.small), True, 70.0, MICI_FLOOR, BACKLIGHT_MIN) == 70.0

  def test_settings_apply_once_the_timer_runs_out(self):
    assert DeviceSP.set_onroad_brightness(state(manual(20), timer=5), True, 70.0, MICI_FLOOR, BACKLIGHT_MIN) == 70.0
    assert DeviceSP.set_onroad_brightness(state(manual(20)), True, 70.0, MICI_FLOOR, BACKLIGHT_MIN) == 20.0
    assert DeviceSP.set_onroad_brightness(state(OnroadBrightness.AUTO_DARK, timer=5), True, 10.0, MICI_FLOOR, BACKLIGHT_MIN) == BACKLIGHT_MIN
