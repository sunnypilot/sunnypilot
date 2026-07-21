import openpilot.cereal.messaging as messaging
from openpilot.cereal import custom
from opendbc.car.structs import car

from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt


def make_live_tracks(motion_states: tuple[int, ...], with_source: bool = True):
  live_tracks = car.RadarData.new_message()
  points = live_tracks.init("points", len(motion_states))
  for track_id, (point, motion_state) in enumerate(zip(points, motion_states, strict=True), start=7):
    point.trackId = track_id
    point.dRel = 12
    point.yRel = -3
    point.vRel = 1
    point.motionState = motion_state
  if with_source:
    live_tracks.trackSources = [{"startAddress": 0x3A5, "endAddress": 0x3C4, "bus": 1,
                                 "trackCount": len(motion_states)}]
  return live_tracks


def test_inactive_radar_tracks_ignores_stale_points():
  cc_sp = custom.CarControlSP.new_message()

  ControlsExt.get_radar_track_data(cc_sp, make_live_tracks((2,), with_source=False), valid=True)

  assert not cc_sp.radarTracksActive
  assert len(cc_sp.radarTracks) == 0


def test_active_radar_tracks_copy_only_classified_points():
  cc_sp = custom.CarControlSP.new_message()

  ControlsExt.get_radar_track_data(cc_sp, make_live_tracks((2, 1, 0, 255)), valid=True)

  assert cc_sp.radarTracksActive
  assert [track.trackId for track in cc_sp.radarTracks] == [7, 8]
  assert [track.motionState for track in cc_sp.radarTracks] == [2, 1]


def test_radar_tracks_are_positioned_relative_to_curved_model_path():
  cc_sp = custom.CarControlSP.new_message()
  live_tracks = make_live_tracks((2, 2))
  live_tracks.points[0].dRel = 20
  live_tracks.points[0].yRel = -3
  live_tracks.points[1].dRel = 20
  live_tracks.points[1].yRel = -6.5
  model = messaging.new_message("modelV2").modelV2
  model.position.x = [0, 10, 20]
  model.position.y = [0, 1, 3]

  ControlsExt.get_radar_track_data(cc_sp, live_tracks, valid=True, model=model, model_valid=True)

  assert cc_sp.radarTracks[0].yRel == 0
  assert cc_sp.radarTracks[1].yRel == -3.5


def test_radar_track_cache_only_rebuilds_when_inputs_update():
  controls_ext = object.__new__(ControlsExt)
  controls_ext._reset_radar_track_cache()
  live_tracks = make_live_tracks((2,))

  controls_ext.update_radar_track_cache(live_tracks, valid=True, inputs_updated=True)
  assert controls_ext._radar_tracks_cache[0]["dRel"] == 12

  live_tracks.points[0].dRel = 30
  controls_ext.update_radar_track_cache(live_tracks, valid=True, inputs_updated=False)
  assert controls_ext._radar_tracks_cache[0]["dRel"] == 12

  controls_ext.update_radar_track_cache(live_tracks, valid=True, inputs_updated=True)
  assert controls_ext._radar_tracks_cache[0]["dRel"] == 30
