"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import threading
import time
import pyray as rl

from openpilot.selfdrive.ui.lib.prime_state import PrimeType
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.lib.wifi_manager import WifiManagerSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.network import AdvancedNetworkSettings, NetworkUI, PanelType, NavButton, WifiManagerUI


class AdvancedNetworkSettingsSP(AdvancedNetworkSettings):
  def __init__(self, wifi_manager: WifiManagerSP):
    super().__init__(wifi_manager)
    self._share_internet_state = False
    self._last_share_internet_sync = 0.0
    self._can_cleanup_stale_nat = False
    self._share_internet_toggle = toggle_item_sp(
      tr("Use Legacy NAT"),
      tr("Uses an iptables-legacy NAT rule as a fallback when hotspot internet sharing does not work correctly."),
      initial_state=self._share_internet_state,
      callback=self._toggle_tethering_internet_sharing,
      enabled=False,
    )
    self._share_internet_toggle.set_touch_valid_callback(self._scroller.scroll_panel.is_touch_valid)
    self._scroller._items.insert(1, self._share_internet_toggle)
    self._sync_share_internet_toggle()

  def _on_network_updated(self, networks):
    super()._on_network_updated(networks)
    self._can_cleanup_stale_nat = True
    self._sync_share_internet_toggle(sync_state=True)

  def _update_state(self):
    super()._update_state()
    tethering_active = self._wifi_manager.is_tethering_active()
    show_cell_settings = ui_state.prime_state.get_type() in (PrimeType.NONE, PrimeType.LITE)
    should_sync = tethering_active and show_cell_settings and time.monotonic() - self._last_share_internet_sync >= 5.0
    self._sync_share_internet_toggle(sync_state=should_sync)

  def _sync_share_internet_toggle(self, sync_state: bool = False):
    tethering_active = self._wifi_manager.is_tethering_active()
    show_cell_settings = ui_state.prime_state.get_type() in (PrimeType.NONE, PrimeType.LITE)
    nat_eligible = tethering_active and show_cell_settings

    self._share_internet_toggle.set_visible(nat_eligible)
    self._share_internet_toggle.action_item.set_enabled(nat_eligible)

    if not sync_state:
      if not nat_eligible and self._share_internet_state:
        self._wifi_manager.set_tethering_internet_shared(False)
      if not nat_eligible:
        self._share_internet_state = False
      self._share_internet_toggle.action_item.set_state(self._share_internet_state)
      return

    self._last_share_internet_sync = time.monotonic()

    if nat_eligible:
      self._share_internet_state = self._wifi_manager.is_tethering_internet_shared()
    else:
      if self._can_cleanup_stale_nat and self._wifi_manager.is_tethering_internet_shared():
        self._wifi_manager.set_tethering_internet_shared(False)
      self._share_internet_state = False
    self._share_internet_toggle.action_item.set_state(self._share_internet_state)

  def _toggle_tethering_internet_sharing(self, enabled: bool):
    self._wifi_manager.set_tethering_internet_shared(enabled)
    self._sync_share_internet_toggle(sync_state=True)


class NetworkUISP(NetworkUI):
  def __init__(self, wifi_manager):
    Widget.__init__(self)
    self._wifi_manager = wifi_manager
    self._current_panel: PanelType = PanelType.WIFI
    self._wifi_panel = self._child(WifiManagerUI(wifi_manager))
    self._advanced_panel = self._child(AdvancedNetworkSettingsSP(wifi_manager))
    self._nav_button = self._child(NavButton(tr("Advanced")))
    self._nav_button.set_click_callback(self._cycle_panel)

    self.scan_button = Button(tr("Scan"), self._scan_clicked, button_style=ButtonStyle.NORMAL, font_size=60, border_radius=30)
    self.scan_button.set_rect(rl.Rectangle(0, 0, 400, 100))

    self._scanning = False
    self._wifi_manager.add_callbacks(networks_updated=self._on_networks_updated)

  def _scan_clicked(self):
    self._scanning = True
    self.scan_button.set_text(tr("Scanning..."))
    self.scan_button.set_enabled(False)

    threading.Thread(target=self._wifi_manager._update_networks, daemon=True).start()
    self._wifi_manager._request_scan()
    self._wifi_manager._last_network_update = time.monotonic()

  def _on_networks_updated(self, networks):
    if self._scanning:
      self._scanning = False
      self.scan_button.set_text(tr("Scan"))
      self.scan_button.set_enabled(True)

  def _render(self, rect: rl.Rectangle):
    super()._render(rect)

    if self._current_panel == PanelType.WIFI:
      self.scan_button.set_position(self._rect.x, self._rect.y + 20)
      self.scan_button.render()
