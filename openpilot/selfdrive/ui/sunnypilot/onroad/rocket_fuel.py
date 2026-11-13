"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.system.ui.lib.application import gui_app

MAX_ACCEL = 4.0
BAR_HEIGHT = 135.0

# equivalent to np.interp(x, [x0, x1], [y0, y1]) but without the numpy dependency
def _lerp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
  if x <= x0:
    return y0
  if x >= x1:
    return y1
  return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


class RocketFuel:
  def __init__(self, scale: float = 1.0):
    self._scale = scale
    self._bar_half_h = BAR_HEIGHT * scale / 2  # half the total track height
    self._cap_r = 7 * scale                    # rounded-cap radius, matches TorqueBar
    # Smooth acceleration and engagement alpha to avoid jarring transitions
    self._accel_filter = FirstOrderFilter(0, 0.1, 1 / gui_app.target_fps)
    self._alpha_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)

  def render(self, rect: rl.Rectangle, sm) -> None:
    if not ui_state.rocket_fuel:
      return

    scale = self._scale

    # Normalize longitudinal acceleration to [-1, 1] relative to MAX_ACCEL
    accel_norm = max(-1.0, min(1.0, sm['carState'].aEgo / MAX_ACCEL))
    self._accel_filter.update(accel_norm)

    # active fades the whole bar in/out; engaged controls color intensity
    active = ui_state.status != UIStatus.DISENGAGED
    engaged = ui_state.status in (UIStatus.ENGAGED, UIStatus.LAT_ONLY)
    self._alpha_filter.update(active)

    accel = self._accel_filter.x   # smoothed normalized accel in [-1, 1]
    alpha = self._alpha_filter.x   # smoothed engagement alpha in [0, 1]

    abs_accel = abs(accel)
    # Bar shifts right slightly and widens as accel magnitude increases (matches TorqueBar geometry)
    bar_x = rect.x + _lerp(abs_accel, 0.5, 1, 20 * scale, 22 * scale)
    bar_w = _lerp(abs_accel, 0.5, 1, 14 * scale, 56 * scale)
    # Center between speed limit label bottom and face icon top
    cy = rect.y + (rect.height + 33) / 2

    # --- Background track ---
    # Track opacity grows with accel magnitude; dims when not engaged
    bg_alpha = _lerp(abs_accel, 0.5, 1.0, 0.25, 0.5)
    bg_opacity = bg_alpha if engaged else 0.15
    bg_color = rl.Color(255, 255, 255, int(255 * bg_opacity * alpha))

    bg_h = self._bar_half_h * 2 * alpha  # track height fades in/out with engagement
    bg_roundness = min(1.0, self._cap_r / (min(bar_w, bg_h) / 2)) if bg_h > 0 else 1.0
    rl.draw_rectangle_rounded(rl.Rectangle(bar_x, cy - bg_h / 2, bar_w, bg_h), bg_roundness, 8, bg_color)

    # --- Foreground bar ---
    # Full opacity when engaged, dimmed when active but not controlling lateral
    fg_alpha = int(255 * (0.9 if engaged else 0.35) * alpha)

    # Height grows from a minimum circle (bar_w) up to concentric with the bg top cap
    fg_h_max = self._bar_half_h * alpha + bar_w / 2
    fg_h = _lerp(abs_accel, 0, 1, bar_w, fg_h_max)

    # Color fades from white at low accel to green (accel) or red (decel) by abs_accel
    fade = int(255 * max(0.0, 1.0 - abs_accel / 0.3))
    if accel >= 0:
      fg_color = rl.Color(fade, 245, fade, fg_alpha)  # white → green
      fg_y = cy - fg_h + bar_w / 2                   # bar grows upward from center
    else:
      fg_color = rl.Color(245, fade, fade, fg_alpha)  # white → red
      fg_y = cy - bar_w / 2                           # bar grows downward from center

    fg_roundness = min(1.0, self._cap_r / (min(bar_w, fg_h) / 2)) if fg_h > 0 else 1.0
    rl.draw_rectangle_rounded(rl.Rectangle(bar_x, fg_y, bar_w, fg_h), fg_roundness, 8, fg_color)

    # Center dot shown when accel is near zero (matches TorqueBar idle indicator)
    if abs_accel < 0.5:
      dot_alpha = int(255 * 0.9 * alpha)
      rl.draw_circle(int(bar_x + bar_w / 2), int(cy), 5 * scale, rl.Color(182, 182, 182, dot_alpha))

