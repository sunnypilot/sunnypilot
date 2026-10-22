"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.cereal import log
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost_ext import get_accel_boost_max

# The readout is wider than the side panel, so the value is right-aligned and bleeds over the camera view
BAR_WIDTH = 24
# Fades to white only near the profile cap, like the stock torque bar fading toward orange at high torque
CAP_BLEND_START = 0.75
MAX_BOOST_BLEND = 0.45

COLOR_TRACK = rl.Color(255, 255, 255, 45)
COLOR_TRACK_EDGE = rl.Color(255, 255, 255, 70)
COLOR_TEXT = rl.Color(255, 255, 255, 235)
COLOR_TEXT_SHADOW = rl.Color(0, 0, 0, 150)

# Temporary debug readout next to the bar, flip off once the bar alone reads right
SHOW_VALUE = True
VALUE_FONT_SIZE = 24

AGGRESSIVE_COLOR = rl.Color(255, 80, 60, 255)
STANDARD_COLOR = rl.Color(0, 230, 120, 255)
RELAXED_COLOR = rl.Color(70, 150, 255, 255)

FADE_THRESHOLD = 0.01


def lighten(color: rl.Color, amount: float) -> rl.Color:
  """Lerp towards white in RGB, so the hue stays put the way HSV blending would not."""
  amount = min(max(amount, 0.0), 1.0)
  return rl.Color(int(color.r + (255 - color.r) * amount),
                  int(color.g + (255 - color.g) * amount),
                  int(color.b + (255 - color.b) * amount), color.a)


def get_boost_fraction(boost: float, max_boost: float) -> float:
  """How much of the active profile's boost budget is in use, clamped to a full bar."""
  if max_boost <= 0.0:
    return 0.0
  return min(max(boost / max_boost, 0.0), 1.0)


def get_boost_style(personality) -> tuple[rl.Color, float]:
  if personality == log.LongitudinalPersonality.aggressive:
    color = AGGRESSIVE_COLOR
  elif personality == log.LongitudinalPersonality.relaxed:
    color = RELAXED_COLOR
  else:
    color = STANDARD_COLOR

  return color, get_accel_boost_max(personality)


class AccelBoostIndicator(Widget):
  def __init__(self):
    super().__init__()
    self._boost_filter = FirstOrderFilter(0.0, 0.15, 1 / gui_app.target_fps)
    self._alpha_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)
    # Smoothly rescale the bar when the follow distance profile changes mid-drive
    self._max_boost_filter = FirstOrderFilter(0.0, 0.25, 1 / gui_app.target_fps)
    self._font = gui_app.font(FontWeight.BOLD)
    self._profile_color = STANDARD_COLOR
    self._max_boost = 0.0

    self.panel_in_use = False

  def _update_state(self):
    sm = ui_state.sm
    extra_enabled = ui_state.follow_distance_accel_boost
    visible = (ui_state.has_longitudinal_control and sm.alive['selfdriveState'] and sm.alive['longitudinalPlan'] and
               sm['selfdriveState'].enabled)
    self._alpha_filter.update(1.0 if visible and extra_enabled else 0.0)
    self._boost_filter.update(float(sm['longitudinalPlan'].accelBoost) if visible else 0.0)

    if sm.alive['selfdriveState']:
      self._profile_color, self._max_boost = get_boost_style(sm['selfdriveState'].personality)
    self._max_boost_filter.update(self._max_boost)

    self.panel_in_use = extra_enabled and ui_state.has_longitudinal_control

  def _render(self, _):
    alpha = self._alpha_filter.x
    if alpha < FADE_THRESHOLD or self._max_boost <= 0.0:
      return

    cx = self.rect.x + self.rect.width - SIDE_PANEL_WIDTH / 2
    bar_x = cx - BAR_WIDTH / 2
    track_top = self.rect.y + self.rect.height * 0.08
    track_bottom = self.rect.y + self.rect.height * 0.92
    track_h = max(1.0, track_bottom - track_top)

    # track, light enough to read on the black side panel
    rl.draw_rectangle_rounded(rl.Rectangle(bar_x, track_top, BAR_WIDTH, track_h), 0.5, 12,
                              rl.Color(COLOR_TRACK.r, COLOR_TRACK.g, COLOR_TRACK.b, int(COLOR_TRACK.a * alpha)))
    rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(bar_x, track_top, BAR_WIDTH, track_h), 0.5, 12, 1,
                                       rl.Color(COLOR_TRACK_EDGE.r, COLOR_TRACK_EDGE.g, COLOR_TRACK_EDGE.b,
                                                int(COLOR_TRACK_EDGE.a * alpha)))

    # Scale to the current profile's cap, so a maxed boost fills the bar and a profile change rescales it
    boost = max(self._boost_filter.x, 0.0)
    ratio = get_boost_fraction(boost, self._max_boost_filter.x)
    fill_h = ratio * track_h
    cap_blend = max(0.0, (ratio - CAP_BLEND_START) / (1.0 - CAP_BLEND_START))
    fill_color = lighten(self._profile_color, MAX_BOOST_BLEND * cap_blend)
    if fill_h > 0.0:
      # soft glow around the tip, like the confidence ball's gradient
      tip_y = track_bottom - fill_h
      glow = rl.Color(fill_color.r, fill_color.g, fill_color.b, int(70 * alpha))
      rl.draw_circle_gradient(rl.Vector2(cx, tip_y), int(BAR_WIDTH * 0.9), glow, rl.BLANK)

      fill = rl.Color(fill_color.r, fill_color.g, fill_color.b, int(255 * alpha))
      if fill_h < BAR_WIDTH:
        rl.draw_circle(int(cx), int(track_bottom - fill_h / 2), max(1, int(BAR_WIDTH / 2)), fill)
      else:
        rl.draw_rectangle_rounded(rl.Rectangle(bar_x, track_bottom - fill_h, BAR_WIDTH, fill_h), 0.5, 12, fill)

    if SHOW_VALUE:
      value = f"+{boost:.2f}"
      value_size = measure_text_cached(self._font, value, VALUE_FONT_SIZE)
      value_pos = rl.Vector2(bar_x - 8 - value_size.x, (track_top + track_bottom) / 2 - value_size.y / 2)
      self._draw_text(self._font, value, value_pos, VALUE_FONT_SIZE,
                      rl.Color(COLOR_TEXT.r, COLOR_TEXT.g, COLOR_TEXT.b, int(COLOR_TEXT.a * alpha)))

  @staticmethod
  def _draw_text(font, text: str, pos: rl.Vector2, font_size: int, color: rl.Color) -> None:
    # Drop shadow keeps the readout legible against the camera feed
    shadow = rl.Color(COLOR_TEXT_SHADOW.r, COLOR_TEXT_SHADOW.g, COLOR_TEXT_SHADOW.b, int(COLOR_TEXT_SHADOW.a * color.a / 255))
    rl.draw_text_ex(font, text, rl.Vector2(pos.x + 1, pos.y + 1), font_size, 0, shadow)
    rl.draw_text_ex(font, text, pos, font_size, 0, color)
