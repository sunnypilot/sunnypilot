"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.mici.onroad.hud_renderer import HudRenderer, FONT_SIZES, SET_SPEED_PERSISTENCE
from openpilot.selfdrive.ui.sunnypilot.onroad.blind_spot_indicators import BlindSpotIndicators
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.text_measure import measure_text_cached


class HudRendererSP(HudRenderer):
  def __init__(self):
    super().__init__()
    self.blind_spot_indicators = BlindSpotIndicators()

  def _update_state(self) -> None:
    super()._update_state()
    self.blind_spot_indicators.update()

  def _render(self, rect: rl.Rectangle) -> None:
    super()._render(rect)
    self.blind_spot_indicators.render(rect)

  def _draw_model_source(self, rect: rl.Rectangle) -> None:
    self._egpu_fade_time = rl.get_time() - SET_SPEED_PERSISTENCE / 2
    super()._draw_model_source(rect)

    if not ui_state.usbgpu_loading or ui_state.sm.recv_frame['selfdriveState'] < ui_state.started_frame:
      return

    icon = self._txt_egpu
    pos = rl.Vector2(rect.x + rect.width - 10 - icon.width,
                     rect.y + rect.height - 14 - (self._txt_wheel.height + icon.height) / 2)

    pct_text = f"{ui_state.usbgpu_load_progress}%"
    size = FONT_SIZES.max_speed
    cell = measure_text_cached(self._font_bold, "0", size)
    widths = [cell.x if c.isdigit() else measure_text_cached(self._font_bold, c, size).x for c in pct_text]
    x = pos.x - 8 - sum(widths)
    y = pos.y + (icon.height - cell.y) / 2
    for c, w in zip(pct_text, widths):
      glyph = measure_text_cached(self._font_bold, c, size).x
      rl.draw_text_ex(self._font_bold, c, rl.Vector2(x + (w - glyph) / 2, y), size, 0, rl.WHITE)
      x += w

  def _has_blind_spot_detected(self) -> bool:

    return self.blind_spot_indicators.detected
