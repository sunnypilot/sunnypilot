"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The tizi onroad Set Speed Assist button, in the corner and size of the experimental mode button
upstream retired with chill mode: the gauge dimmed with the assist off, bright in a green ring with
it on.
"""
import pyray as rl

from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_badge import draw_gauge_on_dial
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets import Widget

GAUGE_HEIGHT = 96  # concentric with the button: the swoosh's outer edge ~60 px from its center, inside the ring
OFF_ALPHA = 0.35
RING_WIDTH = 8
RING_COLOR = rl.Color(0x16, 0x7F, 0x40, 0xFF)  # the engaged border's green (augmented_road_view)


class SpeedAssistButton(Widget):
  def __init__(self, button_size: int):
    super().__init__()
    self._engageable: bool = False
    self._black_bg: rl.Color = rl.Color(0, 0, 0, 166)
    self._rect = rl.Rectangle(0, 0, button_size, button_size)
    # stays pressed past a tap whose press and release land in one frame, so the road view,
    # which handles its events after this button, still sees it pressed and skips the sidebar
    self._click_delay = 0.075

  def set_rect(self, rect: rl.Rectangle) -> None:
    self._rect.x, self._rect.y = rect.x, rect.y

  def _update_state(self) -> None:
    selfdrive_state = ui_state.sm["selfdriveState"]
    self._engageable = selfdrive_state.engageable or selfdrive_state.enabled

  def _handle_mouse_release(self, _):
    super()._handle_mouse_release(_)
    ui_state.toggle_speed_assist()

  def _render(self, rect: rl.Rectangle) -> None:
    center_x = int(self._rect.x + self._rect.width // 2)
    center_y = int(self._rect.y + self._rect.height // 2)
    alpha = 180 / 255 if self.is_pressed or not self._engageable else 1.0

    radius = self._rect.width / 2
    rl.draw_circle(center_x, center_y, radius, self._black_bg)
    if ui_state.speed_assist:
      rl.draw_ring(rl.Vector2(center_x, center_y), radius - RING_WIDTH, radius, 0, 360, 96, rl.color_alpha(RING_COLOR, alpha))
    draw_gauge_on_dial(center_x, center_y, GAUGE_HEIGHT, alpha if ui_state.speed_assist else OFF_ALPHA * alpha)
