import math
import os
from enum import IntEnum
from dataclasses import dataclass
import pyray as rl

from openpilot.common.constants import CV
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
    asset_path = os.path.join(os.path.dirname(__file__), "../assets")
    self.arrow_up = self._load_tex(asset_path, "img_plus_arrow_up.png")
    self.arrow_down = self._load_tex(asset_path, "img_minus_arrow_down.png")

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
    self.road_name = ""

    self.font_bold = gui_app.font(FontWeight.BOLD)
    self.font_demi = gui_app.font(FontWeight.SEMI_BOLD)
    self.font_norm = gui_app.font(FontWeight.NORMAL)

  @property
  def speed_conv(self):
    return CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH

  def _load_tex(self, base, name):
    path = os.path.join(base, name)
    return rl.load_texture(path.encode()) if os.path.exists(path) else None

  def _update_state(self):
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
      self.road_name = lmd.roadName

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
    origin = rl.Vector2(pos_center.x - sz.x/2, pos_center.y - sz.y/2)
    rl.draw_text_ex(font, text, origin, size, 0, color)

  def _render(self, rect: rl.Rectangle):
    w, h = (200, 204) if self.is_metric else (172, 204)
    x, y = rect.x + (298 if self.is_metric else 290), rect.y + 50
    sign_rect = rl.Rectangle(x, y, w, h)

    show_sign = True
    if self.speed_limit_assist_state == 1:
      self.assist_frame += 1
      show_sign = (self.assist_frame % UI_FREQ) >= (UI_FREQ / 2.5)
      self._draw_pre_active_arrow(sign_rect)
    else:
      self.assist_frame = 0
      show_sign = self.speed_limit_assist_active or self.speed_limit_valid or self.speed_limit_last_valid

    if show_sign:
      self._draw_sign_main(sign_rect)
      if self.speed_limit_assist_state != 1:
        self._draw_ahead_info(sign_rect)

    self._draw_road_name(rect)

  def _draw_sign_main(self, rect):
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
      self._render_vienna(rect, limit_str, sub_text, txt_color, has_limit)
    else:
      self._render_mutcd(rect, limit_str, sub_text, txt_color, has_limit)

  def _render_vienna(self, rect, val, sub, color, has_limit):
    center = rl.Vector2(rect.x + rect.width/2, rect.y + rect.height/2)
    radius = rect.width / 2

    rl.draw_circle_v(center, radius, Colors.WHITE)
    rl.draw_ring(center, radius * 0.88, radius, 0, 360, 36, Colors.RED)

    f_size = 70 if len(val) >= 3 else 85
    self._draw_text_centered(self.font_bold, val, f_size, center, color)

    if sub and has_limit:
      s_radius = radius * 0.4
      s_center = rl.Vector2(rect.x + rect.width - s_radius/1.25, rect.y + s_radius/2)

      rl.draw_circle_v(s_center, s_radius, Colors.BLACK)
      rl.draw_ring(s_center, s_radius - 3, s_radius, 0, 360, 36, Colors.DARK_GREY)

      f_scale = 0.5 if len(sub) < 3 else 0.45
      self._draw_text_centered(self.font_bold, sub, int(s_radius * 2 * f_scale), s_center, Colors.WHITE)

  def _render_mutcd(self, rect, val, sub, color, has_limit):
    rl.draw_rectangle_rounded(rect, 0.16, 12, Colors.WHITE)
    inner = rl.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20)
    rl.draw_rectangle_rounded_lines_ex(inner, 0.1, 12, 4, Colors.BLACK)

    self._draw_text_centered(self.font_demi, "SPEED", 40, rl.Vector2(rect.x + rect.width/2, rect.y + 40), Colors.BLACK)
    self._draw_text_centered(self.font_demi, "LIMIT", 40, rl.Vector2(rect.x + rect.width/2, rect.y + 80), Colors.BLACK)
    self._draw_text_centered(self.font_bold, val, 90, rl.Vector2(rect.x + rect.width/2, rect.y + 135), color)

    if sub and has_limit:
      box_sz = rect.width * 0.3
      overlap = box_sz * 0.2
      s_rect = rl.Rectangle(rect.x + rect.width - box_sz/1.5 + overlap, rect.y - box_sz/1.25 + overlap, box_sz, box_sz)

      rl.draw_rectangle_rounded(s_rect, 0.2, 8, Colors.BLACK)
      rl.draw_rectangle_rounded_lines_ex(s_rect, 0.2, 8, 6, Colors.DARK_GREY)

      f_scale = 0.6 if len(sub) < 3 else 0.475
      self._draw_text_centered(self.font_bold, sub, int(box_sz * f_scale),
                               rl.Vector2(s_rect.x + box_sz/2, s_rect.y + box_sz/2), Colors.WHITE)

  def _draw_ahead_info(self, sign_rect):
    source_is_map = self.speed_limit_source == 0 or str(self.speed_limit_source).lower() == "map"
    valid = (self.speed_limit_ahead_valid and
             self.speed_limit_ahead > 0 and
             self.speed_limit_ahead != self.speed_limit)

    if not (valid and source_is_map):
      return

    rect = rl.Rectangle(sign_rect.x + (sign_rect.width - 170)/2, sign_rect.y + sign_rect.height + 10, 170, 160)
    rl.draw_rectangle_rounded(rect, 0.1, 10, Colors.SUB_BG)
    rl.draw_rectangle_rounded_lines_ex(rect, 0.1, 10, 3, Colors.MUTCD_LINES)

    mid_x = rect.x + rect.width/2
    self._draw_text_centered(self.font_demi, "AHEAD", 40, rl.Vector2(mid_x, rect.y + 24), Colors.GREY)
    self._draw_text_centered(self.font_bold, str(round(self.speed_limit_ahead)), 70, rl.Vector2(mid_x, rect.y + 75), Colors.WHITE)
    self._draw_text_centered(self.font_norm, self._format_dist(self.speed_limit_ahead_dist), 40, rl.Vector2(mid_x, rect.y + 130), Colors.GREY)

  def _draw_pre_active_arrow(self, rect):
    if not self.arrow_up or not self.arrow_down:
      return

    bounce = 20 * math.sin(self.assist_frame * (2.0 * math.pi / UI_FREQ))
    x = rect.x + rect.width + 16
    y = rect.y + rect.height / 2 - 45

    tex = self.arrow_up if self.set_speed < self.speed_limit_final_last else self.arrow_down
    direction = 1 if self.set_speed < self.speed_limit_final_last else -1
    rl.draw_texture_ex(tex, rl.Vector2(x, y + (bounce * direction)), 0, 1.0, Colors.WHITE)

  def _draw_road_name(self, rect: rl.Rectangle):
    if not self.road_name:
      return

    text = self.road_name
    text_size = measure_text_cached(self.font_demi, text, 46)

    padding = 40
    rect_width = max(200, min(text_size.x + padding, rect.width - 40))

    road_rect = rl.Rectangle(
      rect.x + rect.width / 2 - rect_width / 2,
      rect.y - 4,
      rect_width,
      60
    )

    rl.draw_rectangle_rounded(road_rect, 0.2, 10, rl.Color(0, 0, 0, 120))

    max_text_width = road_rect.width - 20
    if text_size.x > max_text_width:
      while text_size.x > max_text_width and len(text) > 3:
        text = text[:-1]
        text_size = measure_text_cached(self.font_demi, text + "...", 46)
      text = text + "..."

    self._draw_text_centered(self.font_demi, text, 46,
                             rl.Vector2(road_rect.x + road_rect.width/2,
                                        road_rect.y + road_rect.height/2),
                             rl.Color(255, 255, 255, 200))

  def _format_dist(self, d):
    if self.is_metric:
      if d < 50: return tr("Near")
      return f"{d/1000:.1f} km" if d >= 1000 else f"{round(d, -1 if d < 200 else -2)} m"

    d_ft = d * METER_TO_FOOT
    if d_ft < 100: return tr("Near")
    return f"{d * METER_TO_MILE:.1f} mi" if d_ft >= 900 else f"{round(d_ft, -1 if d_ft < 500 else -2)} ft"