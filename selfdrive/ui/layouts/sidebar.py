import math
import pyray as rl
from dataclasses import dataclass

from cereal import log
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget

ThermalStatus = log.DeviceState.ThermalStatus

SIDEBAR_WIDTH = 300
CARD_RADIUS = 22
CARD_PADDING = 28
CARD_SPACING = 26
TEXT_SIZE_TITLE = 38
TEXT_SIZE_VALUE = 52


# ----------------------------
#  Color Palettes (Minimal)
# ----------------------------

COLOR_GREY_BG = rl.Color(30, 30, 30, 200)
COLOR_CARD_BG = rl.Color(255, 255, 255, 28)
COLOR_WHITE = rl.Color(255, 255, 255, 255)

THERMAL_COLORS = {
  ThermalStatus.green: rl.Color(120, 200, 150, 255),
  ThermalStatus.yellow: rl.Color(230, 210, 140, 255),
  ThermalStatus.red: rl.Color(250, 140, 140, 255),
  ThermalStatus.danger: rl.Color(255, 90, 90, 255),
}

ENGAGED_BORDER = rl.Color(110, 200, 140, 255)
DISENGAGED_BORDER = rl.Color(110, 110, 110, 255)
OVERRIDE_BORDER = rl.Color(240, 190, 90, 255)


@dataclass
class Card:
  title: str
  value: str
  color: rl.Color


class Sidebar(Widget):
  def __init__(self):
    super().__init__()
    self._font_bold = gui_app.font(FontWeight.BOLD)
    self._font_regular = gui_app.font(FontWeight.MEDIUM)

  # -------------------------------
  # Layout Rendering
  # -------------------------------

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(
      rl.Rectangle(rect.x, rect.y, SIDEBAR_WIDTH, rect.height),
      COLOR_GREY_BG,
    )

    cards = self._generate_cards()
    offset_y = rect.y + 40

    # Draw each card
    for card in cards:
      card_rect = rl.Rectangle(
        rect.x + CARD_PADDING,
        offset_y,
        SIDEBAR_WIDTH - CARD_PADDING * 2,
        180,
      )

      self._draw_card(card_rect, card)
      offset_y += 180 + CARD_SPACING

    self._draw_footer(rect)

  # -------------------------------
  # Card Rendering
  # -------------------------------

  def _draw_card(self, rect: rl.Rectangle, card: Card):
    # Card background
    rl.draw_rectangle_rounded(rect, 0.18, 12, COLOR_CARD_BG)

    # Colored top accent bar
    rl.draw_rectangle_rounded_lines_ex(
      rect,
      0.18,
      12,
      4,
      card.color,
    )

    # Title
    title_size = measure_text_cached(self._font_regular, card.title, TEXT_SIZE_TITLE)
    rl.draw_text_ex(
      self._font_regular,
      card.title,
      rl.Vector2(rect.x + 22, rect.y + 24),
      TEXT_SIZE_TITLE,
      0,
      COLOR_WHITE,
    )

    # Value
    rl.draw_text_ex(
      self._font_bold,
      card.value,
      rl.Vector2(rect.x + 22, rect.y + 90),
      TEXT_SIZE_VALUE,
      0,
      COLOR_WHITE,
    )

  # -------------------------------
  # Footer (settings icon)
  # -------------------------------

  def _draw_footer(self, rect: rl.Rectangle):
    footer_rect = rl.Rectangle(
      rect.x + CARD_PADDING,
      rect.height - 160,
      SIDEBAR_WIDTH - CARD_PADDING * 2,
      120,
    )

    rl.draw_rectangle_rounded(footer_rect, 0.18, 12, COLOR_CARD_BG)

    # Settings gear icon
    rl.draw_circle_lines(
      int(footer_rect.x + footer_rect.width / 2),
      int(footer_rect.y + footer_rect.height / 2),
      36,
      COLOR_WHITE,
    )
    # Could add a gear texture later

  # -------------------------------
  # Card Data
  # -------------------------------

  def _generate_cards(self):
    dev_state = ui_state.sm["deviceState"]
    engage_state = ui_state.status

    # Engagement color logic
    if engage_state == UIStatus.ENGAGED:
      eng_color = ENGAGED_BORDER
    elif engage_state == UIStatus.OVERRIDE:
      eng_color = OVERRIDE_BORDER
    else:
      eng_color = DISENGAGED_BORDER

    thermal_color = THERMAL_COLORS.get(
      dev_state.thermalStatus,
      THERMAL_COLORS[ThermalStatus.green],
    )

    # Cards
    cards = [
      Card("System", tr("Hoofpilot Stable"), eng_color),
      Card("Vehicle", tr("Connected") if ui_state.sm.all_readers_updated(["carState"]) else tr("No CAN"), eng_color),
      Card("Thermals", f"{round(dev_state.cpuTempC[0])}°C", thermal_color),
      Card("Network", self._wifi_text(), eng_color),
    ]
    return cards

  def _wifi_text(self):
    wifi = ui_state.sm["wifiNetworkInfo"]

    if wifi.connected:
      return f"{wifi.ssid} · {wifi.strength}dBm"

    return tr("Not Connected")


# Sidebar width for importers
__all__ = ["Sidebar", "SIDEBAR_WIDTH"]