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
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import AlertRenderer
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import BookmarkIcon

METER_TO_KM = 0.001
METER_TO_MILE = 0.000621371

CONTENT_MARGIN = 16
SPEED_LIMIT_SIGN_WIDTH = 146
VIENNA_SIGN_SIZE = 146
MUTCD_SIGN_HEIGHT = 178
OFFSET_BADGE_SIZE = 50
OFFSET_BADGE_PANEL_PADDING = 4
MUTCD_OFFSET_SIGN_Y_SHIFT = 6
VIENNA_BADGE_X_RATIO = 0.80
VIENNA_BADGE_UPCOMING_X_RATIO = 0.70
VIENNA_BADGE_Y_RATIO = -0.82
UPCOMING_SIGN_SIZE_RATIO = 0.76
UPCOMING_SIGN_OVERLAP_RATIO = 0.05
UNIT_FONT_SIZE = 40
SPEED_FONT_SIZE = 114
ROAD_FONT_SIZE = 32
SCC_TAG_WIDTH = 78
SCC_TAG_HEIGHT = 30
SCC_TAG_GAP = 5
COLUMN_GAP = 12


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
  badge_bg: rl.Color = rl.Color(60, 60, 60, 255)


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

  def _handle_mouse_release(self, mouse_pos: MousePos) -> None:
    # Mirror stock AugmentedRoadView: suppress click while bookmark gesture active
    if not self._bookmark_icon.interacting():
      super()._handle_mouse_release(mouse_pos)

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

    left_x = rect.x + CONTENT_MARGIN

    if self.cruise_enabled:
      unit = tr("MAX")
      display_speed = self.set_speed
    else:
      unit = tr("km/h") if ui_state.is_metric else tr("MPH")
      display_speed = self.current_speed

    display_speed_text = str(round(display_speed))
    if self.speed_limit_valid and display_speed > self.speed_limit:
      speed_color = COLORS.red
    else:
      speed_color = COLORS.white

    sign_width = min(SPEED_LIMIT_SIGN_WIDTH, rect.width * 0.30)
    sign_height = VIENNA_SIGN_SIZE if ui_state.is_metric else MUTCD_SIGN_HEIGHT

    has_upcoming_limit = self.next_speed_limit > 0 and self.next_speed_limit != self.speed_limit
    target_sign_slide = 1.0 if has_upcoming_limit else 0.0
    slide_speed = 3.0 * rl.get_frame_time()
    if self._sign_slide < target_sign_slide:
      self._sign_slide = min(self._sign_slide + slide_speed, target_sign_slide)
    elif self._sign_slide > target_sign_slide:
      self._sign_slide = max(self._sign_slide - slide_speed, target_sign_slide)

    upcoming_width = int(sign_width * UPCOMING_SIGN_SIZE_RATIO)
    upcoming_height = int(sign_height * UPCOMING_SIGN_SIZE_RATIO)
    upcoming_reserved_width = int(upcoming_width * 0.85) + 5
    sign_x_without_upcoming = rect.x + rect.width - sign_width - CONTENT_MARGIN
    sign_x_with_upcoming = rect.x + rect.width - sign_width - CONTENT_MARGIN - upcoming_reserved_width
    sign_x = sign_x_without_upcoming + (sign_x_with_upcoming - sign_x_without_upcoming) * self._sign_slide
    sign_y = rect.y + (rect.height - sign_height) / 2
    if not ui_state.is_metric and self.speed_limit_offset != 0 and self.speed_limit_valid:
      sign_y += MUTCD_OFFSET_SIGN_Y_SHIFT

    readout_right = sign_x - COLUMN_GAP
    readout_width = max(1, readout_right - left_x)
    road_y = rect.y + rect.height - 44

    unit_font_size = self._fit_font_size(self._font_semi_bold, unit, readout_width, 46, UNIT_FONT_SIZE, 28)
    speed_font_size = self._fit_font_size(self._font_bold, display_speed_text, readout_width, road_y - (rect.y + 54) - 8,
                                          SPEED_FONT_SIZE, 76)
    speed_size = measure_text_cached(self._font_bold, display_speed_text, speed_font_size)
    speed_y = min(rect.y + 54, road_y - speed_size.y - 8)
    unit_y = max(rect.y + 14, speed_y - unit_font_size - 6)

    rl.draw_text_ex(self._font_semi_bold, unit, rl.Vector2(left_x, unit_y), unit_font_size, 0, COLORS.grey)
    rl.draw_text_ex(self._font_bold, display_speed_text, rl.Vector2(left_x, speed_y), speed_font_size, 0, speed_color)
    self._draw_road_name(left_x, road_y, readout_width)

    if has_upcoming_limit and self._sign_slide > 0.01:
      upcoming_speed_text = str(round(self.next_speed_limit))
      distance_text = self._format_distance(self.next_speed_limit_distance)
      upcoming_x = sign_x + sign_width - int(upcoming_width * UPCOMING_SIGN_OVERLAP_RATIO)
      upcoming_y = sign_y + (sign_height - upcoming_height) / 2

      upcoming_speed_color = COLORS.black
      if ui_state.is_metric:
        self._draw_vienna_sign(upcoming_x, upcoming_y, upcoming_width, upcoming_height, upcoming_speed_text, upcoming_speed_color, is_upcoming=True)
      else:
        self._draw_mutcd_sign(upcoming_x, upcoming_y, upcoming_width, upcoming_height, upcoming_speed_text, upcoming_speed_color, is_upcoming=True)

      distance_font_size = self._fit_font_size(self._font_medium, distance_text, upcoming_width, 30, 24, 16)
      distance_size = measure_text_cached(self._font_medium, distance_text, distance_font_size)
      rl.draw_text_ex(self._font_medium, distance_text, rl.Vector2(upcoming_x + upcoming_width / 2 - distance_size.x / 2, upcoming_y + upcoming_height),
                      distance_font_size, 0, COLORS.grey)

    self._draw_speed_limit_sign(sign_x, sign_y, sign_width, sign_height)

    if self.speed_limit_offset != 0 and self.speed_limit_valid:
      offset_text = str(abs(round(self.speed_limit_offset)))
      badge_size = OFFSET_BADGE_SIZE
      badge_rect = self._offset_badge_rect(rect, sign_x, sign_y, sign_width, sign_height, badge_size, has_upcoming_limit)

      if ui_state.is_metric:
        badge_radius = badge_size / 2
        badge_center_x = badge_rect.x + badge_radius
        badge_center_y = badge_rect.y + badge_radius
        rl.draw_circle(int(badge_center_x), int(badge_center_y), badge_radius + 2, COLORS.dark_grey)
        rl.draw_circle(int(badge_center_x), int(badge_center_y), badge_radius, COLORS.badge_bg)
        self._draw_text_centered_fit(self._font_bold, offset_text, 32, rl.Vector2(badge_center_x, badge_center_y), COLORS.white,
                                     badge_size - 10, badge_size - 8, min_size=24)
      else:
        rl.draw_rectangle_rounded(badge_rect, 0.25, 10, COLORS.badge_bg)
        rl.draw_rectangle_rounded_lines_ex(badge_rect, 0.25, 10, 2, COLORS.dark_grey)
        self._draw_text_centered_fit(self._font_bold, offset_text, 32, rl.Vector2(badge_rect.x + badge_size / 2, badge_rect.y + badge_size / 2),
                                     COLORS.white, badge_size - 10, badge_size - 8, min_size=24)

    scc_tag_x = min(left_x + speed_size.x + COLUMN_GAP, readout_right - SCC_TAG_WIDTH)
    scc_tag_y = speed_y + (speed_size.y - (SCC_TAG_HEIGHT * 2 + SCC_TAG_GAP)) / 2
    if scc_tag_x >= left_x + speed_size.x + 8:
      self._draw_scc_icons(scc_tag_x, scc_tag_y, readout_right)

    self._bookmark_icon.render(rect)

    if ui_state.started:
      alert_obj, no_alert = self._alert_renderer.will_render()
      self._alert_alpha_filter.update(0 if no_alert else 1)
      alpha = self._alert_alpha_filter.x
      if alpha > 0.01:
        rl.draw_rectangle(int(rect.x), int(rect.y), int(rect.width), int(rect.height), rl.Color(0, 0, 0, int(150 * alpha)))
      self._alert_renderer.render(rect)

  def _draw_scc_icons(self, x: float, y: float, right_limit: float) -> None:
    sm = ui_state.sm
    if not sm.valid["longitudinalPlanSP"]:
      return
    scc = sm["longitudinalPlanSP"].smartCruiseControl

    drawn = 0

    for label, active in [("SCC-V", scc.vision.active), ("SCC-M", scc.map.active)]:
      if not active:
        continue
      tag_x = x
      if tag_x + SCC_TAG_WIDTH > right_limit:
        return
      tag_y = y + drawn * (SCC_TAG_HEIGHT + SCC_TAG_GAP)
      rl.draw_rectangle_rounded(rl.Rectangle(tag_x, tag_y, SCC_TAG_WIDTH, SCC_TAG_HEIGHT), 0.3, 10, COLORS.green)
      self._draw_text_centered_fit(self._font_bold, label, 18, rl.Vector2(tag_x + SCC_TAG_WIDTH / 2, tag_y + SCC_TAG_HEIGHT / 2), COLORS.black,
                                   SCC_TAG_WIDTH - 10, SCC_TAG_HEIGHT - 4, min_size=14)
      drawn += 1

  def _draw_speed_limit_sign(self, x: float, y: float, sign_width: float, sign_height: float) -> None:
    speed_str = str(round(self.speed_limit)) if self.speed_limit_valid and self.speed_limit > 0 else "--"
    speed_color = COLORS.black if not self.speed_limit_valid or self.current_speed <= self.speed_limit else COLORS.red

    if ui_state.is_metric:
      self._draw_vienna_sign(x, y, sign_width, sign_height, speed_str, speed_color, is_upcoming=False)
    else:
      self._draw_mutcd_sign(x, y, sign_width, sign_height, speed_str, speed_color, is_upcoming=False)

  def _draw_road_name(self, x: float, y: float, width: float) -> None:
    if width <= 0:
      return

    road_display = self.road_name if self.road_name else "--"
    font_size = self._fit_font_size(self._font_semi_bold, road_display, width, 38, ROAD_FONT_SIZE, 28)
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
    self._draw_text_centered_fit(self._font_bold, speed_str, int(font_size), center, speed_color, width * 0.72, height * 0.50, min_size=24)

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
      self._draw_text_centered_fit(self._font_bold, tr("AHEAD"), int(width * 0.34), rl.Vector2(mid_x, y + height * 0.28), COLORS.black,
                                   width * 0.94, height * 0.32, min_size=20)
    else:
      self._draw_text_centered_fit(self._font_bold, tr("SPEED"), label_size, rl.Vector2(mid_x, y + height * 0.20), COLORS.black,
                                   width * 0.84, height * 0.24, min_size=16)
      self._draw_text_centered_fit(self._font_bold, tr("LIMIT"), label_size, rl.Vector2(mid_x, y + height * 0.40), COLORS.black,
                                   width * 0.84, height * 0.24, min_size=16)

    speed_font_size = int(width * 0.60) if len(speed_str) >= 3 else int(width * 0.72)
    self._draw_text_centered_fit(self._font_bold, speed_str, speed_font_size, rl.Vector2(mid_x, y + height * 0.72), speed_color,
                                 width * 0.90, height * 0.52, min_size=32)

  def _draw_text_centered(self, font, text, size, pos_center, color):
    sz = measure_text_cached(font, text, size)
    rl.draw_text_ex(font, text, rl.Vector2(pos_center.x - sz.x / 2, pos_center.y - sz.y / 2), size, 0, color)

  def _draw_text_centered_fit(self, font, text, size, pos_center, color, max_width: float, max_height: float, min_size: int = 10):
    size = self._fit_font_size(font, text, max_width, max_height, size, min_size)
    self._draw_text_centered(font, text, size, pos_center, color)

  def _fit_font_size(self, font, text: str, max_width: float, max_height: float, max_size: int | float, min_size: int) -> int:
    size = int(max_size)
    while size > min_size:
      text_size = measure_text_cached(font, text, size)
      if text_size.x <= max_width and text_size.y <= max_height:
        return size
      size -= 2
    return min_size

  def _offset_badge_rect(self, panel_rect: rl.Rectangle, sign_x: float, sign_y: float, sign_width: float, sign_height: float,
                         badge_size: float, has_upcoming_limit: bool) -> rl.Rectangle:
    if ui_state.is_metric:
      radius = min(sign_width, sign_height) / 2
      center_x = sign_x + sign_width / 2
      center_y = sign_y + sign_height / 2
      badge_x_ratio = VIENNA_BADGE_UPCOMING_X_RATIO if has_upcoming_limit else VIENNA_BADGE_X_RATIO
      badge_center_x = center_x + radius * badge_x_ratio
      badge_center_y = center_y + radius * VIENNA_BADGE_Y_RATIO
      badge_x = badge_center_x - badge_size / 2
      badge_y = badge_center_y - badge_size / 2
    else:
      badge_x = sign_x + sign_width - badge_size * 0.45
      badge_y = sign_y - badge_size * 0.75

    return rl.Rectangle(
      self._clamp(
        badge_x,
        panel_rect.x + OFFSET_BADGE_PANEL_PADDING,
        panel_rect.x + panel_rect.width - badge_size - OFFSET_BADGE_PANEL_PADDING,
      ),
      self._clamp(
        badge_y,
        panel_rect.y + OFFSET_BADGE_PANEL_PADDING,
        panel_rect.y + panel_rect.height - badge_size - OFFSET_BADGE_PANEL_PADDING,
      ),
      badge_size,
      badge_size,
    )

  @staticmethod
  def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))

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
