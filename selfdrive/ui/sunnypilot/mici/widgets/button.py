"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# SP-specific mici widget extensions — keeps upstream button.py clean.

from collections.abc import Callable

import pyray as rl

from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiParamToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached

BADGE_GREEN = (rl.Color(100, 180, 120, 88), rl.Color(130, 200, 145, 230))   # (border, text)
BADGE_GREY = (rl.Color(255, 255, 255, 40), rl.Color(170, 170, 170, 180))   # (border, text)
CARD_ACTIVE_TINT = rl.Color(140, 230, 150, 255)


def speed_unit():
  return "km/h" if ui_state.is_metric else "mph"


class BigButtonSP(BigButton):
  """BigButton with badge pills, disabled pill, active-state tinting, and sub-panel linking.

  Subtitle area modes (mutually exclusive, set by the corresponding method):
    set_badges()    → green outlined pill chips (key/value summary)
    set_disabled()  → single grey 'disabled' pill
    set_value()     → plain text (upstream behavior)
  """

  def __init__(self, text: str, value: str = "", icon="", icon_size: tuple[int, int] = (64, 64), scroll: bool = False):
    # Init before super: BigButton.__init__ calls _update_label_layout which reads these
    self._badge_labels: list[str] | None = None
    self._disabled: bool = False
    self._active: bool = True
    BigButton.__init__(self, text, value, icon, icon_size, scroll)

  def set_subtitle_font_size(self, size: int):
    self._sub_label.set_font_size(size)

  def set_active(self, active: bool) -> None:
    """Controls badge dimming, not interactivity."""
    self._active = active

  def set_badges(self, entries: list[tuple[str, str]]):
    """Set badge pills from (key, value) pairs. 'off' hides, 'on' shows key, else shows value."""
    new_labels = [key if val == 'on' else val for key, val in entries if val != 'off'] or None
    if new_labels == self._badge_labels and not self._disabled:  # called every frame — guard avoids redundant layout
      return
    self._set_badges(new_labels, disabled=False)

  def set_disabled(self):
    """Show a grey 'disabled' pill instead of a text subtitle."""
    if self._disabled:
      return
    self._set_badges([tr("disabled")], disabled=True)

  def set_value(self, value: str):
    """Set plain text subtitle, clearing any badges."""
    if value == self.value and self._badge_labels is None:
      return
    self.value = value
    self._badge_labels = None
    self._disabled = False
    self._sub_label.set_text(value)
    self._update_label_layout()

  def _set_badges(self, labels: list[str] | None, disabled: bool):
    self._badge_labels = labels
    self._disabled = disabled
    self.value = ""  # clears subtitle so upstream _draw_content skips it; we draw badges instead
    self._update_label_layout()

  def _update_label_layout(self):
    self._label.set_font_size(self._get_label_font_size())
    align = rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP if (self.value or self._badge_labels) else rl.GuiTextAlignmentVertical.TEXT_ALIGN_BOTTOM
    self._label.set_alignment_vertical(align)

  def _draw_badges(self, rect: rl.Rectangle):
    """Render badge labels as outlined pill chips in a flow layout."""
    font = gui_app.font(FontWeight.BOLD)
    font_size, h_pad, gap = 28, 10, 8
    alpha_mult = 1.0 if self._active else 0.3
    border_base, text_base = BADGE_GREY if self._disabled else BADGE_GREEN
    border = rl.Color(border_base.r, border_base.g, border_base.b, int(border_base.a * alpha_mult))
    text_color = rl.Color(text_base.r, text_base.g, text_base.b, int(text_base.a * alpha_mult))

    specs = []
    for label in self._badge_labels:
      text_w = measure_text_cached(font, label, font_size).x
      specs.append((label, text_w + h_pad * 2, text_w))

    # Flow layout: wrap into rows
    rows: list[list] = []
    current_row: list = []
    row_width = 0.0
    for spec in specs:
      needed = spec[1] + (gap if current_row else 0)
      if current_row and row_width + needed > rect.width:
        rows.append(current_row)
        current_row, row_width = [spec], spec[1]
      else:
        current_row.append(spec)
        row_width += needed
    if current_row:
      rows.append(current_row)

    text_h = measure_text_cached(font, "Xg", font_size).y
    max_h = (rect.height - gap * (len(rows) - 1)) / len(rows) if len(rows) > 1 else rect.height
    badge_h = max(text_h, min(text_h + 10, max_h))

    # Draw rows bottom-up
    cy = rect.y + rect.height - badge_h
    for row in reversed(rows):
      total_badge_w = sum(bw for _, bw, _ in row)
      row_gap = gap if len(row) <= 1 else (rect.width - total_badge_w) / (len(row) - 1)
      cx = rect.x
      for label, badge_w, text_w in row:
        pill_rect = rl.Rectangle(cx, cy, badge_w, badge_h)
        rl.draw_rectangle_rounded_lines_ex(pill_rect, 0.5, 6, 2, border)
        ty = cy + (badge_h - text_h) / 2 - 2
        rl.draw_text_ex(font, label, rl.Vector2(cx + (badge_w - text_w) / 2, ty), font_size, 0, text_color)
        cx += badge_w + row_gap
      cy -= badge_h + gap

  def _draw_content(self, btn_y: float):
    # Upstream draws label + subtitle + icon. set_badges() clears self.value,
    # so upstream skips the subtitle area — we just draw badges after.
    super()._draw_content(btn_y)
    if self._badge_labels:
      label_x = self._rect.x + self.LABEL_HORIZONTAL_PADDING
      label_y = btn_y + self.LABEL_VERTICAL_PADDING + self._label.get_content_height(self._width_hint())
      sub_label_height = btn_y + self._rect.height - self.LABEL_VERTICAL_PADDING - label_y
      badge_margin = 8
      self._draw_badges(rl.Rectangle(label_x, label_y + badge_margin, self._width_hint(), sub_label_height - badge_margin))

  def link_sub_panel(self, items):
    """Create a sub-panel NavScroller with the given items, linked to this button's click."""
    from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroller import NavScroller
    view = NavScroller()
    view.add_widgets(items)
    self.set_click_callback(lambda: gui_app.push_widget(view))
    return view

  def _render(self, _):
    txt_bg, btn_x, btn_y, scale = self._handle_background()
    bg_tint = CARD_ACTIVE_TINT if self._badge_labels and self._active and not self._disabled else rl.WHITE
    if self._scroll:
      scaled_rect = rl.Rectangle(btn_x, btn_y, self._rect.width * scale, self._rect.height * scale)
      rl.draw_rectangle_rounded(scaled_rect, 0.4, 7, rl.Color(0, 0, 0, int(255 * 0.5)))
      self._draw_content(btn_y)
      rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, bg_tint)
    else:
      rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, bg_tint)
      self._draw_content(btn_y)


class BigMultiParamToggleSP(BigMultiParamToggle):
  """BigMultiParamToggle with bounds-checked param reading, refresh, and dynamic pill spacing."""

  def _draw_content(self, btn_y: float):
    # Skip BigToggle (draws single pill) — we draw multiple pills with dynamic spacing below
    BigButton._draw_content(self, btn_y)
    checked_idx = self._options.index(self.value)
    n = len(self._options)
    step = min(35, (self._rect.height - self._txt_enabled_toggle.height) / max(n - 1, 1))
    x = self._rect.x + self._rect.width - self._txt_enabled_toggle.width
    y = btn_y
    for i in range(n):
      self._draw_pill(x, y, checked_idx == i)
      y += step

  def _get_param_index(self) -> int:
    """Upstream uses raw `params.get()` without bounds — this clamps to valid range."""
    idx = self._params.get(self._param, return_default=True) or 0
    return max(0, min(int(idx), len(self._options) - 1))

  def _load_value(self):
    self.set_value(self._options[self._get_param_index()])

  def refresh(self):
    new_value = self._options[self._get_param_index()]
    if new_value != self.value:
      self.set_value(new_value)


class BigParamOption(BigButton):
  """A BigButton that shows a numeric param value; opens a picker screen on tap."""

  def __init__(self, text: str, param: str, min_value: int, max_value: int,
               value_change_step: int = 1, label_callback: Callable | None = None,
               value_map: dict[int, int] | None = None, float_param: bool = False,
               picker_label_callback: Callable | None = None,
               picker_unit: str | Callable[[], str] = "", picker_item_width: int = 0):
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
    self._current = self._read_value()
    self._update_display()
    self.set_click_callback(self._open_picker)

  def _read_value(self) -> int:
    val = ui_state.params.get(self._param, return_default=True)
    try:
      return int(float(val)) if val is not None else self._min_value
    except (ValueError, TypeError):
      return self._min_value

  def _update_display(self):
    display_val = self._value_map[self._current] if self._value_map and self._current in self._value_map else self._current
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

  def create_picker_screen(self):
    """Create a NumberPickerScreen from this option's config (also used by screenshot tests)."""
    from openpilot.selfdrive.ui.sunnypilot.mici.widgets.number_picker import NumberPickerScreen
    kwargs = {'item_width': self._picker_item_width} if self._picker_item_width else {}
    return NumberPickerScreen(
      title=self.text, param=self._param, min_value=self._min_value, max_value=self._max_value,
      step=self._step, label_callback=self._picker_label_callback, value_map=self._value_map,
      float_param=self._float_param, unit=self._picker_unit, **kwargs,
    )

  def _open_picker(self):
    from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroller import NavScroller
    view = NavScroller()
    view._scroller._show_scroll_indicator = False
    view._scroller._pad = 0
    view.set_back_callback(lambda: self.refresh())
    view.add_widgets([self.create_picker_screen()])
    view.set_scrolling_enabled(False)
    gui_app.push_widget(view)
