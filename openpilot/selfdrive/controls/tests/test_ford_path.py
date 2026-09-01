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


def _model_pose(model, lookahead: float) -> tuple[float, float]:
  x = np.asarray(model.position.x)
  y = np.asarray(model.position.y)
  heading = np.asarray(model.orientation.z)
  distance = np.concatenate(([0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))))
  horizon = min(lookahead, distance[-1])
  return float(np.interp(horizon, distance, y)), float(np.interp(horizon, distance, heading))


def _command(model, desired_curvature: float, *, v_ego: float = 8.0):
  return FordPathController(dt=1.0).update(model, desired_curvature, v_ego=v_ego)


def test_gentle_path_uses_only_c2():
  command = _command(_path(0.008, speed=20.0), 0.008, v_ego=20.0)
  assert command.valid
  assert command.path_offset == 0.0
  assert command.path_angle == 0.0
  assert np.isclose(command.curvature, 0.008)
  assert command.curvature_rate == 0.0


def test_large_maneuver_uses_model_pose_and_immediately_zeros_c2():
  model = _path(0.04)
  expected_offset, expected_angle = _model_pose(model, 7.0)
  command = _command(model, 0.04)
  assert np.isclose(command.path_offset, expected_offset)
  assert np.isclose(command.path_angle, expected_angle)
  assert command.curvature == 0.0


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


def test_maneuver_handoff_blends_continuously():
  model = _path(0.0105)
  expected_offset, expected_angle = _model_pose(model, 7.0)
  command = _command(model, 0.0105)
  offset_share = command.path_offset / expected_offset
  angle_share = command.path_angle / expected_angle
  assert 0.4 < offset_share < 0.6
  assert np.isclose(offset_share, angle_share)
  assert np.isclose(command.curvature / 0.0105, 1.0 - offset_share)


def test_low_speed_uses_seven_meter_lookahead_for_both_pose_fields():
  model = _path(0.04, speed=2.0)
  expected_offset, expected_angle = _model_pose(model, 7.0)
  command = _command(model, 0.04, v_ego=2.0)
  assert np.isclose(command.path_offset, expected_offset)
  assert np.isclose(command.path_angle, expected_angle)


def test_speed_uses_half_second_lookahead_for_both_pose_fields():
  model = _path(0.02, speed=15.0)
  expected_offset, expected_angle = _model_pose(model, 7.5)
  command = _command(model, 0.02, v_ego=15.0)
  assert np.isclose(command.path_offset, expected_offset)
  assert np.isclose(command.path_angle, expected_angle)


def test_short_model_uses_available_endpoint():
  model = _path(0.04, speed=1.0)
  expected_offset, expected_angle = _model_pose(model, math.inf)
  command = _command(model, 0.04, v_ego=1.0)
  assert np.isclose(command.path_offset, expected_offset)
  assert np.isclose(command.path_angle, expected_angle)


def test_turn_entry_does_not_retain_previous_gentle_c2():
  controller = FordPathController()
  for _ in range(20):
    assert controller.update(_path(0.004), 0.004, v_ego=8.0).curvature > 0.0
  turning = controller.update(_path(0.04), 0.04, v_ego=8.0)
  assert turning.curvature == 0.0


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
