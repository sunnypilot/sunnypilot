import pytest

from opendbc.car import DT_CTRL, gen_empty_fingerprint, structs
from opendbc.car.car_helpers import interfaces
from opendbc.car.ford.values import CAR as FORD
from opendbc.car.gm.values import CAR as GM
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState, long_control_state_trans


VEHICLES = [
  pytest.param(TOYOTA.TOYOTA_RAV4_TSS2, (True, False, 0.0, -2.0, 0.25, 0.25, 0.3), id="toyota-rav4-tss2"),
  pytest.param(HONDA.HONDA_ACCORD, (True, False, 0.0, -2.0, 0.5, 0.5, 0.8), id="honda-accord"),
  pytest.param(GM.CHEVROLET_BOLT_EUV, (True, False, 0.0, -2.0, 0.25, 0.25, 2.0), id="gm-bolt-euv"),
  pytest.param(HYUNDAI.HYUNDAI_SONATA, (True, True, 1.0, -2.0, 0.1, 0.5, 0.8), id="hyundai-sonata"),
  pytest.param(FORD.FORD_ESCAPE_MK4, (True, False, 0.0, -2.0, 0.5, 0.5, 0.8), id="ford-escape"),
]


def get_car_params(candidate):
  fingerprint = gen_empty_fingerprint()
  interface = interfaces[candidate]
  CP = interface.get_params(candidate, fingerprint, [], True, False, False)
  CP_SP = interface.get_params_sp(CP, candidate, fingerprint, [], True, False, False)
  return CP, CP_SP


@pytest.mark.parametrize(("candidate", "expected"), VEHICLES)
def test_real_vehicle_longcontrol_stop_and_start(candidate, expected):
  CP, CP_SP = get_car_params(candidate)
  expected_long, expected_starting, *expected_tuning = expected

  assert CP.openpilotLongitudinalControl is expected_long
  assert CP.startingState is expected_starting
  assert (CP.startAccel, CP.stopAccel, CP.vEgoStarting, CP.vEgoStopping, CP.stoppingDecelRate) == pytest.approx(expected_tuning)

  stop_speeds = [CP.vEgoStopping - 0.01] * 2
  drive_speeds = [CP.vEgoStopping + 0.01] * 2
  _, should_stop = get_accel_from_plan(stop_speeds, [0.0, 0.0], [0.0, 1.0], vEgoStopping=CP.vEgoStopping)
  _, should_drive = get_accel_from_plan(drive_speeds, [0.0, 0.0], [0.0, 1.0], vEgoStopping=CP.vEgoStopping)
  assert should_stop
  assert not should_drive

  departure_state = long_control_state_trans(
    CP,
    CP_SP,
    True,
    LongCtrlState.stopping,
    CP.vEgoStarting - 0.01,
    should_drive,
    brake_pressed=False,
    cruise_standstill=False,
  )
  assert departure_state == (LongCtrlState.starting if CP.startingState else LongCtrlState.pid)
  assert (
    long_control_state_trans(
      CP,
      CP_SP,
      True,
      departure_state,
      CP.vEgoStarting + 0.01,
      should_drive,
      brake_pressed=False,
      cruise_standstill=False,
    )
    == LongCtrlState.pid
  )

  CS = structs.CarState()
  CS.vEgo = 0.0
  CS.aEgo = 0.0
  control = LongControl(CP, CP_SP)

  stopping_accel = control.update(True, CS, 0.0, should_stop, (-3.0, 2.0))
  assert control.long_control_state == LongCtrlState.stopping
  assert stopping_accel == pytest.approx(-CP.stoppingDecelRate * DT_CTRL)

  departure_accel = control.update(True, CS, 0.0, should_drive, (-3.0, 2.0))
  assert control.long_control_state == departure_state
  assert departure_accel == pytest.approx(CP.startAccel)
