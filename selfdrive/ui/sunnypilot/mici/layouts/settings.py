"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog, BigDialog
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.cruise import CruiseLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.display import DisplayLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.steering import SteeringLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.trips import TripsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle import VehicleLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.visuals import VisualsLayoutMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr

ICON_SIZE = 70
BIG_ICON_SIZE = 110
SP_ICON = "../../sunnypilot/selfdrive/assets/offroad"


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    device_panel = DeviceLayoutMici()
    self._scroller._items[2].set_click_callback(lambda: gui_app.push_widget(device_panel))

    self.icon_offroad_enable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/always_offroad.png", BIG_ICON_SIZE, BIG_ICON_SIZE)
    self.icon_offroad_disable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/disable_offroad.png", BIG_ICON_SIZE, BIG_ICON_SIZE)
    self.icon_offroad_slider = gui_app.texture("icons_mici/settings/device/lkas.png", BIG_ICON_SIZE, BIG_ICON_SIZE)

    # onroad: enable button sits at the front (left of toggles)
    self._enable_offroad_btn_onroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_onroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_onroad.set_visible(lambda: ui_state.started and not ui_state.always_offroad)

    # offroad: enable button sits at the end (right of developer)
    self._enable_offroad_btn_offroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_offroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_offroad.set_visible(lambda: not ui_state.started and not ui_state.always_offroad)

    self._disable_offroad_btn = BigCircleButton(self.icon_offroad_disable, red=False)
    self._disable_offroad_btn.set_click_callback(lambda: self._handle_always_offroad(False))
    self._disable_offroad_btn.set_visible(lambda: ui_state.always_offroad)

    panels = [
      (tr("sunnylink"), SunnylinkLayoutMici, gui_app.texture("icons_mici/settings/developer/ssh.png", 56, 64)),
      (tr("models"),    ModelsLayoutMici,    gui_app.texture(f"{SP_ICON}/icon_models.png", 64, 64)),
      (tr("vehicle"),   VehicleLayoutMici,   gui_app.texture(f"{SP_ICON}/icon_vehicle.png", 64, 64)),
      (tr("cruise"),    CruiseLayoutMici,    gui_app.texture("icons/speed_limit.png", 64, 64)),
      (tr("steering"),  SteeringLayoutMici,  gui_app.texture(f"{SP_ICON}/icon_lateral.png", 64, 64)),
      (tr("display"),   DisplayLayoutMici,   gui_app.texture(f"{SP_ICON}/icon_display.png", 64, 64)),
      (tr("visuals"),   VisualsLayoutMici,   gui_app.texture(f"{SP_ICON}/icon_visuals.png", 64, 64)),
      (tr("trips"),     TripsLayoutMici,     gui_app.texture(f"{SP_ICON}/icon_trips.png", 64, 64)),
    ]

    sp_buttons = []
    for label, panel_cls, icon in panels:
      # use back_callback=gui_app.pop_widget to allow popping the widget from the stack
      panel = panel_cls(back_callback=gui_app.pop_widget) if label in [tr("sunnylink"), tr("models"), tr("vehicle")] else panel_cls()
      btn = SettingsBigButton(label, "", icon)
      btn.set_click_callback(lambda p=panel: gui_app.push_widget(p))
      sp_buttons.append(btn)

    items = self._scroller._items.copy()

    for i, btn in enumerate(sp_buttons):
      items.insert(1 + i, btn)

    # front slots (only one ever visible at a time): exit-always-offroad, then enable-onroad
    items.insert(0, self._enable_offroad_btn_onroad)
    items.insert(0, self._disable_offroad_btn)
    # end slot: enable-offroad (right of developer)
    items.append(self._enable_offroad_btn_offroad)

    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)

  def _update_state(self):
    super()._update_state()

  def _handle_always_offroad(self, enable: bool):

    def _set_offroad_status(status: bool):
      if not ui_state.engaged:
        ui_state.params.put_bool("OffroadMode", status)
        ui_state.always_offroad = status

    if not enable:
      dlg = BigConfirmationDialog(tr("slide to exit always offroad"), self.icon_offroad_slider, red=False,
                                  confirm_callback=lambda: _set_offroad_status(False))
    else:
      if ui_state.engaged:
        gui_app.push_widget(BigDialog(tr("disengage to enable always offroad"), "", ))
        return

      dlg = BigConfirmationDialog(tr("slide to force offroad"), self.icon_offroad_slider, red=True,
                                  confirm_callback=lambda: _set_offroad_status(True))
    gui_app.push_widget(dlg)
