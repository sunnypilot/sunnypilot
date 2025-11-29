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

# Soft, modern iOS-style metrics
PADDING_X = 60
PADDING_Y = 48
SPACING = 32
MIN_WIDTH = 600
MAX_WIDTH = 1400
TOP_MARGIN = 36
RADIUS = 50

FONT_BIG = 88
FONT_MED = 72
FONT_SMALL = 60

BLUR_ALPHA = 155   # Light blur/translucent effect (Option A)

SELFDRIVE_STATE_TIMEOUT = 5
SELFDRIVE_UNRESPONSIVE_TIMEOUT = 10

# Alert colors — kept soft & flat for minimal design
ALERT_COLORS = {
  AlertStatus.normal: rl.Color(30, 30, 30, 220),
  AlertStatus.userPrompt: rl.Color(218, 111, 37, 230),
  AlertStatus.critical: rl.Color(201, 34, 49, 230),
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

    self._full_text1 = Label(
      "", font_size=0, font_weight=FontWeight.BOLD,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER
    )
    self._full_text2 = Label(
      "", font_size=FONT_BIG,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER
    )

    # Animation
    self._anim_active = False
    self._anim_start = 0.0
    self._anim_duration = 0.28
    self._last_alert = None


  # ---------------------
  # Dynamic alert fetching
  # ---------------------

  def get_alert(self, sm: messaging.SubMaster):
    ss = sm["selfdriveState"]
    recv_frame = sm.recv_frame["selfdriveState"]

    if not sm.updated["selfdriveState"]:
      elapsed = time.monotonic() - ui_state.started_time
      waiting = recv_frame < ui_state.started_frame

      if waiting and elapsed > 5:
        return ALERT_STARTUP_PENDING

      if TICI and not waiting:
        missing = time.monotonic() - sm.recv_time["selfdriveState"]
        if missing > SELFDRIVE_STATE_TIMEOUT:
          if ss.enabled and (missing - SELFDRIVE_STATE_TIMEOUT) < SELFDRIVE_UNRESPONSIVE_TIMEOUT:
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


  # ---------------------
  # Animation manager
  # ---------------------

  def _maybe_start_animation(self, alert):
    if alert is None:
      self._last_alert = None
      self._anim_active = False
      return

    if alert.status != AlertStatus.normal:
      self._last_alert = alert
      self._anim_active = False
      return

    if (
      self._last_alert is None or
      self._last_alert.text1 != alert.text1 or
      self._last_alert.text2 != alert.text2 or
      self._last_alert.size != alert.size or
      self._last_alert.status != alert.status
    ):
      self._anim_active = True
      self._anim_start = rl.get_time()

    self._last_alert = alert


  def _anim_progress(self):
    if not self._anim_active:
      return 1.0

    elapsed = rl.get_time() - self._anim_start
    if elapsed >= self._anim_duration:
      self._anim_active = False
      return 1.0

    t = elapsed / self._anim_duration
    return 1 - (1 - t) ** 3   # cubic-out easing


  # -------------------------
  # Dynamic layout calculation
  # -------------------------

  def _compute_size(self, alert):
    # Measure width from both lines
    w1 = measure_text_cached(self.font_bold, alert.text1, FONT_BIG).x
    w2 = measure_text_cached(self.font_regular, alert.text2, FONT_MED).x

    text_width = max(w1, w2)
    total_width = text_width + PADDING_X * 2

    # Clamp to nice range
    total_width = max(MIN_WIDTH, min(total_width, MAX_WIDTH))

    # Height depends on text
    height = PADDING_Y * 2 + FONT_BIG
    if alert.text2:
      height += SPACING + FONT_MED

    return total_width, height


  # ---------------------
  # Rendering
  # ---------------------

  def _render(self, rect: rl.Rectangle):
    alert = self.get_alert(ui_state.sm)
    self._maybe_start_animation(alert)

    if not alert:
      return

    # Calculate dynamic width/height
    box_width, box_height = self._compute_size(alert)

    # Centered top position
    x = rect.x + (rect.width - box_width) / 2
    y = rect.y + TOP_MARGIN

    # Apply slide-in animation
    if alert.status == AlertStatus.normal:
      p = self._anim_progress()
      y -= (1 - p) * 60   # slide from above

    alert_rect = rl.Rectangle(x, y, box_width, box_height)

    self._draw_blur_background(alert_rect, alert)
    self._draw_text(alert_rect, alert)


  # ---------------------
  # Blur background
  # ---------------------

  def _draw_blur_background(self, rect, alert):
    # Light translucency
    base = ALERT_COLORS.get(alert.status, ALERT_COLORS[AlertStatus.normal])

    # iOS light blur style glass
    blur_color = rl.Color(base.r, base.g, base.b, BLUR_ALPHA)

    # Rounded background
    rl.draw_rectangle_rounded(rect, 0.18, 16, blur_color)


  # ---------------------
  # Text rendering
  # ---------------------

  def _draw_text(self, rect, alert):
    # Title centered
    title_size = measure_text_cached(self.font_bold, alert.text1, FONT_BIG)
    title_x = rect.x + (rect.width - title_size.x) / 2
    title_y = rect.y + PADDING_Y
    rl.draw_text_ex(
      self.font_bold, alert.text1,
      rl.Vector2(title_x, title_y), FONT_BIG, 0, rl.WHITE
    )

    # Secondary line
    if alert.text2:
      subtitle_size = measure_text_cached(self.font_regular, alert.text2, FONT_MED)
      subtitle_x = rect.x + (rect.width - subtitle_size.x) / 2
      subtitle_y = title_y + FONT_BIG + SPACING
      rl.draw_text_ex(
        self.font_regular, alert.text2,
        rl.Vector2(subtitle_x, subtitle_y), FONT_MED, 0, rl.WHITE
      )