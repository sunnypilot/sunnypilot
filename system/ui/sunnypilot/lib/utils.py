"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.sunnypilot.widgets.list_view import ButtonActionSP


class NoElideButtonAction(ButtonActionSP):
  def get_width_hint(self):
    return super().get_width_hint() + 1


class AlertFadeAnimator:
  def __init__(self, target_fps: int, duration_on: float = 0.75, rc: float = 0.05):
    from openpilot.common.filter_simple import FirstOrderFilter
    self._filter = FirstOrderFilter(1.0, rc, 1 / target_fps)
    self._frame = 0
    self._target_fps = target_fps
    self._duration_on = duration_on

  def update(self, active: bool):
    if active:
      self._frame += 1
      if (self._frame % self._target_fps) < (self._target_fps * self._duration_on):
        self._filter.x = 1.0
      else:
        self._filter.update(0.0)
    else:
      self._frame = 0
      self._filter.update(1.0)

  @property
  def alpha(self) -> float:
    return self._filter.x
