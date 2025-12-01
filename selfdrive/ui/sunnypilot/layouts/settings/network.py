"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.network import NetworkUI, PanelType


class NetworkUISP(NetworkUI):
  def __init__(self, wifi_manager):
    super().__init__(wifi_manager)

    self.scan_button = Button(tr("Scan"), self._scan_clicked, button_style=ButtonStyle.NORMAL, font_size=60, border_radius=30)
    self.scan_button.set_rect(rl.Rectangle(0, 0, 400, 100))

    self._scanning = False
    self._wifi_manager.add_callbacks(networks_updated=self._on_networks_updated)

  def _scan_clicked(self):
    self._scanning = True
    self.scan_button.set_text(tr("Scanning..."))
    self.scan_button.set_enabled(False)
    self._wifi_manager._request_scan()

  def _on_networks_updated(self, networks):
    if self._scanning:
      self._scanning = False
      self.scan_button.set_text(tr("Scan"))
      self.scan_button.set_enabled(True)

  def _render(self, _):
    if self._current_panel == PanelType.WIFI:
      self._nav_button.text = tr("Advanced")
      self.scan_button.set_position(self._rect.x, self._rect.y + 20)
      self.scan_button.render()
      self._nav_button.set_position(self._rect.x + self._rect.width - self._nav_button.rect.width, self._rect.y + 20)
      content_y = self._rect.y + self.scan_button.rect.height + 40
      content_rect = rl.Rectangle(self._rect.x, content_y, self._rect.width, self._rect.height - (content_y - self._rect.y))
      self._wifi_panel.render(content_rect)
    else:
      self._nav_button.text = tr("Back")
      self._nav_button.set_position(self._rect.x, self._rect.y + 20)
      content_rect = rl.Rectangle(self._rect.x, self._rect.y + self._nav_button.rect.height + 40,
                                  self._rect.width, self._rect.height - self._nav_button.rect.height - 40)
      self._advanced_panel.render(content_rect)
    self._nav_button.render()
