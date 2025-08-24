import pyray as rl
from collections.abc import Callable
from openpilot.common.params import Params
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
import openpilot.system.ui.sunnypilot.lib.styles as styles

style = styles.Default

# Dimensions and styling constants
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 80
LABEL_WIDTH = 200
BUTTON_SPACING = 25
VALUE_FONT_SIZE = 50
BUTTON_FONT_SIZE = 60
BUTTON_CORNER_RADIUS = 20
CONTAINER_PADDING = 20
INNER_PADDING = 10
TOP_PADDING = 25

class OptionControlSP(Widget):
    """
    Raylib implementation of OptionControlSP widget for adjusting numeric values
    with increment/decrement buttons and a label showing the current value.

    This widget provides a user interface component similar to the C++ OptionControlSP
    from the sunnypilot project, allowing users to adjust numeric values within a
    specified range.
    """

    def __init__(self, param: str, min_value: int, max_value: int,
                 value_change_step: int = 1, enabled: bool | Callable[[], bool] = True,
                 on_value_changed: Callable[[int], None] | None = None,
                 value_map: dict[int, tuple[int, str]] | None = None,
                 label_width: int = LABEL_WIDTH,
                 use_float_scaling: bool = False, label_callback: Callable[[int], str] | None = None):

        super().__init__()
        self.params = Params()
        self.param_key = param
        self.min_value = min_value
        self.max_value = max_value
        self.value_change_step = value_change_step
        self._enabled = enabled
        self.on_value_changed = on_value_changed
        self.value_map = value_map
        self.label_width = label_width
        self.use_float_scaling = use_float_scaling
        self.current_value = min_value
        self.label_callback = label_callback
        if self.value_map:
            for key in self.value_map:
                if self.value_map[key][0] == self.params.get(self.param_key, return_default = True):
                    self.current_value = int(key)
                    break
        else:
            self.current_value = int(self.params.get(self.param_key, return_default = True))

        # Initialize font and button styles
        self._font = gui_app.font(FontWeight.MEDIUM)

        # Layout rectangles for components
        self.minus_btn_rect = rl.Rectangle(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.label_rect = rl.Rectangle(0, 0, self.label_width, BUTTON_HEIGHT)
        self.plus_btn_rect = rl.Rectangle(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.container_rect = rl.Rectangle(0, 0, 0, 0)

    def set_enabled(self, enabled: bool | Callable[[], bool]):
        """Set whether the control is enabled"""
        self._enabled = enabled

    def get_value(self) -> int:
        """Get the current value of the control"""
        return self.current_value

    def set_value(self, value: int):
        """Set the control to a specific value"""
        if self.min_value <= value <= self.max_value:
            self.current_value = value
            if self.value_map:
                self.params.put(self.param_key, self.value_map[value][0])
            else:
                self.params.put(self.param_key, value)
            if self.on_value_changed:
                self.on_value_changed(value)

    def _update_layout_rects(self):
        """Update the layout rectangles when the widget rect changes"""
        # Calculate total control width
        control_width = (BUTTON_WIDTH * 2) + self.label_width + (BUTTON_SPACING * 2)
        total_width = control_width + (CONTAINER_PADDING * 2)

        # Update the widget's width to match the control
        self._rect.width = total_width

        # Position the control in the parent rectangle
        start_x = self._rect.x + self._rect.width - control_width - (CONTAINER_PADDING * 2)

        # Set container rectangle
        self.container_rect = rl.Rectangle(
            start_x,
            self._rect.y + TOP_PADDING,
            total_width,
            BUTTON_HEIGHT + (CONTAINER_PADDING * 2)
        )

        # Set component rectangles
        component_y = self._rect.y + TOP_PADDING + CONTAINER_PADDING
        start_x = self.container_rect.x + CONTAINER_PADDING

        # Minus button
        self.minus_btn_rect = rl.Rectangle(
            start_x,
            component_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        # Value label
        label_x = start_x + BUTTON_WIDTH + BUTTON_SPACING
        self.label_rect = rl.Rectangle(
            label_x,
            component_y,
            self.label_width,
            BUTTON_HEIGHT
        )

        # Plus button
        plus_x = label_x + self.label_width + BUTTON_SPACING
        self.plus_btn_rect = rl.Rectangle(
            plus_x,
            component_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

    def is_enabled(self) -> bool:
        """Check if the control is enabled"""
        return self._enabled() if callable(self._enabled) else self._enabled

    def get_displayed_value(self) -> str:
        """Get the displayed value, handling value mapping if present"""
        value = self.current_value

        if callable(self.label_callback):
            return self.label_callback(value)

        if self.value_map:
            # Use the value map to get the display string
            if value in self.value_map:
                return self.value_map[value][1]  # Return the display string

        # If using float scaling, format as float
        if self.use_float_scaling:
            return f"{value / 100.0:.2f}"

        return str(value)

    def _render(self, rect: rl.Rectangle) -> bool:
        """Render the widget and handle input"""
        if self._rect.width == 0 or self._rect.height == 0:
            return False

        # Ensure layout rectangles are updated
        if self.container_rect.width == 0:
            self._update_layout_rects()

        # Get enabled state
        enabled = self.is_enabled()

        # Draw container background
        rl.draw_rectangle_rounded(self.container_rect, 1, BUTTON_CORNER_RADIUS, style.OPTIONCONTROL_CONTAINER_BG)

        # Determine button states
        minus_enabled = enabled and self.current_value > self.min_value
        plus_enabled = enabled and self.current_value < self.max_value

        # Render buttons and label
        minus_pressed = self._render_button(self.minus_btn_rect, "-", minus_enabled)
        self._render_value_label()
        plus_pressed = self._render_button(self.plus_btn_rect, "+", plus_enabled)

        # Handle button presses
        value_changed = False
        if minus_pressed and minus_enabled:
            self.current_value -= self.value_change_step
            self.current_value = max(self.min_value, self.current_value)
            value_changed = True
        elif plus_pressed and plus_enabled:
            self.current_value += self.value_change_step
            self.current_value = min(self.max_value, self.current_value)
            value_changed = True

        # Call the value changed callback
        if value_changed:
            self.set_value(self.current_value)

        return value_changed

    def _render_button(self, rect: rl.Rectangle, text: str, enabled: bool) -> bool:
        """Render a button and return True if it was clicked"""
        mouse_pos = rl.get_mouse_position()
        is_hovered = rl.check_collision_point_rec(mouse_pos, rect) and self._touch_valid()
        is_pressed = is_hovered and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT)
        was_clicked = is_hovered and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT)

        # Determine button colors based on state
        if not enabled:
            bg_color = style.OPTIONCONTROL_BTN_DISABLED
            text_color = style.OPTIONCONTROL_TEXT_DISABLED
        elif is_pressed:
            bg_color = style.OPTIONCONTROL_BTN_PRESSED
            text_color = style.OPTIONCONTROL_TEXT_PRESSED
        else:
            bg_color = style.OPTIONCONTROL_BTN_ENABLED
            text_color = style.OPTIONCONTROL_TEXT_ENABLED

        # Draw button background
        rl.draw_rectangle_rounded(rect, 1, BUTTON_CORNER_RADIUS, bg_color)

        # Draw button text
        text_size = measure_text_cached(self._font, text, BUTTON_FONT_SIZE)
        text_x = rect.x + (rect.width - text_size.x) / 2
        text_y = rect.y + (rect.height - text_size.y) / 2
        rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), BUTTON_FONT_SIZE, 0, text_color)

        return was_clicked and enabled

    def _render_value_label(self):
        """Render the current value label"""
        text = self.get_displayed_value()
        text_color = style.OPTIONCONTROL_TEXT_ENABLED if self.is_enabled() else style.OPTIONCONTROL_TEXT_DISABLED

        # Calculate text position centered in the label area
        text_size = measure_text_cached(self._font, text, VALUE_FONT_SIZE)
        text_x = self.label_rect.x + (self.label_rect.width - text_size.x) / 2
        text_y = self.label_rect.y + (self.label_rect.height - text_size.y) / 2

        # Draw the text
        rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), VALUE_FONT_SIZE, 0, text_color)
