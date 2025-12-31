import pyray as rl
from openpilot.selfdrive.ui.onroad.alert_renderer import AlertRenderer, AlertSize, ALERT_FONT_MEDIUM, ALERT_FONT_BIG, \
  ALERT_FONT_SMALL, ALERT_MARGIN, ALERT_HEIGHTS, ALERT_PADDING, Alert
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.wrap_text import wrap_text

ALERT_LINE_SPACING = 15

class AlertRendererSP(AlertRenderer):
  def __init__(self):
    super().__init__()

  def _draw_text(self, rect: rl.Rectangle, alert: Alert) -> None:
    if alert.size == AlertSize.small:
      self._draw_multiline_centered(alert.text1, rect, self.font_bold, ALERT_FONT_MEDIUM)

    elif alert.size == AlertSize.mid:
      wrap_width = int(rect.width)
      lines1 = wrap_text(self.font_bold, alert.text1, ALERT_FONT_BIG, wrap_width)
      lines2 = wrap_text(self.font_regular, alert.text2, ALERT_FONT_SMALL, wrap_width) if alert.text2 else []

      total_text_height = len(lines1) * measure_text_cached(self.font_bold, "A", ALERT_FONT_BIG).y
      if lines2:
        total_text_height += ALERT_LINE_SPACING + len(lines2) * measure_text_cached(self.font_regular, "A", ALERT_FONT_SMALL).y

      curr_y = rect.y + (rect.height - total_text_height) / 2

      for line in lines1:
        line_height = measure_text_cached(self.font_bold, "A", ALERT_FONT_BIG).y
        self._draw_line_centered(line, rl.Rectangle(rect.x, curr_y, rect.width, line_height), self.font_bold, ALERT_FONT_BIG)
        curr_y += line_height

      if lines2:
        curr_y += ALERT_LINE_SPACING
        for line in lines2:
          line_height = measure_text_cached(self.font_regular, "A", ALERT_FONT_SMALL).y
          self._draw_line_centered(line, rl.Rectangle(rect.x, curr_y, rect.width, line_height), self.font_regular, ALERT_FONT_SMALL)
          curr_y += line_height

    else:
      super()._draw_text(rect, alert)

  def _draw_multiline_centered(self, text, rect, font, font_size, color=rl.WHITE) -> None:
    lines = wrap_text(font, text, font_size, rect.width)
    line_height = measure_text_cached(font, "A", font_size).y
    total_height = len(lines) * line_height
    curr_y = rect.y + (rect.height - total_height) / 2
    for line in lines:
      self._draw_line_centered(line, rl.Rectangle(rect.x, curr_y, rect.width, line_height), font, font_size, color)
      curr_y += line_height

  def _draw_line_centered(self, text, rect, font, font_size, color=rl.WHITE) -> None:
    text_size = measure_text_cached(font, text, font_size)
    x = rect.x + (rect.width - text_size.x) / 2
    y = rect.y
    rl.draw_text_ex(font, text, rl.Vector2(x, y), font_size, 0, color)

  def _get_alert_rect(self, rect: rl.Rectangle, size: int) -> rl.Rectangle:
    if size == AlertSize.full:
      return rect

    dev_ui_info = ui_state.developer_ui
    v_adjustment = 40 if dev_ui_info in {2, 3} and size != AlertSize.full else 0
    h_adjustment = 230 if dev_ui_info in {1, 3} and size != AlertSize.full else 0

    w = int(rect.width - ALERT_MARGIN * 2 - h_adjustment)
    h = self._calculate_dynamic_height(size, w)
    return rl.Rectangle(rect.x + ALERT_MARGIN, rect.y + rect.height - h + ALERT_MARGIN - v_adjustment, w,
                        h - ALERT_MARGIN * 2)

  def _calculate_dynamic_height(self, size: int, width: int) -> int:
    alert = self.get_alert(ui_state.sm)
    if not alert:
      return ALERT_HEIGHTS.get(size, 271)

    height = 2 * ALERT_PADDING
    wrap_width = width - 2 * ALERT_PADDING

    if size == AlertSize.small:
      lines = wrap_text(self.font_bold, alert.text1, ALERT_FONT_MEDIUM, wrap_width)
      line_height = measure_text_cached(self.font_bold, "A", ALERT_FONT_MEDIUM).y
      height += len(lines) * line_height
    elif size == AlertSize.mid:
      lines1 = wrap_text(self.font_bold, alert.text1, ALERT_FONT_BIG, wrap_width)
      line_height1 = measure_text_cached(self.font_bold, "A", ALERT_FONT_BIG).y
      height += len(lines1) * line_height1

      if alert.text2:
        lines2 = wrap_text(self.font_regular, alert.text2, ALERT_FONT_SMALL, wrap_width)
        line_height2 = measure_text_cached(self.font_regular, "A", ALERT_FONT_SMALL).y
        height += ALERT_LINE_SPACING + len(lines2) * line_height2
    else:
      height = ALERT_HEIGHTS.get(size, 271)

    return int(height)
