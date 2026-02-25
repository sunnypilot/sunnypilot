from collections.abc import Callable

from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici
from openpilot.selfdrive.ui.mici.widgets.button import BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog, BigConfirmationDialogV2
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr


class DeviceLayoutMiciSP(DeviceLayoutMici):
  def __init__(self, back_callback: Callable):
    super().__init__(back_callback)

    self._enable_offroad = BigCircleButton("../../sunnypilot/selfdrive/assets/icons_mici/always_offroad.png",
                                                      red=True, icon_size=(120, 120))
    self._enable_offroad.set_click_callback(self._handle_always_offroad)

    self._disable_offroad = BigCircleButton("../../sunnypilot/selfdrive/assets/icons_mici/disable_offroad.png",
                                                      red=False, icon_size=(120, 120))
    self._disable_offroad.set_click_callback(self._handle_always_offroad)

    items = self._scroller._items.copy()

    items.insert(len(self._scroller._items) - 2, self._enable_offroad)
    items.insert(len(self._scroller._items) - 2, self._disable_offroad)

    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)

  def _handle_always_offroad(self):
    if ui_state.engaged:
      gui_app.set_modal_overlay(BigDialog(tr("disengage"),tr("\nto enable always offroad")))
      return

    def _enable_always_offroad():
      if not ui_state.engaged:
        ui_state.params.put_bool("OffroadMode", True)
        ui_state.always_offroad = True

    def _disable_always_offroad():
      ui_state.params.put_bool("OffroadMode", False)
      ui_state.always_offroad = False

    if ui_state.params.get_bool("OffroadMode"):
      dlg = BigConfirmationDialogV2(tr("slide to exit always offroad"), "icons_mici/settings/device/lkas.png",
                                  red=True, confirm_callback=_disable_always_offroad)
    else:
      dlg = BigConfirmationDialogV2(tr("slide to enable always offroad"), "icons_mici/settings/device/lkas.png",
                                  red=True, confirm_callback=_enable_always_offroad)
    gui_app.set_modal_overlay(dlg)

  def _update_state(self):
    super()._update_state()

    # Handle Always Offroad buttons
    always_offroad = ui_state.always_offroad
    self._enable_offroad.set_visible(not always_offroad)
    self._disable_offroad.set_visible(always_offroad)
