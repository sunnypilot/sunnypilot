"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import ACCEL_BOOST_MAX
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget

BAR_WIDTH = 26
BAR_RADIUS = 0.5
TRACK_TOP_RATIO = 0.08
TRACK_BOTTOM_RATIO = 0.92
# Fades to white only near the profile cap, like the stock torque bar fading toward orange at high torque
CAP_BLEND_START = 0.70
MAX_BOOST_BLEND = 0.55

COLOR_TRACK = rl.Color(255, 255, 255, 32)
COLOR_TRACK_EDGE = rl.Color(255, 255, 255, 70)
COLOR_HIGHLIGHT = rl.Color(255, 255, 255, 45)

AGGRESSIVE_COLOR = rl.Color(255, 80, 60, 255)
STANDARD_COLOR = rl.Color(0, 230, 120, 255)
RELAXED_COLOR = rl.Color(70, 150, 255, 255)

# The personality enum is ordered aggressive, standard, relaxed, matching ACCEL_BOOST_MAX
PROFILE_STYLES = {
  0: (AGGRESSIVE_COLOR, ACCEL_BOOST_MAX[0]),
  1: (STANDARD_COLOR, ACCEL_BOOST_MAX[1]),
  2: (RELAXED_COLOR, ACCEL_BOOST_MAX[2]),
}

FADE_THRESHOLD = 0.01


def get_boost_style(personality) -> tuple[rl.Color, float]:
  """Color and full-scale boost for the active personality."""
  raw = getattr(personality, "raw", personality)
  return PROFILE_STYLES.get(int(raw), PROFILE_STYLES[1])


def get_boost_fraction(boost: float, max_boost: float) -> float:
  """How much of the active profile's boost budget is in use, clamped to a full bar."""
  if max_boost <= 0.0:
    return 0.0
  return min(max(boost / max_boost, 0.0), 1.0)


def lighten(color: rl.Color, amount: float) -> rl.Color:
  """Lerp towards white in RGB, so the hue stays put the way HSV blending would not."""
  amount = min(max(amount, 0.0), 1.0)
  return rl.Color(int(color.r + (255 - color.r) * amount),
                  int(color.g + (255 - color.g) * amount),
                  int(color.b + (255 - color.b) * amount), color.a)


class AccelBoostIndicator(Widget):
  def __init__(self):
    super().__init__()
    fps = max(gui_app.target_fps, 1)
    self._boost_filter = FirstOrderFilter(0.0, 0.15, 1 / fps)
    self._alpha_filter = FirstOrderFilter(0.0, 0.1, 1 / fps)
    # Smoothly rescale the bar when the follow distance profile changes mid-drive
    self._max_boost_filter = FirstOrderFilter(0.0, 0.25, 1 / fps)
    self._profile_color, self._max_boost = PROFILE_STYLES[1]

    self.panel_in_use = False

  def _update_state(self):
    sm = ui_state.sm
    visible = (ui_state.has_longitudinal_control and sm.alive['selfdriveState'] and
               sm.alive['longitudinalPlan'] and sm['selfdriveState'].enabled)
    self._alpha_filter.update(1.0 if visible else 0.0)
    self._boost_filter.update(float(sm['longitudinalPlan'].accelBoost) if visible else 0.0)

    if sm.alive['selfdriveState']:
      self._profile_color, self._max_boost = get_boost_style(sm['selfdriveState'].personality)
    self._max_boost_filter.update(self._max_boost)

    # The bar owns the panel while it is drawn; the confidence ball returns when it fades out
    self.panel_in_use = self._alpha_filter.x > FADE_THRESHOLD

  def _render(self, _):
    alpha = self._alpha_filter.x
    if alpha < FADE_THRESHOLD or self._max_boost <= 0.0:
      return

    panel_x = self.rect.x + self.rect.width - SIDE_PANEL_WIDTH
    cx = panel_x + SIDE_PANEL_WIDTH / 2
    bar_x = cx - BAR_WIDTH / 2
    track_top = self.rect.y + self.rect.height * TRACK_TOP_RATIO
    track_bottom = self.rect.y + self.rect.height * TRACK_BOTTOM_RATIO
    track_h = max(1.0, track_bottom - track_top)
    track_rect = rl.Rectangle(bar_x, track_top, BAR_WIDTH, track_h)

    # soft well behind the track so the bar reads on the black side panel
    rl.draw_rectangle_rounded(rl.Rectangle(bar_x - 3, track_top - 3, BAR_WIDTH + 6, track_h + 6), BAR_RADIUS, 12,
                              rl.Color(0, 0, 0, int(80 * alpha)))

    # track, light enough to read on the black side panel
    rl.draw_rectangle_rounded(track_rect, BAR_RADIUS, 12,
                              rl.Color(COLOR_TRACK.r, COLOR_TRACK.g, COLOR_TRACK.b, int(COLOR_TRACK.a * alpha)))
    rl.draw_rectangle_rounded_lines_ex(track_rect, BAR_RADIUS, 12, 1,
                                       rl.Color(COLOR_TRACK_EDGE.r, COLOR_TRACK_EDGE.g, COLOR_TRACK_EDGE.b,
                                                int(COLOR_TRACK_EDGE.a * alpha)))

    # Scale to the current profile's cap, so a maxed boost fills the bar and a profile change rescales it
    boost = max(self._boost_filter.x, 0.0)
    ratio = get_boost_fraction(boost, self._max_boost_filter.x)
    fill_h = ratio * track_h
    if fill_h <= 0.0:
      return

    cap_blend = max(0.0, (ratio - CAP_BLEND_START) / (1.0 - CAP_BLEND_START))
    fill_color = lighten(self._profile_color, MAX_BOOST_BLEND * cap_blend)
    tip_y = track_bottom - fill_h

    # soft glow around the tip, like the confidence ball's gradient
    tip_center_y = tip_y + min(fill_h, BAR_WIDTH) / 2
    glow = rl.Color(fill_color.r, fill_color.g, fill_color.b, int(85 * alpha))
    rl.draw_circle_gradient(rl.Vector2(cx, tip_center_y), int(BAR_WIDTH * 0.85), glow, rl.BLANK)

    fill = rl.Color(fill_color.r, fill_color.g, fill_color.b, int(255 * alpha))
    if fill_h < BAR_WIDTH:
      # Keep the cap inside the track: a fixed radius would paint below the track near zero boost
      radius = max(1, int(fill_h / 2))
      rl.draw_circle(int(cx), int(track_bottom - radius), radius, fill)
    else:
      rl.draw_rectangle_rounded(rl.Rectangle(bar_x, tip_y, BAR_WIDTH, fill_h), BAR_RADIUS, 12, fill)

      # subtle inner highlight gives the fill a rounded, glassy edge
      if fill_h > 12:
        highlight_rect = rl.Rectangle(bar_x + 4, tip_y + 5, 3, fill_h - 10)
        rl.draw_rectangle_rounded(highlight_rect, 0.5, 8,
                                  rl.Color(COLOR_HIGHLIGHT.r, COLOR_HIGHLIGHT.g, COLOR_HIGHLIGHT.b,
                                           int(COLOR_HIGHLIGHT.a * alpha)))

      # bright cap at the tip
      rl.draw_circle(int(cx), int(tip_center_y), 2,
                     rl.Color(255, 255, 255, int(150 * alpha)))
