from opendbc.car.structs import car

from openpilot.common.realtime import DT_CTRL
from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.longcontrol import (LongControl, LongCtrlState, STOPPING_HOLD_SPEED,
                                                           STOPPING_JERK, long_control_state_trans)


class TestLongControlStateTransition(OpenpilotTestCase):

  def test_stay_stopped(self):
    CP_SP = custom.CarParamsSP.new_message()
    active = True
    current_state = LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=True, brake_pressed=False, cruise_standstill=False)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=True, cruise_standstill=False)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=False, cruise_standstill=True)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=False, cruise_standstill=False)
    assert next_state == LongCtrlState.pid
    active = False
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=False, cruise_standstill=False)
    assert next_state == LongCtrlState.off

  def test_engage(self):
    CP_SP = custom.CarParamsSP.new_message()
    active = True
    current_state = LongCtrlState.off
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=True, brake_pressed=False, cruise_standstill=False)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=True, cruise_standstill=False)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=False, cruise_standstill=True)
    assert next_state == LongCtrlState.stopping
    next_state = long_control_state_trans(CP_SP, active, current_state,
                             should_stop=False, brake_pressed=False, cruise_standstill=False)
    assert next_state == LongCtrlState.pid


class TestLongControlStopping(OpenpilotTestCase):
  def _long_control(self, stop_accel=-2.0, entry_accel=-1.2, v_ego=0.3):
    CP = car.CarParams.new_message()
    CP.longitudinalTuning.kiBP = [0.0]
    CP.longitudinalTuning.kiV = [0.0]
    CP.stopAccel = stop_accel
    lc = LongControl(CP, custom.CarParamsSP.new_message())
    lc.long_control_state = LongCtrlState.stopping
    lc.last_output_accel = entry_accel

    CS = car.CarState.new_message()
    CS.vEgo = float(v_ego)
    CS.brakePressed = False
    CS.cruiseState.standstill = False
    return lc, CS

  def _run_stop(self, lc, CS, frames=500):
    accels = []
    distance = 0.0
    for _ in range(frames):
      accels.append(lc.update(True, CS, 0.0, True, (-4.0, 2.0)))
      if CS.vEgo < STOPPING_HOLD_SPEED:
        break
      distance += CS.vEgo * DT_CTRL
      CS.vEgo = float(max(0.0, CS.vEgo + accels[-1] * DT_CTRL))
    return accels, distance

  def test_releases_braking_instead_of_ramping_to_stop_accel(self):
    lc, CS = self._long_control(entry_accel=-1.2)
    accels, _ = self._run_stop(lc, CS)
    # the stop state must ease off the brake, not add more of it as the car slows
    assert accels[0] > -1.2
    assert accels[-2] > accels[0]
    # and it must actually get gentle before standstill instead of stopping at the entry decel
    assert accels[-2] > -0.8

  def test_never_increases_decel_while_rolling(self):
    lc, CS = self._long_control(entry_accel=-1.2)
    accels, _ = self._run_stop(lc, CS)
    rolling = accels[:-1]
    assert all(b >= a - 1e-9 for a, b in zip(rolling[:-1], rolling[1:], strict=False)), rolling

  def test_jerk_is_bounded(self):
    lc, CS = self._long_control(entry_accel=-1.5)
    accels, _ = self._run_stop(lc, CS)
    rolling = accels[:-1]
    max_step = max(abs(b - a) for a, b in zip(rolling[:-1], rolling[1:], strict=False))
    assert max_step <= STOPPING_JERK * DT_CTRL + 1e-9

  def test_holds_with_stop_accel_at_standstill(self):
    lc, CS = self._long_control(stop_accel=-2.0)
    accels, _ = self._run_stop(lc, CS)
    assert CS.vEgo < STOPPING_HOLD_SPEED
    assert accels[-1] == -2.0

  def test_weak_entry_does_not_add_braking(self):
    lc, CS = self._long_control(entry_accel=-0.2)
    accels, _ = self._run_stop(lc, CS)
    assert min(accels[:-1]) >= -0.2 - 1e-9

  def test_never_commands_positive_accel(self):
    lc, CS = self._long_control(entry_accel=0.5)
    accels, _ = self._run_stop(lc, CS)
    assert max(accels) <= 0.0

  def test_stops_within_short_distance(self):
    lc, CS = self._long_control(entry_accel=-1.2)
    _, distance = self._run_stop(lc, CS)
    assert CS.vEgo < STOPPING_HOLD_SPEED
    assert distance < 0.25
