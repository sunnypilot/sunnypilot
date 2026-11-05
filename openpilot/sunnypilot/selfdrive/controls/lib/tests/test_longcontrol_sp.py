"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace

import pytest

from opendbc.car.structs import car
from openpilot.common.realtime import DT_CTRL
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.sunnypilot.selfdrive.controls.lib.longcontrol_sp import LongControlSP

SMOOTH_STOP_DECEL_RATE = 0.3

LIMITS = (-3.0, 2.0)


def make_control(stop_accel=-2.0, rate=SMOOTH_STOP_DECEL_RATE):
  CP = car.CarParams.new_message()
  CP.stopAccel = stop_accel
  CP.longitudinalTuning.kiBP = [0.0]
  CP.longitudinalTuning.kiV = [0.0]
  CP_SP = custom.CarParamsSP.new_message()
  CP_SP.smoothStopDecelRate = rate
  return LongControlSP(CP, CP_SP)


def make_cs(v_ego, standstill=False):
  return SimpleNamespace(vEgo=v_ego, aEgo=0.0, brakePressed=False, standstill=standstill,
                         cruiseState=SimpleNamespace(standstill=standstill))


def start_stopping(loc, a_target=-0.5):
  loc.update(True, make_cs(0.5), a_target, False, LIMITS)
  return loc.update(True, make_cs(0.3), a_target, True, LIMITS)


def test_decel_ramps_at_stopping_rate():
  loc = make_control()
  out = start_stopping(loc)
  assert loc.long_control_state == LongCtrlState.stopping
  for _ in range(100):
    prev, out = out, loc.update(True, make_cs(0.1), -0.5, True, LIMITS)
    assert out == pytest.approx(prev - SMOOTH_STOP_DECEL_RATE * DT_CTRL)


def test_no_step_at_handover():
  loc = make_control()
  out = loc.update(True, make_cs(0.5), -0.5, False, LIMITS)
  assert abs(start_stopping(loc) - out) <= SMOOTH_STOP_DECEL_RATE * DT_CTRL + 1e-6


def test_decel_never_fades_to_zero_while_stopping():
  loc = make_control()
  outs = [start_stopping(loc)]
  for v in [0.2, 0.1, 0.03, 0.0] * 50:
    outs.append(loc.update(True, make_cs(v, standstill=v == 0.0), -0.5, True, LIMITS))
  assert all(b <= a for a, b in zip(outs, outs[1:], strict=False))


def test_stops_at_stop_accel():
  loc = make_control(-1.5)
  start_stopping(loc)
  for _ in range(int(10.0 / DT_CTRL)):
    out = loc.update(True, make_cs(0.0, standstill=True), -0.5, True, LIMITS)
  assert out == pytest.approx(-1.5, abs=0.01)


def test_positive_output_starts_from_zero():
  loc = make_control()
  loc.update(True, make_cs(0.5), 0.3, False, LIMITS)
  assert start_stopping(loc, a_target=0.3) <= 0.0


def test_repeatable():
  runs = []
  for _ in range(2):
    loc = make_control()
    runs.append([start_stopping(loc)] + [loc.update(True, make_cs(0.1), -0.5, True, LIMITS) for _ in range(300)])
  assert runs[0] == runs[1]


def test_disabled_uses_stock_stopping_behavior():
  loc = make_control(rate=0.0)
  start_stopping(loc)
  prev = loc.last_output_accel
  assert loc.update(True, make_cs(0.1), -0.5, True, LIMITS) == pytest.approx(prev - 1.0 * DT_CTRL)


@pytest.mark.parametrize("rate", [0.3, 0.8, 2.0])
def test_rate_comes_from_car_params(rate):
  loc = make_control(rate=rate)
  out = start_stopping(loc)
  assert loc.update(True, make_cs(0.1), -0.5, True, LIMITS) == pytest.approx(out - rate * DT_CTRL)
