from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper, LaneChangeState, LaneChangeDirection
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeController, AutoLaneChangeState, \
  AUTO_LANE_CHANGE_TIMER, TIMER_DISABLED


class TestAutoLaneChangeController:
  def setup_method(self):
    self.DH = DesireHelper()
    self.alc = AutoLaneChangeController(self.DH)

  def test_reset(self):
    """Test that reset correctly sets timers back to default."""
    # Set some non-default values
    self.alc.lane_change_wait_timer = 2.0
    self.alc.prev_brake_pressed = True

    # Call reset
    self.alc.reset()

    # Check values were reset
    assert self.alc.lane_change_wait_timer == 0.0
    assert not self.alc.prev_brake_pressed

  def test_nudge_mode(self):
    """Test the default NUDGE mode behavior."""
    self.alc.reset()
    # Setup NUDGE mode
    self.alc.lane_change_bsm_delay = False  # BSM delay off
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGE

    # Update controller
    for _ in range(100):  # Run for 5 seconds
      self.alc.update(blindspot_detected=False, brake_pressed=False)

    # Check behavior for NUDGE mode
    assert self.alc.lane_change_delay == AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGE]
    # NUDGE mode should not allow lane change immediately
    assert not self.alc.auto_lane_change_allowed

  def test_nudgeless_mode(self):
    """Test the NUDGELESS mode behavior."""
    self.alc.reset()
    # Setup NUDGELESS mode
    self.alc.lane_change_bsm_delay = False  # BSM delay off
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS

    # Update controller once to read params
    self.alc.update(blindspot_detected=False, brake_pressed=False)

    # Check the delay is set correctly for NUDGELESS
    assert self.alc.lane_change_delay == AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGELESS]

    # Update multiple times to exceed the timer threshold
    for _ in range(1):  # Should exceed 0.1s with multiple DT_MDL updates
      self.alc.update(blindspot_detected=False, brake_pressed=False)

    # Now lane change should be allowed
    assert self.alc.lane_change_wait_timer > self.alc.lane_change_delay
    assert self.alc.auto_lane_change_allowed

  def test_timers(self):
    for (timer_state, timer_delay) in ((AutoLaneChangeState.HALF_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.HALF_SECOND]),
                                       (AutoLaneChangeState.ONE_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.ONE_SECOND]),
                                       (AutoLaneChangeState.TWO_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.TWO_SECONDS]),
                                       (AutoLaneChangeState.THREE_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.THREE_SECONDS])):
      self.alc.reset()
      self.alc.lane_change_bsm_delay = False  # BSM delay off
      self.alc.lane_change_set_timer = timer_state

      # Update controller once to read params
      self.alc.update(blindspot_detected=False, brake_pressed=False)

      # Check the delay is set correctly for TWO_SECONDS
      assert self.alc.lane_change_delay == timer_delay

      # The timer should still be below the threshold after one update
      assert self.alc.lane_change_wait_timer < self.alc.lane_change_delay
      assert not self.alc.auto_lane_change_allowed

      # Update enough times to exceed the threshold (seconds / DT_MDL)
      num_updates = int(timer_delay / DT_MDL) + 1  # Add one extra updates to ensure we exceed the threshold
      for _ in range(num_updates):
        self.alc.update(blindspot_detected=False, brake_pressed=False)

      # Now lane change should be allowed
      assert self.alc.lane_change_wait_timer > self.alc.lane_change_delay
      assert self.alc.auto_lane_change_allowed

  def test_brake_pressed_disables_auto_lane_change(self):
    """Test that pressing the brake disables auto lane change."""
    self.alc.reset()
    # Setup NUDGELESS mode (which normally allows auto lane change)
    self.alc.lane_change_bsm_delay = False
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS

    # Update with brake pressed for 1 second
    num_updates = int(1.0 / DT_MDL)
    for _ in range(num_updates):
      self.alc.update(blindspot_detected=False, brake_pressed=True)

    # Even though NUDGELESS mode, lane change should be disallowed due to brake pressed prior initiating lane change
    assert not self.alc.auto_lane_change_allowed

    # Check that prev_brake_pressed is saved
    assert self.alc.prev_brake_pressed

    # Even releasing brake shouldn't allow auto lane change
    num_updates = int(1.0 / DT_MDL)
    for _ in range(num_updates):
      self.alc.update(blindspot_detected=False, brake_pressed=False)

    assert not self.alc.auto_lane_change_allowed

  def test_blindspot_detected_with_bsm_delay(self):
    """Test behavior when blindspot is detected with BSM delay enabled."""
    self.alc.reset()
    # Setup NUDGELESS mode with BSM delay enabled
    self.alc.lane_change_bsm_delay = True  # BSM delay on
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS

    # Update with blindspot detected
    self.alc.update(blindspot_detected=True, brake_pressed=False)

    # For NUDGELESS with blindspot, timer should be disabled
    assert self.alc.lane_change_wait_timer == TIMER_DISABLED
    assert not self.alc.auto_lane_change_allowed

    # Test with TWO_SECONDS timer
    self.alc.lane_change_set_timer = AutoLaneChangeState.TWO_SECONDS
    self.alc.reset()  # Reset timer

    # Update with blindspot detected
    self.alc.update(blindspot_detected=True, brake_pressed=False)

    # For TWO_SECONDS with blindspot, timer should be set to delay-1
    assert self.alc.lane_change_wait_timer == 1.0  # 2.0 - 1
    assert not self.alc.auto_lane_change_allowed
