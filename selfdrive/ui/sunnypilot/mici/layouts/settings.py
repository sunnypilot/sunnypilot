"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum

from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici

ICON_SIZE = 70

OP.PanelType = IntEnum(
  "PanelType",
  [es.name for es in OP.PanelType] + [
    "SUNNYLINK",
    "MODELS",
  ],
  start=0,
)


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    sunnylink_btn = BigButton("sunnylink", "", "icons_mici/settings/developer/ssh.png")
    sunnylink_btn.set_click_callback(lambda: self._set_current_panel(OP.PanelType.SUNNYLINK))

    models_btn = BigButton("models", "", "../../sunnypilot/selfdrive/assets/offroad/icon_models.png")
    models_btn.set_click_callback(lambda: self._set_current_panel(OP.PanelType.MODELS))

    self._panels.update({
      OP.PanelType.SUNNYLINK: OP.PanelInfo("sunnylink", SunnylinkLayoutMici(back_callback=lambda: self._set_current_panel(None))),
      OP.PanelType.MODELS: OP.PanelInfo("models", ModelsLayoutMici(back_callback=lambda: self._set_current_panel(None))),
    })

    items = self._scroller._items.copy()

    items.insert(1, sunnylink_btn)
    items.insert(2, models_btn)
    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)
