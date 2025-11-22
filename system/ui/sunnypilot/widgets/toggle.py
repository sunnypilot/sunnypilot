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
SYMBOL_SIZE = KNOB_RADIUS / 2


class ToggleSP(Toggle):
  def __init__(self, initial_state=False, callback: Callable[[bool], None] | None = None, param: str | None = None):
    self.param_key = param
    self.params = Params()
    if self.param_key:
      initial_state = self.params.get_bool(self.param_key)
    Toggle.__init__(self, initial_state, callback)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    if self._enabled and self.param_key:
      self.params.put_bool(self.param_key, self._state)

  def _render(self, rect: rl.Rectangle):
    self.update()
    if self._enabled:
      bg_color = self._blend_color(style.TOGGLE_OFF_COLOR, style.TOGGLE_ON_COLOR, self._progress)
      knob_color = style.TOGGLE_KNOB_COLOR
    else:
      bg_color = self._blend_color(style.TOGGLE_DISABLED_OFF_COLOR, style.TOGGLE_DISABLED_ON_COLOR, self._progress)
      knob_color = style.TOGGLE_DISABLED_KNOB_COLOR

    # Draw background
    bg_rect = rl.Rectangle(self._rect.x, self._rect.y, style.TOGGLE_WIDTH, style.TOGGLE_BG_HEIGHT)

    # Draw outline first
    outline_color = style.TOGGLE_ON_COLOR
    if not self._enabled:
      # Use a more subtle color for disabled state
      outline_color = rl.Color(outline_color.r // 2, outline_color.g // 2, outline_color.b // 2, 255)

    # Draw outline by drawing a slightly larger rounded rectangle behind the background
    outline_rect = rl.Rectangle(bg_rect.x - 2, bg_rect.y - 2, bg_rect.width + 4, bg_rect.height + 4)
    rl.draw_rectangle_rounded(outline_rect, 1.0, 10, outline_color)

    # Draw actual background
    rl.draw_rectangle_rounded(bg_rect, 1.0, 10, bg_color)

    left_edge = bg_rect.x + KNOB_PADDING
    right_edge = bg_rect.x + bg_rect.width - KNOB_PADDING

    knob_travel_distance = right_edge - left_edge - 2 * KNOB_RADIUS
    min_knob_x = left_edge + KNOB_RADIUS
    knob_x = min_knob_x + knob_travel_distance * self._progress
    knob_y = self._rect.y + style.TOGGLE_BG_HEIGHT / 2

    rl.draw_circle(int(knob_x), int(knob_y), KNOB_RADIUS, knob_color)

    if self._state and (self._enabled or self._progress > 0.5):
      # Draw checkmark when toggle is ON
      start_x = knob_x - SYMBOL_SIZE * 0.8
      start_y = knob_y
      mid_x = knob_x - SYMBOL_SIZE * 0.1
      mid_y = knob_y + SYMBOL_SIZE * 0.6
      end_x = knob_x + SYMBOL_SIZE * 0.8
      end_y = knob_y - SYMBOL_SIZE * 0.5

      rl.draw_line_ex(
        rl.Vector2(int(start_x), int(start_y)),
        rl.Vector2(int(mid_x), int(mid_y)),
        3,
        style.TOGGLE_ON_COLOR
      )
      rl.draw_line_ex(
        rl.Vector2(int(mid_x), int(mid_y)),
        rl.Vector2(int(end_x), int(end_y)),
        3,
        style.TOGGLE_ON_COLOR
      )
    else:
      # Draw X when toggle is OFF
      x_offset = SYMBOL_SIZE * 0.65

      rl.draw_line_ex(
        rl.Vector2(int(knob_x - x_offset), int(knob_y - x_offset)),
        rl.Vector2(int(knob_x + x_offset), int(knob_y + x_offset)),
        3,
        style.TOGGLE_OFF_COLOR
      )
      rl.draw_line_ex(
        rl.Vector2(int(knob_x + x_offset), int(knob_y - x_offset)),
        rl.Vector2(int(knob_x - x_offset), int(knob_y + x_offset)),
        3,
        style.TOGGLE_OFF_COLOR
      )
