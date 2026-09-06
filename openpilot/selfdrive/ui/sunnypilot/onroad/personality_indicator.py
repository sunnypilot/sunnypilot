"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.common.filter_simple import FirstOrderFilter


class PersonalityIndicator:
  """Always-visible driving personality chip: one filled bar for aggressive,
  two for standard, three for relaxed - the factory follow-distance idiom.

  Personality comes live from selfdriveState, so wheel-button and settings
  changes reflect within a frame with no extra param polling."""

  WIDTH, HEIGHT = 78, 40
  BAR_W, BAR_H, BAR_GAP = 14, 24, 7
  MARGIN_X, MARGIN_Y = 10, 14

  def __init__(self):
    self._personality: int = -1
    self._flash_filter = FirstOrderFilter(0.0, 0.3, 1 / gui_app.target_fps)

  def update(self) -> None:
    personality = int(ui_state.sm['selfdriveState'].personality.raw)
    if personality != self._personality:
      if self._personality >= 0:
        self._flash_filter.x = 1.0  # brief highlight so a change is noticeable
      self._personality = personality

  def render(self, rect: rl.Rectangle, can_draw: bool = True) -> None:
    # personality only exists with openpilot longitudinal control, and alerts
    # own the screen (can_draw is the same yield the set speed uses)
    if not ui_state.show_driving_personality or not ui_state.has_longitudinal_control:
      return
    if not can_draw or self._personality < 0:
      return

    filled = self._personality + 1  # aggressive=0 -> 1 bar ... relaxed=2 -> 3 bars
    x = rect.x + rect.width - self.MARGIN_X - self.WIDTH
    y = rect.y + self.MARGIN_Y
    flash = self._flash_filter.update(0.0)
    bg = rl.Color(255, 255, 255, int(255 * (0.14 + 0.45 * flash)))
    rl.draw_rectangle_rounded(rl.Rectangle(x, y, self.WIDTH, self.HEIGHT), 0.5, 8, bg)

    bar_x = x + (self.WIDTH - 3 * self.BAR_W - 2 * self.BAR_GAP) / 2
    bar_y = y + (self.HEIGHT - self.BAR_H) / 2
    for i in range(3):
      bar = rl.Rectangle(bar_x + i * (self.BAR_W + self.BAR_GAP), bar_y, self.BAR_W, self.BAR_H)
      color = rl.Color(0, 145, 255, 235) if i < filled else rl.Color(255, 255, 255, 55)
      rl.draw_rectangle_rounded(bar, 0.35, 6, color)
