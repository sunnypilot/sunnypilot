import pyray as rl

from openpilot.system.ui.lib.list_view import ToggleAction, ButtonAction, DualButtonAction, TextAction, MultipleButtonAction, ListItem, ItemAction
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.lib.text_measure import measure_text_cached
from collections.abc import Callable

from openpilot.system.ui.sunnypilot.lib.toggle import ToggleSP
import openpilot.system.ui.sunnypilot.lib.styles as styles
from openpilot.system.ui.sunnypilot.lib.option_control import OptionControl

style = styles.Default


class ToggleActionSP(ToggleAction):
  def __init__(self, initial_state: bool = False, width: int = style.TOGGLE_WIDTH, enabled: bool | Callable[[], bool] = True):
    ToggleAction.__init__(self, initial_state, width, enabled)
    self.toggle = ToggleSP(initial_state=initial_state)

class ListItemSP(ListItem):
  def __init__(self, title: str = "", icon: str | None = None, description: str | Callable[[], str] | None = None,
               description_visible: bool = False, callback: Callable | None = None,
               action_item: ItemAction | None = None):
    ListItem.__init__(self, title, icon, description, description_visible, callback, action_item)

  def get_item_height(self, font: rl.Font, max_width: int) -> float:
    if not self.is_visible:
      return 0

    total_width = self._rect.width - (2 * style.ITEM_PADDING)  # Full width minus padding
    max_width = int(total_width - (2 * style.ITEM_PADDING))

    current_description = self.get_description()
    if self.description_visible and current_description:
      if (
              not self._wrapped_description
              or current_description != self._prev_description
              or max_width != self._prev_max_width
      ):
        self._prev_max_width = max_width
        self._prev_description = current_description

        wrapped_lines = wrap_text(self._font, current_description, style.ITEM_DESC_FONT_SIZE, max_width)
        self._wrapped_description = "\n".join(wrapped_lines)
        self._description_height = len(wrapped_lines) * style.ITEM_DESC_FONT_SIZE + 10
      return style.ITEM_BASE_HEIGHT + self._description_height - (style.ITEM_BASE_HEIGHT - style.ITEM_DESC_V_OFFSET) + style.ITEM_PADDING
    return style.ITEM_BASE_HEIGHT

  def get_right_item_rect(self, item_rect: rl.Rectangle) -> rl.Rectangle:
    if not self.action_item:
      return rl.Rectangle(0, 0, 0, 0)

    right_width = self.action_item.rect.width
    if right_width == 0:  # Full width action (like DualButtonAction)
      return rl.Rectangle(item_rect.x + style.ITEM_PADDING, item_rect.y,
                          item_rect.width - (style.ITEM_PADDING * 2), style.ITEM_BASE_HEIGHT)

    action_width = self.action_item.rect.width
    if isinstance(self.action_item, ToggleAction):
      action_x = item_rect.x
    else:
      action_x = item_rect.x + item_rect.width - action_width
    action_y = item_rect.y
    return rl.Rectangle(action_x, action_y, action_width, style.ITEM_BASE_HEIGHT)

  def _render(self, _):
    content_x = self._rect.x + style.ITEM_PADDING
    text_x = content_x
    left_action_item = isinstance(self.action_item, ToggleAction)

    if left_action_item:
      left_rect = rl.Rectangle(
        content_x,
        self._rect.y + (style.ITEM_BASE_HEIGHT - style.BUTTON_HEIGHT) // 2,
        style.TOGGLE_WIDTH,
        style.BUTTON_HEIGHT
      )
      text_x = left_rect.x + left_rect.width + style.ITEM_PADDING

      # Draw title
      if self.title:
        text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - text_size.y) // 2
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, style.ITEM_TEXT_COLOR)

      # Render toggle and handle callback
      if self.action_item.render(left_rect) and self.action_item.enabled:
        if self.callback:
          self.callback()

    else:
      if self.title:
        # Draw main text
        text_size = measure_text_cached(self._font, self.title, style.ITEM_TEXT_FONT_SIZE)
        item_y = self._rect.y + (style.ITEM_BASE_HEIGHT - text_size.y) // 2
        rl.draw_text_ex(self._font, self.title, rl.Vector2(text_x, item_y), style.ITEM_TEXT_FONT_SIZE, 0, style.ITEM_TEXT_COLOR)

        # Draw right item if present
        if self.action_item:
          right_rect = self.get_right_item_rect(self._rect)
          right_rect.y = self._rect.y
          if self.action_item.render(right_rect) and self.action_item.enabled:
            # Right item was clicked/activated
            if self.callback:
              self.callback()

    # Draw description if visible
    current_description = self.get_description()
    if self.description_visible and current_description and self._wrapped_description:
      rl.draw_text_ex(
        self._font,
        self._wrapped_description,
        rl.Vector2(content_x, self._rect.y + style.ITEM_DESC_V_OFFSET),
        style.ITEM_DESC_FONT_SIZE,
        0,
        style.ITEM_DESC_TEXT_COLOR,
      )

def toggle_item(title: str, description: str | Callable[[], str] | None = None, initial_state: bool = False,
                callback: Callable | None = None, icon: str = "", enabled: bool | Callable[[], bool] = True) -> ListItem:
  action = ToggleActionSP(initial_state=initial_state, enabled=enabled)
  return ListItemSP(title=title, description=description, action_item=action, icon=icon, callback=callback)


def button_item(title: str, button_text: str | Callable[[], str], description: str | Callable[[], str] | None = None,
                callback: Callable | None = None, enabled: bool | Callable[[], bool] = True) -> ListItem:
  action = ButtonAction(text=button_text, enabled=enabled)
  return ListItemSP(title=title, description=description, action_item=action, callback=callback)


def text_item(title: str, value: str | Callable[[], str], description: str | Callable[[], str] | None = None,
              callback: Callable | None = None, enabled: bool | Callable[[], bool] = True) -> ListItem:
  action = TextAction(text=value, color=rl.Color(170, 170, 170, 255), enabled=enabled)
  return ListItemSP(title=title, description=description, action_item=action, callback=callback)


def dual_button_item(left_text: str, right_text: str, left_callback: Callable = None, right_callback: Callable = None,
                     description: str | Callable[[], str] | None = None, enabled: bool | Callable[[], bool] = True) -> ListItem:
  action = DualButtonAction(left_text, right_text, left_callback, right_callback, enabled)
  return ListItemSP(title="", description=description, action_item=action)

def multiple_button_item(title: str, description: str, buttons: list[str], selected_index: int,
                         button_width: int = style.BUTTON_WIDTH, callback: Callable = None, icon: str = ""):
  action = MultipleButtonAction(buttons, button_width, selected_index, callback=callback)
  return ListItemSP(title=title, description=description, icon=icon, action_item=action)



class OptionControlAction(ItemAction):
  def __init__(self, min_value: int, max_value: int, initial_value: int,
               value_change_step: int = 1, enabled: bool | Callable[[], bool] = True,
               on_value_changed: Callable[[int], None] | None = None):
    # TODO: Fix click detection rectangle for description
    super().__init__(width=0, enabled=enabled)
    self.option_control = OptionControl(min_value, max_value, initial_value,
                                        value_change_step, enabled, on_value_changed)

  def _render(self, rect: rl.Rectangle) -> bool | int | None:
    self.option_control.set_enabled(self.enabled)
    return self.option_control.render(rect)


def option_item(title: str, min_value: int, max_value: int, initial_value: int,
                value_change_step: int = 1, description: str | Callable[[], str] | None = None,
                on_value_changed: Callable[[int], None] | None = None,
                enabled: bool | Callable[[], bool] = True,
                icon: str = "") -> ListItem:
  action = OptionControlAction(min_value, max_value, initial_value,
                               value_change_step, enabled, on_value_changed)
  return ListItemSP(title=title, description=description,
                  action_item=action, icon=icon)
