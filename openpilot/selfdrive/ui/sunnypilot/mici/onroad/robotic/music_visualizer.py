"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.music_analyzer import MusicState, NUM_BANDS
from openpilot.system.ui.lib.application import gui_app


def groove_prism_color(t: float) -> tuple[int, int, int]:
  """Smoothly cycle vibrant OLED-friendly cyan -> aqua -> orchid -> mint hues while grooving."""
  # Smooth cosine palette keeping high brightness and pleasant saturation
  r = int(125 + 95 * math.sin(t * 0.9 + 2.2))
  g = int(195 + 55 * math.sin(t * 0.9 + 0.4))
  b = int(215 + 40 * math.sin(t * 0.9 + 4.1))
  return (max(50, min(255, r)), max(90, min(255, g)), max(140, min(255, b)))


class MusicVisualizerRenderer:
  """Smooth 60 FPS OLED equalizer bars, bass pulse aura, and floating musical notes."""

  def __init__(self):
    dt = 1.0 / max(gui_app.target_fps, 1)
    self._alpha = FirstOrderFilter(0.0, 0.16, dt)
    self._bar_filters = [FirstOrderFilter(0.0, 0.06, dt) for _ in range(NUM_BANDS)]

  def render_background(self, rect: rl.Rectangle, music: MusicState, active: bool) -> float:
    """Render smooth ambient bass aura & bottom pill equalizer bars; returns current visualizer alpha."""
    alpha = self._alpha.update(1.0 if active else 0.0)
    if alpha < 0.01:
      return 0.0

    t = rl.get_time()
    cr, cg, cb = groove_prism_color(t)

    # 1. Soft beat-reactive ambient bass aura along bottom center
    aura_r = 140.0 + 75.0 * music.beat_pulse + 35.0 * music.energy
    aura_alpha = int((42 + 52 * music.beat_pulse) * alpha)
    rl.draw_circle_gradient(
      rl.Vector2(rect.x + rect.width / 2.0, rect.y + rect.height + 10.0),
      aura_r,
      rl.Color(cr, cg, cb, aura_alpha),
      rl.Color(cr, cg, cb, 0),
    )

    # 2. Smooth 12-band symmetric pill equalizer along the bottom edge
    bar_count = NUM_BANDS
    total_w = rect.width - 76.0
    gap = 10.0
    bar_w = (total_w - gap * (bar_count - 1)) / bar_count
    start_x = rect.x + (rect.width - total_w) / 2.0
    base_y = rect.y + rect.height - 8.0
    max_bar_h = 44.0

    for i in range(bar_count):
      raw_level = music.bands[i] if i < len(music.bands) else 0.0
      # Keep a smooth living wave + subtle beat lift on bass/mid bars
      wave = 0.14 + 0.10 * math.sin(t * 5.0 + i * 0.65)
      beat_lift = music.beat_pulse * (0.28 if i < 6 else 0.16)
      level = self._bar_filters[i].update(min(1.0, max(wave, raw_level + beat_lift)))
      bar_h = max(8.0, level * max_bar_h)

      bx = start_x + i * (bar_w + gap)
      by = base_y - bar_h

      # Subtle color gradient across the spectrum (cyan -> violet -> pink)
      frac = i / max(1, bar_count - 1)
      br = int(min(255, cr * (1.0 - frac * 0.25) + 255 * frac * 0.25))
      bg = int(min(255, cg * (1.0 - frac * 0.30) + 120 * frac * 0.30))
      bb = int(min(255, cb * 0.85 + 255 * 0.15))

      # Soft glow cap on taller bars
      if level > 0.35:
        rl.draw_circle_gradient(
          rl.Vector2(bx + bar_w / 2.0, by + 4.0),
          bar_w * 1.15,
          rl.Color(br, bg, bb, int(75 * level * alpha)),
          rl.Color(br, bg, bb, 0),
        )

      bar_col = rl.Color(br, bg, bb, int((155 + 90 * level) * alpha))
      rl.draw_rectangle_rounded(rl.Rectangle(bx, by, bar_w, bar_h), 0.9, 10, bar_col)

    return alpha

  def render_foreground_notes(self, rect: rl.Rectangle, music: MusicState, alpha: float) -> None:
    """Draw cute floating vector musical notes on the left and right edges while grooving."""
    if alpha < 0.05:
      return

    t = rl.get_time()
    cr, cg, cb = groove_prism_color(t + 1.2)
    note_specs = (
      (rect.x + 48.0, 0.0, 1.0),
      (rect.x + rect.width - 48.0, 0.5, -1.0),
      (rect.x + 82.0, 0.28, 0.8),
      (rect.x + rect.width - 82.0, 0.76, -0.8),
    )

    for base_x, phase_off, sway_dir in note_specs:
      phase = (t * 0.65 + phase_off) % 1.0
      fade = math.sin(phase * math.pi)
      nx = base_x + math.sin(phase * math.tau) * 10.0 * sway_dir
      ny = rect.y + 150.0 - phase * 98.0
      scale = 0.85 + 0.25 * music.beat_pulse
      col = rl.Color(cr, cg, cb, int(215 * fade * alpha))
      self._draw_eighth_note(nx, ny, 7.5 * scale, col)

  def _draw_eighth_note(self, cx: float, cy: float, r: float, color: rl.Color) -> None:
    """Crisp vector eighth-note glyph (♪) — zero font dependency."""
    rl.draw_circle(int(cx), int(cy), r * 0.72, color)
    stem_x = cx + r * 0.58
    stem_top = cy - r * 2.5
    rl.draw_line_ex(rl.Vector2(stem_x, cy), rl.Vector2(stem_x, stem_top), 2.8, color)
    # Curved flag
    rl.draw_line_ex(
      rl.Vector2(stem_x, stem_top),
      rl.Vector2(stem_x + r * 1.15, stem_top + r * 0.95),
      2.8,
      color,
    )
