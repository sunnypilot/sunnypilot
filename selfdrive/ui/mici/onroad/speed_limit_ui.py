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

from cereal import log
EventName = log.OnroadEvent.EventName

METER_TO_KM = 0.001
METER_TO_FOOT = 3.28084
METER_TO_MILE = 0.000621371
UI_FREQ = 20
SPEED_LIMIT_AHEAD_VALID_FRAME_THRESHOLD = 5

SPEED_LIMIT_SIZE_METRIC = 95
SPEED_LIMIT_SIZE_IMPERIAL_W = 88
SPEED_LIMIT_SIZE_IMPERIAL_H = 110


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
  yellow: rl.Color = rl.Color(255, 200, 0, 255)


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
    self._hide_for_hud: bool = False

    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

    from openpilot.common.filter_simple import FirstOrderFilter
    self._alpha_filter = FirstOrderFilter(0.0, 0.15, 1 / gui_app.target_fps)

  def set_hide_for_hud(self, hide: bool):
    self._hide_for_hud = hide

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

    self.speed_limit_mode = SpeedLimitMode.ASSIST  # TODO: HELPPP

  def _render(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm

    should_show = True
    if sm['onroadEvents']:
      should_show = False

    ss = sm['selfdriveState']
    if ss.alertSize != 0:
      should_show = False

    if self._hide_for_hud:
      should_show = False

    if self.speed_limit_assist_state == 1:
      self.speed_limit_assist_frame += 1
      self.assist_pulse_alpha = 180 + int(40 * math.sin(self.speed_limit_assist_frame / 6))
      show_speed_limit = True
    else:
      self.speed_limit_assist_frame = 0
      self.assist_pulse_alpha = 255
      show_speed_limit = self.speed_limit_mode != SpeedLimitMode.OFF

    if not show_speed_limit:
      should_show = False

    self._alpha_filter.update(1.0 if should_show else 0.0)
    if self._alpha_filter.x < 0.01:
      return

    margin_left = 21
    margin_bottom = 120

    if ui_state.is_metric:
      sign_width = SPEED_LIMIT_SIZE_METRIC
      sign_height = SPEED_LIMIT_SIZE_METRIC
    else:
      sign_width = SPEED_LIMIT_SIZE_IMPERIAL_W
      sign_height = SPEED_LIMIT_SIZE_IMPERIAL_H

    x = rect.x + margin_left
    y = rect.y + rect.height - margin_bottom - sign_height

    sign_rect = rl.Rectangle(x, y, sign_width, sign_height)

    if ui_state.is_metric:
      self._draw_vienna_sign_compact(sign_rect)
    else:
      self._draw_mutcd_sign_compact(sign_rect)

    if self.speed_limit_assist_state != 1:
      self._draw_upcoming_compact(sign_rect)

  def _pulse_element(self, frame: int) -> bool:
    if frame % UI_FREQ < (UI_FREQ / 2.5):
      return False
    return True

  def _draw_vienna_sign_compact(self, sign_rect: rl.Rectangle) -> None:
    """Draw compact EU Vienna"""
    speed_limit_warning_enabled = self.speed_limit_mode >= SpeedLimitMode.WARNING
    has_speed_limit = self.speed_limit_valid or self.speed_limit_last_valid
    overspeed = has_speed_limit and round(self.speed_limit_final_last) < round(self.current_speed)
    speed_limit_str = str(round(self.speed_limit_last)) if has_speed_limit else "---"

    ring_color = COLORS.red
    speed_color_base = COLORS.black
    bg_alpha = 230

    if speed_limit_warning_enabled and overspeed:
      speed_color_base = COLORS.red
      ring_color = COLORS.red
    elif not self.speed_limit_valid and self.speed_limit_last_valid:
      speed_color_base = COLORS.grey
      ring_color = COLORS.grey
      bg_alpha = 180

    alpha_multiplier = self._alpha_filter.x

    shadow_offset = 3
    center = rl.Vector2(
      sign_rect.x + sign_rect.width / 2 + shadow_offset,
      sign_rect.y + sign_rect.height / 2 + shadow_offset
    )
    radius = sign_rect.width / 2
    rl.draw_circle_v(center, radius, rl.Color(0, 0, 0, int(80 * alpha_multiplier)))

    center = rl.Vector2(sign_rect.x + sign_rect.width / 2, sign_rect.y + sign_rect.height / 2)
    rl.draw_circle_v(center, radius, rl.Color(255, 255, 255, int(bg_alpha * alpha_multiplier)))

    if isinstance(ring_color, tuple):
      ring_r, ring_g, ring_b, _ = ring_color
    else:
      ring_r, ring_g, ring_b = ring_color.r, ring_color.g, ring_color.b
    ring_color_alpha = rl.Color(ring_r, ring_g, ring_b, int(255 * alpha_multiplier))
    rl.draw_ring(center, radius * 0.82, radius * 0.95, 0, 360, 36, ring_color_alpha)

    font_size = 36 if len(speed_limit_str) >= 3 else 50  # Bigger text
    text_size = measure_text_cached(self._font_bold, speed_limit_str, font_size)
    text_pos = rl.Vector2(center.x - text_size.x / 2, center.y - text_size.y / 2)

    if isinstance(speed_color_base, tuple):
      speed_r, speed_g, speed_b, _ = speed_color_base
    else:
      speed_r, speed_g, speed_b = speed_color_base.r, speed_color_base.g, speed_color_base.b
    speed_color = rl.Color(speed_r, speed_g, speed_b, int(255 * alpha_multiplier))
    rl.draw_text_ex(self._font_bold, speed_limit_str, text_pos, font_size, 0, speed_color)

    if self.speed_limit_offset != 0 and has_speed_limit:
      self._draw_offset_compact_circular(sign_rect, center, radius)

  def _draw_mutcd_sign_compact(self, sign_rect: rl.Rectangle) -> None:
    """Draw compact US MUTCD"""
    speed_limit_warning_enabled = self.speed_limit_mode >= SpeedLimitMode.WARNING
    has_speed_limit = self.speed_limit_valid or self.speed_limit_last_valid
    overspeed = has_speed_limit and round(self.speed_limit_final_last) < round(self.current_speed)
    speed_limit_str = str(round(self.speed_limit_last)) if has_speed_limit else "---"

    if speed_limit_warning_enabled and overspeed:
      speed_color_base = COLORS.red
    elif not self.speed_limit_valid and self.speed_limit_last_valid:
      speed_color_base = COLORS.grey
    else:
      speed_color_base = COLORS.black

    alpha_multiplier = self._alpha_filter.x

    shadow_offset = 3
    shadow_rect = rl.Rectangle(
      sign_rect.x + shadow_offset,
      sign_rect.y + shadow_offset,
      sign_rect.width,
      sign_rect.height
    )
    rl.draw_rectangle_rounded(shadow_rect, 0.15, 10, rl.Color(0, 0, 0, int(80 * alpha_multiplier)))
    rl.draw_rectangle_rounded(sign_rect, 0.15, 10, rl.Color(255, 255, 255, int(255 * alpha_multiplier)))
    rl.draw_rectangle_rounded_lines_ex(sign_rect, 0.15, 10, 3, rl.Color(0, 0, 0, int(255 * alpha_multiplier)))

    speed_text = tr("SPEED")
    limit_text = tr("LIMIT")

    header_font_size = 28
    speed_size = measure_text_cached(self._font_semi_bold, speed_text, header_font_size)
    limit_size = measure_text_cached(self._font_semi_bold, limit_text, header_font_size)

    speed_pos = rl.Vector2(sign_rect.x + (sign_rect.width - speed_size.x) / 2, sign_rect.y + 3)
    limit_pos = rl.Vector2(sign_rect.x + (sign_rect.width - limit_size.x) / 2, sign_rect.y + 26)

    text_color = rl.Color(0, 0, 0, int(255 * alpha_multiplier))
    rl.draw_text_ex(self._font_semi_bold, speed_text, speed_pos, header_font_size, 0, text_color)
    rl.draw_text_ex(self._font_semi_bold, limit_text, limit_pos, header_font_size, 0, text_color)

    number_font_size = 40 if len(speed_limit_str) >= 3 else 60  # Bigger text
    number_size = measure_text_cached(self._font_bold, speed_limit_str, number_font_size)
    number_pos = rl.Vector2(
      sign_rect.x + (sign_rect.width - number_size.x) / 2,
      sign_rect.y + 45
    )

    if isinstance(speed_color_base, tuple):
      r, g, b, _ = speed_color_base
    else:
      r, g, b = speed_color_base.r, speed_color_base.g, speed_color_base.b
    speed_color = rl.Color(r, g, b, int(255 * alpha_multiplier))
    rl.draw_text_ex(self._font_bold, speed_limit_str, number_pos, number_font_size, 0, speed_color)

    if self.speed_limit_offset != 0 and has_speed_limit:
      return
      #self._draw_offset_compact_rectangular(sign_rect)

  def _draw_offset_compact_circular(self, sign_rect: rl.Rectangle, center: rl.Vector2, radius: float) -> None:
    """Draw compact offset sign"""
    offset_str = ("+" if self.speed_limit_offset > 0 else "") + str(round(self.speed_limit_offset))

    pill_width = 35
    pill_height = 18
    pill_x = center.x - pill_width / 2
    pill_y = sign_rect.y + sign_rect.height + 5

    pill_rect = rl.Rectangle(pill_x, pill_y, pill_width, pill_height)
    rl.draw_rectangle_rounded(pill_rect, 0.5, 10, rl.Color(0, 0, 0, int(166 * self._alpha_filter.x)))

    offset_font_size = 13
    offset_size = measure_text_cached(self._font_semi_bold, offset_str, offset_font_size)
    offset_pos = rl.Vector2(
      pill_x + (pill_width - offset_size.x) / 2,
      pill_y + (pill_height - offset_size.y) / 2
    )
    rl.draw_text_ex(self._font_semi_bold, offset_str, offset_pos, offset_font_size, 0,
                    rl.Color(255, 255, 255, int(255 * self._alpha_filter.x)))

  def _draw_offset_compact_rectangular(self, sign_rect: rl.Rectangle) -> None:
    """Draw compact offset MUTCD"""
    offset_str = ("+" if self.speed_limit_offset > 0 else "") + str(round(self.speed_limit_offset))

    box_width = 32
    box_height = 17
    box_x = sign_rect.x + (sign_rect.width - box_width) / 2
    box_y = sign_rect.y + sign_rect.height + 5

    box_rect = rl.Rectangle(box_x, box_y, box_width, box_height)
    rl.draw_rectangle_rounded(box_rect, 0.3, 10, rl.Color(0, 0, 0, int(166 * self._alpha_filter.x)))

    offset_font_size = 12
    offset_size = measure_text_cached(self._font_semi_bold, offset_str, offset_font_size)
    offset_pos = rl.Vector2(
      box_x + (box_width - offset_size.x) / 2,
      box_y + (box_height - offset_size.y) / 2
    )
    rl.draw_text_ex(self._font_semi_bold, offset_str, offset_pos, offset_font_size, 0,
                    rl.Color(255, 255, 255, int(255 * self._alpha_filter.x)))

  def _draw_upcoming_compact(self, sign_rect: rl.Rectangle) -> None:
    """Draw upcoming speed limit indicator to the right"""
    speed_limit_ahead = (
          self.speed_limit_ahead_valid and
          self.speed_limit_ahead > 0 and
          self.speed_limit_ahead != self.speed_limit and
          self.speed_limit_ahead_valid_frame > 0 and
          self.speed_limit_source == 0
    )

    if not speed_limit_ahead:
      return

    speed_str = str(round(self.speed_limit_ahead))
    distance_str = self._format_distance(self.speed_limit_ahead_distance)
    alpha_multiplier = self._alpha_filter.x

    spacing = 10
    ahead_size = 60
    ahead_x = sign_rect.x + sign_rect.width + spacing
    ahead_y = sign_rect.y + (sign_rect.height - ahead_size) / 2
    ahead_rect = rl.Rectangle(ahead_x, ahead_y, ahead_size, ahead_size)

    center = rl.Vector2(ahead_rect.x + ahead_rect.width / 2, ahead_rect.y + ahead_rect.height / 2)
    radius = ahead_size / 2
    rl.draw_circle_v(center, radius, rl.Color(0, 0, 0, int(160 * alpha_multiplier)))
    border_color = rl.Color(255, 255, 255, int(75 * alpha_multiplier))
    rl.draw_ring(center, radius * 0.88, radius * 0.95, 0, 360, 36, border_color)

    speed_font_size = 26
    speed_size = measure_text_cached(self._font_bold, speed_str, speed_font_size)
    speed_pos = rl.Vector2(center.x - speed_size.x / 2, center.y - speed_size.y / 2 - 6)
    rl.draw_text_ex(self._font_bold, speed_str, speed_pos, speed_font_size, 0,
                    rl.Color(255, 255, 255, int(255 * alpha_multiplier)))

    distance_font_size = 11
    distance_size = measure_text_cached(self._font_medium, distance_str, distance_font_size)
    distance_pos = rl.Vector2(center.x - distance_size.x / 2, center.y + 9)
    rl.draw_text_ex(self._font_medium, distance_str, distance_pos, distance_font_size, 0,
                    rl.Color(200, 200, 200, int(255 * alpha_multiplier)))

  def _format_distance(self, distance: float) -> str:
    """Format distance string"""
    if ui_state.is_metric:
      if distance < 50:
        return tr("Near")
      if distance >= 1000:
        return f"{distance * METER_TO_KM:.1f}km"

      if distance < 200:
        rounded = max(10, self._round_to_interval(distance, 10, 5))
      else:
        rounded = self._round_to_interval(distance, 100, 50)
      return f"{rounded}m"
    else:
      distance_ft = distance * METER_TO_FOOT
      if distance_ft < 100:
        return tr("Near")
      if distance_ft >= 900:
        return f"{distance * METER_TO_MILE:.1f}mi"

      if distance_ft < 500:
        rounded = max(50, self._round_to_interval(distance_ft, 50, 25))
      else:
        rounded = self._round_to_interval(distance_ft, 100, 50)
      return f"{rounded}ft"

  def _round_to_interval(self, distance: float, interval: int, threshold: int) -> int:
    base = int(distance / interval) * interval
    return base + interval if (distance - base >= threshold) else base

  def _draw_pre_active_glow(self, sign_rect: rl.Rectangle) -> None:
    """Draw pulsing glow effect for pre-active state"""
    bounce_frequency = 2.0 * math.pi / UI_FREQ
    glow_intensity = 0.5 + 0.5 * abs(math.sin(self.speed_limit_assist_frame * bounce_frequency))

    center = rl.Vector2(sign_rect.x + sign_rect.width / 2, sign_rect.y + sign_rect.height / 2)

    if ui_state.is_metric:
      radius = sign_rect.width / 2
      glow_color = rl.Color(0, 255, 0, int(100 * glow_intensity))
      rl.draw_circle_v(center, radius + 8, glow_color)
    else:
      glow_rect = rl.Rectangle(
        sign_rect.x - 4,
        sign_rect.y - 4,
        sign_rect.width + 8,
        sign_rect.height + 8
      )
      glow_color = rl.Color(0, 255, 0, int(100 * glow_intensity))
      rl.draw_rectangle_rounded(glow_rect, 0.15, 10, glow_color)
