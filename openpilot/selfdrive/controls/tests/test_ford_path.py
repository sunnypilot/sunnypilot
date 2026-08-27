import math
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.ford_path import DBC_CURVATURE, FordPathController, encode_ford_path


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


def _offset_path(offset: float, speed: float = 8.0):
  t = np.linspace(0.0, 3.0, 61)
  distance = speed * t
  return SimpleNamespace(
    position=SimpleNamespace(t=t.tolist(), x=distance.tolist(), y=np.full_like(distance, offset).tolist()),
    orientation=SimpleNamespace(z=np.zeros_like(distance).tolist()),
  )


def test_gentle_arc_is_geometric_feedforward():
  path = encode_ford_path(_path(0.008), 0.0, v_ego=8.0)

  assert path.valid
  assert abs(path.path_offset) < 1e-6
  assert abs(path.path_angle) < 2e-4
  assert np.isclose(path.curvature, 0.008, atol=5e-5)
  assert abs(path.curvature_rate) < 1e-5


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


def test_tight_arc_caps_slow_feedforward_and_moves_residual_into_fast_heading():
  left = encode_ford_path(_path(0.04), 0.0, v_ego=8.0)
  right = encode_ford_path(_path(-0.04), 0.0, v_ego=8.0)

  assert np.isclose(left.curvature, 0.008, atol=5e-5)
  assert np.isclose(right.curvature, -0.008, atol=5e-5)
  assert abs(left.curvature_rate) < 1e-4
  assert abs(right.curvature_rate) < 1e-4
  assert left.path_angle > 0.06
  assert right.path_angle < -0.06
  assert abs(left.path_offset) < 1e-9
  assert abs(right.path_offset) < 1e-9


def test_c2_does_not_increase_while_tight_curve_unwinds():
  curvatures = (0.04, 0.018, 0.016, 0.014, 0.012, 0.010, 0.008, 0.006, 0.0)
  commands = [encode_ford_path(_path(curvature), 0.0, v_ego=8.0).curvature for curvature in curvatures]

  assert np.all(np.diff(commands) <= 1e-9)


def test_lateral_delay_does_not_change_the_reference_polynomial():
  early = FordPathController().update(_path(0.012, 0.0003), v_ego=10.0, current_curvature=-0.01, actuator_delay=0.1)
  late = FordPathController().update(_path(0.012, 0.0003), v_ego=10.0, current_curvature=-0.01, actuator_delay=0.9)

  assert early == late


def test_reference_offset_is_not_erased_by_an_ego_anchored_replan():
  controller = FordPathController(dt=0.05)
  initial = controller.update(_offset_path(0.4), v_ego=8.0)
  replanned = controller.update(_path(0.0), v_ego=8.0)

  assert initial.path_offset > 0.39
  assert replanned.path_offset > 0.35


def test_s_turn_reverses_fast_fields_while_c2_is_bounded():
  controller = FordPathController(dt=0.05)
  controller.update(_path(0.04), v_ego=8.0, yaw_rate=0.0)
  controller.update(_path(0.04), v_ego=8.0, yaw_rate=0.16)

  outputs = []
  for frame_id in range(5):
    model = _path(-0.02)
    model.frameId = frame_id + 1
    model.timestampEof = frame_id + 1
    outputs.append(controller.update(model, -0.02, v_ego=8.0, current_curvature=0.02, yaw_rate=0.32))

  assert all(path.valid for path in outputs)
  assert all(DBC_CURVATURE[0] <= path.curvature <= DBC_CURVATURE[1] for path in outputs)
  assert all(path.curvature <= 0.0 for path in outputs)
  assert outputs[-1].path_angle < -0.03
  assert outputs[-1].path_offset < 0.0


def test_small_requested_reversal_suppresses_old_c2_and_countersteers():
  reversing = FordPathController().update(_path(0.02), -0.0005, v_ego=8.0, current_curvature=0.01)

  assert reversing.curvature <= 0.0
  assert reversing.path_angle < 0.0


def test_reversal_noise_band_is_continuous():
  inside = FordPathController(dt=1.0).update(_path(0.02), -0.000099, v_ego=8.0, current_curvature=0.01)
  outside = FordPathController(dt=1.0).update(_path(0.02), -0.000101, v_ego=8.0, current_curvature=0.01)

  assert abs(outside.path_angle - inside.path_angle) < 0.005


def test_same_model_advances_reference_from_measured_motion():
  model = _offset_path(0.25)
  controller = FordPathController(dt=0.05)
  before = controller.update(model, v_ego=8.0, current_curvature=0.0)
  after = controller.update(model, v_ego=8.0, yaw_rate=0.16)

  steering_controller = FordPathController(dt=0.05)
  steering_controller.update(model, v_ego=8.0)
  steering_only = steering_controller.update(model, v_ego=8.0, current_curvature=0.02)

  assert before.valid and after.valid
  assert after != before
  assert steering_only != after


def test_fresh_model_replenishes_the_rolling_horizon():
  controller = FordPathController(dt=0.01)
  for frame_id in range(100):
    model = _path(0.008, speed=20.0)
    model.frameId = frame_id + 1
    model.timestampEof = frame_id + 1
    assert controller.update(model, v_ego=20.0, yaw_rate=0.16).valid
    assert controller._reference is not None
    assert controller._reference[0][-1] >= 2.0 * 7.0 - 1e-6


def test_invalid_ford_yaw_rate_does_not_rotate_the_reference():
  model = _offset_path(0.25)
  valid = FordPathController(dt=0.01)
  invalid = FordPathController(dt=0.01)
  valid.update(model, v_ego=8.0)
  invalid.update(model, v_ego=8.0)

  expected = valid.update(model, v_ego=8.0, yaw_rate=0.0)
  sentinel = invalid.update(model, v_ego=8.0, yaw_rate=6.6066)

  assert sentinel == expected


def test_curvature_error_increases_only_the_fast_heading_command():
  behind = FordPathController(dt=0.05).update(_path(0.008), 0.008, v_ego=15.0, current_curvature=0.0)
  tracking = FordPathController(dt=0.05).update(_path(0.008), 0.008, v_ego=15.0, current_curvature=0.008)

  assert behind.path_angle > tracking.path_angle + 0.015
  assert np.isclose(behind.path_offset, tracking.path_offset)
  assert np.isclose(behind.curvature, tracking.curvature)
  assert np.isclose(behind.curvature_rate, tracking.curvature_rate)


def test_rolling_arc_stays_active_while_vehicle_unwinds():
  controller = FordPathController()
  controller.update(_path(0.02), 0.02, v_ego=15.0, current_curvature=0.02, yaw_rate=0.3)
  outputs = [controller.update(_path(0.02), 0.003, v_ego=15.0, current_curvature=0.01, yaw_rate=0.15) for _ in range(4)]
  unwinding = outputs[-1]

  assert 0.0 <= unwinding.curvature <= 0.003
  assert unwinding.path_angle > 0.03


def test_geometric_c2_remains_active_for_centering():
  centering = FordPathController().update(_path(0.002), 0.0, v_ego=15.0, current_curvature=0.0)

  assert centering.curvature > 0.001
  assert centering.path_angle > 0.0


def test_tight_turn_from_stop_uses_fast_heading_command():
  controller = FordPathController()
  outputs = [controller.update(_path(0.04), 0.04, v_ego=0.0, current_curvature=0.0) for _ in range(20)]
  path = outputs[-1]

  assert np.isclose(path.curvature, 0.008, atol=5e-5)
  assert path.path_angle > 0.15
  assert np.max(np.abs(np.diff([output.path_angle for output in outputs]))) <= 0.01 + 1e-9


def test_curvature_feedback_is_bounded_for_bad_measurement():
  bounded = FordPathController().update(_path(0.008), 0.008, v_ego=15.0, current_curvature=-0.02)
  corrupted = FordPathController().update(_path(0.008), 0.008, v_ego=15.0, current_curvature=-1.0)

  assert np.isclose(corrupted.path_angle, bounded.path_angle)


def test_invalid_or_inactive_resets_reference():
  controller = FordPathController()
  assert controller.update(_path(0.0), v_ego=12.0).valid
  assert not controller.update(_path(0.0), v_ego=12.0, active=False).valid
  assert not controller.update(None, v_ego=12.0).valid
