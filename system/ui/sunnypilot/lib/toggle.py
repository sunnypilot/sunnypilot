import pyray as rl
import openpilot.system.ui.lib.toggle as ToggleOP

ON_COLOR = rl.Color(28, 101, 186, 255)
OFF_COLOR = rl.Color(0x39, 0x39, 0x39, 255)
KNOB_COLOR = rl.WHITE
DISABLED_ON_COLOR = rl.Color(0x22, 0x77, 0x22, 255)  # Dark green when disabled + on
DISABLED_OFF_COLOR = rl.Color(0x39, 0x39, 0x39, 255)
DISABLED_KNOB_COLOR = rl.Color(0x88, 0x88, 0x88, 255)
WIDTH, HEIGHT = 130, 80
BG_HEIGHT = 60

class ToggleSP:
  def _render(self, rect: rl.Rectangle):

    if self._enabled:
      bg_color = ToggleOP.Toggle._blend_color(self, OFF_COLOR, ON_COLOR, self._progress)
      knob_color = KNOB_COLOR
    else:
      bg_color = ToggleOP.Toggle._blend_color(self, DISABLED_OFF_COLOR, DISABLED_ON_COLOR, self._progress)
      knob_color = DISABLED_KNOB_COLOR

    # Draw background
    bg_rect = rl.Rectangle(self._rect.x + 5, self._rect.y + 10, WIDTH - 10, BG_HEIGHT)

    # Draw outline first
    outline_color = ON_COLOR
    if not self._enabled:
        # Use a more subtle color for disabled state
        outline_color = rl.Color(outline_color.r // 2, outline_color.g // 2, outline_color.b // 2, 255)
    
    # Draw outline by drawing a slightly larger rounded rectangle behind the background
    outline_rect = rl.Rectangle(bg_rect.x - 2, bg_rect.y - 2, bg_rect.width + 4, bg_rect.height + 4)
    rl.draw_rectangle_rounded(outline_rect, 1.0, 10, outline_color)
    
    # Draw actual background
    rl.draw_rectangle_rounded(bg_rect, 1.0, 10, bg_color)

    # Draw knob to sit inside the background
    knob_padding = 5
    knob_radius = BG_HEIGHT / 2 - knob_padding

    left_edge = bg_rect.x + knob_padding
    right_edge = bg_rect.x + bg_rect.width - knob_padding

    knob_travel_distance = right_edge - left_edge - 2 * knob_radius
    min_knob_x = left_edge + knob_radius
    knob_x = min_knob_x + knob_travel_distance * self._progress
    knob_y = self._rect.y + HEIGHT / 2
    
    rl.draw_circle(int(knob_x), int(knob_y), knob_radius, knob_color)

    symbol_size = knob_radius / 2

    if self._state and (self._enabled or self._progress > 0.5):
        # Draw checkmark when toggle is ON
        start_x = knob_x - symbol_size * 0.8
        start_y = knob_y
        mid_x = knob_x - symbol_size * 0.1
        mid_y = knob_y + symbol_size * 0.6
        end_x = knob_x + symbol_size * 0.8
        end_y = knob_y - symbol_size * 0.5
        
        rl.draw_line_ex(
            rl.Vector2(int(start_x), int(start_y)),
            rl.Vector2(int(mid_x), int(mid_y)),
            3,
            ON_COLOR
        )
        rl.draw_line_ex(
            rl.Vector2(int(mid_x), int(mid_y)),
            rl.Vector2(int(end_x), int(end_y)),
            3,
            ON_COLOR
        )
    else:
        # Draw X when toggle is OFF
        x_size_factor = 0.65
        x_offset = symbol_size * x_size_factor
        
        rl.draw_line_ex(
            rl.Vector2(int(knob_x - x_offset), int(knob_y - x_offset)),
            rl.Vector2(int(knob_x + x_offset), int(knob_y + x_offset)),
            3,
            OFF_COLOR
        )
        rl.draw_line_ex(
            rl.Vector2(int(knob_x + x_offset), int(knob_y - x_offset)),
            rl.Vector2(int(knob_x - x_offset), int(knob_y + x_offset)),
            3,
            OFF_COLOR
        )
    return True
