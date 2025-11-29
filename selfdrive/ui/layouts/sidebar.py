import pyray as rl
from dataclasses import dataclass
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.lib.text_measure import measure_text_cached

SIDEBAR_WIDTH = 360
CARD_RADIUS = 0.18
CARD_PADDING = 24
CARD_SPACING = 24

COLOR_BG = rl.Color(15, 15, 18, 255)
COLOR_CARD_BG = rl.Color(28, 28, 32, 200)
COLOR_WHITE = rl.WHITE
COLOR_GREY = rl.Color(180, 180, 180, 255)
COLOR_ACCENT = rl.Color(120, 180, 255, 255)


class Sidebar:
  def __init__(self):
    self._on_settings = None
    self._on_reboot = None
    self._on_shutdown = None

  # --------------------------------------------------------
  # CALLBACK API (required by MainLayout)
  # --------------------------------------------------------
  def set_callbacks(self, on_settings=None, on_reboot=None, on_shutdown=None):
    self._on_settings = on_settings
    self._on_reboot = on_reboot
    self._on_shutdown = on_shutdown

  # --------------------------------------------------------
  # MAIN RENDER
  # --------------------------------------------------------
  def render(self, rect: rl.Rectangle):
    # Sidebar background
    rl.draw_rectangle(int(rect.x), int(rect.y), SIDEBAR_WIDTH, int(rect.height), COLOR_BG)

    y = rect.y + CARD_PADDING

    # Konik Stable Card
    y = self._draw_card(rect, y, "Konik Stable", self._get_konik_status())

    # Vehicle State Card
    y = self._draw_card(rect, y, "Vehicle State", self._get_vehicle_status())

    # Temperature Card
    y = self._draw_card(rect, y, "Temperature", self._get_temp_status())

    # WiFi Card
    y = self._draw_card(rect, y, "WiFi", self._get_wifi_status())

    # Settings button (footer)
    self._draw_footer(rect)

  # --------------------------------------------------------
  # CARD COMPONENT
  # --------------------------------------------------------
  def _draw_card(self, rect: rl.Rectangle, y: int, title: str, value: str) -> int:
    card_rect = rl.Rectangle(
      rect.x + CARD_PADDING,
      y,
      SIDEBAR_WIDTH - CARD_PADDING * 2,
      130
    )

    # Card background
    rl.draw_rectangle_rounded(card_rect, CARD_RADIUS, 12, COLOR_CARD_BG)

    # Card text
    gui_label(
      rl.Rectangle(card_rect.x + 24, card_rect.y + 18, card_rect.width, 40),
      title,
      font_weight=FontWeight.BOLD,
      font_size=42,
      color=COLOR_WHITE,
    )

    gui_label(
      rl.Rectangle(card_rect.x + 24, card_rect.y + 70, card_rect.width, 40),
      value,
      font_weight=FontWeight.NORMAL,
      font_size=36,
      color=COLOR_GREY,
    )

    return y + 130 + CARD_SPACING

  # --------------------------------------------------------
  # SETTINGS FOOTER (CLICKABLE)
  # --------------------------------------------------------
  def _draw_footer(self, rect: rl.Rectangle):
    footer_rect = rl.Rectangle(
      rect.x + CARD_PADDING,
      rect.height - 160,
      SIDEBAR_WIDTH - CARD_PADDING * 2,
      120,
    )

    rl.draw_rectangle_rounded(footer_rect, CARD_RADIUS, 12, COLOR_CARD_BG)

    # Handle Click
    if rl.is_mouse_button_released(rl.MOUSE_LEFT_BUTTON):
      mx, my = rl.get_mouse_position()
      if rl.check_collision_point_rec(rl.Vector2(mx, my), footer_rect):
        if self._on_settings:
          self._on_settings()

    # Settings Icon (Clean minimal circle)
    cx = int(footer_rect.x + footer_rect.width / 2)
    cy = int(footer_rect.y + footer_rect.height / 2)

    rl.draw_circle_lines(cx, cy, 38, COLOR_WHITE)
    rl.draw_circle(cx, cy, 6, COLOR_WHITE)

  # --------------------------------------------------------
  # STATUS HELPERS
  # --------------------------------------------------------

  def _get_konik_status(self):
    ss = ui_state.sm["controlsState"]
    return "Running" if ss.enabled else "Idle"

  def _get_vehicle_status(self):
    cs = ui_state.sm["carState"]
    if cs.brakePressed:
      return "Brake Pressed"
    elif cs.gasPressed:
      return "Accelerating"
    return "Cruising"

  def _get_temp_status(self):
    thermo = ui_state.sm["deviceState"]
    temp = thermo.cpuTempC
    return f"{temp:.0f}°C"

  def _get_wifi_status(self):
    dev = ui_state.sm["deviceState"]
    rssi = dev.wifiRSSI

    if rssi > -55:
      return "Excellent"
    elif rssi > -65:
      return "Good"
    elif rssi > -75:
      return "Weak"
    return "Very Weak"