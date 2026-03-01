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
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.list_view import ListItem, ToggleAction, ItemAction, MultipleButtonAction, ButtonAction, \
                                                  _resolve_value, BUTTON_WIDTH, BUTTON_HEIGHT, TEXT_PADDING, DualButtonAction
from openpilot.system.ui.widgets.scroller_tici import LineSeparator, LINE_COLOR, LINE_PADDING
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP, LABEL_WIDTH


class Spacer(Widget):
  def __init__(self, height: int = 1):
    super().__init__()
    self._rect = rl.Rectangle(0, 0, 0, height)

  def set_parent_rect(self, parent_rect: rl.Rectangle) -> None:
    super().set_parent_rect(parent_rect)
    self._rect.width = parent_rect.width

  def _render(self, _):
    rl.draw_rectangle(int(self._rect.x), int(self._rect.y), int(self._rect.x + self._rect.width), int(self._rect.y), rl.Color(0,0,0,0))


class ToggleActionSP(ToggleAction):
  def __init__(self, initial_state: bool = False, width: int = style.TOGGLE_WIDTH, enabled: bool | Callable[[], bool] = True,
               callback: Callable[[bool], None] | None = None, param: str | None = None):
    ToggleAction.__init__(self, initial_state, width, enabled, callback)
    self.toggle = ToggleSP(initial_state=initial_state, callback=callback, param=param)


class ButtonSP(Button):
  def _update_state(self):
    super()._update_state()
    if self.enabled:
      if self.is_pressed:
        self._background_color = style.BUTTON_OFF_PRESSED
      else:
        self._background_color = style.BUTTON_ENABLED_OFF
    else:
      self._background_color = style.BUTTON_DISABLED
      self._label.set_text_color(style.BUTTON_TEXT_DISABLED)


class SimpleButtonActionSP(ItemAction):
  def __init__(self, button_text: str | Callable[[], str], callback: Callable | None = None,
               enabled: bool | Callable[[], bool] = True, button_width: int = style.SIMPLE_BUTTON_WIDTH):
    super().__init__(width=button_width, enabled=enabled)
    self.button_action = ButtonSP(button_text, click_callback=callback, button_style=ButtonStyle.NORMAL,
                                  border_radius=20)

  def set_touch_valid_callback(self, touch_callback: Callable[[], bool]) -> None:
    super().set_touch_valid_callback(touch_callback)
    self.button_action.set_touch_valid_callback(touch_callback)

  def _render(self, rect: rl.Rectangle) -> bool | int | None:
    self.button_action.set_enabled(self.enabled)
    return self.button_action.render(rect)


class ButtonActionSP(ButtonAction):
  def __init__(self, text: str | Callable[[], str], width: int = style.BUTTON_ACTION_WIDTH, enabled: bool | Callable[[], bool] = True):
    super().__init__(text=text, width=width, enabled=enabled)
    self._value_color: rl.Color = style.ITEM_TEXT_VALUE_COLOR

  def set_value(self, value: str | Callable[[], str], color: rl.Color = style.ITEM_TEXT_VALUE_COLOR):
    self._value_source = value
    self._value_color = color

  def _render(self, rect: rl.Rectangle) -> bool:
    """Duplicate of ButtonAction._render, with additional value rendering"""
    self._button.set_text(self.text)
    self._button.set_enabled(_resolve_value(self.enabled))
    button_rect = rl.Rectangle(rect.x + rect.width - BUTTON_WIDTH, rect.y + (rect.height - BUTTON_HEIGHT) / 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    self._button.render(button_rect)

    value_text = self.value
    if value_text:
      value_rect = rl.Rectangle(rect.x, rect.y, rect.width - BUTTON_WIDTH - TEXT_PADDING, rect.height)
      gui_label(value_rect, value_text, font_size=style.ITEM_TEXT_FONT_SIZE, color=self._value_color,
                font_weight=FontWeight.NORMAL, alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)

    pressed = self._pressed
    self._pressed = False
    return pressed


class DualButtonActionSP(DualButtonAction):
  def __init__(self, left_text: str | Callable[[], str], right_text: str | Callable[[], str], left_callback: Callable | None = None,
               right_callback: Callable | None = None, enabled: bool | Callable[[], bool] = True, border_radius: int = 15):
    DualButtonAction.__init__(self, left_text, right_text, left_callback, right_callback, enabled)
    self.left_button._border_radius = self.right_button._border_radius = border_radius

  def _render(self, rect: rl.Rectangle):
    button_spacing = 20
    button_height = 150
    button_width = (rect.width - button_spacing) / 2
    button_y = rect.y + (rect.height - button_height) / 2

    left_rect = rl.Rectangle(rect.x, button_y, button_width, button_height)
    right_rect = rl.Rectangle(rect.x + button_width + button_spacing, button_y, button_width, button_height)

    # expand one to full width if other is not visible
    if not self.left_button.is_visible:
      right_rect.x = rect.x
      right_rect.width = rect.width
    elif not self.right_button.is_visible:
      left_rect.width = rect.width

    # Render buttons
    self.left_button.render(left_rect)
    self.right_button.render(right_rect)


class MultipleButtonActionSP(MultipleButtonAction):
  def __init__(self, buttons: list[str | Callable[[], str]], button_width: int, selected_index: int = 0, callback: Callable | None = None,
               param: str | None = None):
    MultipleButtonAction.__init__(self, buttons, button_width, selected_index, callback)
    self.param_key = param
    self.params = Params()
    if self.param_key:
      self.selected_button = int(self.params.get(self.param_key, return_default=True))
    self._anim_x: float | None = None
    self.enabled_buttons: set[int] | None = None

  def set_enabled_buttons(self, indices: set[int] | None):
    self.enabled_buttons = indices

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

      # Check individual button enabled state
      is_button_enabled = self.enabled and (self.enabled_buttons is None or i in self.enabled_buttons)
      current_text_color = text_color if is_button_enabled else style.MBC_DISABLED

      rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), 40, 0, current_text_color)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    # Override parent method to check individual button enabled state
    if not self.enabled:
      return

    button_y = self._rect.y + (self._rect.height - style.BUTTON_HEIGHT) / 2
    for i, _ in enumerate(self.buttons):
      button_x = self._rect.x + i * self.button_width
      button_rect = rl.Rectangle(button_x, button_y, self.button_width, style.BUTTON_HEIGHT)

      if rl.check_collision_point_rec(mouse_pos, button_rect):
        # Check if this specific button is enabled
        if self.enabled_buttons is not None and i not in self.enabled_buttons:
          return

        self.selected_button = i
        if self.callback:
          self.callback(i)

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
    self._right_value_color: rl.Color = style.ITEM_TEXT_VALUE_COLOR

  def set_title(self, title: str | Callable[[], str] = ""):
    self._title = title

  def set_right_value(self, value: str | Callable[[], str], color: rl.Color = style.ITEM_TEXT_VALUE_COLOR):
    self._right_value_source = value
    self._right_value_color = color

  @property
  def right_value(self) -> str:
    if self._right_value_source is None:
      return ""
    return str(_resolve_value(self._right_value_source, ""))

  def _update_state(self):
    prev_desc = self._prev_description
    super()._update_state()
    if self.description_visible and self._prev_description != prev_desc:
      content_width = int(self._rect.width - style.ITEM_PADDING * 2)
      self._rect.height = self.get_item_height(self._font, content_width)

  def set_parent_rect(self, parent_rect: rl.Rectangle) -> None:
    super().set_parent_rect(parent_rect)
    if self.description_visible:
      content_width = int(self._rect.width - style.ITEM_PADDING * 2)
      self._rect.height = self.get_item_height(self._font, content_width)

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
      text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
      action_y = item_rect.y + text_size.y + style.ITEM_PADDING * 3
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, action_y, item_rect.width - (style.ITEM_PADDING * 2), style.BUTTON_HEIGHT)

    right_width = self.action_item.get_width_hint()
    if right_width == 0:
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, item_rect.y, item_rect.width - (style.ITEM_PADDING * 2), style.ITEM_BASE_HEIGHT)

    content_width = item_rect.width - (style.ITEM_PADDING * 2)
    title_width = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE).x
    right_width = min(content_width - title_width, right_width)
    if isinstance(self.action_item, ToggleAction) or isinstance(self.action_item, SimpleButtonActionSP):
      action_x = item_rect.x
    else:
      action_x = item_rect.x + item_rect.width - right_width
    action_y = item_rect.y
    return rl.Rectangle(action_x, action_y, right_width, style.ITEM_BASE_HEIGHT)

  def _render(self, _):
    if not self.is_visible:
      return

    # Don't draw items that are not in parent's viewport
    if (self._rect.y + self.rect.height) <= self._parent_rect.y or self._rect.y >= (self._parent_rect.y + self._parent_rect.height):
      return

    content_x = self._rect.x + style.ITEM_PADDING
    text_x = content_x
    left_action_item = isinstance(self.action_item, ToggleAction) or isinstance(self.action_item, SimpleButtonActionSP)

    if left_action_item:
      item_height = style.SIMPLE_BUTTON_HEIGHT if isinstance(self.action_item, SimpleButtonActionSP) else style.TOGGLE_HEIGHT
      left_rect = rl.Rectangle(
        content_x,
        self._rect.y + (style.ITEM_BASE_HEIGHT - item_height) // 2,
        self.action_item.rect.width,
        item_height
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
          gui_label(value_rect, value_text, font_size=style.ITEM_TEXT_FONT_SIZE, color=self._right_value_color, font_weight=FontWeight.NORMAL,
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


def simple_button_item_sp(button_text: str | Callable[[], str], callback: Callable | None = None,
                          enabled: bool | Callable[[], bool] = True, button_width: int = style.SIMPLE_BUTTON_WIDTH) -> ListItemSP:
  action = SimpleButtonActionSP(button_text=button_text, enabled=enabled, callback=callback, button_width=button_width)
  return ListItemSP(title="", callback=callback, description="", action_item=action)


def toggle_item_sp(title: str | Callable[[], str], description: str | Callable[[], str] | None = None, initial_state: bool = False,
                   callback: Callable | None = None, icon: str = "", enabled: bool | Callable[[], bool] = True, param: str | None = None) -> ListItemSP:
  action = ToggleActionSP(initial_state=initial_state, enabled=enabled, callback=callback, param=param)
  return ListItemSP(title=title, description=description, action_item=action, icon=icon, callback=callback)


def multiple_button_item_sp(title: str | Callable[[], str], description: str | Callable[[], str], buttons: list[str | Callable[[], str]],
                            selected_index: int = 0, button_width: int = style.BUTTON_ACTION_WIDTH, callback: Callable | None = None,
                            icon: str = "", param: str | None = None, inline: bool = False) -> ListItemSP:
  action = MultipleButtonActionSP(buttons, button_width, selected_index, callback=callback, param=param)
  return ListItemSP(title=title, description=description, icon=icon, action_item=action, inline=inline)


def option_item_sp(title: str | Callable[[], str], param: str,
                   min_value: int, max_value: int, description: str | Callable[[], str] | None = None,
                   value_change_step: int = 1, on_value_changed: Callable[[int], None] | None = None,
                   enabled: bool | Callable[[], bool] = True,
                   icon: str = "", label_width: int = LABEL_WIDTH, value_map: dict[int, int] | None = None,
                   use_float_scaling: bool = False, label_callback: Callable[[int], str] | None = None, inline: bool = False) -> ListItemSP:
  action = OptionControlSP(
    param, min_value, max_value, value_change_step,
    enabled, on_value_changed, value_map, label_width, use_float_scaling, label_callback
  )
  return ListItemSP(title=title, description=description, action_item=action, icon=icon, inline=inline)


def button_item_sp(title: str | Callable[[], str], button_text: str | Callable[[], str], description: str | Callable[[], str] | None = None,
                   callback: Callable | None = None, enabled: bool | Callable[[], bool] = True) -> ListItemSP:
  action = ButtonActionSP(text=button_text, enabled=enabled)
  return ListItemSP(title=title, description=description, action_item=action, callback=callback)


def dual_button_item_sp(left_text: str | Callable[[], str], right_text: str | Callable[[], str], left_callback: Callable | None = None,
                        right_callback: Callable | None = None, description: str | Callable[[], str] | None = None,
                        enabled: bool | Callable[[], bool] = True, border_radius: int = 15) -> ListItemSP:
  action = DualButtonActionSP(left_text, right_text, left_callback, right_callback, enabled, border_radius)
  return ListItemSP(title="", description=description, action_item=action)


class LineSeparatorSP(LineSeparator):
  def __init__(self, height: int = 1):
    super().__init__()
    self._rect = rl.Rectangle(0, 0, 0, height)

  def _render(self, _):
    line_y = int(self._rect.y + self._rect.height // 2)
    rl.draw_line(int(self._rect.x) + LINE_PADDING, line_y,
                 int(self._rect.x + self._rect.width) - LINE_PADDING, line_y,
                 LINE_COLOR)
