"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.common.filter_simple import BounceFilter, FirstOrderFilter
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.expressions import (
  EyeGlyph,
  EyeTarget,
  MouthGlyph,
)
from openpilot.system.ui.lib.application import FontWeight, gui_app


class ProceduralFaceRenderer:
  """60 FPS bubbly EMO-inspired procedural vector face renderer for 536x240 MICI OLED."""

  EYE_SPACING = 166.0  # distance between left and right eye centers

  def __init__(self):
    dt = 1.0 / max(gui_app.target_fps, 1)
    # Bubbly spring-overshoot filters for organic squash-and-stretch motion
    self._w = BounceFilter(104.0, 0.08, dt, bounce=3.2)
    self._h = BounceFilter(112.0, 0.08, dt, bounce=3.2)
    self._gaze_x = BounceFilter(0.0, 0.09, dt, bounce=2.6)
    self._gaze_y = BounceFilter(0.0, 0.09, dt, bounce=2.4)
    self._bounce_y = BounceFilter(0.0, 0.06, dt, bounce=3.5)
    self._tilt_y = BounceFilter(0.0, 0.09, dt, bounce=2.4)
    self._scale_x = BounceFilter(1.0, 0.06, dt, bounce=3.6)
    self._scale_y = BounceFilter(1.0, 0.06, dt, bounce=3.6)

    # Crisp first-order filters for eyelids, roundness, and smooth color blending
    self._roundness = FirstOrderFilter(0.48, 0.08, dt)
    self._top_lid = FirstOrderFilter(0.0, 0.035, dt)
    self._bottom_lid = FirstOrderFilter(0.0, 0.035, dt)
    self._top_slant = FirstOrderFilter(0.0, 0.07, dt)
    self._r = FirstOrderFilter(218.0, 0.14, dt)
    self._g = FirstOrderFilter(232.0, 0.14, dt)
    self._b = FirstOrderFilter(248.0, 0.14, dt)
    self._bsm_alpha = FirstOrderFilter(0.0, 0.07, dt)
    self._blinker_alpha = FirstOrderFilter(0.0, 0.06, dt)

    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)

  def render(self, rect: rl.Rectangle, target: EyeTarget, alpha: float = 1.0, y_shift: float = 0.0) -> None:
    if alpha < 0.01:
      return

    t = rl.get_time()

    # Update bubbly & smooth filters
    w = max(24.0, self._w.update(target.width) * self._scale_x.update(target.scale_x))
    h = max(20.0, self._h.update(target.height) * self._scale_y.update(target.scale_y))
    roundness = max(0.15, min(0.85, self._roundness.update(target.roundness)))
    top_lid = max(0.0, min(0.95, self._top_lid.update(target.top_lid)))
    bottom_lid = max(0.0, min(0.95, self._bottom_lid.update(target.bottom_lid)))
    top_slant = self._top_slant.update(target.top_slant)
    gaze_x = self._gaze_x.update(target.gaze_x)
    gaze_y = self._gaze_y.update(target.gaze_y)
    bounce_y = self._bounce_y.update(target.bounce_y)
    tilt_y = self._tilt_y.update(target.tilt_y)

    r = max(0, min(255, int(self._r.update(target.color[0]))))
    g = max(0, min(255, int(self._g.update(target.color[1]))))
    b = max(0, min(255, int(self._b.update(target.color[2]))))

    # Optional alert brightness pulse
    pulse = 1.0
    if target.pulse_speed > 0.0:
      pulse = 0.72 + 0.28 * (0.5 + 0.5 * math.sin(t * target.pulse_speed * math.tau))

    eff_alpha = max(0.0, min(1.0, alpha * pulse))
    core_color = rl.Color(r, g, b, int(255 * eff_alpha))

    # Ambient edge accents (blind spot glow, blinker chevrons, boost speed lines)
    bsm_a = self._bsm_alpha.update(1.0 if target.blind_spot_side != 0 else 0.0)
    if bsm_a > 0.02 and target.blind_spot_side != 0:
      self._draw_bsm_edge_glow(rect, target.blind_spot_side, bsm_a * alpha)

    blinker_a = self._blinker_alpha.update(1.0 if target.blinker_side != 0 else 0.0)
    if blinker_a > 0.02 and target.blinker_side != 0:
      self._draw_blinker_indicator(rect, target.blinker_side, blinker_a * alpha, t)

    if target.show_speed_lines:
      self._draw_speed_lines(rect, core_color, eff_alpha, t)

    cx = rect.x + rect.width / 2.0 + gaze_x
    cy = rect.y + rect.height / 2.0 - 8.0 + gaze_y + bounce_y + y_shift

    left_cx = cx - self.EYE_SPACING / 2.0
    right_cx = cx + self.EYE_SPACING / 2.0
    left_cy = cy - tilt_y
    right_cy = cy + tilt_y

    # Subtle 3D perspective scaling when glancing left/right
    left_scale = 1.0 - max(0.0, gaze_x / 210.0)
    right_scale = 1.0 + min(0.0, gaze_x / 210.0)

    for side_idx, (ecx, ecy, scale) in enumerate(((left_cx, left_cy, left_scale), (right_cx, right_cy, right_scale))):
      ew = w * scale
      eh = h * scale
      slant = top_slant if side_idx == 0 else -top_slant
      glyph = EyeGlyph.CRESCENT if (side_idx == 1 and target.wink_right) else target.glyph
      self._draw_eye(ecx, ecy, ew, eh, roundness, top_lid, bottom_lid, slant, glyph, core_color, eff_alpha, gaze_x, gaze_y, t)

    if target.mouth != MouthGlyph.NONE:
      self._draw_mouth(cx, cy + h * 0.72, target.mouth, core_color)

    if target.show_zzz:
      self._draw_floating_zzz(right_cx + w * 0.58, right_cy - h * 0.35, core_color, eff_alpha, t)

    if target.show_hearts:
      self._draw_floating_mini_hearts(cx, cy - h * 0.58, core_color, eff_alpha, t)

  def _draw_bsm_edge_glow(self, rect: rl.Rectangle, side: int, alpha: float) -> None:
    glow_w = 56
    amber = rl.Color(255, 160, 30, int(145 * alpha))
    clear = rl.Color(255, 160, 30, 0)
    if side < 0:
      rl.draw_rectangle_gradient_h(int(rect.x), int(rect.y), glow_w, int(rect.height), amber, clear)
    else:
      rl.draw_rectangle_gradient_h(int(rect.x + rect.width - glow_w), int(rect.y), glow_w, int(rect.height), clear, amber)

  def _draw_blinker_indicator(self, rect: rl.Rectangle, side: int, alpha: float, t: float) -> None:
    """Crisp pulsing directional chevron on the left/right edge for turn signals."""
    pulse = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 8.4))
    col = rl.Color(85, 240, 140, int(235 * pulse * alpha))
    glow = rl.Color(85, 240, 140, int(65 * pulse * alpha))
    cy = rect.y + rect.height / 2.0
    sign = 1.0 if side > 0 else -1.0
    base_x = (rect.x + rect.width - 34.0) if side > 0 else (rect.x + 34.0)

    for idx in range(2):
      ox = base_x - sign * idx * 14.0
      p_top = rl.Vector2(ox - sign * 10.0, cy - 18.0)
      p_tip = rl.Vector2(ox + sign * 8.0, cy)
      p_bot = rl.Vector2(ox - sign * 10.0, cy + 18.0)
      rl.draw_line_ex(p_top, p_tip, 9.0, glow)
      rl.draw_line_ex(p_tip, p_bot, 9.0, glow)
      rl.draw_line_ex(p_top, p_tip, 4.5, col)
      rl.draw_line_ex(p_tip, p_bot, 4.5, col)

  def _draw_speed_lines(self, rect: rl.Rectangle, color: rl.Color, alpha: float, t: float) -> None:
    """Energetic animated speed streaks on the screen edges during sharp acceleration."""
    for i in range(4):
      phase = (t * 4.5 + i * 0.25) % 1.0
      y = rect.y + 68.0 + i * 44.0
      line_len = 26.0 + 22.0 * math.sin(phase * math.pi)
      a = int(170 * math.sin(phase * math.pi) * alpha)
      col = rl.Color(color.r, color.g, color.b, a)
      # Left & right symmetrical streaks
      lx = rect.x + 12.0 + (1.0 - phase) * 28.0
      rx = rect.x + rect.width - 12.0 - (1.0 - phase) * 28.0
      rl.draw_line_ex(rl.Vector2(lx, y), rl.Vector2(lx + line_len, y), 3.5, col)
      rl.draw_line_ex(rl.Vector2(rx - line_len, y), rl.Vector2(rx, y), 3.5, col)

  def _draw_floating_zzz(self, x: float, y: float, color: rl.Color, alpha: float, t: float) -> None:
    """Softly drifting Zzz bubbles so sleepy/standstill state is continuously animated."""
    for idx, ch in enumerate(("z", "Z")):
      phase = (t * 0.55 + idx * 0.5) % 1.0
      zx = x + phase * 18.0 + math.sin(phase * math.tau) * 4.0
      zy = y - phase * 34.0
      fade = math.sin(phase * math.pi)
      size = 20 + idx * 8
      col = rl.Color(color.r, color.g, color.b, int(190 * fade * alpha))
      rl.draw_text_ex(self._font_semi_bold, ch, rl.Vector2(zx, zy), size, 0, col)

  def _draw_floating_mini_hearts(self, cx: float, y: float, color: rl.Color, alpha: float, t: float) -> None:
    """Floating mini-hearts above the face during pet/bookmark reactions."""
    for idx, dx in enumerate((-62.0, 0.0, 62.0)):
      phase = (t * 1.4 + idx * 0.33) % 1.0
      hx = cx + dx + math.sin(phase * math.tau) * 6.0
      hy = y - phase * 26.0
      fade = math.sin(phase * math.pi)
      col = rl.Color(color.r, color.g, color.b, int(210 * fade * alpha))
      self._draw_heart_eye(hx, hy, 8.5, col, fade * alpha, with_glow=False)

  def _draw_eye(
    self,
    cx: float,
    cy: float,
    w: float,
    h: float,
    roundness: float,
    top_lid: float,
    bottom_lid: float,
    slant_deg: float,
    glyph: EyeGlyph,
    color: rl.Color,
    alpha: float,
    gaze_x: float,
    gaze_y: float,
    t: float,
  ) -> None:
    if glyph == EyeGlyph.STAR:
      self._draw_star_eye(cx, cy, min(w, h) * 0.48, color, alpha, t)
      return
    if glyph == EyeGlyph.HEART:
      self._draw_heart_eye(cx, cy, min(w, h) * 0.48, color, alpha, with_glow=True)
      return
    if glyph == EyeGlyph.CRESCENT:
      self._draw_crescent_eye(cx, cy, w, h, color, alpha)
      return

    # Silky radial OLED bloom (zero banding, consistent with star & heart eyes)
    visible_frac = max(0.25, 1.0 - top_lid - bottom_lid)
    bloom_r = max(w, h) * 0.78 * (0.65 + 0.35 * visible_frac)
    rl.draw_circle_gradient(
      rl.Vector2(cx, cy),
      bloom_r,
      rl.Color(color.r, color.g, color.b, int(92 * visible_frac * alpha)),
      rl.Color(color.r, color.g, color.b, 0),
    )

    # Crisp eye core
    core_rec = rl.Rectangle(cx - w / 2.0, cy - h / 2.0, w, h)
    rl.draw_rectangle_rounded(core_rec, min(0.85, roundness), 24, color)

    # Glossy dual specular catchlights (gently track gaze + micro-shimmer)
    glint_dx = gaze_x * 0.08 + math.sin(t * 2.8) * 1.2
    glint_dy = gaze_y * 0.08 + math.cos(t * 2.2) * 1.0
    hi_col = rl.Color(255, 255, 255, int(92 * alpha))
    rl.draw_rectangle_rounded(
      rl.Rectangle(cx - w * 0.30 + glint_dx, cy - h * 0.32 + glint_dy, w * 0.24, h * 0.19),
      0.85,
      12,
      hi_col,
    )
    rl.draw_circle(
      int(cx + w * 0.22 + glint_dx * 0.5),
      int(cy + h * 0.24 + glint_dy * 0.5),
      max(3.0, min(w, h) * 0.055),
      rl.Color(255, 255, 255, int(68 * alpha)),
    )

    # Sparkle glint inside eyes during sharp acceleration boost
    if glyph == EyeGlyph.SPARKLE_BOOST:
      self._draw_boost_sparkle(cx, cy, min(w, h) * 0.22, alpha, t)

    # Directional chevron glint inside eye during lane changes
    if glyph in (EyeGlyph.ARROW_LEFT, EyeGlyph.ARROW_RIGHT):
      self._draw_chevron_glint(cx, cy, w * 0.24, glyph == EyeGlyph.ARROW_RIGHT, alpha)

    # Laser-alert inner bright core bar
    if glyph == EyeGlyph.LASER_ALERT:
      inner_col = rl.Color(255, 235, 235, int(215 * alpha))
      rl.draw_rectangle_rounded(rl.Rectangle(cx - w * 0.36, cy - 5, w * 0.72, 10), 0.85, 10, inner_col)

    # Eyelid masks (pure black polygons over the OLED canvas, tall enough to cleanly clip outer halo)
    if top_lid > 0.01 or abs(slant_deg) > 0.5:
      lid_h = max(42.0, h * (top_lid + 0.55))
      lid_w = w + 80.0
      lid_cy = (cy - h / 2.0) + h * top_lid - lid_h / 2.0 - 4.0
      rl.draw_rectangle_pro(
        rl.Rectangle(cx, lid_cy, lid_w, lid_h),
        rl.Vector2(lid_w / 2.0, lid_h / 2.0),
        slant_deg,
        rl.BLACK,
      )

    if bottom_lid > 0.01:
      lid_h = max(36.0, h * (bottom_lid + 0.45))
      lid_w = w + 80.0
      lid_cy = (cy + h / 2.0) - h * bottom_lid + lid_h / 2.0 + 4.0
      rl.draw_rectangle_pro(
        rl.Rectangle(cx, lid_cy, lid_w, lid_h),
        rl.Vector2(lid_w / 2.0, lid_h / 2.0),
        0.0,
        rl.BLACK,
      )

  def _draw_boost_sparkle(self, cx: float, cy: float, size: float, alpha: float, t: float) -> None:
    """4-point pulsing star sparkle inside eyes during sharp acceleration."""
    s = size * (0.85 + 0.25 * math.sin(t * 14.0))
    col = rl.Color(255, 255, 255, int(210 * alpha))
    rl.draw_line_ex(rl.Vector2(cx - s, cy), rl.Vector2(cx + s, cy), 4.0, col)
    rl.draw_line_ex(rl.Vector2(cx, cy - s), rl.Vector2(cx, cy + s), 4.0, col)

  def _draw_chevron_glint(self, cx: float, cy: float, size: float, right: bool, alpha: float) -> None:
    sign = 1.0 if right else -1.0
    col = rl.Color(0, 0, 0, int(135 * alpha))
    p_top = rl.Vector2(cx - sign * size * 0.35, cy - size * 0.75)
    p_tip = rl.Vector2(cx + sign * size * 0.55, cy)
    p_bot = rl.Vector2(cx - sign * size * 0.35, cy + size * 0.75)
    rl.draw_line_ex(p_top, p_tip, 7.0, col)
    rl.draw_line_ex(p_tip, p_bot, 7.0, col)

  def _draw_star_eye(self, cx: float, cy: float, outer_r: float, color: rl.Color, alpha: float, t: float) -> None:
    inner_r = outer_r * 0.44
    spin = math.sin(t * 7.0) * 0.14  # playful wobble
    pts: list[rl.Vector2] = []
    for i in range(10):
      angle = -math.pi / 2.0 + spin + i * (math.pi / 5.0)
      rad = outer_r if i % 2 == 0 else inner_r
      pts.append(rl.Vector2(cx + math.cos(angle) * rad, cy + math.sin(angle) * rad))

    rl.draw_circle_gradient(
      rl.Vector2(cx, cy), outer_r * 1.25,
      rl.Color(color.r, color.g, color.b, int(90 * alpha)),
      rl.Color(color.r, color.g, color.b, 0),
    )
    center = rl.Vector2(cx, cy)
    for i in range(10):
      p1 = pts[i]
      p2 = pts[(i + 1) % 10]
      rl.draw_triangle(center, p2, p1, color)

  def _draw_heart_eye(self, cx: float, cy: float, radius: float, color: rl.Color, alpha: float, with_glow: bool = True) -> None:
    if with_glow:
      rl.draw_circle_gradient(
        rl.Vector2(cx, cy), radius * 1.35,
        rl.Color(color.r, color.g, color.b, int(90 * alpha)),
        rl.Color(color.r, color.g, color.b, 0),
      )
    lobe_r = radius * 0.52
    lobe_y = cy - radius * 0.22
    rl.draw_circle(int(cx - lobe_r * 0.85), int(lobe_y), lobe_r, color)
    rl.draw_circle(int(cx + lobe_r * 0.85), int(lobe_y), lobe_r, color)
    rl.draw_triangle(
      rl.Vector2(cx - radius * 0.96, lobe_y + lobe_r * 0.22),
      rl.Vector2(cx, cy + radius * 0.92),
      rl.Vector2(cx + radius * 0.96, lobe_y + lobe_r * 0.22),
      color,
    )

  def _draw_crescent_eye(self, cx: float, cy: float, w: float, h: float, color: rl.Color, alpha: float) -> None:
    radius = min(w, h) * 0.50
    arc_cy = cy + radius * 0.35
    glow_col = rl.Color(color.r, color.g, color.b, int(55 * alpha))
    rl.draw_ring(rl.Vector2(cx, arc_cy), radius - 22.0, radius + 8.0, 200.0, 340.0, 28, glow_col)
    rl.draw_ring(rl.Vector2(cx, arc_cy), radius - 14.0, radius, 202.0, 338.0, 28, color)

  def _draw_mouth(self, cx: float, cy: float, mouth: MouthGlyph, color: rl.Color) -> None:
    if mouth == MouthGlyph.SMILE:
      rl.draw_ring(rl.Vector2(cx, cy - 10.0), 17.0, 23.0, 25.0, 155.0, 20, color)
    elif mouth == MouthGlyph.BIG_GRIN:
      rl.draw_ring(rl.Vector2(cx, cy - 12.0), 19.0, 26.0, 18.0, 162.0, 24, color)
    elif mouth == MouthGlyph.FROWN:
      rl.draw_ring(rl.Vector2(cx, cy + 16.0), 17.0, 23.0, 205.0, 335.0, 20, color)
    elif mouth == MouthGlyph.SURPRISED:
      rl.draw_ring(rl.Vector2(cx, cy + 2.0), 9.0, 15.0, 0.0, 360.0, 24, color)
