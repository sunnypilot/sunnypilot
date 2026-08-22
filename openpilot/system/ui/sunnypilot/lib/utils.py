"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl

from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import ButtonActionSP
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.list_view import BUTTON_WIDTH, BUTTON_HEIGHT, TEXT_PADDING, _resolve_value


class NoElideButtonAction(ButtonActionSP):
  def get_width_hint(self):
    return super().get_width_hint() + 1


class ScrollingButtonAction(ButtonActionSP):
  """ButtonActionSP whose value scrolls instead of eliding when it doesn't fit."""

  def __init__(self, text: str | Callable[[], str], width: int = style.BUTTON_ACTION_WIDTH,
               enabled: bool | Callable[[], bool] = True):
    super().__init__(text=text, width=width, enabled=enabled)
    self._value_label = UnifiedLabel("", font_size=style.ITEM_TEXT_FONT_SIZE, font_weight=FontWeight.NORMAL,
                                     text_color=self._value_color, scroll=True,
                                     alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)

  def set_value(self, value: str | Callable[[], str], color: rl.Color = style.ITEM_TEXT_VALUE_COLOR):
    if self.value != _resolve_value(value, ""):
      self._value_label.reset_scroll()
    super().set_value(value, color)
    self._value_label.set_text(value)
    self._value_label.set_text_color(color)

  def _render(self, rect: rl.Rectangle) -> bool:
    """Duplicate of ButtonActionSP._render, with the value drawn by a scrolling label"""
    self._button.set_text(self.text)
    self._button.set_enabled(_resolve_value(self.enabled))
    button_rect = rl.Rectangle(rect.x + rect.width - BUTTON_WIDTH, rect.y + (rect.height - BUTTON_HEIGHT) / 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    self._button.render(button_rect)

    if self.value:
      self._value_label.render(rl.Rectangle(rect.x, rect.y, rect.width - BUTTON_WIDTH - TEXT_PADDING, rect.height))

    pressed = self._pressed
    self._pressed = False
    return pressed


class AlertFadeAnimator:
  def __init__(self, target_fps: int, duration_on: float = 0.75, rc: float = 0.05):
    from openpilot.common.filter_simple import FirstOrderFilter
    self._filter = FirstOrderFilter(1.0, rc, 1 / target_fps)
    self._frame = 0
    self._target_fps = target_fps
    self._duration_on = duration_on

  def update(self, active: bool):
    if active:
      self._frame += 1
      if (self._frame % self._target_fps) < (self._target_fps * self._duration_on):
        self._filter.x = 1.0
      else:
        self._filter.update(0.0)
    else:
      self._frame = 0
      self._filter.update(1.0)

  @property
  def alpha(self) -> float:
    return self._filter.x
