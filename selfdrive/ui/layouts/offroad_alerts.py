import pyray as rl
import re
import time
from dataclasses import dataclass
from enum import IntEnum

from openpilot.common.params import Params
from openpilot.selfdrive.selfdrived.alertmanager import OFFROAD_ALERTS
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.lib.animation import smooth_towards
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr

REFRESH_INTERVAL = 5.0


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


class GlassAlertCard(Widget):
  WIDTH = 1720
  MIN_HEIGHT = 240
  PADDING = 48

  ICON_SIZE = 96
  ICON_MARGIN = 36

  PRESS_SCALE = 0.96   # squish scale target
  PRESS_SPEED = 10.0   # smoothing speed

  def __init__(self, alert_data: AlertData):
    super().__init__()
    self.alert_data = alert_data

    # severity icons (relative to selfdrive/assets/)
    self.icon_green = gui_app.texture("icons_mici/offroad_alerts/green_wheel.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_orange = gui_app.texture("icons_mici/offroad_alerts/orange_warning.png", self.ICON_SIZE, self.ICON_SIZE)
    self.icon_red = gui_app.texture("icons_mici/offroad_alerts/red_warning.png", self.ICON_SIZE, self.ICON_SIZE)

    self.title_label = UnifiedLabel(
      "",
      58,
      FontWeight.SEMI_BOLD,
      rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      line_height=1.0,
    )
    self.body_label = UnifiedLabel(
      "",
      46,
      FontWeight.ROMAN,
      rl.Color(240, 240, 240, 255),
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      line_height=1.0,
    )

    self.scale_anim = 1.0
    self.update_content()

  # -------- text helpers --------
  def _split_text(self, text: str) -> tuple[str, str]:
    match = re.search(r'[.!?](?:\s+|$)', text)
    if match:
      return text[:match.start()].strip(), text[match.end():].strip()
    return "", text

  # -------- content / layout --------
  def update_content(self):
    if not self.alert_data.visible or not self.alert_data.text:
      self.set_visible(False)
      return

    self.set_visible(True)

    title, body = self._split_text(self.alert_data.text)
    self.title_label.set_text(title)
    self.body_label.set_text(body)

    text_width = self.WIDTH - self.PADDING * 2 - self.ICON_SIZE - self.ICON_MARGIN
    title_h = self.title_label.get_content_height(text_width)
    body_h = self.body_label.get_content_height(text_width)
    height = max(self.MIN_HEIGHT, title_h + body_h + self.PADDING * 2)

    self.set_rect(rl.Rectangle(0, 0, self.WIDTH, height))

  # -------- rendering --------
  def _render(self, _):
    if not self.alert_data.visible:
      return

    # squish animation, anchored to TOP so it doesn’t move down when pressed
    target_scale = self.PRESS_SCALE if self.is_pressed else 1.0
    self.scale_anim = smooth_towards(self.scale_anim, target_scale, self.PRESS_SPEED, rl.get_frame_time())

    rect = self._rect

    # anchor scaling at top-center so the top edge stays fixed
    cx = rect.x + rect.width / 2
    anchor_y = rect.y

    rl.rl_push_matrix()
    rl.rl_translatef(cx, anchor_y, 0)
    rl.rl_scalef(self.scale_anim, self.scale_anim, 1)
    rl.rl_translatef(-cx, -anchor_y, 0)

    # glass + glow
    if self.alert_data.severity == -1:
      glow = rl.Color(80, 200, 120, 255)
    elif self.alert_data.severity == 0:
      glow = rl.Color(240, 170, 70, 255)
    else:
      glow = rl.Color(220, 70, 70, 255)

    # Opaque but dark background so white text remains legible
    bg = rl.Color(24, 24, 24, 255)
    stroke = rl.Color(255, 255, 255, 255)

    rl.draw_rectangle_rounded(rect, 0.14, 12, glow)

    inner = rl.Rectangle(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
    rl.draw_rectangle_rounded(inner, 0.14, 12, bg)
    rl.draw_rectangle_rounded_lines(inner, 0.14, 12, stroke)

    # text
    text_x = rect.x + self.PADDING
    text_y = rect.y + self.PADDING
    text_w = rect.width - self.PADDING * 2 - self.ICON_SIZE - self.ICON_MARGIN

    self.title_label.render(rl.Rectangle(text_x, text_y, text_w, 200))
    text_y += self.title_label.get_content_height(text_w) + 16
    self.body_label.render(rl.Rectangle(text_x, text_y, text_w, rect.height - text_y))

    # severity icon
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


class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self.alert_data_list: list[AlertData] = []
    self.cards: list[GlassAlertCard] = []
    self._last_refresh = 0.0

    self.title_label = UnifiedLabel(
      tr("Alerts"),
      86,
      FontWeight.DISPLAY,
      rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
    )

    self._build_initial()

  # -------- build initial card list --------
  def _build_initial(self):
    # update card
    upd = AlertData("UpdateAvailable", "", -1, False)
    self.alert_data_list.append(upd)
    upd_card = GlassAlertCard(upd)
    self.cards.append(upd_card)

    # other alerts sorted by severity
    for key, cfg in sorted(OFFROAD_ALERTS.items(), key=lambda x: x[1].get("severity", 0), reverse=True):
      sev = cfg.get("severity", 0)
      data = AlertData(key, "", sev, False)
      self.alert_data_list.append(data)
      card = GlassAlertCard(data)
      self.cards.append(card)

  def _active_count(self) -> int:
    return sum(1 for a in self.alert_data_list if a.visible)

  # -------- refresh from Params --------
  def refresh(self) -> int:
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

    # regular alerts
    for data in self.alert_data_list[1:]:
      alert_json = self.params.get(data.key)
      text = ""
      if alert_json:
        try:
          # alertmanager stores dict-like here
          text = alert_json.get("text", "").replace("%1", alert_json.get("extra", ""))
        except Exception:
          text = ""
      data.text = text
      data.visible = bool(text)
      if data.visible:
        active += 1

    for card in self.cards:
      card.update_content()

    return active

  def show_event(self):
    self.refresh()
    self._last_refresh = time.monotonic()

  # -------- state updates (periodic refresh only) --------
  def _update_state(self):
    now = time.monotonic()
    if now - self._last_refresh >= REFRESH_INTERVAL:
      self.refresh()
      self._last_refresh = now

  # -------- rendering --------
  def _render(self, rect: rl.Rectangle):
    # title
    title_rect = rl.Rectangle(rect.x + 64, rect.y + 32, rect.width - 128, 120)
    self.title_label.render(title_rect)

    if self._active_count() == 0:
      # optional: render "no alerts" label here if you want
      return

    # layout cards vertically and render them directly (no scroller, no movement on tap)
    y = rect.y + 160
    center_x = rect.x + rect.width / 2

    for card in self.cards:
      if not card.alert_data.visible:
        continue

      card_x = center_x - card.WIDTH / 2
      card.set_rect(rl.Rectangle(
        card_x,
        y,
        card.WIDTH,
        card.rect.height,
      ))
      card.render(card.rect)
      y += card.rect.height + 24
