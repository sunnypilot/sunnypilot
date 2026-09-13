from types import SimpleNamespace
import unittest

from openpilot.selfdrive.controls.radard import KalmanParams, Track, match_vision_to_track


class TestRadarD(unittest.TestCase):
  @staticmethod
  def make_track(identifier: int, d_rel: float, y_rel: float, v_rel: float, v_ego: float) -> Track:
    track = Track(identifier, v_ego + v_rel, KalmanParams(0.05))
    track.update(d_rel, y_rel, v_rel, v_ego + v_rel)
    return track

  def test_match_vision_to_track_with_missing_lateral_position(self):
    lead = SimpleNamespace(
      x=[31.52],
      xStd=[1.0],
      y=[0.0],
      yStd=[1.0],
      v=[10.0],
      vStd=[1.0],
    )
    less_likely_track = self.make_track(0, 35.0, 0.0, 0.0, 10.0)
    scc_fallback = self.make_track(1, 30.0, float("nan"), 0.0, 10.0)

    matched = match_vision_to_track(10.0, lead, {0: less_likely_track, 1: scc_fallback})

    self.assertIs(matched, scc_fallback)

  def test_missing_lateral_position_is_not_low_speed_lead(self):
    scc_fallback = self.make_track(0, 10.0, float("nan"), 0.0, 0.0)

    self.assertFalse(scc_fallback.potential_low_speed_lead(0.0))
