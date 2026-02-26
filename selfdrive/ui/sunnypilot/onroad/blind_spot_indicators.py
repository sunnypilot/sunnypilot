"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.common.filter_simple import FirstOrderFilter


class BlindSpotIndicators:
  def __init__(self):
    self._txt_blind_spot_left: rl.Texture = gui_app.texture('icons_mici/onroad/blind_spot_left.png', 108, 128)
    self._txt_blind_spot_right: rl.Texture = gui_app.texture('icons_mici/onroad/blind_spot_right.png', 108, 128)

    self._blind_spot_left_alpha_filter = FirstOrderFilter(0, 0.15, 1 / gui_app.target_fps)
    self._blind_spot_right_alpha_filter = FirstOrderFilter(0, 0.15, 1 / gui_app.target_fps)

  def update(self) -> None:
    sm = ui_state.sm
    CS = sm['carState']

    self._blind_spot_left_alpha_filter.update(1.0 if CS.leftBlindspot else 0.0)
    self._blind_spot_right_alpha_filter.update(1.0 if CS.rightBlindspot else 0.0)

  @property
  def detected(self) -> bool:
    return self._blind_spot_left_alpha_filter.x > 0.01 or self._blind_spot_right_alpha_filter.x > 0.01

  def render(self, rect: rl.Rectangle) -> None:
    if not ui_state.blindspot:
      return

    BLIND_SPOT_MARGIN_X = 20  # Distance from edge of screen
    BLIND_SPOT_Y_OFFSET = 100  # Distance from top of screen

    if self._blind_spot_left_alpha_filter.x > 0.01:
      pos_x = int(rect.x + BLIND_SPOT_MARGIN_X)
      pos_y = int(rect.y + BLIND_SPOT_Y_OFFSET)
      alpha = int(255 * self._blind_spot_left_alpha_filter.x)
      color = rl.Color(255, 255, 255, alpha)
      rl.draw_texture(self._txt_blind_spot_left, pos_x, pos_y, color)

    if self._blind_spot_right_alpha_filter.x > 0.01:
      pos_x = int(rect.x + rect.width - BLIND_SPOT_MARGIN_X - self._txt_blind_spot_right.width)
      pos_y = int(rect.y + BLIND_SPOT_Y_OFFSET)
      alpha = int(255 * self._blind_spot_right_alpha_filter.x)
      color = rl.Color(255, 255, 255, alpha)
      rl.draw_texture(self._txt_blind_spot_right, pos_x, pos_y, color)
