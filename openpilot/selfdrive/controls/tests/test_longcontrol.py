from opendbc.car.structs import car
from openpilot.common.realtime import DT_CTRL
from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState, long_control_state_trans


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
  ACCEL_LIMITS = (-2.0, 2.0)

  def make_control(self):
    CP = car.CarParams.new_message()
    CP.stopAccel = -2.0
    CP.longitudinalTuning.kiBP = [0.0]
    CP.longitudinalTuning.kiV = [0.0]
    CP_SP = custom.CarParamsSP.new_message()
    return LongControl(CP, CP_SP)

  def make_cs(self, v_ego, a_ego, standstill=False, cruise_standstill=None):
    CS = car.CarState.new_message()
    CS.vEgo = float(v_ego)
    CS.aEgo = float(a_ego)
    CS.standstill = standstill
    CS.brakePressed = False
    CS.cruiseState.standstill = standstill if cruise_standstill is None else cruise_standstill
    return CS

  def enter_stopping(self, loc, v_ego=0.23, a_ego=-0.55):
    # Run in pid first so last_output_accel is a realistic decel, then enter stopping.
    out = 0.0
    for _ in range(100):
      out = loc.update(True, self.make_cs(2.0, a_ego), a_ego, False, self.ACCEL_LIMITS)
    assert loc.long_control_state == LongCtrlState.pid
    out = loc.update(True, self.make_cs(v_ego, a_ego), a_ego, True, self.ACCEL_LIMITS)
    assert loc.long_control_state == LongCtrlState.stopping
    return out

  def test_entry_is_continuous(self):
    loc = self.make_control()
    out = self.enter_stopping(loc)
    assert abs(out - loc.last_output_accel) < 1e-9
    assert abs(out - (-0.55)) < 0.02

  def test_positive_entry_ramps_down(self):
    loc = self.make_control()
    loc.last_output_accel = 0.3
    loc.stopping_jerk = 0.66
    out = loc._stopping_accel(0.23, False)
    assert abs(out - (0.3 - 0.66 * DT_CTRL)) < 1e-6  # no jump to zero

  def test_taper_never_steps(self):
    loc = self.make_control()
    v_ego = 0.23
    out = self.enter_stopping(loc)
    prev = out
    max_step = 0.0
    for _ in range(400):
      out = loc.update(True, self.make_cs(v_ego, out), -0.55, True, self.ACCEL_LIMITS)
      max_step = max(max_step, abs(out - prev))
      prev = out
      v_ego = max(0.0, v_ego + out * DT_CTRL)

    # bounded by the release jerk (and the 1.0 m/s^3 hold ramp), never a step to stopAccel
    assert max_step <= 1.0 * DT_CTRL + 1e-6
    assert -2.01 < out < -1.9

  def test_taper_releases_before_standstill(self):
    loc = self.make_control()
    v_ego = 0.23
    out = self.enter_stopping(loc)
    while v_ego > 0.11:
      out = loc.update(True, self.make_cs(v_ego, out), -0.55, True, self.ACCEL_LIMITS)
      v_ego = max(0.0, v_ego + out * DT_CTRL)
    assert out > -0.5  # noticeably released before the hold takes over

  def test_hot_entry_still_bounded(self):
    loc = self.make_control()
    out = self.enter_stopping(loc, v_ego=0.25, a_ego=-1.2)
    prev = out
    assert abs(out - (-1.2)) < 0.021
    for _ in range(30):
      out = loc.update(True, self.make_cs(0.25, out), -1.2, True, self.ACCEL_LIMITS)
      assert abs(out - prev) <= 2.0 * DT_CTRL + 1e-6
      prev = out

  def test_hold_ramps_instead_of_stepping(self):
    loc = self.make_control()
    loc.last_output_accel = -0.3
    out = loc._stopping_accel(0.0, True)
    assert out > -0.32  # first hold frame is a ramp, not stopAccel
    for _ in range(300):
      prev = out
      loc.last_output_accel = out
      out = loc._stopping_accel(0.0, True)
      assert abs(out - prev) <= 1.0 * DT_CTRL + 1e-6
    assert -2.01 < out < -1.9

  def test_should_stop_debounce(self):
    loc = self.make_control()
    self.enter_stopping(loc)
    # settle at standstill
    out = -0.55
    for _ in range(300):
      out = loc.update(True, self.make_cs(0.0, 0.0, standstill=True), 0.2, True, self.ACCEL_LIMITS)
    assert out < -1.9
    # one dropped should_stop frame must not release the brake. cruiseState.standstill is
    # false here, matching the observed standstill where should_stop briefly drops.
    out = loc.update(True, self.make_cs(0.0, 0.0, standstill=True, cruise_standstill=False), 0.2, False, self.ACCEL_LIMITS)
    assert loc.long_control_state == LongCtrlState.stopping
    assert out < -1.9
    # and it must eventually exit when the request to move persists
    for _ in range(20):
      out = loc.update(True, self.make_cs(0.0, 0.0, standstill=True, cruise_standstill=False), 0.2, False, self.ACCEL_LIMITS)
    assert loc.long_control_state == LongCtrlState.pid
