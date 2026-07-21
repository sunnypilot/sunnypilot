"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass
import math
import pyray as rl
from opendbc.car.hyundai.radar_interface import RADAR_235_248, RADAR_3A5_3C4
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.label import UnifiedLabel

NEUTRAL_COLOR = (255, 255, 255)
DBC_MOVING_COLOR = (190, 125, 255)
DBC_UNKNOWN_COLOR = (154, 168, 184)
DBC_MOTION_STATIONARY = 1
DBC_MOTION_MOVING = 2
LEAD_TRACK_COLORS = (
  rl.Color(255, 215, 0, 255),
  rl.Color(255, 140, 0, 220),
)


@dataclass(frozen=True)
class ProjectedRadarTrack:
  x: float
  y: float
  radius: float
  color: object
  source_index: int
  camera_object: bool
  track_id: int


def is_preferred_radar_source(source) -> bool:
  return source.startAddress == RADAR_3A5_3C4.start_addr and source.endAddress == RADAR_3A5_3C4.end_addr


def radar_source_sort_key(source) -> tuple[bool, int, int, int]:
  return (
    not is_preferred_radar_source(source),
    int(source.startAddress),
    int(source.endAddress),
    int(source.bus),
  )


def sorted_radar_sources(live_tracks):
  return sorted(live_tracks.trackSources, key=radar_source_sort_key)


def radar_track_source_index(track, sources) -> int:
  address = int(track.sourceAddress)
  bus = int(track.sourceBus)
  if address != 0:
    return next((
      index for index, source in enumerate(sources)
      if source.startAddress <= address <= source.endAddress and source.bus == bus
    ), 0)
  return 0


def is_camera_object_source(source) -> bool:
  return source.startAddress == RADAR_235_248.start_addr and source.endAddress == RADAR_235_248.end_addr


def radar_track_source(track, sources):
  address = int(track.sourceAddress)
  bus = int(track.sourceBus)
  if address == 0:
    return None
  return next((
    source for source in sources
    if source.startAddress <= address <= source.endAddress and source.bus == bus
  ), None)


def radar_source_label(source) -> str:
  prefix = "CAM " if is_camera_object_source(source) else ""
  return f"{prefix}{source.startAddress:X}-{source.endAddress:X}"


def draw_radar_source_marker(center: rl.Vector2, radius: float, color: rl.Color, source_index: int,
                             camera_object: bool = False) -> None:
  if camera_object:
    rl.draw_poly(center, 3, radius, -90.0, color)
    return
  if source_index <= 0:
    rl.draw_circle(int(center.x), int(center.y), radius, color)
    return
  sides = (4, 3, 5, 6)[(source_index - 1) % 4]
  rotation = 45.0 if sides == 4 else -90.0
  rl.draw_poly(center, sides, radius, rotation, color)


def radar_track_display(motion_state: int) -> tuple[rl.Color, bool]:
  """Color tracks exclusively from the radar's DBC motion classification."""
  if motion_state == DBC_MOTION_STATIONARY:
    return rl.Color(*NEUTRAL_COLOR, 255), True
  if motion_state == DBC_MOTION_MOVING:
    return rl.Color(*DBC_MOVING_COLOR, 255), False
  return rl.Color(*DBC_UNKNOWN_COLOR, 255), False


def radar_lead_track_colors(radar_state) -> dict[int, rl.Color]:
  highlighted_tracks = {}
  if radar_state is None:
    return highlighted_tracks

  for lead, color in zip((radar_state.leadOne, radar_state.leadTwo), LEAD_TRACK_COLORS, strict=True):
    if lead.present and lead.radar and lead.radarTrackId >= 0:
      highlighted_tracks.setdefault(int(lead.radarTrackId), color)
  return highlighted_tracks


def draw_radar_lead_connectors(lead_vehicles, matched_positions, highlighted_tracks, screen_offset=(0, 0)) -> None:
  for lead in lead_vehicles:
    if not lead.radar or lead.position is None or lead.radar_track_id not in matched_positions:
      continue

    radar_position = matched_positions[lead.radar_track_id]
    lead_position = (lead.position[0] + screen_offset[0], lead.position[1] + screen_offset[1])
    if math.dist(lead_position, radar_position) < 4:
      continue

    rl.draw_line_ex(
      rl.Vector2(*lead_position), rl.Vector2(*radar_position), 2,
      highlighted_tracks[lead.radar_track_id],
    )


def format_radar_tracks_onroad_columns(live_tracks, v_ego: float = 0.0) -> tuple[str, str, str, str, str, str]:
  sources = sorted_radar_sources(live_tracks)
  if not sources:
    return "", "none", "", "", "", ""

  range_text = "\n".join(radar_source_label(source) for source in sources)
  count_text = "\n".join(str(source.trackCount) for source in sources)
  motion_states = [int(track.motionState) for track in live_tracks.points]

  moving_count = sum(state == DBC_MOTION_MOVING for state in motion_states)
  stationary_count = sum(state == DBC_MOTION_STATIONARY for state in motion_states)
  unknown_count = len(motion_states) - moving_count - stationary_count
  return range_text, count_text, str(moving_count), str(stationary_count), str(unknown_count), ""


class RadarTracksStatus:
  HORIZONTAL_PADDING = 8
  COLUMN_GAP = 8
  SOURCE_MARKER_WIDTH = 18

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
    self._source_count = 0
    self._layout_key: tuple[str, str, str, str, str, str, int] | None = None
    self._column_widths = [0, 36, 0, 0, 0, 0]
    self._width = 52
    self._height = 42

  def update(self, live_tracks, valid: bool, radar_mode: int, v_ego: float = 0.0) -> None:
    if live_tracks.radarTracksAvailable and radar_mode != 2:
      status = ("", "radar detected\ntap to enable", "", "", "", "")
      status_colors = ()
      source_count = 0
    else:
      status = format_radar_tracks_onroad_columns(live_tracks, v_ego) if valid else ("", "none", "", "", "", "")
      status_colors = (DBC_MOVING_COLOR, NEUTRAL_COLOR, DBC_UNKNOWN_COLOR, DBC_UNKNOWN_COLOR)
      source_count = len(live_tracks.trackSources) if valid else 0
    self._set_status(status, status_colors, source_count)

  def reset(self) -> None:
    self._set_status(("", "none", "", "", "", ""), (), 0)

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
    active_columns = [
      (column_index, label, width)
      for column_index, (label, width) in enumerate(zip(self._labels, self._column_widths, strict=True))
      if width
    ]
    for active_index, (column_index, label, width) in enumerate(active_columns):
      label_x = x
      label_width = width
      if column_index == 0 and self._source_count:
        marker_height = (self._rect.height - 10) / self._source_count
        for source_index in range(self._source_count):
          draw_radar_source_marker(
            rl.Vector2(x + 6, self._rect.y + 5 + marker_height * (source_index + 0.5)),
            5.0, rl.Color(0, 255, 64, 255), source_index,
          )
        label_x += self.SOURCE_MARKER_WIDTH
        label_width -= self.SOURCE_MARKER_WIDTH
      label.render(rl.Rectangle(label_x, self._rect.y + 5, label_width, self._rect.height - 10))
      x += width + (self.COLUMN_GAP if active_index < len(active_columns) - 1 else 0)

  def _set_status(self, status: tuple[str, str, str, str, str, str],
                  status_colors: tuple[tuple[int, int, int], ...], source_count: int) -> None:
    if status == self._status and status_colors == self._status_colors and source_count == self._source_count:
      return

    self._status = status
    self._status_colors = status_colors
    self._source_count = source_count
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
    if self._column_widths[0] and self._source_count:
      self._column_widths[0] += self.SOURCE_MARKER_WIDTH
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
  def __init__(self):
    self._projected_tracks: tuple[ProjectedRadarTrack, ...] = ()
    self._projection_initialized = False

  @property
  def projection_initialized(self) -> bool:
    return self._projection_initialized

  def clear_projection(self) -> None:
    self._projected_tracks = ()
    self._projection_initialized = False

  def update_radar_tracks(self, live_tracks, map_to_screen, path_offset_z, track_size=7) -> None:
    projected_tracks = []
    sources = sorted_radar_sources(live_tracks)

    for track in live_tracks.points:
      d_rel, y_rel, v_rel = track.dRel, track.yRel, track.vRel
      if not (math.isfinite(d_rel) and math.isfinite(y_rel) and math.isfinite(v_rel)):
        continue

      motion_state = int(track.motionState)
      if motion_state not in (DBC_MOTION_STATIONARY, DBC_MOTION_MOVING):
        continue

      pt = map_to_screen(d_rel, -y_rel, path_offset_z)
      if pt is None:
        continue

      color, stationary = radar_track_display(motion_state)
      radius = max(1, track_size - 5) if stationary else track_size
      source = radar_track_source(track, sources)
      projected_tracks.append(ProjectedRadarTrack(
        x=pt[0],
        y=pt[1],
        radius=radius,
        color=color,
        source_index=radar_track_source_index(track, sources),
        camera_object=source is not None and is_camera_object_source(source),
        track_id=int(track.trackId),
      ))

    self._projected_tracks = tuple(projected_tracks)
    self._projection_initialized = True

  def draw_cached_radar_tracks(self, screen_offset=(0, 0), highlighted_tracks=None):
    highlighted_tracks = highlighted_tracks or {}
    highlighted_positions = {}

    for track in self._projected_tracks:
      x, y = track.x + screen_offset[0], track.y + screen_offset[1]
      highlight_color = highlighted_tracks.get(track.track_id)
      if highlight_color is not None:
        center = rl.Vector2(int(x), int(y))
        rl.draw_ring(center, track.radius + 2, track.radius + 5, 0, 360, 24, highlight_color)
        highlighted_positions[track.track_id] = (x, y)
      draw_radar_source_marker(
        rl.Vector2(x, y), track.radius, track.color, track.source_index, track.camera_object,
      )

    return highlighted_positions

  def draw_radar_tracks(self, live_tracks, map_to_screen, path_offset_z, track_size=7, screen_offset=(0, 0), v_ego=0.0,
                        highlighted_tracks=None):
    self.update_radar_tracks(live_tracks, map_to_screen, path_offset_z, track_size)
    return self.draw_cached_radar_tracks(screen_offset, highlighted_tracks)
