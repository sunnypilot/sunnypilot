"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import AugmentedRoadView

if gui_app.sunnypilot_ui():
  from openpilot.selfdrive.ui.sunnypilot.mici.onroad.augmented_road_view import AugmentedRoadViewSP as AugmentedRoadView
  from openpilot.selfdrive.ui.sunnypilot.mici.layouts.onroad_info_panel import OnroadInfoPanel


class OnroadViewContainerSP(Scroller):
  def __init__(self, bookmark_callback=None):
    super().__init__(horizontal=False, snap_items=True, spacing=0, pad=0, scroll_indicator=False, edge_shadows=False)
    self.road_view = AugmentedRoadView(bookmark_callback=bookmark_callback)
    self.onroad_info_panel = OnroadInfoPanel(bookmark_callback=bookmark_callback)

    self._scroller.add_widgets([
      self.road_view,
      self.onroad_info_panel,
    ])
    self._scroller.set_reset_scroll_at_show(False)

  def set_rect(self, rect: rl.Rectangle):
    super().set_rect(rect)
    self.road_view.set_rect(rect)
    self.onroad_info_panel.set_rect(rect)
    return self

  def is_swiping_left(self):
    return self.road_view.is_swiping_left() or self.onroad_info_panel.is_swiping_left()

  def set_click_callback(self, callback):
    self.road_view.set_click_callback(callback)
    self.onroad_info_panel.set_click_callback(callback)

  def _render(self, rect: rl.Rectangle):
    if abs(self.rect.x) > gui_app.width / 2:
      self._scroller.scroll_panel.set_offset(0)

    self._scroller.set_scrolling_enabled(lambda: abs(self.rect.x) < 5)

    vertical_offset = self._scroller.scroll_panel.get_offset()
    show_ball = abs(vertical_offset) < rect.height * 0.4
    self.road_view.set_show_confidence_ball(show_ball)

    super()._render(rect)
