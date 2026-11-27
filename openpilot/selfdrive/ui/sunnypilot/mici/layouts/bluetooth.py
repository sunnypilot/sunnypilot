"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time

from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.connect_phone import start_connect_phone
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.system.ble import grants
from openpilot.sunnypilot.system.connect_phone import display_name, write_request
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller

POLL_SECONDS = 1.0


def _phone_count(n: int) -> str:
  return tr("none connected") if n == 0 else tr("{} connected").format(n)


class BluetoothLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._bluetooth_on = ui_state.params.get_bool("BluetoothAllowed")

    def bluetooth_callback(checked: bool):
      self._bluetooth_on = checked

    self._bluetooth_toggle = BigParamControl(tr("bluetooth"), "BluetoothAllowed", toggle_callback=bluetooth_callback)

    self._connect_phone_btn = BigButton(tr("connect phone"), display_name(ui_state.params))
    self._connect_phone_btn.set_click_callback(start_connect_phone)
    self._connect_phone_btn.set_enabled(lambda: self._bluetooth_on)

    self._phones_page = ConnectedPhonesMici()
    self._phones_btn = BigButton(tr("phones"), "")
    self._phones_btn.set_click_callback(lambda: gui_app.push_widget(self._phones_page))
    self._phones_btn.set_visible(lambda: self._bluetooth_on)
    self._last_poll = float("-inf")

    self._scroller.add_widgets([self._bluetooth_toggle, self._connect_phone_btn, self._phones_btn])

  def _update_state(self):
    super()._update_state()
    now = time.monotonic()
    if now - self._last_poll >= POLL_SECONDS:
      self._last_poll = now
      self._phones_btn.set_value(_phone_count(len(grants.load(ui_state.params))))


class ConnectedPhonesMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._phone_items: list[BigButton] = []
    self._grants: list[dict] | None = None
    self._last_poll = float("-inf")

  def _update_state(self):
    super()._update_state()
    now = time.monotonic()
    if now - self._last_poll < POLL_SECONDS:
      return
    self._last_poll = now
    phones = grants.load(ui_state.params)
    if phones != self._grants:
      self._grants = phones
      for item in self._phone_items:
        self._scroller._items.remove(item)
      self._phone_items = [self._phone_item(phone) for phone in phones] or [BigButton(tr("no phones connected yet"), "")]
      self._scroller.add_widgets(self._phone_items)

  def _phone_item(self, phone: dict) -> BigButton:
    spki = phone["spki"]
    item = BigButton(phone["name"], tr("remove"), scroll=True)
    item.set_click_callback(lambda: self._remove(spki))
    return item

  def _remove(self, spki: str) -> None:
    icon = gui_app.texture("icons_mici/settings/network/new/trash.png", 54, 64)
    gui_app.push_widget(BigConfirmationDialog(tr("slide to remove"), icon, lambda: write_request(ui_state.params, "remove", phone=spki), red=True))
