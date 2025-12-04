"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, MousePos, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.list_view import ListItem, ToggleAction, ItemAction, MultipleButtonAction, _resolve_value
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP, LABEL_WIDTH


class ToggleActionSP(ToggleAction):
  def __init__(self, initial_state: bool = False, width: int = style.TOGGLE_WIDTH, enabled: bool | Callable[[], bool] = True,
               callback: Callable[[bool], None] | None = None, param: str | None = None):
    ToggleAction.__init__(self, initial_state, width, enabled, callback)
    self.toggle = ToggleSP(initial_state=initial_state, callback=callback, param=param)


class MultipleButtonActionSP(MultipleButtonAction):
  def __init__(self, buttons: list[str | Callable[[], str]], button_width: int, selected_index: int = 0, callback: Callable = None,
               param: str | None = None):
    MultipleButtonAction.__init__(self, buttons, button_width, selected_index, callback)
    self.param_key = param
    self.params = Params()
    if self.param_key:
      self.selected_button = int(self.params.get(self.param_key, return_default=True))
    self._anim_x: float | None = None

  def _render(self, rect: rl.Rectangle):

    button_y = rect.y + (rect.height - style.BUTTON_HEIGHT) / 2

    total_width = len(self.buttons) * self.button_width
    track_rect = rl.Rectangle(rect.x, button_y, total_width, style.BUTTON_HEIGHT)

    bg_color = style.MBC_TRANSPARENT
    text_color = style.ITEM_TEXT_COLOR if self.enabled else style.MBC_DISABLED
    highlight_color = style.MBC_BG_CHECKED_ENABLED if self.enabled else style.MBC_DISABLED

    # background
    rl.draw_rectangle_rounded(track_rect, 0.2, 20, bg_color)

    # border
    border_color = style.MBC_BG_CHECKED_ENABLED if self.enabled else style.MBC_DISABLED
    rl.draw_rectangle_rounded_lines_ex(track_rect, 0.2, 20, 2, border_color)

    # highlight with animation
    target_x = rect.x + self.selected_button * self.button_width
    if not self._anim_x:
      self._anim_x = target_x
    self._anim_x += (target_x - self._anim_x) * 0.2

    highlight_rect = rl.Rectangle(self._anim_x, button_y, self.button_width, style.BUTTON_HEIGHT)
    rl.draw_rectangle_rounded(highlight_rect, 0.2, 20, highlight_color)

    # text
    for i, _text in enumerate(self.buttons):
      button_x = rect.x + i * self.button_width

      text = _resolve_value(_text, "")
      text_size = measure_text_cached(self._font, text, 40)
      text_x = button_x + (self.button_width - text_size.x) / 2
      text_y = button_y + (style.BUTTON_HEIGHT - text_size.y) / 2

      rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), 40, 0, text_color)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    MultipleButtonAction._handle_mouse_release(self, mouse_pos)
    if self.param_key:
      self.params.put(self.param_key, self.selected_button)


class ListItemSP(ListItem):
  def __init__(self, title: str | Callable[[], str] = "", icon: str | None = None, description: str | Callable[[], str] | None = None,
               description_visible: bool = False, callback: Callable | None = None,
               action_item: ItemAction | None = None, inline: bool = True, title_color: rl.Color = style.ITEM_TEXT_COLOR):
    ListItem.__init__(self, title, icon, description, description_visible, callback, action_item)
    self.title_color = title_color
    self.inline = inline
    if not self.inline:
      self._rect.height += style.ITEM_BASE_HEIGHT/1.75
    self._right_value_source: str | Callable[[], str] | None = None
    self._right_value_font = gui_app.font(FontWeight.NORMAL)

  def set_right_value(self, value: str | Callable[[], str]):
    self._right_value_source = value

  @property
  def right_value(self) -> str:
    if self._right_value_source is None:
      return ""
    return str(_resolve_value(self._right_value_source, ""))

  def get_item_height(self, font: rl.Font, max_width: int) -> float:
    height = super().get_item_height(font, max_width)

    if self.description_visible:
      height += style.ITEM_PADDING * 1.5

    if not self.inline:
      height += style.ITEM_BASE_HEIGHT / 1.75

    return height

  def show_description(self, show: bool):
    self._set_description_visible(show)

  def get_right_item_rect(self, item_rect: rl.Rectangle) -> rl.Rectangle:
    if not self.action_item:
      return rl.Rectangle(0, 0, 0, 0)

    if not self.inline:
      has_description = bool(self.description) and self.description_visible

      if has_description:
        action_y = item_rect.y + self._text_size.y + style.ITEM_PADDING * 3
      else:
        action_y = item_rect.y + item_rect.height - style.BUTTON_HEIGHT - style.ITEM_PADDING * 1.5

      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, action_y, item_rect.width - (style.ITEM_PADDING * 2), style.BUTTON_HEIGHT)

    right_width = self.action_item.rect.width
    if right_width == 0:
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, item_rect.y, item_rect.width - (style.ITEM_PADDING * 2), style.ITEM_BASE_HEIGHT)

    action_width = self.action_item.rect.width
    if isinstance(self.action_item, ToggleAction):
      action_x = item_rect.x
    else:
      action_x = item_rect.x + item_rect.width - action_width
    action_y = item_rect.y
    return rl.Rectangle(action_x, action_y, action_width, style.ITEM_BASE_HEIGHT)

  def _render(self, _):
    if not self.is_visible:
      return

    # Don't draw items that are not in parent's viewport
    if (self._rect.y + self.rect.height) <= self._parent_rect.y or self._rect.y >= (self._parent_rect.y + self._parent_rect.height):
      return

    content_x = self._rect.x + style.ITEM_PADDING
    text_x = content_x
    left_action_item = isinstance(self.action_item, ToggleAction)

    if left_action_item:
      left_rect = rl.Rectangle(
        content_x,
        self._rect.y + (style.ITEM_BASE_HEIGHT - style.TOGGLE_HEIGHT) // 2,
        style.TOGGLE_WIDTH,
        style.TOGGLE_HEIGHT
      )
      text_x = left_rect.x + left_rect.width + style.ITEM_PADDING * 1.5

      # Draw title
      if self.title:
        self._text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - self._text_size.y) // 2
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, self.title_color)

      value_text = self.right_value
      if value_text:
        # area from after the title to the right edge of the row
        value_rect = rl.Rectangle(
          text_x,  # start at the beginning of the text area
          self._rect.y,
          self._rect.width - (text_x - self._rect.x) - style.ITEM_PADDING,
          style.ITEM_BASE_HEIGHT,
        )
        if value_rect.width > 0:
          gui_label(value_rect, value_text, font_size=style.ITEM_TEXT_FONT_SIZE, color=style.ITEM_TEXT_VALUE_COLOR, font_weight=FontWeight.NORMAL,
                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_RIGHT, alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)

      # Render toggle and handle callback
      if self.action_item.render(left_rect) and self.action_item.enabled:
        if self.callback:
          self.callback()

    else:
      if self.title:
        # Draw main text
        self._text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - self._text_size.y) // 2 if self.inline else self._rect.y + style.ITEM_PADDING * 1.5
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, self.title_color)

        # Draw right item if present
        if self.action_item:
          right_rect = self.get_right_item_rect(self._rect)
          if self.action_item.render(right_rect) and self.action_item.enabled:
            # Right item was clicked/activated
            if self.callback:
              self.callback()

    # Draw description if visible
    if self.description_visible:
      content_width = int(self._rect.width - style.ITEM_PADDING * 2)
      description_height = self._html_renderer.get_total_height(content_width)

      desc_y = self._rect.y + style.ITEM_DESC_V_OFFSET
      if not self.inline and self.action_item:
        desc_y = self.action_item.rect.y + style.ITEM_DESC_V_OFFSET - style.ITEM_PADDING * 0.5

      description_rect = rl.Rectangle(self._rect.x + style.ITEM_PADDING, desc_y, content_width, description_height)
      self._html_renderer.render(description_rect)


def toggle_item_sp(title: str | Callable[[], str], description: str | Callable[[], str] | None = None, initial_state: bool = False,
                   callback: Callable | None = None, icon: str = "", enabled: bool | Callable[[], bool] = True, param: str | None = None) -> ListItemSP:
  action = ToggleActionSP(initial_state=initial_state, enabled=enabled, callback=callback, param=param)
  return ListItemSP(title=title, description=description, action_item=action, icon=icon, callback=callback)


def multiple_button_item_sp(title: str | Callable[[], str], description: str | Callable[[], str], buttons: list[str | Callable[[], str]],
                            selected_index: int = 0, button_width: int = style.BUTTON_WIDTH, callback: Callable = None,
                            icon: str = "", param: str | None = None, inline: bool = False) -> ListItemSP:
  action = MultipleButtonActionSP(buttons, button_width, selected_index, callback=callback, param=param)
  return ListItemSP(title=title, description=description, icon=icon, action_item=action, inline=inline)


def option_item_sp(title: str | Callable[[], str], param: str,
                   min_value: int, max_value: int, description: str | Callable[[], str] | None = None,
                   value_change_step: int = 1, on_value_changed: Callable[[int], None] | None = None,
                   enabled: bool | Callable[[], bool] = True,
                   icon: str = "", label_width: int = LABEL_WIDTH, value_map: dict[int, int] | None = None,
                   use_float_scaling: bool = False, label_callback: Callable[[int], str] | None = None) -> ListItemSP:
  action = OptionControlSP(
    param, min_value, max_value, value_change_step,
    enabled, on_value_changed, value_map, label_width, use_float_scaling, label_callback
  )
  return ListItemSP(title=title, description=description, action_item=action, icon=icon)
