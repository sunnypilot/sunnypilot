"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.layouts.home import HomeLayout
from openpilot.selfdrive.ui.sunnypilot.widgets.drive_stats import DriveStatsWidget


class HomeLayoutSP(HomeLayout):
  def __init__(self):
    super().__init__()
    self._drive_stats_widget = DriveStatsWidget()

  def _render_left_column(self):
    self._drive_stats_widget.render(self.left_column_rect)