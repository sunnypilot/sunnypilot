import math
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.ford_path import (DBC_ANGLE, DBC_CURVATURE, DBC_OFFSET, FordPathController,
                                                        _encode_path, _model_path, _predicted_pose, _relative_pose)


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


def _command(model, desired_curvature: float, *, current_curvature: float = 0.0, v_ego: float = 8.0):
  return FordPathController(dt=1.0).update(model, desired_curvature, current_curvature=current_curvature, v_ego=v_ego)


def _equivalent_curvature(command) -> float:
  return 2.0 * command.path_offset / 7.0 ** 2 + 2.0 * command.path_angle / 7.0 + command.curvature


def test_gentle_path_uses_only_c2():
  command = _command(_path(0.004, speed=20.0), 0.004, current_curvature=0.004, v_ego=20.0)
  assert command.valid
  assert command.path_offset == 0.0
  assert command.path_angle == 0.0
  assert np.isclose(command.curvature, 0.004)
  assert command.curvature_rate == 0.0


def test_spatially_growing_path_adds_fast_pose_before_action_becomes_large():
  controller = FordPathController(dt=1.0)
  command = controller.update(_changing_path(0.0, 0.04), 0.012, current_curvature=0.0, v_ego=8.0)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0
  assert command.curvature < 0.012
  assert command.curvature_rate == 0.0


def test_growing_model_pose_adds_authority_but_c3_is_never_transmitted():
  constant = _command(_path(0.012), 0.012)
  growing = _command(_changing_path(0.0, 0.04), 0.012)
  assert _equivalent_curvature(growing) > _equivalent_curvature(constant)
  assert constant.curvature_rate == 0.0
  assert growing.curvature_rate == 0.0


def test_local_tracking_error_corrects_without_replacing_forward_pose():
  model = _changing_path(0.0, 0.04)
  local_curvature = 0.5 * 0.04 * 2.0 / 7.0
  aligned = _command(model, 0.012, current_curvature=local_curvature)
  under = _command(model, 0.012, current_curvature=0.0)
  assert aligned.path_offset > 0.0
  assert aligned.path_angle > 0.0
  assert under.path_offset > aligned.path_offset
  assert under.path_angle > aligned.path_angle


def test_large_maneuver_uses_fast_pose_and_zeros_c2():
  command = _command(_path(0.04), 0.04)
  assert command.path_offset > 0.5
  assert command.path_angle > 0.2
  assert command.curvature == 0.0
  assert command.curvature_rate == 0.0


def test_model_pose_can_trigger_maneuver_when_action_is_late():
  command = _command(_path(0.04), 0.002)
  assert command.path_offset > 0.5
  assert command.path_angle > 0.2
  assert command.curvature == 0.0


def test_action_can_trigger_maneuver_before_model_pose_grows():
  command = _command(_path(0.002), 0.04)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0
  assert command.curvature == 0.0


def test_nearby_demands_blend_continuously_without_a_mode_threshold():
  low = _command(_path(0.0119), 0.0119)
  high = _command(_path(0.0121), 0.0121)
  assert abs(high.path_offset - low.path_offset) < 0.05
  assert abs(high.path_angle - low.path_angle) < 0.03
  assert abs(high.curvature - low.curvature) < 0.001


def test_leaving_c2_normal_band_does_not_drop_total_authority():
  normal = _command(_path(0.006), 0.006)
  transition = _command(_path(0.0061), 0.0061)
  assert transition.curvature <= normal.curvature
  assert _equivalent_curvature(transition) >= _equivalent_curvature(normal)


def test_low_speed_still_uses_available_model_pose():
  command = _command(_path(0.04, speed=2.0), 0.04, v_ego=2.0)
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0


def test_higher_speed_advances_predicted_pose_and_extends_heading_horizon():
  model = _changing_path(0.0, 0.015, speed=20.0)
  slow = _command(model, 0.012, v_ego=7.0)
  fast = _command(model, 0.012, v_ego=20.0)
  assert fast.path_offset > slow.path_offset
  assert fast.path_angle > slow.path_angle


def test_short_model_uses_available_endpoint():
  model = _path(0.04, speed=1.0)
  command = _command(model, 0.04, v_ego=1.0)
  assert command.valid
  assert command.path_offset > 0.0
  assert command.path_angle > 0.0


def test_turn_entry_coordinates_c2_release_with_fast_pose_attack():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    assert controller.update(_path(0.004), 0.004, v_ego=8.0).curvature > 0.0
  outputs = [controller.update(_path(0.04), 0.04, current_curvature=0.01, v_ego=8.0) for _ in range(100)]
  assert 0.0 < outputs[0].curvature < 0.004
  assert outputs[0].path_offset > 0.0
  assert outputs[0].path_angle > 0.0
  assert outputs[-1].curvature == 0.0


def test_turn_exit_allows_c2_to_take_over_while_fast_pose_drains():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    controller.update(_path(0.04), 0.04, current_curvature=0.02, v_ego=8.0)
  outputs = [controller.update(_path(0.004), 0.004, current_curvature=0.004, v_ego=8.0) for _ in range(100)]
  assert 0.0 < outputs[0].curvature < 0.004
  assert outputs[0].path_offset != 0.0 or outputs[0].path_angle != 0.0
  assert outputs[-1].path_offset == 0.0
  assert outputs[-1].path_angle == 0.0


def test_100hz_handoff_preserves_total_authority_without_entry_drop_or_exit_overshoot():
  controller = FordPathController(dt=0.01)
  normal = controller.update(_path(0.006), 0.006, current_curvature=0.006, v_ego=8.0)
  entries = [controller.update(_path(0.04), 0.04, current_curvature=0.01, v_ego=8.0) for _ in range(100)]
  entry_authority = np.asarray([_equivalent_curvature(command) for command in entries])
  assert np.all(np.diff(entry_authority) >= -1e-9)
  assert entry_authority[0] >= _equivalent_curvature(normal)

  exits = [controller.update(_path(0.004), 0.004, current_curvature=0.004, v_ego=8.0) for _ in range(100)]
  exit_authority = np.asarray([_equivalent_curvature(command) for command in exits])
  assert np.all(np.diff(exit_authority) <= 1e-9)
  assert np.all(exit_authority >= 0.004 - 1e-9)


def test_measured_tracking_error_closes_bidirectionally_without_abandoning_the_turn():
  model = _path(0.04)
  under = _command(model, 0.04, current_curvature=0.005)
  on_target = _command(model, 0.04, current_curvature=0.04)
  over = _command(model, 0.04, current_curvature=0.05)
  assert under.path_offset > on_target.path_offset
  assert under.path_angle > on_target.path_angle
  assert 0.0 < over.path_offset < on_target.path_offset
  assert 0.0 < over.path_angle < on_target.path_angle


def test_gentle_curve_leaves_tracking_to_centering_c2():
  model = _path(0.004)
  under = _command(model, 0.004, current_curvature=0.002)
  on_target = _command(model, 0.004, current_curvature=0.004)
  over = _command(model, 0.004, current_curvature=0.006)
  assert under.path_offset == on_target.path_offset == over.path_offset == 0.0
  assert under.path_angle == on_target.path_angle == over.path_angle == 0.0
  assert under.curvature == on_target.curvature == over.curvature == 0.004


def test_recent_curvature_trend_advances_vehicle_pose_without_a_response_gain():
  model = _model_path(_path(0.04))
  assert model is not None
  constant = _encode_path(model, 0.04, current_curvature=0.02, curvature_delta=0.0, v_ego=8.0)
  rising = _encode_path(model, 0.04, current_curvature=0.02, curvature_delta=0.01, v_ego=8.0)
  assert 0.0 < rising.path_offset < constant.path_offset
  assert 0.0 < rising.path_angle < constant.path_angle


def test_model_path_exit_zeros_lingering_c2_and_countersteers():
  command = _command(_path(0.0), 0.004, current_curvature=0.006)
  assert command.path_offset < 0.0
  assert command.path_angle < 0.0
  assert command.curvature == 0.0


def test_model_path_reversal_zeros_opposing_lingering_c2():
  command = _command(_path(-0.004), 0.004, current_curvature=0.002)
  assert command.path_offset < 0.0
  assert command.path_angle < 0.0
  assert command.curvature == 0.0


def test_s_turn_reverses_model_pose_without_slow_c2():
  controller = FordPathController(dt=0.05)
  for _ in range(10):
    controller.update(_path(0.04), 0.04, v_ego=8.0)
  outputs = [controller.update(_path(-0.04), -0.04, v_ego=8.0) for _ in range(10)]
  assert all(command.curvature == 0.0 for command in outputs)
  assert np.all(np.diff([command.path_offset for command in outputs]) < 0.0)
  assert np.all(np.diff([command.path_angle for command in outputs]) < 0.0)
  assert outputs[-1].path_offset < 0.0
  assert outputs[-1].path_angle < 0.0


def test_output_limits_and_rates_are_bounded():
  controller = FordPathController()
  outputs = [controller.update(_path(0.2), 0.2, v_ego=8.0) for _ in range(100)]
  assert all(DBC_OFFSET[0] <= command.path_offset <= DBC_OFFSET[1] for command in outputs)
  assert all(DBC_ANGLE[0] <= command.path_angle <= DBC_ANGLE[1] for command in outputs)
  assert all(DBC_CURVATURE[0] <= command.curvature <= DBC_CURVATURE[1] for command in outputs)
  assert np.max(np.abs(np.diff([command.path_offset for command in outputs]))) <= 0.04 + 1e-9
  assert np.max(np.abs(np.diff([command.path_angle for command in outputs]))) <= 0.01 + 1e-9


def test_clipped_path_angle_uses_available_offset_to_preserve_endpoint():
  horizon = 7.0
  for curvature, angle_limit in ((-0.1, DBC_ANGLE[0]), (0.1, DBC_ANGLE[1])):
    model = _path(curvature)
    command = _command(model, curvature, current_curvature=curvature, v_ego=horizon)
    path = _model_path(model)
    assert path is not None
    advance = 0.1 * horizon
    model_offset, model_angle = _relative_pose(advance + horizon, path,
                                                _predicted_pose(advance, curvature, 0.0))

    assert command.path_angle == angle_limit
    assert np.isclose(command.path_offset + horizon * command.path_angle,
                      model_offset + horizon * model_angle)


def test_invalid_model_ramps_pose_to_zero_and_inactive_resets():
  controller = FordPathController(dt=0.01)
  for _ in range(20):
    active = controller.update(_path(0.04), 0.04, v_ego=8.0)
  invalid = controller.update(None, 0.0, v_ego=8.0)
  assert invalid.valid
  assert abs(invalid.path_offset) < abs(active.path_offset)
  assert abs(invalid.path_angle) < abs(active.path_angle)
  assert not controller.update(_path(0.0), 0.0, v_ego=8.0, active=False).valid


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
