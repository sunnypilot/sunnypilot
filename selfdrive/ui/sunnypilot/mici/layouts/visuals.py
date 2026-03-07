"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigMultiParamToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import NavScroller


TOGGLE_PARAMS = [
  ("blind spot", "BlindSpot"),
  ("steering arc", "TorqueBar"),
  ("rainbow mode", "RainbowMode"),
  ("standstill timer", "StandstillTimer"),
  ("road name", "RoadNameToggle"),
  ("green light alert", "GreenLightAlert"),
  ("lead depart alert", "LeadDepartAlert"),
  ("true speed", "TrueVEgoUI"),
  ("hide speed", "HideVEgoUI"),
  ("turn signals", "ShowTurnSignals"),
  ("accel bar", "RocketFuel"),
]


class VisualsLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._prev_has_long: bool | None = None
    self._toggles: dict[str, BigParamControl] = {}
    items: list[Widget] = []
    for label, param in TOGGLE_PARAMS:
      toggle = BigParamControl(label, param)
      self._toggles[param] = toggle
      items.append(toggle)

    self._chevron_info = BigMultiParamToggle(
      "chevron info", "ChevronInfo",
      ["off", "dist", "speed", "time", "all"],
    )
    self._dev_ui_info = BigMultiParamToggle(
      "dev UI", "DevUIInfo",
      ["off", "bottom", "right", "R&B"],
    )
    items.append(self._chevron_info)
    items.append(self._dev_ui_info)

    self._scroller.add_widgets(items)

  def _update_state(self):
    super()._update_state()
    for _param, toggle in self._toggles.items():
      toggle.refresh()
    self._chevron_info.refresh()
    self._dev_ui_info.refresh()

    has_long = ui_state.has_longitudinal_control
    self._chevron_info.set_enabled(has_long)
    if not has_long and self._prev_has_long is True:
      ui_state.params.put("ChevronInfo", 0)
      self._chevron_info.refresh()
    self._prev_has_long = has_long
