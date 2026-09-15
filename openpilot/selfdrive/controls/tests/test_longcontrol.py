from types import SimpleNamespace

from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState, long_control_state_trans
from openpilot.sunnypilot.selfdrive.controls.lib.longcontrol import LongControlSP


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


class TestStoppingHold:
  def test_weak_brake_does_not_hold_stopping(self):
    control = SimpleNamespace(last_output_accel=-0.109)
    car_state = SimpleNamespace(vEgo=0.277, aEgo=-0.406)
    assert not LongControlSP.should_hold_stopping(control, car_state, -0.072)

  def test_sufficient_brake_holds_stopping(self):
    control = SimpleNamespace(last_output_accel=-0.543)
    car_state = SimpleNamespace(vEgo=0.209, aEgo=-0.534)
    assert LongControlSP.should_hold_stopping(control, car_state, -0.469)

  def test_stopping_decel_rate_is_smooth_while_rolling(self):
    assert LongControlSP.stopping_decel_rate(0.1) == 0.3

  def test_stopping_decel_rate_builds_holding_brake_at_stop(self):
    assert LongControlSP.stopping_decel_rate(0.0) == 2.0
