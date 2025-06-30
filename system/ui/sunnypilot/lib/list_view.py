import pyray as rl

import openpilot.system.ui.lib.list_view as ListItem
from openpilot.system.ui.lib.widget import Widget
from openpilot.system.ui.lib.text_measure import measure_text_cached

LINE_PADDING = 40
ITEM_BASE_HEIGHT = 170
ITEM_PADDING = 20
ITEM_TEXT_FONT_SIZE = 50
ITEM_TEXT_COLOR = rl.WHITE
ITEM_DESC_TEXT_COLOR = rl.Color(128, 128, 128, 255)
ITEM_DESC_FONT_SIZE = 40
ITEM_DESC_V_OFFSET = 140
ICON_SIZE = 80
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 100
BUTTON_FONT_SIZE = 35

class ListItemSP(Widget):

  def __init__(self):
    super().__init__()

  def _render(self, rect: rl.Rectangle):
    # Handle click on title/description area for toggling description
    if self.description and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
      mouse_pos = rl.get_mouse_position()

      text_area_width = rect.width - self.get_action_width() - ITEM_PADDING
      text_area_x = rect.x
      if isinstance(self, ListItem.ToggleItem):
        text_area_x = text_area_x + self.get_action_width() + ITEM_PADDING
      text_area = rl.Rectangle(text_area_x, rect.y, text_area_width, rect.height)

      if rl.check_collision_point_rec(mouse_pos, text_area):
        self.show_desc = not self.show_desc

    # Render title and description
    x = rect.x + ITEM_PADDING

    # Draw description if visible
    if self.show_desc and self._wrapped_description:
      rl.draw_text_ex(self._font, self._wrapped_description, (x, rect.y + ITEM_DESC_V_OFFSET),
                      ITEM_DESC_FONT_SIZE, 0, ITEM_DESC_TEXT_COLOR)

    # Render action if needed
    action_width = self.get_action_width()
    if isinstance(self, ListItem.ToggleItem):
      action_rect = rl.Rectangle(rect.x + ITEM_PADDING, rect.y, action_width, ITEM_BASE_HEIGHT)
      x += action_width + ITEM_PADDING
    else:
      action_rect = rl.Rectangle(rect.x + rect.width - action_width, rect.y, action_width, ITEM_BASE_HEIGHT)

    text_size = measure_text_cached(self._font, self.title, ITEM_TEXT_FONT_SIZE)
    title_y = rect.y + (ITEM_BASE_HEIGHT - text_size.y) // 2
    rl.draw_text_ex(self._font, self.title, (x, title_y), ITEM_TEXT_FONT_SIZE, 0, ITEM_TEXT_COLOR)

    return action_rect
