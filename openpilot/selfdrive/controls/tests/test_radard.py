from types import SimpleNamespace
import unittest

from openpilot.selfdrive.controls.radard import Track, match_vision_to_track


class TestRadarD(unittest.TestCase):
  def test_match_vision_to_track_with_missing_lateral_position(self):
    lead = SimpleNamespace(
      x=[31.52],
      xStd=[1.0],
      y=[0.0],
      yStd=[1.0],
      v=[10.0],
      vStd=[1.0],
    )
    less_likely_track = SimpleNamespace(dRel=35.0, yRel=0.0, vRel=0.0)
    scc_fallback = SimpleNamespace(dRel=30.0, yRel=float("nan"), vRel=0.0)

    matched = match_vision_to_track(10.0, lead, {0: less_likely_track, 1: scc_fallback})

    self.assertIs(matched, scc_fallback)

  def test_missing_lateral_position_is_not_low_speed_lead(self):
    scc_fallback = SimpleNamespace(dRel=10.0, yRel=float("nan"))

    self.assertFalse(Track.potential_low_speed_lead(scc_fallback, 0.0))
