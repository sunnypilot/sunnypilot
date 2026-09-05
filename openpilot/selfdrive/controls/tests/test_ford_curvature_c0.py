"""Action-to-C0 regressions; these do not simulate PSCM/vehicle response."""
import math
import unittest

from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController
from openpilot.selfdrive.controls.tests.test_ford_path_reference import circle


def step(controller, t, desired, model=None, speed=8., yaw_rate=0., **kwargs):
  inputs = {'yaw_rate': yaw_rate, 'speed': speed, 'now': t, 'measurement_time': t,
            'model_time': math.floor((t + 1e-6) / .05) * .05, 'reference_time': t, 'active': True}
  inputs.update(kwargs)
  return controller.update(circle() if model is None else model, desired, **inputs)


class TestFordCurvatureC0(unittest.TestCase):
  def test_centering_action_survives_an_ego_anchored_model(self):
    for sign in (-1, 1):
      controller = FordVirtualAngleController()
      for i in range(200):
        # Action can request recovery even when the short model preview is flat.
        path = step(controller, i * .01, sign * .002, speed=20.)
      self.assertAlmostEqual(path.path_offset, sign * .4, delta=.0051)
      self.assertAlmostEqual(path.path_angle, sign * .04, delta=.000251)
      self.assertEqual((path.curvature, path.curvature_rate), (0., 0.))

  def test_slow_turns_retain_large_absolute_demand_after_curvature_matches(self):
    for speed in (2., 4., 6.):
      for sign in (-1, 1):
        controller = FordVirtualAngleController()
        for i in range(250):
          path = step(controller, i * .01, sign * .04, circle(sign * .04), speed, sign * .04 * speed)
        self.assertAlmostEqual(path.path_offset, sign * 1.28, delta=.0051)
        self.assertGreater(sign * path.path_angle, .2)

  def test_model_heading_cannot_inject_commands_when_action_requests_zero(self):
    for sign in (-1, 1):
      controller = FordVirtualAngleController()
      for i in range(250):
        path = step(controller, i * .01, 0., circle(sign * .12), speed=5.)
      self.assertAlmostEqual(path.path_offset, 0., delta=.0051)
      self.assertAlmostEqual(path.path_angle, 0., delta=.000251)
      self.assertGreater(sign * controller.diagnostics['model_heading_target'], .4)

  def test_c1_reversal_cannot_delay_action_c0_release(self):
    controller = FordVirtualAngleController()
    for i in range(200):
      path = step(controller, i * .01, .1, circle(.12), speed=5.)
    for i in range(200, 280):
      path = step(controller, i * .01, .003125, circle(.12), speed=5.)
    self.assertAlmostEqual(path.path_offset, .1)
    self.assertAlmostEqual(path.path_angle, .1)
    for i in range(280, 283):
      path = step(controller, i * .01, 0., circle(-.12), speed=5.)
    self.assertAlmostEqual(path.path_offset, 0., delta=.0051)
    self.assertGreater(path.path_angle, .08)  # C1 is still in its own limited transition.

  def test_both_commands_reverse_while_model_heading_requests_the_old_turn(self):
    controller = FordVirtualAngleController()
    model = circle(.04)
    for i in range(200):
      path = step(controller, i * .01, .01, model)
    for i in range(200, 240):
      path = step(controller, i * .01, -.01, model)
    self.assertLess(path.path_offset, -.3)
    self.assertLess(path.path_angle, -.07)

  def test_invalid_or_stale_action_clears_both_requests(self):
    for desired, overrides in ((float('nan'), {}), (float('inf'), {}), (2., {}), (.01, {'reference_time': 0.}),
                               (.01, {'reference_time': float('nan')}), (.01, {'reference_time': 1.2})):
      controller = FordVirtualAngleController()
      step(controller, .99, .01, circle(.04))
      self.assertEqual(step(controller, 1., desired, circle(.04), **overrides), FordPath())
      self.assertIsNone(controller.reference.path)

  def test_fresh_action_source_can_change_without_an_inactive_cycle(self):
    controller = FordVirtualAngleController()
    self.assertTrue(step(controller, 1., .01, reference_time=.99).valid)
    # A model/maneuver source switch can select an older but still fresh action.
    self.assertTrue(step(controller, 1.01, .01, reference_time=.98).valid)


if __name__ == '__main__':
  unittest.main()
