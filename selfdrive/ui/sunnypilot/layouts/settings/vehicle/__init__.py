"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import ButtonAction
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.platform_selector import PlatformSelector, LegendWidget
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP


class VehicleLayout(Widget):
  def __init__(self):
    super().__init__()
    self._platform_selector = PlatformSelector(self._update_brand_settings)

    self._vehicle_item = ListItemSP(title=self._platform_selector.text, action_item=ButtonAction(text=tr("Select")),
                                    callback=self._platform_selector._on_clicked)
    self._vehicle_item.title_color = self._platform_selector.color
    self._legend_widget = LegendWidget(self._platform_selector)

    self.items = [self._vehicle_item, self._legend_widget]
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _update_brand_settings(self):
    self._vehicle_item._title = self._platform_selector.text
    self._vehicle_item.title_color = self._platform_selector.color
    vehicle_text = tr("Remove") if ui_state.params.get("CarPlatformBundle") else tr("Select")
    self._vehicle_item.action_item.set_text(vehicle_text)

  def _update_state(self):
    self._update_brand_settings()

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
