"""Compare normal maneuver injection and controller output with channel isolation."""
import math
from collections import defaultdict
from types import SimpleNamespace

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.values import FordFlags
from openpilot.cereal import custom, log, messaging
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.ford_channel_test import FordChannelTest, SPEEDS, use_maneuver_reference
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import Subscriptions, pipeline  # noqa: F401
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import car_params, startup
from openpilot.tools.lateral_maneuvers import lateral_maneuversd as daemon


def plan(channel='c0', phase='maneuver', speed=SPEEDS[0], run_id=1, curvature=.01):
  msg = log.LateralManeuverPlan.new_message(desiredCurvature=curvature)
  msg.fordChannelTest = {'runId': run_id, 'channel': channel, 'phase': phase, 'speed': speed}
  with log.LateralManeuverPlan.from_bytes(msg.to_bytes()) as reader:
    return reader.as_builder()


def update(test, now=10., msg=None, **changes):
  args = {'plan_valid': True, 'plan_time': now, 'now': now, 'normal': FordPath(True, .24, .08),
          'active': True, 'healthy': True, 'driver_input': False, 'speed': SPEEDS[0]}
  return test.update(msg or plan(), **(args | changes))


@pytest.mark.parametrize('changes', [
  {'active': False}, {'healthy': False}, {'driver_input': True}, {'speed': SPEEDS[0]+.71}, {'speed': math.nan},
  {'normal': FordPath()}, {'normal': FordPath(True, math.nan, 0.)}, {'plan_time': 9.8},
])
def test_active_faults_zero_output_and_latch(changes):
  test = FordChannelTest()
  assert update(test).valid
  assert update(test, 10.01, **changes) == FordPath()
  assert update(test, 10.02) == FordPath()
  assert update(test, 10.03, plan_valid=False) is None
  assert update(test, 10.04, plan(run_id=2)).valid


@pytest.mark.parametrize('msg', [plan(channel='c1'), plan(run_id=2), plan(speed=SPEEDS[1]), plan(phase='pulse')])
def test_midrun_identity_changes_abort(msg):
  test = FordChannelTest()
  update(test)
  assert update(test, 10.01, msg) == FordPath()


def test_legacy_raw_pulse_cannot_actuate():
  msg = plan(phase='pulse')
  msg.fordChannelTest.delta = 1.28
  assert update(FordChannelTest(), msg=msg) == FordPath()


def test_fresh_but_frozen_maneuver_times_out():
  test = FordChannelTest()
  for i in range(401):
    assert update(test, 10.+i*.01).valid
  assert update(test, 14.01) == FordPath()


def test_mode_selection_and_transient_parameter(tmp_path):
  params = Params(str(tmp_path))
  params.put_bool('FordModelActionController', True, block=True)
  assert startup(params=params).ford_channel_test is None
  params.put_bool('FordChannelTestMode', True, block=True)
  assert isinstance(startup(params=params).ford_channel_test, FordChannelTest)
  for key in ('FordModelActionController', 'LateralManeuverMode', 'LongitudinalManeuverMode', 'JoystickDebugMode'):
    params.put_bool(key, key != 'FordModelActionController', block=True)
    assert startup(params=params).ford_channel_test is None
    params.put_bool(key, key == 'FordModelActionController', block=True)
  for cp in (car_params(brand='toyota'), car_params(flags=0)):
    assert startup(cp, params).ford_channel_test is None
  for flag in (ParamKeyFlag.CLEAR_ON_MANAGER_START, ParamKeyFlag.CLEAR_ON_OFFROAD_TRANSITION):
    params.put_bool('FordChannelTestMode', True, block=True)
    params.clear_all(flag)
    assert not params.get_bool('FordChannelTestMode')


@pytest.mark.parametrize('channel', ['c0', 'c1'])
@pytest.mark.parametrize('speed', SPEEDS)
@pytest.mark.parametrize('limited', [False, True])
def test_real_injection_and_wire_match_normal_controller_on_selected_channel(pipeline, channel, speed, limited):  # noqa: F811
  call, publication = pipeline
  normal = startup()
  isolated = startup(params=SimpleNamespace(get_bool=lambda key: key in ('FordModelActionController', 'FordChannelTestMode')))
  controllers = (normal, isolated)
  cp = structs.CarParams(flags=int(FordFlags.CANFD), carFingerprint=normal.CP.carFingerprint)
  sender = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp, structs.CarParamsSP())
  vehicle = SimpleNamespace(out=structs.CarState(vEgo=speed, vEgoRaw=speed), acc_tja_status_stock_values=defaultdict(int),
                            lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], sender.CAN.main)
  for control in controllers:
    control.sm, control.desired_curvature, control.curvature = Subscriptions(True), 0., 0.
  model = straight()
  model.action = SimpleNamespace(desiredCurvature=-.15)  # opposite model must lose to the actual maneuver injection
  cs = SimpleNamespace(vEgo=speed, yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.,
                       gasPressed=False, brakePressed=False, cruiseState=SimpleNamespace(enabled=True))
  for i in range(251):
    now = 10.+i*.01
    request = (.5 if i < 100 else -.5)/speed**2
    for control in controllers:
      sm = control.sm
      sm.messages['lateralManeuverPlan'] = plan(channel=channel if control is isolated else 'none', curvature=request, speed=speed)
      sm.logMonoTime = dict.fromkeys(sm.logMonoTime, round(now*1e9))
      status = sm['carStateSP'].fordPscmStatus
      status.valid, status.canMonoTime, status.lateralState, status.limit = True, round(now*1e9), 2, 2 if limited else 0
      cc = structs.CarControl(latActive=True)
      cs.brakePressed = i == 250
      exec(call, {'self': control, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                  'use_maneuver_reference': use_maneuver_reference, 'clip_curvature': clip_curvature,
                  'time': SimpleNamespace(monotonic=lambda t=now: t), 'math': math})
    assert isolated.desired_curvature == normal.desired_curvature
    assert isolated.ford_path_controller.core.correction == normal.ford_path_controller.core.correction
    assert isolated.ford_path_controller.core.proportional == normal.ford_path_controller.core.proportional
    if i != 250:
      assert isolated.ford_path == FordPath(True, normal.ford_path.path_offset if channel == 'c0' else 0.,
                                           normal.ford_path.path_angle if channel == 'c1' else 0.)
      assert isolated.ford_path_controller.diagnostics['reference_age'] == pytest.approx(0.)
    msg = custom.CarControlSP.new_message()
    exec(publication, {'self': isolated, 'CC_SP': msg})
    _, packets = sender.update(cc.as_reader(), convert_carControlSP(msg.as_reader()), vehicle, round(now*1e9))
    parser.update([round(now*1e9), packets])
    wire = parser.vl['LateralMotionControl2']
    assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(-isolated.ford_path.path_offset, abs=1e-7)
    assert wire['LatCtlPath_An_Actl'] == pytest.approx(-isolated.ford_path.path_angle, abs=1e-7)
    assert wire['LatCtl_D2_Rq'] == (0 if i == 250 else 2)
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
    if i == 50:
      assert isolated.desired_curvature > 0.
    if i == 200:
      assert isolated.desired_curvature < 0.


def run_daemon(monkeypatch, interrupt=False):
  class Finished(Exception):
    pass

  plans, alerts, checks = [], [], []
  clock = [10.]
  pulse_samples = [0]
  cp = daemon.car.CarParams.new_message().to_bytes()

  class SM(messaging.SubMaster):
    def __init__(self, services, **kwargs):
      super().__init__(services, **kwargs)
      self.events = {s: messaging.new_message(s) for s in services}

    def update(self):
      clock[0] += .05
      assert clock[0] < 400., 'Suite did not finish'
      cs = self.events['carState'].carState
      cs.vEgo = plans[-1].lateralManeuverPlan.fordChannelTest.speed if plans else SPEEDS[0]
      cs.canValid, cs.cruiseState.enabled = True, True
      cs.steeringPressed = interrupt and pulse_samples[0] == 5
      self.events['carControl'].carControl.latActive = True
      self.events['carControl'].carControl.orientationNED = [0., 0., 0.]
      self.events['selfdriveState'].selfdriveState.enabled = True
      for msg in self.events.values():
        msg.valid, msg.logMonoTime = True, round(clock[0]*1e9)
      self.update_msgs(clock[0], [m.as_reader() for m in self.events.values()])
      checks.append(self.all_checks())
      if cs.steeringPressed:
        pulse_samples[0] += 1

  class PM:
    def __init__(self, _services):
      pass

    def send(self, service, msg):
      msg.logMonoTime = round(clock[0]*1e9)
      (plans if service == 'lateralManeuverPlan' else alerts).append(msg)
      if service == 'lateralManeuverPlan' and msg.valid:
        pulse_samples[0] += 1
      if service == 'alertDebug' and msg.alertDebug.alertText1 == 'Maneuvers Finished':
        raise Finished

  with monkeypatch.context() as mp:
    mp.setattr(daemon.messaging, 'SubMaster', SM)
    mp.setattr(daemon.messaging, 'PubMaster', PM)
    mp.setattr(daemon, 'Params', lambda: SimpleNamespace(get=lambda *_a, **_kw: cp))
    with pytest.raises(Finished):
      daemon.main(ford_channels=True)
  assert all(checks[2:])
  return plans, alerts


@pytest.mark.parametrize('interrupt', [False, True])
def test_actual_daemon_reuses_all_normal_waveforms_repeats_and_retry(monkeypatch, interrupt):
  plans, alerts = run_daemon(monkeypatch, interrupt)
  groups = defaultdict(list)
  for msg in plans:
    if msg.valid:
      groups[msg.lateralManeuverPlan.fordChannelTest.runId].append(msg.lateralManeuverPlan)
  # 16 maneuvers, each performed 3 times. An interrupted attempt is retried.
  assert len(groups) == 48+interrupt
  assert sum(a.alertDebug.alertText1 == 'Complete' for a in alerts) == 48
  expected_runs = []
  for maneuver in daemon.channel_maneuvers():
    for _ in range(3):
      reference = daemon.Maneuver(maneuver.description, maneuver.actions, initial_speed=maneuver.initial_speed)
      expected = []
      while not reference.finished:
        value = reference.get_accel(maneuver.initial_speed, True, 0., 0.)
        if reference.active and not reference._run_completed:
          expected.append(value/maneuver.initial_speed**2)
      expected_runs.append((maneuver.channel, maneuver.initial_speed, expected))
  completed = list(groups.values())[1:] if interrupt else list(groups.values())
  for actual, (channel, speed, expected) in zip(completed, expected_runs, strict=True):
    assert [p.desiredCurvature for p in actual] == pytest.approx(expected, abs=1e-7)
    assert all(p.fordChannelTest.channel == channel and p.fordChannelTest.speed == pytest.approx(speed) for p in actual)
    assert all(p.fordChannelTest.delta == 0. and p.fordChannelTest.phase == 'maneuver' for p in actual)
  if interrupt:
    assert len(next(iter(groups.values()))) == 5


@pytest.mark.parametrize('phase', ['maneuver', 'pulse'])
def test_channel_payload_is_ignored_when_toggle_off(pipeline, phase):  # noqa: F811
  controls = startup()
  sm = Subscriptions(True)
  sm.messages['lateralManeuverPlan'] = plan(phase=phase, curvature=-.1)
  controls.sm, controls.desired_curvature, controls.curvature = sm, 0., 0.
  model = straight()
  model.action = SimpleNamespace(desiredCurvature=.1)
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=20., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.)
  exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                    'use_maneuver_reference': use_maneuver_reference, 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)})
  assert controls.desired_curvature > 0. and controls.ford_path.path_angle > 0.
