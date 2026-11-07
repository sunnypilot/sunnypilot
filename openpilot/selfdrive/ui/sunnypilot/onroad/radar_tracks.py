"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass
import math
import pyray as rl
from opendbc.car.hyundai.radar_interface import RADAR_235_248, RADAR_3A5_3C4

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
