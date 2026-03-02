"""
BluePilot Metric Card Widget
Reusable card component for displaying metrics (CPU, GPU, Memory, Vehicle, Connect, SunnyLink)
"""

import pyray as rl
from dataclasses import dataclass
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from bluepilot.ui.lib.colors import BPColors
from bluepilot.ui.lib.constants import BPConstants


@dataclass
class MetricData:
  """Data structure for metric card content"""
  label: str
  main_value: str = ""
  left_value: str = ""
  right_value: str = ""
  color: rl.Color = None

  def __post_init__(self):
    if self.color is None:
      self.color = BPColors.GOOD


class MetricCard(Widget):
  """
  A metric display card with status indicator bar.

  Supports two layouts:
  - Compact mode: Label on top, values side-by-side (for CPU/GPU/Memory)
  - Standard mode: 3-row layout with label, main value, and bottom values
  """

  def __init__(self, compact: bool = False):
    super().__init__()
    self._compact = compact
    self._data = MetricData(label="", main_value="", color=BPColors.GOOD)
    self._font_label = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_value = gui_app.font(FontWeight.BOLD)

  def set_data(self, data: MetricData):
    """Update the metric data"""
    self._data = data

  def update_values(self, label: str = None, main_value: str = None,
                    left_value: str = None, right_value: str = None,
                    color: rl.Color = None):
    """Update individual values"""
    if label is not None:
      self._data.label = label
    if main_value is not None:
      self._data.main_value = main_value
    if left_value is not None:
      self._data.left_value = left_value
    if right_value is not None:
      self._data.right_value = right_value
    if color is not None:
      self._data.color = color

  def _render(self, rect: rl.Rectangle) -> None:
    # Draw card shadow
    shadow_rect = rl.Rectangle(rect.x + 2, rect.y + 2, rect.width, rect.height)
    rl.draw_rectangle_rounded(shadow_rect, 0.1, 10, BPColors.SHADOW)

    # Draw card background
    rl.draw_rectangle_rounded(rect, 0.1, 10, BPColors.CARD_BACKGROUND)

    # Draw status indicator bar on left side (clipped)
    bar_width = 6
    rl.begin_scissor_mode(int(rect.x), int(rect.y), bar_width, int(rect.height))
    rl.draw_rectangle_rounded(rect, 0.1, 10, self._data.color)
    rl.end_scissor_mode()

    if self._compact:
      self._render_compact(rect)
    else:
      self._render_standard(rect)

  def _render_compact(self, rect: rl.Rectangle):
    """2-row layout: Label on top, values side-by-side below"""
    padding = 20
    label_font_size = BPConstants.FONT_SIZE_MEDIUM
    value_font_size = BPConstants.FONT_SIZE_XLARGE

    # Draw label (top-left)
    label_pos = rl.Vector2(rect.x + padding, rect.y + 10)
    rl.draw_text_ex(self._font_label, self._data.label, label_pos,
                    label_font_size, 0, BPColors.WHITE)

    # Draw values side by side in bottom row
    value_y = rect.y + rect.height / 2 - 10

    if self._data.left_value:
      left_pos = rl.Vector2(rect.x + padding, value_y)
      rl.draw_text_ex(self._font_value, self._data.left_value, left_pos,
                      value_font_size, 0, BPColors.WHITE)

    if self._data.right_value:
      right_size = measure_text_cached(self._font_value, self._data.right_value, value_font_size)
      right_pos = rl.Vector2(rect.x + rect.width - padding - right_size.x, value_y)
      rl.draw_text_ex(self._font_value, self._data.right_value, right_pos,
                      value_font_size, 0, BPColors.WHITE)

  def _render_standard(self, rect: rl.Rectangle):
    """2-row layout: Label on top, main value below with proper spacing"""
    left_padding = 20  # After status bar
    right_padding = 15
    available_width = rect.width - left_padding - right_padding
    label_font_size = BPConstants.FONT_SIZE_SMALL

    # Draw label (top row, smaller font)
    label_y = rect.y + 15
    label_pos = rl.Vector2(rect.x + left_padding, label_y)
    rl.draw_text_ex(self._font_label, self._data.label, label_pos,
                    label_font_size, 0, BPColors.TEXT_SECONDARY)

    # Draw main value (below label with proper spacing)
    # Use font size that fits the available width
    if self._data.main_value:
      main_y = rect.y + 15 + label_font_size + 10
      main_font_size = BPConstants.FONT_SIZE_LARGE  # Start with 32px

      # Measure text and reduce font size if needed to fit
      text_size = measure_text_cached(self._font_value, self._data.main_value, main_font_size)
      while text_size.x > available_width and main_font_size > BPConstants.FONT_SIZE_SMALL:
        main_font_size -= 2
        text_size = measure_text_cached(self._font_value, self._data.main_value, main_font_size)

      main_pos = rl.Vector2(rect.x + left_padding, main_y)
      rl.draw_text_ex(self._font_value, self._data.main_value, main_pos,
                      main_font_size, 0, BPColors.WHITE)

    # Draw bottom values if present (for cards that need 3 rows)
    if self._data.left_value or self._data.right_value:
      value_font_size = BPConstants.FONT_SIZE_MEDIUM
      bottom_y = rect.y + rect.height - 25

      if self._data.left_value:
        left_pos = rl.Vector2(rect.x + left_padding, bottom_y)
        rl.draw_text_ex(self._font_value, self._data.left_value, left_pos,
                        value_font_size, 0, BPColors.WHITE)

      if self._data.right_value:
        right_size = measure_text_cached(self._font_value, self._data.right_value, value_font_size)
        right_pos = rl.Vector2(rect.x + rect.width - right_padding - right_size.x, bottom_y)
        rl.draw_text_ex(self._font_value, self._data.right_value, right_pos,
                        value_font_size, 0, BPColors.WHITE)
