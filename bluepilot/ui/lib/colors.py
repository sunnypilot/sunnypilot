"""
BluePilot Color Scheme for Raylib UI
Matches the Qt SidebarBP color palette
"""

import pyray as rl


class BPColors:
  """BluePilot color scheme matching Qt implementation exactly"""

  # Background colors (from Qt sidebar.h)
  BACKGROUND = rl.Color(32, 33, 35, 255)  # background_color from Qt
  BACKGROUND_DARKER = rl.Color(29, 30, 31, 255)  # 110% darker
  CARD_BACKGROUND = rl.Color(48, 49, 51, 255)  # card_background from Qt
  SIDEBAR_BG = rl.Color(57, 57, 57, 255)  # Stock sidebar background

  # Accent color (BluePilot blue - from Qt)
  ACCENT = rl.Color(24, 144, 255, 255)  # accent_color from Qt

  # Status colors (from Qt sidebar.h)
  GOOD = rl.Color(42, 199, 122, 255)  # good_color from Qt
  WARNING = rl.Color(255, 195, 0, 255)  # warning_color from Qt
  DANGER = rl.Color(242, 72, 85, 255)  # danger_color from Qt
  DISABLED = rl.Color(128, 128, 128, 255)  # disabled_color from Qt
  PROGRESS = rl.Color(3, 132, 252, 255)  # progress_color from Qt

  # Text colors (use explicit Color to avoid tuple issues with rl.WHITE)
  WHITE = rl.Color(255, 255, 255, 255)
  WHITE_DIM = rl.Color(255, 255, 255, 85)  # Semi-transparent white
  GRAY = rl.Color(84, 84, 84, 255)
  LIGHT_GRAY = rl.Color(200, 200, 200, 255)
  TEXT_SECONDARY = rl.Color(180, 180, 180, 255)

  # UI elements
  METRIC_BORDER = rl.Color(255, 255, 255, 85)  # Semi-transparent border
  BUTTON_NORMAL = rl.Color(255, 255, 255, 255)
  BUTTON_PRESSED = rl.Color(255, 255, 255, 166)
  BUTTON_BG = rl.Color(100, 110, 130, 140)
  BUTTON_BG_PRESSED = rl.Color(100, 110, 130, 180)
  SHADOW = rl.Color(0, 0, 0, 40)

  # Signal bar colors
  SIGNAL_ACTIVE = rl.Color(24, 144, 255, 255)  # accent_color from Qt
  SIGNAL_INACTIVE = rl.Color(120, 120, 120, 120)  # Gray for inactive

  # Badge colors (for version badges)
  BADGE_BRAND = rl.Color(74, 144, 226, 255)  # Blue - brand/version
  BADGE_BRANCH = rl.Color(155, 89, 182, 255)  # Purple - branch
  BADGE_COMMIT = rl.Color(230, 126, 34, 255)  # Orange - commit
  BADGE_DATE = rl.Color(149, 165, 166, 255)  # Gray - date

  # Onroad border colors
  BORDER_DISENGAGED = rl.Color(0x17, 0x33, 0x49, 0xC8)  # Blue
  BORDER_OVERRIDE = rl.Color(0x91, 0x9B, 0x95, 0xF1)  # Gray
  BORDER_ENGAGED = rl.Color(0x17, 0x86, 0x44, 0xF1)  # Green

  @staticmethod
  def with_alpha(color: rl.Color, alpha: int) -> rl.Color:
    """Create a new color with modified alpha"""
    return rl.Color(color.r, color.g, color.b, alpha)

  @staticmethod
  def darker(color: rl.Color, factor: float = 0.8) -> rl.Color:
    """Create a darker version of the color"""
    return rl.Color(
      int(color.r * factor),
      int(color.g * factor),
      int(color.b * factor),
      color.a
    )

  @staticmethod
  def lighter(color: rl.Color, factor: float = 1.2) -> rl.Color:
    """Create a lighter version of the color"""
    return rl.Color(
      min(255, int(color.r * factor)),
      min(255, int(color.g * factor)),
      min(255, int(color.b * factor)),
      color.a
    )
