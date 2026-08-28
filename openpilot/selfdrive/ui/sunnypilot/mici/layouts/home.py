"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.selfdrive.ui.mici.layouts.home import MiciHomeLayout
from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.icon_widget import IconWidget
from openpilot.system.ui.widgets.label import UnifiedLabel


class MiciHomeLayoutSP(MiciHomeLayout):
  def __init__(self):
    super().__init__()
    self._openpilot_label = UnifiedLabel("sunnypilot", font_size=88, font_weight=FontWeight.AUDIOWIDE, max_width=480, wrap_text=False)
    self._chestnut_loading_icon = IconWidget("icons_mici/chestnut.png", (68, 40))
    self._chestnut_loading_icon.set_visible(False)
    failed_idx = self._status_bar_layout.widgets.index(self._chestnut_failed_icon)
    self._status_bar_layout.widgets.insert(failed_idx + 1, self._chestnut_loading_icon)

  def _set_chestnut_visibility(self):
    # stock has no loading tier: it shows green from the moment a big model is available. keep the
    # pulse so the status bar and the onroad HUD agree on what loading looks like.
    loading = ui_state.chestnut_state == ChestnutState.LOADING
    self._chestnut_loading_icon._opacity = 0.35 + 0.65 * (0.5 - 0.5 * math.cos(rl.get_time() * 6.0))
    self._chestnut_loading_icon.set_visible(loading)
    self._chestnut_icon.set_visible(not loading and ui_state.chestnut_state in (ChestnutState.READY, ChestnutState.ACTIVE))
    self._chestnut_failed_icon.set_visible(ui_state.chestnut_state in (ChestnutState.UNCOMPILED, ChestnutState.FAILED))
