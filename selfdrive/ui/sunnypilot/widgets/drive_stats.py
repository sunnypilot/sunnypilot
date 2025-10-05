"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import json
import pyray as rl
from typing import Dict, Optional

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import gui_label
from openpilot.tools.lib.api import CommaApi
from openpilot.common.params import Params

import openpilot.system.ui.sunnypilot.lib.styles as styles
style = styles.Default

MILE_TO_KM = 1.609344

class DriveStatsWidget(Widget):
  """Widget for displaying driving statistics"""

  BG_COLOR = style.BASE_BG_COLOR
  TEXT_COLOR = rl.WHITE
  SECONDARY_TEXT_COLOR = style.ITEM_DESC_TEXT_COLOR

  def __init__(self):
    super().__init__()
    self.stats = {"all": {"routes": 0, "distance": 0, "minutes": 0},
                  "week": {"routes": 0, "distance": 0, "minutes": 0}}
    self.metric = Params().get_bool("IsMetric")
    self.api_client = CommaApi()
    self.last_fetch_time = 0
    self.fetch_interval = 30  # 30 seconds between fetches

    # Initial fetch
    self._fetch_stats()

  def _fetch_stats(self):
    """Fetch driving statistics from the API"""
    dongle_id = Params().get("DongleId")
    if dongle_id:
      url = f"v1.1/devices/{dongle_id}/stats"
      try:
        response = self.api_client.get(url)
        self._handle_response(response.text, response.status_code)
      except Exception as e:
        print(f"Exception fetching drive stats for dongle id {dongle_id}: {e}")

  def _handle_response(self, response_text, status_code):
    """Handle API response for drive statistics"""
    if status_code != 200:
      print(f"Error fetching drive stats: {status_code}")
      return

    try:
      response = json.loads(response_text)
      self.stats = response
    except json.JSONDecodeError:
      print("Failed to parse drive stats response")

  def _get_distance_unit(self):
    """Get the distance unit based on metric setting"""
    return "km" if self.metric else "mi"

  def _render_stats_section(self, rect: rl.Rectangle, title: str, stats_data: Dict):
    """Render a stats section (All Time or Past Week)"""
    x, y = rect.x, rect.y
    width = rect.width

    # Title
    gui_label(rl.Rectangle(x, y, width, 51), title, 51, font_weight=FontWeight.MEDIUM)
    y += 80  # Move down after title

    # Calculate values
    routes = int(stats_data.get("routes", 0))
    distance = int(stats_data.get("distance", 0) * (MILE_TO_KM if self.metric else 1))
    hours = int(stats_data.get("minutes", 0) / 60)

    # Layout for values and labels
    column_width = width / 3

    # Draw values
    font_bold = gui_app.font(FontWeight.MEDIUM)
    font_light = gui_app.font(FontWeight.LIGHT)

    # Routes column
    rl.draw_text_ex(font_bold, str(routes), rl.Vector2(x, y), 78, 0, self.TEXT_COLOR)
    rl.draw_text_ex(font_light, "Drives", rl.Vector2(x, y + 85), 51, 0, self.SECONDARY_TEXT_COLOR)

    # Distance column
    rl.draw_text_ex(font_bold, str(distance), rl.Vector2(x + column_width, y), 78, 0, self.TEXT_COLOR)
    rl.draw_text_ex(font_light, self._get_distance_unit(), rl.Vector2(x + column_width, y + 85), 51, 0, self.SECONDARY_TEXT_COLOR)

    # Hours column
    rl.draw_text_ex(font_bold, str(hours), rl.Vector2(x + column_width * 2, y), 78, 0, self.TEXT_COLOR)
    rl.draw_text_ex(font_light, "Hours", rl.Vector2(x + column_width * 2, y + 85), 51, 0, self.SECONDARY_TEXT_COLOR)

    # Return the height of this section
    return 160  # Approximate height of the section

  def _render(self, rect):
    """Main render method"""
    # Check if we need to update stats
    current_time = rl.get_time()
    if current_time - self.last_fetch_time >= self.fetch_interval:
      self._fetch_stats()
      self.last_fetch_time = current_time

    # Check if metric setting has changed
    current_metric = Params().get_bool("IsMetric")
    if self.metric != current_metric:
      self.metric = current_metric

    # Draw background
    rl.draw_rectangle_rounded(rect, 0.02, 10, self.BG_COLOR)

    # Content margins
    content_rect = rl.Rectangle(
      rect.x + 50,  # left margin
      rect.y + 50,  # top margin
      rect.width - 100,  # width with margins
      rect.height - 110   # height with margins
    )

    # Render all time stats
    all_time_rect = rl.Rectangle(content_rect.x, content_rect.y, content_rect.width, 0)
    all_time_height = self._render_stats_section(all_time_rect, "ALL TIME", self.stats.get("all", {}))

    # Space between sections
    spacing = 200

    # Render past week stats
    week_rect = rl.Rectangle(
      content_rect.x, 
      content_rect.y + all_time_height + spacing, 
      content_rect.width, 
      0
    )
    self._render_stats_section(week_rect, "PAST WEEK", self.stats.get("week", {}))
