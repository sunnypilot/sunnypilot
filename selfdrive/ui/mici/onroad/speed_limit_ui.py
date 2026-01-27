import pyray as rl
from dataclasses import dataclass
from openpilot.common.constants import CV
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

METER_TO_KM = 0.001
METER_TO_MILE = 0.000621371

SPEED_LIMIT_WIDTH_METRIC = 200
SPEED_LIMIT_WIDTH_IMPERIAL = 172
SPEED_LIMIT_HEIGHT = 204


@dataclass(frozen=True)
class SpeedLimitColors:
  white: rl.Color = rl.WHITE
  black: rl.Color = rl.BLACK
  red: rl.Color = rl.Color(255, 0, 0, 255)
  grey: rl.Color = rl.Color(145, 155, 149, 241)
  green: rl.Color = rl.Color(0, 255, 0, 255)
  light_grey: rl.Color = rl.Color(200, 200, 200, 255)
  dark_grey: rl.Color = rl.Color(180, 180, 180, 255)
  border_grey: rl.Color = rl.Color(77, 77, 77, 255)
  black_translucent: rl.Color = rl.Color(0, 0, 0, 166)
  border_translucent: rl.Color = rl.Color(255, 255, 255, 75)


COLORS = SpeedLimitColors()


class SpeedLimitRenderer(Widget):
  def __init__(self):
    super().__init__()
    self.speed_limit: float = 0.0
    self.speed_limit_valid: bool = False
    self.next_speed_limit: float = 0.0
    self.next_speed_limit_distance: float = 0.0
    self.road_name: str = ""
    self.current_speed: float = 0.0

    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

  def _update_state(self) -> None:
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    speed_conv = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH
    if sm.valid["mapdOut"]:
      mapd = sm["mapdOut"]
      self.speed_limit = mapd.speedLimit * speed_conv
      self.speed_limit_valid = mapd.speedLimit > 0
      self.next_speed_limit = mapd.nextSpeedLimit * speed_conv
      self.next_speed_limit_distance = mapd.nextSpeedLimitDistance
      self.road_name = mapd.roadName
    else:
      self.speed_limit_valid = False

    if sm.updated["carState"]:
      self.current_speed = sm["carState"].vEgo * speed_conv

  def _render(self, rect: rl.Rectangle) -> None:
    self._update_state()

    if not self.speed_limit_valid:
      return

    sign_width = SPEED_LIMIT_WIDTH_METRIC if ui_state.is_metric else SPEED_LIMIT_WIDTH_IMPERIAL
    sign_height = SPEED_LIMIT_HEIGHT
    sign_margin = 12
    sign_x = rect.x + sign_margin
    sign_y = rect.y + 45

    sign_rect = rl.Rectangle(sign_x, sign_y, sign_width, sign_height)

    speed_str = str(round(self.speed_limit))
    speed_color = COLORS.white if self.current_speed <= self.speed_limit else COLORS.red

    if ui_state.is_metric:
      self._draw_vienna_sign(sign_rect, speed_str, "", speed_color, True)
    else:
      self._draw_mutcd_sign(sign_rect, speed_str, "", speed_color, True)
    if self.next_speed_limit > 0 and self.next_speed_limit != self.speed_limit:
      self._draw_upcoming_speed_limit(sign_rect)

  def _draw_vienna_sign(self, sign_rect: rl.Rectangle, speed_str: str, sub_text: str, speed_color: rl.Color, has_speed_limit: bool) -> None:
    """Draw EU/Vienna sign."""
    center = rl.Vector2(sign_rect.x + sign_rect.width / 2, sign_rect.y + sign_rect.height / 2)
    outer_radius = min(sign_rect.width, sign_rect.height) / 2
    circle_size = outer_radius * 2

    rl.draw_circle_v(center, outer_radius, COLORS.white)
    ring_width = outer_radius * 0.18
    rl.draw_ring(center, outer_radius - ring_width, outer_radius, 0, 360, 36, COLORS.red)

    font_size = circle_size * (0.35 if len(speed_str) >= 3 else 0.45)
    text_size = measure_text_cached(self._font_bold, speed_str, int(font_size))
    text_pos = rl.Vector2(center.x - text_size.x / 2, center.y - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, speed_str, text_pos, font_size, 0, speed_color)

  def _draw_mutcd_sign(self, sign_rect: rl.Rectangle, speed_str: str, sub_text: str, speed_color: rl.Color, has_speed_limit: bool) -> None:
    """Draw US/Canada MUTCD sign."""
    padding = 8
    inner_rect = rl.Rectangle(sign_rect.x + padding, sign_rect.y + padding, sign_rect.width - (padding * 2), sign_rect.height - (padding * 2))
    rl.draw_rectangle_rounded(inner_rect, 0.35, 10, COLORS.white)
    rl.draw_rectangle_rounded_lines_ex(inner_rect, 0.35, 10, 4, COLORS.black)

    border_width = 4
    border_rect = rl.Rectangle(
      inner_rect.x + border_width, inner_rect.y + border_width, inner_rect.width - (border_width * 2), inner_rect.height - (border_width * 2)
    )
    speed_text = tr("SPEED")
    limit_text = tr("LIMIT")

    speed_size = measure_text_cached(self._font_semi_bold, speed_text, 40)
    limit_size = measure_text_cached(self._font_semi_bold, limit_text, 40)

    speed_pos = rl.Vector2(border_rect.x + (border_rect.width - speed_size.x) / 2, sign_rect.y + 27)
    limit_pos = rl.Vector2(border_rect.x + (border_rect.width - limit_size.x) / 2, sign_rect.y + 65)

    rl.draw_text_ex(self._font_semi_bold, speed_text, speed_pos, 40, 0, COLORS.black)
    rl.draw_text_ex(self._font_semi_bold, limit_text, limit_pos, 40, 0, COLORS.black)

    font_size = 70 if len(speed_str) >= 3 else 90
    speed_value_size = measure_text_cached(self._font_bold, speed_str, font_size)
    speed_value_pos = rl.Vector2(border_rect.x + (border_rect.width - speed_value_size.x) / 2, sign_rect.y + 100)
    rl.draw_text_ex(self._font_bold, speed_str, speed_value_pos, font_size, 0, speed_color)

  def _draw_upcoming_speed_limit(self, sign_rect: rl.Rectangle) -> None:
    """Draw upcoming speed limit."""
    speed_str = str(round(self.next_speed_limit))
    distance_str = self._format_distance(self.next_speed_limit_distance)

    ahead_width = 150
    ahead_height = 100
    ahead_x = sign_rect.x + (sign_rect.width - ahead_width) / 2
    ahead_y = sign_rect.y + sign_rect.height + 6
    ahead_rect = rl.Rectangle(ahead_x, ahead_y, ahead_width, ahead_height)

    rl.draw_rectangle_rounded(ahead_rect, 0.2, 10, rl.Color(0, 0, 0, 180))
    rl.draw_rectangle_rounded_lines_ex(ahead_rect, 0.2, 10, 3, rl.Color(255, 255, 255, 100))

    ahead_label = tr("AHEAD")
    ahead_size = measure_text_cached(self._font_semi_bold, ahead_label, 28)
    ahead_pos = rl.Vector2(ahead_rect.x + (ahead_rect.width - ahead_size.x) / 2, ahead_rect.y + 4)
    rl.draw_text_ex(self._font_semi_bold, ahead_label, ahead_pos, 28, 0, COLORS.light_grey)

    speed_size = measure_text_cached(self._font_bold, speed_str, 48)
    speed_pos = rl.Vector2(ahead_rect.x + (ahead_rect.width - speed_size.x) / 2, ahead_rect.y + 26)
    rl.draw_text_ex(self._font_bold, speed_str, speed_pos, 48, 0, COLORS.white)

    distance_size = measure_text_cached(self._font_medium, distance_str, 28)
    distance_pos = rl.Vector2(ahead_rect.x + (ahead_rect.width - distance_size.x) / 2, ahead_rect.y + 70)
    rl.draw_text_ex(self._font_medium, distance_str, distance_pos, 28, 0, COLORS.dark_grey)

  def _format_distance(self, distance: float) -> str:
    if ui_state.is_metric:
      if distance < 50:
        return tr("Near")
      if distance >= 1000:
        return f"{distance * METER_TO_KM:.1f}" + tr("km")
      if distance < 200:
        rounded = max(10, int(distance / 10) * 10)
      else:
        rounded = int(distance / 100) * 100
      return str(rounded) + tr("m")
    else:
      distance_mi = distance * METER_TO_MILE
      if distance_mi < 0.1:
        return tr("Near")
      return f"{distance_mi:.1f}" + tr("mi")
