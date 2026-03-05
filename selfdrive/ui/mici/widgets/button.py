import math
from collections.abc import Callable
from enum import Enum
from typing import Union

import pyray as rl

from openpilot.common.filter_simple import BounceFilter
from openpilot.system.ui.lib.application import FontWeight, MousePos, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.scroller import DO_ZOOM

try:
  from openpilot.common.params import Params
except ImportError:
  Params = None

SCROLLING_SPEED_PX_S = 50
COMPLICATION_SIZE = 36
LABEL_COLOR = rl.Color(255, 255, 255, int(255 * 0.9))
COMPLICATION_GREY = rl.Color(0xAA, 0xAA, 0xAA, 255)
BADGE_GREEN_BG = rl.Color(51, 171, 76, 50)  # green chip background
BADGE_GREEN_FG = rl.Color(175, 235, 185, 200)  # green-tinted text
CARD_ACTIVE_TINT = rl.Color(140, 230, 150, 255)  # visible green tint for card bg
PRESSED_SCALE = 1.15 if DO_ZOOM else 1.07


class ScrollState(Enum):
  PRE_SCROLL = 0
  SCROLLING = 1
  POST_SCROLL = 2


class BigCircleButton(Widget):
  def __init__(self, icon: str, red: bool = False, icon_size: tuple[int, int] = (64, 53), icon_offset: tuple[int, int] = (0, 0)):
    super().__init__()
    self._red = red
    self._icon_offset = icon_offset

    # State
    self.set_rect(rl.Rectangle(0, 0, 180, 180))
    self._scale_filter = BounceFilter(1.0, 0.1, 1 / gui_app.target_fps)
    self._click_delay = 0.075

    # Icons
    self._txt_icon = gui_app.texture(icon, *icon_size)
    self._txt_btn_disabled_bg = gui_app.texture("icons_mici/buttons/button_circle_disabled.png", 180, 180)

    self._txt_btn_bg = gui_app.texture("icons_mici/buttons/button_circle.png", 180, 180)
    self._txt_btn_pressed_bg = gui_app.texture("icons_mici/buttons/button_circle_pressed.png", 180, 180)

    self._txt_btn_red_bg = gui_app.texture("icons_mici/buttons/button_circle_red.png", 180, 180)
    self._txt_btn_red_pressed_bg = gui_app.texture("icons_mici/buttons/button_circle_red_pressed.png", 180, 180)

  def _draw_content(self, btn_y: float):
    # draw icon
    icon_color = rl.Color(255, 255, 255, int(255 * 0.9)) if self.enabled else rl.Color(255, 255, 255, int(255 * 0.35))
    rl.draw_texture_ex(
      self._txt_icon,
      (
        self._rect.x + (self._rect.width - self._txt_icon.width) / 2 + self._icon_offset[0],
        btn_y + (self._rect.height - self._txt_icon.height) / 2 + self._icon_offset[1],
      ),
      0,
      1.0,
      icon_color,
    )

  def _render(self, _):
    # draw background
    txt_bg = self._txt_btn_bg if not self._red else self._txt_btn_red_bg
    if not self.enabled:
      txt_bg = self._txt_btn_disabled_bg
    elif self.is_pressed:
      txt_bg = self._txt_btn_pressed_bg if not self._red else self._txt_btn_red_pressed_bg

    scale = self._scale_filter.update(PRESSED_SCALE if self.is_pressed else 1.0)
    btn_x = self._rect.x + (self._rect.width * (1 - scale)) / 2
    btn_y = self._rect.y + (self._rect.height * (1 - scale)) / 2
    rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, rl.WHITE)

    self._draw_content(btn_y)


class BigCircleToggle(BigCircleButton):
  def __init__(self, icon: str, toggle_callback: Callable | None = None, icon_size: tuple[int, int] = (64, 53), icon_offset: tuple[int, int] = (0, 0)):
    super().__init__(icon, False, icon_size=icon_size, icon_offset=icon_offset)
    self._toggle_callback = toggle_callback

    # State
    self._checked = False

    # Icons
    self._txt_toggle_enabled = gui_app.texture("icons_mici/buttons/toggle_dot_enabled.png", 66, 66)
    self._txt_toggle_disabled = gui_app.texture("icons_mici/buttons/toggle_dot_disabled.png", 66, 66)

  def set_checked(self, checked: bool):
    self._checked = checked

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    self._checked = not self._checked
    if self._toggle_callback:
      self._toggle_callback(self._checked)

  def _draw_content(self, btn_y: float):
    super()._draw_content(btn_y)

    # draw status icon
    rl.draw_texture_ex(
      self._txt_toggle_enabled if self._checked else self._txt_toggle_disabled,
      (self._rect.x + (self._rect.width - self._txt_toggle_enabled.width) / 2, btn_y + 5),
      0,
      1.0,
      rl.WHITE,
    )


class BigButton(Widget):
  LABEL_HORIZONTAL_PADDING = 40
  LABEL_VERTICAL_PADDING = 23  # visually matches 30 in figma

  """A lightweight stand-in for the Qt BigButton, drawn & updated each frame."""

  def __init__(self, text: str, value: str = "", icon: Union[str, rl.Texture] = "", icon_size: tuple[int, int] = (64, 64), scroll: bool = False):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, 402, 180))
    self.text = text
    self.value = value
    self._icon_size = icon_size
    self._scroll = scroll
    self.set_icon(icon)

    self._scale_filter = BounceFilter(1.0, 0.1, 1 / gui_app.target_fps)
    self._click_delay = 0.075
    self._shake_start: float | None = None
    self._grow_animation_until: float | None = None

    self._rotate_icon_t: float | None = None
    self._badge_labels: list[str] | None = None
    self._active: bool | Callable[[], bool] = True

    self._label = UnifiedLabel(
      text,
      font_size=self._get_label_font_size(),
      font_weight=FontWeight.BOLD,
      text_color=LABEL_COLOR,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_BOTTOM,
      scroll=scroll,
      line_height=0.9,
    )
    self._sub_label = UnifiedLabel(
      value,
      font_size=COMPLICATION_SIZE,
      font_weight=FontWeight.ROMAN,
      text_color=COMPLICATION_GREY,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_BOTTOM,
    )
    self._update_label_layout()

    self._load_images()

  def set_icon(self, icon: Union[str, rl.Texture]):
    self._txt_icon = gui_app.texture(icon, *self._icon_size) if isinstance(icon, str) and len(icon) else icon

  def set_rotate_icon(self, rotate: bool):
    if rotate and self._rotate_icon_t is not None:
      return
    self._rotate_icon_t = rl.get_time() if rotate else None

  def _load_images(self):
    self._txt_default_bg = gui_app.texture("icons_mici/buttons/button_rectangle.png", 402, 180)
    self._txt_pressed_bg = gui_app.texture("icons_mici/buttons/button_rectangle_pressed.png", 402, 180)
    self._txt_disabled_bg = gui_app.texture("icons_mici/buttons/button_rectangle_disabled.png", 402, 180)

  def set_touch_valid_callback(self, touch_callback: Callable[[], bool]) -> None:
    super().set_touch_valid_callback(lambda: touch_callback() and self._grow_animation_until is None)

  def _width_hint(self) -> int:
    # Single line if scrolling, so hide behind icon if exists
    icon_size = self._icon_size[0] if self._txt_icon and self._scroll and self.value else 0
    return int(self._rect.width - self.LABEL_HORIZONTAL_PADDING * 2 - icon_size)

  def _get_label_font_size(self):
    if len(self.text) <= 18:
      return 48
    else:
      return 42

  def _update_label_layout(self):
    self._label.set_font_size(self._get_label_font_size())
    if self.value or self._badge_labels:
      self._label.set_alignment_vertical(rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)
    else:
      self._label.set_alignment_vertical(rl.GuiTextAlignmentVertical.TEXT_ALIGN_BOTTOM)

  def set_text(self, text: str):
    if text == self.text:
      return
    self.text = text
    self._label.set_text(text)
    self._update_label_layout()

  def set_subtitle_font_size(self, size: int):
    self._sub_label.set_font_size(size)

  def set_value(self, value: str):
    # Also update if badges were set — need to clear pill mode even if text matches
    if value == self.value and self._badge_labels is None:
      return
    self.value = value
    self._badge_labels = None
    self._sub_label.set_text(value)
    self._update_label_layout()

  def set_badges(self, entries: list[tuple[str, str]]):
    """Set badge pill chips from (key, value) pairs.

    - 'off' values are hidden
    - 'on' values show just the key
    - Other values show 'key:value'
    """
    labels = []
    for key, val in entries:
      if val == 'off':
        continue
      labels.append(key if val == 'on' else f"{key}:{val}")
    new_labels = labels or None
    if new_labels == self._badge_labels:
      return
    self._badge_labels = new_labels
    self.value = ""
    self._update_label_layout()

  @property
  def active(self) -> bool:
    return self._active() if callable(self._active) else self._active

  def set_active(self, active: bool | Callable[[], bool]) -> None:
    """Set whether the setting is logically in effect (controls badge dimming, not interactivity)."""
    self._active = active

  def get_value(self) -> str:
    return self.value

  def get_text(self):
    return self.text

  def trigger_shake(self):
    self._shake_start = rl.get_time()

  def trigger_grow_animation(self, duration: float = 0.65):
    self._grow_animation_until = rl.get_time() + duration

  @property
  def _shake_offset(self) -> float:
    SHAKE_DURATION = 0.5
    SHAKE_AMPLITUDE = 24.0
    SHAKE_FREQUENCY = 32.0
    t = rl.get_time() - (self._shake_start or 0.0)
    if t > SHAKE_DURATION:
      return 0.0
    decay = 1.0 - t / SHAKE_DURATION
    return decay * SHAKE_AMPLITUDE * math.sin(t * SHAKE_FREQUENCY)

  def set_position(self, x: float, y: float) -> None:
    super().set_position(x + self._shake_offset, y)

  def _handle_background(self) -> tuple[rl.Texture, float, float, float]:
    if self._grow_animation_until is not None:
      if rl.get_time() >= self._grow_animation_until:
        self._grow_animation_until = None

    # draw _txt_default_bg
    txt_bg = self._txt_default_bg
    if not self.enabled:
      txt_bg = self._txt_disabled_bg
    elif self.is_pressed:
      txt_bg = self._txt_pressed_bg

    scale = self._scale_filter.update(PRESSED_SCALE if self.is_pressed or self._grow_animation_until is not None else 1.0)
    btn_x = self._rect.x + (self._rect.width * (1 - scale)) / 2
    btn_y = self._rect.y + (self._rect.height * (1 - scale)) / 2
    return txt_bg, btn_x, btn_y, scale

  def _draw_badges(self, rect: rl.Rectangle):
    """Render cached badge labels as pill chips in a flow layout."""
    font = gui_app.font(FontWeight.BOLD)
    font_size = 26
    h_pad = 10
    gap = 8
    alpha_mult = 1.0 if self.active else 0.3
    badge_bg = rl.Color(BADGE_GREEN_BG.r, BADGE_GREEN_BG.g, BADGE_GREEN_BG.b, int(BADGE_GREEN_BG.a * alpha_mult))
    badge_fg = rl.Color(BADGE_GREEN_FG.r, BADGE_GREEN_FG.g, BADGE_GREEN_FG.b, int(BADGE_GREEN_FG.a * alpha_mult))

    # Measure each badge
    assert self._badge_labels is not None
    specs = []
    for label in self._badge_labels:
      text_w = measure_text_cached(font, label, font_size).x
      specs.append((label, text_w + h_pad * 2, text_w))

    # Flow layout: wrap into rows
    rows: list[list] = []
    current_row: list = []
    row_width = 0.0
    for spec in specs:
      w = spec[1]
      needed = w + (gap if current_row else 0)
      if current_row and row_width + needed > rect.width:
        rows.append(current_row)
        current_row = [spec]
        row_width = w
      else:
        current_row.append(spec)
        row_width += needed
    if current_row:
      rows.append(current_row)

    # Fit badge height to available space
    num_rows = len(rows)
    text_h = measure_text_cached(font, "Xg", font_size).y  # representative line height
    max_h = (rect.height - gap * (num_rows - 1)) / num_rows
    badge_h = max(text_h, min(text_h + 4, max_h))
    v_pad = (badge_h - text_h) / 2

    # Draw rows bottom-up, offset left so first badge *text* aligns with title
    avail_w = rect.width
    cy = rect.y + rect.height - badge_h
    for row in reversed(rows):
      total_badge_w = sum(bw for _, bw, _ in row)
      # Justify: spread badges across full row width when there are 2+ pills
      row_gap = gap if len(row) <= 1 else (avail_w - total_badge_w) / (len(row) - 1)
      cx = rect.x
      for label, badge_w, text_w in row:
        rl.draw_rectangle_rounded(rl.Rectangle(cx, cy, badge_w, badge_h), 0.5, 6, badge_bg)
        rl.draw_text_ex(font, label, rl.Vector2(cx + (badge_w - text_w) / 2, cy + v_pad), font_size, 0, badge_fg)
        cx += badge_w + row_gap
      cy -= badge_h + gap

  def _draw_content(self, btn_y: float):
    # LABEL ------------------------------------------------------------------
    label_x = self._rect.x + self.LABEL_HORIZONTAL_PADDING

    label_color = LABEL_COLOR if self.enabled else rl.Color(255, 255, 255, int(255 * 0.35))
    self._label.set_color(label_color)
    label_rect = rl.Rectangle(label_x, btn_y + self.LABEL_VERTICAL_PADDING, self._width_hint(), self._rect.height - self.LABEL_VERTICAL_PADDING * 2)
    self._label.render(label_rect)

    if self.value or self._badge_labels:
      label_y = btn_y + self.LABEL_VERTICAL_PADDING + self._label.get_content_height(self._width_hint())
      sub_label_height = btn_y + self._rect.height - self.LABEL_VERTICAL_PADDING - label_y
      sub_label_rect = rl.Rectangle(label_x, label_y, self._width_hint(), sub_label_height)
      if self._badge_labels:
        self._draw_badges(sub_label_rect)
      else:
        self._sub_label.render(sub_label_rect)

    # ICON -------------------------------------------------------------------
    if self._txt_icon:
      rotation = 0
      if self._rotate_icon_t is not None:
        rotation = (rl.get_time() - self._rotate_icon_t) * 180

      # draw top right with 30px padding
      x = self._rect.x + self._rect.width - 30 - self._txt_icon.width / 2
      y = btn_y + 30 + self._txt_icon.height / 2
      source_rec = rl.Rectangle(0, 0, self._txt_icon.width, self._txt_icon.height)
      dest_rec = rl.Rectangle(x, y, self._txt_icon.width, self._txt_icon.height)
      origin = rl.Vector2(self._txt_icon.width / 2, self._txt_icon.height / 2)
      rl.draw_texture_pro(self._txt_icon, source_rec, dest_rec, origin, rotation, rl.Color(255, 255, 255, int(255 * 0.9)))

  def _render(self, _):
    txt_bg, btn_x, btn_y, scale = self._handle_background()
    bg_tint = CARD_ACTIVE_TINT if self._badge_labels and self.active else rl.WHITE

    if self._scroll:
      # Scroll mode: draw content UNDER the card texture so the semi-transparent
      # edges of the card act as a soft clip mask for overflowing scroll text.
      scaled_rect = rl.Rectangle(btn_x, btn_y, self._rect.width * scale, self._rect.height * scale)
      rl.draw_rectangle_rounded(scaled_rect, 0.4, 7, rl.Color(0, 0, 0, int(255 * 0.5)))
      self._draw_content(btn_y)
      rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, bg_tint)
    else:
      rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, bg_tint)
      self._draw_content(btn_y)


class BigToggle(BigButton):
  def __init__(self, text: str, value: str = "", initial_state: bool = False, toggle_callback: Callable | None = None):
    super().__init__(text, value, "")
    self._checked = initial_state
    self._toggle_callback = toggle_callback

  @property
  def is_checked(self) -> bool:
    return self._checked

  def _load_images(self):
    super()._load_images()
    self._txt_enabled_toggle = gui_app.texture("icons_mici/buttons/toggle_pill_enabled.png", 84, 66)
    self._txt_disabled_toggle = gui_app.texture("icons_mici/buttons/toggle_pill_disabled.png", 84, 66)

  def set_checked(self, checked: bool):
    self._checked = checked

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    self._checked = not self._checked
    if self._toggle_callback:
      self._toggle_callback(self._checked)

  def _draw_pill(self, x: float, y: float, checked: bool):
    # draw toggle icon top right
    if checked:
      rl.draw_texture_ex(self._txt_enabled_toggle, (x, y), 0, 1.0, rl.WHITE)
    else:
      rl.draw_texture_ex(self._txt_disabled_toggle, (x, y), 0, 1.0, rl.WHITE)

  def _draw_content(self, btn_y: float):
    super()._draw_content(btn_y)

    x = self._rect.x + self._rect.width - self._txt_enabled_toggle.width
    y = btn_y
    self._draw_pill(x, y, self._checked)


class BigMultiToggle(BigToggle):
  def __init__(self, text: str, options: list[str], toggle_callback: Callable | None = None, select_callback: Callable | None = None):
    super().__init__(text, "", toggle_callback=toggle_callback)
    assert len(options) > 0
    self._options = options
    self._select_callback = select_callback

    self.set_value(self._options[0])

  def _width_hint(self) -> int:
    return int(self._rect.width - self.LABEL_HORIZONTAL_PADDING * 2 - self._txt_enabled_toggle.width)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    cur_idx = self._options.index(self.value)
    new_idx = (cur_idx + 1) % len(self._options)
    self.set_value(self._options[new_idx])
    if self._select_callback:
      self._select_callback(self.value)

  def _draw_content(self, btn_y: float):
    # don't draw pill from BigToggle
    BigButton._draw_content(self, btn_y)

    checked_idx = self._options.index(self.value)

    x = self._rect.x + self._rect.width - self._txt_enabled_toggle.width
    y = btn_y

    n = len(self._options)
    spacing = min(35, (self._rect.height - self._txt_enabled_toggle.height) / max(n - 1, 1))
    for i in range(n):
      self._draw_pill(x, y, checked_idx == i)
      y += spacing


class BigMultiParamToggle(BigMultiToggle):
  def __init__(self, text: str, param: str, options: list[str], toggle_callback: Callable | None = None, select_callback: Callable | None = None):
    super().__init__(text, options, toggle_callback, select_callback)
    self._param = param

    self._params = Params()
    self._load_value()

  def _get_param_index(self) -> int:
    idx = self._params.get(self._param, return_default=True) or 0
    return max(0, min(int(idx), len(self._options) - 1))

  def _load_value(self):
    self.set_value(self._options[self._get_param_index()])

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    new_idx = self._options.index(self.value)
    self._params.put_nonblocking(self._param, new_idx)

  def refresh(self):
    new_value = self._options[self._get_param_index()]
    if new_value != self.value:
      self.set_value(new_value)


class _ParamControlMixin:
  """Shared param management for BigParamControl and BigCircleParamControl."""

  def _init_param(self, param: str):
    self._param_key = param
    self._params = Params()
    self.set_checked(self._params.get_bool(self._param_key, False))

  def _write_param(self):
    self._params.put_bool(self._param_key, self._checked)

  def refresh(self):
    new_state = self._params.get_bool(self._param_key, False)
    if new_state != self._checked:
      self.set_checked(new_state)


class BigParamControl(_ParamControlMixin, BigToggle):
  def __init__(self, text: str, param: str, toggle_callback: Callable | None = None):
    BigToggle.__init__(self, text, "", toggle_callback=toggle_callback)
    self._init_param(param)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    # Write param before BigToggle fires toggle_callback so the callback sees the new value
    Widget._handle_mouse_release(self, mouse_pos)
    self._checked = not self._checked
    self._write_param()
    if self._toggle_callback:
      self._toggle_callback(self._checked)


class BigCircleParamControl(_ParamControlMixin, BigCircleToggle):
  def __init__(
    self, icon: str, param: str, toggle_callback: Callable | None = None, icon_size: tuple[int, int] = (64, 53), icon_offset: tuple[int, int] = (0, 0)
  ):
    BigCircleToggle.__init__(self, icon, toggle_callback, icon_size=icon_size, icon_offset=icon_offset)
    self._init_param(param)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)
    self._write_param()


class BigParamOption(BigButton):
  """A BigButton that shows a numeric param value; opens a picker screen on tap."""

  def __init__(
    self,
    text: str,
    param: str,
    min_value: int,
    max_value: int,
    value_change_step: int = 1,
    label_callback: Callable | None = None,
    value_map: dict[int, int] | None = None,
    float_param: bool = False,
    picker_label_callback: Callable | None = None,
    picker_unit: str | Callable[[], str] = "",
    picker_item_width: int = 0,
  ):
    super().__init__(text, "")
    self._param = param
    self._min_value = min_value
    self._max_value = max_value
    self._step = value_change_step
    self._label_callback = label_callback
    self._value_map = value_map
    self._float_param = float_param
    self._picker_label_callback = picker_label_callback
    self._picker_unit = picker_unit
    self._picker_item_width = picker_item_width
    self._params = Params()
    self._current = self._read_value()
    self._update_display()
    self.set_click_callback(self._open_picker)

  def _read_value(self) -> int:
    val = self._params.get(self._param, return_default=True)
    try:
      # float() needed: float_param options store values as float in params
      return int(float(val)) if val is not None else self._min_value
    except (ValueError, TypeError):
      return self._min_value

  def _display_value(self) -> int:
    """Return the mapped display value if value_map exists, otherwise the raw value."""
    if self._value_map and self._current in self._value_map:
      return self._value_map[self._current]
    return self._current

  def _update_display(self):
    display_val = self._display_value()
    if self._label_callback:
      self.set_value(self._label_callback(display_val))
    else:
      self.set_value(str(display_val))

  def refresh(self):
    new = self._read_value()
    if new != self._current:
      self._current = new
      self._update_display()
    elif self._label_callback:
      # Label may depend on external state (e.g. offset type), re-render
      self._update_display()

  def _open_picker(self):
    from openpilot.system.ui.widgets.scroller import NavScroller

    picker = self.create_picker_screen()
    view = NavScroller(scroll_indicator=False, pad=0)
    view.set_back_callback(lambda: self.refresh())
    view.add_widgets([picker])
    view.set_scrolling_enabled(False)
    gui_app.push_widget(view)

  def create_picker_screen(self):
    """Factory: create a NumberPickerScreen from this option's config."""
    from openpilot.selfdrive.ui.mici.widgets.number_picker import NumberPickerScreen

    kwargs = {}
    if self._picker_item_width:
      kwargs['item_width'] = self._picker_item_width
    return NumberPickerScreen(
      title=self.text,
      param=self._param,
      min_value=self._min_value,
      max_value=self._max_value,
      step=self._step,
      label_callback=self._picker_label_callback,
      value_map=self._value_map,
      float_param=self._float_param,
      unit=self._picker_unit,
      **kwargs,
    )
