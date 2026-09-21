"""Opt-in entry assist at the real Ford adapter and CAN packing boundary."""
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.car.ford_joint_control import FordJointControl, select_joint_control
from openpilot.selfdrive.car.tests.test_ford_joint_control import Pipeline, cp
from openpilot.selfdrive.controls.lib.ford_joint.encoder import state


def assisted():
  p = Pipeline()
  p.joint = FordJointControl(cp(), turn_entry_assist=True)
  return p


def test_turn_entry_is_default_off_and_requires_the_existing_joint_controller(tmp_path):
  params = Params(str(tmp_path))
  assert params.get_default_value('FordPscmTurnEntryAssist') is False
  assert not params.get_bool('FordPscmTurnEntryAssist')
  assert b'FordPscmTurnEntryAssist' in params.all_keys(ParamKeyFlag.PERSISTENT | ParamKeyFlag.BACKUP)
  params.put_bool('FordPscmTurnEntryAssist', True, block=True)
  assert select_joint_control(cp(), params) is None
  params.put_bool('FordModelActionController', True, block=True)
  assert select_joint_control(cp(), params) is None
  params.put_bool('FordPscmJointControl', True, block=True)
  assert select_joint_control(cp(), params).turn_entry_assist
  params.put_bool('FordPscmTurnEntryAssist', False, block=True)
  assert not select_joint_control(cp(), params).turn_entry_assist
  params.put_bool('FordPscmTurnEntryAssist', True, block=True)
  for key in ('FordGeometryReference', 'JoystickDebugMode'):
    params.put_bool(key, True, block=True)
    assert select_joint_control(cp(), params) is None
    params.put_bool(key, False, block=True)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_large_growing_undertracked_request_adds_to_real_wire_commands(sign):
  base, trial = Pipeline(), assisted()
  for p in (base, trial):
    p.tick(1., 0.)
    p.tick(1.01, sign * 120.)
  np.testing.assert_allclose(np.array(trial.joint.sent[:2]) - base.joint.sent[:2], sign * np.array([.60, .04]), atol=1e-12)
  assert trial.joint.diagnostics['requested_angle'] == sign * 120.
  assert trial.joint.diagnostics['trimmed_angle'] == base.joint.diagnostics['trimmed_angle']
  assert trial.joint.diagnostics['requested_rate'] == base.joint.diagnostics['requested_rate']
  assert trial.joint.diagnostics['turn_entry_weight'] == 1.
  assert trial.joint.sent[2] and base.joint.sent[2]


@pytest.mark.parametrize('sign', [-1., 1.])
def test_extra_clips_at_dbc_bounds_through_real_packer(sign, monkeypatch):
  p = assisted()
  p.tick(1., 0.)
  choose = p.joint.encoder.choose

  def near_bounds(*args, **kwargs):
    _, info = choose(*args, **kwargs)
    return (sign * 5.10, sign * .49), info

  monkeypatch.setattr(p.joint.encoder, 'choose', near_bounds)
  p.tick(1.01, sign * 120.)
  assert p.joint.sent[:2] == pytest.approx((sign * 5.11, sign * .5))


def test_small_requests_and_small_errors_keep_full_history_identical():
  base, trial = Pipeline(), assisted()
  for i in range(1200):
    target = 25 * np.sin(i * .02) if i < 600 else 100.
    wheel = 0. if i < 600 else 90.
    for p in (base, trial):
      p.cs.steeringAngleDeg = wheel
      p.tick(1. + i * .01, float(target))
    assert trial.joint.sent == base.joint.sent
    np.testing.assert_array_equal(state(trial.joint.request), state(base.joint.request))
    assert trial.joint.angle_trim == base.joint.angle_trim


@pytest.mark.parametrize('sign', [-1., 1.])
def test_new_term_clears_on_relaxation_without_resetting_observed_state(sign):
  p = assisted()
  for i in range(100):
    p.cs.steeringAngleDeg = sign * 20.
    p.tick(1. + i * .01, sign * (100. + i))
  assert p.joint.diagnostics['turn_entry_c0'] * sign > 0
  p.tick(2., sign * 50.)
  assert p.joint.diagnostics['turn_entry_c0'] == p.joint.diagnostics['turn_entry_c1'] == 0.
  assert abs(p.joint.request.c0) + abs(p.joint.request.c1) > 0
  assert p.joint.sent[2]


@pytest.mark.parametrize('gate', ['touch', 'limit', 'denied', 'fault', 'stale', 'inactive', 'accel'])
def test_extra_respects_intervention_health_and_target_limit_gates(gate):
  p = assisted()
  p.cs.vEgo = 30. if gate == 'accel' else 5.36
  p.tick(1., 0.)
  p.cs.steeringPressed = gate == 'touch'
  p.cs.steerFaultTemporary = gate == 'fault'
  status = SimpleNamespace(valid=True, canMonoTime=1_010_000_000, limit=2 if gate == 'limit' else 0, denied=gate == 'denied')
  p.tick(1.01, 120., active=gate != 'inactive', fresh=gate != 'stale', pscm_status=status)
  d = p.joint.diagnostics
  assert d['turn_entry_c0'] == d['turn_entry_c1'] == 0.
  if gate in ('touch', 'limit', 'accel'):
    assert p.joint.sent[2]  # Only the added term is suppressed.
  else:
    assert p.joint.sent == (0., 0., False)
  if gate == 'accel':
    assert d['accel_limited']
