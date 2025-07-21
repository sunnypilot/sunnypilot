import pyray as rl
from collections.abc import Callable
from openpilot.system.ui.lib.widget import Widget
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached

# Dimensions
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 120
BUTTON_SPACING = 40
LABEL_WIDTH = 200
VALUE_FONT_SIZE = 56
BUTTON_FONT_SIZE = 48
BUTTON_CORNER_RADIUS = 20
CONTAINER_PADDING = 24
TOP_PADDING = 32

# Calculate total control width including padding
OPTION_CONTROL_WIDTH = (BUTTON_WIDTH * 2) + LABEL_WIDTH + (BUTTON_SPACING * 2) + (CONTAINER_PADDING * 2)

class OptionControl(Widget):
    def __init__(self, min_value: int, max_value: int, initial_value: int,
                 value_change_step: int = 1, enabled: bool | Callable[[], bool]= True,
                 on_value_changed: Callable[[int], None] | None = None):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = initial_value
        self.value_change_step = value_change_step
        self._enabled = enabled
        self.on_value_changed = on_value_changed

        self._font = gui_app.font(FontWeight.MEDIUM)
        self._init_button_style()

    def _init_button_style(self):
        # Material Design 3 colors
        self.surface_container = rl.Color(28, 27, 31, 255)  # Surface container
        self.surface_container_low = rl.Color(23, 22, 26, 255)  # Surface container low
        self.surface_container_high = rl.Color(37, 35, 41, 255)  # Surface container high
        self.surface_container_highest = rl.Color(44, 42, 49, 255)  # Surface container highest
        self.primary = rl.Color(28, 101, 186, 255)  # Primary

        # Button states
        self.btn_enabled = self.surface_container_high
        self.btn_hovered = self.surface_container_highest
        self.btn_pressed = self.primary
        self.btn_disabled = self.surface_container_low

        # Text colors
        self.text_enabled = rl.Color(230, 225, 229, 255)  # On surface
        self.text_pressed = rl.Color(28, 27, 31, 255)  # On primary
        self.text_disabled = rl.Color(146, 144, 148, 255)  # Disabled state

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def _render(self, rect: rl.Rectangle) -> bool:
        inner_width = BUTTON_WIDTH * 2 + LABEL_WIDTH + BUTTON_SPACING * 2

        # Position the control at the right edge of the layout
        start_x = rect.x + rect.width - inner_width - (CONTAINER_PADDING * 2)

        # Draw container background with proper padding
        container_rect = rl.Rectangle(
            start_x - CONTAINER_PADDING,
            rect.y + TOP_PADDING - CONTAINER_PADDING,
            inner_width + (CONTAINER_PADDING * 2),
            BUTTON_HEIGHT + (CONTAINER_PADDING * 2)
        )

        # Draw subtle container shadow
        shadow_color = rl.Color(0, 0, 0, 20)
        shadow_rect = rl.Rectangle(
            container_rect.x,
            container_rect.y + 2,
            container_rect.width,
            container_rect.height
        )
        rl.draw_rectangle_rounded(shadow_rect, 0.2, BUTTON_CORNER_RADIUS, shadow_color)

        # Draw container
        rl.draw_rectangle_rounded(container_rect, 0.2, BUTTON_CORNER_RADIUS, self.surface_container)

        # Adjust component positions for top padding
        component_y = rect.y + TOP_PADDING

        # Position components relative to the right-aligned container
        start_x = container_rect.x + CONTAINER_PADDING

        # Minus button
        minus_btn = rl.Rectangle(start_x, component_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        minus_pressed = self._render_button(minus_btn, "-", self._enabled and self.current_value > self.min_value)

        # Value label
        label_x = start_x + BUTTON_WIDTH + BUTTON_SPACING
        self._render_value_label(label_x, component_y)

        # Plus button
        plus_x = label_x + LABEL_WIDTH + BUTTON_SPACING
        plus_btn = rl.Rectangle(plus_x, component_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        plus_pressed = self._render_button(plus_btn, "+", self._enabled and self.current_value < self.max_value)
        # TODO: Unicode support

        if minus_pressed and self.current_value > self.min_value:
            self._change_value(-self.value_change_step)
            return True
        elif plus_pressed and self.current_value < self.max_value:
            self._change_value(self.value_change_step)
            return True
        return False

    def _render_button(self, rect: rl.Rectangle, text: str, enabled: bool) -> bool:
        mouse_pos = rl.get_mouse_position()
        is_hovered = rl.check_collision_point_rec(mouse_pos, rect)
        is_pressed = is_hovered and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT)
        was_clicked = is_hovered and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT)

        # State-based colors following Material Design state layering
        if not enabled:
            bg_color = self.btn_disabled
            text_color = self.text_disabled
        elif is_pressed:
            bg_color = self.btn_pressed
            text_color = self.text_pressed
        elif is_hovered:
            bg_color = self.btn_hovered
            text_color = self.text_enabled
        else:
            bg_color = self.btn_enabled
            text_color = self.text_enabled

        button_rect = rect
        if enabled and is_pressed:
            # Move button down when pressed (MD3 pressed state)
            button_rect = rl.Rectangle(
                rect.x,
                rect.y + 1,  # Smaller offset for more subtle press
                rect.width,
                rect.height
            )

            # Draw pressed state shadow (more concentrated)
            shadow_color = rl.Color(0, 0, 0, 30)
            rl.draw_rectangle_rounded(button_rect, 0.2, BUTTON_CORNER_RADIUS, shadow_color)
        else:
            # Draw elevation shadow when not pressed
            if enabled:
                # Level 2 elevation (MD3 spec for interactive elements)
                shadow_colors = [
                    (rl.Color(0, 0, 0, 10), 1),  # Ambient shadow
                    (rl.Color(0, 0, 0, 15), 2),  # Mid shadow
                ]

                for color, offset in shadow_colors:
                    shadow_rect = rl.Rectangle(
                        rect.x,
                        rect.y + offset,
                        rect.width,
                        rect.height
                    )
                    rl.draw_rectangle_rounded(shadow_rect, 0.2, BUTTON_CORNER_RADIUS, color)

        # Draw the button
        rl.draw_rectangle_rounded(button_rect, 0.2, BUTTON_CORNER_RADIUS, bg_color)

        # Draw button text
        text_size = measure_text_cached(self._font, text, BUTTON_FONT_SIZE)
        text_x = button_rect.x + (button_rect.width - text_size.x) / 2
        text_y = button_rect.y + (button_rect.height - text_size.y) / 2 - 2
        rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), BUTTON_FONT_SIZE, 0, text_color)

        return was_clicked and enabled

    def _render_value_label(self, x: float, y: float):
        text = str(self.current_value)
        text_size = measure_text_cached(self._font, text, VALUE_FONT_SIZE)

        # Center the text in the label area with slight y-offset for visual balance
        text_x = x + (LABEL_WIDTH - text_size.x) / 2
        text_y = y + (BUTTON_HEIGHT - text_size.y) / 2 - 2

        text_color = self.text_enabled if self._enabled else self.text_disabled
        rl.draw_text_ex(self._font, text, rl.Vector2(text_x, text_y), VALUE_FONT_SIZE, 0, text_color)

    def _change_value(self, delta: int):
        new_value = self.current_value + delta
        if self.min_value <= new_value <= self.max_value:
            self.current_value = new_value
            if self.on_value_changed:
                self.on_value_changed(new_value)
