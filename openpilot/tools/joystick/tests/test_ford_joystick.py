"""Run joystickd offline through real messages, the Ford CAN encoder, and alerts."""
from collections import defaultdict
from types import SimpleNamespace

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.structs import car
from opendbc.car.ford.carcontroller import CarController
from openpilot.cereal import messaging
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.selfdrived.events import joystick_alert, joystick_permanent_alert
from openpilot.tools.joystick import joystick_control as frontend, joystickd as daemon


def car_params(brand='ford', flags=1):
  return car.CarParams.new_message(brand=brand, flags=flags, carFingerprint='FORD_F_150_LIGHTNING_MK1',
                                  mass=3000., rotationalInertia=5500., wheelbase=3.7, centerToFront=1.7,
                                  steerRatio=16., tireStiffnessFront=100000., tireStiffnessRear=100000.,
                                  pcmCruise=True, openpilotLongitudinalControl=True)


def run_daemon(monkeypatch, samples, CP=None, module=daemon):
  CP = car_params() if CP is None else CP
  raw_cp = CP.to_bytes()
  outputs, index = defaultdict(list), [-1]

  class Finished(Exception):
    pass

  class SM(messaging.SubMaster):
    def update(self, _timeout):
      index[0] += 1
      sample = samples[index[0]]
      t = 10.+index[0]*.01
      messages = []
      for service in self.services:
        if (service == 'vehicleParameters' and index[0] % 5) or (service == 'onroadEvents' and index[0] % 100):
          continue
        if service == 'testJoystick' and not sample.get('send', True):
          continue
        msg = messaging.new_message(service, 0) if service == 'onroadEvents' else messaging.new_message(service)
        msg.valid, msg.logMonoTime = True, round(t*1e9)
        if service == 'carState':
          cs = msg.carState
          cs.vEgo, cs.vEgoRaw = sample.get('speed', 10.), sample.get('speed', 10.)
          cs.canValid = sample.get('can', True)
          cs.cruiseState.enabled = True
          cs.steeringAngleDeg = 2.
          cs.brakePressed = sample.get('brake', False)
          cs.steerFaultTemporary = sample.get('fault', False)
        elif service == 'selfdriveState':
          msg.selfdriveState.enabled = msg.selfdriveState.active = sample.get('active', True)
        elif service == 'testJoystick':
          msg.valid = sample.get('valid', True)
          msg.testJoystick.axes = sample.get('axes', [sample.get('gb', .2), sample.get('steer', 0.)])
          msg.testJoystick.fordChannel = sample.get('channel', 'standard')
        messages.append(msg.as_reader())
      self.update_msgs(t, messages)

  class PM:
    def __init__(self, services):
      self.services = services

    def send(self, service, msg):
      assert service in self.services
      outputs[service].append(msg.as_reader())

  class RK:
    def __init__(self, *args, **kwargs):
      pass

    def keep_time(self):
      if index[0] == len(samples)-1:
        raise Finished

  with monkeypatch.context() as mp:
    mp.setattr(module, 'Params', lambda: SimpleNamespace(get=lambda *a, **kw: raw_cp))
    mp.setattr(module.messaging, 'SubMaster', SM)
    mp.setattr(module.messaging, 'PubMaster', PM)
    mp.setattr(module, 'Ratekeeper', RK)
    with pytest.raises(Finished):
      module.joystickd_thread()
  return outputs


@pytest.mark.parametrize('channel', ['c0', 'c1'])
@pytest.mark.parametrize('speed', [0., 1., 6.7, 20., 35.])
@pytest.mark.parametrize('steer', [-1., -.05, .05, 1.])
def test_direct_field_reaches_real_can_at_any_speed(monkeypatch, channel, speed, steer):
  samples = [{'channel': channel, 'speed': speed}]*40 + [{'channel': channel, 'speed': speed, 'steer': steer}]*10
  output = run_daemon(monkeypatch, samples)
  cp = structs.CarParams(flags=1, carFingerprint='FORD_F_150_LIGHTNING_MK1')
  sender = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp, structs.CarParamsSP())
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], sender.CAN.main)
  vehicle = SimpleNamespace(out=structs.CarState(vEgo=speed, vEgoRaw=speed), acc_tja_status_stock_values=defaultdict(int),
                            lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
  for i in range(40, 50):
    cc, extra = output['carControl'][i].carControl, output['carControlSP'][i].carControlSP
    assert cc.latActive and cc.longActive and cc.actuators.accel == pytest.approx(.8)
    assert cc.actuators.curvature == cc.actuators.steeringAngleDeg == cc.actuators.torque == 0.
    _, packets = sender.update(cc, convert_carControlSP(extra), vehicle, round((10+i*.01)*1e9))
    parser.update([round((10+i*.01)*1e9), packets])
    wire = parser.vl['LateralMotionControl2']
    assert wire['LatCtl_D2_Rq'] == 2
    assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(steer*5.11 if channel == 'c0' else 0., abs=.0051)
    assert wire['LatCtlPath_An_Actl'] == pytest.approx(steer*.5 if channel == 'c1' else 0., abs=.000251)
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
  alert = output['alertDebug'][-1].alertDebug
  assert alert.alertText1 == f'Joystick Mode — {channel.upper()} only'
  assert 'Wheel: +2.0°' in alert.alertText2


@pytest.mark.parametrize('fault', [{'active': False}, {'fault': True}, {'can': False}, {'valid': False},
                                 {'axes': [0.]}, {'axes': [0., float('nan')]}, {'send': False}])
def test_interruptions_zero_commands_and_require_center_before_restart(monkeypatch, fault):
  base = {'channel': 'c0', 'steer': .5}
  samples = [{'channel': 'c0'}]*40 + [base]*5 + [base | fault]*25 + [base]*5 + [base | {'steer': 0.}]*2 + [base]*2
  output = run_daemon(monkeypatch, samples)
  for i in (44, 78):
    assert output['carControl'][i].carControl.latActive
    assert output['carControlSP'][i].carControlSP.fordLateralPath.pathOffset != 0.
  for i in (69, 74):
    assert not output['carControl'][i].carControl.latActive
    path = output['carControlSP'][i].carControlSP.fordLateralPath
    assert path.enabled and not path.valid
    assert path.pathOffset == path.pathAngle == path.curvature == path.curvatureRate == 0.


def test_switch_cannot_reinterpret_a_held_command_and_standard_clears_path(monkeypatch):
  samples = ([{'channel': 'c0'}]*40 + [{'channel': 'c0', 'steer': .5}]*2
             + [{'channel': 'c1', 'steer': .5}]*2 + [{'channel': 'c1'}]*2 + [{'channel': 'c1', 'steer': .5}]*2
             + [{'channel': 'standard', 'steer': .5}]*2 + [{'channel': 'standard'}]*2 + [{'channel': 'standard', 'steer': .5}]*2)
  output = run_daemon(monkeypatch, samples)
  for i in (42, 43, 48, 49):
    assert not output['carControl'][i].carControl.latActive
  path = output['carControlSP'][46].carControlSP.fordLateralPath
  assert path.pathOffset == 0. and path.pathAngle == -.25
  assert output['carControl'][53].carControl.actuators.torque == .5
  assert not output['carControlSP'][53].carControlSP.fordLateralPath.enabled
  assert not output['alertDebug'][53].valid


@pytest.mark.parametrize('brand,flags', [('ford', 0), ('honda', 1)])
def test_explicit_ford_channel_does_not_fall_back_to_other_car_steering(monkeypatch, brand, flags):
  output = run_daemon(monkeypatch, [{'channel': 'c1'}]*40+[{'channel': 'c1', 'steer': 1.}]*2, car_params(brand, flags))
  cc = output['carControl'][-1].carControl
  assert not cc.latActive and cc.actuators.torque == cc.actuators.curvature == 0.
  assert cc.actuators.accel == pytest.approx(.8)
  assert 'carControlSP' not in output


def test_keyboard_opt_in_selection_does_not_change_normal_keys(monkeypatch):
  keys = iter('wa2a1d0ar')
  monkeypatch.setattr(frontend, 'KBHit', lambda: SimpleNamespace(getch=lambda: next(keys)))
  kb = frontend.Keyboard('c0')
  kb.update()
  kb.update()
  assert kb.axes_values == {'gb': .05, 'steer': .05}
  for channel, steer in [('c1', 0.), ('c1', .05), ('c0', 0.), ('c0', -.05), ('standard', 0.), ('standard', .05), ('standard', 0.)]:
    kb.update()
    assert kb.ford_channel == channel and kb.axes_values['steer'] == steer
  assert kb.axes_values['gb'] == 0.
  monkeypatch.setattr(frontend, 'KBHit', lambda: SimpleNamespace(getch=lambda: '2'))
  assert not frontend.Keyboard().update()  # opt-out keeps the previously unused key unused


def test_alert_names_selected_channel_and_preserves_standard_text():
  sm = messaging.SubMaster(['carControl', 'alertDebug'])
  cp, cs = car_params(), car.CarState.new_message()
  cc = messaging.new_message('carControl')
  cc.carControl.actuators.accel, cc.carControl.actuators.torque = 2., -.2
  sm.update_msgs(10., [cc.as_reader()])
  alert = joystick_alert(cp, cs, sm, False, 0, None)
  assert alert.alert_text_1 == 'Joystick Mode' and alert.alert_text_2 == 'Gas: 50%, Steer: -20%'
  assert joystick_permanent_alert(cp, cs, sm, False, 0, None).alert_text_2 == ''
  for i, channel in enumerate(('C0', 'C1')):
    msg = messaging.new_message('alertDebug')
    msg.valid = True
    msg.alertDebug.alertText1, msg.alertDebug.alertText2 = f'Joystick Mode — {channel} only', 'command / wheel'
    sm.update_msgs(10.01+i*.01, [msg.as_reader()])
    for callback in (joystick_alert, joystick_permanent_alert):
      assert callback(cp, cs, sm, False, 0, None).alert_text_1 == f'Joystick Mode — {channel} only'


@pytest.mark.parametrize('channel', ['standard', 'c0', 'c1'])
def test_existing_sender_publishes_channel_with_unchanged_axes(monkeypatch, channel):
  class Finished(Exception):
    pass

  def done():
    raise Finished

  captured = []
  monkeypatch.setattr(frontend.messaging, 'PubMaster', lambda _services: SimpleNamespace(send=lambda _s, m: captured.append(m.as_reader())))
  monkeypatch.setattr(frontend, 'Ratekeeper', lambda *a, **kw: SimpleNamespace(frame=0, keep_time=done))
  joystick = SimpleNamespace(axes_values={'gb': -.2, 'steer': .35}, axes_order=['gb', 'steer'], ford_channel=channel)
  with pytest.raises(Finished):
    frontend.send_thread(joystick)
  assert captured[0].testJoystick.fordChannel == channel
  assert list(captured[0].testJoystick.axes) == pytest.approx([-.2, .35])
