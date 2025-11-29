import pyray as rl
import re
import time
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


class AlertItem(Widget):
  ALERT_WIDTH = 520
  ALERT_HEIGHT_SMALL = 212
  ALERT_HEIGHT_MED = 240
  ALERT_HEIGHT_BIG = 324
  ALERT_PADDING = 28
  ICON_SIZE = 64
  ICON_MARGIN = 12
  TEXT_COLOR = rl.Color(255, 255, 255, int(255 * 0.9))
  TITLE_BODY_SPACING = 24

  def __init__(self, alert_data: AlertData):
    super().__init__()
    self.alert_data = alert_data

    self._bg_small = gui_app.texture("icons_mici/offroad_alerts/small_alert.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_SMALL)
    self._bg_small_pressed = gui_app.texture("icons_mici/offroad_alerts/small_alert_pressed.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_SMALL)
    self._bg_medium = gui_app.texture("icons_mici/offroad_alerts/medium_alert.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_MED)
    self._bg_medium_pressed = gui_app.texture("icons_mici/offroad_alerts/medium_alert_pressed.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_MED)
    self._bg_big = gui_app.texture("icons_mici/offroad_alerts/big_alert.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_BIG)
    self._bg_big_pressed = gui_app.texture("icons_mici/offroad_alerts/big_alert_pressed.png", self.ALERT_WIDTH, self.ALERT_HEIGHT_BIG)

    self._icon_orange = gui_app.texture("icons_mici/offroad_alerts/orange_warning.png", self.ICON_SIZE, self.ICON_SIZE)
    self._icon_red = gui_app.texture("icons_mici/offroad_alerts/red_warning.png", self.ICON_SIZE, self.ICON_SIZE)
    self._icon_green = gui_app.texture("icons_mici/offroad_alerts/green_wheel.png", self.ICON_SIZE, self.ICON_SIZE)

    self._title_label = UnifiedLabel(
      text="", font_size=32, font_weight=FontWeight.SEMI_BOLD, text_color=self.TEXT_COLOR,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP, line_height=0.95,
    )

    self._body_label = UnifiedLabel(
      text="", font_size=28, font_weight=FontWeight.ROMAN, text_color=self.TEXT_COLOR,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_BOTTOM, line_height=0.95,
    )

    self._title_text = ""
    self._body_text = ""
    self._alert_size = AlertSize.SMALL

    self._update_content()

  def _split_text(self, text: str) -> tuple[str, str]:
    match = re.search(r'[.!?](?:\s+|$)', text)
    if match:
      title = text[:match.start()].strip()
      body = text[match.end():].strip()
      return title, body
    return "", text

  def _update_content(self):
    if not self.alert_data.visible or not self.alert_data.text:
      self.set_visible(False)
      return

    self.set_visible(True)
    self._title_text, self._body_text = self._split_text(self.alert_data.text)

    title_width = self.ALERT_WIDTH - (self.ALERT_PADDING * 2) - self.ICON_SIZE - self.ICON_MARGIN
    body_width = self.ALERT_WIDTH - (self.ALERT_PADDING * 2)

    self._title_label.set_text(self._title_text)
    self._body_label.set_text(self._body_text)

    title_height = self._title_label.get_content_height(title_width) if self._title_text else 0
    body_height = self._body_label.get_content_height(body_width) if self._body_text else 0
    spacing = self.TITLE_BODY_SPACING if (self._title_text and self._body_text) else 0
    total_text_height = title_height + spacing + body_height

    min_height_with_padding = total_text_height + (self.ALERT_PADDING * 2)
    if min_height_with_padding > self.ALERT_HEIGHT_MED:
      self._alert_size = AlertSize.BIG
      height = self.ALERT_HEIGHT_BIG
    elif min_height_with_padding > self.ALERT_HEIGHT_SMALL:
      self._alert_size = AlertSize.MEDIUM
      height = self.ALERT_HEIGHT_MED
    else:
      self._alert_size = AlertSize.SMALL
      height = self.ALERT_HEIGHT_SMALL

    self.set_rect(rl.Rectangle(0, 0, self.ALERT_WIDTH, height))

  def update_alert_data(self, alert_data: AlertData):
    self.alert_data = alert_data
    self._update_content()

  def _render(self, _):
    if not self.alert_data.visible or not self.alert_data.text:
      return

    if self._alert_size == AlertSize.BIG:
      bg_texture = self._bg_big_pressed if self.is_pressed else self._bg_big
    elif self._alert_size == AlertSize.MEDIUM:
      bg_texture = self._bg_medium_pressed if self.is_pressed else self._bg_medium
    else:
      bg_texture = self._bg_small_pressed if self.is_pressed else self._bg_small

    rl.draw_texture(bg_texture, int(self._rect.x), int(self._rect.y), rl.WHITE)

    title_width = self.ALERT_WIDTH - (self.ALERT_PADDING * 2) - self.ICON_SIZE - self.ICON_MARGIN
    body_width = self.ALERT_WIDTH - (self.ALERT_PADDING * 2)
    text_x = self._rect.x + self.ALERT_PADDING
    text_y = self._rect.y + self.ALERT_PADDING

    if self._title_text:
      title_rect = rl.Rectangle(
        text_x,
        text_y,
        title_width,
        self._title_label.get_content_height(title_width),
      )
      self._title_label.render(title_rect)
      text_y += title_rect.height + self.TITLE_BODY_SPACING

    if self._body_text:
      body_rect = rl.Rectangle(
        text_x,
        text_y,
        body_width,
        self._rect.height - text_y + self._rect.y - self.ALERT_PADDING,
      )
      self._body_label.render(body_rect)

    if self.alert_data.severity == -1:
      icon_texture = self._icon_green
    elif self.alert_data.severity > 0:
      icon_texture = self._icon_red
    else:
      icon_texture = self._icon_orange
    icon_x = self._rect.x + self.ALERT_WIDTH - self.ALERT_PADDING - self.ICON_SIZE
    icon_y = self._rect.y + self.ALERT_PADDING
    rl.draw_texture(icon_texture, int(icon_x), int(icon_y), rl.WHITE)


class OffroadAlertsLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self.sorted_alerts: list[AlertData] = []
    self.alert_items: list[AlertItem] = []
    self._last_refresh = 0.0

    self._scroller = Scroller([], horizontal=False, spacing=12, pad_start=0, pad_end=0, snap_items=False)
    self._empty_label = UnifiedLabel(
      tr("no alerts"), 65, FontWeight.DISPLAY, rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE,
    )

    self._build_alerts()

  def active_alerts(self) -> int:
    return sum(alert.visible for alert in self.sorted_alerts)

  def scrolling(self):
    return self._scroller.scroll_panel.is_touch_valid()

  def _build_alerts(self):
    self.sorted_alerts = []
    self.alert_items = []

    update_alert_data = AlertData(key="UpdateAvailable", text="", severity=-1)
    self.sorted_alerts.append(update_alert_data)
    update_alert_item = AlertItem(update_alert_data)
    self.alert_items.append(update_alert_item)
    self._scroller.add_widget(update_alert_item)

    for key, config in sorted(OFFROAD_ALERTS.items(), key=lambda x: x[1].get("severity", 0), reverse=True):
      severity = config.get("severity", 0)
      alert_data = AlertData(key=key, text="", severity=severity)
      self.sorted_alerts.append(alert_data)

      alert_item = AlertItem(alert_data)
      self.alert_items.append(alert_item)
      self._scroller.add_widget(alert_item)

  def refresh(self) -> int:
    active_count = 0
    update_available = self.params.get_bool("UpdateAvailable")
    update_alert_data = next((a for a in self.sorted_alerts if a.key == "UpdateAvailable"), None)

    if update_alert_data:
      if update_available:
        update_alert_data.text = "update available. go to comma.ai/blog to read the release notes."
        new_desc = self.params.get("UpdaterNewDescription") or ""
        if new_desc:
          parts = new_desc.split(" / ")
          if len(parts) > 3:
            version, date = parts[0], parts[3]
            update_alert_data.text = f"update available\n hoofpilot {version}, {date}."
        update_alert_data.visible = True
        active_count += 1
      else:
        update_alert_data.text = ""
        update_alert_data.visible = False

    for alert_data in self.sorted_alerts:
      if alert_data.key == "UpdateAvailable":
        continue

      text = ""
      alert_json = self.params.get(alert_data.key)

      if alert_json:
        text = alert_json.get("text", "").replace("%1", alert_json.get("extra", ""))

      alert_data.text = text
      alert_data.visible = bool(text)

      if alert_data.visible:
        active_count += 1

    for alert_item in self.alert_items:
      alert_item.update_alert_data(alert_item.alert_data)

    return active_count

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
    if self.active_alerts() == 0:
      self._empty_label.render(rect)
    else:
      self._scroller.render(rect)
