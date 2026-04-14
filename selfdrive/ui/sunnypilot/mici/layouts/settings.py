"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.system.ui.lib.application import gui_app

ICON_SIZE = 70


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    sunnylink_panel = SunnylinkLayoutMici(back_callback=gui_app.pop_widget)
    sunnylink_btn = BigButton("sunnylink", "", gui_app.texture("icons_mici/settings/developer/ssh.png", ICON_SIZE, ICON_SIZE))
    sunnylink_btn.set_click_callback(lambda: gui_app.push_widget(sunnylink_panel))

    models_panel = ModelsLayoutMici(back_callback=gui_app.pop_widget)
    models_btn = BigButton("models", "", gui_app.texture("../../sunnypilot/selfdrive/assets/offroad/icon_models.png", ICON_SIZE, ICON_SIZE))
    models_btn.set_click_callback(lambda: gui_app.push_widget(models_panel))

    items = self._scroller._items.copy()

    items.insert(1, sunnylink_btn)
    items.insert(2, models_btn)
    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)
