"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import MousePos
from openpilot.system.ui.widgets.toggle import Toggle
from openpilot.system.ui.sunnypilot.lib.styles import style

KNOB_PADDING = 5
KNOB_RADIUS = style.TOGGLE_BG_HEIGHT / 2 - KNOB_PADDING


class ToggleSP(Toggle):
  def __init__(self, initial_state=False, callback: Callable[[bool], None] | None = None, param: str | None = None):
    self.param_key = param
    self.params = Params()
    if self.param_key:
      initial_state = self.params.get_bool(self.param_key)
    Toggle.__init__(self, initial_state, callback)

  def set_rect(self, rect: rl.Rectangle):
    self._rect = rl.Rectangle(rect.x, rect.y, style.TOGGLE_WIDTH, style.TOGGLE_HEIGHT)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    if self._enabled and self.param_key:
      self.params.put_bool(self.param_key, self._state)

  def _render(self, rect: rl.Rectangle):
    self.update()
    self._rect.y -= style.ITEM_PADDING / 2
    if self._enabled:
      bg_color = self._blend_color(style.TOGGLE_OFF_COLOR, style.TOGGLE_ON_COLOR, self._progress)
      knob_color = style.TOGGLE_KNOB_COLOR
    else:
      bg_color = self._blend_color(style.TOGGLE_DISABLED_OFF_COLOR, style.TOGGLE_DISABLED_ON_COLOR, self._progress)
      knob_color = style.TOGGLE_DISABLED_KNOB_COLOR

    # Draw background
    bg_rect = rl.Rectangle(self._rect.x, self._rect.y, style.TOGGLE_WIDTH, style.TOGGLE_BG_HEIGHT)

    # Draw actual background
    rl.draw_rectangle_rounded(bg_rect, 1.0, 10, bg_color)

    left_edge = bg_rect.x + KNOB_PADDING
    right_edge = bg_rect.x + bg_rect.width - KNOB_PADDING

    knob_travel_distance = right_edge - left_edge - 2 * KNOB_RADIUS
    min_knob_x = left_edge + KNOB_RADIUS
    knob_x = min_knob_x + knob_travel_distance * self._progress
    knob_y = self._rect.y + style.TOGGLE_BG_HEIGHT / 2

    rl.draw_circle(int(knob_x), int(knob_y), KNOB_RADIUS, knob_color)
