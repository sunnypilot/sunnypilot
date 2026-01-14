"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

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

@dataclass(frozen=True)
class MapdPanelColors:
  white: rl.Color = rl.WHITE
  black: rl.Color = rl.BLACK
  red: rl.Color = rl.Color(255, 0, 0, 255)
  green: rl.Color = rl.Color(0, 255, 0, 255)
  grey: rl.Color = rl.Color(145, 155, 149, 241)
  light_grey: rl.Color = rl.Color(200, 200, 200, 255)
  dark_grey: rl.Color = rl.Color(100, 100, 100, 255)
  bg_dark: rl.Color = rl.Color(30, 30, 30, 255)
  card_bg: rl.Color = rl.Color(50, 50, 50, 200)

COLORS = MapdPanelColors()

class MapdInfoPanel(Widget):
  def __init__(self):
    super().__init__()
    self.speed_limit: float = 0.0
    self.speed_limit_valid: bool = False
    self.next_speed_limit: float = 0.0
    self.next_speed_limit_distance: float = 0.0
    self.road_name: str = ""
    self.current_speed: float = 0.0
    self.lanes: int = 0
    self.road_context: str = ""
    self.hazard: str = ""
    self.vision_curve_speed: float = 0.0
    self.map_curve_speed: float = 0.0
    self.tile_loaded: bool = False

    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

  def _update_state(self) -> None:
    sm = ui_state.sm
    speed_conv = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH
    if sm.valid["mapdOut"]:
      mapd = sm["mapdOut"]
      self.speed_limit = mapd.speedLimit * speed_conv
      self.speed_limit_valid = mapd.speedLimit > 0
      self.next_speed_limit = mapd.nextSpeedLimit * speed_conv
      self.next_speed_limit_distance = mapd.nextSpeedLimitDistance
      self.road_name = mapd.roadName
      self.lanes = mapd.lanes
      self.hazard = mapd.hazard
      self.vision_curve_speed = mapd.visionCurveSpeed * speed_conv
      self.map_curve_speed = mapd.mapCurveSpeed * speed_conv
      self.tile_loaded = mapd.tileLoaded

      road_ctx = mapd.roadContext
      if hasattr(road_ctx, 'raw'):
        ctx_val = road_ctx.raw
      else:
        ctx_val = int(road_ctx)
      self.road_context = ["Freeway", "City", "Unknown"][ctx_val] if ctx_val < 3 else "Unknown"
    else:
      self.speed_limit_valid = False

    if sm.updated["carState"]:
      self.current_speed = sm["carState"].vEgo * speed_conv

  def _render(self, rect: rl.Rectangle) -> None:
    self._update_state()

    rl.draw_rectangle(int(rect.x), int(rect.y), int(rect.width), int(rect.height), COLORS.bg_dark)
    margin = 15
    left_width = 130
    right_x = rect.x + left_width + margin + 10
    right_width = rect.width - left_width - margin * 3
    sign_x = rect.x + margin + 5
    sign_y = rect.y + (rect.height - 140) / 2
    self._draw_speed_limit_sign(sign_x, sign_y)
    info_y = rect.y + 25

    # Road name
    self._draw_road_name(right_x, info_y, right_width)
    info_y += 55

    # Road context (Freeway/City) and lanes
    self._draw_road_details(right_x, info_y, right_width)
    info_y += 45

    # Next speed limit
    self._draw_next_speed_limit(right_x, info_y, right_width)
    info_y += 45

    # Curve speeds
    self._draw_curve_speeds(right_x, info_y, right_width)
    info_y += 45

    # Hazard warning Beta
    if self.hazard:
      self._draw_hazard(right_x, info_y, right_width)

    status_text = tr("Map Loaded") if self.tile_loaded else tr("No Map Data")
    status_color = COLORS.green if self.tile_loaded else COLORS.red
    status_size = measure_text_cached(self._font_medium, status_text, 18)
    status_pos = rl.Vector2(rect.x + (rect.width - status_size.x) / 2, rect.y + rect.height - 30)
    rl.draw_text_ex(self._font_medium, status_text, status_pos, 18, 0, status_color)

  def _draw_speed_limit_sign(self, x: float, y: float) -> None:
    sign_width = 110 if ui_state.is_metric else 100
    sign_height = 120 if ui_state.is_metric else 110

    speed_str = str(round(self.speed_limit)) if self.speed_limit_valid else "--"
    speed_color = COLORS.black if not self.speed_limit_valid or self.current_speed <= self.speed_limit else COLORS.red

    if ui_state.is_metric:
      self._draw_vienna_sign(x, y, sign_width, sign_height, speed_str, speed_color)
    else:
      self._draw_mutcd_sign(x, y, sign_width, sign_height, speed_str, speed_color)

  def _draw_road_name(self, x: float, y: float, width: float) -> None:
    road_display = self.road_name if self.road_name else "--"
    road_size = measure_text_cached(self._font_semi_bold, road_display, 34)
    if road_size.x > width:
      road_display = road_display[:20] + "..."
    rl.draw_text_ex(self._font_semi_bold, road_display, rl.Vector2(x, y), 34, 0, COLORS.white)

  def _draw_road_details(self, x: float, y: float, width: float) -> None:
    details = []
    if self.road_context and self.road_context != "Unknown":
      details.append(self.road_context)
    if self.lanes > 0:
      details.append(f"{self.lanes} {tr('lanes')}")
    details_text = " • ".join(details) if details else "--"
    rl.draw_text_ex(self._font_medium, details_text, rl.Vector2(x, y), 26, 0, COLORS.light_grey)

  def _draw_next_speed_limit(self, x: float, y: float, width: float) -> None:
    if self.next_speed_limit > 0 and self.next_speed_limit != self.speed_limit:
      next_text = f"{tr('Next')}: {round(self.next_speed_limit)} ({self._format_distance(self.next_speed_limit_distance)})"
    else:
      next_text = f"{tr('Next')}: --"
    rl.draw_text_ex(self._font_medium, next_text, rl.Vector2(x, y), 26, 0, COLORS.light_grey)

  def _draw_curve_speeds(self, x: float, y: float, width: float) -> None:
    unit = tr("km/h") if ui_state.is_metric else tr("mph")
    vision_val = str(round(self.vision_curve_speed)) if self.vision_curve_speed > 0 else "--"
    map_val = str(round(self.map_curve_speed)) if self.map_curve_speed > 0 else "--"
    curve_text = f"{tr('Curve')}: V:{vision_val} M:{map_val} {unit}"
    rl.draw_text_ex(self._font_medium, curve_text, rl.Vector2(x, y), 24, 0, COLORS.light_grey)

  def _draw_hazard(self, x: float, y: float, width: float) -> None:
    hazard_text = f"⚠ {self.hazard}"
    rl.draw_text_ex(self._font_semi_bold, hazard_text, rl.Vector2(x, y), 26, 0, COLORS.red)

  def _draw_vienna_sign(self, x: float, y: float, width: float, height: float, speed_str: str, speed_color: rl.Color) -> None:
    center = rl.Vector2(x + width / 2, y + height / 2)
    outer_radius = min(width, height) / 2

    rl.draw_circle_v(center, outer_radius, COLORS.white)
    ring_width = outer_radius * 0.18
    rl.draw_ring(center, outer_radius - ring_width, outer_radius, 0, 360, 36, COLORS.red)

    font_size = outer_radius * (0.7 if len(speed_str) >= 3 else 0.9)
    text_size = measure_text_cached(self._font_bold, speed_str, int(font_size))
    text_pos = rl.Vector2(center.x - text_size.x / 2, center.y - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, speed_str, text_pos, font_size, 0, speed_color)

  def _draw_mutcd_sign(self, x: float, y: float, width: float, height: float, speed_str: str, speed_color: rl.Color) -> None:
    sign_rect = rl.Rectangle(x, y, width, height)
    rl.draw_rectangle_rounded(sign_rect, 0.2, 10, COLORS.white)
    rl.draw_rectangle_rounded_lines_ex(sign_rect, 0.2, 10, 3, COLORS.black)

    speed_label = tr("SPEED")
    limit_label = tr("LIMIT")
    label_size = 16

    speed_text_size = measure_text_cached(self._font_semi_bold, speed_label, label_size)
    speed_pos = rl.Vector2(x + (width - speed_text_size.x) / 2, y + 8)
    rl.draw_text_ex(self._font_semi_bold, speed_label, speed_pos, label_size, 0, COLORS.black)

    limit_text_size = measure_text_cached(self._font_semi_bold, limit_label, label_size)
    limit_pos = rl.Vector2(x + (width - limit_text_size.x) / 2, y + 26)
    rl.draw_text_ex(self._font_semi_bold, limit_label, limit_pos, label_size, 0, COLORS.black)

    font_size = 40 if len(speed_str) >= 3 else 50
    num_size = measure_text_cached(self._font_bold, speed_str, font_size)
    num_pos = rl.Vector2(x + (width - num_size.x) / 2, y + 45)
    rl.draw_text_ex(self._font_bold, speed_str, num_pos, font_size, 0, speed_color)

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
