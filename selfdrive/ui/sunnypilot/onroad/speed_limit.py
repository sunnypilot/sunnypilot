"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from dataclasses import dataclass
import math
import pyray as rl

from cereal import custom
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.onroad.hud_renderer import UI_CONFIG
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode as SpeedLimitMode
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

METER_TO_FOOT = 3.28084
METER_TO_MILE = 0.000621371
AHEAD_THRESHOLD = 5
SET_SPEED_NA = 255
KM_TO_MILE = 0.621371

AssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState
SpeedLimitSource = custom.LongitudinalPlanSP.SpeedLimit.Source


@dataclass(frozen=True)
class Colors:
  WHITE = rl.WHITE
  BLACK = rl.BLACK
  RED = rl.Color(235, 32, 32, 255)
  GREY = rl.Color(145, 155, 149, 255)
  DARK_GREY = rl.Color(77, 77, 77, 255)
  SUB_BG = rl.Color(0, 0, 0, 180)
  MUTCD_LINES = rl.Color(255, 255, 255, 100)


class SpeedLimitRenderer(Widget):
  def __init__(self):
    super().__init__()

    self.speed_limit = 0.0
    self.speed_limit_last = 0.0
    self.speed_limit_offset = 0.0
    self.speed_limit_valid = False
    self.speed_limit_last_valid = False
    self.speed_limit_final_last = 0.0
    self.speed_limit_source = SpeedLimitSource.none
    self.speed_limit_assist_state = AssistState.disabled

    self.speed_limit_ahead = 0.0
    self.speed_limit_ahead_dist = 0.0
    self.speed_limit_ahead_dist_prev = 0.0
    self.speed_limit_ahead_valid = False
    self.speed_limit_ahead_frame = 0

    self.assist_frame = 0
    self.is_cruise_set: bool = False
    self.is_cruise_available: bool = True
    self.set_speed: float = SET_SPEED_NA
    self.speed: float = 0.0
    self.v_ego_cluster_seen: bool = False

    self.font_bold = gui_app.font(FontWeight.BOLD)
    self.font_demi = gui_app.font(FontWeight.SEMI_BOLD)
    self.font_norm = gui_app.font(FontWeight.NORMAL)
    self._sign_alpha_filter = FirstOrderFilter(1.0, 0.5, 1 / gui_app.target_fps)

    arrow_size = 90
    self._arrow_up = gui_app.texture("../../sunnypilot/selfdrive/assets/img_plus_arrow_up.png", arrow_size, arrow_size)
    self._arrow_down = gui_app.texture("../../sunnypilot/selfdrive/assets/img_minus_arrow_down.png", arrow_size, arrow_size)

  @property
  def speed_conv(self):
    return CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH

  def update(self):
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      self.set_speed = SET_SPEED_NA
      self.speed = 0.0
      return

    if sm.updated["longitudinalPlanSP"]:
      lp_sp = sm["longitudinalPlanSP"]
      resolver = lp_sp.speedLimit.resolver
      assist = lp_sp.speedLimit.assist

      self.speed_limit = resolver.speedLimit * self.speed_conv
      self.speed_limit_last = resolver.speedLimitLast * self.speed_conv
      self.speed_limit_offset = resolver.speedLimitOffset * self.speed_conv
      self.speed_limit_valid = resolver.speedLimitValid
      self.speed_limit_last_valid = resolver.speedLimitLastValid
      self.speed_limit_final_last = resolver.speedLimitFinalLast * self.speed_conv
      self.speed_limit_source = resolver.source
      self.speed_limit_assist_state = assist.state

    if sm.updated["liveMapDataSP"]:
      lmd = sm["liveMapDataSP"]
      self.speed_limit_ahead_valid = lmd.speedLimitAheadValid
      self.speed_limit_ahead = lmd.speedLimitAhead * self.speed_conv
      self.speed_limit_ahead_dist = lmd.speedLimitAheadDistance

      if self.speed_limit_ahead_dist < self.speed_limit_ahead_dist_prev and self.speed_limit_ahead_frame < AHEAD_THRESHOLD:
        self.speed_limit_ahead_frame += 1
      elif self.speed_limit_ahead_dist > self.speed_limit_ahead_dist_prev and self.speed_limit_ahead_frame > 0:
        self.speed_limit_ahead_frame -= 1

      self.speed_limit_ahead_dist_prev = self.speed_limit_ahead_dist

    controls_state = sm['controlsState']
    car_state = sm["carState"]

    v_cruise_cluster = car_state.vCruiseCluster
    self.set_speed = (
      controls_state.vCruiseDEPRECATED if v_cruise_cluster == 0.0 else v_cruise_cluster
    )
    self.is_cruise_set = 0 < self.set_speed < SET_SPEED_NA
    self.is_cruise_available = self.set_speed != -1

    if self.is_cruise_set and not ui_state.is_metric:
      self.set_speed *= KM_TO_MILE

    self.v_ego_cluster_seen = self.v_ego_cluster_seen or car_state.vEgoCluster != 0.0
    v_ego = car_state.vEgoCluster if self.v_ego_cluster_seen else car_state.vEgo
    self.speed = max(0.0, v_ego * self.speed_conv)

  @staticmethod
  def _draw_text_centered(font, text, size, pos_center, color):
    sz = measure_text_cached(font, text, size)
    rl.draw_text_ex(font, text, rl.Vector2(pos_center.x - sz.x / 2, pos_center.y - sz.y / 2), size, 0, color)

  def _render(self, rect: rl.Rectangle):
    width = UI_CONFIG.set_speed_width_metric if ui_state.is_metric else UI_CONFIG.set_speed_width_imperial
    x = rect.x + 60 + width + 30 - 6
    y = rect.y + 45 - 6

    sign_rect = rl.Rectangle(x, y, width, UI_CONFIG.set_speed_height + 6 * 2)

    if self.speed_limit_assist_state == AssistState.preActive:
      self.assist_frame += 1
      pulse_value = 0.65 + 0.35 * math.sin(self.assist_frame * math.pi / gui_app.target_fps)
      alpha = self._sign_alpha_filter.update(pulse_value)
    else:
      self.assist_frame = 0
      alpha = self._sign_alpha_filter.update(1.0)

    if ui_state.speed_limit_mode != SpeedLimitMode.off:
      self._draw_sign_main(sign_rect, alpha)
      if self.speed_limit_assist_state == AssistState.preActive:
        self._draw_pre_active_arrow(sign_rect)
      else:
        self._draw_ahead_info(sign_rect)

  def _draw_sign_main(self, rect, alpha=1.0):
    speed_limit_warning_enabled = ui_state.speed_limit_mode >= SpeedLimitMode.warning
    has_limit = self.speed_limit_valid or self.speed_limit_last_valid
    is_overspeed = has_limit and round(self.speed_limit_final_last) < round(self.speed)

    limit_str = str(round(self.speed_limit_last)) if has_limit else "---"
    sub_text = ""
    if self.speed_limit_offset != 0:
      sign = "" if self.speed_limit_offset > 0 else "-"
      sub_text = f"{sign}{round(abs(self.speed_limit_offset))}"

    txt_color = Colors.BLACK
    if speed_limit_warning_enabled and is_overspeed:
      txt_color = Colors.RED
    elif not self.speed_limit_valid:
      txt_color = Colors.GREY

    if ui_state.is_metric:
      self._render_vienna(rect, limit_str, sub_text, txt_color, has_limit, alpha)
    else:
      self._render_mutcd(rect, limit_str, sub_text, txt_color, has_limit, alpha)

  def _draw_pre_active_arrow(self, sign_rect):
    set_speed_rounded = round(self.set_speed)
    limit_rounded = round(self.speed_limit_final_last)

    bounce_frequency = 2.0 * math.pi / (gui_app.target_fps * 2.5)
    bounce_offset = int(20 * math.sin(self.assist_frame * bounce_frequency))

    sign_margin = 12
    arrow_spacing = int(sign_margin * 1.4)
    arrow_x = sign_rect.x + sign_rect.width + arrow_spacing

    if set_speed_rounded < limit_rounded:
      arrow_y = sign_rect.y + (sign_rect.height - self._arrow_up.height) / 2 + bounce_offset
      rl.draw_texture(self._arrow_up, int(arrow_x), int(arrow_y), rl.WHITE)
    elif set_speed_rounded > limit_rounded:
      arrow_y = sign_rect.y + (sign_rect.height - self._arrow_down.height) / 2 - bounce_offset
      rl.draw_texture(self._arrow_down, int(arrow_x), int(arrow_y), rl.WHITE)

  def _render_vienna(self, rect, val, sub, color, has_limit, alpha=1.0):
    center = rl.Vector2(rect.x + rect.width / 2, rect.y + rect.height / 2)
    radius = (rect.width + 18) / 2

    white = rl.color_alpha(Colors.WHITE, alpha)
    red = rl.color_alpha(Colors.RED, alpha)
    black = rl.color_alpha(Colors.BLACK, alpha)
    dark_grey = rl.color_alpha(Colors.DARK_GREY, alpha)
    text_color = rl.color_alpha(color, alpha)

    rl.draw_circle_v(center, radius, white)
    rl.draw_ring(center, radius * 0.75, radius, 0, 360, 36, red)

    font_size = 70 if len(val) >= 3 else 85
    self._draw_text_centered(self.font_bold, val, font_size, center, text_color)

    if sub and has_limit:
      s_radius = radius * 0.4
      s_center = rl.Vector2(rect.x + rect.width - s_radius / 2, rect.y + s_radius / 2)

      rl.draw_circle_v(s_center, s_radius, black)
      rl.draw_ring(s_center, s_radius - 3, s_radius, 0, 360, 36, dark_grey)

      font_scale = 0.5 if len(sub) < 3 else 0.45
      self._draw_text_centered(self.font_bold, sub, int(s_radius * 2 * font_scale), s_center, white)

  def _render_mutcd(self, rect, val, sub, color, has_limit, alpha=1.0):
    white = rl.color_alpha(Colors.WHITE, alpha)
    black = rl.color_alpha(Colors.BLACK, alpha)
    dark_grey = rl.color_alpha(Colors.DARK_GREY, alpha)
    text_color = rl.color_alpha(color, alpha)

    rl.draw_rectangle_rounded(rect, 0.35, 10, white)

    inner = rl.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    outer_radius = 0.35 * rect.width / 2.0
    inner_radius = outer_radius - 10.0
    inner_roundness = inner_radius / (inner.width / 2.0)

    rl.draw_rectangle_rounded_lines_ex(inner, inner_roundness, 10, 4, black)

    self._draw_text_centered(self.font_demi, "SPEED", 40, rl.Vector2(rect.x + rect.width / 2, rect.y + 40), black)
    self._draw_text_centered(self.font_demi, "LIMIT", 40, rl.Vector2(rect.x + rect.width / 2, rect.y + 80), black)
    self._draw_text_centered(self.font_bold, val, 90, rl.Vector2(rect.x + rect.width / 2, rect.y + 150), text_color)

    if sub and has_limit:
      box_sz = rect.width * 0.3
      overlap = box_sz * 0.2
      s_rect = rl.Rectangle(rect.x + rect.width - box_sz / 1.5 + overlap, rect.y - box_sz / 1.25 + overlap, box_sz, box_sz)

      rl.draw_rectangle_rounded(s_rect, 0.35, 10, black)
      rl.draw_rectangle_rounded_lines_ex(s_rect, 0.35, 10, 6, dark_grey)

      f_scale = 0.6 if len(sub) < 3 else 0.475
      self._draw_text_centered(self.font_bold, sub, int(box_sz * f_scale), rl.Vector2(s_rect.x + box_sz / 2, s_rect.y + box_sz / 2), white)

  def _draw_ahead_info(self, sign_rect):
    source_is_map = self.speed_limit_source == SpeedLimitSource.map
    valid = self.speed_limit_ahead_valid and self.speed_limit_ahead > 0 and self.speed_limit_ahead != self.speed_limit

    if not (valid and source_is_map):
      return

    rect = rl.Rectangle(sign_rect.x + (sign_rect.width - 170) / 2, sign_rect.y + sign_rect.height + 10, 170, 160)
    rl.draw_rectangle_rounded(rect, 0.35, 10, Colors.SUB_BG)
    rl.draw_rectangle_rounded_lines_ex(rect, 0.35, 10, 3, Colors.MUTCD_LINES)

    mid_x = rect.x + rect.width / 2
    self._draw_text_centered(self.font_demi, "AHEAD", 40, rl.Vector2(mid_x, rect.y + 28), Colors.GREY)
    self._draw_text_centered(self.font_bold, str(round(self.speed_limit_ahead)), 70, rl.Vector2(mid_x, rect.y + 82), Colors.WHITE)
    self._draw_text_centered(self.font_norm, self._format_dist(self.speed_limit_ahead_dist), 36, rl.Vector2(mid_x, rect.y + 134), Colors.GREY)

  @staticmethod
  def _format_dist(d):
    # metric
    if ui_state.is_metric:
      if d < 50:
        return tr("Near")

      if d >= 1000:
        return f"{d / 1000:.1f} km"

      d_rounded = round(d, -1) if d < 200 else round(d, -2)
      return f"{int(d_rounded)} m"

    # imperial
    d_ft = d * METER_TO_FOOT
    if d_ft < 100:
      return tr("Near")

    if d_ft >= 900:
      return f"{d * METER_TO_MILE:.1f} mi"

    if d_ft < 500:
      return f"{int(round(d_ft / 50) * 50)} ft"

    return f"{int(round(d_ft / 100) * 100)} ft"
