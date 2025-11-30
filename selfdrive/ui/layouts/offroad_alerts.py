import json
import time
import pyray as rl
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
class Entry:
  key: str
  kind: EntryKind
  title: str
  line2: str
  line3: str
  severity: int  # -1 update/ok, 0 warn, 1 critical


class EntryCard(Widget):
  def __init__(self, entry: Entry):
    super().__init__()
    self.entry = entry
    self._title_label = UnifiedLabel(
      "",
      60,
      FontWeight.SEMI_BOLD,
      rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
    )
    self._line_label = UnifiedLabel(
      "",
      48,
      FontWeight.ROMAN,
      rl.Color(230, 230, 230, 255),
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      line_height=1.0,
    )
    self._update_state()

  def set_entry(self, entry: Entry):
    self.entry = entry
    self._update_state()

  def _update_state(self):
    self._title_label.set_text(self.entry.title)
    body = "\n".join([s for s in [self.entry.line2, self.entry.line3] if s])
    self._line_label.set_text(body)

  def _render(self, rect: rl.Rectangle):
    pad = 40
    accent = (
      rl.Color(120, 200, 120, 255)
      if self.entry.severity <= -1
      else rl.Color(255, 180, 64, 255)
      if self.entry.severity == 0
      else rl.Color(230, 80, 80, 255)
    )
    bg = rl.Color(20, 20, 20, 245)
    rl.draw_rectangle_rounded(rect, 0.22, 12, bg)
    rl.draw_rectangle_rounded_lines_ex(rect, 0.22, 12, 4, accent)

    text_w = rect.width - pad * 2
    text_x = rect.x + pad
    text_y = rect.y + pad
    self._title_label.render(rl.Rectangle(text_x, text_y, text_w, 200))
    text_y += self._title_label.get_content_height(text_w) + 12
    self._line_label.render(
      rl.Rectangle(
        text_x,
        text_y,
        text_w,
        rect.height - (text_y - rect.y) - pad,
      )
    )


class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self._cards: List[EntryCard] = []
    self._scroller = Scroller(
      [], horizontal=False, spacing=28, pad_start=32, pad_end=32, snap_items=False
    )
    self._last_refresh = 0.0
    self._empty_label = UnifiedLabel(
      tr("no alerts"),
      96,
      FontWeight.DISPLAY,
      rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE,
    )

  def active_entries(self) -> int:
    return len(self._cards)

  def _parse_update_entry(self) -> Entry | None:
    if not self.params.get_bool("UpdateAvailable"):
      return None

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
    return Entry("__update__", EntryKind.UPDATE, title, line2, line3, -1)

  def _parse_alert_entry(self, key: str, config: dict) -> Entry | None:
    alert_json = self.params.get(key)
    if not alert_json:
      return None
    text = ""
    try:
      if isinstance(alert_json, bytes):
        alert_json = alert_json.decode("utf-8", "replace")
      if isinstance(alert_json, str):
        alert_json = json.loads(alert_json)
      if isinstance(alert_json, dict):
        text = (alert_json.get("text", "") or "").replace(
          "%1", alert_json.get("extra", "")
        )
      else:
        text = str(alert_json)
    except Exception:
      text = ""
    if not text:
      return None

    title, body = self._split_text(text)
    sev = config.get("severity", 0)
    return Entry(key, EntryKind.ALERT, title or "Alert", body, "", sev)

  @staticmethod
  def _split_text(text: str) -> tuple[str, str]:
    # Split on first sentence end
    import re

    match = re.search(r"[.!?](?:\s+|$)", text)
    if match:
      return text[: match.start()].strip(), text[match.end() :].strip()
    return text, ""

  def _rebuild(self):
    # Recreate scroller fresh (original behavior), but dedupe entries by key
    self._scroller = Scroller(
      [], horizontal=False, spacing=28, pad_start=32, pad_end=32, snap_items=False
    )
    self._cards = []

    entries: List[Entry] = []

    # Single update entry
    upd = self._parse_update_entry()
    if upd:
      entries.append(upd)

    # Unique alerts keyed by alert key, sorted by severity (critical first)
    for key, config in sorted(
      OFFROAD_ALERTS.items(), key=lambda x: x[1].get("severity", 0), reverse=True
    ):
      if key == "UpdateAvailable":
        continue
      e = self._parse_alert_entry(key, config)
      if e is not None:
        entries.append(e)

    # Deduplicate by key to avoid repeated "update available" or duplicate alerts
    by_key: dict[str, Entry] = {}
    for e in entries:
      by_key[e.key] = e
    entries = list(by_key.values())

    # Build cards
    for e in entries:
      card = EntryCard(e)
      self._cards.append(card)
      self._scroller.add_widget(card)

  def refresh(self) -> int:
    self._rebuild()
    return len(self._cards)

  def show_event(self):
    self._scroller.show_event()
    self._last_refresh = time.monotonic()
    self.refresh()

  def _update_state(self):
    if time.monotonic() - self._last_refresh >= REFRESH_INTERVAL:
      self.refresh()
      self._last_refresh = time.monotonic()

  def _render(self, rect: rl.Rectangle):
    if self.active_entries() == 0:
      self._empty_label.render(rect)
      return

    # Lay out cards with consistent width and spacing
    spacing = getattr(self._scroller, "_spacing", 28)
    width = min(rect.width * 0.9, 1800)
    x = rect.x + (rect.width - width) / 2
    y = rect.y + 32

    for card in self._cards:
      body_w = width - 80
      height = (
        card._title_label.get_content_height(body_w)
        + card._line_label.get_content_height(body_w)
        + 200
      )
      card.set_rect(rl.Rectangle(x, y, width, max(300, height)))
      y += card.rect.height + spacing

    self._scroller.render(rect)
