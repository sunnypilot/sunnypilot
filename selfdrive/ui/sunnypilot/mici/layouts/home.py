
import pyray as rl

from openpilot.selfdrive.ui.mici.layouts.home import MiciHomeLayout
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.selfdrive.ui.ui_state import ui_state

class MiciHomeLayoutSP(MiciHomeLayout):
  def __init__(self):
    super().__init__()

  def _render_bottom_status_bar(self):
    super()._render_bottom_status_bar()

    ITEM_SPACING = 18
    Y_CENTER = 28

    if ui_state.always_offroad:
      text = "always offroad"
      font_size = 32
      padding_x = 10
      padding_y = 10
      font = gui_app.font(FontWeight.BOLD)

      # Measure text size
      text_width = measure_text_cached(font, text, font_size).x
      text_height = font_size
      pos_x = self._rect.x + self.rect.width - ITEM_SPACING - text_width - 5

      # Calculate rectangle dimensions
      rect_width = text_width + padding_x * 2
      rect_height = text_height + padding_y * 2

      # Draw rounded rectangle background (red)
      bg_rect = rl.Rectangle(pos_x, self._rect.y + self.rect.height - rect_height / 2 - Y_CENTER, rect_width,
                             rect_height)
      rl.draw_rectangle_rounded(bg_rect, 0.5, 10, rl.Color(245, 56, 56, 175))

      # Draw white text centered on the rectangle
      text_x = pos_x + padding_x
      text_y = self._rect.y + self.rect.height - rect_height / 2 - Y_CENTER + padding_y / 1.4
      rl.draw_text_ex(font, text, rl.Vector2(int(text_x), int(text_y)), font_size, 0, rl.WHITE)


