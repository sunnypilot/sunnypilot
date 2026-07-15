from cereal import car, custom

from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt


def make_live_tracks(with_source: bool):
  live_tracks = car.RadarData.new_message()
  point = live_tracks.init("points", 1)[0]
  point.trackId = 7
  point.dRel = 12
  point.yRel = -3
  point.vRel = 1
  if with_source:
    live_tracks.trackSources = [{"startAddress": 0x500, "endAddress": 0x51F, "bus": 1, "trackCount": 1}]
  return live_tracks


def test_inactive_radar_tracks_ignores_stale_points():
  cc_sp = custom.CarControlSP.new_message()

  ControlsExt.get_radar_track_data(cc_sp, make_live_tracks(with_source=False), valid=True)

  assert not cc_sp.radarTracksActive
  assert len(cc_sp.radarTracks) == 0


def test_active_radar_tracks_are_copied():
  cc_sp = custom.CarControlSP.new_message()

  ControlsExt.get_radar_track_data(cc_sp, make_live_tracks(with_source=True), valid=True)

  assert cc_sp.radarTracksActive
  assert len(cc_sp.radarTracks) == 1
  assert cc_sp.radarTracks[0].trackId == 7
