"""
BluePilot Network Card Widget
Custom network status card with signal bars, carrier/SSID display
"""

import pyray as rl
from collections.abc import Callable
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from bluepilot.ui.lib.colors import BPColors
from bluepilot.ui.lib.constants import BPConstants


class NetworkCard(Widget):
  """
  Network status card displaying:
  - Network label
  - Carrier/SSID name (in accent color)
  - Network type (WiFi, LTE, etc.)
  - Signal strength bars
  """

  def __init__(self):
    super().__init__()
    self._net_type = "Offline"
    self._net_carrier_ssid = "No Connection"
    self._net_strength = 0
    self._is_pressed_state = False
    self._on_click: Callable | None = None

    self._font_label = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_carrier = gui_app.font(FontWeight.BOLD)
    self._font_type = gui_app.font(FontWeight.SEMI_BOLD)

  def set_on_click(self, callback: Callable):
    """Set callback for when card is clicked"""
    self._on_click = callback

  def update_network(self, net_type: str, carrier_ssid: str, strength: int):
    """Update network status"""
    self._net_type = net_type
    self._net_carrier_ssid = carrier_ssid
    self._net_strength = max(0, min(5, strength))

  def _handle_mouse_release(self, mouse_pos: MousePos) -> bool:
    if self._on_click:
      self._on_click()
      return True
    return False

  def _render(self, rect: rl.Rectangle) -> None:
    # Determine if pressed for visual feedback
    bg_color = BPColors.darker(BPColors.CARD_BACKGROUND) if self.is_pressed else BPColors.CARD_BACKGROUND

    # Draw card shadow
    shadow_rect = rl.Rectangle(rect.x + 2, rect.y + 2, rect.width, rect.height)
    rl.draw_rectangle_rounded(shadow_rect, 0.08, 10, BPColors.SHADOW)

    # Draw card background
    rl.draw_rectangle_rounded(rect, 0.08, 10, bg_color)

    # Draw accent indicator bar on left side
    rl.begin_scissor_mode(int(rect.x), int(rect.y), 6, int(rect.height))
    rl.draw_rectangle_rounded(rect, 0.08, 10, BPColors.ACCENT)
    rl.end_scissor_mode()

    # Draw "NETWORK" label (top-left)
    label_pos = rl.Vector2(rect.x + 20, rect.y + 15)
    rl.draw_text_ex(self._font_label, "NETWORK", label_pos,
                    BPConstants.FONT_SIZE_MEDIUM, 0, BPColors.WHITE)

    # Draw carrier/SSID (in accent color)
    carrier_y = rect.y + 50
    available_width = rect.width - 40  # Padding on both sides

    # Truncate carrier name if too long
    display_name = self._net_carrier_ssid
    carrier_size = measure_text_cached(self._font_carrier, display_name, BPConstants.FONT_SIZE_LARGE)
    if carrier_size.x > available_width:
      # Simple truncation with ellipsis
      while len(display_name) > 3:
        display_name = display_name[:-1]
        carrier_size = measure_text_cached(self._font_carrier, display_name + "...", BPConstants.FONT_SIZE_LARGE)
        if carrier_size.x <= available_width:
          display_name += "..."
          break

    carrier_pos = rl.Vector2(rect.x + 20, carrier_y)
    rl.draw_text_ex(self._font_carrier, display_name, carrier_pos,
                    BPConstants.FONT_SIZE_LARGE, 0, BPColors.ACCENT)

    # Draw signal strength bars (bottom right)
    self._draw_signal_bars(rect)

    # Draw network type text (bottom left)
    type_text = self._net_type if self._net_type else "Unknown"
    type_pos = rl.Vector2(rect.x + 20, rect.y + rect.height - 35)
    rl.draw_text_ex(self._font_type, type_text, type_pos,
                    BPConstants.FONT_SIZE_SMALL, 0, BPColors.LIGHT_GRAY)

  def _draw_signal_bars(self, rect: rl.Rectangle):
    """Draw signal strength indicator bars"""
    bar_x = int(rect.x + rect.width - 90)
    bar_y = int(rect.y + rect.height - 15)
    bar_width = BPConstants.SIGNAL_BAR_WIDTH
    spacing = BPConstants.SIGNAL_BAR_SPACING
    max_height = BPConstants.SIGNAL_BAR_MAX_HEIGHT

    for i in range(BPConstants.SIGNAL_BAR_COUNT):
      bar_height = (i + 1) * max_height // BPConstants.SIGNAL_BAR_COUNT
      bar_color = BPColors.ACCENT if i < self._net_strength else BPColors.SIGNAL_INACTIVE

      # Draw shadow
      shadow_x = bar_x + i * (bar_width + spacing) + 1
      shadow_y = bar_y - bar_height + 2
      rl.draw_rectangle_rounded(
        rl.Rectangle(shadow_x, shadow_y, bar_width, bar_height),
        0.3, 4, BPColors.SHADOW
      )

      # Draw bar
      x = bar_x + i * (bar_width + spacing)
      y = bar_y - bar_height
      bar_rect = rl.Rectangle(x, y, bar_width, bar_height)

      # Draw bar with slight border
      rl.draw_rectangle_rounded(bar_rect, 0.3, 4, bar_color)

      # Add subtle border for active bars
      if i < self._net_strength:
        border_color = BPColors.with_alpha(BPColors.WHITE, 30)
        rl.draw_rectangle_rounded_lines_ex(bar_rect, 0.3, 4, 1, border_color)
