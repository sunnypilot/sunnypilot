"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os

import pyray as rl

SHOW_MOUSE_COORDS = os.getenv("SHOW_MOUSE_COORDS") == "1"
SUNNYPILOT_UI = os.getenv("SUNNYPILOT_UI", "1") == "1"


class GuiApplicationExt:
  def __init__(self):
    self._show_mouse_coords = SHOW_MOUSE_COORDS

  @staticmethod
  def sunnypilot_ui() -> bool:
    return SUNNYPILOT_UI

  @staticmethod
  def _draw_mouse_coordinates(font):
    coords_text = f"X:{int(rl.get_mouse_x())}, Y:{int(rl.get_mouse_y())}"

    # Draw the text with same style as FPS
    rl.draw_text(coords_text, 100, 10, 20, rl.WHITE)

  def set_show_mouse_coords(self, show: bool):
    self._show_mouse_coords = show
