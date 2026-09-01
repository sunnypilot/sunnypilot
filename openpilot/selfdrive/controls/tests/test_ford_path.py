import math
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.ford_path import DBC_ANGLE, DBC_CURVATURE, DBC_OFFSET, FordPathController


def _path(curvature: float, speed: float = 8.0):
  t = np.linspace(0.0, 3.0, 61)
  distance = speed * t
  heading = curvature * distance
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


def _changing_path(start_curvature: float, end_curvature: float, speed: float = 8.0):
  t = np.linspace(0.0, 3.0, 61)
  distance = speed * t
  curvature = np.interp(distance, [distance[0], min(distance[-1], 7.0)], [start_curvature, end_curvature])
  heading = np.zeros_like(distance)
  x = np.zeros_like(distance)
  y = np.zeros_like(distance)
  for i in range(1, len(distance)):
    ds = distance[i] - distance[i - 1]
    heading[i] = heading[i - 1] + 0.5 * (curvature[i] + curvature[i - 1]) * ds
    average_heading = 0.5 * (heading[i] + heading[i - 1])
    x[i] = x[i - 1] + ds * math.cos(average_heading)
    y[i] = y[i - 1] + ds * math.sin(average_heading)
  return SimpleNamespace(
    position=SimpleNamespace(t=t.tolist(), x=x.tolist(), y=y.tolist()),
    orientation=SimpleNamespace(z=heading.tolist()),
  )


def _command(model, *, current_curvature: float = 0.0, v_ego: float = 8.0, actuator_delay: float = 0.4):
  return FordPathController(dt=1.0).update(model, current_curvature=current_curvature, v_ego=v_ego,
                                          actuator_delay=actuator_delay)


def _equivalent_curvature(command) -> float:
  return 2.0 * command.path_offset / 7.0 ** 2 + 2.0 * command.path_angle / 7.0 + command.curvature


def test_gentle_path_uses_only_c2():
  command = _command(_path(0.004, speed=20.0), current_curvature=0.004, v_ego=20.0)
  assert command.valid
  assert np.isclose(command.path_offset, 0.0)
  assert np.isclose(command.path_angle, 0.0)
  assert np.isclose(command.curvature, 0.004)
  assert command.curvature_rate == 0.0


def test_spatially_growing_path_adds_fast_pose_before_average_curvature_becomes_large():
  command = _command(_changing_path(0.0, 0.04), current_curvature=0.0, v_ego=8.0)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0
  assert command.curvature < 0.012
  assert command.curvature_rate == 0.0


def test_gentle_curvature_ramp_transfers_its_changing_share_out_of_c2():
  command = _command(_changing_path(0.0, 0.008), current_curvature=0.0, v_ego=8.0, actuator_delay=0.0)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0
  assert 0.0 < command.curvature < 0.004


def test_growing_model_pose_adds_authority_but_c3_is_never_transmitted():
  constant = _command(_path(0.012))
  growing = _command(_changing_path(0.0, 0.04))
  assert growing.path_offset > constant.path_offset
  assert growing.path_angle > constant.path_angle
  assert constant.curvature_rate == 0.0
  assert growing.curvature_rate == 0.0


def test_large_maneuver_uses_fast_pose_and_zeros_c2():
  command = _command(_path(0.04))
  assert command.path_offset > 0.5
  assert command.path_angle > 0.2
  assert command.curvature == 0.0
  assert command.curvature_rate == 0.0


def test_model_pose_alone_defines_the_maneuver():
  command = _command(_path(0.04))
  assert command.path_offset > 0.5
  assert command.path_angle > 0.2
  assert command.curvature == 0.0


def test_gentle_model_path_remains_c2_only():
  command = _command(_path(0.002))
  assert np.isclose(command.path_offset, 0.0)
  assert np.isclose(command.path_angle, 0.0)
  assert np.isclose(command.curvature, 0.002)


def test_nearby_demands_blend_continuously_without_a_mode_threshold():
  low = _command(_path(0.0119))
  high = _command(_path(0.0121))
  assert abs(high.path_offset - low.path_offset) < 0.05
  assert abs(high.path_angle - low.path_angle) < 0.03
  assert abs(high.curvature - low.curvature) < 0.001


def test_leaving_c2_normal_band_does_not_drop_total_authority():
  normal = _command(_path(0.006))
  transition = _command(_path(0.0061))
  assert transition.curvature <= normal.curvature
  assert _equivalent_curvature(transition) >= _equivalent_curvature(normal)


def test_low_speed_still_uses_available_model_pose():
  command = _command(_path(0.04, speed=2.0), v_ego=2.0)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0


def test_higher_speed_advances_farther_along_a_growing_path_during_the_same_delay():
  model = _changing_path(0.0, 0.015, speed=20.0)
  slow = _command(model, v_ego=7.0)
  fast = _command(model, v_ego=20.0)
  assert fast.path_offset > slow.path_offset
  assert fast.path_angle > slow.path_angle


def test_delay_alignment_is_invariant_while_tracking_a_constant_arc():
  model = _path(0.01, speed=20.0)
  immediate = _command(model, current_curvature=0.01, v_ego=20.0, actuator_delay=0.0)
  delayed = _command(model, current_curvature=0.01, v_ego=20.0, actuator_delay=0.4)
  assert np.isclose(delayed.path_offset, immediate.path_offset, atol=0.01)
  assert np.isclose(delayed.path_angle, immediate.path_angle, atol=0.01)
  assert np.isclose(delayed.curvature, immediate.curvature, atol=0.001)


def test_short_model_uses_available_endpoint():
  model = _path(0.04, speed=1.0)
  command = _command(model, v_ego=1.0)
  assert command.valid
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0


def test_turn_entry_coordinates_c2_release_with_fast_pose_attack():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    assert controller.update(_path(0.004), current_curvature=0.004, v_ego=8.0, actuator_delay=0.4).curvature > 0.0
  outputs = [controller.update(_path(0.04), current_curvature=0.01, v_ego=8.0, actuator_delay=0.4) for _ in range(100)]
  assert 0.0 < outputs[0].curvature < 0.004
  assert outputs[0].path_offset > 0.0
  assert outputs[0].path_angle > 0.0
  assert outputs[-1].curvature == 0.0


def test_turn_exit_allows_c2_to_take_over_while_fast_pose_drains():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    controller.update(_path(0.04), current_curvature=0.02, v_ego=8.0, actuator_delay=0.4)
  outputs = [controller.update(_path(0.004), current_curvature=0.004, v_ego=8.0, actuator_delay=0.4) for _ in range(100)]
  assert 0.0 < outputs[0].curvature < 0.004
  assert outputs[0].path_offset != 0.0 or outputs[0].path_angle != 0.0
  assert np.isclose(outputs[-1].path_offset, 0.0)
  assert np.isclose(outputs[-1].path_angle, 0.0)


def test_100hz_handoff_preserves_total_authority_without_entry_drop_or_exit_overshoot():
  controller = FordPathController(dt=0.01)
  normal = controller.update(_path(0.006), current_curvature=0.006, v_ego=8.0, actuator_delay=0.4)
  entries = [controller.update(_path(0.04), current_curvature=0.01, v_ego=8.0, actuator_delay=0.4) for _ in range(100)]
  entry_authority = np.asarray([_equivalent_curvature(command) for command in entries])
  assert np.all(np.diff(entry_authority) >= -1e-9)
  assert entry_authority[0] >= _equivalent_curvature(normal)

  exits = [controller.update(_path(0.004), current_curvature=0.004, v_ego=8.0, actuator_delay=0.4) for _ in range(100)]
  exit_authority = np.asarray([_equivalent_curvature(command) for command in exits])
  assert np.all(np.diff(exit_authority) <= 1e-9)
  assert np.all(exit_authority >= 0.004 - 1e-9)


def test_predicted_pose_makes_undertracking_grow_and_overshoot_shrink_the_remaining_path():
  model = _path(0.04)
  under = _command(model, current_curvature=0.005)
  on_target = _command(model, current_curvature=0.04)
  over = _command(model, current_curvature=0.05)
  assert under.path_offset > on_target.path_offset
  assert under.path_angle > on_target.path_angle
  assert over.path_offset < on_target.path_offset
  assert over.path_angle < on_target.path_angle


def test_s_turn_reverses_model_pose_without_slow_c2():
  controller = FordPathController(dt=0.05)
  for _ in range(10):
    controller.update(_path(0.04), v_ego=8.0, actuator_delay=0.4)
  outputs = [controller.update(_path(-0.04), v_ego=8.0, actuator_delay=0.4) for _ in range(10)]
  assert all(command.curvature == 0.0 for command in outputs)
  assert np.all(np.diff([command.path_offset for command in outputs]) < 0.0)
  assert np.all(np.diff([command.path_angle for command in outputs]) < 0.0)
  assert outputs[-1].path_offset < 0.0
  assert outputs[-1].path_angle < 0.0


def test_output_limits_and_rates_are_bounded():
  controller = FordPathController()
  outputs = [controller.update(_path(0.2), v_ego=8.0, actuator_delay=0.4) for _ in range(100)]
  assert all(DBC_OFFSET[0] <= command.path_offset <= DBC_OFFSET[1] for command in outputs)
  assert all(DBC_ANGLE[0] <= command.path_angle <= DBC_ANGLE[1] for command in outputs)
  assert all(DBC_CURVATURE[0] <= command.curvature <= DBC_CURVATURE[1] for command in outputs)
  assert np.max(np.abs(np.diff([command.path_offset for command in outputs]))) <= 0.04 + 1e-9
  assert np.max(np.abs(np.diff([command.path_angle for command in outputs]))) <= 0.01 + 1e-9


def test_clipped_path_angle_uses_available_offset_to_preserve_endpoint():
  horizon = 7.0
  for curvature, angle_limit in ((-0.1, DBC_ANGLE[0]), (0.1, DBC_ANGLE[1])):
    model = _path(curvature)
    command = _command(model, current_curvature=curvature, v_ego=horizon, actuator_delay=0.0)

    distance = np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(model.position.x), np.diff(model.position.y)))))
    model_offset = np.interp(horizon, distance, model.position.y)
    model_angle = np.interp(horizon, distance, model.orientation.z)

    assert command.path_angle == angle_limit
    assert np.isclose(command.path_offset + horizon * command.path_angle,
                      model_offset + horizon * model_angle)


def test_invalid_model_ramps_pose_to_zero_and_inactive_resets():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    active = controller.update(_path(0.04), v_ego=8.0, actuator_delay=0.4)
  invalid = controller.update(None, v_ego=8.0, actuator_delay=0.4)
  assert invalid.valid
  assert abs(invalid.path_offset) < abs(active.path_offset)
  assert abs(invalid.path_angle) < abs(active.path_angle)
  assert not controller.update(_path(0.0), v_ego=8.0, actuator_delay=0.4, active=False).valid


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
