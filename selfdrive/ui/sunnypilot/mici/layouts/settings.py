"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.cruise import CruiseLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.display import DisplayLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.steering import SteeringLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.trips import TripsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.visuals import VisualsLayoutMici
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr

SP_ICON = "../../sunnypilot/selfdrive/assets/offroad"


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    panels = [
      (tr("sunnylink"), SunnylinkLayoutMici, gui_app.texture("icons_mici/settings/developer/ssh.png", 56, 64)),
      (tr("models"),    ModelsLayoutMici,    gui_app.texture(f"{SP_ICON}/icon_models.png", 64, 64)),
      (tr("cruise"),    CruiseLayoutMici,    gui_app.texture(f"{SP_ICON}/icon_vehicle.png", 64, 64)),
      (tr("steering"),  SteeringLayoutMici,  gui_app.texture(f"{SP_ICON}/icon_lateral.png", 64, 64)),
      (tr("display"),   DisplayLayoutMici,   gui_app.texture(f"{SP_ICON}/icon_display.png", 64, 64)),
      (tr("visuals"),   VisualsLayoutMici,   gui_app.texture(f"{SP_ICON}/icon_visuals.png", 64, 64)),
      (tr("trips"),     TripsLayoutMici,     gui_app.texture(f"{SP_ICON}/icon_trips.png", 64, 64)),
    ]

    sp_buttons = []
    for label, panel_cls, icon in panels:
      panel = panel_cls()
      btn = SettingsBigButton(label, "", icon)
      btn.set_click_callback(lambda p=panel: gui_app.push_widget(p))
      sp_buttons.append(btn)

    items = self._scroller.items.copy()
    for i, btn in enumerate(sp_buttons):
      items.insert(1 + i, btn)
    self._scroller.items.clear()
    for item in items:
      self._scroller.add_widget(item)
