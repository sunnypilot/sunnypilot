import math
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.ford_path import DBC_CURVATURE, FordPathController


def _path(curvature: float, curvature_rate: float = 0.0, speed: float = 8.0):
  t = np.linspace(0.0, 3.0, 61)
  distance = speed * t
  heading = curvature * distance + 0.5 * curvature_rate * distance ** 2
  x = np.zeros_like(distance)
  y = np.zeros_like(distance)
  for i in range(1, len(distance)):
    ds = distance[i] - distance[i - 1]
    average_heading = 0.5 * (heading[i] + heading[i - 1])
    x[i] = x[i - 1] + ds * math.cos(average_heading)
    y[i] = y[i - 1] + ds * math.sin(average_heading)
  return SimpleNamespace(
    position=SimpleNamespace(t=t.tolist(), x=x.tolist(), y=y.tolist()),
    orientation=SimpleNamespace(z=heading.tolist()),
  )


def _equivalent_curvature(path, distance: float = 7.0) -> float:
  offset = path.path_offset + path.path_angle * distance + 0.5 * path.curvature * distance ** 2 + \
    path.curvature_rate * distance ** 3 / 6.0
  return 2.0 * offset / distance ** 2


def _command(model, desired_curvature: float, *, v_ego: float = 0.0, current_curvature: float | None = None):
  return FordPathController(dt=1.0).update(model, desired_curvature, v_ego=v_ego, current_curvature=current_curvature)


def test_steady_arc_keeps_c2_with_small_continuous_pose_authority():
  path = _command(_path(0.008), 0.008, v_ego=8.0)

  assert path.valid
  assert 0.0 < path.path_offset < 0.02
  assert 0.0 < path.path_angle < 0.01
  assert np.isclose(path.curvature, 0.0052, atol=5e-5)
  assert abs(path.curvature_rate) < 1e-5


def test_gentle_changing_curve_keeps_continuous_pose_authority():
  path = _command(_path(0.004, 0.00015), 0.004, v_ego=8.0, current_curvature=0.004)

  assert abs(path.path_offset) > 0.0001
  assert abs(path.path_angle) > 0.0001
  assert 0.0 < path.curvature < 0.004


def test_c2_unloads_before_near_horizon_curve_exit():
  path = _command(_path(0.004, -0.0005), 0.004, v_ego=8.0, current_curvature=0.004)

  assert path.curvature == 0.0
  assert path.curvature_rate == 0.0
  assert path.path_angle < 0.02


def test_tight_curve_unwind_keeps_fast_pose_without_loading_c2():
  steady = _command(_path(0.015), 0.015, v_ego=10.0, current_curvature=0.012)
  unwinding = _command(_path(0.015, -0.0005), 0.015, v_ego=10.0, current_curvature=0.012)

  assert steady.curvature == 0.0
  assert unwinding.curvature == 0.0
  assert abs(_equivalent_curvature(unwinding)) > 0.9 * abs(_equivalent_curvature(steady))


def test_action_curvature_wins_over_opposing_model_geometry():
  path = _command(_path(0.008), -0.004, v_ego=7.0, current_curvature=0.0)

  assert path.path_angle < 0.0
  assert _equivalent_curvature(path) < -0.003


def test_changing_path_keeps_c3_zero_without_software_drain():
  controller = FordPathController()
  for _ in range(100):
    changing = controller.update(_path(0.004, 0.001), 0.004, v_ego=15.0, current_curvature=0.004)
  flat = controller.update(_path(0.004), 0.004, v_ego=15.0, current_curvature=0.004)

  assert changing.curvature_rate == 0.0
  assert flat.curvature_rate == 0.0


def test_sunnypilot_path_message_round_trip():
  message = custom.CarControlSP.new_message()
  message.fordLateralPath.pathOffset = 0.3
  message.fordLateralPath.pathAngle = -0.2
  message.fordLateralPath.curvature = 0.008
  message.fordLateralPath.curvatureRate = -0.0004
  message.fordLateralPath.valid = True

  path = convert_carControlSP(message.as_reader()).fordLateralPath
  assert np.isclose(path.pathOffset, 0.3)
  assert np.isclose(path.pathAngle, -0.2)
  assert np.isclose(path.curvature, 0.008)
  assert np.isclose(path.curvatureRate, -0.0004)
  assert path.valid


def test_tight_arc_uses_signed_forward_pose_without_slow_c2():
  left = _command(_path(0.04), 0.04, v_ego=8.0)
  right = _command(_path(-0.04), -0.04, v_ego=8.0)

  assert left.curvature == 0.0
  assert right.curvature == 0.0
  assert abs(left.curvature_rate) < 1e-4
  assert abs(right.curvature_rate) < 1e-4
  assert left.path_angle > 0.06
  assert right.path_angle < -0.06
  assert left.path_offset > 0.5
  assert right.path_offset < -0.5


def test_c2_does_not_increase_while_tight_curve_unwinds():
  curvatures = (0.04, 0.018, 0.016, 0.014, 0.012, 0.010, 0.008, 0.006, 0.0)
  measured = (0.04,) + curvatures[:-1]
  commands = [_command(_path(curvature), curvature, v_ego=8.0, current_curvature=actual).curvature
              for curvature, actual in zip(curvatures, measured, strict=True)]

  assert np.all(np.diff(commands) <= 1e-9)


def test_fresh_model_replaces_previous_path_without_hidden_state():
  controller = FordPathController(dt=1.0)
  initial = controller.update(_path(0.04), 0.04, v_ego=8.0)
  replanned = controller.update(_path(0.0), 0.0, v_ego=8.0)

  assert initial.path_offset > 0.5
  assert replanned == FordPathController().update(_path(0.0), 0.0, v_ego=8.0)


def test_s_turn_reverses_fast_fields_while_c2_is_bounded():
  controller = FordPathController(dt=0.05)
  controller.update(_path(0.04), 0.04, v_ego=8.0)
  controller.update(_path(0.04), 0.04, v_ego=8.0)

  outputs = []
  for frame_id in range(5):
    model = _path(-0.02)
    model.frameId = frame_id + 1
    model.timestampEof = frame_id + 1
    outputs.append(controller.update(model, -0.02, v_ego=8.0, current_curvature=0.02))

  assert all(path.valid for path in outputs)
  assert all(DBC_CURVATURE[0] <= path.curvature <= DBC_CURVATURE[1] for path in outputs)
  assert all(path.curvature <= 0.0 for path in outputs)
  assert outputs[-1].path_angle < -0.03
  assert outputs[-1].path_offset < 0.0


def test_reversal_does_not_add_software_persistence_to_centering_c2():
  controller = FordPathController()
  assert controller.update(_path(0.002), 0.002, v_ego=8.0).curvature > 0.0

  reversing = controller.update(_path(-0.02), -0.02, v_ego=8.0)

  assert reversing.curvature <= 0.0


def test_requested_turn_is_not_cancelled_by_previous_path():
  controller = FordPathController(dt=1.0)
  previous = _path(-0.02, speed=3.0)
  previous.frameId = 1
  previous.timestampEof = 1
  controller.update(previous, -0.02, v_ego=3.0, current_curvature=-0.01)

  requested = _path(0.02, speed=3.0)
  requested.frameId = 2
  requested.timestampEof = 2
  command = controller.update(requested, 0.02, v_ego=3.0, current_curvature=0.007)

  assert command.path_offset >= 0.0
  assert command.path_angle >= 0.0
  assert command.curvature >= 0.0
  assert _equivalent_curvature(command) >= 0.02


def test_short_low_speed_model_uses_available_path_endpoint():
  command = FordPathController().update(_path(0.02, speed=1.0), 0.02, v_ego=1.0, current_curvature=0.0)

  assert command.valid
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0


def test_action_demand_exposes_forward_path_authority():
  command = FordPathController().update(_path(0.002), 0.0055, v_ego=8.0, current_curvature=0.0005)

  assert _equivalent_curvature(command) >= 0.004


def test_model_curvature_does_not_change_fast_command_for_same_action():
  gentle_model = _command(_path(0.004), 0.004, v_ego=8.0, current_curvature=0.002)
  aggressive_model = _command(_path(0.04), 0.004, v_ego=8.0, current_curvature=0.002)

  assert np.isclose(aggressive_model.path_offset, gentle_model.path_offset)
  assert np.isclose(aggressive_model.path_angle, gentle_model.path_angle)


def test_fast_fields_encode_one_virtual_curvature():
  command = _command(_path(0.004), 0.008, v_ego=8.0, current_curvature=0.0)

  offset_curvature = 2.0 * command.path_offset / 7.0 ** 2
  angle_curvature = command.path_angle / 8.0
  assert np.isclose(offset_curvature, angle_curvature)


def test_action_turn_exposes_fast_authority_without_large_model_arc():
  command = FordPathController(dt=1.0).update(_path(0.002), 0.04, v_ego=8.0, current_curvature=0.002)

  assert command.curvature == 0.0
  assert command.path_offset > 0.5
  assert command.path_angle > 0.2


def test_minor_curve_blends_c2_with_small_pose_authority_when_tracking_is_close():
  command = FordPathController(dt=1.0).update(_path(0.005), 0.005, v_ego=8.0, current_curvature=0.0048)

  assert 0.0 < command.path_offset < 0.01
  assert 0.0 < command.path_angle < 0.01
  assert command.curvature > 0.003


def test_minor_changing_curve_keeps_future_geometry_in_pose_not_c3():
  command = FordPathController(dt=1.0).update(_path(0.005, 0.0003), 0.005, v_ego=8.0, current_curvature=0.0048)

  assert abs(command.path_offset) < 0.02
  assert abs(command.path_angle) < 0.01
  assert command.curvature > 0.003
  assert command.curvature_rate == 0.0


def test_c2_uses_stable_action_curvature_not_independent_model_fit():
  controller = FordPathController(dt=1.0)
  first = controller.update(_path(0.004), 0.002, v_ego=8.0, current_curvature=0.002)
  second = controller.update(_path(0.006), 0.002, v_ego=8.0, current_curvature=0.002)

  assert np.isclose(first.curvature, 0.0013)
  assert np.isclose(second.curvature, 0.0013)


def test_action_curvature_corrects_stale_opposing_model_at_low_speed():
  command = FordPathController().update(_path(-0.001, speed=1.0), 0.005, v_ego=1.0, current_curvature=0.001)

  assert command.path_offset > 0.0
  assert command.path_angle > 0.0
  assert command.curvature >= 0.0
  assert _equivalent_curvature(command) >= 0.004


def test_action_sign_wins_over_opposing_model_path():
  command = FordPathController(dt=1.0).update(_path(0.04), -0.0005, v_ego=6.0, current_curvature=0.02)

  assert command.path_offset < 0.0
  assert command.path_angle < 0.0
  assert _equivalent_curvature(command) < 0.0


def test_measured_curvature_after_path_exit_commands_countersteer():
  command = FordPathController().update(_path(0.0), 0.0, v_ego=8.0, current_curvature=0.006)

  assert command.curvature == 0.0
  assert command.path_offset < 0.0
  assert command.path_angle < 0.0


def test_measured_curvature_countersteers_when_beyond_modeled_arc():
  controller = FordPathController(dt=1.0)
  command = controller.update(_path(0.004), 0.003, v_ego=8.0, current_curvature=0.012)
  tracking = FordPathController(dt=1.0).update(_path(0.004), 0.003, v_ego=8.0, current_curvature=0.004)

  assert command.path_offset < 0.0
  assert command.path_angle < 0.0
  assert command.path_angle < tracking.path_angle
  assert command.curvature == 0.0


def test_model_reversal_suppresses_old_c2_and_countersteers():
  reversing = FordPathController().update(_path(-0.02), -0.0005, v_ego=8.0, current_curvature=0.01)

  assert reversing.curvature <= 0.0
  assert reversing.path_angle < 0.0


def test_reversal_noise_band_is_continuous():
  inside = FordPathController(dt=1.0).update(_path(0.02), -0.000099, v_ego=8.0, current_curvature=0.01)
  outside = FordPathController(dt=1.0).update(_path(0.02), -0.000101, v_ego=8.0, current_curvature=0.01)

  assert abs(outside.path_angle - inside.path_angle) < 0.005


def test_curvature_error_increases_forward_pose_command_while_behind():
  behind = FordPathController(dt=1.0).update(_path(0.008), 0.008, v_ego=15.0, current_curvature=0.0)
  tracking = FordPathController(dt=1.0).update(_path(0.008), 0.008, v_ego=15.0, current_curvature=0.008)

  assert behind.path_offset > tracking.path_offset + 0.01
  assert behind.path_angle > tracking.path_angle + 0.015
  assert np.isclose(behind.curvature, tracking.curvature)
  assert tracking.curvature > 0.005
  assert np.isclose(behind.curvature_rate, tracking.curvature_rate)


def test_measured_wheel_beyond_action_countersteers_model_arc():
  controller = FordPathController()
  controller.update(_path(0.02), 0.02, v_ego=15.0, current_curvature=0.02)
  outputs = [controller.update(_path(0.02), 0.003, v_ego=15.0, current_curvature=0.01) for _ in range(4)]
  unwinding = outputs[-1]

  assert unwinding.curvature == 0.0
  assert unwinding.path_angle < 0.0


def test_action_c2_remains_active_for_centering():
  centering = FordPathController(dt=1.0).update(_path(0.002), 0.002, v_ego=15.0, current_curvature=0.002)

  assert centering.curvature > 0.001
  assert centering.path_offset > 0.0
  assert centering.path_angle > 0.0


def test_tight_turn_from_stop_builds_bounded_forward_pose_authority():
  controller = FordPathController()
  outputs = [controller.update(_path(0.04), 0.04, v_ego=0.0, current_curvature=0.0) for _ in range(20)]
  path = outputs[-1]

  assert path.curvature == 0.0
  assert path.path_offset > 0.7
  assert path.path_angle > 0.15
  assert np.max(np.abs(np.diff([output.path_offset for output in outputs]))) <= 0.04 + 1e-9
  assert np.max(np.abs(np.diff([output.path_angle for output in outputs]))) <= 0.01 + 1e-9


def test_curvature_feedback_is_bounded_for_bad_measurement():
  bounded = FordPathController().update(_path(0.008), 0.008, v_ego=15.0, current_curvature=-0.02)
  corrupted = FordPathController().update(_path(0.008), 0.008, v_ego=15.0, current_curvature=-1.0)

  assert np.isclose(corrupted.path_angle, bounded.path_angle)


def test_invalid_model_ramps_pose_to_zero_while_remaining_in_extended_mode():
  controller = FordPathController()
  for _ in range(10):
    active = controller.update(_path(0.04), 0.04, v_ego=12.0)
  missing = controller.update(None, 0.0, v_ego=12.0)

  assert active.path_offset > 0.0
  assert missing.valid
  assert np.isclose(active.path_offset - missing.path_offset, 0.04)
  assert missing.curvature == 0.0
  assert not controller.update(_path(0.0), 0.0, v_ego=12.0, active=False).valid
