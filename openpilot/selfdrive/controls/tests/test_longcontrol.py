from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.drive_helpers import STOPPING_SPEED, should_stop
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState, long_control_state_trans
from openpilot.sunnypilot.selfdrive.controls.lib.stopping_controller import StoppingController


def update_long_control(LoC, StopC, active, CS, a_target, should_stop, accel_limits, has_lead=False):
  prev_state = LoC.long_control_state
  prev_accel = LoC.last_output_accel
  stock_accel = LoC.update(active, CS, a_target, should_stop, accel_limits)
  stock_state = LoC.long_control_state
  state, accel = StopC.update(prev_state, stock_state, CS, a_target, prev_accel, stock_accel,
                              accel_limits, has_lead)
  if state != stock_state:
    LoC.reset()
  LoC.long_control_state = state
  LoC.last_output_accel = accel
  return accel


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

class TestStoppingController(OpenpilotTestCase):
  def test_stock_long_control_remains_available(self):
    from opendbc.car.structs import car
    CP = car.CarParams.new_message()
    CP_SP = custom.CarParamsSP.new_message()
    stock = LongControl(CP, CP_SP)
    tuned = StoppingController(CP.stopAccel)
    assert type(stock) is LongControl
    assert not isinstance(tuned, LongControl)

  def test_stopping_tune_is_gentler_than_upstream_default(self):
    # Upstream #38394 hardcoded a 1.0 m/s^2/s ramp and a 0.3 m/s latch. comma's own one-stopping-tune uses
    # 0.3 / 0.25, and every stop recorded on this car was driven with that pair. Both must stay on the less
    # braking side, or a future edit re-deepens the terminal brake unnoticed - which already happened once.
    assert 0.0 < StoppingController.STOPPING_DECEL_RATE <= 1.0
    assert 0.0 < STOPPING_SPEED <= 0.3
    assert should_stop(STOPPING_SPEED - 0.01, 0.0)
    assert not should_stop(0.29, 0.0)  # the band upstream would latch in and we do not

  def test_standstill_hold_firms_faster_than_the_stopping_ramp(self):
    # The faster standstill ramp builds the hold without changing the approach-to-stop ramp.
    assert StoppingController.STANDSTILL_HOLD_RATE >= StoppingController.STOPPING_DECEL_RATE
    assert 0.5 <= StoppingController.STANDSTILL_HOLD_RATE <= 2.0

  def test_standstill_hold_waits_after_the_standstill_flag(self):
    """The request is frozen through the stop and for the configured delay after standstill."""
    from opendbc.car.structs import car
    from openpilot.common.realtime import DT_CTRL
    hold_delays = ((True, StoppingController.STANDSTILL_HOLD_DELAY_LEAD),
                   (False, StoppingController.STANDSTILL_HOLD_DELAY_NO_LEAD))
    for has_lead, delay in hold_delays:
      with self.subTest(has_lead=has_lead):
        CP = car.CarParams.new_message(stopAccel=-1.0)
        CP_SP = custom.CarParamsSP.new_message()
        LoC = LongControl(CP, CP_SP)
        StopC = StoppingController(CP.stopAccel)
        moving = car.CarState.new_message(vEgo=0.2, standstill=False)
        still = car.CarState.new_message(vEgo=0.0, standstill=True)
        LoC.long_control_state = LongCtrlState.stopping
        LoC.last_output_accel = -0.3
        # 0.5 s of stopping state before the wheels read zero: nothing changes
        for _ in range(int(0.5 / DT_CTRL)):
          a = float(update_long_control(LoC, StopC, True, moving, 0.0, True, (-3.5, 1.5), has_lead=has_lead))
        assert a == -0.3
        a = [-0.3]
        for _ in range(int(2.5 / DT_CTRL)):
          a.append(float(update_long_control(LoC, StopC, True, still, 0.0, True, (-3.5, 1.5), has_lead=has_lead)))
        n_delay = int(delay / DT_CTRL)
        assert a[n_delay - 1] == -0.3                              # still frozen at the end of the wait
        assert a[n_delay + 5] < -0.3                               # and falling right after it
        late = (a[n_delay] - a[n_delay + 50]) / (50 * DT_CTRL)
        assert abs(late - StoppingController.STANDSTILL_HOLD_RATE) < 0.05, late  # fast once the delay has passed
    assert StoppingController.STANDSTILL_HOLD_DELAY_NO_LEAD > StoppingController.STANDSTILL_HOLD_DELAY_LEAD

  def test_stopping_ramp_resumes_if_the_car_never_stops(self):
    from opendbc.car.structs import car
    from openpilot.common.realtime import DT_CTRL
    CP = car.CarParams.new_message(stopAccel=-1.0)
    LoC = LongControl(CP, custom.CarParamsSP.new_message())
    StopC = StoppingController(CP.stopAccel)
    LoC.long_control_state = LongCtrlState.stopping
    LoC.last_output_accel = -0.1
    creeping = car.CarState.new_message(vEgo=0.15, standstill=False)
    for _ in range(int(StoppingController.STOPPING_FREEZE_MAX / DT_CTRL) - 1):
      a = float(update_long_control(LoC, StopC, True, creeping, 0.0, True, (-3.5, 1.5)))
    assert a == -0.1                                           # frozen for the whole grace period
    for _ in range(int(1.0 / DT_CTRL)):
      a = float(update_long_control(LoC, StopC, True, creeping, 0.0, True, (-3.5, 1.5)))
    assert abs((-0.1 - a) - StoppingController.STOPPING_DECEL_RATE) < 0.02  # then the upstream ramp

  def test_standstill_hold_timer_resets_when_the_car_moves(self):
    from opendbc.car.structs import car
    CP = car.CarParams.new_message(stopAccel=-1.0)
    LoC = LongControl(CP, custom.CarParamsSP.new_message())
    StopC = StoppingController(CP.stopAccel)
    LoC.long_control_state = LongCtrlState.stopping
    LoC.last_output_accel = -0.3
    still = car.CarState.new_message(standstill=True)
    moving = car.CarState.new_message(standstill=False, vEgo=0.1)
    for _ in range(40):
      update_long_control(LoC, StopC, True, still, 0.0, True, (-3.5, 1.5))
    update_long_control(LoC, StopC, True, moving, 0.0, True, (-3.5, 1.5))
    assert StopC.standstill_t == 0.0

  def test_one_frame_go_does_not_release_the_hold_at_standstill(self):
    from opendbc.car.structs import car
    from openpilot.common.realtime import DT_CTRL
    CP = car.CarParams.new_message(stopAccel=-1.0)
    CP.longitudinalTuning.kiBP = [0.0]
    CP.longitudinalTuning.kiV = [0.0]
    LoC = LongControl(CP, custom.CarParamsSP.new_message())
    StopC = StoppingController(CP.stopAccel)
    still = car.CarState.new_message(vEgo=0.0, standstill=True)
    LoC.long_control_state = LongCtrlState.stopping
    LoC.last_output_accel = -1.0
    for _ in range(200):
      update_long_control(LoC, StopC, True, still, 0.0, True, (-3.5, 1.5), has_lead=True)
    a = float(update_long_control(LoC, StopC, True, still, 1.2, False, (-3.5, 1.5), has_lead=True))   # one frame of "go"
    assert LoC.long_control_state == LongCtrlState.stopping and a <= -0.99, (LoC.long_control_state, a)
    for _ in range(5):
      a = float(update_long_control(LoC, StopC, True, still, 0.0, True, (-3.5, 1.5), has_lead=True))  # stop again
    assert a <= -0.99
    # a sustained go leaves the hold after the debounce
    n = 0
    while LoC.long_control_state == LongCtrlState.stopping and n < 100:
      update_long_control(LoC, StopC, True, still, 1.2, False, (-3.5, 1.5), has_lead=True); n += 1
    assert abs(n * DT_CTRL - StoppingController.STOPPING_EXIT_DEBOUNCE) < 0.03, n

  def test_request_keeps_easing_with_the_plan_before_the_wheels_stop(self):
    from opendbc.car.structs import car
    CP = car.CarParams.new_message(stopAccel=-1.0)
    LoC = LongControl(CP, custom.CarParamsSP.new_message())
    StopC = StoppingController(CP.stopAccel)
    LoC.long_control_state = LongCtrlState.stopping
    LoC.last_output_accel = -0.40
    rolling = car.CarState.new_message(vEgo=0.2, standstill=False)
    for _ in range(30):
      a = float(update_long_control(LoC, StopC, True, rolling, -0.20, True, (-3.5, 1.5), has_lead=True))   # plan eases to -0.20
    assert abs(a + 0.20) < 1e-6, a                                                   # followed (lighter)
    a = float(update_long_control(LoC, StopC, True, rolling, -0.60, True, (-3.5, 1.5), has_lead=True))     # plan firmer: not followed
    assert abs(a + 0.20) < 1e-6, a
    for _ in range(10):
      a = float(update_long_control(LoC, StopC, True, rolling, 0.0, True, (-3.5, 1.5), has_lead=True))     # plan at 0 (flicker): not followed
    assert abs(a + 0.20) < 1e-6, a
    assert StoppingController.STOPPING_FOLLOW_MIN < 0.0

  def test_creep_after_the_stop_adds_brake_gently_then_more(self):
    from opendbc.car.structs import car
    from openpilot.common.realtime import DT_CTRL
    CP = car.CarParams.new_message(stopAccel=-1.0)
    LoC = LongControl(CP, custom.CarParamsSP.new_message())
    StopC = StoppingController(CP.stopAccel)
    LoC.long_control_state = LongCtrlState.stopping
    LoC.last_output_accel = -0.20
    still = car.CarState.new_message(vEgo=0.0, standstill=True)
    creep = car.CarState.new_message(vEgo=0.08, standstill=False)
    for _ in range(10):
      a = float(update_long_control(LoC, StopC, True, still, -0.1, True, (-3.5, 1.5), has_lead=True))
    assert abs(a + 0.20) < 1e-6, a
    a0 = a
    for _ in range(int(0.25 / DT_CTRL)):
      a = float(update_long_control(LoC, StopC, True, creep, -0.1, True, (-3.5, 1.5), has_lead=True))
    first = a0 - a
    assert 0.0 < first < 0.2, first
    for _ in range(int(0.25 / DT_CTRL)):
      a2 = float(update_long_control(LoC, StopC, True, creep, -0.1, True, (-3.5, 1.5), has_lead=True))
    second = a - a2
    assert second > first * 1.5, (first, second)
    for _ in range(5):
      a3 = float(update_long_control(LoC, StopC, True, still, -0.1, True, (-3.5, 1.5), has_lead=True))
    assert abs(a3 - a2) < 1e-6
    assert StoppingController.CREEP_RATE_GROWTH > 0.0
