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
from openpilot.selfdrive.car.ford_joint_control import ANGLE_TRIM_MAX, FordJointControl, joint_control_enabled, select_joint_control
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
  cc.angularVelocity = [0., 0., 0.]
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

  def tick(self, now, target=30., active=True, *, angular_velocity=None, **kwargs):
    cc, sp = controls(target, active)
    cc.angularVelocity = [0., 0., -self.cs.yawRate] if angular_velocity is None else angular_velocity
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


def test_joint_reference_carrier_stays_valid_through_stop():
  from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
  c = FordModelActionController(joint_control=True)
  for i, speed in enumerate([5., .3, .29, .01, 0., 0., .01, .29, .3, 5.]):
    path = update(c, now=1+i*.01, speed=speed)
    assert path.valid, (speed, c.diagnostics)
    assert path.path_offset == path.path_angle == 0.
  assert not update(c, now=1.1, speed=0., valid=False).valid


@pytest.mark.parametrize('sign', [-1., 1.])
def test_stop_repeats_transmitted_request_and_resume_keeps_target(sign):
  p = Pipeline()
  p.cs.steeringAngleDeg = sign*120.
  p.cs.yawRate = p.cs.vEgo*math.radians(sign*120.)/(3.7*16.9)
  for i in range(200):
    p.tick(1+i*.01, sign*120.)
  sent = p.joint.sent
  assert sent[2] and any(abs(v) > .01 for v in sent[:2])
  p.joint.angle_trim = sign*.5
  for i, speed in enumerate([.29, .01]+[0.]*200+[.01, .29]):
    p.cs.vEgo = speed
    p.cs.yawRate = speed*math.radians(sign*120.)/(3.7*16.9)
    assert p.tick(3+i*.01, sign*120.).latActive
    assert p.joint.sent == sent
    assert p.joint.angle_trim == sign*.5
    assert not p.joint.fault
    json.dumps(p.joint.diagnostics, allow_nan=False)
  p.cs.vEgo = .3
  p.cs.yawRate = .3*math.radians(sign*120.)/(3.7*16.9)
  assert p.tick(5.04, sign*120.).latActive
  assert p.joint.diagnostics['requested_angle'] == sign*120.
  assert p.joint.diagnostics['requested_rate'] == 0.
  assert not p.joint.fault


@pytest.mark.parametrize('sign', [-1., 1.])
def test_stop_speed_filter_undershoot_keeps_actual_transmitted_hold(sign):
  p = Pipeline()
  p.cs.gearShifter = structs.CarState.GearShifter.drive
  for i in range(30):
    p.tick(1+i*.01, sign*120.)
  sent = p.joint.sent
  assert sent[2] and any(abs(v) > .01 for v in sent[:2])
  p.cs.vEgoRaw, p.cs.standstill = 0., True
  for i, speed in enumerate([.01, 0., -.01, -.04, -.01, 0., .01, .29]):
    p.cs.vEgo = speed
    assert p.tick(1.3+i*.01, sign*120.).latActive
    assert p.joint.sent == sent
    assert p.joint.diagnostics['stop_hold']
  p.cs.vEgo = p.cs.vEgoRaw = .3
  assert p.tick(1.38, sign*120.).latActive
  assert p.joint.sent[0]*sign > 0 and p.joint.sent[1]*sign > 0
  p.cs.gearShifter = structs.CarState.GearShifter.reverse
  assert not p.tick(1.39, sign*120.).latActive
  assert p.joint.sent == (0., 0., False)


@pytest.mark.parametrize('failure', ['disengage', 'stale', 'can', 'steering_fault', 'override', 'denied'])
def test_stopped_hold_still_releases_and_does_not_resurrect_old_command(failure):
  p = Pipeline()
  for i in range(20):
    p.tick(1+i*.01, 120.)
  previous = p.joint.sent
  p.cs.vEgo = 0.
  assert p.tick(1.2, 120.).latActive
  assert p.joint.sent == previous
  p.cs.canValid = failure != 'can'
  p.cs.steerFaultTemporary = failure == 'steering_fault'
  status = SimpleNamespace(valid=True, canMonoTime=1_210_000_000, limit=3 if failure == 'override' else 0, denied=failure == 'denied')
  assert not p.tick(1.21, 120., active=failure != 'disengage', fresh=failure != 'stale', pscm_status=status).latActive
  assert p.joint.sent == (0., 0., False)
  p.cs.canValid, p.cs.steerFaultTemporary = True, False
  assert p.tick(1.22, 120.).latActive
  assert p.joint.sent == (0., 0., True)


def test_can_yaw_zero_offset_does_not_bias_the_command():
  reference, biased = Pipeline(), Pipeline()
  biased.cs.yawRate = -.008  # Route 175: raw CAN disagrees with calibrated yaw.
  for i in range(200):
    now = 1. + i*.01
    reference.tick(now, 0., angular_velocity=[0., 0., 0.])
    biased.tick(now, 0., angular_velocity=[0., 0., 0.])
    assert biased.joint.sent == reference.joint.sent
    assert biased.joint.measurement[2] == 0.


def test_calibrated_yaw_sign_matches_pinion_coordinates():
  p = Pipeline()
  p.cs.yawRate = .012
  p.tick(1., angular_velocity=[.01, .02, -.02])
  assert p.joint.measurement[2] == pytest.approx(.02)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_persistent_small_wheel_error_builds_bounded_correction(sign):
  # Route 17a: a steady request ~1.5 degrees from the wheel, no driver or
  # PSCM limit. The nominal encoder alone has no way to remove that residual.
  p = Pipeline()
  p.cs.vEgo = 20.
  before = None
  for i in range(601):
    p.tick(1. + i*.01, sign*1.5)
    if i == 100:
      before = p.joint.diagnostics['target_curvature']
  assert sign*(p.joint.diagnostics['target_curvature'] - before) > 0.00005
  assert 1.7 < sign*p.joint.angle_trim < ANGLE_TRIM_MAX


@pytest.mark.parametrize('bias', [-1.5, 1.5])
def test_trim_removes_static_mismatch_in_synthetic_angle_plant(bias):
  # A regression for residual feedback, NOT a validated PSCM/wheel simulation.
  # Use the actual packed-command observer and angle stage, then a deliberately
  # simple 0.4 s wheel lag with a known additive mismatch.
  p = Pipeline()
  p.cs.vEgo = 20.
  angle = rate = 0.
  errors = []
  for i in range(3000):
    p.cs.steeringAngleDeg, p.cs.steeringRateDeg = angle, rate
    p.cs.yawRate = math.radians(angle)/16.9*20./(3.7+(33/16384)*20**2)
    p.tick(1.+i*.01, 0.)
    nominal = copy.copy(p.joint.angle).step(72., p.joint.diagnostics['predicted_curvature'], angle,
                                          p.cs.yawRate, p.cs.yawRate*20., 3.7, 16.9)
    rate = (nominal+bias-angle)/.4
    angle += rate*.01
    errors.append(angle)
  assert np.mean(np.abs(errors[-500:])) < .1


@pytest.mark.parametrize('target,rate,speed', [(60., 0., 5.), (1.5, 20., 5.), (1.5, 0., 1.)])
def test_trim_does_not_learn_large_lag_fast_motion_or_crawl(target, rate, speed):
  p = Pipeline()
  p.cs.vEgo = speed
  for i in range(200):
    # Real Ford CarState leaves steeringRateDeg at zero, even during motion.
    p.cs.steeringAngleDeg = rate*i*.01
    p.tick(1.+i*.01, target+p.cs.steeringAngleDeg)
    assert abs(p.joint.angle_trim) < .015  # Only the derivative's initial settling.
  if rate:
    assert p.joint.wheel_rate == pytest.approx(rate, abs=.01)
    assert not p.joint.diagnostics['trim_learning']


def test_trim_bounded_retained_at_zero_error_and_frozen_on_light_touch():
  p = Pipeline()
  for i in range(1201):
    p.tick(1.+i*.01, 2.)
    assert abs(p.joint.angle_trim) <= ANGLE_TRIM_MAX
  assert p.joint.angle_trim == ANGLE_TRIM_MAX
  p.cs.steeringPressed = True
  assert p.tick(13.01, -2.).latActive
  assert p.joint.angle_trim == ANGLE_TRIM_MAX
  p.cs.steeringPressed = False
  p.tick(13.02, 0.)
  assert p.joint.angle_trim == ANGLE_TRIM_MAX
  assert not p.tick(13.03, active=False).latActive
  assert p.joint.angle_trim == 0.


@pytest.mark.parametrize('limit,denied', [(3, False), (0, True)])
def test_explicit_override_resets_trim(limit, denied):
  p = Pipeline()
  p.joint.angle_trim = 1.
  status = SimpleNamespace(valid=True, canMonoTime=1_000_000_000, limit=limit, denied=denied)
  assert not p.tick(1., 1.5, pscm_status=status).latActive
  assert p.joint.angle_trim == 0.


def test_limit_reached_does_not_grow_trim_but_allows_relief():
  p = Pipeline()
  p.joint.angle_trim = 1.
  for i in range(101):
    now = 1.+i*.01
    status = SimpleNamespace(valid=True, canMonoTime=round(now*1e9), limit=2, denied=False)
    assert p.tick(now, 1.5, pscm_status=status).latActive
    assert p.joint.angle_trim == 1.
  p.cs.steeringAngleDeg = 3.
  p.tick(2.01, 1.5, pscm_status=status)
  assert 0.99 < p.joint.angle_trim < 1.


def test_acceleration_clipping_does_not_grow_trim():
  p = Pipeline()
  p.cs.vEgo = 50.
  p.cs.steeringAngleDeg = 200.
  for i in range(100):
    p.tick(1.+i*.01, 201.5)
    assert p.joint.diagnostics['accel_limited']
    assert p.joint.angle_trim == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_small_wheel_motion_does_not_discard_steady_request_trim(sign):
  # Route 17c, 1461 s: a ~1-degree trim disappears when a brief wheel
  # movement crosses the target, although the requested angle barely changes.
  p = Pipeline()
  p.cs.vEgo = 24.
  p.cs.steeringAngleDeg = sign * -2.1
  for i in range(60):
    p.tick(1. + i * .01, sign * -1.3)
  p.joint.angle_trim = sign * .985
  p.cs.steeringAngleDeg = sign * -.8
  assert p.tick(1.6, sign * -1.3).latActive
  assert abs(p.joint.wheel_rate) > 5.
  assert not p.joint.diagnostics['trim_learning']
  assert p.joint.diagnostics['angle_trim'] == pytest.approx(sign * .985)
  assert .98 < sign * p.joint.angle_trim < .985  # Opposing error can bleed it.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_fast_request_releases_opposing_trim_before_wheel_moves(sign):
  p = Pipeline()
  for i in range(60):
    p.tick(1. + i * .01, 0.)
  p.joint.angle_trim = sign
  request = sign * -2.
  p.tick(1.6, request)
  assert p.joint.wheel_rate == 0.
  assert p.joint.diagnostics['angle_trim'] == 0.
  assert p.joint.diagnostics['trimmed_angle'] == request


def test_inactive_request_history_cannot_clear_trim_after_reengagement():
  p = Pipeline()
  p.tick(1., 0.)
  p.tick(1.01, 60.)
  assert abs(p.joint.requested_rate) > 5.
  p.tick(1.02, 0., active=False)
  assert p.joint.requested_rate == 0. and p.joint.last_target is None
  p.tick(1.03, 1.)
  p.joint.angle_trim = -.5
  p.tick(1.04, 1.)
  assert p.joint.diagnostics['angle_trim'] == -.5


@pytest.mark.parametrize('target,rate', [(-60., 0.), (-2., -30.)])
def test_reversal_or_fast_unwind_clears_old_trim_before_allocation(target, rate):
  p = Pipeline()
  for i in range(10):
    p.cs.steeringAngleDeg = rate*i*.01
    p.tick(1.+i*.01, target+p.cs.steeringAngleDeg)
  p.joint.angle_trim = ANGLE_TRIM_MAX
  for i in range(10, 101):
    p.cs.steeringAngleDeg = rate*i*.01
    request = target+p.cs.steeringAngleDeg
    p.tick(1.+i*.01, request)
    assert p.joint.angle_trim == 0.
    assert p.joint.diagnostics['trimmed_angle'] == pytest.approx(request, abs=1e-5)


@pytest.mark.parametrize('angular_velocity', [[], [0., 0.], [0., 0., math.nan], [0., 0., math.inf], [0., 0., 3.1]])
def test_missing_or_invalid_calibrated_yaw_does_not_fall_back_to_raw_can(angular_velocity):
  p = Pipeline()
  p.tick(1.)
  assert not p.tick(1.01, angular_velocity=angular_velocity).latActive
  assert p.joint.sent == (0., 0., False)
  assert p.tick(1.02).latActive


def test_touch_does_not_zero_the_command_or_reset_held_state():
  reference, touched = Pipeline(), Pipeline()
  for i in range(160):
    touched.cs.steeringPressed = 40 <= i < 50 or 100 <= i < 115
    target = 60. if i < 100 else -30.
    reference.tick(1. + i*.01, target)
    assert touched.tick(1. + i*.01, target).latActive
    assert touched.joint.sent == reference.joint.sent
    np.testing.assert_array_equal(state(touched.joint.request), state(reference.joint.request))


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
  result = p.tick(2.02, 60., active=False)
  assert not result.latActive and p.joint.sent == (0., 0., False)
  assert abs(p.joint.request.c0) > 0 or abs(p.joint.request.c1) > 0
  held = copy.copy(p.joint.request)
  phase = p.joint.phase
  p.tick(2.03, 60., active=False)
  ticks = int((phase+.01+1e-12)/.008)
  for _ in range(ticks):
    held.step(5.36*3.6, 0., 0., active=False, freeze_i=True)
  np.testing.assert_allclose(state(p.joint.request), state(held), atol=1e-12)
  assert p.tick(2.04, -30.).latActive
  assert p.joint.diagnostics['requested_angle'] == -30.


@pytest.mark.parametrize('limit,denied,active', [(0, False, True), (2, False, True), (3, False, False), (0, True, False)])
def test_limit_reached_does_not_freeze_but_override_inhibits(limit, denied, active):
  p = Pipeline()
  status = SimpleNamespace(valid=True, canMonoTime=1_000_000_000, limit=limit, denied=denied)
  assert p.tick(1., pscm_status=status).latActive == active


@pytest.mark.parametrize('field,value', [('vEgo', -.01), ('vEgo', 56.), ('yawRate', 3.1),
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


@pytest.mark.parametrize('speed,c0,c1,filtered,fast,target,phase,pair,cost', [
  (20., 0., 0., 0., False, .03, 0, (.03, .002), 5.206693787207076),
  (20., 3., .4, .03, False, -.03, 2, (2.98, .399), 149.0975016923494),
  (40., 3., .4, .03, True, 0., 0, (2.95, .395), 12.167867914611671),
  (6., 5.11, .5, .1, False, -.1, 0, (5.08, .498), 1423.8735141422555),
  (80., -5.11, -.5, -.1, True, .03, 2, (-5.08, -.4975), 39.42744549117561),
  (40., 3., -.4, 0., False, 0., 2, (3.02, -.399), 6.184073685045232),
])
def test_optimized_selection_matches_frozen_cases(speed, c0, c1, filtered, fast, target, phase, pair, cost):
  # Frozen outputs from 528ed3615 before pruning/caching the full-return search.
  # Cover entry, reversal, release, saturation, cancellation and both tick counts.
  # Costs refreshed for the equal-buildup endpoint and residual allocation at
  # field bounds, then for the supervisor-saturation C0 endpoint (its return
  # path differs). All six immediate selected packets remain unchanged.
  m = MainRequest(native_lookup=True)
  m.c0, m.c1, m.filtered, m.fast = c0, c1, filtered, fast
  command, info = PairedRelease(m).choose(speed, target, phase)
  assert command == pytest.approx(pair, abs=1e-15, rel=0)
  assert info['cost'] == pytest.approx(cost, abs=1e-12, rel=1e-12)


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
  assert p.joint.sent[2] == active
  assert p.joint.last_sent_time == 1.
  assert owner.CC_prev.to_dict() == {**original, 'latActive': active}
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
