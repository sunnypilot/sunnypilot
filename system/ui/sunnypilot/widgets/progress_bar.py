import pyray as rl
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets.list_view import ListItem, ItemAction


class ProgressBarAction(ItemAction):
  def __init__(self, width=600):
    super().__init__(width=width)
    self.progress = 0.0
    self.text = ""
    self.show_progress = False
    self.text_color = rl.BLACK
    self._font = gui_app.font(FontWeight.NORMAL)

  def update(self, progress, text, show_progress=False, text_color=rl.BLACK):
    self.progress = progress
    self.text = text
    self.show_progress = show_progress
    self.text_color = text_color

  def _render(self, rect: rl.Rectangle):
    font_size = 40
    text_size = measure_text_cached(self._font, self.text, font_size)

    padding = 30
    bar_width = text_size.x + 2 * padding
    bar_height = 60

    bar_x = rect.x + rect.width - bar_width
    bar_y = rect.y + (rect.height - bar_height) / 2
    bar_rect = rl.Rectangle(bar_x, bar_y, bar_width, bar_height)

    if self.show_progress:
      inner_rect = rl.Rectangle(bar_rect.x + 4, bar_rect.y + 4, bar_rect.width - 8, bar_rect.height - 8)
      if inner_rect.width > 0:
        fill_width = inner_rect.width * (self.progress / 100.0)
        rl.draw_rectangle_rounded(rl.Rectangle(inner_rect.x, inner_rect.y, fill_width, inner_rect.height), 0.2, 10, rl.Color(30, 121, 232, 255))

    text_x = bar_rect.x + (bar_rect.width - text_size.x) / 2
    text_y = bar_rect.y + (bar_rect.height - text_size.y) / 2
    rl.draw_text_ex(self._font, self.text, rl.Vector2(text_x, text_y), font_size, 0, self.text_color)


def progress_item(title):
  action = ProgressBarAction()
  return ListItem(title=title, action_item=action)
