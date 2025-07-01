import pyray as rl
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.lib.text_measure import measure_text_cached
import openpilot.system.ui.sunnypilot.lib.styles as styles

style = styles.Default

class ListItemSP:

  def get_item_height(self) -> float:
    if not self.is_visible:
      return 0

    total_width = self._rect.width - (2 * style.ITEM_PADDING)  # Full width minus padding
    max_width = total_width - (2 * style.ITEM_PADDING)

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

  def get_action_item_rect(self, item_rect: rl.Rectangle, left_action_item: bool) -> rl.Rectangle:
    action_width = self.action_item.rect.width
    if left_action_item:
      action_x = item_rect.x
    else:
      action_x = item_rect.x + item_rect.width - action_width
    action_y = item_rect.y
    return rl.Rectangle(action_x, action_y, action_width, style.ITEM_BASE_HEIGHT)

  def _render(self, left_action_item: bool):
    content_x = self._rect.x + style.ITEM_PADDING
    text_x = content_x

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

    return True
