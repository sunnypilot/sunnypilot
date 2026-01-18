"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum

from openpilot.common.params import Params
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp, ToggleActionSP

ONROAD_BRIGHTNESS_TIMER_VALUES = {0: 15, 1: 30, **{i: (i - 1) * 60 for i in range(2, 12)}}


class OnroadBrightness(IntEnum):
  AUTO = 0
  AUTO_DARK = 1


class DisplayLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._onroad_brightness_toggle = toggle_item_sp(
      param="OnroadScreenOffControl",
      title=lambda: tr("Customize Onroad Brightness"),
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
      value_map=ONROAD_BRIGHTNESS_TIMER_VALUES,
      label_callback=lambda value: f"{value} s" if value < 60 else f"{int(value/60)} m",
      inline=True
    )
    self._onroad_brightness = option_item_sp(
      param="OnroadScreenOffBrightness",
      title=lambda: tr("Onroad Brightness"),
      description="",
      min_value=0,
      max_value=21,
      value_change_step=1,
      label_callback=lambda value: self.update_onroad_brightness(value),
      inline=True
    )
    items = [
      self._onroad_brightness_toggle,
      self._onroad_brightness_timer,
      self._onroad_brightness,
    ]
    return items

  @staticmethod
  def update_onroad_brightness(val):
    if val == OnroadBrightness.AUTO:
      return tr("Auto (Default)")

    if val == OnroadBrightness.AUTO_DARK:
      return tr("Auto (Dark)")

    return f"{(val - 1) * 5} %"

  def _update_state(self):
    super()._update_state()

    for _item in self._scroller._items:
      if isinstance(_item.action_item, ToggleActionSP) and _item.action_item.toggle.param_key is not None:
        _item.action_item.set_state(self._params.get_bool(_item.action_item.toggle.param_key))
      elif isinstance(_item.action_item, OptionControlSP) and _item.action_item.param_key is not None:
        _item.action_item.set_value(self._params.get(_item.action_item.param_key, return_default=True))

    self._onroad_brightness_timer.set_visible(self._onroad_brightness_toggle.action_item.get_state())
    self._onroad_brightness.set_visible(self._onroad_brightness_toggle.action_item.get_state())

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
