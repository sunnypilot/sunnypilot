"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroller_sp import ScrollerSP
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.augmented_road_view import AugmentedRoadViewSP
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.onroad_info_panel import OnroadInfoPanel

CONFIDENCE_BALL_VISIBLE_RATIO = 0.4
HORIZONTAL_SETTLE_PX = 5
HORIZONTAL_RESET_RATIO = 0.5


class OnroadViewContainerSP(ScrollerSP):
  def __init__(self, bookmark_callback=None):
    super().__init__(horizontal=False, snap_items=True, spacing=0, pad=0, scroll_indicator=False, edge_shadows=False)
    self.road_view = AugmentedRoadViewSP(bookmark_callback=bookmark_callback)
    self.onroad_info_panel = OnroadInfoPanel(bookmark_callback=bookmark_callback)

    self._scroller.add_widgets([
      self.road_view,
      self.onroad_info_panel,
    ])
    self._scroller.set_reset_scroll_at_show(False)
    self._scroller.set_scrolling_enabled(lambda: abs(self.rect.x) < HORIZONTAL_SETTLE_PX)

    for child in (self.road_view, self.onroad_info_panel):
      inner_touch_valid = child._touch_valid_callback
      child.set_touch_valid_callback(
        lambda inner=inner_touch_valid: self._touch_valid() and (inner() if inner else True)
      )

  def set_rect(self, rect: rl.Rectangle):
    super().set_rect(rect)
    self.road_view.set_rect(rect)
    self.onroad_info_panel.set_rect(rect)
    return self

  def is_swiping_left(self) -> bool:
    return self.road_view.is_swiping_left() or self.onroad_info_panel.is_swiping_left()

  def set_click_callback(self, callback) -> None:
    self.road_view.set_click_callback(callback)
    self.onroad_info_panel.set_click_callback(callback)

  def is_on_info_panel(self) -> bool:
    """True when scrolled past halfway toward onroad_info_panel (used by main layout
    to skip auto-pop-back-to-camera while user is reading the info panel)."""
    return abs(self._scroller.scroll_panel.get_offset()) > self._rect.height / 2

  def _render(self, rect: rl.Rectangle):
    if abs(self.rect.x) > gui_app.width * HORIZONTAL_RESET_RATIO:
      self._scroller.scroll_panel.set_offset(0)

    vertical_offset = self._scroller.scroll_panel.get_offset()
    show_ball = abs(vertical_offset) < rect.height * CONFIDENCE_BALL_VISIBLE_RATIO
    self.road_view.set_show_confidence_ball(show_ball)

    super()._render(rect)
