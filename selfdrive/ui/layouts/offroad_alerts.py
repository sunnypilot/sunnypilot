import pyray as rl
import time
import re
import json
from dataclasses import dataclass
from enum import IntEnum

from openpilot.common.params import Params
from openpilot.selfdrive.selfdrived.alertmanager import OFFROAD_ALERTS
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr


REFRESH_INTERVAL = 5.0


class AlertSeverity(IntEnum):
  UPDATE = -1
  WARNING = 0
  CRITICAL = 1


@dataclass
class AlertEntry:
  key: str
  text: str
  severity: int
  visible: bool = False


# -------------------------------
# Glass Card Component
# -------------------------------
class GlassAlertCard(Widget):
  CARD_WIDTH = 1480
  MIN_HEIGHT = 180
  PADDING = 48
  ICON_SIZE = 78
  ICON_MARGIN = 28

  # subtle gradient glass tint
  GLASS_TINT_TOP = rl.Color(255, 255, 255, 36)
  GLASS_TINT_BOTTOM = rl.Color(255, 255, 255, 16)

  TEXT_COLOR = rl.Color(255, 255, 255, 230)

  def __init__(self, entry: AlertEntry):
    super().__init__()
    self.entry = entry

    # severity glow effects
    self._glow_green = rl.Color(100, 255, 180, 255)
    self._glow_orange = rl.Color(255, 200, 80, 255)
    self._glow_red = rl.Color(255, 90, 90, 255)

    # icons
    self.icon_green = gui_app.texture("icons_mici/offroad_alerts/icon_green.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_orange = gui_app.texture("icons_mici/offroad_alerts/icon_orange.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_red = gui_app.texture("icons_mici/offroad_alerts/icon_red.png", self.ICON_SIZE, self.ICON_SIZE)

    # typography
    self.title_label = UnifiedLabel("", 52, FontWeight.BOLD, self.TEXT_COLOR,
                                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self.body_label = UnifiedLabel("", 40, FontWeight.ROMAN, self.TEXT_COLOR,
                                   alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT, line_height=1.06)

    # update content & sizing
    self._update_content()

  def _split_text(self, text: str):
    match = re.search(r'[.!?](?:\s+|$)', text)
    if match:
      return text[:match.start()].strip(), text[match.end():].strip()
    return "", text

  def _update_content(self):
    if not self.entry.visible or not self.entry.text:
      self.set_visible(False)
      return

    self.set_visible(True)

    title, body = self._split_text(self.entry.text)
    self.title_label.set_text(title)
    self.body_label.set_text(body)

    text_width = self.CARD_WIDTH - (self.PADDING * 2) - self.ICON_SIZE - self.ICON_MARGIN
    title_height = self.title_label.get_content_height(text_width)
    body_height = self.body_label.get_content_height(text_width)

    total_height = max(self.MIN_HEIGHT, title_height + body_height + self.PADDING * 2 + 20)

    self.set_rect(rl.Rectangle(0, 0, self.CARD_WIDTH, total_height))

  def update_entry(self, entry: AlertEntry):
    self.entry = entry
    self._update_content()

  def _pick_glow(self):
    if self.entry.severity == -1:
      return self._glow_green
    if self.entry.severity == 1:
      return self._glow_red
    return self._glow_orange

  def _pick_icon(self):
    if self.entry.severity == -1:
      return self.icon_green
    if self.entry.severity == 1:
      return self.icon_red
    return self.icon_orange

  def _render(self, _):
    if not self.entry.visible:
      return

    # --- draw glow ---
    glow_color = self._pick_glow()
    glow_rect = rl.Rectangle(self._rect.x - 6, self._rect.y - 6,
                             self._rect.width + 12, self._rect.height + 12)
    rl.draw_rectangle_rounded(glow_rect, 0.12, 16, rl.Color(glow_color.r, glow_color.g, glow_color.b, 90))

    # --- draw glass card ---
    rl.draw_rectangle_rounded(self._rect, 0.12, 16, rl.Color(255,255,255,25))
    rl.draw_rectangle_gradient_v(
      int(self._rect.x), int(self._rect.y),
      int(self._rect.width), int(self._rect.height),
      self.GLASS_TINT_TOP,
      self.GLASS_TINT_BOTTOM
    )

    text_x = self._rect.x + self.PADDING
    text_y = self._rect.y + self.PADDING
    text_w = self._rect.width - (self.PADDING * 2) - self.ICON_SIZE - self.ICON_MARGIN

    # title
    if self.title_label.text:
      h = self.title_label.get_content_height(text_w)
      self.title_label.render(rl.Rectangle(text_x, text_y, text_w, h))
      text_y += h + 16

    # body
    if self.body_label.text:
      self.body_label.render(rl.Rectangle(text_x, text_y, text_w, self._rect.height - text_y))

    # severity icon top-right
    icon = self._pick_icon()
    rl.draw_texture(icon,
      int(self._rect.x + self._rect.width - self.PADDING - self.ICON_SIZE),
      int(self._rect.y + self.PADDING),
      rl.WHITE
    )


# -------------------------------------------------------
# Main Offroad Alerts Layout (Tizi Glass Version)
# -------------------------------------------------------
class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()

    self.entries: list[AlertEntry] = []
    self.cards: list[GlassAlertCard] = []

    self.scroller = Scroller([], horizontal=False, spacing=32, pad_start=16, pad_end=16)
    self.last_refresh = 0

    self.empty_label = UnifiedLabel(tr("no alerts"), 72, FontWeight.DISPLAY, rl.WHITE,
                                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                    alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)

    self._build_structure()

  def _build_structure(self):
    # Update alert (special entry)
    upd = AlertEntry("UpdateAvailable", "", -1, False)
    self.entries.append(upd)
    card = GlassAlertCard(upd)
    self.cards.append(card)
    self.scroller.add_widget(card)

    # normal alerts
    for key, cfg in sorted(OFFROAD_ALERTS.items(), key=lambda x: x[1]["severity"], reverse=True):
      if key == "UpdateAvailable":
        continue
      entry = AlertEntry(key, "", cfg.get("severity", 0), False)
      self.entries.append(entry)
      card = GlassAlertCard(entry)
      self.cards.append(card)
      self.scroller.add_widget(card)

  def refresh(self) -> int:
    active = 0

    # update alert
    upd = next(e for e in self.entries if e.key == "UpdateAvailable")
    if self.params.get_bool("UpdateAvailable"):
      desc = self.params.get("UpdaterNewDescription") or ""
      if desc:
        parts = desc.split(" / ")
        if len(parts) >= 4:
          version, date = parts[0], parts[3]
          upd.text = f"Update available! Hoofpilot {version} — {date}."
        else:
          upd.text = "Update available."
      else:
        upd.text = "Update available."
      upd.visible = True
      active += 1
    else:
      upd.visible = False
      upd.text = ""

    # normal alerts
    for entry in self.entries:
      if entry.key == "UpdateAvailable":
        continue

      value = self.params.get(entry.key)
      if not value:
        entry.visible = False
        entry.text = ""
        continue

      try:
        if isinstance(value, bytes):
          value = value.decode("utf-8", "replace")
        alert_json = json.loads(value)
        entry.text = (alert_json.get("text", "") or "").replace("%1", alert_json.get("extra", ""))
      except:
        entry.text = ""

      entry.visible = bool(entry.text)
      if entry.visible:
        active += 1

    for card in self.cards:
      card.update_entry(card.entry)

    return active

  def show_event(self):
    self.scroller.show_event()
    self.last_refresh = time.monotonic()
    self.refresh()

  def _update_state(self):
    if time.monotonic() - self.last_refresh >= REFRESH_INTERVAL:
      self.refresh()
      self.last_refresh = time.monotonic()

  def _render(self, rect: rl.Rectangle):
    visible_count = sum(e.visible for e in self.entries)

    if visible_count == 0:
      self.empty_label.render(rect)
      return

    # center cards
    x = rect.x + (rect.width - GlassAlertCard.CARD_WIDTH) / 2

    y = rect.y + 48
    for card in self.cards:
      if not card.entry.visible:
        continue

      card.set_position(x, y)
      y += card.rect.height + 32

    self.scroller.render(rect)