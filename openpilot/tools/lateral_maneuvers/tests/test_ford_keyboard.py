"""Offline keyboard, maneuver, and real controller/CAN checks; no hardware actuation."""
import math
from types import SimpleNamespace

import pytest

from opendbc.car.structs import car
from openpilot.cereal import log, messaging
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.controls.lib.ford_channel_test import KEYBOARD_PARAM, PARAM, SPEEDS, FordChannelTest
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup
from openpilot.tools.joystick.ford_keyboard_control import KeyboardControl, enable
from openpilot.tools.lateral_maneuvers import ford_keyboard as daemon
from openpilot.tools.lateral_maneuvers.ford_keyboard import KeyboardManeuver, BASELINE_S, STEP_S, RELEASE_S


def request(**kw):
  return log.Joystick.FordKeyboard.new_message(**({'requestId': 0, 'channel': 'c0', 'speed': SPEEDS[0],
                                                  'accel': .5, 'action': 'idle'} | kw))


def step(test, t, req, **kw):
  test.update(t, req, **({'input_time': t, 'input_valid': True, 'healthy': True, 'ready': True,
                         'speed': req.speed, 'curvature': .001} | kw))
  return test.plan(kw.get('speed', req.speed))


def ready(test, req, start=10.):
  for i in range(42):
    step(test, start+i*.05, req)
  assert test.status == 'Ready: A left / D right'
  return start+2.10


@pytest.mark.parametrize('channel', ['c0', 'c1'])
@pytest.mark.parametrize('speed', SPEEDS)
@pytest.mark.parametrize('direction,sign', [('left', -1), ('right', 1)])
@pytest.mark.parametrize('amplitude', [.25, .5, 3.])
def test_timed_step_uses_normal_curvature_then_returns_to_baseline(channel, speed, direction, sign, amplitude):
  test = KeyboardManeuver()
  req = request(channel=channel, speed=speed, accel=amplitude)
  start = ready(test, req)
  req.requestId, req.action = 1, direction
  plans = [step(test, start+i*.05, req) for i in range(61)]
  assert plans[0].valid and not plans[-1].valid
  assert plans[-1].lateralManeuverPlan.fordChannelTest.phase == 'complete'
  phases = [str(p.lateralManeuverPlan.fordChannelTest.keyboardPhase) for p in plans[:-1]]
  assert {'baseline', 'pulse', 'release'} == set(phases)
  assert sum(x == 'pulse' for x in phases)*.05 == pytest.approx(STEP_S, abs=.05)
  for p in plans[:-1]:
    plan = p.lateralManeuverPlan
    expected = .001+(sign*amplitude/speed**2 if plan.fordChannelTest.keyboardPhase == 'pulse' else 0.)
    assert plan.desiredCurvature == pytest.approx(expected)
    assert plan.fordChannelTest.phase == 'maneuver' and plan.fordChannelTest.delta == 0.
    assert plan.fordChannelTest.keyboardRequestId == 1
    assert plan.fordChannelTest.targetAccel == pytest.approx(sign*amplitude)
  for i in range(1, 81):
    step(test, start+3.+i*.05, req)
    assert not test.active  # holding the last trigger never repeats a step


@pytest.mark.parametrize('fault', [
  {'input_valid': False}, {'input_time': 1.}, {'input_time': 100.}, {'healthy': False},
  {'speed': SPEEDS[0]+.71}, {'speed': math.nan}, {'curvature': math.nan},
])
def test_abort_never_queues_or_retries_old_request(fault):
  test, req = KeyboardManeuver(), request()
  start = ready(test, req)
  req.requestId, req.action = 1, 'left'
  assert step(test, start, req).valid
  assert not step(test, start+.05, req, **fault).valid
  for i in range(1, 61):
    assert not step(test, start+.05+i*.05, req).valid
  req.requestId = 2
  assert step(test, start+3.10, req).valid


def test_unready_and_busy_keypresses_are_consumed_not_queued():
  test, req = KeyboardManeuver(), request(requestId=1, action='right')
  start = ready(test, req)
  assert not test.active
  req.requestId = 2
  assert step(test, start, req).valid
  req.requestId, req.action, req.channel, req.accel = 3, 'left', 'c1', 3.
  for i in range(1, 121):
    p = step(test, start+i*.05, req)
    if p.valid:
      assert p.lateralManeuverPlan.fordChannelTest.channel == 'c0'
      assert p.lateralManeuverPlan.fordChannelTest.targetAccel == .5
  assert test.run_id == 1 and not test.active


@pytest.mark.parametrize('changes', [{'channel': 'none'}, {'accel': math.nan}, {'accel': 3.25}, {'accel': 0.}, {'speed': 0.}])
def test_bad_input_cannot_trigger(changes):
  test, req = KeyboardManeuver(), request()
  start = ready(test, req)
  req.requestId, req.action = 1, 'right'
  for k, v in changes.items():
    setattr(req, k, v)
  assert not step(test, start, req).valid


def test_frozen_time_clock_gap_and_cancel_abort():
  for delta in [0., -.1, .151]:
    test, req = KeyboardManeuver(), request()
    start = ready(test, req)
    req.requestId, req.action = 1, 'right'
    step(test, start, req)
    assert not step(test, start+delta, req).valid
  test, req = KeyboardManeuver(), request()
  start = ready(test, req)
  req.requestId, req.action = 1, 'right'
  step(test, start, req)
  req.requestId, req.action = 2, 'cancel'
  assert not step(test, start+.05, req).valid
  assert test.phase == 'aborted'


def test_keyboard_mapping_heartbeat_repeat_suppression_and_cancel():
  control = KeyboardControl()
  for key in ('2', '+', 'v'):
    assert control.key(key, 10.)
  control.key('a', 11.)
  p = control.message().testJoystick
  assert list(p.axes) == [0., 0.]
  assert p.fordKeyboard.channel == 'c1' and p.fordKeyboard.action == 'left'
  assert p.fordKeyboard.accel == .75 and p.fordKeyboard.speed == pytest.approx(SPEEDS[1])
  first = p.fordKeyboard.requestId
  for i in range(1, 101):
    control.key('a', 11.+i*.05)
    assert control.message().testJoystick.fordKeyboard.requestId == first
  control.key('a', 17.)
  assert control.request.requestId > first
  control.key('r', 18.)
  assert control.request.action == 'cancel'
  assert not control.key('q', 19.)


@pytest.mark.parametrize('kwargs', [{'speed': 10}, {'accel': math.nan}, {'accel': math.inf}, {'accel': 0.}, {'accel': 3.1}])
def test_cli_rejects_invalid_settings(kwargs):
  with pytest.raises(ValueError):
    KeyboardControl(**kwargs)


def test_offroad_setup_and_mode_lifecycle_use_real_params(tmp_path):
  params = Params(str(tmp_path))
  cp = car.CarParams.new_message(brand='ford', flags=1)
  params.put('CarParamsPersistent', cp.to_bytes(), block=True)
  params.put_bool('FordModelActionController', True, block=True)
  with pytest.raises(ValueError, match='offroad'):
    enable(params)
  params.put_bool('IsOffroad', True, block=True)
  params.put_bool('JoystickDebugMode', True, block=True)
  params.put_bool(PARAM, True, block=True)
  enable(params)
  assert params.get_bool(KEYBOARD_PARAM) and not params.get_bool(PARAM) and not params.get_bool('JoystickDebugMode')
  assert startup(params=params).ford_channel_test.keyboard
  params.put_bool('IsOffroad', False, block=True)
  enable(params)  # reconnect to the selected mode, without an ignition cycle
  params.put_bool(PARAM, True, block=True)
  with pytest.raises(ValueError, match='offroad'):
    enable(params)
  assert params.get_bool(PARAM)  # a refused onroad mode change has no side effects
  params.put_bool(PARAM, False, block=True)
  for flag in (ParamKeyFlag.CLEAR_ON_MANAGER_START, ParamKeyFlag.CLEAR_ON_OFFROAD_TRANSITION):
    params.put_bool(KEYBOARD_PARAM, True, block=True)
    params.clear_all(flag)
    assert not params.get_bool(KEYBOARD_PARAM)
  for brand, flags in [('toyota', 1), ('ford', 0)]:
    params.put_bool('IsOffroad', True, block=True)
    params.put('CarParamsPersistent', car.CarParams.new_message(brand=brand, flags=flags).to_bytes(), block=True)
    with pytest.raises(ValueError, match='CAN FD Ford'):
      enable(params)


def test_keyboard_plan_requires_keyboard_mode():
  test, req = KeyboardManeuver(), request()
  start = ready(test, req)
  req.requestId, req.action = 1, 'right'
  p = step(test, start, req).lateralManeuverPlan
  from openpilot.selfdrive.controls.tests.test_ford_channel_test import update
  assert not update(FordChannelTest(), msg=p).valid
  assert update(FordChannelTest(keyboard=True), msg=p).valid


@pytest.mark.parametrize('keyboard', [False, True])
def test_manager_imported_entrypoint_selects_the_correct_daemon(monkeypatch, keyboard):
  # Manager imports the module and calls main(); it does not execute __main__.
  from openpilot.tools.lateral_maneuvers import ford_maneuversd
  calls = []
  monkeypatch.setattr(ford_maneuversd, 'Params', lambda: SimpleNamespace(get_bool=lambda _key: keyboard))
  monkeypatch.setattr(ford_maneuversd, 'keyboard_main', lambda: calls.append('keyboard'))
  monkeypatch.setattr(ford_maneuversd, 'suite_main', lambda **kw: calls.append(kw))
  ford_maneuversd.main()
  assert calls == (['keyboard'] if keyboard else [{'ford_channels': True}])


def test_real_daemon_allows_mads_manual_throttle_and_publishes_complete_run(monkeypatch):
  class Finished(Exception):
    pass
  clock, plans = [10.], []
  class SM(messaging.SubMaster):
    def __init__(self, services, **kwargs):
      super().__init__(services, **kwargs)
      self.events = {s: messaging.new_message(s) for s in services}

    def update(self, _timeout):
      clock[0] += .05
      assert clock[0] < 20
      cs = self.events['carState'].carState
      cs.vEgo, cs.canValid, cs.gasPressed, cs.cruiseState.enabled = SPEEDS[0], True, True, False
      self.events['carControl'].carControl.latActive = True  # MADS, selfdriveState.enabled remains false
      self.events['carStateSP'].carStateSP.fordPscmStatus = {'valid': True, 'canMonoTime': round(clock[0]*1e9), 'lateralState': 2}
      self.events['testJoystick'].testJoystick.fordKeyboard = request(requestId=1 if clock[0] > 12.5 else 0, action='right')
      for msg in self.events.values():
        msg.valid, msg.logMonoTime = True, round(clock[0]*1e9)
      self.update_msgs(clock[0], [m.as_reader() for m in self.events.values()])

  class PM:
    def __init__(self, _services):
      pass

    def send(self, service, msg):
      if service == 'lateralManeuverPlan':
        plans.append(msg)
        if msg.lateralManeuverPlan.fordChannelTest.phase == 'complete':
          raise Finished

  monkeypatch.setattr(daemon.messaging, 'SubMaster', SM)
  monkeypatch.setattr(daemon.messaging, 'PubMaster', PM)
  monkeypatch.setattr(daemon, 'time', SimpleNamespace(monotonic=lambda: clock[0]))
  monkeypatch.setattr(daemon, 'Ratekeeper', lambda *_a, **_kw: SimpleNamespace(keep_time=lambda: None))
  with pytest.raises(Finished):
    daemon.main()
  active = [p for p in plans if p.valid]
  assert len(active)*.05 == pytest.approx(BASELINE_S+STEP_S+RELEASE_S, abs=.05)
  assert {str(p.lateralManeuverPlan.fordChannelTest.keyboardPhase) for p in active} == {'baseline', 'pulse', 'release'}
