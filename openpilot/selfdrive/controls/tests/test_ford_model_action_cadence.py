"""Exercise 100Hz calculation and 20Hz transmission through the real CAN sender."""
from collections import defaultdict
from types import SimpleNamespace

import pytest

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.fordcan import calculate_lat_ctl2_checksum
from opendbc.car.ford.values import FordFlags, FordFlagsSP, FordSafetyFlags
from opendbc.safety.tests.libsafety import libsafety_py
from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


def sender(canfd=True, selected=True):
  cp = structs.CarParams(flags=int(FordFlags.CANFD) if canfd else 0, carFingerprint='FORD_F_150_LIGHTNING_MK1',
                         safetyConfigs=[structs.CarParams.SafetyConfig()])
  cp_sp = structs.CarParamsSP(flags=int(FordFlagsSP.MODEL_ACTION) if selected else 0)
  controller = CarController({Bus.pt: 'ford_lincoln_base_pt'}, cp, cp_sp)
  cs = SimpleNamespace(out=structs.CarState(vEgo=20., vEgoRaw=20.), acc_tja_status_stock_values=defaultdict(int),
                       lkas_status_stock_values=defaultdict(int), buttons_stock_values=defaultdict(int))
  return controller, cs


@pytest.mark.parametrize('canfd,selected,step', [(True, True, 5), (True, False, 1), (False, True, 5), (False, False, 5)])
def test_send_intervals_latest_sample_counter_and_checksum(canfd, selected, step):
  controller, cs = sender(canfd, selected)
  cc, sp = structs.CarControl(latActive=True), structs.CarControlSP()
  sp.fordLateralPath.valid = True
  name = 'LateralMotionControl2' if canfd else 'LateralMotionControl'
  address = 0x3d6 if canfd else 0x3d3
  parser = CANParser('ford_lincoln_base_pt', [(name, 0)], controller.CAN.main)
  sent = []
  for frame in range(1000):
    sp.fordLateralPath.pathOffset = (frame % 101 - 50) * .01
    sp.fordLateralPath.pathAngle = (frame % 101 - 50) * .0005
    _, packets = controller.update(cc.as_reader(), sp, cs, frame * 10_000_000)
    lateral = [p for p in packets if p[0] == address]
    assert len(lateral) == int(frame % step == 0)
    if not lateral:
      continue
    sent.append(frame)
    parser.update([frame * 10_000_000, lateral])
    wire = parser.vl[name]
    assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(-sp.fordLateralPath.pathOffset)
    assert wire['LatCtlPath_An_Actl'] == pytest.approx(-sp.fordLateralPath.pathAngle)
    if canfd:
      counter = (len(sent) - 1) % 16
      assert wire['LatCtlPath_No_Cnt'] == counter
      assert wire['LatCtlPath_No_Cs'] == calculate_lat_ctl2_checksum(2, counter, lateral[0][1])
  assert sent == list(range(0, 1000, step))


@pytest.mark.parametrize('failure_frame', range(1, 6))
@pytest.mark.parametrize('disengage', [False, True])
def test_next_scheduled_frame_clears_invalid_or_inactive_path(failure_frame, disengage):
  controller, cs = sender()
  cc, sp = structs.CarControl(latActive=True), structs.CarControlSP()
  sp.fordLateralPath.valid = True
  sp.fordLateralPath.pathOffset, sp.fordLateralPath.pathAngle = .4, .1
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 0)], controller.CAN.main)
  for frame in range(11):
    if frame == failure_frame:
      if disengage:
        cc.latActive = False
      else:
        sp.fordLateralPath.valid = False
    _, packets = controller.update(cc.as_reader(), sp, cs, frame * 10_000_000)
    lateral = [p for p in packets if p[0] == 0x3d6]
    assert len(lateral) == int(frame % 5 == 0)
    if lateral and frame >= failure_frame:
      parser.update([frame * 10_000_000, lateral])
      wire = parser.vl['LateralMotionControl2']
      assert wire['LatCtl_D2_Rq'] == (0 if disengage else 2)
      assert all(wire[k] == 0. for k in ('LatCtlPathOffst_L_Actl', 'LatCtlPath_An_Actl', 'LatCtlCurv_No_Actl', 'LatCtlCrv_NoRate2_Actl'))


def test_core_slew_per_second_and_actual_panda_acceptance():
  controller, cs = sender()
  core = ModelActionController()
  cc, sp = structs.CarControl(latActive=True), structs.CarControlSP()
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 0)], controller.CAN.main)
  safety = libsafety_py.libsafety
  assert safety.set_safety_hooks(structs.CarParams.SafetyModel.ford, FordSafetyFlags.CANFD) == 0
  safety.init_tests()
  safety.set_controls_allowed(True)
  frames = []
  for frame in range(100):
    command = core.update(straight(10.), .1, speed=20., dt=.01, pose_yaw_rate=0.)
    assert core.c0 == pytest.approx((frame + 1) * .04)
    assert core.c1 == pytest.approx((frame + 1) * .005)
    sp.fordLateralPath.valid = command.valid
    sp.fordLateralPath.pathOffset, sp.fordLateralPath.pathAngle = command.path_offset, command.path_angle
    _, packets = controller.update(cc.as_reader(), sp, cs, frame * 10_000_000)
    for address, data, bus in packets:
      if address != 0x3d6:
        continue
      frames.append(frame)
      safety.set_timer(frame * 10_000)
      assert safety.safety_tx_hook(libsafety_py.make_CANPacket(address, bus, data))
      parser.update([frame * 10_000_000, [(address, data, bus)]])
      wire = parser.vl['LateralMotionControl2']
      assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(-command.path_offset)
      assert wire['LatCtlPath_An_Actl'] == pytest.approx(-command.path_angle)
      assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
  assert frames == list(range(0, 100, 5))
