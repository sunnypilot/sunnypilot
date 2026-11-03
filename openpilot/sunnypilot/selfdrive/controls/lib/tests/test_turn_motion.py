import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

SPEC = importlib.util.spec_from_file_location('turn_motion_test_subject', Path(__file__).resolve().parents[1]/'turn_motion.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestTurnMotion(unittest.TestCase):
  def test_nonuniform_horizons_interpolate_boundary_points(self):
    position = SimpleNamespace(t=[0., .5, 1.5, 3.], x=[0., .5, 1.5, 3.], y=[0., 0., 0., 0.])
    self.assertAlmostEqual(MODULE.predicted_travel(position), 1.)

  def test_turning_sideways_does_not_look_stationary(self):
    position = SimpleNamespace(t=[0., 1., 1.5, 2., 3.], x=[0., 1., 1.5, 1.5, 1.5], y=[0., 0., .5, 1.5, 2.])
    self.assertAlmostEqual(MODULE.predicted_travel(position), .5**.5+1.)

  def test_stationary_trajectory_has_zero_travel(self):
    position = SimpleNamespace(t=[0., 1., 2., 3.], x=[1., 1., 1., 1.], y=[2., 2., 2., 2.])
    self.assertEqual(MODULE.predicted_travel(position), 0.)

  def test_invalid_or_incomplete_forecast_is_unavailable(self):
    for position in (None, SimpleNamespace(t=[0., 1.], x=[0., 1.], y=[0., 0.]),
      SimpleNamespace(t=[0., 1., 1., 3.], x=[0.]*4, y=[0.]*4),
      SimpleNamespace(t=[0., 1., 2., 3.], x=[0., 0., float('nan'), 1.], y=[0.]*4)):
      with self.subTest(position=position):
        self.assertIsNone(MODULE.predicted_travel(position))


if __name__ == '__main__':
  unittest.main()
