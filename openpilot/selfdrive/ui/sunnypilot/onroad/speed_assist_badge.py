"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import raylib_nb as rl

from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_dial import DIAL_HEIGHT, DIAL_WIDTH, draw_dial
from openpilot.system.ui.widgets import Widget

STATUS_ICON_HEIGHT = 40  # px, like the other footer icons
STATUS_ICON_ALPHA = 0.9  # like settings and network
HOME_DIAL_SCALE = 1.25  # 44 x 26 px


class SpeedAssistIcon(Widget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, round(DIAL_WIDTH * HOME_DIAL_SCALE), STATUS_ICON_HEIGHT))
    self.set_enabled(False)

  def _render(self, _) -> None:
    top = self._rect.y + (self._rect.height - DIAL_HEIGHT * HOME_DIAL_SCALE) / 2
    draw_dial(self._rect.x + self._rect.width / 2, top, HOME_DIAL_SCALE, alpha=STATUS_ICON_ALPHA, track=rl.WHITE, needle=rl.WHITE)
