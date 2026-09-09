"""Exercise the candidate through existing selection, publication and CAN code.

Tests enable the candidate through controlsd's real startup selection.
No hardware, IPC or CAN transmission is involved.
"""
import ast
from collections import defaultdict
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.values import FordFlags
from openpilot.cereal import custom
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import circle, straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup


def update(controller, now=1., **overrides):
  kwargs = {'model': straight(.4), 'desired_curvature': .01, 'speed': 20., 'yaw_rate': 0., 'now': now,
                'model_time': now, 'measurement_time': now, 'reference_time': now, 'active': True}
  kwargs.update(overrides)
  return controller.update(**kwargs)


@pytest.mark.parametrize('field', ['model_time', 'measurement_time', 'reference_time'])
@pytest.mark.parametrize('age', [.151, -.006])
def test_stale_or_future_service_clears_commands_and_reengages_from_zero(field, age):
  controller = FordModelActionController()
  update(controller)
  assert update(controller, 1.01, **{field: 1.01-age}) == FordPath()
  assert controller.diagnostics['status'] == 'stale_input'
  assert update(controller, 1.02).path_offset == pytest.approx(.04)


@pytest.mark.parametrize('change,reason', [
  ({'now': 1.}, 'timing_reset'),
  ({'now': .99}, 'timing_reset'),
  ({'now': 1.001}, 'timing_reset'),
  ({'now': 1.101}, 'timing_reset'),
  ({'model_time': .999}, 'timing_reset'),
  ({'measurement_time': .999}, 'timing_reset'),
  ({'active': False}, 'inactive'),
  ({'valid': False}, 'invalid_service'),
  ({'model': None}, 'invalid_path'),
  ({'yaw_rate': math.nan}, 'nonfinite'),
  ({'yaw_rate': 3.01}, 'input_range'),
  ({'speed': 55.01}, 'input_range'),
  ({'desired_curvature': 1.01}, 'input_range'),
])
def test_invalid_cycle_never_keeps_a_previous_active_request(change, reason):
  controller = FordModelActionController()
  update(controller)
  now = change.get('now', 1.01)
  assert update(controller, **dict(change, now=now)) == FordPath()
  assert controller.diagnostics['status'] == reason
  assert (controller.core.c0, controller.core.c1) == (0., 0.)
  assert update(controller, now+1.).path_angle == pytest.approx(.005)


@pytest.mark.parametrize('field', ['now', 'measurement_time', 'model_time', 'reference_time', 'speed', 'yaw_rate', 'desired_curvature'])
@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf, None])
def test_nonfinite_input_never_raises_or_leaks_into_diagnostics(field, value):
  controller = FordModelActionController()
  update(controller)
  assert update(controller, **{field: value}) == FordPath()
  assert controller.diagnostics['status'] == 'nonfinite'
  json.dumps(controller.diagnostics, allow_nan=False)


def test_repeated_measurements_do_not_freeze_slew_or_cache_invalid_model_geometry():
  controller = FordModelActionController()
  for i in range(10):
    result = update(controller, 1.+i*.01, measurement_time=1., model_time=1., reference_time=1.)
  assert result.path_offset == pytest.approx(.4)
  assert result.path_angle == pytest.approx(.05)
  broken = straight(.4)
  broken.position.y[5] = math.nan
  assert update(controller, 1.1, model=broken, model_time=1., measurement_time=1.) == FordPath()
  assert controller.diagnostics['status'] == 'invalid_path'


def test_yaw_offset_does_not_change_the_base():
  controllers = [FordModelActionController() for _ in range(3)]
  variants = [{}, {'yaw_rate': .0072}, {'yaw_rate': -.0072}]
  for i in range(100):
    outputs = [update(c, 1.+i*.01, **kwargs) for c, kwargs in zip(controllers, variants, strict=True)]
    assert all(out == outputs[0] for out in outputs)
  assert outputs[0].path_angle == pytest.approx(.2)


def test_reference_source_can_change_to_an_older_but_fresh_publication():
  controller = FordModelActionController()
  update(controller, reference_time=.99)
  assert update(controller, 1.01, reference_time=.98).valid


def test_release_keeps_current_geometry_and_may_grow_c0_while_c1_decreases():
  for sign in (-1., 1.):
    controller = FordModelActionController()
    for i in range(100):
      before = update(controller, 1.+i*.01, model=circle(sign*.01), desired_curvature=sign*.005)
    for i in range(100):
      after = update(controller, 2.+i*.01, model=circle(sign*.02), desired_curvature=sign*.004)
    assert abs(after.path_offset) > abs(before.path_offset)
    assert abs(after.path_angle) < abs(before.path_angle)
    for i in range(100):
      released = update(controller, 3.+i*.01, model=circle(sign*.02), desired_curvature=0.)
    assert released.path_offset == after.path_offset
    assert released.path_angle == pytest.approx(0.)


def _method(filename, class_name, method):
  tree = ast.parse(filename.read_text())
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
  return next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method)


@pytest.fixture
def pipeline():
  root = Path(__file__).resolve().parents[3]
  controls_file = root/'selfdrive/controls/controlsd.py'
  body = _method(controls_file, 'Controls', 'state_control').body
  # Execute the actual source choice, upstream limiter and Ford integration.
  selection = next(n for n in body if isinstance(n, ast.If) and ast.unparse(n.test) == "self.sm.valid['lateralManeuverPlan']")
  limiter = next(n for n in body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and
                 isinstance(n.value.func, ast.Name) and n.value.func.id == 'clip_curvature')
  branch = next(n for n in body if isinstance(n, ast.If) and ast.unparse(n.test) == "self.CP.brand == 'ford'")
  call = compile(ast.Module(body=[selection, limiter, branch], type_ignores=[]), str(controls_file), 'exec')
  publication_file = root/'sunnypilot/selfdrive/controls/controlsd_ext.py'
  body = _method(publication_file, 'ControlsExt', 'state_control_ext').body
  publish = [n for n in body if (isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'ford_path') or
             (isinstance(n, ast.If) and ast.unparse(n.test) == 'ford_path is not None')]
  assert len(publish) == 2
  publication = compile(ast.Module(body=publish, type_ignores=[]), str(publication_file), 'exec')
  return call, publication


class Subscriptions:
  frame = 1

  def __init__(self, maneuver):
    self.valid = {'lateralManeuverPlan': maneuver, 'modelV2': True}
    self.logMonoTime = {'carState': 995_000_000, 'modelV2': 980_000_000, 'lateralManeuverPlan': 990_000_000}
    self.failed = set()
    self.messages = {'carStateSP': custom.CarStateSP.new_message(), 'lateralManeuverPlan': SimpleNamespace(desiredCurvature=-.1)}

  def __getitem__(self, service):
    return self.messages[service]

  def all_checks(self, services):
    return not self.failed.intersection(services) and all(self.valid.get(s, True) for s in services)


@pytest.mark.parametrize('maneuver', [False, True])
def test_actual_controlsd_selection_limiting_publication_and_downstream_can(pipeline, maneuver):
  call, publication = pipeline
  sm = Subscriptions(maneuver)
  controls = startup()
  controller = controls.ford_path_controller
  controls.sm, controls.desired_curvature, controls.curvature = sm, 0., 0.
  model = straight(.4)
  model.action = SimpleNamespace(desiredCurvature=.1)
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=20., yawRate=-.0072, canValid=True, steeringPressed=False, steeringTorque=0.)
  environment = {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                     'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)}
  exec(call, environment)
  expected_curvature = (-1 if maneuver else 1)*.000125
  assert controls.desired_curvature == pytest.approx(expected_curvature)
  assert controls.ford_path.path_angle == pytest.approx(20.*expected_curvature)
  assert controls.ford_path.path_offset == pytest.approx(.04)
  assert cc.latActive and cc.actuators.curvature == 0.
  assert controller.diagnostics['reference_age'] == pytest.approx(.01 if maneuver else .02)

  cp = structs.CarParams(flags=int(FordFlags.CANFD), carFingerprint='FORD_F_150_LIGHTNING_MK1')
  downstream = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp, structs.CarParamsSP())
  vehicle = SimpleNamespace(out=structs.CarState(vEgo=20., vEgoRaw=20.), acc_tja_status_stock_values=defaultdict(int),
                            lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], downstream.CAN.main)
  for i, fail in enumerate((False, True)):
    if fail:
      sm.failed.add('modelV2')
      exec(call, environment)
      assert not cc.latActive and controls.ford_path == FordPath()
    msg = custom.CarControlSP.new_message()
    exec(publication, {'self': controls, 'CC_SP': msg})
    _, packets = downstream.update(cc.as_reader(), convert_carControlSP(msg.as_reader()), vehicle, (i+1)*10_000_000)
    parser.update([(i+1)*10_000_000, packets])
    wire = parser.vl['LateralMotionControl2']
    assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(-controls.ford_path.path_offset)
    assert wire['LatCtlPath_An_Actl'] == pytest.approx(-controls.ford_path.path_angle)
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
    assert wire['LatCtl_D2_Rq'] == (0 if fail else 2)


@pytest.mark.parametrize('maneuver', [False, True])
@pytest.mark.parametrize('failed', ['carState', 'modelV2', 'vehicleParameters', 'lateralManeuverPlan'])
def test_actual_controlsd_service_gates(pipeline, maneuver, failed):
  sm = Subscriptions(maneuver)
  sm.failed.add(failed)
  controls = startup()
  controls.sm, controls.desired_curvature, controls.curvature = sm, 0., 0.
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=20., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.)
  model = straight()
  model.action = SimpleNamespace(desiredCurvature=.1)
  exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                         'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)})
  assert controls.ford_path.valid == cc.latActive == (failed == 'lateralManeuverPlan' and not maneuver)
