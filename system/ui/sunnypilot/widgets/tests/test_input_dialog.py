import os

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP


os.environ['SDL_VIDEODRIVER'] = 'dummy'

class TestInputDialog:
  def setup_method(self):
    self.params = Params()

  def test_input_dialog_int(self):
    gui_app.init_window("test window")
    dialog = InputDialogSP("title", current_text="current_text", param="MapTargetVelocities")  # some rando param, sorry sunny bc its your's
    dialog.show()

    dialog.keyboard._render_return_status = 1
    gui_app._handle_modal_overlay()

    assert self.params.get("MapTargetVelocities") == "current_text"
