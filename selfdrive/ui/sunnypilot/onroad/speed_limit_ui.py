"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum
from dataclasses import dataclass
import math
import pyray as rl

from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

METER_TO_FOOT = 3.28084
METER_TO_MILE = 0.000621371
AHEAD_THRESHOLD = 5
UI_FREQ = 20


@dataclass(frozen=True)
class Colors:
  WHITE = rl.WHITE
  BLACK = rl.BLACK
  RED = rl.RED
  GREY = rl.Color(145, 155, 149, 255)
  DARK_GREY = rl.Color(77, 77, 77, 255)
  SUB_BG = rl.Color(0, 0, 0, 180)
  MUTCD_LINES = rl.Color(255, 255, 255, 100)


class SpeedLimitMode(IntEnum):
  OFF = 0
  WARNING = 1
  ASSIST = 2


class SpeedLimitRenderer(Widget):
  def __init__(self):
    super().__init__()

    self.speed_limit = 0.0
    self.speed_limit_last = 0.0
    self.speed_limit_offset = 0.0
    self.speed_limit_valid = False
    self.speed_limit_last_valid = False
    self.speed_limit_final_last = 0.0
    self.speed_limit_source = 0
    self.speed_limit_assist_state = 0
    self.speed_limit_assist_active = False

    self.speed_limit_ahead = 0.0
    self.speed_limit_ahead_dist = 0.0
    self.speed_limit_ahead_dist_prev = 0.0
    self.speed_limit_ahead_valid = False
    self.speed_limit_ahead_frame = 0

    self.assist_frame = 0
    self.speed = 0.0
    self.set_speed = 0.0
    self.is_metric = False

    self.font_bold = gui_app.font(FontWeight.BOLD)
    self.font_demi = gui_app.font(FontWeight.SEMI_BOLD)
    self.font_norm = gui_app.font(FontWeight.NORMAL)
    self._sign_alpha_filter = FirstOrderFilter(1.0, 0.5, 1 / UI_FREQ)

    arrow_size = 90
    self._arrow_up = gui_app.texture("../../sunnypilot/selfdrive/assets/img_plus_arrow_up.png", arrow_size, arrow_size)
    self._arrow_down = gui_app.texture("../../sunnypilot/selfdrive/assets/img_minus_arrow_down.png", arrow_size, arrow_size)

  @property
  def speed_conv(self):
    return CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH

  def update(self):
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    self.is_metric = ui_state.is_metric
    conv = self.speed_conv

    if sm.updated["longitudinalPlanSP"]:
      lp = sm["longitudinalPlanSP"]
      res, assist = lp.speedLimit.resolver, lp.speedLimit.assist
      self.speed_limit = res.speedLimit * conv
      self.speed_limit_last = res.speedLimitLast * conv
      self.speed_limit_offset = res.speedLimitOffset * conv
      self.speed_limit_valid = res.speedLimitValid
      self.speed_limit_last_valid = res.speedLimitLastValid
      self.speed_limit_final_last = res.speedLimitFinalLast * conv
      self.speed_limit_source = res.source
      self.speed_limit_assist_state = assist.state
      self.speed_limit_assist_active = assist.active

    if sm.updated["liveMapDataSP"]:
      lmd = sm["liveMapDataSP"]
      self.speed_limit_ahead_valid = lmd.speedLimitAheadValid
      self.speed_limit_ahead = lmd.speedLimitAhead * conv
      self.speed_limit_ahead_dist = lmd.speedLimitAheadDistance

      if self.speed_limit_ahead_dist < self.speed_limit_ahead_dist_prev and self.speed_limit_ahead_frame < AHEAD_THRESHOLD:
        self.speed_limit_ahead_frame += 1
      elif self.speed_limit_ahead_dist > self.speed_limit_ahead_dist_prev and self.speed_limit_ahead_frame > 0:
        self.speed_limit_ahead_frame -= 1

      self.speed_limit_ahead_dist_prev = self.speed_limit_ahead_dist

    cs = sm["carState"]
    self.set_speed = cs.cruiseState.speed * conv
    v_ego = cs.vEgoCluster if cs.vEgoCluster != 0.0 else cs.vEgo
    self.speed = max(0.0, v_ego * conv)

  def _draw_text_centered(self, font, text, size, pos_center, color):
    sz = measure_text_cached(font, text, size)
    rl.draw_text_ex(font, text, rl.Vector2(pos_center.x - sz.x / 2, pos_center.y - sz.y / 2), size, 0, color)

  def _render(self, rect: rl.Rectangle):
    w, h = (200, 204) if self.is_metric else (172, 204)
    x, y = rect.x + (298 if self.is_metric else 290), rect.y + 50
    sign_rect = rl.Rectangle(x, y, w, h)

    if self.speed_limit_assist_state == 1:
      self.assist_frame += 1
      pulse_value = 0.65 + 0.35 * math.sin(self.assist_frame * math.pi / UI_FREQ)
      alpha = self._sign_alpha_filter.update(pulse_value)
      show_sign = True
    else:
      self.assist_frame = 0
      alpha = self._sign_alpha_filter.update(1.0)
      show_sign = self.speed_limit_assist_active or self.speed_limit_valid or self.speed_limit_last_valid

    if show_sign:
      self._draw_sign_main(sign_rect, alpha)
      if self.speed_limit_assist_state == 1:
        self._draw_pre_active_arrow(sign_rect)
      else:
        self._draw_ahead_info(sign_rect)

  def _draw_sign_main(self, rect, alpha=1.0):
    has_limit = self.speed_limit_valid or self.speed_limit_last_valid
    is_overspeed = has_limit and round(self.speed_limit_final_last) < round(self.speed)

    limit_str = str(round(self.speed_limit_last)) if has_limit else "---"
    sub_text = ""
    if self.speed_limit_offset != 0:
      sign = "" if self.speed_limit_offset > 0 else "-"
      sub_text = f"{sign}{round(abs(self.speed_limit_offset))}"

    txt_color = Colors.BLACK
    if is_overspeed:
      txt_color = Colors.RED
    elif not self.speed_limit_valid:
      txt_color = Colors.GREY

    if self.is_metric:
      self._render_vienna(rect, limit_str, sub_text, txt_color, has_limit, alpha)
    else:
      self._render_mutcd(rect, limit_str, sub_text, txt_color, has_limit, alpha)

  def _draw_pre_active_arrow(self, sign_rect):
    set_speed_rounded = round(self.set_speed)
    limit_rounded = round(self.speed_limit_final_last)

    bounce_frequency = 2.0 * math.pi / (UI_FREQ * 2.5)
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
    radius = rect.width / 2

    white = rl.Color(255, 255, 255, int(255 * alpha))
    red = rl.Color(255, 0, 0, int(255 * alpha))

    if hasattr(color, 'r'):
      text_color = rl.Color(color.r, color.g, color.b, int(255 * alpha))
    else:
      text_color = rl.Color(color[0], color[1], color[2], int(255 * alpha))

    black = rl.Color(0, 0, 0, int(255 * alpha))
    dark_grey = rl.Color(77, 77, 77, int(255 * alpha))

    rl.draw_circle_v(center, radius, white)
    rl.draw_ring(center, radius * 0.88, radius, 0, 360, 36, red)

    f_size = 70 if len(val) >= 3 else 85
    self._draw_text_centered(self.font_bold, val, f_size, center, text_color)

    if sub and has_limit:
      s_radius = radius * 0.4
      s_center = rl.Vector2(rect.x + rect.width - s_radius / 1.25, rect.y + s_radius / 2)

      rl.draw_circle_v(s_center, s_radius, black)
      rl.draw_ring(s_center, s_radius - 3, s_radius, 0, 360, 36, dark_grey)

      f_scale = 0.5 if len(sub) < 3 else 0.45
      self._draw_text_centered(self.font_bold, sub, int(s_radius * 2 * f_scale), s_center, white)

  def _render_mutcd(self, rect, val, sub, color, has_limit, alpha=1.0):
    white = rl.Color(255, 255, 255, int(255 * alpha))
    black = rl.Color(0, 0, 0, int(255 * alpha))
    dark_grey = rl.Color(77, 77, 77, int(255 * alpha))

    if hasattr(color, 'r'):
      text_color = rl.Color(color.r, color.g, color.b, int(255 * alpha))
    else:
      text_color = rl.Color(color[0], color[1], color[2], int(255 * alpha))

    rl.draw_rectangle_rounded(rect, 0.16, 12, white)
    inner = rl.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    rl.draw_rectangle_rounded_lines_ex(inner, 0.1, 12, 4, black)

    self._draw_text_centered(self.font_demi, "SPEED", 40, rl.Vector2(rect.x + rect.width / 2, rect.y + 40), black)
    self._draw_text_centered(self.font_demi, "LIMIT", 40, rl.Vector2(rect.x + rect.width / 2, rect.y + 80), black)
    self._draw_text_centered(self.font_bold, val, 90, rl.Vector2(rect.x + rect.width / 2, rect.y + 135), text_color)

    if sub and has_limit:
      box_sz = rect.width * 0.3
      overlap = box_sz * 0.2
      s_rect = rl.Rectangle(rect.x + rect.width - box_sz / 1.5 + overlap, rect.y - box_sz / 1.25 + overlap, box_sz, box_sz)

      rl.draw_rectangle_rounded(s_rect, 0.2, 8, black)
      rl.draw_rectangle_rounded_lines_ex(s_rect, 0.2, 8, 6, dark_grey)

      f_scale = 0.6 if len(sub) < 3 else 0.475
      self._draw_text_centered(self.font_bold, sub, int(box_sz * f_scale), rl.Vector2(s_rect.x + box_sz / 2, s_rect.y + box_sz / 2), white)

  def _draw_ahead_info(self, sign_rect):
    source_is_map = self.speed_limit_source == 0 or str(self.speed_limit_source).lower() == "map"
    valid = self.speed_limit_ahead_valid and self.speed_limit_ahead > 0 and self.speed_limit_ahead != self.speed_limit

    if not (valid and source_is_map):
      return

    rect = rl.Rectangle(sign_rect.x + (sign_rect.width - 170) / 2, sign_rect.y + sign_rect.height + 10, 170, 160)
    rl.draw_rectangle_rounded(rect, 0.1, 10, Colors.SUB_BG)
    rl.draw_rectangle_rounded_lines_ex(rect, 0.1, 10, 3, Colors.MUTCD_LINES)

    mid_x = rect.x + rect.width / 2
    self._draw_text_centered(self.font_demi, "AHEAD", 40, rl.Vector2(mid_x, rect.y + 24), Colors.GREY)
    self._draw_text_centered(self.font_bold, str(round(self.speed_limit_ahead)), 70, rl.Vector2(mid_x, rect.y + 75), Colors.WHITE)
    self._draw_text_centered(self.font_norm, self._format_dist(self.speed_limit_ahead_dist), 40, rl.Vector2(mid_x, rect.y + 130), Colors.GREY)

  def _format_dist(self, d):
    if self.is_metric:
      if d < 50:
        return tr("Near")
      return f"{d / 1000:.1f} km" if d >= 1000 else f"{round(d, -1 if d < 200 else -2)} m"

    d_ft = d * METER_TO_FOOT
    if d_ft < 100:
      return tr("Near")
    return f"{d * METER_TO_MILE:.1f} mi" if d_ft >= 900 else f"{round(d_ft, -1 if d_ft < 500 else -2)} ft"
