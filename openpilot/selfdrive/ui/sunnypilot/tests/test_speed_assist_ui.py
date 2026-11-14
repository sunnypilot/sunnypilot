"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
import raylib_nb as rl

from openpilot.cereal import log
from openpilot.common.parameterized import parameterized
from openpilot.common.params import Params
from openpilot.common.prefix import OpenpilotPrefix

_prefix = OpenpilotPrefix()


# a hidden window and isolated params, since widgets load textures
def setUpModule():
  _prefix.__enter__()
  rl.set_config_flags(rl.FLAG_WINDOW_HIDDEN)
  from openpilot.system.ui.lib.application import gui_app
  gui_app.init_window("test_speed_assist_ui", fps=30)


def tearDownModule():
  from openpilot.system.ui.lib.application import gui_app
  gui_app.close()
  _prefix.__exit__(None, None, None)


def render(widget):
  widget.render(rl.Rectangle(0, 0, 800, 600))


class FakeSubMaster(dict):
  def __init__(self, msgs):
    super().__init__(msgs)
    self.valid = dict.fromkeys(msgs, True)


class SpeedAssistTestCase(unittest.TestCase):
  def setUp(self):
    from openpilot.selfdrive.ui.ui_state import ui_state
    self.params = Params()
    ui_state.params = self.params
    ui_state.update_params()
    self.addCleanup(self.params.remove, "SetSpeedAssist")

  def patch(self, target, name, value):
    patcher = mock.patch.object(target, name, value)
    patcher.start()
    self.addCleanup(patcher.stop)


class TestSpeedAssistDial(SpeedAssistTestCase):
  def test_fill_runs_from_the_arc_start_to_the_needle(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    assert d.fill_to(0.0) == d.ARC_FROM
    assert d.fill_to(1.0) == d.NEEDLE_DEG
    assert d.fill_to(0.5) == (d.ARC_FROM + d.NEEDLE_DEG) / 2
    assert d.fill_to(2.0) == d.NEEDLE_DEG

  def test_needle_turns_green_only_on_arrival(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_dial import needle_level
    assert needle_level(0.0) == needle_level(0.8) == 0.0
    assert 0.0 < needle_level(0.92) < 1.0
    assert needle_level(1.0) == 1.0

  def test_dial_matches_the_car(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    arc = d.arc_outline(1.0, d.ARC_TO)
    assert np.isclose(arc[:, 0].max() - arc[:, 0].min(), 35.0, atol=0.05)  # the lead car's width
    needle = d.needle_outline(1.0)
    top = -(d.RADIUS + d.STROKE / 2)
    assert np.isclose(min(arc[:, 1].min(), needle[:, 1].min()), top, atol=0.05)
    assert np.isclose(max(arc[:, 1].max(), needle[:, 1].max()) - top, d.DIAL_HEIGHT, atol=0.05)
    assert np.hypot(needle[:, 0], needle[:, 1]).max() <= d.RADIUS - d.STROKE / 2 - d.NEEDLE_CLEARANCE + 0.05

  def test_layout_lands_on_whole_pixels(self):
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li
    assert li.DIAL_TOP == int(li.DIAL_TOP) and li.STACK_TOP + li.STACK_SHIFT == int(li.STACK_TOP + li.STACK_SHIFT)
    assert li.DIAL_TOP - li.DM_BOTTOM >= li.DIAL_GAP

  def _settle(self, frames=200):
    """Steps LongIndicatorSP over a stub of upstream's _render. Returns (stack rects, dial draws)."""
    from openpilot.selfdrive.ui.mici.onroad.long_indicator import LongIndicator
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li

    stacks, dials = [], []
    def upstream_render(self, rect):
      stacks.append(rect)
      self._alpha_filter.x = self._dim_filter.x = 1.0
    self.patch(LongIndicator, "_render", upstream_render)
    self.patch(li, "draw_dial", lambda cx, top, **kw: dials.append((top, kw)))
    sp = li.LongIndicatorSP()
    for _ in range(frames):
      sp._render(rl.Rectangle(0, 0, 72, 240))
    return stacks, dials

  @parameterized.expand([(True,), (False,)])
  def test_stack_shifts_only_with_the_assist(self, speed_assist):
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li
    from openpilot.selfdrive.ui.ui_state import ui_state

    self.patch(ui_state, "speed_assist", speed_assist)
    stacks, dials = self._settle()
    if speed_assist:
      assert math.isclose(stacks[-1].y, li.STACK_SHIFT, abs_tol=0.05)
      assert math.isclose(dials[-1][0], li.DIAL_TOP, abs_tol=0.05) and math.isclose(dials[-1][1]["alpha"], 1.0, abs_tol=0.01)
    else:
      assert math.isclose(stacks[-1].y, 0.0, abs_tol=1e-12) and math.isclose(dials[-1][1]["alpha"], 0.0, abs_tol=1e-12)

  def test_lift_fills_the_dial(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    from openpilot.selfdrive.ui.ui_state import ui_state

    self.patch(ui_state, "speed_assist", True)
    self.patch(d, "lift_fraction", lambda: 0.75)
    _, dials = self._settle(frames=300)
    assert math.isclose(dials[-1][1]["lift"], 0.75, abs_tol=0.01)

  @parameterized.expand([
    (True, True, 0.5),
    (True, False, 0.0),  # MADS lateral-only, or disengaged
    (False, True, 0.0),  # the car's own ACC
  ])
  def test_lift_only_while_openpilot_drives_longitudinal(self, has_long, enabled, expected):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    from openpilot.selfdrive.ui.ui_state import ui_state
    from openpilot.sunnypilot.selfdrive.controls.lib.set_speed_assist import approach_ceiling

    standard = log.LongitudinalPersonality.standard
    lift = 0.5 * approach_ceiling(20., standard)
    self.patch(ui_state, "sm", FakeSubMaster({
      'selfdriveState': SimpleNamespace(enabled=enabled, personality=standard),
      'carState': SimpleNamespace(vEgo=20.),
      'longitudinalPlanSP': SimpleNamespace(setSpeedAssist=SimpleNamespace(lift=lift)),
    }))
    self.patch(ui_state, "started", True)
    self.patch(ui_state, "has_longitudinal_control", has_long)
    assert math.isclose(d.lift_fraction(), expected, rel_tol=1e-6, abs_tol=1e-12)

  def test_dial_draws(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_dial import draw_dial
    for lift in (0.0, 0.005, 0.4, 1.0):
      draw_dial(36, 71, lift=lift)


class TestSpeedAssistQuickToggles(SpeedAssistTestCase):
  def test_home_shows_speed_assist_after_network(self):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.home import MiciHomeLayoutSP
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_badge import STATUS_ICON_HEIGHT
    from openpilot.selfdrive.ui.ui_state import ui_state

    home = MiciHomeLayoutSP()
    assert home._status_bar_layout.widgets[2] is home._speed_assist_icon
    assert home._speed_assist_icon.rect.height == STATUS_ICON_HEIGHT
    for has_long, speed_assist, shown in ((True, True, True), (True, False, False), (False, True, False)):
      self.patch(ui_state, "has_longitudinal_control", has_long)
      self.patch(ui_state, "speed_assist", speed_assist)
      assert home._speed_assist_icon.is_visible == shown
    render(home)

  def _switches(self, toggle):
    from openpilot.selfdrive.ui.ui_state import ui_state

    self.patch(ui_state, "has_longitudinal_control", True)
    for start in (True, False):
      ui_state.speed_assist = start
      toggle()
      assert self.params.get_bool("SetSpeedAssist") is (not start)
      assert ui_state.speed_assist is (not start)

    # no openpilot longitudinal, nothing to switch
    self.patch(ui_state, "has_longitudinal_control", False)
    self.params.put_bool("SetSpeedAssist", True)
    ui_state.speed_assist = True
    toggle()
    assert self.params.get_bool("SetSpeedAssist") and ui_state.speed_assist

  def test_home_long_press_switches_speed_assist(self):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.home import MiciHomeLayoutSP
    self._switches(MiciHomeLayoutSP()._long_press_callback)

  def test_onroad_button_switches_speed_assist(self):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_button import SpeedAssistButton
    button = SpeedAssistButton(192)
    self._switches(lambda: button._handle_mouse_release(None))

  @parameterized.expand([(True,), (False,)])
  def test_onroad_button_draws(self, speed_assist):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_button import SpeedAssistButton
    from openpilot.selfdrive.ui.ui_state import ui_state

    self.patch(ui_state, "speed_assist", speed_assist)
    SpeedAssistButton(192).render(rl.Rectangle(0, 0, 192, 192))
