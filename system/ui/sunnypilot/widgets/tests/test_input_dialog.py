import os
import pytest

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.keyboard import Keyboard
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP

os.environ['SDL_VIDEODRIVER'] = 'dummy'
if not os.environ.get('CI'):
  pytest.skip("Test in CI environment, or comment out this flag to test locally", allow_module_level=True)


class TestInputDialog:
  def setup_method(self):
    self.params = Params()

  def test_input_dialog_int(self):
    gui_app.init_window("test window")
    dialog = InputDialogSP("title", current_text="current_text", param="MapTargetVelocities")
    dialog.show()

    dialog.keyboard._render_return_status = 1
    gui_app._handle_modal_overlay()

    assert self.params.get("MapTargetVelocities") == "current_text"

  def test_before_input_dialog(self):
    gui_app.init_window("test window")
    current_apn = "gsmapn"
    # This tests the pre InputDialogSP, where keyboard setup had to be done for every single dialog box you want to use.
    self.keyboard = Keyboard()
    self.keyboard.reset(min_text_size=0)
    self.keyboard.set_title(("Enter APN"), ("networking"))
    self.keyboard.set_text(current_apn)

    def pre_input_dialog_callback(result):
      if result == 1:
        apn = self.keyboard.text.strip()
        self.params.put("GsmApn", apn)

    gui_app.set_modal_overlay(self.keyboard, pre_input_dialog_callback)
    self.keyboard.set_text("new_apn")
    self.keyboard._render_return_status = 1
    gui_app._handle_modal_overlay()
    pre_input_dialog_result = self.params.get("GsmApn")

    assert pre_input_dialog_result == "new_apn"

    dialog = InputDialogSP(title="Enter APN", sub_title="networking", current_text=current_apn, param="GsmApn")
    dialog.show()
    dialog.keyboard.set_text("new_apn")
    dialog.keyboard._render_return_status = 1
    gui_app._handle_modal_overlay()
    input_dialog_result = self.params.get("GsmApn")

    assert input_dialog_result == "new_apn"
    assert pre_input_dialog_result == input_dialog_result
