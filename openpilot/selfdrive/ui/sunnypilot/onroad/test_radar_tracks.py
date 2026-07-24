from types import SimpleNamespace

from opendbc.car.structs import car

from openpilot.selfdrive.ui.sunnypilot.onroad import radar_tracks
from openpilot.selfdrive.ui.sunnypilot.onroad.radar_tracks import draw_radar_lead_connectors, format_radar_tracks_onroad_columns, \
  radar_lead_track_colors, radar_track_display


def lane_line(lateral):
  return SimpleNamespace(x=[0.0, 2000.0], y=[lateral, lateral])


THREE_LANE_LINES = [lane_line(-5.4), lane_line(-1.8), lane_line(1.8), lane_line(5.4)]


def color_tuple(color):
  return color.r, color.g, color.b, color.a


def test_dbc_motion_colors():
  assert color_tuple(radar_track_display(2)[0]) == (190, 125, 255, 255)
  assert not radar_track_display(2)[1]
  assert color_tuple(radar_track_display(1)[0]) == (255, 255, 255, 255)
  assert radar_track_display(1)[1]


def test_unknown_dbc_motion_uses_neutral_dbc_color():
  color, stationary = radar_track_display(0)

  assert color_tuple(color) == (*radar_tracks.DBC_UNKNOWN_COLOR, 255)
  assert not stationary


def test_radar_lead_track_colors_only_highlight_radar_matches():
  radar_state = SimpleNamespace(
    leadOne=SimpleNamespace(present=True, radar=True, radarTrackId=7),
    leadTwo=SimpleNamespace(present=True, radar=False, radarTrackId=9),
  )

  colors = radar_lead_track_colors(radar_state)

  assert list(colors) == [7]
  assert color_tuple(colors[7]) == color_tuple(radar_tracks.LEAD_TRACK_COLORS[0])


def test_draw_radar_lead_connectors_applies_screen_offset(monkeypatch):
  lead = SimpleNamespace(radar=True, position=(10, 20), radar_track_id=7)
  color = radar_tracks.LEAD_TRACK_COLORS[0]
  drawn = []
  monkeypatch.setattr(
    radar_tracks.rl, "draw_line_ex",
    lambda start, end, width, line_color: drawn.append(
      ((start.x, start.y), (end.x, end.y), width, color_tuple(line_color))
    ),
  )

  draw_radar_lead_connectors(
    [lead], {7: (120, 30)}, {7: color}, screen_offset=(100, 5),
  )

  assert drawn == [((110, 25), (120, 30), 2, color_tuple(color))]


def test_format_radar_tracks_columns_none():
  live_tracks = car.RadarData.new_message()

  assert format_radar_tracks_onroad_columns(live_tracks) == ("", "none", "", "", "", "")


def test_format_radar_tracks_columns_range_and_count():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x3A5, "endAddress": 0x3C4, "bus": 1, "trackCount": 2}]
  points = live_tracks.init("points", 2)
  points[0].motionState = 2
  points[1].motionState = 1

  assert format_radar_tracks_onroad_columns(live_tracks) == ("3A5-3C4", "2", "1", "1", "0", "")


def test_format_camera_objects_are_not_labeled_as_radar():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x235, "endAddress": 0x248, "bus": 1, "trackCount": 3}]
  points = live_tracks.init("points", 3)
  for point in points:
    point.motionState = 2

  assert format_radar_tracks_onroad_columns(live_tracks) == ("CAM 235-248", "3", "3", "0", "0", "")


def test_format_radar_tracks_columns_stacks_all_ranges_with_preferred_first():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [
    {"startAddress": 0x500, "endAddress": 0x51F, "bus": 2, "trackCount": 3},
    {"startAddress": 0x3A5, "endAddress": 0x3C4, "bus": 1, "trackCount": 2},
  ]
  points = live_tracks.init("points", 3)
  points[0].motionState = 2
  points[0].sourceAddress = 0x3A5
  points[1].motionState = 1
  points[1].sourceAddress = 0x3A6
  points[2].motionState = 0
  points[2].sourceAddress = 0x500

  assert format_radar_tracks_onroad_columns(live_tracks) == (
    "3A5-3C4\n500-51F",
    "2\n3",
    "1",
    "1",
    "1",
    "",
  )


def test_format_radar_tracks_columns_shows_non_motion_source():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x500, "endAddress": 0x51F, "bus": 1, "trackCount": 4}]
  points = live_tracks.init("points", 4)
  for point, v_rel in zip(points, (-5.0, 0.2, -20.0, 5.0), strict=True):
    point.vRel = v_rel
    point.motionState = 0
    point.sourceAddress = 0x500

  assert format_radar_tracks_onroad_columns(live_tracks, v_ego=20.0) == ("500-51F", "4", "0", "0", "4", "")


def test_format_radar_tracks_columns_shows_64_track_source():
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x500, "endAddress": 0x53F, "bus": 1, "trackCount": 7}]

  assert format_radar_tracks_onroad_columns(live_tracks) == ("500-53F", "7", "0", "0", "0", "")


def test_draw_radar_tracks_applies_screen_offset(monkeypatch):
  live_tracks = car.RadarData.new_message()
  points = live_tracks.init("points", 1)
  points[0].dRel = 10
  points[0].yRel = 1
  points[0].vRel = 2
  points[0].motionState = radar_tracks.DBC_MOTION_MOVING
  drawn_circles = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_circles.append((x, y, size)))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks,
    lambda d_rel, y_rel, z: (20, 30),
    path_offset_z=1.2,
    track_size=3,
    screen_offset=(100, 7),
    lane_lines=THREE_LANE_LINES,
  )

  assert drawn_circles == [(120, 37, 3)]


def test_draw_radar_tracks_hides_unknown_motion(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = -5
  point.motionState = 0
  drawn_colors = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_colors.append(color_tuple(color)))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, lane_lines=THREE_LANE_LINES,
  )

  assert drawn_colors == []


def test_draw_radar_tracks_hides_unknown_motion_from_other_source(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = -5
  point.motionState = 0
  point.sourceAddress = 0x500
  drawn_circles = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda *args: drawn_circles.append(args))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, lane_lines=THREE_LANE_LINES,
  )

  assert drawn_circles == []


def test_draw_radar_tracks_only_shows_tofus_in_three_lanes(monkeypatch):
  live_tracks = car.RadarData.new_message()
  points = live_tracks.init("points", 5)
  for point, y_rel in zip(points, (3.6, 0.0, -3.6, -6.1, 6.1), strict=True):
    point.dRel = 50
    point.yRel = y_rel
    point.vRel = 2
    point.motionState = radar_tracks.DBC_MOTION_MOVING

  drawn_circles = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda *args: drawn_circles.append(args))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, lane_lines=THREE_LANE_LINES,
  )

  assert len(drawn_circles) == 3


def test_radar_track_picks_lane_with_closest_center():
  def track(y_rel):
    return SimpleNamespace(dRel=50, yRel=y_rel)

  assert radar_tracks.radar_track_lane_index(track(3.6), THREE_LANE_LINES) == 0
  assert radar_tracks.radar_track_lane_index(track(2.5), THREE_LANE_LINES) == 0
  assert radar_tracks.radar_track_lane_index(track(0.0), THREE_LANE_LINES) == 1
  assert radar_tracks.radar_track_lane_index(track(-1.0), THREE_LANE_LINES) == 1
  assert radar_tracks.radar_track_lane_index(track(-3.6), THREE_LANE_LINES) == 2
  assert radar_tracks.radar_track_lane_index(track(6.1), THREE_LANE_LINES) is None
  assert radar_tracks.radar_track_lane_index(track(-6.1), THREE_LANE_LINES) is None
  assert radar_tracks.radar_track_lane_index(track(0.0), None) is None


def test_draw_radar_tracks_uses_source_shapes_with_preferred_circle(monkeypatch):
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [
    {"startAddress": 0x500, "endAddress": 0x51F, "bus": 1, "trackCount": 1},
    {"startAddress": 0x3A5, "endAddress": 0x3C4, "bus": 1, "trackCount": 1},
  ]
  points = live_tracks.init("points", 2)
  for point, address in zip(points, (0x500, 0x3A5), strict=True):
    point.dRel = address
    point.yRel = 1
    point.vRel = 2
    point.motionState = radar_tracks.DBC_MOTION_MOVING
    point.sourceAddress = address
    point.sourceBus = 1

  circles = []
  polygons = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, radius, color: circles.append((x, radius)))
  monkeypatch.setattr(
    radar_tracks.rl, "draw_poly",
    lambda center, sides, radius, rotation, color: polygons.append((center.x, sides, radius, rotation)),
  )

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (d_rel, 30), path_offset_z=1.2, track_size=6,
    lane_lines=THREE_LANE_LINES,
  )

  assert circles == [(0x3A5, 6)]
  assert polygons == [(0x500, 4, 6, 45.0)]


def test_draw_camera_objects_uses_triangle(monkeypatch):
  live_tracks = car.RadarData.new_message()
  live_tracks.trackSources = [{"startAddress": 0x235, "endAddress": 0x248, "bus": 1, "trackCount": 1}]
  point = live_tracks.init("points", 1)[0]
  point.dRel = 25
  point.yRel = 1
  point.vRel = 2
  point.motionState = radar_tracks.DBC_MOTION_MOVING
  point.sourceAddress = 0x235
  point.sourceBus = 1
  polygons = []
  monkeypatch.setattr(
    radar_tracks.rl, "draw_poly",
    lambda center, sides, radius, rotation, color: polygons.append((center.x, sides, radius, rotation)),
  )

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (d_rel, 30), path_offset_z=1.2, track_size=6,
    lane_lines=THREE_LANE_LINES,
  )

  assert polygons == [(25, 3, 6, -90.0)]


def test_draw_radar_tracks_shrinks_stationary_dots(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = -20
  point.motionState = 1
  drawn_sizes = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_sizes.append(size))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, track_size=6, v_ego=20,
    lane_lines=THREE_LANE_LINES,
  )

  assert drawn_sizes == [1]


def test_draw_radar_tracks_keeps_matched_speed_dots_large(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.dRel = 10
  point.yRel = 1
  point.vRel = 0.5
  point.motionState = radar_tracks.DBC_MOTION_MOVING
  drawn_sizes = []
  monkeypatch.setattr(radar_tracks.rl, "draw_circle", lambda x, y, size, color: drawn_sizes.append(size))

  radar_tracks.RadarTracks().draw_radar_tracks(
    live_tracks, lambda d_rel, y_rel, z: (20, 30), path_offset_z=1.2, track_size=6, v_ego=20,
    lane_lines=THREE_LANE_LINES,
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
    point.motionState = radar_tracks.DBC_MOTION_MOVING

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
    screen_offset=(100, 7), highlighted_tracks={11: highlight_color}, lane_lines=THREE_LANE_LINES,
  )

  assert drawn_rings == [((111, 37), 9, 12, (255, 215, 0, 255))]
  assert matched_positions == {11: (111, 37)}


def test_cached_radar_tracks_only_reproject_on_update(monkeypatch):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.trackId = 7
  point.dRel = 10
  point.yRel = 1
  point.vRel = 0
  point.motionState = radar_tracks.DBC_MOTION_MOVING
  projected = []
  drawn = []

  def map_to_screen(d_rel, y_rel, z):
    projected.append((d_rel, y_rel, z))
    return (20, 30)

  monkeypatch.setattr(
    radar_tracks.rl, "draw_circle",
    lambda x, y, radius, color: drawn.append((x, y)),
  )
  renderer = radar_tracks.RadarTracks()
  renderer.update_radar_tracks(live_tracks, map_to_screen, path_offset_z=1.2, lane_lines=THREE_LANE_LINES)
  renderer.draw_cached_radar_tracks(screen_offset=(100, 7))
  renderer.draw_cached_radar_tracks(screen_offset=(200, 9))

  assert projected == [(10, -1, 1.2)]
  assert drawn == [(120, 37), (220, 39)]
