"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import raylib_nb as rl
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import UIStatus, ui_state
from openpilot.system.ui.lib.application import gui_app

BORDER_COLORS_SP = {
  UIStatus.LAT_ONLY: rl.Color(0x00, 0xC8, 0xC8, 0xFF),  # Cyan for lateral-only state
  UIStatus.LONG_ONLY: rl.Color(0x96, 0x1C, 0xA8, 0xFF),  # Purple for longitudinal-only state
}

# (start, end) as fractions of the fade height, (start, end) alpha; eases in like onroad_fade.png's center
FADE_HEIGHT = 0.3
FADE_BANDS = ((0.0, 0.4, 0, 20), (0.4, 0.75, 20, 110), (0.75, 1.0, 110, 210))


class AugmentedRoadViewSP:
  def __init__(self):
    self._fade_alpha_filter = FirstOrderFilter(0, 0.1, 1 / gui_app.target_fps)

  def update_fade_out_bottom_overlay(self, _content_rect):
    # Fade out bottom of overlays for looks (only when engaged)
    fade_alpha = self._fade_alpha_filter.update(ui_state.status != UIStatus.DISENGAGED)
    if ui_state.torque_bar and fade_alpha > 1e-2:
      # the device UI renders in software: a full-screen texture blend drops tizi from 20 to 10 fps
      h = _content_rect.height * FADE_HEIGHT
      y = _content_rect.y + _content_rect.height - h
      for f0, f1, a0, a1 in FADE_BANDS:
        y0, y1 = int(y + h * f0), int(y + h * f1)
        rl.draw_rectangle_gradient_v(int(_content_rect.x), y0, int(_content_rect.width), y1 - y0,
                                     rl.Color(0, 0, 0, int(a0 * fade_alpha)), rl.Color(0, 0, 0, int(a1 * fade_alpha)))
