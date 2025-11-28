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

ALERT_MARGIN = 40
ALERT_PADDING = 60
ALERT_LINE_SPACING = 45
ALERT_BORDER_RADIUS = 30

ALERT_FONT_SMALL = 66
ALERT_FONT_MEDIUM = 74
ALERT_FONT_BIG = 88

ALERT_HEIGHTS = {
  AlertSize.small: 271,
  AlertSize.mid: 420,
}

SELFDRIVE_STATE_TIMEOUT = 5
SELFDRIVE_UNRESPONSIVE_TIMEOUT = 10

ALERT_COLORS = {
  AlertStatus.normal: rl.Color(0x15, 0x15, 0x15, 0xF1),
  AlertStatus.userPrompt: rl.Color(0xDA, 0x6F, 0x25, 0xF1),
  AlertStatus.critical: rl.Color(0xC9, 0x22, 0x31, 0xF1),
}


@dataclass
class Alert:
  text1: str = ""
  text2: str = ""
  size: int = 0
  status: int = 0


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

    self._full_text1_label = Label("", font_size=0, font_weight=FontWeight.BOLD,
                                   text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                   text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)

    self._full_text2_label = Label("", font_size=ALERT_FONT_BIG,
                                   text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                   text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)

    # --- Animation state ---
    self._anim_y_offset = -300  # starts above screen
    self._anim_active = False
    self._anim_start_time = 0.0
    self._anim_duration = 0.30
    self._last_alert_id = None

  # --------------------------------------------
  # Alert extraction logic
  # --------------------------------------------
  def get_alert(self, sm: messaging.SubMaster) -> Alert | None:
    ss = sm['selfdriveState']

    recv_frame = sm.recv_frame['selfdriveState']
    if not sm.updated['selfdriveState']:
      time_since_onroad = time.monotonic() - ui_state.started_time
      waiting_for_startup = recv_frame < ui_state.started_frame

      if waiting_for_startup and time_since_onroad > 5:
        return ALERT_STARTUP_PENDING

      if TICI and not waiting_for_startup:
        ss_missing = time.monotonic() - sm.recv_time['selfdriveState']
        if ss_missing > SELFDRIVE_STATE_TIMEOUT:
          if ss.enabled and (ss_missing - SELFDRIVE_STATE_TIMEOUT) < SELFDRIVE_UNRESPONSIVE_TIMEOUT:
            return ALERT_CRITICAL_TIMEOUT
          return ALERT_CRITICAL_REBOOT

    if ss.alertSize == 0:
      return None

    if recv_frame < ui_state.started_frame:
      return None

    return Alert(text1=ss.alertText1, text2=ss.alertText2,
                 size=ss.alertSize.raw, status=ss.alertStatus.raw)

  # --------------------------------------------
  # Render with animation + top-positioning
  # --------------------------------------------
  def _render(self, rect: rl.Rectangle):
    alert = self.get_alert(ui_state.sm)
    if not alert:
      self._anim_active = False
      return

    # Detect alert change → trigger animation
    alert_id = (alert.text1, alert.text2, alert.size, alert.status)
    if alert_id != self._last_alert_id:
      self._anim_active = True
      self._anim_start_time = rl.get_time()
      self._anim_y_offset = -300  # start above the top
      self._last_alert_id = alert_id

    # Update animation
    if self._anim_active:
      t = (rl.get_time() - self._anim_start_time) / self._anim_duration
      t = max(0.0, min(1.0, t))
      eased = 1 - (1 - t)**3  # cubic ease-out
      self._anim_y_offset = -300 + eased * 300

      if t >= 1.0:
        self._anim_active = False
        self._anim_y_offset = 0

    # -------------------
    # TOP POSITION ALERT
    # -------------------
    h = ALERT_HEIGHTS.get(alert.size, rect.height)
    alert_rect = rl.Rectangle(
      rect.x + ALERT_MARGIN,
      rect.y + self._anim_y_offset + ALERT_MARGIN,
      rect.width - ALERT_MARGIN * 2,
      h - ALERT_MARGIN * 2
    )

    self._draw_background(alert_rect, alert)

    text_rect = rl.Rectangle(
      alert_rect.x + ALERT_PADDING,
      alert_rect.y + ALERT_PADDING,
      alert_rect.width - 2 * ALERT_PADDING,
      alert_rect.height - 2 * ALERT_PADDING
    )
    self._draw_text(text_rect, alert)

  # --------------------------------------------
  # Internal drawing helpers
  # --------------------------------------------
  def _draw_background(self, rect: rl.Rectangle, alert: Alert):
    color = ALERT_COLORS.get(alert.status, ALERT_COLORS[AlertStatus.normal])
    roundness = ALERT_BORDER_RADIUS / (min(rect.width, rect.height) / 2)
    rl.draw_rectangle_rounded(rect, roundness, 10, color)

  def _draw_text(self, rect: rl.Rectangle, alert: Alert):
    if alert.size == AlertSize.small:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_MEDIUM)

    elif alert.size == AlertSize.mid:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_BIG, center_y=False)
      rect.y += ALERT_FONT_BIG + ALERT_LINE_SPACING
      self._draw_centered(alert.text2, rect, self.font_regular, ALERT_FONT_SMALL, center_y=False)

    else:
      is_long = len(alert.text1) > 15
      font_size1 = 132 if is_long else 177

      top_offset = 200 if is_long or "\n" in alert.text1 else 270
      title_rect = rl.Rectangle(rect.x, rect.y + top_offset, rect.width, 600)
      self._full_text1_label.set_text(alert.text1)
      self._full_text1_label.set_font_size(font_size1)
      self._full_text1_label.render(title_rect)

      bottom_offset = 361 if is_long else 420
      subtitle_rect = rl.Rectangle(rect.x, rect.y + rect.height - bottom_offset,
                                   rect.width, 300)
      self._full_text2_label.set_text(alert.text2)
      self._full_text2_label.render(subtitle_rect)

  def _draw_centered(self, text, rect, font, font_size, center_y=True, color=rl.WHITE):
    text_size = measure_text_cached(font, text, font_size)
    x = rect.x + (rect.width - text_size.x) / 2
    y = rect.y + ((rect.height - text_size.y) / 2 if center_y else 0)
    rl.draw_text_ex(font, text, rl.Vector2(x, y), font_size, 0, color)