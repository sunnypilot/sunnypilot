"""Exercise the opt-in trial through the production Ford CAN packer."""
import copy
import itertools
import json
import math
from collections import defaultdict
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car import Bus, structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.values import FordFlags
from opendbc.car.interfaces import CarInterfaceBase
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.car.ford_joint_control import FordJointControl, joint_control_enabled, select_joint_control
from openpilot.selfdrive.controls.lib.ford_joint.angle import AngleModel
from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease, state
from openpilot.selfdrive.controls.lib.ford_joint.inverse import invert_angle
from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import update
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import car_params, startup


def cp():
  return structs.CarParams(brand='ford', flags=int(FordFlags.CANFD), carFingerprint='FORD_F_150_LIGHTNING_MK1', wheelbase=3.7, steerRatio=16.9)


def controls(target=30., active=True):
  cc = structs.CarControl(latActive=active, longActive=True)
  cc.actuators.steeringAngleDeg = target
  cc.actuators.accel = .3
  sp = structs.CarControlSP()
  sp.fordLateralPath.enabled = sp.fordLateralPath.valid = True
  return cc, sp


class Pipeline:
  def __init__(self):
    self.joint = FordJointControl(cp())
    self.sender = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp(), structs.CarParamsSP())
    self.cs = structs.CarState(vEgo=5.36, vEgoRaw=5.36, canValid=True)
    self.vehicle = SimpleNamespace(out=self.cs, acc_tja_status_stock_values=defaultdict(int),
                                   lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
    self.interface = SimpleNamespace(CC=self.sender, CS=self.vehicle)

  def tick(self, now, target=30., active=True, **kwargs):
    cc, sp = controls(target, active)
    result = self.joint.prepare(cc.as_reader(), sp, self.cs, now, **kwargs)
    _, packets = CarInterfaceBase.apply(self.interface, result, sp, round(now * 1e9))
    assert sum(p[0] == 0x3d6 for p in packets) == 1
    self.joint.record_sent(packets, round(now * 1e9))
    assert result.longActive and result.actuators.accel == cc.actuators.accel
    wire = self.joint.parser.vl['LateralMotionControl2']
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
    assert abs(wire['LatCtlPathOffst_L_Actl']) <= 5.11 + 1e-10
    assert abs(wire['LatCtlPath_An_Actl']) <= .5 + 1e-10
    assert wire['LatCtl_D2_Rq'] == (2 if result.latActive else 0)
    assert self.joint.sent == pytest.approx((*self.joint.diagnostics['wire_command'], result.latActive))
    return result


@pytest.mark.parametrize('master,trial,geometry,joystick', itertools.product((False, True), repeat=4))
@pytest.mark.parametrize('compatible', [False, True])
def test_startup_gate_matches_both_processes(master, trial, geometry, joystick, compatible):
  params = SimpleNamespace(get_bool=lambda k: {'FordModelActionController': master, 'FordPscmJointControl': trial,
                                              'FordGeometryReference': geometry, 'JoystickDebugMode': joystick}.get(k, False))
  params_cp = car_params(flags=FordFlags.CANFD if compatible else 0)
  expected = compatible and master and trial and not geometry and not joystick
  assert joint_control_enabled(params_cp, params) == expected
  selected = startup(params_cp, params).ford_path_controller
  assert bool(selected and selected.joint_control) == expected
  if not expected:
    assert select_joint_control(params_cp, params) is None
  if not master:
    assert selected is None


def test_parameter_is_persistent_default_off(tmp_path):
  params = Params(str(tmp_path))
  assert params.get_default_value('FordPscmJointControl') is False
  assert not params.get_bool('FordPscmJointControl')
  for flag in (ParamKeyFlag.PERSISTENT, ParamKeyFlag.BACKUP):
    assert b'FordPscmJointControl' in params.all_keys(flag)


def test_reference_carrier_adds_no_second_feedback_loop():
  from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
  c = FordModelActionController(joint_control=True, c0_time_based=True)
  for i in range(100):
    p = update(c, now=1+i*.01, current_curvature=-.005)
    assert p.valid and p.path_offset == p.path_angle == p.curvature == p.curvature_rate == 0.
    assert c.core.correction == c.core.proportional == c.core.offset_proportional == 0.
  assert not c.set_c0_time_based(True, lateral_engaged=False)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_can_coordinates_entry_reversal_release_and_100hz(sign):
  p = Pipeline()
  for i in range(250):
    target = sign * (30. if i < 80 else -30. if i < 160 else 0.)
    assert p.tick(1+i*.01, target).latActive
    if i == 0:
      # The existing sender negates OP path fields; the adapter compensates once.
      assert sign * p.joint.sent[0] > 0 and sign * p.joint.sent[1] > 0
    json.dumps(p.joint.diagnostics, allow_nan=False)
  assert not p.joint.fault


def test_observer_follows_packed_command_only_and_inactive_slew():
  p = Pipeline()
  cc, sp = controls()
  before = state(p.joint.request).copy()
  p.joint.prepare(cc, sp, p.cs, 1.)  # An untransmitted candidate is not held input.
  p.joint.advance(1.01)
  np.testing.assert_array_equal(state(p.joint.request), before)
  for i in range(100):
    p.tick(1.02+i*.01, 60.)
  held = copy.copy(p.joint.request)
  p.cs.steeringPressed = True
  result = p.tick(2.02, 60.)
  assert not result.latActive and p.joint.sent == (0., 0., False)
  assert abs(p.joint.request.c0) > 0 or abs(p.joint.request.c1) > 0
  held = copy.copy(p.joint.request)
  phase = p.joint.phase
  p.tick(2.03, 60.)
  ticks = int((phase+.01+1e-12)/.008)
  for _ in range(ticks):
    held.step(5.36*3.6, 0., 0., active=False, freeze_i=True)
  np.testing.assert_allclose(state(p.joint.request), state(held), atol=1e-12)
  p.cs.steeringPressed = False
  assert p.tick(2.04, -30.).latActive
  assert p.joint.diagnostics['requested_angle'] == -30.


@pytest.mark.parametrize('limit,denied,active', [(0, False, True), (2, False, True), (3, False, False), (0, True, False)])
def test_limit_reached_does_not_freeze_but_override_inhibits(limit, denied, active):
  p = Pipeline()
  status = SimpleNamespace(valid=True, canMonoTime=1_000_000_000, limit=limit, denied=denied)
  assert p.tick(1., pscm_status=status).latActive == active


@pytest.mark.parametrize('field,value', [('vEgo', 0.), ('vEgo', .29), ('vEgo', 56.), ('yawRate', 3.1),
                                       ('steeringAngleDeg', math.nan), ('vEgo', math.inf), ('canValid', False),
                                       ('steerFaultTemporary', True), ('steerFaultPermanent', True)])
def test_bad_measurements_never_send_previous_request(field, value):
  p = Pipeline()
  p.tick(1.)
  setattr(p.cs, field, value)
  assert not p.tick(1.01).latActive
  assert p.joint.sent == (0., 0., False)
  json.dumps(p.joint.diagnostics, allow_nan=False)


@pytest.mark.parametrize('target', [math.nan, math.inf, -math.inf])
def test_nonfinite_target_and_stale_control_are_inactive(target):
  p = Pipeline()
  assert not p.tick(1., target).latActive
  assert not p.tick(1.01, fresh=False).latActive
  assert p.tick(1.02).latActive


@pytest.mark.parametrize('next_time', [.9, 1.101])
def test_unknown_clock_history_latches_inactive(next_time):
  p = Pipeline()
  p.tick(1.)
  assert not p.tick(next_time).latActive
  assert not p.tick(next_time+.01).latActive
  assert p.joint.fault


def test_angle_inverse_matches_forward_stage_across_speeds():
  rng = np.random.default_rng(418)
  for _ in range(80):
    m = AngleModel(MainRequest().cal)
    m.yaw_acc, m.bank_residual, m.angle_bias = rng.uniform(-1., 1., 3)
    speed = float(rng.uniform(1.1, 180.))
    target, angle = map(float, rng.uniform(-300., 300., 2))
    yaw = float(rng.uniform(-.5, .5))
    result = invert_angle(m, speed, target, angle, yaw, yaw*speed/3.6, 3.7, 16.9)
    actual = m.step(speed, result['curvature'], angle, yaw, yaw*speed/3.6, 3.7, 16.9)
    assert actual == pytest.approx(result['reachable_target'], abs=1e-9)
    assert abs(result['bounded_accel']) <= result['allowance']


def test_candidate_does_not_mutate_state_and_native_step_matches_python():
  rng = np.random.default_rng(919)
  for j in range(40):
    m = MainRequest(native_lookup=True)
    m.c0, m.c1, m.filtered = map(float, rng.uniform([-5., -.49, -.08], [5., .49, .08]))
    m.fast = bool(j % 2)
    speed, curvature = float(rng.uniform(1.1, 180.)), float(rng.uniform(-.1, .1))
    old = state(m).copy()
    pair, info = PairedRelease(m).choose(speed, curvature, phase=j % 10)
    np.testing.assert_array_equal(state(m), old)
    for _ in range(info['count']):
      m.step(speed, *pair, freeze_i=True)
    np.testing.assert_allclose(state(m), info['first_state'], atol=1e-12, rtol=0)
    assert abs(info['first_state'][3]-info['planned_target']) <= info['immediate_error_bound']+1e-12


@pytest.mark.parametrize('active,override', list(itertools.product((False, True), repeat=2)))
def test_card_transmit_hook_and_fault_alert_use_actual_source(active, override):
  import ast
  from pathlib import Path
  from openpilot.cereal import custom
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  source_path = Path(__file__).resolve().parents[1] / 'card.py'
  tree = ast.parse(source_path.read_text())
  car = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Car')
  method = next(n for n in car.body if isinstance(n, ast.FunctionDef) and n.name == 'controls_update')
  branch = next(n for n in method.body if isinstance(n, ast.If) and ast.unparse(n.test) == "self.sm.all_alive(['carControl'])")
  code = compile(ast.Module(body=[branch], type_ignores=[]), str(source_path), 'exec')
  p = Pipeline()
  p.cs.steeringPressed = override
  sent = []
  owner = SimpleNamespace(ford_joint_control=p.joint, sm=SimpleNamespace(all_alive=lambda _: True, all_checks=lambda _: True, frame=1),
                          CI=SimpleNamespace(apply=lambda cc, sp, now: CarInterfaceBase.apply(p.interface, cc, sp, now)),
                          pm=SimpleNamespace(send=lambda service, data: sent.append((service, data))))
  cc, _ = controls(active=active)
  original = cc.to_dict()
  sp = custom.CarControlSP.new_message()
  sp.fordLateralPath.enabled = sp.fordLateralPath.valid = True
  exec(code, {'self': owner, 'CC': cc.as_reader(), 'CC_SP': sp, 'CS': p.cs, 'pscm_status': None, 'REPLAY': False,
              'time': SimpleNamespace(monotonic=lambda: 1.), 'convert_carControlSP': convert_carControlSP,
              'can_list_to_can_capnp': lambda data, **kwargs: data})
  assert sent[0][0] == 'sendcan'
  assert p.joint.sent[2] == (active and not override)
  assert p.joint.last_sent_time == 1.
  assert owner.CC_prev.to_dict() == {**original, 'latActive': active and not override}
  assert cc.to_dict() == original

  update_method = next(n for n in car.body if isinstance(n, ast.FunctionDef) and n.name == 'state_update')
  alert = next(n for n in update_method.body if isinstance(n, ast.If) and 'self.ford_joint_control.fault' in ast.unparse(n.test))
  alert_code = compile(ast.Module(body=[alert], type_ignores=[]), str(source_path), 'exec')
  p.joint.fault = 'command_timing_gap'
  exec(alert_code, {'self': owner, 'CS': p.cs})
  assert p.cs.steerFaultTemporary


def test_nonfinite_native_result_latches_inactive(monkeypatch):
  from openpilot.selfdrive.controls.lib.ford_joint.encoder import LIB
  p = Pipeline()
  monkeypatch.setattr(LIB, 'paired_select', lambda *args: None)
  assert not p.tick(1.).latActive
  assert p.joint.fault == 'invalid_prediction'


def test_duplicate_clock_and_missing_receipts_cannot_advance_unknown_history():
  p = Pipeline()
  p.tick(1.)
  assert p.tick(1.).latActive
  assert state(p.joint.request).tolist() == [0., 0., 0., 0., 0.]
  # Prepare can run without sending, but stale TX history must end the trial.
  for now in (1.05, 1.10, 1.15):
    cc, sp = controls()
    result = p.joint.prepare(cc, sp, p.cs, now)
  assert not result.latActive and p.joint.fault == 'missing_transmit_history'
