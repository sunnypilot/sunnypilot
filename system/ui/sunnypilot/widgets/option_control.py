import pyray as rl
from collections.abc import Callable
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.widgets.list_view import ItemAction

# Dimensions and styling constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 150
LABEL_WIDTH = 350
BUTTON_SPACING = 25
VALUE_FONT_SIZE = 50
BUTTON_FONT_SIZE = 60
CONTAINER_PADDING = 20


class OptionControlSP(ItemAction):
  def __init__(self, param: str, min_value: int, max_value: int,
               value_change_step: int = 1, enabled: bool | Callable[[], bool] = True,
               on_value_changed: Callable[[int], None] | None = None,
               value_map: dict[int, int] | None = None,
               label_width: int = LABEL_WIDTH,
               use_float_scaling: bool = False, label_callback: Callable[[int], str] | None = None):

    super().__init__(enabled=enabled)
    self.params = Params()
    self.param_key = param
    self.min_value = min_value
    self.max_value = max_value
    self.value_change_step = value_change_step
    self._minus_enabled = enabled
    self._plus_enabled = enabled
    self.on_value_changed = on_value_changed
    self.value_map = value_map
    self.label_width = label_width
    self.use_float_scaling = use_float_scaling
    self.current_value = min_value
    self.label_callback = label_callback
    if self.value_map:
      for key in self.value_map:
        if self.value_map[key] == self.params.get(self.param_key, return_default=True):
          self.current_value = int(key)
          break
    else:
      self.current_value = int(self.params.get(self.param_key, return_default=True))

    # Initialize font and button styles
    self._font = gui_app.font(FontWeight.MEDIUM)

    # Layout rectangles for components
    self.minus_btn_rect = rl.Rectangle(0, 0, 0, 0)
    self.plus_btn_rect = rl.Rectangle(0, 0, 0, 0)

  def get_value(self) -> int:
    """Get the current value of the control"""
    return self.current_value

  def set_value(self, value: int):
    """Set the control to a specific value"""
    if self.min_value <= value <= self.max_value:
      self.current_value = value
      if self.value_map:
        self.params.put(self.param_key, self.value_map[value])
      else:
        if self.use_float_scaling:
          self.params.put(self.param_key, value / 100.0)
        else:
          self.params.put(self.param_key, value)
      if self.on_value_changed:
        self.on_value_changed(value)

  def get_displayed_value(self) -> str:
    """Get the displayed value, handling value mapping if present"""
    value = self.current_value

    if callable(self.label_callback):
      if self.value_map:
        return self.label_callback(self.value_map[value])
      else:
        return self.label_callback(value)

    if self.value_map:
      # Use the value map to get the display string
      if value in self.value_map:
        return str(self.value_map[value])  # Return the display string

    # If using float scaling, format as float
    if self.use_float_scaling:
      return f"{value / 100.0:.2f}"

    return str(value)

  def _render(self, rect: rl.Rectangle):
    if self._rect.width == 0 or self._rect.height == 0 or not self.is_visible:
      return

    control_width = (BUTTON_WIDTH * 2) + self.label_width + (BUTTON_SPACING * 2)
    total_width = control_width + (CONTAINER_PADDING * 2)
    self._rect.width = total_width

    start_x = self._rect.x + self._rect.width - control_width - (CONTAINER_PADDING * 2)
    component_y = rect.y + (rect.height - BUTTON_HEIGHT) / 2
    self.container_rect = rl.Rectangle(start_x, component_y, total_width, BUTTON_HEIGHT)

    # background
    rl.draw_rectangle_rounded(self.container_rect, 0.2, 20, style.OPTION_CONTROL_CONTAINER_BG)

    # minus button
    self.minus_btn_rect = rl.Rectangle(self.container_rect.x, component_y, BUTTON_WIDTH + CONTAINER_PADDING,
                                       BUTTON_HEIGHT)

    # label
    label_x = self.container_rect.x + CONTAINER_PADDING + BUTTON_WIDTH + BUTTON_SPACING
    self.label_rect = rl.Rectangle(label_x, component_y, self.label_width, BUTTON_HEIGHT)

    # plus button
    plus_x = label_x + self.label_width + BUTTON_SPACING
    self.plus_btn_rect = rl.Rectangle(plus_x, component_y, BUTTON_WIDTH + CONTAINER_PADDING, BUTTON_HEIGHT)

    self._minus_enabled = self.enabled and self.current_value > self.min_value
    self._plus_enabled = self.enabled and self.current_value < self.max_value

    self._render_button(self.minus_btn_rect, "-", self._minus_enabled)
    self._render_value_label()
    self._render_button(self.plus_btn_rect, "+", self._plus_enabled)

  def _render_button(self, rect: rl.Rectangle, text: str, enabled: bool):
    mouse_pos = rl.get_mouse_position()
    is_pressed = (rl.check_collision_point_rec(mouse_pos, rect) and
                  self._touch_valid() and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT))

    text_color = style.ITEM_TEXT_COLOR if enabled else style.ITEM_DISABLED_TEXT_COLOR

    # highlight
    if enabled and is_pressed:
      rl.draw_rectangle_rounded(rect, 0.2, 20, style.OPTION_CONTROL_BTN_PRESSED)

    # button text
    text_size = measure_text_cached(self._font, text, BUTTON_FONT_SIZE)
    text_x = rect.x + (rect.width - text_size.x) / 2
    text_y = rect.y + (rect.height - text_size.y) / 2
    rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), BUTTON_FONT_SIZE, 0, text_color)

  def _render_value_label(self):
    """Render the current value label"""
    text = self.get_displayed_value()
    text_color = style.ITEM_TEXT_COLOR if self.enabled else style.ITEM_DISABLED_TEXT_COLOR

    text_size = measure_text_cached(self._font, text, VALUE_FONT_SIZE)
    text_x = self.label_rect.x + (self.label_rect.width - text_size.x) / 2
    text_y = self.label_rect.y + (self.label_rect.height - text_size.y) / 2

    rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), VALUE_FONT_SIZE, 0, text_color)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if self._minus_enabled and rl.check_collision_point_rec(mouse_pos, self.minus_btn_rect):
      self.current_value -= self.value_change_step
      self.current_value = max(self.min_value, self.current_value)
    elif self._plus_enabled and rl.check_collision_point_rec(mouse_pos, self.plus_btn_rect):
      self.current_value += self.value_change_step
      self.current_value = min(self.max_value, self.current_value)

    self.set_value(self.current_value)
