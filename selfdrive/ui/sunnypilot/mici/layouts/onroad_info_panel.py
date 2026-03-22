"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pyray as rl
from dataclasses import dataclass
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import AlertRenderer
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import BookmarkIcon

METER_TO_KM = 0.001
METER_TO_MILE = 0.000621371


@dataclass(frozen=True)
class OnroadInfoPanelColors:
  white: rl.Color = rl.WHITE
  black: rl.Color = rl.BLACK
  red: rl.Color = rl.Color(255, 0, 0, 255)
  green: rl.Color = rl.Color(0, 255, 0, 255)
  grey: rl.Color = rl.Color(190, 195, 190, 255)
  light_grey: rl.Color = rl.Color(200, 200, 200, 255)
  dark_grey: rl.Color = rl.Color(100, 100, 100, 255)
  bg_dark: rl.Color = rl.Color(0, 0, 0, 255)
  card_bg: rl.Color = rl.Color(50, 50, 50, 200)


COLORS = OnroadInfoPanelColors()


class OnroadInfoPanel(Widget):
  def __init__(self, bookmark_callback=None):
    super().__init__()
    self.speed_limit: float = 0.0
    self.speed_limit_valid: bool = False
    self.speed_limit_offset: float = 0.0
    self.next_speed_limit: float = 0.0
    self.next_speed_limit_distance: float = 0.0
    self.road_name: str = ""
    self.current_speed: float = 0.0
    self.set_speed: float = 0.0
    self.cruise_enabled: bool = False

    self._sign_slide: float = 0.0

    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

    self._marquee_offset: float = 0.0
    self._marquee_direction: int = 1
    self._marquee_pause_timer: float = 0.0
    self._marquee_speed: float = 40.0
    self._marquee_pause_duration: float = 1.5

    self._alert_renderer = AlertRenderer()
    self._alert_alpha_filter = FirstOrderFilter(0, 0.05, 1 / gui_app.target_fps)

    self._bookmark_icon = BookmarkIcon(bookmark_callback)

  def is_swiping_left(self) -> bool:
    return self._bookmark_icon.is_swiping_left()

  def _update_state(self) -> None:
    sm = ui_state.sm
    speed_conv = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH

    if sm.valid["longitudinalPlanSP"]:
      lp_sp = sm["longitudinalPlanSP"]
      resolver = lp_sp.speedLimit.resolver
      self.speed_limit = resolver.speedLimit * speed_conv
      self.speed_limit_valid = resolver.speedLimitValid
      self.speed_limit_offset = resolver.speedLimitOffset * speed_conv

    if sm.valid["liveMapDataSP"]:
      lmd = sm["liveMapDataSP"]
      self.next_speed_limit = lmd.speedLimitAhead * speed_conv
      self.next_speed_limit_distance = lmd.speedLimitAheadDistance
      self.road_name = lmd.roadName

    if sm.updated["carState"]:
      self.current_speed = sm["carState"].vEgo * speed_conv

    if sm.valid["carState"] and sm.valid["controlsState"]:
      self.cruise_enabled = sm["carState"].cruiseState.enabled
      v_cruise_cluster = sm["carState"].vCruiseCluster
      set_speed_kph = sm["controlsState"].vCruiseDEPRECATED if v_cruise_cluster == 0.0 else v_cruise_cluster
      self.set_speed = set_speed_kph * (METER_TO_MILE / METER_TO_KM) if not ui_state.is_metric else set_speed_kph

  def _render(self, rect: rl.Rectangle) -> None:
    self._update_state()

    rl.draw_rectangle(int(rect.x), int(rect.y), int(rect.width), int(rect.height), COLORS.bg_dark)
    margin = 20
    mid_y = rect.y + rect.height / 2

    left_x = rect.x + margin

    if self.cruise_enabled:
      unit = tr("MAX")
      display_speed = self.set_speed
    else:
      unit = tr("km/h") if ui_state.is_metric else tr("MPH")
      display_speed = self.current_speed

    speed_val = str(round(display_speed))
    if self.speed_limit_valid and display_speed > self.speed_limit:
      speed_color = COLORS.red
    else:
      speed_color = COLORS.white

    rl.draw_text_ex(self._font_semi_bold, unit, rl.Vector2(left_x, mid_y - 95), 38, 0, COLORS.grey)
    rl.draw_text_ex(self._font_bold, speed_val, rl.Vector2(left_x, mid_y - 60), 110, 0, speed_color)

    sign_width = 135 if ui_state.is_metric else 135
    sign_height = 135 if ui_state.is_metric else 175

    has_next = self.next_speed_limit > 0 and self.next_speed_limit != self.speed_limit
    target_slide = 1.0 if has_next else 0.0
    slide_speed = 3.0 * rl.get_frame_time()
    if self._sign_slide < target_slide:
      self._sign_slide = min(self._sign_slide + slide_speed, target_slide)
    elif self._sign_slide > target_slide:
      self._sign_slide = max(self._sign_slide - slide_speed, target_slide)

    next_w = int(sign_width * 0.7)
    next_h = int(sign_height * 0.7)
    next_peek = int(next_w * 0.85) + 5
    centered_x = rect.x + rect.width - sign_width - margin
    shifted_x = rect.x + rect.width - sign_width - margin - next_peek
    sign_x = centered_x + (shifted_x - centered_x) * self._sign_slide
    sign_y = rect.y + (rect.height - sign_height) / 2

    road_y = mid_y + 55
    road_width = sign_x - left_x - margin
    self._draw_road_name(left_x, road_y, road_width)

    if has_next and self._sign_slide > 0.01:
      next_val = str(round(self.next_speed_limit))
      dist_str = self._format_distance(self.next_speed_limit_distance)
      next_x = sign_x + sign_width - int(next_w * 0.15)
      next_y = sign_y + (sign_height - next_h) / 2

      next_speed_color = COLORS.black
      if ui_state.is_metric:
        self._draw_vienna_sign(next_x, next_y, next_w, next_h, next_val, next_speed_color, is_upcoming=True)
      else:
        self._draw_mutcd_sign(next_x, next_y, next_w, next_h, next_val, next_speed_color, is_upcoming=True)

      dist_size = measure_text_cached(self._font_medium, dist_str, 24)
      rl.draw_text_ex(self._font_medium, dist_str, rl.Vector2(next_x + next_w / 2 - dist_size.x / 2, next_y + next_h + 4), 24, 0, COLORS.grey)

    self._draw_speed_limit_sign(sign_x, sign_y, sign_width, sign_height)

    if self.speed_limit_offset != 0 and self.speed_limit_valid:
      offset_val = str(abs(round(self.speed_limit_offset)))
      badge_sz = 42
      badge_x = sign_x + sign_width - badge_sz * 0.85
      badge_y = sign_y - badge_sz * 0.25

      if ui_state.is_metric:
        badge_r = badge_sz / 2
        badge_cx = badge_x + badge_r
        badge_cy = badge_y + badge_r
        rl.draw_circle(int(badge_cx), int(badge_cy), badge_r + 2, COLORS.dark_grey)
        rl.draw_circle(int(badge_cx), int(badge_cy), badge_r, rl.Color(60, 60, 60, 255))
        self._draw_text_centered(self._font_bold, offset_val, 24, rl.Vector2(badge_cx, badge_cy), COLORS.white)
      else:
        mutcd_badge_x = sign_x + sign_width - badge_sz * 0.65
        mutcd_badge_y = sign_y - badge_sz * 0.50
        badge_rect = rl.Rectangle(mutcd_badge_x, mutcd_badge_y, badge_sz, badge_sz)
        rl.draw_rectangle_rounded(badge_rect, 0.25, 10, rl.Color(60, 60, 60, 255))
        rl.draw_rectangle_rounded_lines_ex(badge_rect, 0.25, 10, 2, COLORS.dark_grey)
        self._draw_text_centered(self._font_bold, offset_val, 24, rl.Vector2(mutcd_badge_x + badge_sz / 2, mutcd_badge_y + badge_sz / 2), COLORS.white)

    # SCC
    speed_size = measure_text_cached(self._font_bold, speed_val, 110)
    scc_x = left_x + speed_size.x + 30
    scc_y = mid_y - 50
    self._draw_scc_icons(scc_x, scc_y)

    self._bookmark_icon.render(rect)

    if ui_state.started:
      alert_obj, no_alert = self._alert_renderer.will_render()
      self._alert_alpha_filter.update(0 if no_alert else 1)
      alpha = self._alert_alpha_filter.x
      if alpha > 0.01:
        rl.draw_rectangle(int(rect.x), int(rect.y), int(rect.width), int(rect.height), rl.Color(0, 0, 0, int(150 * alpha)))
      self._alert_renderer.render(rect)

  def _draw_scc_icons(self, x: float, y: float) -> None:
    sm = ui_state.sm
    if not sm.valid["longitudinalPlanSP"]:
      return
    scc = sm["longitudinalPlanSP"].smartCruiseControl

    box_w, box_h = 100, 36
    gap = 6
    drawn = 0

    for label, active in [("SCC-V", scc.vision.active), ("SCC-M", scc.map.active)]:
      if not active:
        continue
      bx = x
      by = y + drawn * (box_h + gap)
      rl.draw_rectangle_rounded(rl.Rectangle(bx, by, box_w, box_h), 0.3, 10, COLORS.green)
      self._draw_text_centered(self._font_bold, label, 20, rl.Vector2(bx + box_w / 2, by + box_h / 2), COLORS.black)
      drawn += 1

  def _draw_speed_limit_sign(self, x: float, y: float, sign_width: float, sign_height: float) -> None:
    speed_str = str(round(self.speed_limit)) if self.speed_limit_valid and self.speed_limit > 0 else "--"
    speed_color = COLORS.black if not self.speed_limit_valid or self.current_speed <= self.speed_limit else COLORS.red

    if ui_state.is_metric:
      self._draw_vienna_sign(x, y, sign_width, sign_height, speed_str, speed_color, is_upcoming=False)
    else:
      self._draw_mutcd_sign(x, y, sign_width, sign_height, speed_str, speed_color, is_upcoming=False)

  def _draw_road_name(self, x: float, y: float, width: float) -> None:
    road_display = self.road_name if self.road_name else "--"
    font_size = 30
    road_size = measure_text_cached(self._font_semi_bold, road_display, font_size)
    text_width = road_size.x

    if text_width <= width:
      self._marquee_offset = 0.0
      self._marquee_direction = 1
      self._marquee_pause_timer = 0.0
      rl.draw_text_ex(self._font_semi_bold, road_display, rl.Vector2(x, y), font_size, 0, COLORS.white)
    else:
      overflow = text_width - width
      dt = rl.get_frame_time()

      if self._marquee_pause_timer > 0:
        self._marquee_pause_timer -= dt
      else:
        self._marquee_offset += self._marquee_direction * self._marquee_speed * dt

        if self._marquee_offset >= overflow:
          self._marquee_offset = overflow
          self._marquee_direction = -1
          self._marquee_pause_timer = self._marquee_pause_duration
        elif self._marquee_offset <= 0:
          self._marquee_offset = 0
          self._marquee_direction = 1
          self._marquee_pause_timer = self._marquee_pause_duration

      rl.begin_scissor_mode(int(x), int(y), int(width), int(road_size.y + 4))
      text_pos = rl.Vector2(x - self._marquee_offset, y)
      rl.draw_text_ex(self._font_semi_bold, road_display, text_pos, font_size, 0, COLORS.white)
      rl.end_scissor_mode()

  def _draw_vienna_sign(self, x: float, y: float, width: float, height: float, speed_str: str, speed_color: rl.Color, is_upcoming: bool = False) -> None:
    center = rl.Vector2(x + width / 2, y + height / 2)
    outer_radius = min(width, height) / 2

    rl.draw_circle_v(center, outer_radius, COLORS.white)
    ring_width = outer_radius * 0.18
    rl.draw_ring(center, outer_radius - ring_width, outer_radius, 0, 360, 36, COLORS.red)

    font_size = outer_radius * (0.7 if len(speed_str) >= 3 else 0.9)
    text_size = measure_text_cached(self._font_bold, speed_str, int(font_size))
    text_pos = rl.Vector2(center.x - text_size.x / 2, center.y - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, speed_str, text_pos, font_size, 0, speed_color)

  def _draw_mutcd_sign(self, x: float, y: float, width: float, height: float, speed_str: str, speed_color: rl.Color, is_upcoming: bool = False) -> None:
    sign_rect = rl.Rectangle(x, y, width, height)
    rl.draw_rectangle_rounded(sign_rect, 0.35, 10, COLORS.white)

    inset = max(4, width * 0.05)
    inner_rect = rl.Rectangle(x + inset, y + inset, width - inset * 2, height - inset * 2)
    outer_radius = 0.35 * width / 2.0
    inner_radius = outer_radius - inset
    inner_roundness = inner_radius / (inner_rect.width / 2.0)
    rl.draw_rectangle_rounded_lines_ex(inner_rect, inner_roundness, 10, 3, COLORS.black)

    mid_x = x + width / 2
    label_size = max(18, int(width * 0.26))
    if is_upcoming:
      self._draw_text_centered(self._font_bold, tr("AHEAD"), label_size, rl.Vector2(mid_x, y + height * 0.27), COLORS.black)
    else:
      self._draw_text_centered(self._font_bold, tr("SPEED"), label_size, rl.Vector2(mid_x, y + height * 0.20), COLORS.black)
      self._draw_text_centered(self._font_bold, tr("LIMIT"), label_size, rl.Vector2(mid_x, y + height * 0.40), COLORS.black)

    speed_font_size = int(width * 0.52) if len(speed_str) >= 3 else int(width * 0.62)
    self._draw_text_centered(self._font_bold, speed_str, speed_font_size, rl.Vector2(mid_x, y + height * 0.72), speed_color)

  def _draw_text_centered(self, font, text, size, pos_center, color):
    sz = measure_text_cached(font, text, size)
    rl.draw_text_ex(font, text, rl.Vector2(pos_center.x - sz.x / 2, pos_center.y - sz.y / 2), size, 0, color)

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
