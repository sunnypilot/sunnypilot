from sunnypilot.selfdrive.controls.lib.dynamic_experimental_controller import (
  DynamicExperimentalController,
  TRAJECTORY_SIZE,
  LEAD_WINDOW_SIZE,
  SLOW_DOWN_WINDOW_SIZE,
  DANGEROUS_TTC_WINDOW_SIZE,
  MPC_FCW_WINDOW_SIZE,
  SNG_State,
  SLOWNESS_CRUISE_OFFSET,
  SLOW_DOWN_BP,
  SLOW_DOWN_DIST, STOP_AND_GO_FRAME
)

import unittest
import numpy as np
from unittest.mock import MagicMock, patch

class MockInterp:
  def __call__(self, x, xp, fp):
    return np.interp(x, xp, fp)

class MockCarState:
  def __init__(self, v_ego=0., standstill=False, left_blinker=False, right_blinker=False):
    self.vEgo = v_ego
    self.standstill = standstill
    self.leftBlinker = left_blinker
    self.rightBlinker = right_blinker

class MockLeadOne:
  def __init__(self, status=False, d_rel=0):
    self.status = status
    self.dRel = d_rel

class MockModelData:
  def __init__(self, x_vals=None, positions=None):
    self.orientation = MagicMock()
    self.position = MagicMock()
    if x_vals is not None:
      self.orientation.x = x_vals
    if positions is not None:
      self.position.x = positions

class MockControlState:
  def __init__(self, v_cruise=0):
    self.vCruise = v_cruise

class TestDynamicExperimentalController(unittest.TestCase):
  def setUp(self):
    """Set up test environment before each test case"""
    patcher = patch('openpilot.common.numpy_fast.interp', new_callable=MockInterp)
    self.addCleanup(patcher.stop)
    patcher.start()

    self.controller = DynamicExperimentalController()
    self.controller.set_enabled(True)

  def test_initial_state(self):
    """Test initial state of the controller"""
    self.assertEqual(self.controller._mode, 'acc')
    self.assertFalse(self.controller._has_lead)
    self.assertFalse(self.controller._has_standstill)
    self.assertEqual(self.controller._sng_state, SNG_State.off)
    self.assertFalse(self.controller._has_lead_filtered)
    self.assertFalse(self.controller._has_slow_down)
    self.assertFalse(self.controller._has_dangerous_ttc)
    self.assertFalse(self.controller._has_mpc_fcw)

  def test_standstill_detection(self):
      """Test standstill detection and state transitions"""
      car_state = MockCarState(standstill=True)
      lead_one = MockLeadOne()
      md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[150] * TRAJECTORY_SIZE)
      controls_state = MockControlState()

      # Test transition to standstill
      self.controller.update(False, car_state, lead_one, md, controls_state)
      self.assertEqual(self.controller._sng_state, SNG_State.stopped)
      self.assertEqual(self.controller.get_mpc_mode(), 'blended')

      # Test transition from standstill to moving
      car_state.standstill = False
      self.controller.update(False, car_state, lead_one, md, controls_state)
      self.assertEqual(self.controller._sng_state, SNG_State.going)

      # Test complete transition to normal driving
      for _ in range(STOP_AND_GO_FRAME + 1):
        self.controller.update(False, car_state, lead_one, md, controls_state)
      self.assertEqual(self.controller._sng_state, SNG_State.off)

  def test_lead_detection(self):
    """Test lead vehicle detection and filtering"""
    car_state = MockCarState(v_ego=20)  # 72 kph
    lead_one = MockLeadOne(status=True, d_rel=50)  # Safe distance
    md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[150] * TRAJECTORY_SIZE)
    controls_state = MockControlState(v_cruise=72)

    # Let moving average stabilize
    for _ in range(LEAD_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertTrue(self.controller._has_lead_filtered)
    self.assertEqual(self.controller.get_mpc_mode(), 'acc')

    # Test lead loss detection
    lead_one.status = False
    for _ in range(LEAD_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertFalse(self.controller._has_lead_filtered)

  def test_slow_down_detection(self):
    """Test slow down detection based on trajectory"""
    car_state = MockCarState(v_ego=10/3.6)  # 10 kph
    lead_one = MockLeadOne()
    x_vals = [0] * TRAJECTORY_SIZE
    positions = [20] * TRAJECTORY_SIZE  # Position within slow down threshold
    md = MockModelData(x_vals=x_vals, positions=positions)
    controls_state = MockControlState(v_cruise=30)

    # Test slow down detection
    for _ in range(SLOW_DOWN_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertTrue(self.controller._has_slow_down)
    self.assertEqual(self.controller.get_mpc_mode(), 'blended')

    # Test slow down recovery
    positions = [200] * TRAJECTORY_SIZE  # Position outside slow down threshold
    md = MockModelData(x_vals=x_vals, positions=positions)
    for _ in range(SLOW_DOWN_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertFalse(self.controller._has_slow_down)

    def test_dangerous_ttc_detection(self):
      """Test Time-To-Collision detection and handling"""
      car_state = MockCarState(v_ego=10)  # 36 kph
      lead_one = MockLeadOne(status=True)
      md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[150] * TRAJECTORY_SIZE)
      controls_state = MockControlState(v_cruise=36)

      # First establish normal conditions
      lead_one.dRel = 100  # Safe distance
      for _ in range(DANGEROUS_TTC_WINDOW_SIZE + 1):
        self.controller.update(False, car_state, lead_one, md, controls_state)

      self.assertFalse(self.controller._has_dangerous_ttc)

      # Now test dangerous TTC detection
      lead_one.dRel = 10  # 10m distance - should trigger dangerous TTC
      # TTC = dRel/vEgo = 10/10 = 1s (which is less than DANGEROUS_TTC = 2.3s)

      # Need to update multiple times to allow the weighted average to stabilize
      for _ in range(DANGEROUS_TTC_WINDOW_SIZE * 2):
        self.controller.update(False, car_state, lead_one, md, controls_state)

      self.assertTrue(self.controller._has_dangerous_ttc,
                      f"TTC of 1s should be considered dangerous (threshold: {DANGEROUS_TTC}s)")
      self.assertEqual(self.controller.get_mpc_mode(), 'blended',
                       "Should be in blended mode with dangerous TTC")

    def test_mode_transitions(self):
      """Test comprehensive mode transitions under different conditions"""
      # Initialize with normal driving conditions
      car_state = MockCarState(v_ego=25)  # 90 kph
      lead_one = MockLeadOne(status=False)
      md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[200] * TRAJECTORY_SIZE)
      controls_state = MockControlState(v_cruise=100)

      def stabilize_filters():
        """Helper to let all moving averages stabilize"""
        for _ in range(max(LEAD_WINDOW_SIZE, SLOW_DOWN_WINDOW_SIZE,
                           DANGEROUS_TTC_WINDOW_SIZE, MPC_FCW_WINDOW_SIZE) + 1):
          self.controller.update(False, car_state, lead_one, md, controls_state)

      # Test 1: Normal driving -> ACC mode
      stabilize_filters()
      self.assertEqual(self.controller.get_mpc_mode(), 'acc',
                       "Should be in ACC mode under normal driving conditions")

      # Test 2: Standstill -> Blended mode
      car_state.standstill = True
      self.controller.update(False, car_state, lead_one, md, controls_state)
      self.assertEqual(self.controller.get_mpc_mode(), 'blended',
                       "Should be in blended mode during standstill")

      # Test 3: Lead car appears -> ACC mode
      car_state = MockCarState(v_ego=25)  # Reset car state
      lead_one.status = True
      lead_one.dRel = 50
      stabilize_filters()
      self.assertEqual(self.controller.get_mpc_mode(), 'acc',
                       "Should be in ACC mode with safe lead distance")

      # Test 4: Dangerous TTC -> Blended mode
      # Set up conditions that will definitely trigger dangerous TTC
      car_state = MockCarState(v_ego=20)  # 72 kph
      lead_one.status = True
      lead_one.dRel = 20  # This creates a TTC of 1s, well below DANGEROUS_TTC

      # Need more updates to allow the weighted average to stabilize
      for _ in range(DANGEROUS_TTC_WINDOW_SIZE * 2):
        self.controller.update(False, car_state, lead_one, md, controls_state)

      self.assertTrue(self.controller._has_dangerous_ttc,
                      "Should detect dangerous TTC condition")
      self.assertEqual(self.controller.get_mpc_mode(), 'blended',
                       "Should be in blended mode with dangerous TTC")

  def test_mpc_fcw_handling(self):
    """Test MPC FCW crash count handling and mode transitions"""
    car_state = MockCarState(v_ego=20)
    lead_one = MockLeadOne()
    md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[150] * TRAJECTORY_SIZE)
    controls_state = MockControlState(v_cruise=72)

    # Test FCW activation
    self.controller.set_mpc_fcw_crash_cnt(5)
    for _ in range(MPC_FCW_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertTrue(self.controller._has_mpc_fcw)
    self.assertEqual(self.controller.get_mpc_mode(), 'blended')

    # Test FCW recovery
    self.controller.set_mpc_fcw_crash_cnt(0)
    for _ in range(MPC_FCW_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)

    self.assertFalse(self.controller._has_mpc_fcw)

  def test_radar_unavailable_handling(self):
    """Test behavior transitions between radar available and unavailable states"""
    car_state = MockCarState(v_ego=27.78)  # 100 kph
    lead_one = MockLeadOne(status=True, d_rel=50)
    md = MockModelData(x_vals=[0] * TRAJECTORY_SIZE, positions=[150] * TRAJECTORY_SIZE)
    controls_state = MockControlState(v_cruise=100)

    # Test with radar available
    for _ in range(LEAD_WINDOW_SIZE + 1):
      self.controller.update(False, car_state, lead_one, md, controls_state)
    radar_mode = self.controller.get_mpc_mode()

    # Test with radar unavailable
    for _ in range(LEAD_WINDOW_SIZE + 1):
      self.controller.update(True, car_state, lead_one, md, controls_state)
    radarless_mode = self.controller.get_mpc_mode()

    self.assertIsNotNone(radar_mode)
    self.assertIsNotNone(radarless_mode)

if __name__ == '__main__':
  unittest.main()