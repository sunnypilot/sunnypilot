"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.ui_state import UIStatus

BORDER_COLORS_SP = {
  UIStatus.LAT_ONLY: rl.Color(0x00, 0xC8, 0xC8, 0xFF),  # Cyan for lateral-only state
  UIStatus.LONG_ONLY: rl.Color(0x96, 0x1C, 0xA8, 0xFF),  # Purple for longitudinal-only state
}
