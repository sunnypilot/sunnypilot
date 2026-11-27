"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.common.filter_simple import BounceFilter
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.expressions import (
  DrivingSnapshot,
  PALETTE,
  display_speed_and_set_speed,
)
from openpilot.selfdrive.ui.ui_state import UIStatus
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached


class SpeedArcRenderer:
  """Reference-video-inspired color-coded speed + curved arc gauge and subtle Set-Speed badge."""

  SPEED_FONT_SIZE = 114
  UNIT_FONT_SIZE = 24
  BADGE_SPEED_FONT_SIZE = 32

  def __init__(self):
    dt = 1.0 / max(gui_app.target_fps, 1)
    self._font_display: rl.Font = gui_app.font(FontWeight.DISPLAY)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)
    self._arc_progress = BounceFilter(0.0, 0.11, dt, bounce=2.4)

  def _speed_color(self, snap: DrivingSnapshot) -> tuple[int, int, int]:
    if snap.status == UIStatus.OVERRIDE or snap.a_ego > 1.8:
      return (255, 205, 65)    # Warm yellow/amber
    if snap.status == UIStatus.ENGAGED:
      return (85, 238, 150)    # Vibrant green
    if snap.status == UIStatus.LAT_ONLY:
      return PALETTE["lat_only"]
    return (240, 245, 255)     # Crisp white

  def render_speed_mode(
    self,
    rect: rl.Rectangle,
    snap: DrivingSnapshot,
    alpha: float,
    cruising_smoothly: bool,
    reason: str,
  ) -> None:
    if alpha < 0.01:
      return

    t = rl.get_time()
    cur_speed, set_speed = display_speed_and_set_speed(snap)
    sr, sg, sb = self._speed_color(snap)
    speed_color = rl.Color(sr, sg, sb, int(255 * alpha))
    sub_color = rl.Color(255, 255, 255, int(195 * alpha))

    cx = rect.x + rect.width / 2.0
    # Subtle breathing float so speed mode is alive and never frozen
    float_y = math.sin(t * 2.2) * 2.0

    # Top accent above speed: MAX set-speed pill or gently pulsing heart
    if reason == "set_speed" and set_speed is not None:
      pill_text = f"{tr('MAX')} {set_speed}"
      pill_sz = measure_text_cached(self._font_semi_bold, pill_text, 26)
      pill_w = pill_sz.x + 28
      pill_h = 34
      pill_rect = rl.Rectangle(cx - pill_w / 2.0, rect.y + 14 + float_y * 0.5, pill_w, pill_h)
      rl.draw_rectangle_rounded(pill_rect, 0.5, 14, rl.Color(sr, sg, sb, int(48 * alpha)))
      rl.draw_rectangle_rounded_lines_ex(pill_rect, 0.5, 14, 2.0, rl.Color(sr, sg, sb, int(180 * alpha)))
      rl.draw_text_ex(
        self._font_semi_bold,
        pill_text,
        rl.Vector2(cx - pill_sz.x / 2.0, pill_rect.y + (pill_h - pill_sz.y) / 2.0),
        26,
        0,
        speed_color,
      )
    elif cruising_smoothly:
      heart_r = 10.0 * (1.0 + 0.10 * math.sin(t * 4.5))
      self._draw_tiny_heart(cx, rect.y + 30 + float_y * 0.5, heart_r, rl.Color(255, 118, 168, int(240 * alpha)))
    elif set_speed is not None:
      max_lbl = f"{tr('MAX')} {set_speed}"
      lbl_sz = measure_text_cached(self._font_medium, max_lbl, self.UNIT_FONT_SIZE)
      rl.draw_text_ex(
        self._font_medium,
        max_lbl,
        rl.Vector2(cx - lbl_sz.x / 2.0, rect.y + 18 + float_y * 0.5),
        self.UNIT_FONT_SIZE,
        0,
        sub_color,
      )

    # Big centered speed number
    speed_text = str(cur_speed)
    speed_sz = measure_text_cached(self._font_display, speed_text, self.SPEED_FONT_SIZE)
    speed_y = rect.y + rect.height / 2.0 - speed_sz.y / 2.0 - 8.0 + float_y
    rl.draw_text_ex(
      self._font_display,
      speed_text,
      rl.Vector2(cx - speed_sz.x / 2.0, speed_y),
      self.SPEED_FONT_SIZE,
      0,
      speed_color,
    )

    # Unit beside speed (small & subtle)
    unit_text = tr("km/h") if snap.is_metric else tr("mph")
    rl.draw_text_ex(
      self._font_medium,
      unit_text,
      rl.Vector2(cx + speed_sz.x / 2.0 + 10.0, speed_y + speed_sz.y - 34.0),
      self.UNIT_FONT_SIZE,
      0,
      rl.Color(255, 255, 255, int(150 * alpha)),
    )

    # Curved arc speedometer gauge underneath (matches reference video)
    max_ref = float(set_speed) if (set_speed is not None and set_speed > 0) else (130.0 if snap.is_metric else 85.0)
    raw_frac = max(0.0, min(1.0, cur_speed / max_ref))
    frac = max(0.0, min(1.0, self._arc_progress.update(raw_frac)))

    arc_center = rl.Vector2(cx, rect.y + rect.height + 74.0)
    inner_r = 104.0
    outer_r = 114.0
    mid_r = (inner_r + outer_r) / 2.0
    cap_r = (outer_r - inner_r) / 2.0
    start_deg = 228.0
    end_deg = 312.0
    span_deg = end_deg - start_deg

    # Track background arc with rounded caps
    track_col = rl.Color(255, 255, 255, int(45 * alpha))
    rl.draw_ring(arc_center, inner_r, outer_r, start_deg, end_deg, 32, track_col)
    for deg in (start_deg, end_deg):
      rad = math.radians(deg)
      rl.draw_circle(int(arc_center.x + math.cos(rad) * mid_r), int(arc_center.y + math.sin(rad) * mid_r), cap_r, track_col)

    # Active glowing arc + bright animated tip pip
    if frac > 0.01:
      active_end = start_deg + span_deg * frac
      glow_pulse = 0.78 + 0.22 * math.sin(t * 3.5)
      rl.draw_ring(
        arc_center,
        inner_r - 4.0,
        outer_r + 4.0,
        start_deg,
        active_end,
        32,
        rl.Color(sr, sg, sb, int(65 * glow_pulse * alpha)),
      )
      rl.draw_ring(arc_center, inner_r, outer_r, start_deg, active_end, 32, speed_color)

      # Rounded start cap & bright glowing tip pip
      s_rad = math.radians(start_deg)
      e_rad = math.radians(active_end)
      rl.draw_circle(int(arc_center.x + math.cos(s_rad) * mid_r), int(arc_center.y + math.sin(s_rad) * mid_r), cap_r, speed_color)
      tip_x = arc_center.x + math.cos(e_rad) * mid_r
      tip_y = arc_center.y + math.sin(e_rad) * mid_r
      rl.draw_circle_gradient(
        rl.Vector2(tip_x, tip_y),
        14.0,
        rl.Color(255, 255, 255, int(140 * glow_pulse * alpha)),
        rl.Color(sr, sg, sb, 0),
      )
      rl.draw_circle(int(tip_x), int(tip_y), cap_r + 1.5, rl.Color(255, 255, 255, int(235 * alpha)))

  def render_corner_badge(self, rect: rl.Rectangle, snap: DrivingSnapshot, alpha: float) -> None:
    """Subtle top-left Set-Speed / engagement pill visible during normal hero-face mode."""
    if alpha < 0.01:
      return

    t = rl.get_time()
    _, set_speed = display_speed_and_set_speed(snap)
    sr, sg, sb = self._speed_color(snap)
    dot_pulse = 0.72 + 0.28 * math.sin(t * 3.0)

    x = rect.x + 16.0
    y = rect.y + 12.0

    if set_speed is not None:
      text = str(set_speed)
      sz = measure_text_cached(self._font_semi_bold, text, self.BADGE_SPEED_FONT_SIZE)
      pill_w = sz.x + 48.0
      pill_h = 38.0
      pill_rec = rl.Rectangle(x, y, pill_w, pill_h)
      rl.draw_rectangle_rounded(pill_rec, 0.5, 14, rl.Color(255, 255, 255, int(22 * alpha)))
      rl.draw_rectangle_rounded_lines_ex(pill_rec, 0.5, 14, 1.5, rl.Color(255, 255, 255, int(35 * alpha)))
      rl.draw_circle(int(x + 16), int(y + pill_h / 2.0), 5.0, rl.Color(sr, sg, sb, int(235 * dot_pulse * alpha)))
      rl.draw_text_ex(
        self._font_semi_bold,
        text,
        rl.Vector2(x + 28.0, y + (pill_h - sz.y) / 2.0),
        self.BADGE_SPEED_FONT_SIZE,
        0,
        rl.Color(255, 255, 255, int(210 * alpha)),
      )
    else:
      rl.draw_circle(int(x + 10), int(y + 12), 5.5, rl.Color(sr, sg, sb, int(200 * dot_pulse * alpha)))

  def _draw_tiny_heart(self, cx: float, cy: float, radius: float, color: rl.Color) -> None:
    lobe_r = radius * 0.55
    lobe_y = cy - radius * 0.2
    rl.draw_circle(int(cx - lobe_r * 0.8), int(lobe_y), lobe_r, color)
    rl.draw_circle(int(cx + lobe_r * 0.8), int(lobe_y), lobe_r, color)
    rl.draw_triangle(
      rl.Vector2(cx - radius * 0.95, lobe_y + lobe_r * 0.2),
      rl.Vector2(cx, cy + radius * 0.9),
      rl.Vector2(cx + radius * 0.95, lobe_y + lobe_r * 0.2),
      color,
    )
