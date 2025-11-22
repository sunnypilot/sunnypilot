import pyray as rl
from collections.abc import Callable
from cereal import log

from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigMultiParamToggle
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import NavWidget
from openpilot.selfdrive.ui.layouts.settings.common import restart_needed_callback
from openpilot.selfdrive.ui.ui_state import ui_state



class SunnylinkLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)

    self._sunnylink_toggle = BigParamControl("enable sunnylink", "SunnylinkEnabled")

    self._scroller = Scroller([
      self._sunnylink_toggle
    ], snap_items=True)

    # Toggle lists
    self._refresh_toggles = (
      ("SunnylinkEnabled", self._sunnylink_toggle),
    )

  def _update_state(self):
    super()._update_state()

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    self._update_toggles()

  def _update_toggles(self):
    ui_state.update_params()

    # Refresh toggles from params to mirror external changes
    for key, item in self._refresh_toggles:
      item.set_checked(ui_state.params.get_bool(key))

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)
