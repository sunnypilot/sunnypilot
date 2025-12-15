"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass

import pyray as rl


@dataclass
class Base:
  # Widget/Control Base Dimensions
  ITEM_BASE_HEIGHT = 170
  ITEM_PADDING = 20
  ITEM_TEXT_FONT_SIZE = 50
  ITEM_DESC_FONT_SIZE = 40
  ITEM_DESC_V_OFFSET = 150
  ITEM_TEXT_VALUE_COLOR = rl.Color(170, 170, 170, 255)
  CLOSE_BTN_SIZE = 160

  TEXT_PADDING = 20

  # Toggle Control
  TOGGLE_HEIGHT = 120
  TOGGLE_WIDTH = int(TOGGLE_HEIGHT * 1.75)
  TOGGLE_BG_HEIGHT = TOGGLE_HEIGHT - 20

  # Button Control
  BUTTON_ACTION_WIDTH = 300
  BUTTON_HEIGHT = 120

  # Simple Button Control
  SIMPLE_BUTTON_WIDTH = 800
  SIMPLE_BUTTON_HEIGHT = 150


@dataclass
class DefaultStyleSP(Base):
  # Base Colors
  BASE_BG_COLOR = rl.Color(57, 57, 57, 255)  # Grey
  ON_BG_COLOR = rl.Color(28, 101, 186, 255)  # Blue
  OFF_BG_COLOR = BASE_BG_COLOR
  ON_HOVER_BG_COLOR = rl.Color(17, 78, 150, 255)  # Dark Blue
  OFF_HOVER_BG_COLOR = rl.Color(21, 21, 21, 255)  # Dark gray
  DISABLED_ON_BG_COLOR = rl.Color(37, 70, 107, 255)  # Dull Blue
  DISABLED_OFF_BG_COLOR = rl.Color(39, 39, 39, 255)  # Grey
  ITEM_TEXT_COLOR = rl.WHITE
  ITEM_DISABLED_TEXT_COLOR = rl.Color(88, 88, 88, 255)
  ITEM_DESC_TEXT_COLOR = rl.Color(128, 128, 128, 255)

  # Toggle Control
  TOGGLE_ON_COLOR = ON_BG_COLOR
  TOGGLE_OFF_COLOR = OFF_BG_COLOR
  TOGGLE_KNOB_COLOR = rl.WHITE
  TOGGLE_DISABLED_ON_COLOR = DISABLED_ON_BG_COLOR
  TOGGLE_DISABLED_OFF_COLOR = DISABLED_OFF_BG_COLOR
  TOGGLE_DISABLED_KNOB_COLOR = rl.Color(88, 88, 88, 255)  # Lighter Grey

  # Multi Button Control
  MBC_TRANSPARENT = rl.Color(255, 255, 255, 0)
  MBC_BG_CHECKED_ENABLED = rl.Color(0x69, 0x68, 0x68, 0xFF)
  MBC_DISABLED = rl.Color(0xFF, 0xFF, 0xFF, 0x33)

  # Option Control
  OPTION_CONTROL_CONTAINER_BG = OFF_BG_COLOR
  OPTION_CONTROL_BTN_ENABLED = rl.Color(88, 88, 88, 255)
  OPTION_CONTROL_BTN_PRESSED = rl.Color(0x69, 0x68, 0x68, 0xFF)
  OPTION_CONTROL_BTN_DISABLED = DISABLED_OFF_BG_COLOR
  OPTION_CONTROL_TEXT_ENABLED = rl.WHITE
  OPTION_CONTROL_TEXT_PRESSED = rl.WHITE
  OPTION_CONTROL_TEXT_DISABLED = ITEM_DISABLED_TEXT_COLOR

  # Tree Button Colors
  BUTTON_PRIMARY_COLOR = rl.Color(70, 91, 234, 255)  # Royal Blue
  BUTTON_NEUTRAL_GRAY = rl.Color(51, 51, 51, 255)
  BUTTON_DISABLED_BG_COLOR = rl.Color(30, 30, 30, 255)  # Very Dark Grey
  TREE_DIALOG_TRANSPARENT = rl.Color(0, 0, 0, 0)
  TREE_DIALOG_SEARCH_BUTTON_PRESSED = rl.Color(0x69, 0x68, 0x68, 0xFF)
  TREE_DIALOG_SEARCH_BUTTON_BORDER = rl.Color(150, 150, 150, 200)

  # Vehicle Description Colors
  GREEN = rl.Color(0, 241, 0, 255)
  BLUE = rl.Color(0, 134, 233, 255)
  YELLOW = rl.Color(255, 213, 0, 255)

  # Button Colors
  BUTTON_ENABLED_OFF = rl.Color(0x39, 0x39, 0x39, 0xFF)
  BUTTON_OFF_PRESSED = rl.Color(0x4A, 0x4A, 0x4A, 0xFF)
  BUTTON_DISABLED = rl.Color(0x12, 0x12, 0x12, 0xFF)
  BUTTON_TEXT_DISABLED = rl.Color(0x5C, 0x5C, 0x5C, 0xFF)


style = DefaultStyleSP
