from parameterized import parameterized

from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper, LaneChangeState, LaneChangeDirection
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import (
  AutoLaneChangeController, AutoLaneChangeState, AUTO_LANE_CHANGE_TIMER, TIMER_DISABLED
)


class TestAutoLaneChangeController:
  def setup_method(self):
    self.DH = DesireHelper()
    self.alc = AutoLaneChangeController(self.DH)

  def _reset_states(self):
    self.lane_change_wait_timer = 0.0
    self.prev_brake_pressed = False
    self.prev_lane_change = False

  def test_reset(self):
    """Test that reset correctly sets timers back to default."""
    # Set some non-default values
    self.alc.lane_change_wait_timer = 2.0
    self.alc.prev_brake_pressed = True

    # Set the DesireHelper to trigger a reset
    self.DH.lane_change_state = LaneChangeState.off
    self.DH.lane_change_direction = LaneChangeDirection.none

    # Call reset
    self.alc.reset()

    # Check values were reset
    assert self.alc.lane_change_wait_timer == 0.0
    assert not self.alc.prev_brake_pressed

  @parameterized.expand([
    (AutoLaneChangeState.OFF, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.OFF]),
    (AutoLaneChangeState.NUDGE, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGE]),
  ])
  def test_off_and_nudge_mode(self, timer_state, timer_delay):
    """Test the default OFF and NUDGE mode behavior."""
    self._reset_states()
    # Setup NUDGE mode
    self.alc.lane_change_bsm_delay = False  # BSM delay off
    self.alc.lane_change_set_timer = timer_state

    # Update controller
    num_updates = int(5.0 / DT_MDL)
    for _ in range(num_updates):  # Run for 5 seconds
      self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

    # Check behavior for mode
    assert self.alc.lane_change_delay == timer_delay

    # Mode should not allow lane change immediately
    assert not self.alc.auto_lane_change_allowed

  def test_nudgeless_mode(self):
    """Test the NUDGELESS mode behavior."""
    self._reset_states()
    # Setup NUDGELESS mode
    self.alc.lane_change_bsm_delay = False  # BSM delay off
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS

    # Update controller once to read params
    self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

    # Check the delay is set correctly for NUDGELESS
    assert self.alc.lane_change_delay == AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGELESS]

    # Update multiple times to exceed the timer threshold
    for _ in range(1):  # Should exceed 0.1s with multiple DT_MDL updates
      self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

    # Now lane change should be allowed
    assert self.alc.lane_change_wait_timer > self.alc.lane_change_delay
    assert self.alc.auto_lane_change_allowed

  @parameterized.expand([
    (AutoLaneChangeState.HALF_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.HALF_SECOND]),
    (AutoLaneChangeState.ONE_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.ONE_SECOND]),
    (AutoLaneChangeState.TWO_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.TWO_SECONDS]),
    (AutoLaneChangeState.THREE_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.THREE_SECONDS])
  ])
  def test_timers(self, timer_state, timer_delay):
      self._reset_states()
      self.alc.lane_change_bsm_delay = False  # BSM delay off
      self.alc.lane_change_set_timer = timer_state

      # Update controller once
      self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

      # Check the delay is set correctly
      assert self.alc.lane_change_delay == timer_delay

      # The timer should still be below the threshold after one update
      assert self.alc.lane_change_wait_timer < self.alc.lane_change_delay
      assert not self.alc.auto_lane_change_allowed

      # Update enough times to exceed the threshold (seconds / DT_MDL)
      num_updates = int(timer_delay / DT_MDL) + 1  # Add one extra updates to ensure we exceed the threshold
      for _ in range(num_updates):
        self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

      # Now lane change should be allowed
      assert self.alc.lane_change_wait_timer > self.alc.lane_change_delay
      assert self.alc.auto_lane_change_allowed

  def test_brake_pressed_disables_auto_lane_change(self):
    """Test that pressing the brake disables auto lane change."""
    self._reset_states()
    # Setup NUDGELESS mode (which normally allows auto lane change)
    self.alc.lane_change_bsm_delay = False
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS
    num_updates = int(1.0 / DT_MDL)

    # Update with brake pressed for 1 second
    for _ in range(num_updates):
      self.alc.update_lane_change(blindspot_detected=False, brake_pressed=True)

    # Even though NUDGELESS mode, lane change should be disallowed due to brake pressed prior initiating lane change
    assert not self.alc.auto_lane_change_allowed

    # Check that prev_brake_pressed is saved
    assert self.alc.prev_brake_pressed

    # Even releasing brake shouldn't allow auto lane change
    for _ in range(num_updates):
      self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

    assert not self.alc.auto_lane_change_allowed

  def test_blindspot_detected_with_bsm_delay(self):
    """Test behavior when blindspot is detected with BSM delay enabled."""
    self._reset_states()
    # Setup NUDGELESS mode with BSM delay enabled
    self.alc.lane_change_bsm_delay = True  # BSM delay on
    self.alc.lane_change_set_timer = AutoLaneChangeState.NUDGELESS

    # Update with blindspot detected
    self.alc.update_lane_change(blindspot_detected=True, brake_pressed=False)

    # For NUDGELESS with blindspot, timer should be disabled
    assert self.alc.lane_change_wait_timer == TIMER_DISABLED
    assert not self.alc.auto_lane_change_allowed

    # Test with TWO_SECONDS timer
    self._reset_states()
    self.alc.lane_change_set_timer = AutoLaneChangeState.TWO_SECONDS

    # Update with blindspot detected
    self.alc.update_lane_change(blindspot_detected=True, brake_pressed=False)

    # For TWO_SECONDS with blindspot, timer should be set to delay-1
    assert self.alc.lane_change_wait_timer == 1.0  # 2.0 - 1
    assert not self.alc.auto_lane_change_allowed

  @parameterized.expand([
    (AutoLaneChangeState.NUDGELESS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGELESS]),
    (AutoLaneChangeState.HALF_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.HALF_SECOND]),
    (AutoLaneChangeState.ONE_SECOND, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.ONE_SECOND]),
    (AutoLaneChangeState.TWO_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.TWO_SECONDS]),
    (AutoLaneChangeState.THREE_SECONDS, AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.THREE_SECONDS])
  ])
  def test_disallow_continuous_auto_lane_change(self, timer_state, timer_delay):
      self._reset_states()
      self.alc.lane_change_bsm_delay = False  # BSM delay off
      self.alc.lane_change_set_timer = timer_state
      num_updates = int(timer_delay / DT_MDL) + 1  # Add one extra updates to ensure we exceed the threshold

      # Update enough times to exceed the threshold (seconds / DT_MDL)
      for _ in range(num_updates):
        self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

      # Now lane change should be allowed
      assert self.alc.lane_change_wait_timer > self.alc.lane_change_delay
      assert self.alc.auto_lane_change_allowed

      # Simulate lane change is initiated
      self.DH.lane_change_state = LaneChangeState.laneChangeStarting
      self.alc.update_state()

      # Simulate lane change is completed, and one_blinker stays on
      self.DH.lane_change_state = LaneChangeState.preLaneChange
      self.alc.update_state()

      # Update enough times to exceed the threshold (seconds / DT_MDL)
      for _ in range(num_updates):
        self.alc.update_lane_change(blindspot_detected=False, brake_pressed=False)

      assert not self.alc.auto_lane_change_allowed
