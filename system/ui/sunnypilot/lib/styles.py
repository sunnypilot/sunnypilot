import pyray as rl
from dataclasses import dataclass

@dataclass
class Base:
  # Widget/Control Base Dimensions
  ITEM_BASE_HEIGHT = 170
  ITEM_PADDING = 20
  ITEM_TEXT_FONT_SIZE = 50
  ITEM_DESC_FONT_SIZE = 40
  ITEM_DESC_V_OFFSET = 150

  # Toggle Control
  TOGGLE_HEIGHT = 100
  TOGGLE_WIDTH = int(TOGGLE_HEIGHT * 1.75)
  TOGGLE_BG_HEIGHT = TOGGLE_HEIGHT - 20

@dataclass
class SP_Default(Base):
  # Base Colors
  BASE_BG_COLOR = rl.Color(57, 57, 57, 255) # Grey
  ON_BG_COLOR = rl.Color(28, 101, 186, 255) # Blue
  OFF_BG_COLOR = BASE_BG_COLOR
  ON_HOVER_BG_COLOR = rl.Color(17, 78, 150, 255) # Dark Blue
  OFF_HOVER_BG_COLOR = rl.Color(21, 21, 21, 255)  # Dark gray
  DISABLED_ON_BG_COLOR = rl.Color(37, 70, 107, 255) # Dull Blue
  DISABLED_OFF_BG_COLOR = rl.Color(39, 39, 39, 255) # Grey
  ITEM_TEXT_COLOR = rl.WHITE
  ITEM_DISABLED_TEXT_COLOR = rl.Color(88, 88, 88, 255)
  ITEM_DESC_TEXT_COLOR = rl.Color(128, 128, 128, 255)

  # Toggle Control
  TOGGLE_ON_COLOR = ON_BG_COLOR
  TOGGLE_OFF_COLOR = OFF_BG_COLOR
  TOGGLE_KNOB_COLOR = rl.WHITE
  TOGGLE_DISABLED_ON_COLOR = DISABLED_ON_BG_COLOR
  TOGGLE_DISABLED_OFF_COLOR = DISABLED_OFF_BG_COLOR
  TOGGLE_DISABLED_KNOB_COLOR = rl.Color(88, 88, 88, 255) # Lighter Grey

style = SP_Default
