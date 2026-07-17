"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import pyray as rl
from opendbc.car.hyundai.radar_interface import RADAR_3A5_3C4
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.label import UnifiedLabel

NEUTRAL_COLOR = (255, 255, 255)
DBC_MOVING_COLOR = (190, 125, 255)
DBC_UNKNOWN_COLOR = (154, 168, 184)
DBC_MOTION_STATIONARY = 1
DBC_MOTION_MOVING = 2


def is_preferred_radar_source(source) -> bool:
  return source.startAddress == RADAR_3A5_3C4.start_addr and source.endAddress == RADAR_3A5_3C4.end_addr


def preferred_radar_tracks(live_tracks):
  points = list(live_tracks.points)
  if any(int(track.sourceAddress) != 0 for track in points):
    return [
      track for track in points
      if RADAR_3A5_3C4.start_addr <= int(track.sourceAddress) <= RADAR_3A5_3C4.end_addr
    ]

  # Legacy messages have no per-point source metadata. They are unambiguous only
  # when 3A5-3C4 is the sole reported source (or tests provide no source list).
  sources = list(live_tracks.trackSources)
  if not sources or all(is_preferred_radar_source(source) for source in sources):
    return points
  return []


def radar_track_display(motion_state: int) -> tuple[rl.Color, bool]:
  """Color tracks exclusively from the radar's DBC motion classification."""
  if motion_state == DBC_MOTION_STATIONARY:
    return rl.Color(*NEUTRAL_COLOR, 255), True
  if motion_state == DBC_MOTION_MOVING:
    return rl.Color(*DBC_MOVING_COLOR, 255), False
  return rl.Color(*DBC_UNKNOWN_COLOR, 255), False


def format_radar_tracks_onroad_columns(live_tracks, v_ego: float = 0.0) -> tuple[str, str, str, str, str, str]:
  sources = sorted(
    (source for source in live_tracks.trackSources if is_preferred_radar_source(source)),
    key=lambda source: (source.startAddress, source.endAddress, source.bus),
  )
  if not sources:
    return "", "none", "", "", "", ""

  range_text = "\n".join(f"{source.startAddress:X}-{source.endAddress:X}" for source in sources)
  count_text = "\n".join(str(source.trackCount) for source in sources)
  motion_states = [int(track.motionState) for track in preferred_radar_tracks(live_tracks)]

  moving_count = sum(state == DBC_MOTION_MOVING for state in motion_states)
  stationary_count = sum(state == DBC_MOTION_STATIONARY for state in motion_states)
  unknown_count = len(motion_states) - moving_count - stationary_count
  return range_text, count_text, str(moving_count), str(stationary_count), str(unknown_count), ""


class RadarTracksStatus:
  HORIZONTAL_PADDING = 8
  COLUMN_GAP = 8

  def __init__(self, settings_callback=None, right_margin: int = 12):
    self._settings_callback = settings_callback
    self._right_margin = right_margin
    self._rect = rl.Rectangle()
    text_args = {
      "font_size": 26,
      "font_weight": FontWeight.SEMI_BOLD,
      "alignment": rl.GuiTextAlignment.TEXT_ALIGN_RIGHT,
      "alignment_vertical": rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      "wrap_text": False,
    }
    self._labels = (
      UnifiedLabel("", text_color=rl.Color(0, 255, 64, 255), **text_args),
      UnifiedLabel("none", text_color=rl.Color(0, 255, 64, 255), **text_args),
      UnifiedLabel("", text_color=rl.Color(*DBC_MOVING_COLOR, 255), **text_args),
      UnifiedLabel("", text_color=rl.Color(*NEUTRAL_COLOR, 255), **text_args),
      UnifiedLabel("", text_color=rl.Color(*DBC_UNKNOWN_COLOR, 255), **text_args),
      UnifiedLabel("", text_color=rl.Color(*DBC_UNKNOWN_COLOR, 255), **text_args),
    )
    self._status = ("", "none", "", "", "", "")
    self._status_colors: tuple[tuple[int, int, int], ...] = ()
    self._layout_key: tuple[str, str, str, str, str, str, int] | None = None
    self._column_widths = [0, 36, 0, 0, 0, 0]
    self._width = 52
    self._height = 42

  def update(self, live_tracks, valid: bool, radar_mode: int, v_ego: float = 0.0) -> None:
    if live_tracks.radarTracksAvailable and radar_mode != 2:
      status = ("", "radar detected\ntap to enable", "", "", "", "")
      status_colors = ()
    else:
      status = format_radar_tracks_onroad_columns(live_tracks, v_ego) if valid else ("", "none", "", "", "", "")
      status_colors = (DBC_MOVING_COLOR, NEUTRAL_COLOR, DBC_UNKNOWN_COLOR, DBC_UNKNOWN_COLOR)
    self._set_status(status, status_colors)

  def reset(self) -> None:
    self._set_status(("", "none", "", "", "", ""), ())

  def handle_mouse(self, mouse_pos) -> bool:
    if self._settings_callback is None or not rl.check_collision_point_rec(mouse_pos, self._rect):
      return False

    self._settings_callback()
    return True

  def render(self, content_rect: rl.Rectangle) -> None:
    self._update_layout(int(content_rect.width - 40))
    self._rect = rl.Rectangle(
      content_rect.x + content_rect.width - self._width - self._right_margin,
      content_rect.y + 8,
      self._width,
      self._height,
    )
    rl.draw_rectangle_rounded(self._rect, 0.5, 8, rl.Color(0, 0, 0, 170))
    x = self._rect.x + self.HORIZONTAL_PADDING
    active_columns = [(label, width) for label, width in zip(self._labels, self._column_widths, strict=True) if width]
    for index, (label, width) in enumerate(active_columns):
      label.render(rl.Rectangle(x, self._rect.y + 5, width, self._rect.height - 10))
      x += width + (self.COLUMN_GAP if index < len(active_columns) - 1 else 0)

  def _set_status(self, status: tuple[str, str, str, str, str, str],
                  status_colors: tuple[tuple[int, int, int], ...]) -> None:
    if status == self._status and status_colors == self._status_colors:
      return

    self._status = status
    self._status_colors = status_colors
    for label, text in zip(self._labels, status, strict=True):
      label.set_text(text)
    for label, color in zip(self._labels[2:], status_colors, strict=False):
      label.set_text_color(rl.Color(*color, 255))
    self._layout_key = None

  def _update_layout(self, max_inner_width: int) -> None:
    layout_key = (*self._status, max_inner_width)
    if layout_key == self._layout_key:
      return

    for label in self._labels:
      label.get_content_height(max_inner_width)
    self._column_widths = [
      math.ceil(label.text_width) if text else 0
      for label, text in zip(self._labels, self._status, strict=True)
    ]
    self._column_widths[1] = max(36, self._column_widths[1])
    for index in (2, 3, 4):
      if self._column_widths[index]:
        self._column_widths[index] = max(36, self._column_widths[index])
    active_widths = [width for width in self._column_widths if width]
    inner_width = sum(active_widths) + self.COLUMN_GAP * (len(active_widths) - 1)
    self._width = inner_width + self.HORIZONTAL_PADDING * 2
    self._height = max(
      42,
      *(label.get_content_height(max(width, 1)) + 10
        for label, width in zip(self._labels, self._column_widths, strict=True) if width),
    )
    self._layout_key = layout_key


class RadarTracks:
  def draw_radar_tracks(self, live_tracks, map_to_screen, path_offset_z, track_size=7, screen_offset=(0, 0), v_ego=0.0,
                        highlighted_tracks=None):
    highlighted_tracks = highlighted_tracks or {}
    highlighted_positions = {}

    for track in preferred_radar_tracks(live_tracks):
      d_rel, y_rel, v_rel = track.dRel, track.yRel, track.vRel
      if not (math.isfinite(d_rel) and math.isfinite(y_rel) and math.isfinite(v_rel)):
        continue

      pt = map_to_screen(d_rel, -y_rel, path_offset_z)
      if pt is None:
        continue

      x, y = pt[0] + screen_offset[0], pt[1] + screen_offset[1]
      color, stationary = radar_track_display(int(track.motionState))
      radius = max(1, track_size - 4) if stationary else track_size
      track_id = int(track.trackId)
      highlight_color = highlighted_tracks.get(track_id)
      if highlight_color is not None:
        center = rl.Vector2(int(x), int(y))
        rl.draw_ring(center, radius + 2, radius + 5, 0, 360, 24, highlight_color)
        highlighted_positions[track_id] = (x, y)
      rl.draw_circle(int(x), int(y), radius, color)

    return highlighted_positions
