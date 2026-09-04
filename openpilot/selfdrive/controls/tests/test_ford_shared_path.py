import cProfile
import math
import random
import tempfile
import unittest
from types import SimpleNamespace

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from opendbc.car.ford.values import CarControllerParams, FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_shared_path import (
  ContributionAllocator, FordSharedPathController, contributions, request_for_model, select_shared_path_controller,
)


def circle(curvature, speed=8.0):
  distance = [i * 0.1 for i in range(401)]
  heading = [curvature * s for s in distance]
  return SimpleNamespace(
    position=SimpleNamespace(x=[math.sin(h) / curvature if curvature else s for s, h in zip(distance, heading, strict=True)],
                             y=[(1 - math.cos(h)) / curvature if curvature else 0.0 for h in heading]),
    orientation=SimpleNamespace(z=heading),
  )


class TestSharedRequest(unittest.TestCase):
  def test_gentle_request_is_c2_only_and_preserves_upstream_request(self):
    for desired in (-0.004, 0.0, 0.004):
      request = request_for_model(circle(0.003), desired, current_curvature=0.005, v_ego=20.0)
      self.assertEqual(request.preferred.path_offset, 0.0)
      self.assertEqual(request.preferred.path_angle, 0.0)
      self.assertEqual(request.preferred.curvature, desired)
      self.assertEqual(request.feedback, 0.0)
      self.assertAlmostEqual(request.total, 0.30078125 * 20.0 ** 2 * desired)

  def test_saturated_turn_can_back_off_without_erasing_the_arc_at_target(self):
    for sign in (-1, 1):
      model = circle(sign * 0.04)
      aligned = request_for_model(model, sign * 0.04, current_curvature=sign * 0.04, v_ego=8.0)
      over = request_for_model(model, sign * 0.04, current_curvature=sign * 0.06, v_ego=8.0)
      self.assertGreater(sign * aligned.total, 0.7)
      self.assertLess(sign * over.feedback, -0.1)
      self.assertLess(sign * over.total, sign * aligned.total - 0.1)
      self.assertEqual(over.preferred.curvature, 0.0)

  def test_remaining_model_arc_survives_a_collapsed_action(self):
    request = request_for_model(circle(0.04), 0.0, current_curvature=0.04, v_ego=8.0)
    self.assertGreater(request.total, 0.5)
    self.assertAlmostEqual(request.feedback, 0.0, places=5)
    self.assertEqual(request.preferred.curvature, 0.0)

  def test_measured_turn_retains_unwind_after_model_straightens(self):
    for sign in (-1, 1):
      request = request_for_model(circle(0.0), sign * 0.002, current_curvature=sign * 0.03, v_ego=8.0)
      self.assertLess(sign * request.feedback, -0.1)
      self.assertLess(sign * request.total, 0.0)
      self.assertEqual(request.preferred.curvature, 0.0)


class TestContributionAllocator(unittest.TestCase):
  def test_candidate_search_has_bounded_curvature_limiter_work(self):
    allocator = ContributionAllocator(initial_state=(0.2, 0.01, 0.003))
    allocator.set_command(FordPath(True, 0.2, 0.01, 0.003))
    profile = cProfile.Profile()
    profile.runcall(allocator.allocate, 0.3, FordPath(True, 0.4, 0.02, 0.002), 12.0)
    limit_code = CarControllerParams.CURVATURE_LIMITS.apply_limits.__func__.__code__
    calls = sum(entry.callcount for entry in profile.getstats() if entry.code is limit_code)
    # Two bounds, at most eight distinct candidate C2 values, and final packet.
    # This operation budget catches repeated work without flaky wall-clock limits.
    self.assertGreater(calls, 0)
    self.assertLessEqual(calls, 11)

  def test_fixed_request_is_preserved_while_c2_unloads(self):
    speed = 10.0
    initial = (0.0, 0.0, 0.004)
    requested = sum(contributions(initial, speed))
    allocator = ContributionAllocator(initial_state=initial)
    allocator.set_command(FordPath(True, *initial))
    for _ in range(180):
      command = allocator.allocate(requested, FordPath(True, 0.1, 0.01, 0.0), speed)
      self.assertLessEqual(command.curvature, 0.004)
      allocator.advance(0.01)
      self.assertLessEqual(abs(sum(contributions(allocator.state, speed)) - requested), allocator.tolerance(speed) + 1e-8)
    self.assertLess(abs(allocator.state[2]), 0.00004)
    self.assertGreater(allocator.state[0] + allocator.state[1], 0.0)

  def test_c2_reloads_only_as_fast_contribution_can_be_removed(self):
    speed = 20.0
    initial = (0.4, 0.01, 0.0)
    requested = sum(contributions(initial, speed))
    desired_c2 = requested / (0.30078125 * speed ** 2)
    allocator = ContributionAllocator(initial_state=initial)
    allocator.set_command(FordPath(True, *initial))
    for _ in range(400):
      allocator.allocate(requested, FordPath(True, 0.0, 0.0, desired_c2), speed)
      self.assertLessEqual(allocator.predicted_peak_error, allocator.tolerance(speed) + 1e-8)
      allocator.advance(0.01)
    self.assertLess(abs(allocator.state[0]), 0.01)
    self.assertLess(abs(allocator.state[1]), 0.0005)
    self.assertAlmostEqual(allocator.state[2], desired_c2, delta=0.00002)

  def test_inactive_state_drains_instead_of_resetting_instantly(self):
    allocator = ContributionAllocator(initial_state=(1.0, 0.1, 0.01))
    allocator.set_command(FordPath())
    self.assertEqual(allocator.state, (1.0, 0.1, 0.01))
    allocator.advance(0.004)
    self.assertAlmostEqual(allocator.state[2], 0.002)
    allocator.advance(0.004)
    self.assertEqual(allocator.state, (0.0, 0.0, 0.0))

  def test_unknown_history_and_gaps_cannot_be_used_as_exact_state(self):
    allocator = ContributionAllocator()
    self.assertFalse(allocator.initialized)
    with self.assertRaises(ValueError):
      allocator.allocate(0.1, FordPath(True), 10.0)
    allocator.set_command(FordPath())
    allocator.advance(0.024)
    self.assertTrue(allocator.initialized)
    allocator.advance(0.25)
    self.assertFalse(allocator.initialized)

  def test_startup_does_not_invent_an_inactive_command(self):
    allocator = ContributionAllocator()
    allocator.advance(0.1)
    self.assertFalse(allocator.initialized)

  def test_unreachable_request_is_reported_and_never_refills_c2(self):
    allocator = ContributionAllocator(initial_state=(0.0, 0.0, 0.0))
    command = allocator.allocate(0.84, FordPath(True, 1.0, 0.03, 0.0), 10.0)
    self.assertEqual(command.curvature, 0.0)
    self.assertGreater(allocator.shortfall, 0.7)
    self.assertLessEqual(command.path_offset, 0.04)
    self.assertLessEqual(command.path_angle, 0.01)

  def test_active_state_uses_250hz_slew_and_wire_values(self):
    allocator = ContributionAllocator(initial_state=(0.0, 0.0, 0.0))
    allocator.set_command(FordPath(True, 0.1001, 0.0101, 0.002001))
    allocator.advance(0.01)
    self.assertAlmostEqual(allocator.state[0], 1.5 * 0.008)
    self.assertAlmostEqual(allocator.state[1], 0.100006103515625 * 0.008)
    allocator.advance(0.01)
    self.assertAlmostEqual(allocator.state[0], 1.5 * 0.020)
    self.assertAlmostEqual(allocator.command.path_angle, 0.0100)

  def test_estimated_packet_matches_float32_carcontrol_and_can_packing(self):
    from openpilot.cereal import custom
    packer = CANPacker('ford_lincoln_base_pt')
    parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 0)], 0)
    allocator = ContributionAllocator(initial_state=(0.0, 0.0, 0.0))
    for c0, c1, c2 in ((0.005, 0.00025, 0.00001), (-0.005, -0.00025, -0.00001),
                       (0.115, 0.03475, 0.00301), (-0.115, -0.03475, -0.00301)):
      command = FordPath(True, c0, c1, c2)
      allocator.set_command(command)
      message = custom.CarControlSP.new_message()
      path = message.fordLateralPath
      path.pathOffset, path.pathAngle, path.curvature = c0, c1, c2
      packet = create_lat_ctl2_msg(packer, CanBus(fingerprint={0: {}}), 2, -path.pathOffset, -path.pathAngle, -path.curvature, 0.0, 0)
      parser.update([0, [packet]])
      decoded = parser.vl['LateralMotionControl2']
      for value, field in ((allocator.command.path_offset, 'LatCtlPathOffst_L_Actl'),
                           (allocator.command.path_angle, 'LatCtlPath_An_Actl'), (allocator.command.curvature, 'LatCtlCurv_No_Actl')):
        self.assertAlmostEqual(value, -decoded[field], places=10)

  def test_s_shape_preference_keeps_opposing_fast_fields(self):
    allocator = ContributionAllocator(initial_state=(0.0, 0.0, 0.0))
    preferred = FordPath(True, 0.2, -0.01, 0.0)
    for _ in range(100):
      command = allocator.allocate(0.0, preferred, 8.0)
      allocator.advance(0.01)
    self.assertGreater(command.path_offset, 0.1)
    self.assertLess(command.path_angle, -0.005)
    self.assertLessEqual(abs(sum(contributions(allocator.state, 8.0))), allocator.tolerance(8.0))


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
      self.assertIsInstance(chosen, FordSharedPathController)  # running selection is unchanged
      self.assertIs(select_shared_path_controller('ford', FordFlags.CANFD, params.get_bool('FordSharedPathController'), prior), prior)

  def test_inactive_initializes_history_and_large_turn_uses_live_fast_fields(self):
    controller = FordSharedPathController()
    model = circle(0.04)
    for _ in range(4):
      self.assertFalse(controller.update(model, 0.04, current_curvature=0.0, v_ego=8.0, v_ego_raw=8.0, active=False).valid)
    for _ in range(100):
      command = controller.update(model, 0.04, current_curvature=0.0, v_ego=8.0, v_ego_raw=8.0)
      self.assertTrue(command.valid)
      self.assertEqual(command.curvature, 0.0)
    self.assertEqual(controller.diagnostics['status'], 'active')
    self.assertGreater(command.path_offset, 0.0)
    self.assertGreater(command.path_angle, 0.0)

  def test_default_off_and_unsupported_cars_retain_the_exact_previous_object(self):
    for previous in (FordPathController(), FordPscmObserverPathController()):
      for brand, flags, enabled in (("ford", FordFlags.CANFD, False), ("ford", 0, True), ("tesla", FordFlags.CANFD, True)):
        self.assertIs(select_shared_path_controller(brand, flags, enabled, previous), previous)
      self.assertIsInstance(select_shared_path_controller("ford", FordFlags.CANFD, True, previous), FordSharedPathController)

  def test_invalid_model_and_timing_gap_do_not_jump_fast_fields(self):
    controller = FordSharedPathController()
    model = circle(0.04)
    for i in range(4):
      controller.update(model, 0.04, v_ego=8.0, v_ego_raw=8.0, active=False, now=i * 0.01)
    for i in range(4, 104):
      previous = controller.update(model, 0.04, v_ego=8.0, v_ego_raw=8.0, now=i * 0.01)
    command = controller.update(None, 0.04, v_ego=8.0, v_ego_raw=8.0, now=1.04)
    self.assertEqual(controller.diagnostics['status'], 'invalid_input')
    self.assertLessEqual(abs(command.path_offset - previous.path_offset), 0.04 + 1e-9)
    self.assertLessEqual(abs(command.path_angle - previous.path_angle), 0.01 + 1e-9)
    previous = command
    command = controller.update(model, 0.04, v_ego=8.0, v_ego_raw=8.0, now=2.0)
    self.assertEqual(controller.diagnostics['status'], 'warming_history')
    self.assertLessEqual(abs(command.path_offset - previous.path_offset), 0.04 + 1e-9)
    self.assertLessEqual(abs(command.path_angle - previous.path_angle), 0.01 + 1e-9)

  def test_random_sequences_keep_existing_command_and_downstream_limits(self):
    rng = random.Random(68)
    controller = FordSharedPathController()
    previous = FordPath()
    for i in range(600):
      speed = rng.uniform(1.0, 35.0)
      curvature = rng.uniform(-0.12, 0.12)
      active = i >= 4 and i % 37 != 0
      command = controller.update(circle(curvature), rng.uniform(-0.02, 0.02),
                                  current_curvature=rng.uniform(-0.12, 0.12), v_ego=speed, v_ego_raw=speed, active=active)
      self.assertTrue(all(math.isfinite(v) for v in (command.path_offset, command.path_angle, command.curvature)))
      self.assertLessEqual(abs(command.path_offset), 5.11)
      self.assertLessEqual(abs(command.path_angle), 0.5)
      self.assertLessEqual(abs(command.curvature), 0.02)
      self.assertEqual(command.curvature_rate, 0.0)
      if active:
        self.assertLessEqual(abs(command.path_offset - previous.path_offset), 0.04 + 1e-9)
        self.assertLessEqual(abs(command.path_angle - previous.path_angle), 0.01 + 1e-9)
        limited = CarControllerParams.CURVATURE_LIMITS.apply_limits(command.curvature, previous.curvature, speed, 0.0, True, 1)
        self.assertAlmostEqual(command.curvature, limited, places=10)
      else:
        self.assertEqual(command, FordPath())
      previous = command


if __name__ == '__main__':
  unittest.main()
