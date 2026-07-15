"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import pyray as rl

RELATIVE_SPEED_COLOR_RANGE = 10.0  # m/s; speeds beyond this use the full endpoint color
APPROACHING_COLOR = (0, 128, 255)
NEUTRAL_COLOR = (255, 255, 255)
RECEDING_COLOR = (255, 32, 32)


def radar_track_color(v_rel: float) -> rl.Color:
  """Map relative speed from approaching blue through neutral white to receding red."""
  blend = min(abs(v_rel) / RELATIVE_SPEED_COLOR_RANGE, 1.0)
  target = APPROACHING_COLOR if v_rel < 0.0 else RECEDING_COLOR
  rgb = tuple(round(neutral + (endpoint - neutral) * blend) for neutral, endpoint in zip(NEUTRAL_COLOR, target, strict=True))
  return rl.Color(*rgb, 255)


def format_radar_tracks_onroad_status(live_tracks) -> str:
  range_text, count_text = format_radar_tracks_onroad_columns(live_tracks)
  if not range_text:
    return count_text

  return "\n".join(f"{radar_range} {track_count}" for radar_range, track_count in zip(range_text.splitlines(), count_text.splitlines(), strict=True))


def format_radar_tracks_onroad_columns(live_tracks) -> tuple[str, str]:
  sources = sorted(live_tracks.trackSources, key=lambda source: (source.startAddress, source.endAddress, source.bus))
  if not sources:
    return "", "none"

  range_text = "\n".join(f"{source.startAddress:X}-{source.endAddress:X}" for source in sources)
  count_text = "\n".join(str(source.trackCount) for source in sources)
  return range_text, count_text


class RadarTracks:
  def draw_radar_tracks(self, live_tracks, map_to_screen, path_offset_z, track_size=6, screen_offset=(0, 0)):
    for track in live_tracks.points:
      d_rel, y_rel, v_rel = track.dRel, track.yRel, track.vRel
      if not (math.isfinite(d_rel) and math.isfinite(y_rel) and math.isfinite(v_rel)):
        continue

      pt = map_to_screen(d_rel, -y_rel, path_offset_z)
      if pt is None:
        continue

      x, y = pt[0] + screen_offset[0], pt[1] + screen_offset[1]
      rl.draw_circle(int(x), int(y), track_size, radar_track_color(v_rel))
