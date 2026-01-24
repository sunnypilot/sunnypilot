"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget

from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeMode


class LaneChangeSettingsLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._lane_change_timer = option_item_sp(
      title=lambda: tr("Auto Lane Change by Blinker"),
      param="AutoLaneChangeTimer",
      description=lambda: tr("Set a timer to delay the auto lane change operation when the blinker is used. " +
                             "No nudge on the steering wheel is required to auto lane change if a timer is set. Default is Nudge.<br>" +
                             "Please use caution when using this feature. Only use the blinker when traffic and road conditions permit."),
      min_value=-1,
      max_value=5,
      value_change_step=1,
      label_callback=(lambda x:
                      tr("Off") if x == -1 else
                      tr("Nudge") if x == 0 else
                      tr("Nudgeless") if x == 1 else
                      f"0.5 {tr('s')}" if x == 2 else
                      f"1 {tr('s')}" if x == 3 else
                      f"2 {tr('s')}" if x == 4 else
                      f"3 {tr('s')}")
    )
    self._bsm_delay = toggle_item_sp(
      param="AutoLaneChangeBsmDelay",
      title=lambda: tr("Auto Lane Change: Delay with Blind Spot"),
      description=lambda: tr("Toggle to enable a delay timer for seamless lane changes when blind spot monitoring " +
                             "(BSM) detects a obstructing vehicle, ensuring safe maneuvering."),
    )

    items = [
      self._lane_change_timer,
      LineSeparatorSP(40),
      self._bsm_delay,
    ]

    return items

  def _update_state(self):
    super()._update_state()
    self._update_toggles()

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    # subtract button
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()

  def _update_toggles(self):
    enable_bsm = ui_state.CP and ui_state.CP.enableBsm
    if not enable_bsm and ui_state.params.get_bool("AutoLaneChangeBsmDelay"):
      ui_state.params.remove("AutoLaneChangeBsmDelay")
    self._bsm_delay.action_item.set_enabled(enable_bsm and ui_state.params.get("AutoLaneChangeTimer", return_default=True) > AutoLaneChangeMode.NUDGE)
