"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Set Speed Assist's dial: over mici's long indicator, in the home footer and in the tizi onroad button.
"""
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import log


@pytest.fixture(scope="module")
def gui():
  """A hidden window and isolated params: widgets load textures."""
  import raylib_nb as rl
  from openpilot.common.prefix import OpenpilotPrefix

  with OpenpilotPrefix():
    rl.set_config_flags(rl.FLAG_WINDOW_HIDDEN)
    from openpilot.system.ui.lib.application import gui_app
    gui_app.init_window("test_speed_assist_ui", fps=30)
    yield gui_app
    gui_app.close()


@pytest.fixture
def params(gui):
  from openpilot.common.params import Params
  from openpilot.selfdrive.ui.ui_state import ui_state

  p = Params()
  ui_state.params = p
  ui_state.update_params()
  yield p
  p.remove("SetSpeedAssist")


def render(widget):
  import raylib_nb as rl
  widget.render(rl.Rectangle(0, 0, 800, 600))


class FakeSubMaster(dict):
  def __init__(self, msgs):
    super().__init__(msgs)
    self.valid = dict.fromkeys(msgs, True)


class TestSpeedAssistDial:
  """Shown over mici's long indicator with the assist on, the stack shifted to make room, and the arc
  filling toward the parked needle with the lift."""

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
    # the needle stops short of the arc's inner edge
    assert np.hypot(needle[:, 0], needle[:, 1]).max() <= d.RADIUS - d.STROKE / 2 - d.NEEDLE_CLEARANCE + 0.05

  def test_layout_lands_on_whole_pixels(self):
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li
    assert li.DIAL_TOP == int(li.DIAL_TOP) and li.STACK_TOP + li.STACK_SHIFT == int(li.STACK_TOP + li.STACK_SHIFT)
    assert li.DIAL_TOP - li.DM_BOTTOM >= li.DIAL_GAP  # the margins stay wider than the stack's own pitch

  @staticmethod
  def _settle(monkeypatch, frames=200):
    """LongIndicatorSP over a stub of upstream's _render that records the rect it is given and leaves the
    stack fully shown; returns (stack rects, dial draws)."""
    import raylib_nb as rl
    from openpilot.selfdrive.ui.mici.onroad.long_indicator import LongIndicator
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li

    stacks, dials = [], []
    def upstream_render(self, rect):
      stacks.append(rect)
      self._alpha_filter.x = self._dim_filter.x = 1.0
    monkeypatch.setattr(LongIndicator, "_render", upstream_render)
    monkeypatch.setattr(li, "draw_dial", lambda cx, top, **kw: dials.append((top, kw)))
    sp = li.LongIndicatorSP()
    for _ in range(frames):
      sp._render(rl.Rectangle(0, 0, 72, 240))
    return stacks, dials

  @pytest.mark.parametrize("speed_assist", [True, False])
  def test_stack_shifts_only_with_the_assist(self, params, monkeypatch, speed_assist):
    from openpilot.selfdrive.ui.sunnypilot.mici.onroad import long_indicator as li
    from openpilot.selfdrive.ui.ui_state import ui_state

    monkeypatch.setattr(ui_state, "speed_assist", speed_assist)
    stacks, dials = self._settle(monkeypatch)
    if speed_assist:
      assert stacks[-1].y == pytest.approx(li.STACK_SHIFT, abs=0.05)
      assert dials[-1][0] == pytest.approx(li.DIAL_TOP, abs=0.05) and dials[-1][1]["alpha"] == pytest.approx(1.0, abs=0.01)
    else:
      assert stacks[-1].y == pytest.approx(0.0) and dials[-1][1]["alpha"] == pytest.approx(0.0)

  def test_lift_fills_the_dial(self, params, monkeypatch):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    from openpilot.selfdrive.ui.ui_state import ui_state

    monkeypatch.setattr(ui_state, "speed_assist", True)
    monkeypatch.setattr(d, "lift_fraction", lambda: 0.75)
    _, dials = self._settle(monkeypatch, frames=300)
    assert dials[-1][1]["lift"] == pytest.approx(0.75, abs=0.01)

  @pytest.mark.parametrize(("has_long", "enabled", "expected"), [
    (True, True, 0.5),
    (True, False, 0.0),  # MADS lateral-only, or disengaged
    (False, True, 0.0),  # the car's own ACC
  ])
  def test_lift_only_while_openpilot_drives_longitudinal(self, params, monkeypatch, has_long, enabled, expected):
    from openpilot.selfdrive.ui.sunnypilot.onroad import speed_assist_dial as d
    from openpilot.selfdrive.ui.ui_state import ui_state
    from openpilot.sunnypilot.selfdrive.controls.lib.set_speed_assist import approach_ceiling

    standard = log.LongitudinalPersonality.standard
    lift = 0.5 * approach_ceiling(20., standard)
    monkeypatch.setattr(ui_state, "sm", FakeSubMaster({
      'selfdriveState': SimpleNamespace(enabled=enabled, personality=standard),
      'carState': SimpleNamespace(vEgo=20.),
      'longitudinalPlanSP': SimpleNamespace(setSpeedAssist=SimpleNamespace(lift=lift)),
    }))
    monkeypatch.setattr(ui_state, "started", True)
    monkeypatch.setattr(ui_state, "has_longitudinal_control", has_long)
    assert d.lift_fraction() == pytest.approx(expected)

  def test_dial_draws(self, params):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_dial import draw_dial
    for lift in (0.0, 0.005, 0.4, 1.0):
      draw_dial(36, 71, lift=lift)


class TestSpeedAssistQuickToggles:
  """The home footer shows the dial after the network icon, the home long press switches the assist, and so
  does the tizi onroad button."""

  def test_home_shows_speed_assist_after_network(self, params, monkeypatch):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.home import MiciHomeLayoutSP
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_badge import STATUS_ICON_HEIGHT
    from openpilot.selfdrive.ui.ui_state import ui_state

    home = MiciHomeLayoutSP()
    assert home._status_bar_layout.widgets[2] is home._speed_assist_icon
    # upstream's footer icons are 40 px of ink, and so is the dial's
    assert home._speed_assist_icon.rect.height == STATUS_ICON_HEIGHT
    for has_long, speed_assist, shown in ((True, True, True), (True, False, False), (False, True, False)):
      monkeypatch.setattr(ui_state, "has_longitudinal_control", has_long)
      monkeypatch.setattr(ui_state, "speed_assist", speed_assist)
      assert home._speed_assist_icon.is_visible == shown
    render(home)

  @staticmethod
  def _switches(params, monkeypatch, toggle):
    from openpilot.selfdrive.ui.ui_state import ui_state

    monkeypatch.setattr(ui_state, "has_longitudinal_control", True)
    for start in (True, False):
      ui_state.speed_assist = start
      toggle()
      assert params.get_bool("SetSpeedAssist") is (not start)
      assert ui_state.speed_assist is (not start)

    # no openpilot longitudinal, nothing to switch
    monkeypatch.setattr(ui_state, "has_longitudinal_control", False)
    params.put_bool("SetSpeedAssist", True)
    ui_state.speed_assist = True
    toggle()
    assert params.get_bool("SetSpeedAssist") and ui_state.speed_assist

  def test_home_long_press_switches_speed_assist(self, params, monkeypatch):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.home import MiciHomeLayoutSP
    self._switches(params, monkeypatch, MiciHomeLayoutSP()._long_press_callback)

  def test_onroad_button_switches_speed_assist(self, params, monkeypatch):
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_button import SpeedAssistButton
    button = SpeedAssistButton(192)
    self._switches(params, monkeypatch, lambda: button._handle_mouse_release(None))

  @pytest.mark.parametrize("speed_assist", [True, False])
  def test_onroad_button_draws(self, params, monkeypatch, speed_assist):
    import raylib_nb as rl
    from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_button import SpeedAssistButton
    from openpilot.selfdrive.ui.ui_state import ui_state

    monkeypatch.setattr(ui_state, "speed_assist", speed_assist)
    SpeedAssistButton(192).render(rl.Rectangle(0, 0, 192, 192))
