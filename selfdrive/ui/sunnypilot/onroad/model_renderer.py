"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.onroad.chevron_metrics import ChevronMetrics
from openpilot.selfdrive.ui.sunnypilot.onroad.rainbow_path import RainbowPath
from openpilot.selfdrive.ui.sunnypilot.onroad.radar_tracks import RadarTracks


class ModelRendererSP:
  def __init__(self):
    self.rainbow_path = RainbowPath()
    self.chevron_metrics = ChevronMetrics()
    self.radar_tracks = RadarTracks()

  def _draw_radar_tracks(self, live_tracks, track_size=6):
    self.radar_tracks.draw_radar_tracks(live_tracks, self._map_to_screen, self._path_offset_z, track_size)
