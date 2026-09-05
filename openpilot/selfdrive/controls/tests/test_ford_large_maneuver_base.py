"""Large-turn command regressions, not a model of the PSCM's wheel response."""
import unittest

from openpilot.selfdrive.controls.lib.ford_path import FordPathController
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController, PscmStatus
from openpilot.selfdrive.controls.tests.test_ford_curvature_c0 import step
from openpilot.selfdrive.controls.tests.test_ford_path_reference import circle


class TestFordLargeManeuverBase(unittest.TestCase):
  def test_aligned_large_turn_keeps_baseline_pose_without_integral_authority(self):
    # A stronger forward path than the instantaneous curvature is present in
    # the recorded successful turns. A frozen integral cannot supply that base.
    for sign in (-1, 1):
      with self.subTest(sign=sign):
        model = circle(sign * .065)
        previous, controller = FordPathController(), FordVirtualAngleController()
        for i in range(300):
          now = i * .01
          baseline = previous.update(model, sign * .04, current_curvature=sign * .04, v_ego=5.)
          actual = step(controller, now, sign * .04, model, speed=5., yaw_rate=sign * .2,
                        pscm_status=PscmStatus(now, 2, 2, 2, False))
        self.assertEqual(controller.diagnostics['heading_bias'], 0.)
        self.assertAlmostEqual(actual.path_offset, baseline.path_offset, delta=.010001)
        self.assertAlmostEqual(actual.path_angle, baseline.path_angle, delta=.000501)
        self.assertEqual((actual.curvature, actual.curvature_rate), (0., 0.))

  def test_small_action_remains_a_centering_request_despite_a_distant_turn(self):
    for sign in (-1, 1):
      controller = FordVirtualAngleController()
      for i in range(300):
        actual = step(controller, i * .01, sign * .002, circle(sign * .065), speed=5.)
      self.assertAlmostEqual(actual.path_offset, sign * .064, delta=.005001)
      self.assertAlmostEqual(actual.path_angle, sign * .014, delta=.000501)

  def test_zero_and_reversed_action_supersede_old_model_turn(self):
    for next_action in (0., -.04):
      controller = FordVirtualAngleController()
      model = circle(.065)
      for i in range(300):
        step(controller, i * .01, .04, model, speed=5.)
      for i in range(300, 510):
        actual = step(controller, i * .01, next_action, model, speed=5.)
      self.assertAlmostEqual(actual.path_offset, 32. * next_action, delta=.005001)
      self.assertAlmostEqual(actual.path_angle, 7. * next_action, delta=.000501)
      self.assertEqual(controller.diagnostics['heading_bias'], 0.)


if __name__ == '__main__':
  unittest.main()
