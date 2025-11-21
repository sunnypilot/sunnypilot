import pyray as rl

from collections.abc import Callable
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.list_view import ListItem, ToggleAction, ItemAction, ButtonAction, MultipleButtonAction, _resolve_value
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
from openpilot.system.ui.sunnypilot.lib.styles import style


class ToggleActionSP(ToggleAction):
  def __init__(self, initial_state: bool = False, width: int = style.TOGGLE_WIDTH, enabled: bool | Callable[[], bool] = True,
               callback: Callable[[bool], None] | None = None, param: str | None = None):
    ToggleAction.__init__(self, initial_state, width, enabled, callback)
    self.toggle = ToggleSP(initial_state=initial_state, callback=callback, param=param)

class SimpleButtonActionSP(ItemAction):
  def __init__(self, button_text: str | Callable[[], str], callback: Callable = None,
               enabled: bool | Callable[[], bool] = True, button_width: int | None = None):
    super().__init__(width=button_width, enabled=enabled)
    self.button_action = Button(button_text, click_callback=callback, button_style=ButtonStyle.NORMAL,
                                border_radius=20)

  def set_touch_valid_callback(self, touch_callback: Callable[[], bool]) -> None:
    super().set_touch_valid_callback(touch_callback)
    self.button_action.set_touch_valid_callback(touch_callback)

  def _render(self, rect: rl.Rectangle):
    self.button_action.render(rect)

class MultipleButtonActionSP(MultipleButtonAction):
  def __init__(self, param: str | None, buttons: list[str | Callable[[], str]], button_width: int, selected_index: int = 0, callback: Callable = None):
    MultipleButtonAction.__init__(self, buttons, button_width, selected_index, callback)
    self.param_key = param
    self.params = Params()
    if self.param_key:
      self.selected_button = int(self.params.get(self.param_key, return_default=True))

  def _render(self, rect: rl.Rectangle):
    spacing = style.ITEM_PADDING
    button_y = rect.y + (rect.height - style.BUTTON_HEIGHT) / 2

    for i, _text in enumerate(self.buttons):
      button_x = rect.x + i * (self.button_width + spacing)
      button_rect = rl.Rectangle(button_x, button_y, self.button_width, style.BUTTON_HEIGHT)

      # Check button state
      mouse_pos = rl.get_mouse_position()
      is_hovered = rl.check_collision_point_rec(mouse_pos, button_rect)
      is_pressed = is_hovered and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT) and self.is_pressed
      is_selected = i == self.selected_button

      # Button colors
      if is_selected:
        bg_color = style.ON_BG_COLOR
        if is_pressed:
          bg_color = style.ON_HOVER_BG_COLOR
      elif is_pressed:
        bg_color = style.OFF_HOVER_BG_COLOR
      else:
        bg_color = style.OFF_BG_COLOR

      if not self.enabled:
        bg_color = style.DISABLED_OFF_BG_COLOR

      # Draw button
      rl.draw_rectangle_rounded(button_rect, 1.0, 20, bg_color)

      # Draw text
      text = _resolve_value(_text, "")
      text_size = measure_text_cached(self._font, text, 40)
      text_x = button_x + (self.button_width - text_size.x) / 2
      text_y = button_y + (style.BUTTON_HEIGHT - text_size.y) / 2
      text_color = style.ITEM_TEXT_COLOR if self.enabled else style.ITEM_DISABLED_TEXT_COLOR
      rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), 40, 0, text_color)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    MultipleButtonAction._handle_mouse_release(self, mouse_pos)
    if self.param_key:
      self.params.put(self.param_key, self.selected_button)

class ListItemSP(ListItem):
  def __init__(self, title: str | Callable[[], str] = "", icon: str | None = None, description: str | Callable[[], str] | None = None,
               description_visible: bool = False, callback: Callable | None = None,
               action_item: ItemAction | None = None, inline: bool = True):
    ListItem.__init__(self, title, icon, description, description_visible, callback, action_item)
    self._is_left_action_item = (isinstance(self.action_item, ToggleAction) or
                                isinstance(self.action_item, SimpleButtonActionSP))
    self.inline = inline
    if not self.inline:
      self._rect.height += style.ITEM_BASE_HEIGHT/1.75

  def show_description(self, show: bool):
    self._set_description_visible(show)

  def get_item_height(self, font: rl.Font, max_width: int) -> float:
    height = super().get_item_height(font, max_width)
    if not self.inline:
      height = height + style.ITEM_BASE_HEIGHT/1.75
    return height

  def get_right_item_rect(self, item_rect: rl.Rectangle) -> rl.Rectangle:
    if not self.action_item:
      return rl.Rectangle(0, 0, 0, 0)

    if not self.inline:
      action_y = item_rect.y + self._text_size.y + style.ITEM_PADDING * 3
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, action_y, item_rect.width - (style.ITEM_PADDING * 2), style.BUTTON_HEIGHT)

    right_width = self.action_item.rect.width
    if right_width == 0:  # Full width action (like DualButtonAction)
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, item_rect.y,
                          item_rect.width - (style.ITEM_PADDING * 2), style.ITEM_BASE_HEIGHT)

    action_width = self.action_item.rect.width
    if self._is_left_action_item:
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

    if self._is_left_action_item:
      left_rect = rl.Rectangle(
        content_x,
        self._rect.y + (style.ITEM_BASE_HEIGHT - style.TOGGLE_HEIGHT) // 2,
        self.action_item.rect.width,
        style.TOGGLE_HEIGHT
      )
      text_x = left_rect.x + left_rect.width + style.ITEM_PADDING * 1.5

      # Draw title
      if self.title:
        self._text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - self._text_size.y) // 2
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, style.ITEM_TEXT_COLOR)

      # Render action item and handle callback
      if self.action_item.render(left_rect) and self.action_item.enabled:
        if self.callback:
          self.callback()

    else:
      if self.title:
        # Draw main text
        self._text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - self._text_size.y) // 2 if self.inline else self._rect.y + style.ITEM_PADDING * 1.5
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, style.ITEM_TEXT_COLOR)

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
        desc_y = self.action_item.rect.y + style.ITEM_DESC_V_OFFSET - style.ITEM_PADDING * 1.75

      description_rect = rl.Rectangle(self._rect.x + style.ITEM_PADDING, desc_y, content_width, description_height)
      self._html_renderer.render(description_rect)

def toggle_item_sp(title: str | Callable[[], str], description: str | Callable[[], str] | None = None, initial_state: bool = False,
                callback: Callable | None = None, icon: str = "", enabled: bool | Callable[[], bool] = True, param: str | None = None) -> ListItemSP:
  action = ToggleActionSP(initial_state=initial_state, enabled=enabled, callback=callback, param=param)
  return ListItemSP(title=title, description=description, action_item=action, icon=icon, callback=callback)

def option_item_sp(title: str | Callable[[], str], param: str,
                   min_value: int, max_value: int, description: str | Callable[[], str] | None = None,
                   value_change_step: int = 1, on_value_changed: Callable[[int], None] | None = None,
                   enabled: bool | Callable[[], bool] = True,
                   icon: str = "", label_width: int = style.BUTTON_WIDTH, value_map: dict[int, int] | None = None,
                   use_float_scaling: bool = False, label_callback: Callable[[int], str] | None = None) -> ListItemSP:
  action = OptionControlSP(
    param, min_value, max_value, value_change_step,
    enabled, on_value_changed, value_map, label_width, use_float_scaling, label_callback
  )
  return ListItemSP(title=title, description=description, action_item=action, icon=icon)

def multiple_button_item_sp(title: str | Callable[[], str], description: str| Callable[[], str], buttons: list[str | Callable[[], str]],
                            selected_index: int = 0, button_width: int = style.BUTTON_WIDTH, callback: Callable = None,
                            icon: str = "", param: str | None = None, inline: bool = True) -> ListItemSP:
  action = MultipleButtonActionSP(param, buttons, button_width, selected_index, callback=callback)
  return ListItemSP(title=title, description=description, icon=icon, action_item=action, inline=inline)

def simple_button_item_sp(button_text: str | Callable[[], str], callback: Callable | None = None,
                          enabled: bool | Callable[[], bool] = True, button_width: int = style.BUTTON_WIDTH) -> ListItemSP:
  action = SimpleButtonActionSP(button_text=button_text, enabled=enabled, callback=callback, button_width=button_width)
  return ListItemSP(title="", callback=callback, description="", action_item=action)
