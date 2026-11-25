"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import time

from openpilot.common.params import Params
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.connect_phone import ConnectPhoneLayout
from openpilot.sunnypilot.system.ble import grants
from openpilot.sunnypilot.system.connect_phone import write_request
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp, simple_button_item_sp, toggle_item_sp
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.list_view import text_item
from openpilot.system.ui.widgets.scroller_tici import Scroller

POLL_INTERVAL = 1.0


class BluetoothLayout(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()

    self._bluetooth_toggle = toggle_item_sp(
      title=lambda: tr("Bluetooth"),
      description=lambda: tr("Allow phones to connect to this device over Bluetooth."),
      param="BluetoothAllowed",
    )
    self._connect_phone_button = simple_button_item_sp(
      button_text=lambda: tr("Connect phone"),
      callback=lambda: gui_app.push_widget(ConnectPhoneLayout()),
      enabled=lambda: self._bluetooth_toggle.action_item.get_state(),
    )

    self._connected_header = text_item(title=lambda: tr("Connected phones"), value="")
    self._connected_header.set_visible(self._bluetooth_on)
    self._phone_items = []
    self._grants: list[dict] | None = None
    self._last_poll = float("-inf")

    self._scroller = Scroller([self._bluetooth_toggle, self._connect_phone_button, self._connected_header], line_separator=True, spacing=0)

  def _bluetooth_on(self) -> bool:
    return self._bluetooth_toggle.action_item.get_state()

  def _update_state(self):
    now = time.monotonic()
    if now - self._last_poll < POLL_INTERVAL:
      return
    self._last_poll = now
    phones = grants.load(self._params)
    if phones != self._grants:
      self._grants = phones
      self._rebuild_phone_items()

  def _rebuild_phone_items(self):
    for item in self._phone_items:
      self._scroller._items.remove(item)
    if self._grants:
      self._phone_items = [self._phone_item(phone) for phone in self._grants]
    else:
      self._phone_items = [text_item(title=lambda: tr("No phones connected yet"), value="")]
    for item in self._phone_items:
      item.set_visible(self._bluetooth_on)
      self._scroller.add_widget(item)

  def _phone_item(self, phone: dict):
    spki = phone["spki"]
    return button_item_sp(title=phone["name"], button_text=lambda: tr("REMOVE"), callback=lambda: self._remove(spki, phone["name"]))

  def _remove(self, spki: str, name: str):
    def done(result: DialogResult):
      if result == DialogResult.CONFIRM:
        write_request(self._params, "remove", phone=spki)
    gui_app.push_widget(ConfirmDialog(tr("Remove {}?").format(name), tr("Remove"), tr("Cancel"), callback=done))

  def _render(self, rect):
    self._scroller.render(rect)
