"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import pyray as rl

from openpilot.cereal import log
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import get_boost_max
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget

BAR_WIDTH = 26
TRACK_TOP_RATIO = 0.08
TRACK_BOTTOM_RATIO = 0.92
CAP_BLEND_START = 0.45
MAX_BOOST_BLEND = 0.55
FADE_THRESHOLD = 0.01

COLOR_TRACK = rl.Color(255, 255, 255, 28)
COLOR_FILL = rl.Color(0, 230, 120, 255)


def get_boost_fraction(boost: float, max_boost: float) -> float:
  if max_boost <= 0.0:
    return 0.0
  return min(max(boost / max_boost, 0.0), 1.0)


def lighten(color: rl.Color, amount: float) -> rl.Color:
  amount = min(max(amount, 0.0), 1.0)
  return rl.Color(int(color.r + (255 - color.r) * amount),
                  int(color.g + (255 - color.g) * amount),
                  int(color.b + (255 - color.b) * amount), color.a)


def get_boost_color(fraction: float) -> rl.Color:
  blend = max(0.0, (fraction - CAP_BLEND_START) / (1.0 - CAP_BLEND_START))
  return lighten(COLOR_FILL, MAX_BOOST_BLEND * blend)


class AccelBoostIndicator(Widget):
  def __init__(self, panel_width: float = SIDE_PANEL_WIDTH, bar_width: float = BAR_WIDTH):
    super().__init__()
    self._panel_width = panel_width
    self._bar_width = bar_width
    fps = max(gui_app.target_fps, 1)
    self._boost_filter = FirstOrderFilter(0.0, 0.15, 1 / fps)
    self._alpha_filter = FirstOrderFilter(0.0, 0.1, 1 / fps)
    self._max_boost_filter = FirstOrderFilter(get_boost_max(), 0.25, 1 / fps)

  @property
  def holding_panel(self) -> bool:
    return self._alpha_filter.x > FADE_THRESHOLD

  def _update_state(self):
    sm = ui_state.sm
    visible = (ui_state.accel_boost and ui_state.has_longitudinal_control and sm.alive['selfdriveState'] and
               sm.alive['longitudinalPlan'] and sm['selfdriveState'].enabled)
    plan = sm['longitudinalPlan']
    applied = visible and plan.longitudinalPlanSource == log.LongitudinalPlan.LongitudinalPlanSource.e2e
    self._boost_filter.update(float(plan.accelBoost) if applied else 0.0)
    self._alpha_filter.update(1.0 if visible else 0.0)

    if sm.alive['selfdriveState']:
      self._max_boost_filter.update(get_boost_max(sm['selfdriveState'].personality))

  def _render(self, _):
    alpha = self._alpha_filter.x
    if alpha < FADE_THRESHOLD:
      return

    panel_x = max(self.rect.x, self.rect.x + self.rect.width - self._panel_width)
    bar_x = panel_x + (self._panel_width - self._bar_width) / 2
    track_top = self.rect.y + self.rect.height * TRACK_TOP_RATIO
    track = rl.Rectangle(bar_x, track_top, self._bar_width,
                         max(1.0, self.rect.height * (TRACK_BOTTOM_RATIO - TRACK_TOP_RATIO)))
    rl.draw_rectangle_rounded(track, 0.5, 12,
                              rl.Color(COLOR_TRACK.r, COLOR_TRACK.g, COLOR_TRACK.b, int(COLOR_TRACK.a * alpha)))

    fraction = get_boost_fraction(self._boost_filter.x, self._max_boost_filter.x)
    fill_h = fraction * track.height
    if fill_h < 1.0:
      return

    fill_color = get_boost_color(fraction)
    tip = track.y + track.height - fill_h
    rl.begin_scissor_mode(int(track.x), int(tip), int(math.ceil(track.width)) + 1, int(math.ceil(fill_h)))
    rl.draw_rectangle_rounded(track, 0.5, 12, rl.Color(fill_color.r, fill_color.g, fill_color.b, int(235 * alpha)))
    rl.end_scissor_mode()
