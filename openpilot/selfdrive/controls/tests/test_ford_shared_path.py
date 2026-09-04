import math
import tempfile
import unittest
from types import SimpleNamespace

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_shared_path import (
  _C2_FREE_HORIZON_S, FordSharedPathController, _c2_free_request, select_shared_path_controller,
)


def circle(curvature: float, speed: float = 8.0):
  distance = [i * 0.1 for i in range(401)]
  heading = [curvature * s for s in distance]
  return SimpleNamespace(
    position=SimpleNamespace(
      t=[s / speed for s in distance],
      x=[math.sin(h) / curvature if curvature else s for s, h in zip(distance, heading, strict=True)],
      y=[(1.0 - math.cos(h)) / curvature if curvature else 0.0 for h in heading],
    ),
    orientation=SimpleNamespace(z=heading),
  )


class TestSharedController(unittest.TestCase):
  def test_native_toggle_is_default_off_and_selection_is_startup_only(self):
    from openpilot.common.params import Params
    with tempfile.TemporaryDirectory(prefix='ford-shared-params-') as directory:
      params = Params(directory)
      self.assertIs(params.get_default_value('FordSharedPathController'), False)
      self.assertFalse(params.get_bool('FordSharedPathController'))
      prior = FordPscmObserverPathController()
      params.put_bool('FordSharedPathController', True, block=True)
      chosen = select_shared_path_controller('ford', FordFlags.CANFD, params.get_bool('FordSharedPathController'), prior)
      self.assertIsInstance(chosen, FordSharedPathController)
      params.put_bool('FordSharedPathController', False, block=True)
      self.assertIsInstance(chosen, FordSharedPathController)
      self.assertIs(select_shared_path_controller('ford', FordFlags.CANFD, params.get_bool('FordSharedPathController'), prior), prior)

  def test_default_off_and_unsupported_cars_retain_the_exact_previous_object(self):
    for previous in (FordPathController(), FordPscmObserverPathController()):
      for brand, flags, enabled in (("ford", FordFlags.CANFD, False), ("ford", 0, True), ("tesla", FordFlags.CANFD, True)):
        self.assertIs(select_shared_path_controller(brand, flags, enabled, previous), previous)
      self.assertIsInstance(select_shared_path_controller("ford", FordFlags.CANFD, True, previous), FordSharedPathController)

  def test_c2_and_c3_are_always_zero(self):
    controller = FordSharedPathController()
    requests = [
      controller.update(circle(curvature, speed), desired, current_curvature=actual,
                        v_ego=speed, v_ego_raw=speed)
      for curvature, desired, actual, speed in (
        (0.0, 0.0, 0.0, 20.0), (0.003, -0.01, 0.005, 20.0),
        (0.12, 0.12, 0.0, 5.0), (-0.12, 0.12, -0.2, 5.0),
      )
    ]
    requests += [controller.update(None, 0.1), controller.update(circle(0.1), 0.1, active=False)]
    for command in requests:
      self.assertEqual(command.curvature, 0.0)
      self.assertEqual(command.curvature_rate, 0.0)

  def test_constant_curvature_uses_firmware_derived_temporal_offset(self):
    for sign in (-1, 1):
      for speed in (5.0, 10.0, 15.0, 20.0):
        curvature = sign * 0.001
        request = _c2_free_request(circle(curvature, speed), curvature)
        self.assertIsNotNone(request)
        c2_equivalent = 0.30078125 * speed ** 2 * curvature
        self.assertAlmostEqual(0.5 * request.command.path_offset, c2_equivalent, delta=abs(c2_equivalent) * 1e-3)
        self.assertAlmostEqual(request.command.path_angle, 0.0, delta=1e-5)
        self.assertEqual(request.command.curvature, 0.0)

  def test_exact_time_sample_and_origin_transform(self):
    horizon = _C2_FREE_HORIZON_S
    local_x = [0.0, 2.0, 6.0]
    local_y = [0.0, 0.4, 1.2]
    local_heading = [0.0, 0.12, 0.3]

    def transformed(rotation, tx, ty):
      cosine, sine = math.cos(rotation), math.sin(rotation)
      return SimpleNamespace(
        position=SimpleNamespace(
          t=[0.0, horizon, 2.0 * horizon],
          x=[tx + cosine * x - sine * y for x, y in zip(local_x, local_y, strict=True)],
          y=[ty + sine * x + cosine * y for x, y in zip(local_x, local_y, strict=True)],
        ),
        orientation=SimpleNamespace(z=[rotation + heading for heading in local_heading]),
      )

    reference = _c2_free_request(transformed(0.0, 0.0, 0.0), 0.01)
    moved = _c2_free_request(transformed(0.7, 40.0, -3.0), 0.01)
    self.assertIsNotNone(reference)
    self.assertIsNotNone(moved)
    self.assertAlmostEqual(reference.model_offset, 0.4)
    self.assertAlmostEqual(reference.model_heading, 0.12)
    self.assertAlmostEqual(reference.arc, math.hypot(2.0, 0.4))
    self.assertAlmostEqual(moved.model_offset, reference.model_offset)
    self.assertAlmostEqual(moved.model_heading, reference.model_heading)
    self.assertAlmostEqual(moved.arc, reference.arc)
    self.assertAlmostEqual(moved.command.path_offset, reference.command.path_offset)
    self.assertAlmostEqual(moved.command.path_angle, reference.command.path_angle)

  def test_c1_is_only_remaining_heading_error(self):
    for sign in (-1, 1):
      curvature = sign * 0.02
      model = circle(curvature, 8.0)
      behind = _c2_free_request(model, 0.0)
      aligned = _c2_free_request(model, curvature)
      ahead = _c2_free_request(model, 2.0 * curvature)
      self.assertGreater(sign * behind.command.path_angle, 0.0)
      self.assertAlmostEqual(aligned.command.path_angle, 0.0, delta=1e-5)
      self.assertLess(sign * ahead.command.path_angle, 0.0)
      for request in (behind, aligned, ahead):
        expected = math.atan2(math.sin(request.model_heading - request.predicted_heading),
                              math.cos(request.model_heading - request.predicted_heading))
        self.assertAlmostEqual(request.command.path_angle, expected)

  def test_action_curvature_does_not_change_model_pose_command(self):
    controller = FordSharedPathController()
    model = circle(0.03, 10.0)
    commands = [controller.update(model, desired, current_curvature=0.01, v_ego=10.0, v_ego_raw=10.0)
                for desired in (-0.1, -0.005, 0.0, 0.005, 0.1)]
    self.assertTrue(all(command == commands[0] for command in commands[1:]))

  def test_direct_targets_do_not_have_host_side_slew_or_history(self):
    controller = FordSharedPathController()
    positive = controller.update(circle(0.08, 5.0), 0.08, current_curvature=0.0)
    negative = controller.update(circle(-0.08, 5.0), -0.08, current_curvature=0.0)
    positive_again = controller.update(circle(0.08, 5.0), 0.08, current_curvature=0.0)
    self.assertGreater(positive.path_offset, 0.0)
    self.assertGreater(positive.path_angle, 0.0)
    self.assertLess(negative.path_offset, 0.0)
    self.assertLess(negative.path_angle, 0.0)
    self.assertEqual(positive_again, positive)

  def test_invalid_model_never_falls_back_to_c2(self):
    controller = FordSharedPathController()
    invalid_models = [
      None,
      SimpleNamespace(position=SimpleNamespace(t=[0.0], x=[0.0], y=[0.0]), orientation=SimpleNamespace(z=[0.0])),
      SimpleNamespace(position=SimpleNamespace(t=[0.0, 2.0], x=[0.0, math.nan], y=[0.0, 0.0]),
                      orientation=SimpleNamespace(z=[0.0, 0.0])),
    ]
    for model in invalid_models:
      command = controller.update(model, 0.02, current_curvature=0.01)
      self.assertEqual(command, FordPath(valid=True))
      self.assertEqual(controller.diagnostics['status'], 'invalid_input')
    self.assertEqual(controller.update(circle(0.02), 0.02, active=False), FordPath())
    self.assertEqual(controller.diagnostics['status'], 'inactive')

  def test_commands_use_full_symmetric_dbc_bounds(self):
    horizon = _C2_FREE_HORIZON_S
    packer = CANPacker('ford_lincoln_base_pt')
    parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 0)], 0)
    for sign in (-1, 1):
      model = SimpleNamespace(
        position=SimpleNamespace(t=[0.0, horizon], x=[0.0, 0.0], y=[0.0, sign * 20.0]),
        orientation=SimpleNamespace(z=[0.0, sign * 2.0]),
      )
      command = FordSharedPathController().update(model, 0.0, current_curvature=0.0)
      self.assertEqual(command.path_offset, sign * 5.11)
      self.assertEqual(command.path_angle, sign * 0.5)
      self.assertEqual(command.curvature, 0.0)
      self.assertEqual(command.curvature_rate, 0.0)
      packet = create_lat_ctl2_msg(packer, CanBus(fingerprint={0: {}}), 2, -command.path_offset,
                                   -command.path_angle, -command.curvature, -command.curvature_rate, 0)
      parser.update([0, [packet]])
      decoded = parser.vl['LateralMotionControl2']
      self.assertAlmostEqual(decoded['LatCtlPathOffst_L_Actl'], -command.path_offset)
      self.assertAlmostEqual(decoded['LatCtlPath_An_Actl'], -command.path_angle)
      self.assertEqual(decoded['LatCtlCurv_No_Actl'], 0.0)


if __name__ == '__main__':
  unittest.main()
