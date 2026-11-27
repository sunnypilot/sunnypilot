"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import time

import raylib_nb as rl

from openpilot.selfdrive.ui.mici.layouts.home import MiciHomeLayout
from openpilot.selfdrive.ui.ui_state import ui_state, ChestnutState
from openpilot.sunnypilot.system.connect_phone import phone_indicator, read_status
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.icon_widget import IconWidget
from openpilot.system.ui.widgets.label import UnifiedLabel

BT_POLL_SECONDS = 1.0
BT_WAITING_OPACITY = 0.35


class MiciHomeLayoutSP(MiciHomeLayout):
  def __init__(self):
    super().__init__()
    self._openpilot_label = UnifiedLabel("sunnypilot", font_size=88, font_weight=FontWeight.AUDIOWIDE, max_width=480, wrap_text=False)
    self._bluetooth_icon = IconWidget("../../sunnypilot/selfdrive/assets/offroad/icon_bluetooth.png", (40, 40))
    self._bluetooth_icon.set_visible(False)
    self._bt_polled_at = float("-inf")
    self._status_bar_layout.add_widget(self._bluetooth_icon)

  def _update_state(self):
    super()._update_state()
    now = time.monotonic()
    if now - self._bt_polled_at >= BT_POLL_SECONDS:
      self._bt_polled_at = now
      state = phone_indicator(read_status(ui_state.params))
      self._bluetooth_icon.set_visible(state != "hidden")
      self._bluetooth_icon.set_opacity(1.0 if state == "connected" else BT_WAITING_OPACITY)

  def _set_chestnut_visibility(self):
    usb_connected = ui_state.usb_connected
    usb_unknown = ui_state.usb_unknown
    chestnut_state = ui_state.chestnut_state
    loading = chestnut_state == ChestnutState.LOADING

    self._usb_icon.set_visible(usb_connected and usb_unknown)
    self._chestnut_loading_icon.set_opacity(0.35 + 0.65 * (0.5 - 0.5 * math.cos(rl.get_time() * 6.0)))
    self._chestnut_loading_icon.set_visible(not usb_unknown and loading)
    self._chestnut_icon.set_visible(not usb_unknown and not loading and
                                    chestnut_state in (ChestnutState.READY, ChestnutState.ACTIVE))
    self._chestnut_failed_icon.set_visible(not usb_unknown and chestnut_state in (ChestnutState.UNCOMPILED, ChestnutState.FAILED))
