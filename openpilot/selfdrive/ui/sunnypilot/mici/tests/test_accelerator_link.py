"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# The models panel's accelerator link, picker and status line, and the home-screen icon state.

import os

import pytest

os.environ["BIG"] = "0"
os.environ.setdefault("SCALE", "1")


@pytest.fixture(scope="module")
def gui():
  """Hidden raylib window + isolated params dir. Widgets need textures, so a window is required."""
  import pyray as rl
  from openpilot.common.prefix import OpenpilotPrefix

  with OpenpilotPrefix():
    rl.set_config_flags(rl.FLAG_WINDOW_HIDDEN)
    from openpilot.system.ui.lib.application import gui_app
    gui_app.init_window("test_accelerator_link", fps=30)
    yield gui_app
    gui_app.close()


@pytest.fixture
def params(gui):
  from openpilot.common.params import Params
  from openpilot.selfdrive.ui.ui_state import ui_state

  p = Params()
  ui_state.params = p
  # on device update_params() runs every frame before anything draws, so attributes it
  # sets (always_offroad, screensaver_enabled, ...) exist by render time. Without this a
  # layout reading one of them fails in the test for a reason the device never sees.
  ui_state.update_params()
  return p


def render(widget):
  """Drive one frame through Widget.render, which calls _update_state."""
  import pyray as rl
  widget.render(rl.Rectangle(0, 0, 800, 600))


def wait_for_param(params, key, timeout=2.0):
  """Widgets write with a non-blocking put(), which lands on a background thread."""
  import time
  deadline = time.monotonic() + timeout
  last = params.get(key)
  while time.monotonic() < deadline:
    time.sleep(0.005)
    val = params.get(key)
    if val != last:
      return val
    last = val
  return last


class TestAcceleratorProgressRenders:
  """The models panel's provisioning line.

  Provisioning an accelerator is an upload plus a build, minutes long, and this
  is the only place a user sees it happening. The layout sweep above runs with
  no progress set, so none of these branches is covered by it.
  """

  STAGES = ['download', 'connect', 'upload', 'build', 'failed']

  def _info(self, stage, frac):
    from openpilot.selfdrive.ui.ui_state import ui_state
    ui_state.accelerator_progress = {'stage': stage, 'frac': frac, 'msg': ''}
    try:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import _model_info
      return _model_info()
    finally:
      ui_state.accelerator_progress = None

  @pytest.mark.parametrize("stage", STAGES)
  def test_every_stage_gives_a_line(self, params, stage):
    active, header, info = self._info(stage, 0.42)
    assert active and header and info

  def test_a_percentage_is_shown_while_working(self, params):
    _, _, info = self._info('download', 0.42)
    assert '42%' in info

  def test_a_message_is_shown_instead_of_a_percentage_that_means_nothing(self, params):
    # A join has nothing to measure: it is waiting for a Jetson to boot, or
    # for a safe frame to swap on. Rendering that as "connect 0%" tells the
    # driver nothing, and "getting ready" alone does not separate a Jetson
    # that is unplugged from one six seconds from ready.
    from openpilot.selfdrive.ui.ui_state import ui_state
    ui_state.accelerator_progress = {'stage': 'connect', 'frac': 0.0, 'msg': 'waiting for the jetson'}
    try:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import _model_info
      _, _, info = _model_info()
    finally:
      ui_state.accelerator_progress = None
    assert 'waiting for the jetson' in info
    assert '%' not in info

  def test_failure_says_so_rather_than_showing_100_percent(self, params):
    _, _, info = self._info('failed', 1.0)
    assert '100%' not in info

  def test_ready_falls_back_to_the_normal_line(self, params):
    # 'ready' is the steady state: the panel must go back to naming the model,
    # not sit on a finished progress bar forever.
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts import models as models_layout
    ready = self._info('ready', 1.0)
    from openpilot.selfdrive.ui.ui_state import ui_state
    ui_state.accelerator_progress = None
    assert ready == models_layout._model_info()

  @pytest.mark.parametrize("stage", STAGES)
  def test_the_panel_draws_with_progress_set(self, params, stage):
    from openpilot.selfdrive.ui.ui_state import ui_state
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici

    ui_state.accelerator_progress = {'stage': stage, 'frac': 0.5, 'msg': ''}
    try:
      layout = ModelsLayoutMici()
      render(layout)
      render(layout)
      for item in layout._scroller.items:
        render(item)
      render(layout.current_model_info)
    finally:
      ui_state.accelerator_progress = None


class TestAcceleratorIconState:
  """The home screen and sidebar draw ui_state.chestnut_state. For a backend
  the comma is the USB gadget for, the state has to come from the accelerator
  view and the progress param, not from a USB id the comma will never enumerate.
  A fitted chestnut keeps upstream's state machine untouched."""

  class FakeSM:
    def __init__(self, big=False, alive=False, recv=0):
      self.recv_frame = {"modelV2": recv}
      self.alive = {"modelV2": alive}
      self.big = big

    def __getitem__(self, name):
      if name == "deviceState":
        return type("DS", (), {"chestnutPresent": False})()
      assert name == "modelV2"
      return type("M", (), {"big": self.big})()

  @staticmethod
  def _view(present=True, ready=False, progress=None, state='none'):
    from openpilot.selfdrive.ui.sunnypilot.ui_state import AcceleratorView
    return AcceleratorView(present, ready, progress, True, state)

  def _state(self, view, sm=None, started=False):
    from openpilot.selfdrive.ui.ui_state import ui_state
    saved = ui_state.sm, ui_state.started, ui_state.started_frame, ui_state.accelerator_view
    ui_state.sm, ui_state.started, ui_state.started_frame = sm or self.FakeSM(), started, 0
    ui_state.accelerator_view = view
    try:
      ui_state._update_chestnut_state()
      return ui_state.chestnut_state
    finally:
      ui_state.sm, ui_state.started, ui_state.started_frame, ui_state.accelerator_view = saved

  def test_offroad_states(self, params):
    from openpilot.selfdrive.ui.ui_state import ChestnutState
    assert self._state(self._view(present=False)) == ChestnutState.DISCONNECTED
    assert self._state(self._view(ready=True)) == ChestnutState.READY
    assert self._state(self._view()) == ChestnutState.UNCOMPILED
    assert self._state(self._view(progress={'stage': 'build', 'frac': 0.3})) == ChestnutState.LOADING
    assert self._state(self._view(progress={'stage': 'failed', 'frac': 1.0})) == ChestnutState.FAILED
    assert self._state(self._view(ready=True, progress={'stage': 'connect', 'frac': 0.0})) == ChestnutState.LOADING
    assert self._state(self._view(ready=True, progress={'stage': 'failed', 'frac': 1.0})) == ChestnutState.FAILED
    assert self._state(self._view(ready=True, progress={'stage': 'ready', 'frac': 1.0})) == ChestnutState.READY

  def test_absent_accelerator_does_not_pulse_onroad(self, params):
    from openpilot.selfdrive.ui.ui_state import ChestnutState
    view = self._view(present=False, ready=True, state='retrying')
    assert self._state(view, self.FakeSM(alive=True, recv=1), started=True) == ChestnutState.DISCONNECTED

  def test_onroad_states(self, params):
    from openpilot.selfdrive.ui.ui_state import ChestnutState
    driving = self.FakeSM(alive=True, recv=1)
    assert self._state(self._view(ready=True, state='joining'), driving, started=True) == ChestnutState.LOADING
    assert self._state(self._view(ready=True, state='retrying'), driving, started=True) == ChestnutState.LOADING
    assert self._state(self._view(ready=True, state='running'), driving, started=True) == ChestnutState.ACTIVE
    assert self._state(self._view(ready=True, state='unavailable'), driving, started=True) == ChestnutState.FAILED
    assert self._state(self._view(ready=False, state='none'), driving, started=True) == ChestnutState.UNCOMPILED
    # nothing from modeld yet is loading, not failed
    assert self._state(self._view(ready=True), self.FakeSM(), started=True) == ChestnutState.LOADING
    # a big frame is proof, whatever the status field says
    big = self.FakeSM(big=True, alive=True, recv=1)
    assert self._state(self._view(ready=True, state='unavailable'), big, started=True) == ChestnutState.ACTIVE


class TestAcceleratorModelSelection:
  def test_selection_does_not_write_model_manager_slots(self, params):
    from unittest import mock
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici

    choice = {'name': 'Cinque Terre', 'selected': False, 'cached': True}
    layout = ModelsLayoutMici()
    with mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.accelerators.select_model') as select, \
         mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.ui_state.is_offroad', return_value=True), \
         mock.patch.object(layout, '_pop_to_main'), mock.patch.object(params, 'put') as put:
      layout._choose_accelerator(choice)
      select.assert_called_once_with('Cinque Terre')
      put.assert_not_called()

  def test_selection_that_crosses_ignition_does_not_change_the_model(self, params):
    from unittest import mock
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici

    layout = ModelsLayoutMici()
    with mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.accelerators.select_model') as select, \
         mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.ui_state.is_offroad', return_value=False):
      layout._choose_accelerator({'name': 'Cinque Terre'})
      select.assert_not_called()

  @staticmethod
  def _usb(present):
    from contextlib import ExitStack
    from unittest import mock
    from openpilot.selfdrive.ui import ui_state as module
    stack = ExitStack()
    stack.enter_context(mock.patch.object(module, 'read_int', return_value=1))
    stack.enter_context(mock.patch.object(module, 'get_usb_state', return_value=[]))
    stack.enter_context(mock.patch("openpilot.sunnypilot.accelerators.present", return_value=present))
    return stack

  def test_a_present_accelerator_is_not_an_unknown_usb_device(self, params):
    import time
    from openpilot.selfdrive.ui.ui_state import ui_state
    saved = ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown, ui_state.accelerator_view
    try:
      ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown = True, time.monotonic() - 11.0, False
      with self._usb(present=True):
        ui_state.update_params()  # builds the view
        ui_state.usb_connected_ts = time.monotonic() - 11.0
        ui_state.update_params()  # decides
      assert ui_state.accelerator_view is not None
      assert ui_state.usb_unknown is False
      with self._usb(present=False):
        ui_state.update_params()
        ui_state.usb_connected_ts = time.monotonic() - 11.0
        ui_state.update_params()
      assert ui_state.accelerator_view is None
      assert ui_state.usb_unknown is True
    finally:
      ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown, ui_state.accelerator_view = saved

  def test_an_accelerator_recognised_after_the_grace_period_clears_unknown(self, params):
    """The cable is seen from power-on but the Jetson configures the gadget
    ~25 s after the UI starts, so the one-shot decision has already said
    "unknown" by then. Presence arriving later must still clear it."""
    from openpilot.selfdrive.ui.ui_state import ui_state
    saved = ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown, ui_state.accelerator_view
    try:
      ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown = True, None, True
      with self._usb(present=False):
        ui_state.update_params()
        assert ui_state.usb_unknown is True
      with self._usb(present=True):
        ui_state.update_params()
        assert ui_state.usb_unknown is False
    finally:
      ui_state.usb_connected, ui_state.usb_connected_ts, ui_state.usb_unknown, ui_state.accelerator_view = saved


class TestAcceleratorLinkToggle:
  """The models panel's on / off control over the accelerator link.

  On is the only enable, and the control is hidden on a device it means nothing
  to: a plain comma must not grow a setting for hardware it will never see.
  """

  PARAM = "JetlinkEnabled"

  @staticmethod
  def _accelerators(present=False, ready=False, reason=None):
    from contextlib import ExitStack
    from unittest import mock

    stack = ExitStack()
    stack.enter_context(mock.patch("openpilot.sunnypilot.accelerators.present", return_value=present))
    stack.enter_context(mock.patch("openpilot.sunnypilot.accelerators.ready", return_value=ready))
    stack.enter_context(mock.patch("openpilot.sunnypilot.accelerators.unavailable_reason", return_value=reason))
    return stack

  def _meaningful(self, **accelerators) -> bool:
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import link_toggle_meaningful
    with self._accelerators(**accelerators):
      return link_toggle_meaningful()

  def test_hidden_on_a_plain_device(self, params):
    params.remove(self.PARAM)
    assert not self._meaningful()

  def test_shown_when_an_accelerator_is_attached(self, params):
    params.remove(self.PARAM)
    assert self._meaningful(present=True)

  def test_shown_when_ready_with_the_hardware_out_of_the_car(self, params):
    # the engine is cached and the link may be on, so modeld will still try it at
    # the next ignition. this is the case the off position exists for
    params.remove(self.PARAM)
    assert self._meaningful(ready=True)

  def test_shown_when_the_backend_has_a_complaint(self, params):
    params.remove(self.PARAM)
    assert self._meaningful(reason="no gadget")

  def test_shown_once_the_user_has_turned_it_on(self, params):
    params.put_bool(self.PARAM, True, block=True)
    assert self._meaningful()

  def test_hidden_when_off_with_nothing_attached(self, params):
    params.put_bool(self.PARAM, False, block=True)
    assert not self._meaningful()

  def test_absent_reads_as_off(self, params):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import link_enabled

    params.remove(self.PARAM)
    assert link_enabled() is False
    params.put_bool(self.PARAM, True, block=True)
    assert link_enabled() is True
    params.put_bool(self.PARAM, False, block=True)
    assert link_enabled() is False

  def test_tap_toggles_on_and_off(self, params):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import AcceleratorLinkToggle
    from openpilot.system.ui.lib.application import MousePos

    params.remove(self.PARAM)
    params.put("ModelRunnerTypeCache", 1)
    toggle = AcceleratorLinkToggle()
    assert not toggle._checked
    toggle._handle_mouse_release(MousePos(0, 0))
    assert params.get(self.PARAM) is True
    assert params.get("ModelRunnerTypeCache") is None, "the link decides which modeld manager runs"
    toggle._handle_mouse_release(MousePos(0, 0))
    assert params.get(self.PARAM) is False

  def test_refresh_follows_the_param(self, params):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import AcceleratorLinkToggle

    params.remove(self.PARAM)
    toggle = AcceleratorLinkToggle()
    params.put_bool(self.PARAM, True, block=True)
    toggle.refresh()
    assert toggle._checked

  def test_link_toggle_cannot_change_runner_after_ignition(self, params):
    from unittest import mock
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import AcceleratorLinkToggle

    params.remove(self.PARAM)
    toggle = AcceleratorLinkToggle()
    with mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.ui_state.is_offroad', return_value=False), \
         mock.patch('openpilot.selfdrive.ui.sunnypilot.mici.layouts.models.set_link_enabled') as write:
      toggle._store(True)
      write.assert_not_called()
    assert params.get(self.PARAM) is None
    assert not toggle._checked, "the pill must not show a state the param does not have"

  def test_layout_hides_the_toggle_until_it_means_something(self, params):
    from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici

    params.remove(self.PARAM)
    with self._accelerators():
      layout = ModelsLayoutMici()
      assert not layout.link_toggle.is_visible
      assert layout.link_toggle in layout._scroller.items
    with self._accelerators(present=True):
      layout = ModelsLayoutMici()
      assert layout.link_toggle.is_visible
      render(layout)
      render(layout)
      render(layout.link_toggle)
