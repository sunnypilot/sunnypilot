import pyray as rl
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget

class BlindSpotRenderer(Widget):
  def __init__(self, margin_x: int = 60, y_offset: int = 440):
    super().__init__()
    self.margin_x = margin_x
    self.y_offset = y_offset

    self._txt_blind_spot_left: rl.Texture = gui_app.texture('icons_mici/onroad/blind_spot_left.png', 162, 192)
    self._txt_blind_spot_right: rl.Texture = gui_app.texture('icons_mici/onroad/blind_spot_right.png', 162, 192)

    self._blind_spot_left_alpha_filter = FirstOrderFilter(0, 0.15, 1 / gui_app.target_fps)
    self._blind_spot_right_alpha_filter = FirstOrderFilter(0, 0.15, 1 / gui_app.target_fps)

  def _render(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm
    car_state = sm['carState']

    try:
      left_detected = car_state.leftBlindspot
    except AttributeError:
      left_detected = False

    try:
      right_detected = car_state.rightBlindspot
    except AttributeError:
      right_detected = False

    self._blind_spot_left_alpha_filter.update(1.0 if left_detected else 0.0)
    self._blind_spot_right_alpha_filter.update(1.0 if right_detected else 0.0)

    if self._blind_spot_left_alpha_filter.x > 0.01:
      pos_x = int(rect.x + self.margin_x)
      pos_y = int(rect.y + self.y_offset)
      alpha = int(255 * self._blind_spot_left_alpha_filter.x)
      color = rl.Color(255, 255, 255, alpha)
      rl.draw_texture(self._txt_blind_spot_left, pos_x, pos_y, color)

    if self._blind_spot_right_alpha_filter.x > 0.01:
      pos_x = int(rect.x + rect.width - self.margin_x - self._txt_blind_spot_right.width)
      pos_y = int(rect.y + self.y_offset)
      alpha = int(255 * self._blind_spot_right_alpha_filter.x)
      color = rl.Color(255, 255, 255, alpha)
      rl.draw_texture(self._txt_blind_spot_right, pos_x, pos_y, color)
