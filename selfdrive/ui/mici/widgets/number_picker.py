import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.scroll_panel2 import ScrollState
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import Scroller

try:
  from openpilot.common.params import Params
except ImportError:
  Params = None

ITEM_WIDTH = 100
ITEM_HEIGHT = 140
SCREEN_WIDTH = 536
TITLE_HEIGHT = 50
CAROUSEL_HEIGHT = 176  # SCREEN_HEIGHT(226) - TITLE_HEIGHT

# Selection band line color
BAND_COLOR = rl.Color(255, 255, 255, int(255 * 0.15))

# Font sizes and alphas for distance tiers
CENTER_FONT_SIZE = 56
CENTER_ALPHA = 0.9
ADJ_FONT_SIZE = 40
ADJ_ALPHA = 0.4
FAR_FONT_SIZE = 32
FAR_ALPHA = 0.2
EDGE_FONT_SIZE = 28
EDGE_ALPHA = 0.1


class PickerItem(Widget):
  """A lightweight label widget for a single picker value."""

  def __init__(self, raw_value: int, display_label: str, on_tap: Callable[[int], None] | None = None,
               item_width: int = ITEM_WIDTH):
    super().__init__()
    self.raw_value = raw_value
    self.display_label = display_label
    self._on_tap = on_tap
    self._item_width = item_width
    self.set_rect(rl.Rectangle(0, 0, item_width, ITEM_HEIGHT))

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    if self._on_tap:
      self._on_tap(self.raw_value)

  def _render(self, rect):
    # Compute distance from parent (Scroller viewport) center in item-widths
    if self._parent_rect is not None:
      parent_center_x = self._parent_rect.x + self._parent_rect.width / 2
    else:
      parent_center_x = SCREEN_WIDTH / 2

    item_center_x = self._rect.x + self._rect.width / 2
    dist = abs(item_center_x - parent_center_x) / self._item_width

    # Interpolate font size and alpha based on distance
    if dist < 0.5:
      font_size = CENTER_FONT_SIZE
      alpha = CENTER_ALPHA
      font_weight = FontWeight.BOLD
    elif dist < 1.5:
      t = (dist - 0.5)
      font_size = int(CENTER_FONT_SIZE + (ADJ_FONT_SIZE - CENTER_FONT_SIZE) * t)
      alpha = CENTER_ALPHA + (ADJ_ALPHA - CENTER_ALPHA) * t
      font_weight = FontWeight.ROMAN
    elif dist < 2.5:
      t = (dist - 1.5)
      font_size = int(ADJ_FONT_SIZE + (FAR_FONT_SIZE - ADJ_FONT_SIZE) * t)
      alpha = ADJ_ALPHA + (FAR_ALPHA - ADJ_ALPHA) * t
      font_weight = FontWeight.ROMAN
    else:
      font_size = EDGE_FONT_SIZE
      alpha = EDGE_ALPHA
      font_weight = FontWeight.ROMAN

    font = gui_app.font(font_weight)
    color = rl.Color(255, 255, 255, int(255 * alpha))
    padding = 8
    max_width = self._rect.width - padding

    if '\n' in self.display_label:
      # Multi-line: main line at full size, subtitle smaller and dimmer
      lines = self.display_label.split('\n', 1)

      # Shrink to fit: text labels like "default" (ui timeout) overflow at size 56
      main_size = measure_text_cached(font, lines[0], font_size)
      if main_size.x > max_width and main_size.x > 0:
        font_size = max(int(font_size * max_width / main_size.x), 14)
        main_size = measure_text_cached(font, lines[0], font_size)

      sub_font_size = max(int(font_size * 0.42), 14)
      sub_font = gui_app.font(FontWeight.ROMAN)
      sub_size = measure_text_cached(sub_font, lines[1], sub_font_size)

      # Keep main line at same vertical center as single-line items, subtitle below
      main_y = self._rect.y + (self._rect.height - main_size.y) / 2
      main_x = self._rect.x + (self._rect.width - main_size.x) / 2
      rl.draw_text_ex(font, lines[0], rl.Vector2(main_x, main_y), font_size, 0, color)

      gap = -2
      sub_color = rl.Color(255, 255, 255, int(255 * alpha * 0.55))
      sub_x = self._rect.x + (self._rect.width - sub_size.x) / 2
      rl.draw_text_ex(sub_font, lines[1], rl.Vector2(sub_x, main_y + main_size.y + gap), sub_font_size, 0, sub_color)
    else:
      # Shrink to fit: text labels like "default" (ui timeout) overflow at size 56
      text_size = measure_text_cached(font, self.display_label, font_size)
      if text_size.x > max_width and text_size.x > 0:
        font_size = max(int(font_size * max_width / text_size.x), 14)
        text_size = measure_text_cached(font, self.display_label, font_size)
      text_x = self._rect.x + (self._rect.width - text_size.x) / 2
      text_y = self._rect.y + (self._rect.height - text_size.y) / 2
      rl.draw_text_ex(font, self.display_label, rl.Vector2(text_x, text_y), font_size, 0, color)


class NumberPickerScreen(Widget):
  """Full picker sub-screen with title and horizontal snap-scrolling carousel."""

  def __init__(self, title: str, param: str, min_value: int, max_value: int,
               step: int = 1, label_callback: Callable | None = None,
               value_map: dict[int, int] | None = None, float_param: bool = False,
               unit: str | Callable[[], str] = "", item_width: int = ITEM_WIDTH):
    super().__init__()
    self._title = title
    self._param = param
    self._min_value = min_value
    self._max_value = max_value
    self._step = step
    self._label_callback = label_callback
    self._value_map = value_map
    self._float_param = float_param
    self._unit = unit
    self._item_width = item_width
    assert step > 0, "step must be positive"
    self._params = Params()
    self._last_center_value: int | None = None

    # Build picker items
    self._picker_items: list[PickerItem] = []
    val = min_value
    while val <= max_value:
      display = self._make_label(val)
      item = PickerItem(val, display, on_tap=self._on_item_tap, item_width=item_width)
      self._picker_items.append(item)
      val += step

    # Horizontal scroller with snap, centered padding
    pad = (SCREEN_WIDTH - item_width) // 2
    self._scroller = Scroller(
      horizontal=True,
      snap_items=True,
      scroll_indicator=False,
      pad=pad,
      spacing=0,
      edge_shadows=False,
    )
    self._scroller.add_widgets(self._picker_items)
    self._scroller.set_reset_scroll_at_show(False)

    self.set_rect(rl.Rectangle(0, 0, SCREEN_WIDTH, TITLE_HEIGHT + CAROUSEL_HEIGHT))

  def _make_label(self, raw_value: int) -> str:
    display_val = raw_value
    if self._value_map and raw_value in self._value_map:
      display_val = self._value_map[raw_value]
    if self._label_callback:
      return self._label_callback(display_val)
    return str(display_val)

  @property
  def _scroll_panel(self):
    return self._scroller.scroll_panel

  def _center_index(self) -> int:
    """Compute center item index from scroll offset (independent of layout timing)."""
    offset = self._scroll_panel.get_offset()
    idx = int(-offset / self._item_width + 0.5)
    return max(0, min(idx, len(self._picker_items) - 1))

  def _scroll_to_index(self, idx: int):
    """Scroll so item at idx is centered."""
    self._scroll_panel.set_offset(-(idx * self._item_width))

  def _on_item_tap(self, raw_value: int):
    for idx, item in enumerate(self._picker_items):
      if item.raw_value == raw_value:
        self._scroll_to_index(idx)
        break

  def _read_value(self) -> int:
    val = self._params.get(self._param, return_default=True)
    try:
      # float() needed: float_param options store values as float in params
      return int(float(val)) if val is not None else self._min_value
    except (ValueError, TypeError):
      return self._min_value

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    current = self._read_value()
    self._last_center_value = current
    for idx, item in enumerate(self._picker_items):
      if item.raw_value == current:
        self._scroll_to_index(idx)
        break

  def _commit_value(self):
    """Write the current center item's value to params."""
    if not self._picker_items:
      return
    center = self._picker_items[self._center_index()]
    if center.raw_value != self._last_center_value:
      self._last_center_value = center.raw_value
      self._params.put_nonblocking(self._param, float(center.raw_value) if self._float_param else center.raw_value)

  def hide_event(self):
    super().hide_event()
    self._scroller.hide_event()
    self._commit_value()

  def _update_state(self):
    super()._update_state()
    # Only commit while scroll is settled — during AUTO_SCROLL or
    # MANUAL_SCROLL the offset is in flux and can transiently indicate
    # the wrong item, causing off-by-one writes. hide_event() handles
    # the case where the picker is dismissed mid-animation.
    if self._scroll_panel.state != ScrollState.STEADY:
      return
    self._commit_value()

  def _render(self, rect):
    # Title
    font = gui_app.font(FontWeight.BOLD)
    title_size = measure_text_cached(font, self._title, 36)
    title_x = rect.x + (rect.width - title_size.x) / 2
    title_y = rect.y + (TITLE_HEIGHT - title_size.y) / 2
    rl.draw_text_ex(font, self._title, rl.Vector2(title_x, title_y), 36, 0,
                    rl.Color(255, 255, 255, int(255 * 0.9)))

    # Carousel area
    carousel_rect = rl.Rectangle(rect.x, rect.y + TITLE_HEIGHT, SCREEN_WIDTH, CAROUSEL_HEIGHT)
    self._scroller.render(carousel_rect)

    # Selection band lines
    band_left = rect.x + (SCREEN_WIDTH - self._item_width) / 2
    band_right = band_left + self._item_width
    band_top = rect.y + TITLE_HEIGHT + 10
    band_bottom = rect.y + TITLE_HEIGHT + CAROUSEL_HEIGHT - 10
    rl.draw_line_ex(rl.Vector2(band_left, band_top), rl.Vector2(band_left, band_bottom), 2, BAND_COLOR)
    rl.draw_line_ex(rl.Vector2(band_right, band_top), rl.Vector2(band_right, band_bottom), 2, BAND_COLOR)

    # Unit label — resolve dynamically if callable, hide for non-numeric labels
    center = self._picker_items[self._center_index()] if self._picker_items else None
    unit_text = self._unit() if not isinstance(self._unit, str) else self._unit
    # Hide unit for non-numeric labels (e.g. "auto" in brightness, "default" in timeout)
    if unit_text and center is not None:
      try:
        float(center.display_label.replace('\n', ''))
      except ValueError:
        unit_text = ""
    if unit_text:
      unit_font = gui_app.font(FontWeight.ROMAN)
      unit_font_size = 24
      unit_color = rl.Color(255, 255, 255, int(255 * 0.35))
      unit_size = measure_text_cached(unit_font, unit_text, unit_font_size)
      unit_x = rect.x + (SCREEN_WIDTH - unit_size.x) / 2
      unit_y = band_bottom - unit_size.y - 4
      rl.draw_text_ex(unit_font, unit_text, rl.Vector2(unit_x, unit_y), unit_font_size, 0, unit_color)
