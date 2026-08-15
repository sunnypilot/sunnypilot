"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state


class RocketFuel:
  def __init__(self):
    self.vc_accel = 0.0

  def render(self, rect: rl.Rectangle, sm) -> None:
    if not ui_state.rocket_fuel:
      return

    vc_accel0 = sm['carState'].aEgo

    # Smooth the acceleration
    self.vc_accel = self.vc_accel + (vc_accel0 - self.vc_accel) / 5.0

    hha = 0.0
    color = rl.Color(0, 0, 0, 0)  # Transparent by default

    if self.vc_accel > 0:
      hha = 0.85 - 0.1 / self.vc_accel  # only extend up to 85%
      color = rl.Color(0, 245, 0, 200)
    elif self.vc_accel < 0:
      hha = 0.85 + 0.1 / self.vc_accel  # only extend up to 85%
      color = rl.Color(245, 0, 0, 200)

    if hha < 0:
      hha = 0.0

    hha = hha * rect.height
    wp = 28.0

    # Draw
    rect_h = rect.height

    if self.vc_accel > 0:
      ra_y = rect_h / 2.0 - hha / 2.0
    else:
      ra_y = rect_h / 2.0

    if hha > 0:
      rl.draw_rectangle(int(rect.x), int(rect.y + ra_y), int(wp), int(hha / 2.0), color)
