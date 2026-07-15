from cereal import car

from openpilot.selfdrive.ui.sunnypilot.onroad import radar_tracks
from openpilot.selfdrive.ui.sunnypilot.onroad.radar_tracks import format_radar_tracks_onroad_columns, radar_track_color


def color_tuple(color):
  return color.r, color.g, color.b, color.a


def test_radar_track_relative_speed_colors():
  assert color_tuple(radar_track_color(-10.0)) == (0, 140, 255, 255)
  assert color_tuple(radar_track_color(0.0)) == (255, 255, 255, 255)
  assert color_tuple(radar_track_color(10.0)) == (255, 45, 45, 255)
  assert color_tuple(radar_track_color(-5.0)) == (0, 140, 255, 255)
  assert color_tuple(radar_track_color(5.0)) == (255, 45, 45, 255)


def test_radar_track_relative_speed_deadband_is_green():
  assert color_tuple(radar_track_color(-0.5, v_ego=10.0)) == (0, 255, 64, 255)
  assert color_tuple(radar_track_color(0.5, v_ego=10.0)) == (0, 255, 64, 255)
  assert color_tuple(radar_track_color(-0.51, v_ego=10.0)) == (0, 140, 255, 255)
  assert color_tuple(radar_track_color(0.51, v_ego=10.0)) == (255, 45, 45, 255)


def test_radar_track_stationary_world_object_is_white():
  assert color_tuple(radar_track_color(-20.0, v_ego=20.0)) == (255, 255, 255, 255)
  assert color_tuple(radar_track_color(-19.0, v_ego=20.0)) == (255, 255, 255, 255)
  assert color_tuple(radar_track_color(-18.9, v_ego=20.0)) == (0, 140, 255, 255)


def test_format_radar_tracks_columns_none():
  live_tracks = car.RadarData.new_message()

  assert format_radar_tracks_onroad_columns(live_tracks) == ("", "none")


def test_format_radar_tracks_columns_range_and_count():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x500, "endAddress": 0x51F, "bus": 1, "trackCount": 2}]
  live_tracks.init("points", 2)

  assert format_radar_tracks_onroad_columns(live_tracks) == ("500-51F", "2")


def test_format_radar_tracks_columns_sorts_ranges():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [
    {"startAddress": 0x500, "endAddress": 0x51F, "bus": 2, "trackCount": 3},
    {"startAddress": 0x210, "endAddress": 0x21F, "bus": 1, "trackCount": 1},
    {"startAddress": 0x500, "endAddress": 0x51F, "bus": 0, "trackCount": 2},
  ]
  live_tracks.init("points", 1)

  assert format_radar_tracks_onroad_columns(live_tracks) == (
    "210-21F\n500-51F\n500-51F",
    "1\n2\n3",
  )


def test_draw_radar_tracks_applies_screen_offset(monkeypatch):
  live_tracks = car.RadarData.new_message()
  points = live_tracks.init("points", 1)
  points[0].dRel = 10
  points[0].yRel = 1
  points[0].vRel = 2
  points[0].aRel = 0
  drawn_circles = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_circles.append((x, y, size)))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks,
    lambda d_rel, y_rel, z: (20, 30),
    path_offset_z=1.2,
    track_size=3,
    screen_offset=(100, 7),
  )

  assert drawn_circles == [(120, 37, 3)]


def test_draw_radar_tracks_allows_unknown_acceleration(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = -5
  point.aRel = float("nan")
  drawn_colors = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_colors.append(color_tuple(color)))

  radar_tracks.RadarTracks().draw_radar_tracks(live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2)

  assert drawn_colors == [color_tuple(radar_track_color(-5))]


def test_draw_radar_tracks_hides_stationary_dots(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = -20
  point.aRel = 0
  drawn_sizes = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_sizes.append(size))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, track_size=6, v_ego=20,
  )

  assert drawn_sizes == []


def test_draw_radar_tracks_keeps_matched_speed_dots_large(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = 0.5
  point.aRel = 0
  drawn_sizes = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_sizes.append(size))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, track_size=6, v_ego=20,
  )

  assert drawn_sizes == [6]


def test_draw_radar_tracks_highlights_and_returns_matched_track(monkeypatch):
  live_tracks = car.RadarData.new_message()
  points = live_tracks.init("points", 2)
  for track_id, point in enumerate(points, start=10):
    point.trackId = track_id
    point.dRel = track_id
    point.yRel = 1
    point.vRel = 2
    point.aRel = 0

  highlight_color = radar_tracks.rl.Color(255, 215, 0, 255)
  drawn_rings = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda *args: None)
  monkeypatch.setattr(
    radar_tracks.rl,
    "draw_ring",
    lambda center, inner, outer, start, end, segments, color: drawn_rings.append(
      ((center.x, center.y), inner, outer, color_tuple(color))
    ),
  )

  matched_positions = radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (d_rel, 30), path_offset_z=1.2,
    screen_offset=(100, 7), highlighted_tracks={11: highlight_color},
  )

  assert drawn_rings == [((111, 37), 9, 12, (255, 215, 0, 255))]
  assert matched_positions == {11: (111, 37)}
