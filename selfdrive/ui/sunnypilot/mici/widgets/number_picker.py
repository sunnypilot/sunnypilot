import pyray as rl
from collections.abc import Callable

from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.scroll_panel2 import ScrollState
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller import _Scroller as _BaseScroller


class _Scroller(_BaseScroller):
  """_Scroller with snap_ready guard — skips snap for one frame after show_event
  so items can be laid out at the correct offset before snap reads their positions."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._snap_ready = False

  def show_event(self):
    super().show_event()
    self._snap_ready = False

  def _get_scroll(self, visible_items, content_size):
    if self._snap_items and not self._snap_ready:
      # First layout after show — item positions are stale, skip snap correction
      self._snap_ready = True
      self._scroll_snap_filter.x = 0
      self.scroll_panel.update(self._rect, content_size)
      return self.scroll_panel.get_offset()
    return super()._get_scroll(visible_items, content_size)

try:
  from openpilot.common.params import Params
except ImportError:
  Params = None

ITEM_WIDTH = 100
ITEM_HEIGHT = 140
SCREEN_WIDTH = 536
TITLE_HEIGHT = 46
CAROUSEL_TOP = 36   # carousel overlaps title zone by 10px for tighter layout
CAROUSEL_HEIGHT = 180

# Selection band — precomputed gradient texture (see _build_band_texture)
BAND_COLOR = rl.Color(255, 255, 255, int(255 * 0.25))
BAND_TOP = CAROUSEL_TOP + 14
BAND_FADE_LEN = 40


def _lerp(dist, tiers, values):
  """Piecewise linear interpolation for small tier arrays."""
  i = min(int(dist), len(tiers) - 2)
  t = max(0.0, min(1.0, dist - tiers[i]))
  return values[i] + (values[i + 1] - values[i]) * t


class PickerItem(Widget):
  """A lightweight label widget for a single picker value."""

  _DIST_TIERS = [0, 1, 2, 3]
  _FONT_SIZES = [56, 40, 32, 28]   # center, adjacent, far, edge
  _ALPHAS = [0.9, 0.4, 0.2, 0.1]

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

    # Continuous interpolation of font size, alpha, and weight based on distance
    font_size = int(_lerp(dist, self._DIST_TIERS, self._FONT_SIZES))
    alpha = _lerp(dist, self._DIST_TIERS, self._ALPHAS)
    font_weight = FontWeight.BOLD if dist < 0.5 else FontWeight.ROMAN

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


def _build_band_texture():
  """Build a 2px-wide vertical gradient strip: fade in → solid → fade out."""
  band_h = CAROUSEL_HEIGHT - 14 * 2
  fade = min(BAND_FADE_LEN, band_h // 3)
  img = rl.gen_image_color(2, band_h, rl.Color(0, 0, 0, 0))
  for y in range(band_h):
    if y < fade:
      a = int(BAND_COLOR.a * y / fade)
    elif y >= band_h - fade:
      a = int(BAND_COLOR.a * (band_h - 1 - y) / fade)
    else:
      a = BAND_COLOR.a
    c = rl.Color(BAND_COLOR.r, BAND_COLOR.g, BAND_COLOR.b, a)
    rl.image_draw_rectangle(img, 0, y, 2, 1, c)
  tex = rl.load_texture_from_image(img)
  rl.unload_image(img)
  return tex


# Lazy singleton — created on first use (needs OpenGL context)
_band_texture = None


def _get_band_texture():
  global _band_texture
  if _band_texture is None:
    _band_texture = _build_band_texture()
  return _band_texture


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
    self._float_param = float_param
    self._unit = unit
    self._item_width = item_width
    assert step > 0, "step must be positive"
    self._params = Params()
    self._last_center_value: int | None = None
    self._was_settled = True

    # Build picker items — label_callback and value_map only needed during construction
    self._picker_items: list[PickerItem] = []
    val = min_value
    while val <= max_value:
      display_val = value_map[val] if value_map and val in value_map else val
      display = label_callback(display_val) if label_callback else str(display_val)
      self._picker_items.append(PickerItem(val, display, on_tap=self._on_item_tap, item_width=item_width))
      val += step

    # Horizontal scroller with snap, centered padding
    pad = (SCREEN_WIDTH - item_width) // 2
    self._scroller = _Scroller(
      self._picker_items,
      horizontal=True,
      snap_items=True,
      scroll_indicator=False,
      pad=pad,
      spacing=0,
      edge_shadows=False,
    )
    self._scroller.set_reset_scroll_at_show(False)

    self.set_rect(rl.Rectangle(0, 0, SCREEN_WIDTH, TITLE_HEIGHT + CAROUSEL_HEIGHT))

  @property
  def _scroll_panel(self):
    return self._scroller.scroll_panel

  def _center_index(self) -> int:
    """Find which item is between the selection bars using actual layout positions."""
    center_x = self._scroller._rect.x + self._scroller._rect.width / 2
    closest_idx = 0
    closest_dist = float('inf')
    for idx, item in enumerate(self._picker_items):
      dist = abs(item.rect.x + item.rect.width / 2 - center_x)
      if dist < closest_dist:
        closest_dist = dist
        closest_idx = idx
    return closest_idx

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

  def _update_state(self):
    super()._update_state()
    settled = self._scroll_panel.state == ScrollState.STEADY
    if settled and not self._was_settled:
      self._commit_value()
    self._was_settled = settled

  def _render(self, rect):
    # Title
    font = gui_app.font(FontWeight.BOLD)
    title_size = measure_text_cached(font, self._title, 36)
    title_x = rect.x + (rect.width - title_size.x) / 2
    title_y = rect.y + (TITLE_HEIGHT - title_size.y) / 2
    rl.draw_text_ex(font, self._title, rl.Vector2(title_x, title_y), 36, 0,
                    rl.Color(255, 255, 255, int(255 * 0.9)))

    # Carousel area
    carousel_rect = rl.Rectangle(rect.x, rect.y + CAROUSEL_TOP, SCREEN_WIDTH, CAROUSEL_HEIGHT)
    self._scroller.render(carousel_rect)

    # Unit label — resolve dynamically if callable, hide for non-numeric labels
    center = self._picker_items[self._center_index()] if self._picker_items else None
    unit_text = self._unit() if not isinstance(self._unit, str) else self._unit
    if unit_text and center is not None:
      try:
        float(center.display_label.replace('\n', ''))
      except ValueError:
        unit_text = ""

    # Selection band lines — precomputed gradient texture drawn at left and right edges
    band_tex = _get_band_texture()
    band_left = rect.x + (SCREEN_WIDTH - self._item_width) / 2 - 1
    band_right = band_left + self._item_width
    for x in (band_left, band_right):
      rl.draw_texture(band_tex, int(x), int(rect.y + BAND_TOP), rl.WHITE)

    if unit_text:
      unit_font = gui_app.font(FontWeight.BOLD)
      unit_font_size = 32
      unit_color = rl.Color(255, 255, 255, int(255 * 0.5))
      unit_size = measure_text_cached(unit_font, unit_text, unit_font_size)
      unit_x = rect.x + (SCREEN_WIDTH - unit_size.x) / 2
      unit_y = rect.y + rect.height - unit_size.y - 2
      rl.draw_text_ex(unit_font, unit_text, rl.Vector2(unit_x, unit_y), unit_font_size, 0, unit_color)
