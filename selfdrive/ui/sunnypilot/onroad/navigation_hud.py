"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

if TYPE_CHECKING:
  from pyray import Texture2D

ASSETS_PATH = Path(__file__).parents[4] / "sunnypilot" / "selfdrive" / "assets" / "navigation"

ICON_MAP = {
  "turn|uturn": "direction_uturn.png",
  "turn|sharp right": "direction_turn_sharp_right.png",
  "turn|right": "direction_turn_right.png",
  "turn|slight right": "direction_turn_slight_right.png",
  "turn|straight": "direction_turn_straight.png",
  "turn|slight left": "direction_turn_slight_left.png",
  "turn|left": "direction_turn_left.png",
  "turn|sharp left": "direction_turn_sharp_left.png",
  "arrive|right": "direction_arrive_right.png",
  "arrive|straight": "direction_arrive_straight.png",
  "arrive|left": "direction_arrive_left.png",
  "arrive|": "direction_arrive.png",
  "merge|slight right": "direction_merge_slight_right.png",
  "merge|right": "direction_merge_right.png",
  "merge|straight": "direction_merge_straight.png",
  "merge|slight left": "direction_merge_slight_left.png",
  "merge|left": "direction_merge_left.png",
  "on ramp|sharp right": "direction_on_ramp_sharp_right.png",
  "on ramp|right": "direction_on_ramp_right.png",
  "on ramp|slight right": "direction_on_ramp_slight_right.png",
  "on ramp|straight": "direction_on_ramp_straight.png",
  "on ramp|slight left": "direction_on_ramp_slight_left.png",
  "on ramp|left": "direction_on_ramp_left.png",
  "on ramp|sharp left": "direction_on_ramp_sharp_left.png",
  "off ramp|slight right": "direction_off_ramp_slight_right.png",
  "off ramp|right": "direction_off_ramp_right.png",
  "off ramp|slight left": "direction_off_ramp_slight_left.png",
  "off ramp|left": "direction_off_ramp_left.png",
  "roundabout|sharp right": "direction_roundabout_sharp_right.png",
  "roundabout|right": "direction_roundabout_right.png",
  "roundabout|slight right": "direction_roundabout_slight_right.png",
  "roundabout|straight": "direction_roundabout_straight.png",
  "roundabout|slight left": "direction_roundabout_slight_left.png",
  "roundabout|left": "direction_roundabout_left.png",
  "roundabout|sharp left": "direction_roundabout_sharp_left.png",
  "roundabout|": "direction_roundabout.png",
}

CONTAINER_WIDTH = 1080
CONTAINER_HEIGHT = 225
CONTAINER_Y = 62
BORDER_RADIUS = 42
ICON_SIZE = 150
ICON_PADDING = 30
THEN_SECTION_WIDTH = 180
THEN_ICON_SIZE = 105


class NavigationHudRenderer(Widget):
  def __init__(self):
    super().__init__()
    self._font_bold = gui_app.font(FontWeight.BOLD)
    self._font_medium = gui_app.font(FontWeight.MEDIUM)
    self._icons: dict[str, rl.Texture2D] = {}
    self._valid = False
    self._street = ""
    self._distance = ""
    self._maneuver_type = ""
    self._modifier = ""
    self._next_maneuver_type = ""
    self._next_modifier = ""
    self._has_next = False
    self._debug_info = ""

  def _get_icon(self, maneuver_type: str, modifier: str) -> Texture2D | None:
    normalized_type = maneuver_type
    if normalized_type == "rotary":
      normalized_type = "roundabout"
    elif normalized_type in ("new name", "continue"):
      normalized_type = "turn"

    icon_name = None
    for key in [f"{normalized_type}|{modifier}", f"{normalized_type}|", f"turn|{modifier}"]:
      icon_name = ICON_MAP.get(key)
      if icon_name:
        break
    if not icon_name:
      icon_name = "direction_turn_straight.png"

    if icon_name not in self._icons:
      icon_path = ASSETS_PATH / icon_name
      if icon_path.exists():
        self._icons[icon_name] = rl.load_texture(str(icon_path))
      else:
        return None
    return self._icons.get(icon_name)

  def _format_distance(self, dist: float, is_metric: bool) -> str:
    if is_metric:
      if dist < 1000:
        if dist < 500:
          return f"{round(dist / 25) * 25} m"
        return f"{round(dist / 50) * 50} m"
      dist_km = dist / 1000
      if dist_km >= 10.0:
        return f"{math.floor(dist_km)} km"
      return f"{dist_km:.1f} km"
    else:
      dist_ft = dist * 3.28084
      if dist_ft < 1000:
        if dist_ft <= 100:
          return f"{round(dist_ft / 10) * 10} ft"
        return f"{round(dist_ft / 50) * 50} ft"
      dist_mi = dist_ft / 5280
      if dist_mi >= 10.0:
        return f"{math.floor(dist_mi)} mi"
      return f"{dist_mi:.1f} mi"

  def _update_state(self) -> None:
    sm = ui_state.sm
    if "navigationd" not in sm.data:
      self._debug_info = "NAV: not subscribed"
      self._valid = False
      return

    recv_frame = sm.recv_frame.get("navigationd", 0)
    if recv_frame < ui_state.started_frame:
      self._debug_info = f"NAV: no msg (frame {recv_frame} < {ui_state.started_frame})"
      self._valid = False
      return

    nav = sm["navigationd"]
    if not nav.valid:
      self._debug_info = f"NAV: invalid (maneuvers={len(nav.allManeuvers)})"
      self._valid = False
      return

    if len(nav.allManeuvers) == 0:
      self._debug_info = "NAV: no maneuvers"
      self._valid = False
      return

    self._debug_info = f"NAV: OK ({len(nav.allManeuvers)} maneuvers)"
    self._valid = True

    curr_idx = 1 if len(nav.allManeuvers) > 1 else 0
    maneuver = nav.allManeuvers[curr_idx]

    self._modifier = maneuver.modifier
    self._maneuver_type = maneuver.type
    self._distance = self._format_distance(maneuver.distance, ui_state.is_metric)

    instruction = maneuver.instruction
    parts = instruction.split(" onto ")
    self._street = parts[1].strip() if len(parts) > 1 else instruction
    self._street = self._street.replace(".", "")

    if len(nav.allManeuvers) > 2:
      next_maneuver = nav.allManeuvers[2]
      self._next_modifier = next_maneuver.modifier
      self._next_maneuver_type = next_maneuver.type
      self._has_next = True
    else:
      self._has_next = False

  def _render(self, rect: rl.Rectangle) -> None:
    # Always show debug info at bottom left
    if self._debug_info:
      rl.draw_text_ex(self._font_medium, self._debug_info, rl.Vector2(20, rect.height - 60), 36, 0, rl.Color(255, 255, 0, 200))

    if not self._valid:
      return

    container_x = int((rect.width - CONTAINER_WIDTH) / 2)
    container_rect = rl.Rectangle(container_x, CONTAINER_Y, CONTAINER_WIDTH, CONTAINER_HEIGHT)
    rl.draw_rectangle_rounded(container_rect, BORDER_RADIUS / CONTAINER_HEIGHT, 10, rl.Color(0, 0, 0, 180))

    icon_x = container_x + ICON_PADDING
    icon_y = CONTAINER_Y + (CONTAINER_HEIGHT - ICON_SIZE - 38) // 2

    icon = self._get_icon(self._maneuver_type, self._modifier)
    if icon and icon.id > 0:
      dest_rect = rl.Rectangle(icon_x, icon_y, ICON_SIZE, ICON_SIZE)
      source_rect = rl.Rectangle(0, 0, icon.width, icon.height)
      rl.draw_texture_pro(icon, source_rect, dest_rect, rl.Vector2(0, 0), 0, rl.WHITE)

    distance_y = icon_y + ICON_SIZE + 5
    distance_size = measure_text_cached(self._font_bold, self._distance, 48)
    distance_x = icon_x + (ICON_SIZE - distance_size.x) / 2
    rl.draw_text_ex(self._font_bold, self._distance, rl.Vector2(distance_x, distance_y), 48, 0, rl.WHITE)

    text_x = icon_x + ICON_SIZE + 53
    text_area_width = CONTAINER_WIDTH - (text_x - container_x) - ICON_PADDING - THEN_SECTION_WIDTH

    street_y = CONTAINER_Y + (CONTAINER_HEIGHT - 75) // 2
    self._draw_wrapped_text(self._street, text_x, street_y, text_area_width, 75)

    if self._has_next:
      divider_x = container_x + CONTAINER_WIDTH - THEN_SECTION_WIDTH - 8
      rl.draw_line_ex(
        rl.Vector2(divider_x, CONTAINER_Y + 23),
        rl.Vector2(divider_x, CONTAINER_Y + CONTAINER_HEIGHT - 23),
        2,
        rl.Color(255, 255, 255, 50)
      )

      then_x = divider_x + 15
      then_label = "Then"
      then_size = measure_text_cached(self._font_medium, then_label, 53)
      then_label_x = then_x + (THEN_SECTION_WIDTH - 23 - then_size.x) / 2
      rl.draw_text_ex(self._font_medium, then_label, rl.Vector2(then_label_x, CONTAINER_Y + 30), 53, 0, rl.WHITE)

      next_icon = self._get_icon(self._next_maneuver_type, self._next_modifier)
      if next_icon and next_icon.id > 0:
        then_icon_x = then_x + (THEN_SECTION_WIDTH - 23 - THEN_ICON_SIZE) / 2
        then_icon_y = CONTAINER_Y + 75
        dest_rect = rl.Rectangle(then_icon_x, then_icon_y, THEN_ICON_SIZE, THEN_ICON_SIZE)
        source_rect = rl.Rectangle(0, 0, next_icon.width, next_icon.height)
        rl.draw_texture_pro(next_icon, source_rect, dest_rect, rl.Vector2(0, 0), 0, rl.WHITE)

  def _draw_wrapped_text(self, text: str, x: int, y: int, max_width: int, font_size: int) -> None:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
      test_line = f"{current_line} {word}".strip() if current_line else word
      text_width = measure_text_cached(self._font_bold, test_line, font_size).x
      if text_width <= max_width:
        current_line = test_line
      else:
        if current_line:
          lines.append(current_line)
        current_line = word
        if len(lines) >= 2:
          break

    if current_line and len(lines) < 2:
      lines.append(current_line)

    if len(lines) == 1:
      text_y = y
    else:
      text_y = CONTAINER_Y + 23

    for i, line in enumerate(lines[:2]):
      rl.draw_text_ex(self._font_bold, line, rl.Vector2(x, text_y + i * font_size), font_size, 0, rl.WHITE)
