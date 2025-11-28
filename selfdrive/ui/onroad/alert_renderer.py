import time
import pyray as rl
from dataclasses import dataclass
from cereal import messaging, log
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware import TICI
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import Label

AlertSize = log.SelfdriveState.AlertSize
AlertStatus = log.SelfdriveState.AlertStatus

# Minimalist spacing & sizing
ALERT_MARGIN = 40
ALERT_PADDING = 50
ALERT_LINE_SPACING = 36
ALERT_CORNER_RADIUS = 24  # softer radius

# Typography
ALERT_FONT_SMALL = 60
ALERT_FONT_MEDIUM = 74
ALERT_FONT_BIG = 92

# Height presets for small/mid alerts
ALERT_HEIGHTS = {
  AlertSize.small: 250,
  AlertSize.mid: 360,
}

SELFDRIVE_STATE_TIMEOUT = 5
SELFDRIVE_UNRESPONSIVE_TIMEOUT = 10

# Minimalist color palette
ALERT_COLORS = {
  AlertStatus.normal: rl.Color(25, 25, 25, 235),      # soft charcoal
  AlertStatus.userPrompt: rl.Color(218, 111, 37, 235), # warm amber
  AlertStatus.critical: rl.Color(201, 34, 49, 235),    # softened danger red
}

# Soft iOS-style blur shadow layers
def draw_soft_shadow(rect: rl.Rectangle, radius: float):
  shadow_colors = [
    rl.Color(0, 0, 0, 40),
    rl.Color(0, 0, 0, 28),
    rl.Color(0, 0, 0, 18),
  ]

  expansions = [10, 20, 30]

  for expand, col in zip(expansions, shadow_colors):
    expanded = rl.Rectangle(
      rect.x - expand / 2,
      rect.y - expand / 2,
      rect.width + expand,
      rect.height + expand,
    )
    rl.draw_rectangle_rounded(expanded, radius, 16, col)


@dataclass
class Alert:
  text1: str = ""
  text2: str = ""
  size: int = 0
  status: int = 0


# Predefined alerts
ALERT_STARTUP_PENDING = Alert(
  text1=tr("hoofpilot Unavailable"),
  text2=tr("Waiting to start"),
  size=AlertSize.mid,
  status=AlertStatus.normal,
)
ALERT_CRITICAL_TIMEOUT = Alert(
  text1=tr("TAKE CONTROL IMMEDIATELY"),
  text2=tr("System Unresponsive"),
  size=AlertSize.full,
  status=AlertStatus.critical,
)
ALERT_CRITICAL_REBOOT = Alert(
  text1=tr("System Unresponsive"),
  text2=tr("Reboot Device"),
  size=AlertSize.mid,
  status=AlertStatus.normal,
)


class AlertRenderer(Widget):
  def __init__(self):
    super().__init__()
    self.font_regular = gui_app.font(FontWeight.NORMAL)
    self.font_bold = gui_app.font(FontWeight.BOLD)

    self._full_text1_label = Label(
      "",
      font_size=0,
      font_weight=FontWeight.BOLD,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
    )
    self._full_text2_label = Label(
      "",
      font_size=ALERT_FONT_BIG,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
    )

    # Slide animation
    self._anim_active = False
    self._anim_start_time = 0.0
    self._anim_duration = 0.28
    self._last_alert: Alert | None = None

  def get_alert(self, sm: messaging.SubMaster):
    ss = sm["selfdriveState"]

    recv_frame = sm.recv_frame["selfdriveState"]
    if not sm.updated["selfdriveState"]:
      time_since_onroad = time.monotonic() - ui_state.started_time

      waiting = recv_frame < ui_state.started_frame
      if waiting and time_since_onroad > 5:
        return ALERT_STARTUP_PENDING

      if TICI and not waiting:
        ss_missing = time.monotonic() - sm.recv_time["selfdriveState"]
        if ss_missing > SELFDRIVE_STATE_TIMEOUT:
          if ss.enabled and (ss_missing - SELFDRIVE_STATE_TIMEOUT) < SELFDRIVE_UNRESPONSIVE_TIMEOUT:
            return ALERT_CRITICAL_TIMEOUT
          return ALERT_CRITICAL_REBOOT

    if ss.alertSize == 0:
      return None
    if recv_frame < ui_state.started_frame:
      return None

    return Alert(
      text1=ss.alertText1,
      text2=ss.alertText2,
      size=ss.alertSize.raw,
      status=ss.alertStatus.raw,
    )

  def _maybe_start_animation(self, alert):
    if alert is None:
      self._anim_active = False
      self._last_alert = None
      return

    if alert.status != AlertStatus.normal:
      self._anim_active = False
      self._last_alert = alert
      return

    if (
      self._last_alert is None
      or self._last_alert.text1 != alert.text1
      or self._last_alert.text2 != alert.text2
      or self._last_alert.size != alert.size
      or self._last_alert.status != alert.status
    ):
      self._anim_active = True
      self._anim_start_time = rl.get_time()
      self._last_alert = alert

  def _anim_progress(self):
    if not self._anim_active:
      return 1.0

    elapsed = rl.get_time() - self._anim_start_time
    if elapsed >= self._anim_duration:
      self._anim_active = False
      return 1.0

    t = elapsed / self._anim_duration
    return 1.0 - (1.0 - t) ** 3  # cubic out

  def _render(self, rect):
    alert = self.get_alert(ui_state.sm)
    self._maybe_start_animation(alert)

    if not alert:
      return

    alert_rect = self._get_alert_rect(rect, alert.size)

    # Slide-in animation
    if alert.status == AlertStatus.normal:
      p = self._anim_progress()
      start_y = alert_rect.y - 70
      cur_y = start_y + (alert_rect.y - start_y) * p
      alert_rect = rl.Rectangle(alert_rect.x, cur_y, alert_rect.width, alert_rect.height)

    # Soft shadow
    draw_soft_shadow(alert_rect, ALERT_CORNER_RADIUS / 50)

    # Background
    self._draw_background(alert_rect, alert)

    # Text region
    inner = rl.Rectangle(
      alert_rect.x + ALERT_PADDING,
      alert_rect.y + ALERT_PADDING,
      alert_rect.width - ALERT_PADDING * 2,
      alert_rect.height - ALERT_PADDING * 2,
    )
    self._draw_text(inner, alert)

  def _get_alert_rect(self, rect, size):
    if size == AlertSize.full:
      return rl.Rectangle(rect.x, rect.y, rect.width, rect.height)

    h = ALERT_HEIGHTS.get(size, rect.height)
    return rl.Rectangle(
      rect.x + ALERT_MARGIN,
      rect.y + ALERT_MARGIN,
      rect.width - 2 * ALERT_MARGIN,
      h,
    )

  def _draw_background(self, rect, alert):
    color = ALERT_COLORS.get(alert.status, ALERT_COLORS[AlertStatus.normal])
    rl.draw_rectangle_rounded(rect, ALERT_CORNER_RADIUS / (rect.height / 2), 24, color)

    # subtle white border (1 px)
    border_col = rl.Color(255, 255, 255, 40)
    rl.draw_rectangle_rounded_lines_ex(rect, ALERT_CORNER_RADIUS / (rect.height / 2), 24, 2, border_col)

  def _draw_text(self, rect, alert):
    if alert.size == AlertSize.small:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_MEDIUM)

    elif alert.size == AlertSize.mid:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_BIG, center_y=False)
      rect.y += ALERT_FONT_BIG + ALERT_LINE_SPACING
      self._draw_centered(alert.text2, rect, self.font_regular, ALERT_FONT_SMALL, center_y=False)

    else:  # full-size
      is_long = len(alert.text1) > 15
      font_size1 = 140 if is_long else 170
      top_offset = 200 if is_long else 260

      # Title
      r1 = rl.Rectangle(rect.x, rect.y + top_offset, rect.width, 300)
      self._full_text1_label.set_font_size(font_size1)
      self._full_text1_label.set_text(alert.text1)
      self._full_text1_label.render(r1)

      # Subtitle
      r2 = rl.Rectangle(rect.x, rect.y + rect.height - 360, rect.width, 260)
      self._full_text2_label.set_text(alert.text2)
      self._full_text2_label.render(r2)

  def _draw_centered(self, text, rect, font, size, center_y=True):
    ts = measure_text_cached(font, text, size)
    x = rect.x + (rect.width - ts.x) / 2
    y = rect.y + ((rect.height - ts.y) / 2 if center_y else 0)
    rl.draw_text_ex(font, text, rl.Vector2(x, y), size, 0, rl.WHITE)