"""Exercise pulse timing, fault handling, actual controlsd and the Ford CAN sender."""
import math
from collections import defaultdict
from types import SimpleNamespace

import pytest

from opendbc.can.parser import CANParser
from opendbc.car import Bus, structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.values import FordFlags
from openpilot.cereal import custom, log
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.ford_channel_test import AMPLITUDE, SPEEDS, FordChannelTest, is_channel_plan
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import Subscriptions, pipeline  # noqa: F401
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import car_params, startup
from openpilot.tools.lateral_maneuvers.ford_maneuversd import Sequence, TRIALS
from openpilot.selfdrive.car.helpers import convert_carControlSP


def plan(channel='c0', phase='baseline', delta=0., speed=SPEEDS[0], run_id=1):
  msg = log.LateralManeuverPlan.new_message()
  msg.fordChannelTest = {'runId': run_id, 'channel': channel, 'phase': phase, 'delta': delta, 'speed': speed}
  # Exercise real Float32 serialization.
  with log.LateralManeuverPlan.from_bytes(msg.to_bytes()) as reader:
    return reader.as_builder()


def status(now=10., **changes):
  return SimpleNamespace(**({'valid': True, 'canMonoTime': round(now*1e9), 'denied': False, 'limit': 0, 'lateralState': 2} | changes))


def update(test, now=10., msg=None, **changes):
  args = {'plan_valid': True, 'plan_time': now, 'now': now, 'normal': FordPath(True, .01, .002, 0., 0.), 'active': True,
              'healthy': True, 'driver_input': False, 'speed': SPEEDS[0], 'angle': 0., 'curvature': 0., 'pscm': status(now)}
  return test.update(msg or plan(), **(args | changes))


def pulse(test):
  for i in range(51):
    result = update(test, 10.+i*.01, plan(phase='pulse', delta=.03) if i == 50 else plan())
  assert result.valid
  return result


@pytest.mark.parametrize('changes', [
  {'active': False}, {'healthy': False}, {'driver_input': True}, {'speed': SPEEDS[0]+.71},
  {'speed': math.nan}, {'angle': math.inf}, {'angle': 15.01}, {'curvature': .1},
  {'normal': FordPath()}, {'normal': FordPath(True, math.nan, 0.)}, {'plan_time': 10.},
  {'pscm': None}, {'pscm': status(10.51, denied=True)}, {'pscm': status(10.51, limit=2)},
  {'pscm': status(10.51, limit=3)}, {'pscm': status(10.51, lateralState=1)}, {'pscm': status(10.)},
])
def test_active_faults_zero_output_and_latch(changes):
  test = FordChannelTest()
  pulse(test)
  assert update(test, 10.51, plan(phase='pulse', delta=.03), **changes) == FordPath()
  assert test.aborted
  assert update(test, 10.52, plan(phase='pulse', delta=.03)) == FordPath()
  assert update(test, 10.53, plan(phase='aborted'), plan_valid=False) is None


@pytest.mark.parametrize('msg', [
  plan('c1', 'pulse', .01), plan('c0', 'pulse', -.03), plan('c0', 'pulse', .04),
  plan('c0', 'pulse', math.nan), plan('c0', 'pulse', .03, run_id=2), plan('c0', 'baseline'),
  plan('c0', 'pulse', .03, speed=SPEEDS[1]), plan('c0', 'release'),
])
def test_midpulse_identity_or_phase_changes_abort(msg):
  test = FordChannelTest()
  pulse(test)
  assert update(test, 10.51, msg) == FordPath()


@pytest.mark.parametrize('phase,delta', [('pulse', .03), ('release', 0.)])
def test_cannot_start_midrun(phase, delta):
  assert update(FordChannelTest(), msg=plan(phase=phase, delta=delta)) == FordPath()


@pytest.mark.parametrize('phase', ['baseline', 'pulse', 'release'])
def test_frozen_phase_times_out_even_with_fresh_timestamps(phase):
  test = FordChannelTest()
  result = None
  for i in range(350):
    stage = 'baseline' if i < 50 or phase == 'baseline' else ('pulse' if i < 100 or phase == 'pulse' else 'release')
    result = update(test, 10.+i*.01, plan(phase=stage, delta=.03 if stage == 'pulse' else 0.))
    if not result.valid:
      break
  assert result == FordPath() and test.aborted


def seq_update(seq, now, **changes):
  return seq.update(now, **({'engaged': True, 'lat_active': True, 'healthy': True, 'ready': True,
                                'driver_input': False, 'speed': TRIALS[min(seq.index, 7)].speed} | changes))


def test_full_suite_with_serialized_20hz_plans_and_100hz_receiver():
  seq, test = Sequence(), FordChannelTest()
  phases, counts, baselines = {}, defaultdict(int), {}
  result = seq_update(seq, 10., engaged=False, lat_active=False)
  msg = plan(result.trial.channel, result.phase, result.delta, result.trial.speed, result.run_id)
  plan_time = 10.
  for i in range(1, 6501):
    now = 10.+i*.01
    if i % 5 == 0:
      result = seq_update(seq, now)
      msg = plan(result.trial.channel, result.phase, result.delta, result.trial.speed, result.run_id)
      plan_time = now
    normal = FordPath(True, .01, .002) if result.phase == 'baseline' else FordPath(True, 1., .2)
    output = update(test, now, msg, plan_valid=result.active, plan_time=plan_time, normal=normal, speed=result.trial.speed)
    if result.active:
      assert output.valid, test.diagnostics
      expected = (.01+result.delta, .002) if result.trial.channel == 'c0' else (.01, .002+result.delta)
      assert (output.path_offset, output.path_angle) == pytest.approx(expected)
      assert output.curvature == output.curvature_rate == 0.
      phases.setdefault(result.run_id, set()).add(result.phase)
      counts[result.run_id, result.phase] += 1
      if result.phase == 'baseline':
        baselines[result.run_id] = output
      if result.phase == 'release':
        assert output == baselines[result.run_id]
    else:
      assert output is None
    if result.text == 'Ford tests finished':
      break
  assert seq.index == 8
  assert len(phases) == 8
  assert all(stages == {'baseline', 'pulse', 'release'} for stages in phases.values())
  assert all(45 <= counts[run, 'pulse'] <= 55 and 195 <= counts[run, 'release'] <= 205 for run in phases)
  assert {(t.speed, t.channel, t.direction) for t in TRIALS} == {(v, c, s) for v in SPEEDS for c in AMPLITUDE for s in (1, -1)}
  assert [t.description for t in TRIALS] == [f'{channel} {direction} {mph} mph'
                                          for mph in (15, 20) for channel in ('C0', 'C1') for direction in ('right', 'left')]


@pytest.mark.parametrize('changes', [{'driver_input': True}, {'healthy': False}, {'lat_active': False},
                                     {'engaged': False}, {'speed': SPEEDS[1]}, {'speed': math.nan}])
def test_sequence_requires_real_disengagement_to_retry(changes):
  seq = Sequence()
  assert seq_update(seq, 10.).phase == 'aborted'  # restarting while engaged cannot arm
  seq_update(seq, 10.05, engaged=False)
  for i in range(1, 45):
    result = seq_update(seq, 10.05+i*.05)
  assert result.active
  assert seq_update(seq, 12.3, **changes).phase == 'aborted'
  for i in range(1, 20):
    assert seq_update(seq, 12.3+i*.05, lat_active=False).phase == 'aborted'
  seq_update(seq, 13.3, engaged=False, lat_active=False)
  for i in range(1, 45):
    result = seq_update(seq, 13.3+i*.05)
  assert result.active and result.run_id == 2 and seq.index == 0


def test_mode_selection_and_transient_parameter(tmp_path):
  params = Params(str(tmp_path))
  assert not params.get_bool('FordChannelTestMode')
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
  assert b'FordChannelTestMode' not in params.all_keys(ParamKeyFlag.BACKUP)


@pytest.mark.parametrize('trial', TRIALS)
def test_actual_controlsd_and_wire_isolate_release_then_abort(pipeline, trial):  # noqa: F811
  call, publication = pipeline
  params = SimpleNamespace(get_bool=lambda key: key in ('FordModelActionController', 'FordChannelTestMode'))
  controls = startup(params=params)
  sm = Subscriptions(True)
  controls.sm, controls.desired_curvature, controls.curvature = sm, 0., 0.
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=trial.speed, yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.,
                       gasPressed=False, brakePressed=False, steeringAngleDeg=0., cruiseState=SimpleNamespace(enabled=True))
  model = straight()
  model.action = SimpleNamespace(desiredCurvature=.0003)
  cp = structs.CarParams(flags=int(FordFlags.CANFD), carFingerprint=controls.CP.carFingerprint)
  sender = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp, structs.CarParamsSP())
  vehicle = SimpleNamespace(out=structs.CarState(vEgo=trial.speed, vEgoRaw=trial.speed), acc_tja_status_stock_values=defaultdict(int),
                            lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], sender.CAN.main)
  baseline = None
  for i in range(151):
    now = 10.+i*.01
    phase = 'baseline' if i < 50 else ('pulse' if i < 100 else 'release')
    delta = trial.direction*AMPLITUDE[trial.channel] if phase == 'pulse' else 0.
    sm.messages['lateralManeuverPlan'] = plan(trial.channel, phase, delta, trial.speed)
    sm.logMonoTime = dict.fromkeys(sm.logMonoTime, round(now*1e9))
    pscm = sm['carStateSP'].fordPscmStatus
    pscm.valid, pscm.canMonoTime, pscm.lateralState = True, round(now*1e9), 2
    cs.brakePressed = i == 150
    if i > 0:
      model.action.desiredCurvature = .03  # normal PI/model requests cannot leak into the held fields
    exec(call, {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                'is_channel_plan': is_channel_plan, 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda t=now: t), 'math': math})
    msg = custom.CarControlSP.new_message()
    exec(publication, {'self': controls, 'CC_SP': msg})
    _, packets = sender.update(cc.as_reader(), convert_carControlSP(msg.as_reader()), vehicle, round(now*1e9))
    parser.update([round(now*1e9), packets])
    wire = parser.vl['LateralMotionControl2']
    if baseline is None:
      baseline = (wire['LatCtlPathOffst_L_Actl'], wire['LatCtlPath_An_Actl'])
    actual = (wire['LatCtlPathOffst_L_Actl'], wire['LatCtlPath_An_Actl'])
    if i == 150:
      assert wire['LatCtl_D2_Rq'] == 0 and actual == (0., 0.) and not cc.latActive
    else:
      expected = (baseline[0]-delta, baseline[1]) if trial.channel == 'c0' else (baseline[0], baseline[1]-delta)
      assert actual == pytest.approx(expected, abs=1e-8)
      assert wire['LatCtl_D2_Rq'] == 2
      assert controls.ford_path_controller.core.correction == 0.
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.


def test_daemon_publishes_both_speeds_and_real_schema(monkeypatch):
  from openpilot.cereal import messaging
  from openpilot.tools.lateral_maneuvers import ford_maneuversd as daemon
  from openpilot.tools.lateral_maneuvers.ford_report import ChannelRuns

  class Finished(Exception):
    pass

  plans, alerts = [], []
  clock = [10.]

  subscribers = []

  class SM(messaging.SubMaster):
    def __init__(self, services, **kwargs):
      super().__init__(services, **kwargs)
      self.events = {s: messaging.new_message(s) for s in services}
      subscribers.append(self)

    def update(self, _timeout):
      cs = self.events['carState'].carState
      cs.vEgo = plans[-1].lateralManeuverPlan.fordChannelTest.speed if plans else SPEEDS[0]
      cs.canValid, cs.cruiseState.enabled = True, True
      self.events['selfdriveState'].selfdriveState.enabled = clock[0] > 10.
      self.events['carControl'].carControl.latActive = clock[0] > 10.
      self.events['carControlSP'].carControlSP.fordLateralPath = {'enabled': True, 'valid': True}
      self.events['carStateSP'].carStateSP.fordPscmStatus = {'valid': True, 'canMonoTime': round(clock[0]*1e9), 'lateralState': 2}
      for msg in self.events.values():
        msg.valid, msg.logMonoTime = True, round(clock[0]*1e9)
      # SubMaster conflates 100 Hz services to the daemon's 20 Hz polling rate.
      # Keep its real frequency/alive/valid checks instead of assuming health.
      self.update_msgs(clock[0], [m.as_reader() for m in self.events.values()])

  class PM:
    def __init__(self, _services):
      pass

    def send(self, service, message):
      message.logMonoTime = round(clock[0]*1e9)
      (plans if service == 'lateralManeuverPlan' else alerts).append(message)
      if service == 'alertDebug' and message.alertDebug.alertText1 == 'Ford tests finished':
        raise Finished

  class Clock:
    def __init__(self, rate):
      assert rate == 20

    def keep_time(self):
      clock[0] += .05
      assert clock[0] < 75., f'Test never completed; frequency checks: {subscribers[0].freq_ok}'

  monkeypatch.setattr(daemon.messaging, 'SubMaster', SM)
  monkeypatch.setattr(daemon.messaging, 'PubMaster', PM)
  monkeypatch.setattr(daemon, 'Ratekeeper', Clock)
  monkeypatch.setattr(daemon, 'time', SimpleNamespace(monotonic=lambda: clock[0]))
  monkeypatch.setattr(daemon, 'cloudlog', SimpleNamespace(event=lambda *_a, **_kw: None))
  with pytest.raises(Finished):
    daemon.main()
  grouped = ChannelRuns()
  for msg in plans:
    grouped.add(msg)
    assert msg.lateralManeuverPlan.desiredCurvature == 0.  # channel plans never pretend to be model references
  assert len(grouped.runs) == 8
  assert all(run.outcome == 'complete' for run in grouped.runs)
  active = {(m.lateralManeuverPlan.fordChannelTest.channel, round(m.lateralManeuverPlan.fordChannelTest.speed, 3))
            for m in plans if m.valid}
  assert active == {(c, round(v, 3)) for c in AMPLITUDE for v in SPEEDS}


def test_enabled_channel_payload_is_ignored_when_toggle_off(pipeline):  # noqa: F811
  controls = startup()
  sm = Subscriptions(True)
  sm.messages['lateralManeuverPlan'] = plan(phase='pulse', delta=.03)
  sm.messages['lateralManeuverPlan'].desiredCurvature = -.1
  controls.sm, controls.desired_curvature, controls.curvature = sm, 0., 0.
  model = straight()
  model.action = SimpleNamespace(desiredCurvature=.1)
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=20., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.)
  exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model, 'lp': SimpleNamespace(roll=0.),
                    'is_channel_plan': is_channel_plan, 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)})
  assert controls.ford_channel_test is None
  assert controls.desired_curvature > 0. and controls.ford_path.path_angle > 0.
  assert controls.ford_path.path_offset == 0.
  assert controls.ford_path_controller.diagnostics['reference_age'] == pytest.approx(.02)
