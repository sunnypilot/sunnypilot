# ================================================================
# TIZI GLASS OFFROAD ALERTS  (Hoofpilot Edition)
# Frosted-glass cards, soft glows, squish animations, fading scrollbar
# ================================================================
import pyray as rl
import re
import time
import math
from dataclasses import dataclass
from enum import IntEnum

from openpilot.common.params import Params
from openpilot.selfdrive.selfdrived.alertmanager import OFFROAD_ALERTS
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr

REFRESH_INTERVAL = 5.0
FADEOUT_DELAY = 1.0
FADE_SPEED = 4.0  # controls scrollbar fade-in/out timing


# ================================================================
# ENUMS / DATA
# ================================================================

class AlertSize(IntEnum):
  SMALL = 0
  MEDIUM = 1
  BIG = 2


@dataclass
class AlertData:
  key: str
  text: str
  severity: int
  visible: bool = False


# ================================================================
# GLASS ALERT CARD WIDGET
# ================================================================

class GlassAlertCard(Widget):
  WIDTH = 1720
  MIN_HEIGHT = 240
  PADDING = 48

  ICON_SIZE = 96
  ICON_MARGIN = 36

  GLOW_STRENGTH = 26

  PRESS_SCALE = 0.96  # squish scale target
  PRESS_SPEED = 10.0  # smoothing speed

  def __init__(self, alert_data: AlertData):
    super().__init__()
    self.alert_data = alert_data

    # Load severity icons
    self.icon_green = gui_app.texture("icons_mici/offroad_alerts/icon_green.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_orange = gui_app.texture("icons_mici/offroad_alerts/icon_orange.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_red = gui_app.texture("icons_mici/offroad_alerts/icon_red.png", self.ICON_SIZE, self.ICON_SIZE)

    # Text labels
    self.title_label = UnifiedLabel("", 58, FontWeight.SEMI_BOLD, rl.WHITE,
                                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                                    alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP, line_height=1.0)

    self.body_label = UnifiedLabel("", 46, FontWeight.ROMAN, rl.Color(240, 240, 240, 255),
                                   alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                                   alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP, line_height=1.0)

    # Animation state
    self.scale_anim = 1.0

    self.update_content()

  # ------------------------------------------------------------
  # TEXT SPLITTING
  # ------------------------------------------------------------
  def split_text(self, text: str):
    match = re.search(r'[.!?](?:\s+|$)', text)
    if match:
      return text[:match.start()].strip(), text[match.end():].strip()
    return "", text

  # ------------------------------------------------------------
  # CONTENT UPDATE
  # ------------------------------------------------------------
  def update_content(self):
    if not self.alert_data.visible or not self.alert_data.text:
      self.set_visible(False)
      return

    self.set_visible(True)

    title, body = self.split_text(self.alert_data.text)
    self.title_label.set_text(title)
    self.body_label.set_text(body)

    # Calculate height based on label sizes
    text_width = self.WIDTH - self.PADDING * 2 - self.ICON_SIZE - self.ICON_MARGIN
    title_height = self.title_label.get_content_height(text_width)
    body_height = self.body_label.get_content_height(text_width)

    height = max(self.MIN_HEIGHT, title_height + body_height + self.PADDING * 2)

    self.set_rect(rl.Rectangle(0, 0, self.WIDTH, height))

  # ------------------------------------------------------------
  # RENDERING
  # ------------------------------------------------------------
  def _render(self, _):
    if not self.alert_data.visible:
      return

    # Smooth squish animation
    target = self.PRESS_SCALE if self.is_pressed else 1.0
    self.scale_anim += (target - self.scale_anim) * rl.get_frame_time() * self.PRESS_SPEED

    # Centered scaled drawing
    cx = self._rect.x + self._rect.width / 2
    cy = self._rect.y + self._rect.height / 2

    rl.rl_push_matrix()
    rl.rl_translatef(cx, cy, 0)
    rl.rl_scalef(self.scale_anim, self.scale_anim, 1)
    rl.rl_translatef(-cx, -cy, 0)

    # --------------------------------------------------------
    # GLASS BACKGROUND
    # --------------------------------------------------------
    bg = rl.Color(255, 255, 255, 28)
    stroke = rl.Color(255, 255, 255, 70)
    glow_color = {
      -1: rl.Color(100, 255, 150, 80),
       0: rl.Color(255, 190, 90, 80),
       1: rl.Color(255, 95, 95, 90)
    }[self.alert_data.severity]

    rect = self._rect

    # outer glow
    rl.draw_rectangle_rounded(rect, 0.14, 12, glow_color)
    # inset glass pane
    inner = rl.Rectangle(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
    rl.draw_rectangle_rounded(inner, 0.14, 12, bg)
    rl.draw_rectangle_rounded_lines(inner, 0.14, 12, stroke)

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------
    text_x = rect.x + self.PADDING
    text_y = rect.y + self.PADDING
    text_w = rect.width - self.PADDING * 2 - self.ICON_SIZE - self.ICON_MARGIN

    self.title_label.render(rl.Rectangle(text_x, text_y, text_w, 200))
    text_y += self.title_label.get_content_height(text_w) + 16
    self.body_label.render(rl.Rectangle(text_x, text_y, text_w, rect.height - text_y))

    # --------------------------------------------------------
    # SEVERITY ICON
    # --------------------------------------------------------
    if self.alert_data.severity == -1:
      icon = self.icon_green
    elif self.alert_data.severity == 0:
      icon = self.icon_orange
    else:
      icon = self.icon_red

    ix = rect.x + rect.width - self.PADDING - self.ICON_SIZE
    iy = rect.y + self.PADDING

    rl.draw_texture(icon, int(ix), int(iy), rl.WHITE)

    rl.rl_pop_matrix()


# ================================================================
# MAIN ALERTS LAYOUT
# ================================================================

class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self.alert_data_list = []
    self.cards = []

    self.scrollbar_alpha = 0.0
    self.last_scroll_time = 0.0

    # Scroll indicator asset
    self.scrollbar_img = gui_app.texture(
      "assets/icons_mici/settings/vertical_scroll_indicator.png",
      36, 220
    )

    # Scroller
    self.scroller = Scroller([], horizontal=False, spacing=32, pad_start=48, pad_end=48, snap_items=False)

    # Title
    self.title_label = UnifiedLabel("Alerts", 86, FontWeight.DISPLAY, rl.WHITE,
                                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self.build_initial()

  # ------------------------------------------------------------
  def build_initial(self):
    # Update card (always first)
    upd = AlertData("UpdateAvailable", "", -1, False)
    self.alert_data_list.append(upd)
    card = GlassAlertCard(upd)
    self.cards.append(card)
    self.scroller.add_widget(card)

    # Regular alerts
    for key, cfg in sorted(OFFROAD_ALERTS.items(), key=lambda x: x[1]["severity"], reverse=True):
      data = AlertData(key, "", cfg["severity"], False)
      self.alert_data_list.append(data)
      card = GlassAlertCard(data)
      self.cards.append(card)
      self.scroller.add_widget(card)

  # ------------------------------------------------------------
  def active_count(self):
    return sum(a.visible for a in self.alert_data_list)

  # ------------------------------------------------------------
  def refresh(self):
    active = 0

    # UpdateAvailable
    upd = self.alert_data_list[0]
    if self.params.get_bool("UpdateAvailable"):
      desc = self.params.get("UpdaterNewDescription") or ""
      version = ""
      date = ""

      if desc:
        parts = desc.split(" / ")
        if len(parts) > 3:
          version = parts[0]
          date = parts[3]

      upd.text = f"update available.\nhoofpilot {version}, {date}".strip()
      upd.visible = True
      active += 1
    else:
      upd.visible = False
      upd.text = ""

    # Normal alerts
    for data in self.alert_data_list[1:]:
      entry = self.params.get(data.key)
      if entry:
        try:
          text = entry.get("text", "").replace("%1", entry.get("extra", ""))
        except:
          text = ""
        data.text = text
        data.visible = bool(text)
        if data.visible:
          active += 1
      else:
        data.visible = False
        data.text = ""

    # Update cards
    for card in self.cards:
      card.update_content()

    return active

  # ------------------------------------------------------------
  def show_event(self):
    self.scroller.show_event()
    self.refresh()

  # ------------------------------------------------------------
  def update_state(self):
    # Scrollbar fading
    if self.scroller.scrolling():
      self.last_scroll_time = time.monotonic()
      self.scrollbar_alpha += (1.0 - self.scrollbar_alpha) * rl.get_frame_time() * FADE_SPEED
    else:
      dt = time.monotonic() - self.last_scroll_time
      if dt > FADEOUT_DELAY:
        self.scrollbar_alpha += (0.0 - self.scrollbar_alpha) * rl.get_frame_time() * FADE_SPEED

  # ------------------------------------------------------------
  def _render(self, rect):
    # Title
    self.title_label.render(rl.Rectangle(rect.x + 64, rect.y + 32, 800, 150))

    # Alerts
    if self.active_count() == 0:
      return

    # Lay out cards
    y = rect.y + 160
    for card in self.cards:
      if card.alert_data.visible:
        card.set_rect(rl.Rectangle(
          rect.x + (rect.width - card.WIDTH) / 2,
          y,
          card.WIDTH,
          card.rect.height
        ))
        y += card.rect.height + 24

    # Render scroller
    self.scroller.render(rect)

    # Scrollbar (fade in/out)
    if self.scrollbar_alpha > 0.01:
      alpha = int(255 * self.scrollbar_alpha)
      sb_y = rect.y + 160
      sb_x = rect.x + rect.width - 64
      rl.draw_texture(self.scrollbar_img, int(sb_x), int(sb_y), rl.Color(255, 255, 255, alpha))
