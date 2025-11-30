import json
import pyray as rl
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import List

from openpilot.common.params import Params
from openpilot.selfdrive.selfdrived.alertmanager import OFFROAD_ALERTS
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr

REFRESH_INTERVAL = 5.0


class EntryKind(IntEnum):
  UPDATE = 0
  ALERT = 1


@dataclass
class EntryData:
  kind: EntryKind
  title: str
  line2: str
  line3: str
  severity: int  # -1 update/ok, 0 warn, 1 critical


class EntryCard(Widget):
  def __init__(self, data: EntryData):
    super().__init__()
    self.data = data
    self._title_label = UnifiedLabel("", 64, FontWeight.SEMI_BOLD, rl.WHITE,
                                     alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._line_label = UnifiedLabel("", 48, FontWeight.ROMAN, rl.Color(230, 230, 230, 255),
                                    alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                                    alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP, line_height=1.0)
    self._update_state()

  def set_entry(self, data: EntryData):
    self.data = data
    self._update_state()

  def _update_state(self):
    self._title_label.set_text(self.data.title)
    combined = "\n".join([s for s in [self.data.line2, self.data.line3] if s])
    self._line_label.set_text(combined)

  def _render(self, rect: rl.Rectangle):
    pad = 32
    corner = 18
    bg = rl.Color(28, 28, 28, 245)
    accent = rl.Color(120, 200, 120, 255) if self.data.severity <= -1 else rl.Color(255, 180, 64, 255) if self.data.severity == 0 else rl.Color(230, 80, 80, 255)
    rl.draw_rectangle_rounded(rect, 0.2, 12, bg)
    rl.draw_rectangle_rounded_lines_ex(rect, 0.2, 12, 4, accent)

    text_x = rect.x + pad
    text_y = rect.y + pad
    self._title_label.render(rl.Rectangle(text_x, text_y, rect.width - pad * 2, 200))
    text_y += self._title_label.get_content_height(rect.width - pad * 2) + 12
    self._line_label.render(rl.Rectangle(text_x, text_y, rect.width - pad * 2, rect.height - text_y + rect.y - pad))


class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self._cards: List[EntryCard] = []
    self._scroller = Scroller([], horizontal=False, spacing=24, pad_start=32, pad_end=32, snap_items=False)
    self._last_refresh = 0.0
    self._empty_label = UnifiedLabel(tr("no alerts"), 96, FontWeight.DISPLAY, rl.WHITE,
                                     alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                     alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)

  def active_entries(self) -> int:
    return len(self._cards)

  def _build_entries(self):
    entries: List[EntryData] = []
    seen: set[tuple[int, str, str, str]] = set()

    # Update card
    if self.params.get_bool("UpdateAvailable"):
      desc = self.params.get("UpdaterNewDescription") or ""
      if isinstance(desc, bytes):
        desc = desc.decode("utf-8", "replace")
      version = branch = commit = date = ""
      if desc:
        parts = [p.strip() for p in desc.split(" / ")]
        if len(parts) > 0:
          version = parts[0]
        if len(parts) > 1:
          branch = parts[1]
        if len(parts) > 2:
          commit = parts[2]
        if len(parts) > 3:
          date = parts[3]
      title = "update available"
      line2 = f"hoofpilot {version}".strip()
      line3_parts = [p for p in [branch, commit, date] if p]
      line3 = " / ".join(line3_parts)
      entry = EntryData(EntryKind.UPDATE, title, line2, line3, -1)
      key = (entry.kind, entry.title, entry.line2, entry.line3)
      if key not in seen:
        seen.add(key)
        entries.append(entry)

    # Regular alerts
    for key, config in sorted(OFFROAD_ALERTS.items(), key=lambda x: x[1].get("severity", 0), reverse=True):
      if key == "UpdateAvailable":
        continue  # handled by the dedicated update card above
      alert_json = self.params.get(key)
      if not alert_json:
        continue
      try:
        if isinstance(alert_json, bytes):
          alert_json = alert_json.decode("utf-8", "replace")
        if isinstance(alert_json, str):
          alert_json = json.loads(alert_json)
        text = (alert_json.get("text", "") or "").replace("%1", alert_json.get("extra", ""))
      except Exception:
        text = ""
      if not text:
        continue

      title, body = self._split_text(text)
      sev = config.get("severity", 0)
      entry = EntryData(EntryKind.ALERT, title or "Alert", body, "", sev)
      key = (entry.kind, entry.title, entry.line2, entry.line3)
      if key not in seen:
        seen.add(key)
        entries.append(entry)

    # Build cards
    # Clear state before repopulating
    self._cards = []
    try:
      self._scroller.clear_widgets()
    except Exception:
      self._scroller._widgets = []

    for e in entries:
      card = EntryCard(e)
      self._cards.append(card)
      self._scroller.add_widget(card)

  @staticmethod
  def _split_text(text: str) -> tuple[str, str]:
    match = re.search(r'[.!?](?:\s+|$)', text)
    if match:
      return text[:match.start()].strip(), text[match.end():].strip()
    return "", text

  def refresh(self) -> int:
    self._build_entries()
    return len(self._cards)

  def show_event(self):
    self._scroller.show_event()
    self._last_refresh = time.monotonic()
    self.refresh()

  def _update_state(self):
    current_time = time.monotonic()
    if current_time - self._last_refresh >= REFRESH_INTERVAL:
      self.refresh()
      self._last_refresh = current_time

  def _render(self, rect: rl.Rectangle):
    if self.active_entries() == 0:
      self._empty_label.render(rect)
      return

    # Set card sizes based on viewport
    width = min(rect.width * 0.92, 1800)
    x = rect.x + (rect.width - width) / 2
    y = rect.y
    spacing = getattr(self._scroller, "_spacing", 24)
    for card in self._cards:
      height = card._title_label.get_content_height(width - 128) + card._line_label.get_content_height(width - 128) + 160
      card.set_rect(rl.Rectangle(x, y, width, max(260, height)))
      y += card.rect.height + spacing

    # Render scroller
    self._scroller.render(rl.Rectangle(rect.x, rect.y, rect.width, rect.height))
