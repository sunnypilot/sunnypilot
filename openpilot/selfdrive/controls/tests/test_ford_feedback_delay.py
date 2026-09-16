"""Feedforward remains current while feedback follows comma's request history."""
import ast
from collections import deque
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, encode_model_action
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_feedback import status


def step(controller, frame, desired, measured=0., **overrides):
  now = 1.+frame*.01
  kwargs = {'current_curvature': measured, 'speed': 5., 'yaw_rate': 0., 'now': now,
            'measurement_time': now, 'model_time': now, 'reference_time': now,
            'active': True, 'lat_delay': .2}
  kwargs.update(overrides)
  return controller.update(straight(), desired, **kwargs)


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('direct_path', [False, True])
def test_perfectly_delayed_tracking_does_not_generate_phantom_feedback(sign, direct_path):
  controller = FordModelActionController(direct_path=direct_path)
  requests = [0.]*100+[sign*.004]*100+[-sign*.003]*100+[0.]*100
  for i, desired in enumerate(requests):
    measured = requests[max(0, i-20)]
    command = step(controller, i, desired, measured)
    assert command.valid
    assert controller.core.feedback_curvature == pytest.approx(measured)
    assert controller.core.proportional == controller.core.offset_proportional == controller.core.correction == 0.
    # Current heading reverses/releases immediately even while feedback uses the old request.
    assert command.path_angle == pytest.approx(7.*desired, abs=.00025)
    if not direct_path:
      assert command.path_offset == pytest.approx(encode_model_action(straight(), desired, 5.).path_offset, abs=.005)


@pytest.mark.parametrize('delay', [-1., 0., .009, .16894637048244476, .2, .4, .99, 2.])
def test_same_buffer_index_as_comma_torque_controller(delay):
  controller = FordModelActionController()
  upstream = deque([0.]*100, maxlen=100)
  # Execute the actual upstream selection expressions, not a second copy of our formula.
  source_path = Path(__file__).resolve().parents[1]/'lib/latcontrol_torque.py'
  tree = ast.parse(source_path.read_text())
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'LatControlTorque')
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update')
  nodes = [n for n in method.body if isinstance(n, ast.Assign) and
           ast.unparse(n.targets[0]) in ('delay_frames', 'expected_lateral_accel')]
  assert len(nodes) == 2
  oracle = compile(ast.Module(body=nodes, type_ignores=[]), str(source_path), 'exec')
  torque = SimpleNamespace(dt=.01, lat_accel_request_buffer=upstream, lat_accel_request_buffer_len=100)
  for i in range(230):
    desired = .005*math.sin(i*.023)
    upstream.append(desired)
    context = {'self': torque, 'np': np, 'lat_delay': delay}
    exec(oracle, context)
    expected = context['expected_lateral_accel']
    step(controller, i, desired, lat_delay=delay)
    assert controller.core.feedback_curvature == expected
    assert controller.diagnostics['feedback_delay'] == pytest.approx((context['delay_frames']-1)*.01)


def test_history_keeps_up_while_disengaged_and_delay_changes_without_another_queue():
  controller = FordModelActionController()
  requests = []
  for i in range(170):
    desired = .00001*i
    requests.append(desired)
    if i < 130:
      assert step(controller, i, desired, active=False) == FordPath()
    else:
      delay = .1 if i < 150 else .3
      measured = requests[i-round(delay/.01)]
      step(controller, i, desired, measured, lat_delay=delay)
      assert controller.core.feedback_curvature == pytest.approx(measured)
      assert controller.core.correction == 0.


def test_persistent_error_still_builds_correction_and_repeated_measurements_do_not_double_integrate():
  controller = FordModelActionController()
  for i in range(150):
    step(controller, i, .004, active=False)
  step(controller, 150, .004, .003)
  for i in range(151, 251):
    step(controller, i, .004, .003)
  assert controller.core.proportional > 0. and controller.core.offset_proportional > 0.
  assert controller.core.correction == pytest.approx(.005)
  for i in range(251, 256):
    step(controller, i, .004, .003, measurement_time=3.5)
  assert controller.core.correction == pytest.approx(.005)


@pytest.mark.parametrize('override', ['driver', 'pscm'])
def test_driver_override_still_clears_feedback_immediately_with_delayed_reference(override):
  controller = FordModelActionController()
  for i in range(150):
    step(controller, i, .004)
  assert controller.core.correction > 0.
  kwargs = {'driver_pressed': True} if override == 'driver' else {'pscm_status': status(2.5, limit=3)}
  command = step(controller, 150, -.004, **kwargs)
  assert controller.core.proportional == controller.core.offset_proportional == controller.core.correction == 0.
  assert command.path_angle < 0.


@pytest.mark.parametrize('delay', [math.nan, math.inf, None])
def test_invalid_delay_rejects_command_without_raising(delay):
  controller = FordModelActionController()
  assert step(controller, 0, .004, lat_delay=delay) == FordPath()
  assert controller.diagnostics['status'] == 'nonfinite'


@pytest.mark.parametrize('invalid', [{'valid': False}, {'desired': math.nan}, {'lat_delay': math.nan}, {'now': 5.}])
def test_bad_input_or_timing_resets_request_history(invalid):
  controller = FordModelActionController()
  for i in range(150):
    step(controller, i, .004)
  options = dict(invalid)
  desired = options.pop('desired', .004)
  assert step(controller, 150, desired, **options) == FordPath()
  assert all(value == 0. for value in controller.request_buffer)
  assert step(controller, 151, 0.).valid
  assert controller.core.feedback_curvature == 0.
