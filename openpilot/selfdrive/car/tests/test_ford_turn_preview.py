"""Signaled preview through real model messages, SP transport and Ford packing."""
import ast
import itertools
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import custom, log
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.car.ford_joint_control import FordJointControl, select_joint_control
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.car.tests.test_ford_joint_control import Pipeline, cp
from openpilot.selfdrive.controls.lib.ford_joint.encoder import state
from openpilot.selfdrive.controls.lib.ford_turn_preview import FordTurnPreview, turn_preview_lead
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import _method
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup


def model(sign=1., action=-.01):
  m = log.ModelDataV2.new_message()
  station = np.linspace(0, 32, 33)
  m.position.x = station.tolist()
  m.position.y = np.zeros(33).tolist()
  m.orientation.z = (-sign * np.radians(station * 2.2)).tolist()
  m.action.desiredCurvature = action
  return m


def sample(sign=1., stamp=1_010_000_000):
  cue = FordTurnPreview()
  cue.update(model(sign, 0.), stamp - 50_000_000, True)
  data = cue.update(model(sign, -sign * .01), stamp, True)
  # Serialize exactly the additive production carrier; use its reader at card.
  sp = custom.CarControlSP.new_message(fordTurnPreview=data)
  with custom.CarControlSP.from_bytes(sp.to_bytes()) as parsed:
    convert_carControlSP(parsed)  # The cue is card metadata, not an opendbc field.
    return parsed.as_builder().as_reader().fordTurnPreview


def pipeline(enabled=True):
  p = Pipeline()
  p.joint = FordJointControl(cp(), turn_entry_assist=True, turn_preview=enabled)
  return p


def test_default_off_startup_and_master_fallback(tmp_path):
  params = Params(str(tmp_path))
  assert params.get_default_value('FordPscmTurnPreview') is False
  assert b'FordPscmTurnPreview' in params.all_keys(ParamKeyFlag.PERSISTENT | ParamKeyFlag.BACKUP)
  params.put_bool('FordPscmTurnPreview', True, block=True)
  assert select_joint_control(cp(), params) is None
  params.put_bool('FordModelActionController', True, block=True)
  assert select_joint_control(cp(), params) is None
  params.put_bool('FordPscmJointControl', True, block=True)
  assert select_joint_control(cp(), params).turn_preview
  for key in ('FordGeometryReference', 'JoystickDebugMode'):
    params.put_bool(key, True, block=True)
    assert select_joint_control(cp(), params) is None
    params.put_bool(key, False, block=True)
  params.put_bool('FordPscmTurnPreview', False, block=True)
  assert not select_joint_control(cp(), params).turn_preview


@pytest.mark.parametrize('master,joint,geometry,joystick,preview', list(itertools.product((False, True), repeat=5)))
def test_both_processes_select_preview_with_the_same_gates(master, joint, geometry, joystick, preview):
  flags = {'FordModelActionController': master, 'FordPscmJointControl': joint, 'FordGeometryReference': geometry,
           'JoystickDebugMode': joystick, 'FordPscmTurnPreview': preview}
  params = SimpleNamespace(get_bool=lambda key: flags.get(key, False))
  selected = select_joint_control(cp(), params)
  expected = master and joint and preview and not geometry and not joystick
  assert bool(selected and selected.turn_preview) == expected
  assert (startup(params=params).ford_turn_preview is not None) == expected


def publish_preview(tracker, message, stamp, *, healthy=True, maneuver=False):
  root = Path(__file__).resolve().parents[3]
  filename = root / 'sunnypilot/selfdrive/controls/controlsd_ext.py'
  body = _method(filename, 'ControlsExt', 'state_control_ext').body
  nodes = [n for n in body if (isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'turn_preview') or
           (isinstance(n, ast.If) and ast.unparse(n.test) == 'turn_preview is not None')]
  assert len(nodes) == 2

  class Subscriptions(dict):
    valid = {'modelV2': True, 'lateralManeuverPlan': maneuver}
    logMonoTime = {'modelV2': stamp}

    def all_checks(self, services):
      return healthy

  sp = custom.CarControlSP.new_message()
  sp.fordLateralPath.enabled = sp.fordLateralPath.valid = True
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(filename), 'exec'),
       {'self': SimpleNamespace(ford_turn_preview=tracker), 'sm': Subscriptions(modelV2=message), 'CC_SP': sp})
  return sp


@pytest.mark.parametrize('healthy,maneuver', [(True, False), (False, False), (True, True)])
def test_actual_publication_gates_and_original_model_timestamp(healthy, maneuver):
  tracker = FordTurnPreview()
  publish_preview(tracker, model(action=0.), 1_000_000_000)
  sp = publish_preview(tracker, model(), 1_050_000_000, healthy=healthy, maneuver=maneuver)
  assert sp.fordTurnPreview.valid == (healthy and not maneuver)
  assert sp.fordTurnPreview.modelMonoTime == 1_050_000_000
  assert sp.fordLateralPath.valid
  convert_carControlSP(sp.as_reader())


def test_card_consumes_published_preview_and_preserves_reader_contract():
  from opendbc.car import structs
  from opendbc.car.interfaces import CarInterfaceBase
  from openpilot.selfdrive.car.tests.test_ford_joint_control import controls

  root = Path(__file__).resolve().parents[3]
  filename = root / 'selfdrive/car/card.py'
  method = _method(filename, 'Car', 'controls_update')
  env = {'car': structs.car, 'custom': custom, 'REPLAY': True, 'convert_carControlSP': convert_carControlSP,
         'can_list_to_can_capnp': lambda *args, **kwargs: None}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(filename), 'exec'), env)
  p = pipeline()
  p.cs.leftBlinker = True
  card = SimpleNamespace(initialized_prev=True, ford_joint_control=p.joint,
                         sm=SimpleNamespace(all_alive=lambda services: True, all_checks=lambda services: True, frame=1),
                         pm=SimpleNamespace(send=lambda *args: None),
                         CI=SimpleNamespace(apply=lambda *args: CarInterfaceBase.apply(p.interface, *args)))
  tracker = FordTurnPreview()
  for stamp, target, raw in ((1_000_000_000, 0., 0.), (1_050_000_000, 100., -.01)):
    sp = publish_preview(tracker, model(action=raw), stamp)
    with custom.CarControlSP.from_bytes(sp.to_bytes()) as reader:
      card.can_log_mono_time = stamp
      control, _ = controls(target)
      env['controls_update'](card, p.cs, control.as_reader(), reader)
  assert p.joint.sent[2]
  assert p.joint.diagnostics['geometry_lead'] == 30.
  assert card.CC_prev.actuators.as_builder().steeringAngleDeg == 100.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_heading_distance_and_action_sign(sign):
  p = sample(sign)
  assert p.valid
  assert p.heading7 == pytest.approx(sign * 15.4, abs=1e-5)
  assert p.heading14 == pytest.approx(sign * 30.8, abs=1e-5)
  assert turn_preview_lead(sign * 50., p, 1.01) == (sign * 10., 1.)
  assert turn_preview_lead(sign * 1000., p, 1.01) == (sign * 30., 1.)
  assert turn_preview_lead(-sign * 50., p, 1.01)[0] == 0.


def test_folded_path_uses_arc_distance_and_unwrapped_heading():
  m = model()
  angle = np.linspace(0., 3.5, 33)
  m.position.x = (6 * np.sin(angle)).tolist()
  m.position.y = (6 * (1 - np.cos(angle))).tolist()
  m.orientation.z = ((angle + np.pi) % (2 * np.pi) - np.pi).tolist()
  p = FordTurnPreview().update(m, 1_000_000_000, True)
  assert p['valid']
  assert p['heading14'] < p['heading7'] < -60.  # x folds back, distance keeps increasing.


@pytest.mark.parametrize('bad', ['invalid', 'short', 'mismatch', 'nan', 'action_nan', 'lane_change'])
def test_invalid_geometry_disables_only_preview(bad):
  m = model()
  if bad == 'short':
    m.position.x = np.linspace(0., 13., 33).tolist()
  elif bad == 'mismatch':
    m.orientation.z = [0.]
  elif bad == 'nan':
    m.position.y = [float('nan')] * 33
  elif bad == 'action_nan':
    m.action.desiredCurvature = float('nan')
  elif bad == 'lane_change':
    m.meta.laneChangeState = 'laneChangeStarting'
  p = FordTurnPreview().update(m, 1_000_000_000, bad != 'invalid')
  assert not p['valid']


def test_duplicate_stale_and_invalid_action_history():
  c = FordTurnPreview()
  c.update(model(action=0.), 1_000_000_000, True)
  good = c.update(model(), 1_050_000_000, True).copy()
  assert good['actionRate'] > 0
  assert c.update(model(action=.1), 1_050_000_000, True) == good
  p = sample(stamp=1_050_000_000)
  for now in (1.049, 1.201):
    assert turn_preview_lead(100., p, now) == (0., 0.)
  c.update(model(), 1_100_000_000, False)
  assert c.update(model(action=-.02), 1_150_000_000, True)['actionRate'] == 0.
  assert c.update(model(action=-.03), 1_400_000_000, True)['actionRate'] == 0.


@pytest.mark.parametrize('signal', ['none', 'opposite', 'hazards'])
def test_no_matching_signal_retains_identical_packet_history(signal):
  base, trial = pipeline(False), pipeline()
  for i in range(500):
    now = 1. + i * .01
    target = 70. + 50. * np.sin(i * .02)
    for p in (base, trial):
      p.cs.leftBlinker = signal == 'hazards'
      p.cs.rightBlinker = signal != 'none'
      p.tick(now, float(target), turn_preview=sample(stamp=round(now * 1e9)))
    assert trial.joint.sent == base.joint.sent
    np.testing.assert_array_equal(state(trial.joint.request), state(base.joint.request))
    assert trial.joint.angle_trim == base.joint.angle_trim


@pytest.mark.parametrize('sign', [-1., 1.])
def test_matching_signal_changes_inverse_only_and_retains_bounds(sign):
  p = pipeline()
  p.cs.leftBlinker, p.cs.rightBlinker = sign > 0, sign < 0
  p.tick(1., 0.)
  p.tick(1.01, sign * 100., turn_preview=sample(sign))
  d = p.joint.diagnostics
  assert d['geometry_lead'] == sign * 30.
  assert d['inverse_target'] == d['trimmed_angle'] + sign * 30.
  assert d['requested_angle'] == sign * 100.
  assert d['requested_rate'] * sign > 0.
  # Raw action relaxing suppresses the extra even while filtered request grows.
  p.tick(1.02, sign * 105., turn_preview=sample(-sign, 1_020_000_000))
  assert p.joint.diagnostics['geometry_lead'] == 0.
  assert p.joint.sent[2]


@pytest.mark.parametrize('gate', ['touch', 'limit', 'denied', 'fault', 'stale', 'inactive', 'missing'])
def test_preview_respects_existing_health_and_override_gates(gate):
  p = pipeline()
  p.cs.leftBlinker = True
  p.tick(1., 0.)
  p.cs.steeringPressed = gate == 'touch'
  p.cs.steerFaultTemporary = gate == 'fault'
  status = SimpleNamespace(valid=True, canMonoTime=1_010_000_000, limit=2 if gate == 'limit' else 0, denied=gate == 'denied')
  p.tick(1.01, 120., active=gate != 'inactive', fresh=gate != 'stale', pscm_status=status,
         turn_preview=None if gate == 'missing' else sample())
  assert p.joint.diagnostics.get('geometry_lead', 0.) == 0.
  if gate in ('touch', 'limit', 'missing'):
    assert p.joint.sent[2]
  else:
    assert p.joint.sent == (0., 0., False)
