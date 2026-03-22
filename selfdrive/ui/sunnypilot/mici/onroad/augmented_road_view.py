"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pyray as rl
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import AugmentedRoadView


class AugmentedRoadViewSP(AugmentedRoadView):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._show_confidence_ball: bool = True
    self._real_confidence_ball = self._confidence_ball
    self._confidence_ball = _ConfidenceBall()

  def set_show_confidence_ball(self, show: bool) -> None:
    self._show_confidence_ball = show

  def _render(self, rect: rl.Rectangle) -> None:
    super()._render(rect)
    if self._show_confidence_ball:
      self._real_confidence_ball.render(self.rect)


class _ConfidenceBall:
  def render(self, *_):
    pass
