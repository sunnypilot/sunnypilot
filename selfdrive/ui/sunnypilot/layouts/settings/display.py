"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, ToggleActionSP

onroad_brightness_timer_values = {
  0: 15,
  1: 30,
  2: 60,
  3: 120,
  4: 180,
  5: 240,
  6: 300,
  7: 360,
  8: 420,
  9: 480,
  10: 540,
  11: 600
}

class DisplayLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._onroad_brightness_toggle = toggle_item_sp(
      param="OnroadScreenOffControl",
      title=lambda: tr("Onroad Screen: Reduced Brightness"),
      description=lambda: tr("Turn off device screen or reduce brightness after driving starts. " +
         "It automatically brightens again when screen is touched or a visible alert is displayed."),
    )
    self._onroad_brightness_timer = option_item_sp(
      param="OnroadScreenOffTimer",
      title=lambda: tr("Onroad Brightness Delay"),
      description="",
      min_value=0,
      max_value=11,
      value_change_step=1,
      value_map=onroad_brightness_timer_values,
      label_callback=lambda value: f"{value} s" if value < 60 else f"{int(value/60)} m",
      inline=True
    )
    self._onroad_brightness = option_item_sp(
      param="OnroadScreenOffBrightness",
      title=lambda: tr("Onroad Brightness"),
      description="",
      min_value=0,
      max_value=90,
      value_change_step=5,
      label_callback=lambda value: f"{value} %" if value > 0 else tr("Screen Off"),
      inline=True
    )
    items = [
      self._onroad_brightness_toggle,
      self._onroad_brightness_timer,
      self._onroad_brightness,
    ]
    return items

  def _update_state(self):
    super()._update_state()

    for _item in self._scroller._items:
      if isinstance(_item.action_item, ToggleActionSP) and _item.action_item.toggle.param_key is not None:
        _item.action_item.set_state(ui_state.params.get_bool(_item.action_item.toggle.param_key))
      elif isinstance(_item.action_item, OptionControlSP) and _item.action_item.param_key is not None:
        _item.action_item.set_value(ui_state.params.get(_item.action_item.param_key, return_default=True))

    self._onroad_brightness_timer.set_visible(self._onroad_brightness_toggle.action_item.get_state())
    self._onroad_brightness.set_visible(self._onroad_brightness_toggle.action_item.get_state())

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
