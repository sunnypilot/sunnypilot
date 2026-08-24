"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pyray as rl
from openpilot.system.ui.lib.application import MouseEvent
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2, ScrollState


class GuiScrollPanel2SP(GuiScrollPanel2):
  """Scroll panel behavior for nested Mici pagers."""

  def __init__(self, horizontal: bool = True, handle_out_of_bounds: bool = True) -> None:
    super().__init__(horizontal, handle_out_of_bounds=handle_out_of_bounds)

  def _handle_mouse_event(self, mouse_event: MouseEvent, bounds: rl.Rectangle, bounds_size: float,
                          content_size: float) -> None:
    state_before_update = self._state
    super()._handle_mouse_event(mouse_event, bounds, bounds_size, content_size)

    if self._state == ScrollState.MANUAL_SCROLL and state_before_update == ScrollState.PRESSED and \
       self._initial_click_event is not None:
      drag_x = abs(mouse_event.pos.x - self._initial_click_event.pos.x)
      drag_y = abs(mouse_event.pos.y - self._initial_click_event.pos.y)
      primary_drag = drag_x if self._horizontal else drag_y
      cross_drag = drag_y if self._horizontal else drag_x
      if cross_drag > primary_drag:
        self._state = ScrollState.STEADY
        self._velocity = 0.0
        self._velocity_buffer.clear()
