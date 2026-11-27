"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.cereal import log
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import Alert, AlertRenderer
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, TextAlignment, gui_app
from openpilot.system.ui.widgets.label import UnifiedLabel

AlertStatus = log.SelfdriveState.AlertStatus


class RoboticAlertOverlay:
  """Harmonized alert overlay that keeps robotic expressions visible while preserving safety readability."""

  def __init__(self):
    dt = 1.0 / max(gui_app.target_fps, 1)
    self._alert_source = AlertRenderer()
    self._prev_alert: Alert | None = None
    self._alpha_filter = FirstOrderFilter(0.0, 0.06, dt)

    self._text1_label = UnifiedLabel(
      text="",
      font_size=44,
      font_weight=FontWeight.DISPLAY,
      alignment=TextAlignment.CENTER,
      line_height=0.9,
    )
    self._text2_label = UnifiedLabel(
      text="",
      font_size=26,
      font_weight=FontWeight.MEDIUM,
      alignment=TextAlignment.CENTER,
      line_height=0.95,
    )

  def get_alert(self) -> Alert | None:
    alert = self._alert_source.get_alert(ui_state.sm)
    if gui_app.sunnypilot_ui():
      ui_state.onroad_brightness_handle_alerts(ui_state, alert)
    return alert

  def render(self, rect: rl.Rectangle, alert: Alert | None) -> float:
    """Render alert overlay and return current alpha (0..1) so caller can shift face if needed."""
    alpha = self._alpha_filter.update(1.0 if alert is not None else 0.0)
    if alert is not None:
      self._prev_alert = alert
    elif alpha > 0.02 and self._prev_alert is not None:
      alert = self._prev_alert
    else:
      self._prev_alert = None
      return 0.0

    is_critical = alert.status == AlertStatus.critical
    is_prompt = alert.status == AlertStatus.userPrompt

    if is_critical:
      pulse = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(rl.get_time() * 14.0))
      # Pulsing red edge frame + bottom dark backing so red eyes + takeover text are unmistakable
      border_col = rl.Color(255, 25, 35, int(230 * pulse * alpha))
      rl.draw_rectangle_rounded_lines_ex(
        rl.Rectangle(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6),
        0.16,
        12,
        10.0,
        border_col,
      )
      band_h = 98
      rl.draw_rectangle_gradient_v(
        int(rect.x),
        int(rect.y + rect.height - band_h - 18),
        int(rect.width),
        band_h + 18,
        rl.Color(180, 0, 15, 0),
        rl.Color(210, 0, 20, int(230 * alpha)),
      )
      self._draw_banner_text(rect, alert, rect.y + rect.height - band_h + 4, band_h, alpha, big=True)
    elif is_prompt:
      band_h = 84
      rl.draw_rectangle_gradient_v(
        int(rect.x),
        int(rect.y + rect.height - band_h - 14),
        int(rect.width),
        band_h + 14,
        rl.Color(220, 95, 0, 0),
        rl.Color(235, 105, 0, int(215 * alpha)),
      )
      self._draw_banner_text(rect, alert, rect.y + rect.height - band_h + 6, band_h, alpha, big=False)
    else:
      # Soft / normal alert: compact bottom pill leaving the expressive eyes unobstructed
      band_h = 66
      pill = rl.Rectangle(rect.x + 24, rect.y + rect.height - band_h - 8, rect.width - 48, band_h)
      rl.draw_rectangle_rounded(pill, 0.38, 12, rl.Color(24, 28, 34, int(215 * alpha)))
      rl.draw_rectangle_rounded_lines_ex(pill, 0.38, 12, 2.0, rl.Color(255, 255, 255, int(45 * alpha)))
      self._draw_banner_text(rect, alert, pill.y + 6, band_h - 8, alpha, big=False)

    return alpha

  def _draw_banner_text(
    self,
    rect: rl.Rectangle,
    alert: Alert,
    top_y: float,
    band_h: float,
    alpha: float,
    big: bool,
  ) -> None:
    text1 = alert.text1.lower()
    text2 = alert.text2.lower()

    if big:
      font1 = 42 if len(text1) <= 18 else 34
    else:
      font1 = 34 if len(text1) <= 22 else 28

    margin_x = 34
    w = rect.width - margin_x * 2

    self._text1_label.set_text(text1)
    self._text1_label.set_font_size(font1)
    self._text1_label.set_text_color(rl.Color(255, 255, 255, int(245 * alpha)))
    self._text1_label.render(rl.Rectangle(rect.x + margin_x, top_y, w, band_h))

    if text2:
      font2 = 24 if len(text2) <= 28 else 20
      self._text2_label.set_text(text2)
      self._text2_label.set_font_size(font2)
      self._text2_label.set_text_color(rl.Color(255, 255, 255, int(195 * alpha)))
      self._text2_label.render(rl.Rectangle(rect.x + margin_x, top_y + font1 + 2, w, max(24.0, band_h - font1)))
