"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import pyray as rl
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.label import UnifiedLabel

RELATIVE_SPEED_MOVING_THRESHOLD = 0.5  # m/s relative speed deadband
STATIONARY_SPEED_THRESHOLD = 1.0  # m/s estimated ground speed
APPROACHING_COLOR = (0, 140, 255)
NEUTRAL_COLOR = (255, 255, 255)
RECEDING_COLOR = (255, 45, 45)


def radar_track_color(v_rel: float, v_ego: float = 0.0) -> rl.Color:
  """Classify tracks as stationary, approaching, or receding with discrete colors."""
  if abs(v_ego + v_rel) <= STATIONARY_SPEED_THRESHOLD or abs(v_rel) <= RELATIVE_SPEED_MOVING_THRESHOLD:
    return rl.Color(*NEUTRAL_COLOR, 255)

  color = APPROACHING_COLOR if v_rel < 0.0 else RECEDING_COLOR
  return rl.Color(*color, 255)


def format_radar_tracks_onroad_columns(live_tracks) -> tuple[str, str]:
  sources = sorted(live_tracks.trackSources, key=lambda source: (source.startAddress, source.endAddress, source.bus))
  if not sources:
    return "", "none"

  range_text = "\n".join(f"{source.startAddress:X}-{source.endAddress:X}" for source in sources)
  count_text = "\n".join(str(source.trackCount) for source in sources)
  return range_text, count_text


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
      "text_color": rl.Color(0, 255, 64, 255),
      "alignment": rl.GuiTextAlignment.TEXT_ALIGN_RIGHT,
      "alignment_vertical": rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      "wrap_text": False,
    }
    self._ranges_label = UnifiedLabel("", **text_args)
    self._counts_label = UnifiedLabel("none", **text_args)
    self._status = ("", "none")
    self._layout_key: tuple[str, str, int] | None = None
    self._range_width = 0
    self._count_width = 36
    self._width = 52
    self._height = 42

  def update(self, live_tracks, valid: bool, radar_mode: int) -> None:
    if live_tracks.radarTracksAvailable and radar_mode != 2:
      status = ("", "radar detected\ntap to enable")
    else:
      status = format_radar_tracks_onroad_columns(live_tracks) if valid else ("", "none")
    self._set_status(status)

  def reset(self) -> None:
    self._set_status(("", "none"))

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
    self._ranges_label.render(rl.Rectangle(
      self._rect.x + self.HORIZONTAL_PADDING,
      self._rect.y + 5,
      self._range_width,
      self._rect.height - 10,
    ))
    self._counts_label.render(rl.Rectangle(
      self._rect.x + self.HORIZONTAL_PADDING + self._range_width + (self.COLUMN_GAP if self._range_width else 0),
      self._rect.y + 5,
      self._count_width,
      self._rect.height - 10,
    ))

  def _set_status(self, status: tuple[str, str]) -> None:
    if status == self._status:
      return

    self._status = status
    self._ranges_label.set_text(status[0])
    self._counts_label.set_text(status[1])
    self._layout_key = None

  def _update_layout(self, max_inner_width: int) -> None:
    layout_key = (*self._status, max_inner_width)
    if layout_key == self._layout_key:
      return

    self._ranges_label.get_content_height(max_inner_width - 36 - self.COLUMN_GAP)
    self._counts_label.get_content_height(max_inner_width)
    self._range_width = math.ceil(self._ranges_label.text_width)
    self._count_width = max(36, math.ceil(self._counts_label.text_width))
    inner_width = self._range_width + self._count_width + (self.COLUMN_GAP if self._range_width else 0)
    self._width = inner_width + self.HORIZONTAL_PADDING * 2
    self._height = max(
      42,
      self._ranges_label.get_content_height(max(self._range_width, 1)) + 10,
      self._counts_label.get_content_height(self._count_width) + 10,
    )
    self._layout_key = layout_key


class RadarTracks:
  def draw_radar_tracks(self, live_tracks, map_to_screen, path_offset_z, track_size=6, screen_offset=(0, 0), v_ego=0.0):
    for track in live_tracks.points:
      d_rel, y_rel, v_rel = track.dRel, track.yRel, track.vRel
      if not (math.isfinite(d_rel) and math.isfinite(y_rel) and math.isfinite(v_rel)):
        continue

      pt = map_to_screen(d_rel, -y_rel, path_offset_z)
      if pt is None:
        continue

      x, y = pt[0] + screen_offset[0], pt[1] + screen_offset[1]
      color = radar_track_color(v_rel, v_ego)
      neutral = (color.r, color.g, color.b) == NEUTRAL_COLOR
      rl.draw_circle(int(x), int(y), max(1, track_size - 3) if neutral else track_size, color)
