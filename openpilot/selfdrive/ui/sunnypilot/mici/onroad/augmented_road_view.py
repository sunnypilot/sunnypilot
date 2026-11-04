"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.sunnypilot.mici.onroad.accel_boost_indicator import AccelBoostIndicator


class AugmentedRoadViewSP:
  def __init__(self):
    self._accel_boost_indicator = AccelBoostIndicator()

  def render_side_panel(self, rect: rl.Rectangle) -> None:
    self._accel_boost_indicator.render(rect)
    if not self._accel_boost_indicator.holding_panel:
      self._confidence_ball.render(rect)
