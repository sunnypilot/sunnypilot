import pyray as rl
import math
from dataclasses import dataclass
from enum import IntEnum
from openpilot.common.constants import CV
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

METER_TO_KM = 0.001
METER_TO_FOOT = 3.28084
METER_TO_MILE = 0.000621371
UI_FREQ = 20
SPEED_LIMIT_AHEAD_VALID_FRAME_THRESHOLD = 5

SPEED_LIMIT_WIDTH_METRIC = 200
SPEED_LIMIT_WIDTH_IMPERIAL = 172
SPEED_LIMIT_HEIGHT = 204


class SpeedLimitMode(IntEnum):
  OFF = 0
  WARNING = 1
  ASSIST = 2


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
    self.speed_limit_last: float = 0.0
    self.speed_limit_offset: float = 0.0
    self.speed_limit_valid: bool = False
    self.speed_limit_last_valid: bool = False
    self.speed_limit_final_last: float = 0.0
    self.speed_limit_source: int = 0
    self.speed_limit_assist_state: int = 0
    self.speed_limit_assist_active: bool = False
    self.speed_limit_mode: SpeedLimitMode = SpeedLimitMode.OFF
    self.speed_limit_ahead_valid: bool = False
    self.speed_limit_ahead: float = 0.0
    self.speed_limit_ahead_distance: float = 0.0
    self.speed_limit_ahead_distance_prev: float = 0.0
    self.speed_limit_ahead_valid_frame: int = 0
    self.speed_limit_assist_frame: int = 0
    self.long_override: bool = False
    self.current_speed: float = 0.0

    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

  def _update_state(self) -> None:
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    speed_conv = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH

    if sm.updated["longitudinalPlanSP"]:
      lp_sp = sm["longitudinalPlanSP"]
      speed_limit_data = lp_sp.speedLimit
      resolver = speed_limit_data.resolver
      assist = speed_limit_data.assist

      self.speed_limit = resolver.speedLimit * speed_conv
      self.speed_limit_last = resolver.speedLimitLast * speed_conv
      self.speed_limit_offset = resolver.speedLimitOffset * speed_conv
      self.speed_limit_valid = resolver.speedLimitValid
      self.speed_limit_last_valid = resolver.speedLimitLastValid
      self.speed_limit_final_last = resolver.speedLimitFinalLast * speed_conv
      self.speed_limit_source = resolver.source
      self.speed_limit_assist_state = assist.state
      self.speed_limit_assist_active = assist.active

    if sm.updated["liveMapDataSP"]:
      lmd = sm["liveMapDataSP"]
      self.speed_limit_ahead_valid = lmd.speedLimitAheadValid
      self.speed_limit_ahead = lmd.speedLimitAhead * speed_conv
      self.speed_limit_ahead_distance = lmd.speedLimitAheadDistance

      if (self.speed_limit_ahead_distance < self.speed_limit_ahead_distance_prev and
        self.speed_limit_ahead_valid_frame < SPEED_LIMIT_AHEAD_VALID_FRAME_THRESHOLD):
        self.speed_limit_ahead_valid_frame += 1
      elif (self.speed_limit_ahead_distance > self.speed_limit_ahead_distance_prev and
            self.speed_limit_ahead_valid_frame > 0):
        self.speed_limit_ahead_valid_frame -= 1

      self.speed_limit_ahead_distance_prev = self.speed_limit_ahead_distance

    car_control = sm["carControl"]
    #self.long_override = car_control.cruiseControl.override_

    car_state = sm["carState"]
    v_ego_cluster = car_state.vEgoCluster
    v_ego_cluster_seen = v_ego_cluster != 0.0
    v_ego = v_ego_cluster if v_ego_cluster_seen else car_state.vEgo
    self.current_speed = max(0.0, v_ego * speed_conv)

    self.speed_limit_mode = SpeedLimitMode.WARNING  # TODO: HELPPP

  def _render(self, rect: rl.Rectangle) -> None:
    show_speed_limit = False

    if self.speed_limit_assist_state == 1:  # PRE_ACTIVE state
      self.speed_limit_assist_frame += 1
      show_speed_limit = self._pulse_element(self.speed_limit_assist_frame)
    else:
      self.speed_limit_assist_frame = 0
      show_speed_limit = self.speed_limit_mode != SpeedLimitMode.OFF

    if not show_speed_limit:
      return

    speed_limit_width = SPEED_LIMIT_WIDTH_METRIC if ui_state.is_metric else SPEED_LIMIT_WIDTH_IMPERIAL

    base_x = 280 if ui_state.is_metric else 272

    x = rect.x + base_x + (SPEED_LIMIT_WIDTH_IMPERIAL - speed_limit_width) // 2
    y = rect.y + 45

    sign_rect = rl.Rectangle(x, y, speed_limit_width, SPEED_LIMIT_HEIGHT)

    # Draw pre-active arrows
    if self.speed_limit_assist_state == 1:  # PRE_ACTIVE
      self._draw_pre_active_arrow(sign_rect)

    self._draw_speed_limit_sign(sign_rect)

    # Draw upcoming speed limit if not in PRE_ACTIVE state
    if self.speed_limit_assist_state != 1:
      self._draw_upcoming_speed_limit(sign_rect)

  def _pulse_element(self, frame: int) -> bool:
    if frame % UI_FREQ < (UI_FREQ / 2.5):
      return False
    return True

  def _draw_speed_limit_sign(self, sign_rect: rl.Rectangle) -> None:
    speed_limit_warning_enabled = self.speed_limit_mode >= SpeedLimitMode.WARNING
    has_speed_limit = self.speed_limit_valid or self.speed_limit_last_valid
    overspeed = has_speed_limit and round(self.speed_limit_final_last) < round(self.current_speed)
    speed_limit_str = str(round(self.speed_limit_last)) if has_speed_limit else "---"

    speed_limit_sub_text = ""
    if self.speed_limit_offset != 0:
      speed_limit_sub_text = ("" if self.speed_limit_offset > 0 else "-") + str(round(abs(self.speed_limit_offset)))

    speed_color = COLORS.black
    if speed_limit_warning_enabled and overspeed:
      speed_color = COLORS.red
    elif not self.speed_limit_valid and self.speed_limit_last_valid:
      speed_color = COLORS.grey

    if ui_state.is_metric:
      self._draw_vienna_sign(sign_rect, speed_limit_str, speed_limit_sub_text, speed_color, has_speed_limit)
    else:
      self._draw_mutcd_sign(sign_rect, speed_limit_str, speed_limit_sub_text, speed_color, has_speed_limit)

  def _draw_vienna_sign(self, sign_rect: rl.Rectangle, speed_str: str, sub_text: str,
                        speed_color: rl.Color, has_speed_limit: bool) -> None:
    """Draw EU Vienna sign."""
    padding = 15
    circle_size = min(sign_rect.width, sign_rect.height) - (padding * 2)
    circle_x = sign_rect.x + (sign_rect.width - circle_size) / 2
    circle_y = sign_rect.y + (sign_rect.height - circle_size) / 2
    center = rl.Vector2(circle_x + circle_size / 2, circle_y + circle_size / 2)
    radius = circle_size / 2

    rl.draw_circle_v(center, radius, COLORS.white)
    rl.draw_ring(center, radius * 0.88, radius, 0, 360, 36, COLORS.red)

    font_size = 70 if len(speed_str) >= 3 else 85
    text_size = measure_text_cached(self._font_bold, speed_str, font_size)
    text_pos = rl.Vector2(center.x - text_size.x / 2, center.y - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, speed_str, text_pos, font_size, 0, speed_color)

    # Offset value
    if sub_text and has_speed_limit:
      offset_size = circle_size * 0.4
      overlap = offset_size * 0.25
      offset_center = rl.Vector2(
        sign_rect.x + sign_rect.width - offset_size / 1.25 + overlap,
        sign_rect.y - offset_size / 1.75 + overlap + offset_size / 2
      )
      rl.draw_circle_v(offset_center, offset_size / 2, COLORS.black)
      rl.draw_ring(offset_center, offset_size / 2 - 3, offset_size / 2, 0, 360, 36, COLORS.border_grey)

      sub_font_size = offset_size * (0.5 if ui_state.is_metric else 0.6)
      if len(sub_text) >= 3:
        sub_font_size = offset_size * 0.475

      sub_text_size = measure_text_cached(self._font_bold, sub_text, int(sub_font_size))
      sub_text_pos = rl.Vector2(
        offset_center.x - sub_text_size.x / 2,
        offset_center.y - sub_text_size.y / 2
      )
      rl.draw_text_ex(self._font_bold, sub_text, sub_text_pos, int(sub_font_size), 0, COLORS.white)

  def _draw_mutcd_sign(self, sign_rect: rl.Rectangle, speed_str: str, sub_text: str,
                       speed_color: rl.Color, has_speed_limit: bool) -> None:
    """Draw US/Canada MUTCD sign."""
    #rl.draw_rectangle_rounded(sign_rect, 0.35, 10, COLORS.white) # this is here for sunny
    padding = 8
    inner_rect = rl.Rectangle(
      sign_rect.x + padding,
      sign_rect.y + padding,
      sign_rect.width - (padding * 2),
      sign_rect.height - (padding * 2)
    )
    rl.draw_rectangle_rounded(inner_rect, 0.35, 10, COLORS.white)
    rl.draw_rectangle_rounded_lines_ex(inner_rect, 0.35, 10, 4, COLORS.black)

    border_width = 4
    border_rect = rl.Rectangle(
      inner_rect.x + border_width,
      inner_rect.y + border_width,
      inner_rect.width - (border_width * 2),
      inner_rect.height - (border_width * 2)
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
    speed_value_pos = rl.Vector2(
      border_rect.x + (border_rect.width - speed_value_size.x) / 2,
      sign_rect.y + 100
    )
    rl.draw_text_ex(self._font_bold, speed_str, speed_value_pos, font_size, 0, speed_color)

    # Offset value
    if sub_text and has_speed_limit:
      offset_box_size = sign_rect.width * 0.4
      overlap = offset_box_size * 0.25
      offset_rect = rl.Rectangle(
        sign_rect.x + sign_rect.width - offset_box_size / 1.5 + overlap,
        sign_rect.y - offset_box_size / 1.25 + overlap,
        offset_box_size,
        offset_box_size
      )

      corner_radius = offset_box_size * 0.2 / offset_box_size
      rl.draw_rectangle_rounded(offset_rect, corner_radius, 10, COLORS.black)
      rl.draw_rectangle_rounded_lines_ex(offset_rect, corner_radius, 10, 6, COLORS.border_grey)

      sub_font_size = offset_box_size * 0.6
      if len(sub_text) >= 3:
        sub_font_size = offset_box_size * 0.475

      sub_text_size = measure_text_cached(self._font_bold, sub_text, int(sub_font_size))
      sub_text_pos = rl.Vector2(
        offset_rect.x + (offset_rect.width - sub_text_size.x) / 2,
        offset_rect.y + (offset_rect.height - sub_text_size.y) / 2
      )
      rl.draw_text_ex(self._font_bold, sub_text, sub_text_pos, int(sub_font_size), 0, COLORS.white)

  def _draw_upcoming_speed_limit(self, sign_rect: rl.Rectangle) -> None:
    """Draw upcoming speed limit indicator"""
    speed_limit_ahead = (
      self.speed_limit_ahead_valid and
      self.speed_limit_ahead > 0 and
      self.speed_limit_ahead != self.speed_limit and
      self.speed_limit_ahead_valid_frame > 0 and
      self.speed_limit_source == 0  # source
    )

    if not speed_limit_ahead:
      return

    speed_str = str(round(self.speed_limit_ahead))
    distance_str = self._format_distance(self.speed_limit_ahead_distance)

    ahead_width = 170
    ahead_height = 160
    ahead_x = sign_rect.x + (sign_rect.width - ahead_width) / 2
    ahead_y = sign_rect.y + sign_rect.height + 10
    ahead_rect = rl.Rectangle(ahead_x, ahead_y, ahead_width, ahead_height)

    rl.draw_rectangle_rounded(ahead_rect, 0.2, 10, rl.Color(0, 0, 0, 180))
    rl.draw_rectangle_rounded_lines_ex(ahead_rect, 0.2, 10, 3, rl.Color(255, 255, 255, 100))

    ahead_label = tr("AHEAD")
    ahead_size = measure_text_cached(self._font_semi_bold, ahead_label, 40)
    ahead_pos = rl.Vector2(ahead_rect.x + (ahead_rect.width - ahead_size.x) / 2, ahead_rect.y + 4)
    rl.draw_text_ex(self._font_semi_bold, ahead_label, ahead_pos, 40, 0, COLORS.light_grey)

    speed_size = measure_text_cached(self._font_bold, speed_str, 70)
    speed_pos = rl.Vector2(ahead_rect.x + (ahead_rect.width - speed_size.x) / 2, ahead_rect.y + 38)
    rl.draw_text_ex(self._font_bold, speed_str, speed_pos, 70, 0, COLORS.white)

    distance_size = measure_text_cached(self._font_medium, distance_str, 40)
    distance_pos = rl.Vector2(
      ahead_rect.x + (ahead_rect.width - distance_size.x) / 2,
      ahead_rect.y + 110
    )
    rl.draw_text_ex(self._font_medium, distance_str, distance_pos, 40, 0, COLORS.dark_grey)

  def _format_distance(self, distance: float) -> str:
    if ui_state.is_metric:
      if distance < 50:
        return tr("Near")
      if distance >= 1000:
        return f"{distance * METER_TO_KM:.1f}" + tr("km")

      # Round to appropriate
      if distance < 200:
        rounded = max(10, self._round_to_interval(distance, 10, 5))
      else:
        rounded = self._round_to_interval(distance, 100, 50)
      return str(rounded) + tr("m")
    else:
      distance_ft = distance * METER_TO_FOOT
      if distance_ft < 100:
        return tr("Near")
      if distance_ft >= 900:
        return f"{distance * METER_TO_MILE:.1f}" + tr("mi")

      if distance_ft < 500:
        rounded = max(50, self._round_to_interval(distance_ft, 50, 25))
      else:
        rounded = self._round_to_interval(distance_ft, 100, 50)
      return str(rounded) + tr("ft")

  def _round_to_interval(self, distance: float, interval: int, threshold: int) -> int:
    base = int(distance / interval) * interval
    return base + interval if (distance - base >= threshold) else base

  def _draw_pre_active_arrow(self, sign_rect: rl.Rectangle) -> None:
    sign_margin = 12
    arrow_spacing = sign_margin * 1.4
    arrow_x = sign_rect.x + sign_rect.width + arrow_spacing

    set_speed = 0
    speed_limit_final = round(self.speed_limit_final_last)

    bounce_frequency = 2.0 * math.pi / UI_FREQ
    bounce_offset = 20 * math.sin(self.speed_limit_assist_frame * bounce_frequency)

    arrow_size = 45
    center_y = sign_rect.y + sign_rect.height / 2

    if set_speed < speed_limit_final:
      arrow_y = center_y - arrow_size + bounce_offset
      self._draw_triangle_up(arrow_x, arrow_y, arrow_size, COLORS.green)
    elif set_speed > speed_limit_final:
      arrow_y = center_y - bounce_offset
      self._draw_triangle_down(arrow_x, arrow_y, arrow_size, COLORS.green)

  def _draw_triangle_up(self, x: float, y: float, size: float, color: rl.Color) -> None:
    v1 = rl.Vector2(x + size / 2, y)
    v2 = rl.Vector2(x, y + size)
    v3 = rl.Vector2(x + size, y + size)
    rl.draw_triangle(v1, v3, v2, color)

  def _draw_triangle_down(self, x: float, y: float, size: float, color: rl.Color) -> None:
    v1 = rl.Vector2(x, y)
    v2 = rl.Vector2(x + size, y)
    v3 = rl.Vector2(x + size / 2, y + size)
    rl.draw_triangle(v1, v2, v3, color)
