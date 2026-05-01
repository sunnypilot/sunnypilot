"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pyray as rl
from openpilot.system.ui.lib.application import MouseEvent
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2, ScrollState


class GuiScrollPanel2SP(GuiScrollPanel2):
  """Reject orthogonal-dominant drags so nested scrollers (outer horizontal +
  inner vertical) don't both engage on a slightly diagonal swipe.

  Implemented as a post-super state rollback rather than reimplementing the
  PRESSED state machine — keeps stock behaviour authoritative."""

  def _handle_mouse_event(self, mouse_event: MouseEvent, bounds: rl.Rectangle, bounds_size: float,
                          content_size: float) -> None:
    pre_state = self._state
    super()._handle_mouse_event(mouse_event, bounds, bounds_size, content_size)

    if self._state == ScrollState.MANUAL_SCROLL and pre_state == ScrollState.PRESSED and \
       self._initial_click_event is not None:
      diff_x = abs(mouse_event.pos.x - self._initial_click_event.pos.x)
      diff_y = abs(mouse_event.pos.y - self._initial_click_event.pos.y)
      along = diff_x if self._horizontal else diff_y
      anti = diff_y if self._horizontal else diff_x
      if anti > along:
        self._state = ScrollState.STEADY
        self._velocity = 0.0
        self._velocity_buffer.clear()
