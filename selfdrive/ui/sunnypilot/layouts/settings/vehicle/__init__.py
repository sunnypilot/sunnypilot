"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import ButtonAction
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.factory import BrandSettingsFactory
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.platform_selector import PlatformSelector, LegendWidget
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP


class VehicleLayout(Widget):
  def __init__(self):
    super().__init__()
    self._brand_settings = None
    self._brand_items = []
    self._current_brand = None
    self._platform_selector = PlatformSelector(self._update_brand_settings)

    self._vehicle_item = ListItemSP(title=self._platform_selector.text, action_item=ButtonAction(text=tr("SELECT")),
                                    callback=self._platform_selector._on_clicked)
    self._vehicle_item.title_color = self._platform_selector.color
    self._legend_widget = LegendWidget(self._platform_selector)

    self.items = [self._vehicle_item, self._legend_widget]
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  @staticmethod
  def get_brand():
    if bundle := ui_state.params.get("CarPlatformBundle"):
      return bundle.get("brand", "")
    elif ui_state.CP and ui_state.CP.carFingerprint != "MOCK":
      return ui_state.CP.brand
    return ""

  def _update_brand_settings(self):
    self._vehicle_item._title = self._platform_selector.text
    self._vehicle_item.title_color = self._platform_selector.color
    vehicle_text = tr("REMOVE") if ui_state.params.get("CarPlatformBundle") else tr("SELECT")
    self._vehicle_item.action_item.set_text(vehicle_text)

    brand = self.get_brand()
    if brand != self._current_brand:
      self._current_brand = brand
      self._brand_settings = BrandSettingsFactory.create_brand_settings(brand)
      self._brand_items = self._brand_settings.items if self._brand_settings else []

      self.items = [self._vehicle_item, self._legend_widget] + self._brand_items
      self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _update_state(self):
    self._update_brand_settings()
    if self._brand_settings:
      self._brand_settings.update_settings()
    self._platform_selector.refresh()

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
