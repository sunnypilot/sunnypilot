"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# ui_state's accelerator view beside upstream's chestnut state, and the tici
# models panel's link toggle and accelerator picker.

import os
from contextlib import ExitStack
from unittest import mock

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
    gui_app.init_window("test_accelerator_ui", fps=30)
    yield gui_app
    gui_app.close()


@pytest.fixture
def params(gui):
  from openpilot.common.params import Params
  from openpilot.selfdrive.ui.ui_state import ui_state

  p = Params()
  ui_state.params = p
  ui_state.update_params()
  return p


def accelerator(present=False, ready=False, progress=None, stock=False, choices=None):
  stack = ExitStack()
  for name, value in (("present", present), ("ready", ready), ("progress", progress),
                      ("uses_stock_runner", stock), ("model_choices", choices or []),
                      ("unavailable_reason", None)):
    stack.enter_context(mock.patch(f"openpilot.sunnypilot.accelerators.{name}", return_value=value))
  return stack


class FakeSM:
  def __init__(self, board, big=False, alive=False, recv=0, state='none'):
    self.board = board
    self.recv_frame = {"modelV2": recv}
    self.alive = {"modelV2": alive}
    self.big = big
    self.state = state

  def __getitem__(self, name):
    if name == "deviceState":
      return type("DS", (), {"chestnutPresent": self.board})()
    if name == "modelDataV2SP":
      return type("SP", (), {"acceleratorState": self.state})()
    assert name == "modelV2"
    return type("M", (), {"big": self.big})()


class TestUIStateAcceleratorView:
  @staticmethod
  def _with(sm, started=False):
    from openpilot.selfdrive.ui.ui_state import ui_state
    saved = ui_state.sm, ui_state.started, ui_state.started_frame, ui_state.accelerator_view, ui_state.chestnut_present
    ui_state.sm, ui_state.started, ui_state.started_frame = sm, started, 0
    ui_state.chestnut_present = sm.board
    return saved

  @staticmethod
  def _restore(saved):
    from openpilot.selfdrive.ui.ui_state import ui_state
    ui_state.sm, ui_state.started, ui_state.started_frame, ui_state.accelerator_view, ui_state.chestnut_present = saved

  def test_a_fitted_chestnut_never_asks_the_accelerator(self, params):
    """A board present is upstream's path byte for byte: no view, and nothing in the
    state update consults sunnypilot/accelerators."""
    from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
    saved = self._with(FakeSM(board=True))
    try:
      with accelerator(present=True, ready=True, stock=True):
        ui_state.update_params()
      assert ui_state.accelerator_view is None
      ui_state.chestnut_compiled = True
      with mock.patch("openpilot.sunnypilot.accelerators.present", side_effect=AssertionError("consulted")), \
           mock.patch("openpilot.sunnypilot.accelerators.ready", side_effect=AssertionError("consulted")):
        ui_state._update_chestnut_state()
      assert ui_state.chestnut_state == ChestnutState.READY
    finally:
      self._restore(saved)

  def test_no_board_and_nothing_of_ours_is_no_view(self, params):
    from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
    saved = self._with(FakeSM(board=False))
    try:
      with accelerator():
        ui_state.update_params()
      assert ui_state.accelerator_view is None
      ui_state._update_chestnut_state()
      assert ui_state.chestnut_state == ChestnutState.DISCONNECTED
    finally:
      self._restore(saved)

  def test_an_attached_accelerator_builds_the_view(self, params):
    from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
    saved = self._with(FakeSM(board=False))
    try:
      with accelerator(present=True, ready=True, stock=True):
        ui_state.update_params()
      view = ui_state.accelerator_view
      assert view is not None and view.present and view.ready and view.uses_stock_runner
      ui_state._update_chestnut_state()
      assert ui_state.chestnut_state == ChestnutState.READY
    finally:
      self._restore(saved)

  def test_a_bundle_that_is_not_running_does_not_read_compiled(self, params):
    """Under the accelerator override manager runs stock modeld, so a stored tinygrad
    bundle must not make the icon say the big model is ready."""
    from openpilot.selfdrive.ui.ui_state import ui_state
    from openpilot.sunnypilot.models.helpers import ACTIVE_BUNDLE_KEYS
    saved = self._with(FakeSM(board=False))
    compiled, real = ui_state.chestnut_compiled, ui_state.params
    # served from a wrapper rather than written: the model manager's validation
    # discards a bundle it cannot resolve, from whatever thread reaches it first
    fake = mock.Mock(wraps=real)
    fake.get.side_effect = lambda key, *a, **k: {"runner": "tinygrad"} if key == ACTIVE_BUNDLE_KEYS["qcom"] else real.get(key, *a, **k)
    try:
      ui_state.chestnut_compiled = False
      ui_state.params = fake
      with accelerator(present=True, stock=True):
        ui_state.update_params()
      assert ui_state.model_runner_tinygrad
      assert ui_state.chestnut_compiled is False
      with accelerator(present=True, stock=False):
        ui_state.update_params()
      assert ui_state.chestnut_compiled is True
    finally:
      ui_state.params = real
      ui_state.chestnut_compiled = compiled
      self._restore(saved)

  def test_onroad_disconnected_then_active(self, params):
    from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
    saved = self._with(FakeSM(board=False, alive=True, recv=1, state='retrying'), started=True)
    try:
      with accelerator(present=False, ready=True, stock=True):
        ui_state.update_params()
      assert ui_state.accelerator_view is not None
      ui_state._update_chestnut_state()
      assert ui_state.chestnut_state == ChestnutState.DISCONNECTED

      ui_state.sm = FakeSM(board=False, big=True, alive=True, recv=1, state='running')
      with accelerator(present=True, ready=True, stock=True):
        ui_state.update_params()
      ui_state._update_chestnut_state()
      assert ui_state.chestnut_state == ChestnutState.ACTIVE
    finally:
      self._restore(saved)

  def test_the_status_name_is_read_where_sm_updates(self, params):
    from openpilot.selfdrive.ui.sunnypilot.ui_state import UIStateSP
    from openpilot.selfdrive.ui.ui_state import ui_state
    saved = self._with(FakeSM(board=False, state='joining'))
    try:
      UIStateSP.update(ui_state)
      with accelerator(present=True):
        ui_state.update_params()
      assert ui_state.accelerator_view.state == 'joining'
    finally:
      self._restore(saved)


class TestTiciModelsPanel:
  CHOICES = [{'name': 'Cinque Terre', 'selected': True, 'cached': True},
             {'name': 'Lebowski', 'selected': False, 'cached': False}]

  @staticmethod
  def _layout():
    from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
    return ModelsLayout()

  def test_hidden_on_a_plain_device(self, params):
    with accelerator():
      layout = self._layout()
    assert not layout.accelerator_link_item.is_visible
    assert not layout.accelerator_model_item.is_visible

  def test_shown_with_an_accelerator(self, params):
    with accelerator(present=True, choices=self.CHOICES):
      layout = self._layout()
    assert layout.accelerator_link_item.is_visible
    assert layout.accelerator_model_item.is_visible

  def test_toggle_writes_the_param_and_drops_the_runner_cache(self, params):
    params.put("ModelRunnerTypeCache", 1)
    with accelerator(present=True), mock.patch.object(ui_state_module().ui_state, "is_offroad", return_value=True):
      layout = self._layout()
      layout._set_link_state(True)
      assert params.get_bool("JetlinkEnabled") is True
      assert params.get("ModelRunnerTypeCache") is None
      layout._set_link_state(False)
      assert params.get_bool("JetlinkEnabled") is False

  def test_toggle_is_inert_onroad(self, params):
    params.remove("JetlinkEnabled")
    with accelerator(present=True), mock.patch.object(ui_state_module().ui_state, "is_offroad", return_value=False):
      layout = self._layout()
      layout._set_link_state(True)
      assert params.get("JetlinkEnabled") is None
      assert layout.accelerator_link_item.action_item.get_state() is False

  def test_picker_selects_through_the_module_api(self, params):
    from openpilot.system.ui.widgets import DialogResult
    with accelerator(present=True, choices=self.CHOICES), \
         mock.patch("openpilot.sunnypilot.accelerators.select_model") as select, \
         mock.patch.object(ui_state_module().ui_state, "is_offroad", return_value=True), \
         mock.patch("openpilot.system.ui.lib.application.gui_app.push_widget"):
      layout = self._layout()
      layout._open_accelerator_dialog()
      assert layout.accelerator_dialog is not None
      layout.accelerator_dialog.selection = 'Lebowski'
      layout._on_accelerator_selected(DialogResult.CONFIRM)
      select.assert_called_once_with('Lebowski')
      assert params.get("ModelManager_DownloadRef") is None

  def test_picker_is_inert_onroad(self, params):
    from openpilot.system.ui.widgets import DialogResult
    with accelerator(present=True, choices=self.CHOICES), \
         mock.patch("openpilot.sunnypilot.accelerators.select_model") as select, \
         mock.patch.object(ui_state_module().ui_state, "is_offroad", return_value=False), \
         mock.patch("openpilot.system.ui.lib.application.gui_app.push_widget"):
      layout = self._layout()
      layout._open_accelerator_dialog()
      layout.accelerator_dialog.selection = 'Lebowski'
      layout._on_accelerator_selected(DialogResult.CONFIRM)
      select.assert_not_called()

  def test_status_note_names_the_accelerator_not_the_chestnut(self, params):
    from openpilot.selfdrive.ui.sunnypilot.ui_state import AcceleratorView
    ui_state = ui_state_module().ui_state
    saved = ui_state.accelerator_view, ui_state.chestnut_present
    try:
      ui_state.chestnut_present = False
      with accelerator(present=True, choices=self.CHOICES), \
           mock.patch("openpilot.selfdrive.ui.sunnypilot.layouts.settings.models.big_model_state", return_value=None):
        layout = self._layout()
        ui_state.accelerator_view = AcceleratorView(True, False, None, True, 'none')
        note = layout._status_note()
        assert "chestnut" not in note
        assert "Cinque Terre will drive when the accelerator is ready." == note
        ui_state.accelerator_view = AcceleratorView(True, True, None, True, 'none')
        note = layout._status_note()
        assert note.startswith("Cinque Terre will drive.") and "chestnut" not in note
    finally:
      ui_state.accelerator_view, ui_state.chestnut_present = saved

  def test_panel_renders(self, params):
    import pyray as rl
    with accelerator(present=True, choices=self.CHOICES):
      layout = self._layout()
      layout.render(rl.Rectangle(0, 0, 800, 600))


def ui_state_module():
  from openpilot.selfdrive.ui import ui_state
  return ui_state
