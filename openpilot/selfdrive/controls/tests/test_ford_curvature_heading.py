"""Command-reference regressions, not predictions of vehicle response."""
import unittest

from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController
from openpilot.selfdrive.controls.tests.test_ford_curvature_c0 import step
from openpilot.selfdrive.controls.tests.test_ford_path_reference import circle


class TestFordCurvatureHeading(unittest.TestCase):
  def test_model_turn_cannot_hold_c1_after_action_releases(self):
    controller = FordVirtualAngleController()
    model = circle(.12)
    for i in range(200):
      path = step(controller, i * .01, .04, model, speed=5.)
    self.assertAlmostEqual(path.path_angle, .28, delta=.000251)
    for i in range(200, 270):
      path = step(controller, i * .01, 0., model, speed=5.)
    self.assertAlmostEqual(path.path_angle, 0., delta=.000251)
    self.assertAlmostEqual(path.path_offset, 0., delta=.0051)

  def test_full_heading_survives_flat_geometry_and_matching_actual_curvature(self):
    for speed in (3., 8., 20.):
      for sign in (-1, 1):
        controller = FordVirtualAngleController()
        for i in range(200):
          path = step(controller, i * .01, sign * .02, circle(), speed=speed, yaw_rate=sign * .02 * speed)
        self.assertAlmostEqual(path.path_angle, sign * .02 * max(7., speed), delta=.000251)
        self.assertEqual((path.curvature, path.curvature_rate), (0., 0.))

  def test_heading_reverses_with_action_while_model_keeps_old_turn(self):
    controller = FordVirtualAngleController()
    model = circle(.12)
    for i in range(200):
      path = step(controller, i * .01, .04, model, speed=5.)
    for i in range(200, 320):
      path = step(controller, i * .01, -.04, model, speed=5.)
    self.assertAlmostEqual(path.path_angle, -.28, delta=.000251)
    self.assertLess(path.path_offset, 0.)

  def test_model_shape_does_not_change_valid_action_commands(self):
    straight, bent = FordVirtualAngleController(), FordVirtualAngleController()
    for i in range(300):
      desired = .04 if i < 150 else -.04
      left = step(straight, i * .01, desired, circle(), speed=8.)
      right = step(bent, i * .01, desired, circle(.12), speed=8.)
      self.assertEqual(left, right)


if __name__ == '__main__':
  unittest.main()
