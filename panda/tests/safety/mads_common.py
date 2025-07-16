import unittest
from abc import abstractmethod


class MadsCommonBase(unittest.TestCase):
  @abstractmethod
  def _lkas_button_msg(self, enabled):
    raise NotImplementedError

  @abstractmethod
  def _acc_state_msg(self, enabled):
    raise NotImplementedError

  def _mads_states_cleanup(self):
    self.safety.set_mads_button_press(-1)
    self.safety.set_controls_allowed_lat(False)
    self.safety.set_controls_requested_lat(False)
    self.safety.set_acc_main_on(False)
    self.safety.set_mads_params(False, False)
    self.safety.set_heartbeat_engaged_mads(True)

  def test_enable_control_allowed_with_mads_button(self):
    """Toggle MADS with MADS button"""
    try:
      self._lkas_button_msg(False)
    except NotImplementedError:
      raise unittest.SkipTest("Skipping test because MADS button is not supported")

    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", mads_enabled=enable_mads):
          self._mads_states_cleanup()
          self.safety.set_mads_params(enable_mads, False)
          self.assertEqual(enable_mads, self.safety.get_enable_mads())

          self._rx(self._lkas_button_msg(True))
          self._rx(self._speed_msg(0))
          self._rx(self._lkas_button_msg(False))
          self._rx(self._speed_msg(0))
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_enable_control_allowed_with_manual_acc_main_on_state(self):
    try:
      self._acc_state_msg(False)
    except NotImplementedError:
      self._mads_states_cleanup()
      raise unittest.SkipTest("Skipping test because _acc_state_msg is not implemented for this car")

    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", mads_enabled=enable_mads):
          self._mads_states_cleanup()
          self.safety.set_mads_params(enable_mads, False)
          self._rx(self._acc_state_msg(True))
          self._rx(self._speed_msg(0))
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_enable_control_allowed_with_manual_mads_button_state(self):
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", mads_enabled=enable_mads):
          for mads_button_press in (-1, 0, 1):
            with self.subTest("mads_button_press", button_state=mads_button_press):
              self._mads_states_cleanup()
              self.safety.set_mads_params(enable_mads, False)

              self.safety.set_mads_button_press(mads_button_press)
              self._rx(self._speed_msg(0))
              self.assertEqual(enable_mads and mads_button_press == 1, self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_enable_control_allowed_from_acc_main_on(self):
    """Test that lateral controls are allowed when ACC main is enabled and disabled when ACC main is disabled"""
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", mads_enabled=enable_mads):
          for acc_main_on in (True, False):
            with self.subTest("initial_acc_main", initial_acc_main=acc_main_on):
              self._mads_states_cleanup()
              self.safety.set_mads_params(enable_mads, False)

              # Set initial state
              self.safety.set_acc_main_on(acc_main_on)
              self._rx(self._speed_msg(0))
              expected_lat = enable_mads and acc_main_on
              self.assertEqual(expected_lat, self.safety.get_controls_allowed_lat(),
                               f"Expected lat: [{expected_lat}] when acc_main_on goes to [{acc_main_on}]")

              # Test transition to opposite state
              self.safety.set_acc_main_on(not acc_main_on)
              self._rx(self._speed_msg(0))
              expected_lat = enable_mads and not acc_main_on
              self.assertEqual(expected_lat, self.safety.get_controls_allowed_lat(),
                               f"Expected lat: [{expected_lat}] when acc_main_on goes from [{acc_main_on}] to [{not acc_main_on}]")

              # Test transition back to initial state
              self.safety.set_acc_main_on(acc_main_on)
              self._rx(self._speed_msg(0))
              expected_lat = enable_mads and acc_main_on
              self.assertEqual(expected_lat, self.safety.get_controls_allowed_lat(),
                               f"Expected lat: [{expected_lat}] when acc_main_on goes from [{not acc_main_on}] to [{acc_main_on}]")
    finally:
      self._mads_states_cleanup()

  def test_mads_with_acc_main_on(self):
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", mads_enabled=enable_mads):
          self._mads_states_cleanup()
          self.safety.set_mads_params(enable_mads, False)

          self.safety.set_acc_main_on(True)
          self._rx(self._speed_msg(0))
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())

          self.safety.set_acc_main_on(False)
          self._rx(self._speed_msg(0))
          self.assertFalse(self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_disengage_lateral_on_brake_setup(self):
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", enable_mads=enable_mads):
          for disengage_on_brake in (True, False):
            with self.subTest("disengage on brake", disengage_on_brake=disengage_on_brake):
              self._mads_states_cleanup()
              self.safety.set_mads_params(enable_mads, disengage_on_brake)
              self.assertEqual(enable_mads and disengage_on_brake, self.safety.get_disengage_lateral_on_brake())
    finally:
      self._mads_states_cleanup()

  def test_disengage_lateral_on_brake(self):
    try:
      self._mads_states_cleanup()
      self.safety.set_mads_params(True, True)

      self._rx(self._user_brake_msg(False))
      self.safety.set_controls_requested_lat(True)
      self.safety.set_controls_allowed_lat(True)

      self._rx(self._user_brake_msg(True))
      # Test we pause lateral
      self.assertFalse(self.safety.get_controls_allowed_lat())
      # Make sure we can re-gain lateral actuation
      self._rx(self._user_brake_msg(False))
      self.assertTrue(self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_no_disengage_lateral_on_brake(self):
    try:
      self._mads_states_cleanup()
      self.safety.set_mads_params(True, False)

      self._rx(self._user_brake_msg(False))
      self.safety.set_controls_requested_lat(True)
      self.safety.set_controls_allowed_lat(True)

      self._rx(self._user_brake_msg(True))
      self.assertTrue(self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_engage_with_brake_pressed(self):
    try:
      self._lkas_button_msg(False)
    except NotImplementedError:
      raise unittest.SkipTest("Skipping test because MADS button is not supported")

    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", enable_mads=enable_mads):
          for disengage_lateral_on_brake in (True, False):
            with self.subTest("disengage_lateral_on_brake", disengage_lateral_on_brake=disengage_lateral_on_brake):
              with self.subTest("mads_button"):
                self._mads_states_cleanup()
                self.safety.set_mads_params(enable_mads, disengage_lateral_on_brake)

                # Brake press rising edge
                self._rx(self._user_brake_msg(True))
                self._rx(self._lkas_button_msg(True))
                self._rx(self._speed_msg(0))
                self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())

                # Continuous braking after the first frame of brake press rising edge
                self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())
                for _ in range(400):
                  self._rx(self._user_brake_msg(True))
                  self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())

              with self.subTest("acc_main_on"):
                self._mads_states_cleanup()
                self.safety.set_mads_params(enable_mads, disengage_lateral_on_brake)

                # Brake press rising edge
                self._rx(self._user_brake_msg(True))
                self.safety.set_acc_main_on(True)
                self._rx(self._speed_msg(0))
                self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())

                # Continuous braking after the first frame of brake press rising edge
                self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())
                for _ in range(400):
                  self._rx(self._user_brake_msg(True))
                  self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_disengage_lateral_on_brake_with_pressed_and_released(self):
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", enable_mads=enable_mads):
          for disengage_lateral_on_brake in (True, False):
            with self.subTest("disengage_lateral_on_brake", disengage_lateral_on_brake=disengage_lateral_on_brake):
              self._mads_states_cleanup()
              self.safety.set_mads_params(enable_mads, disengage_lateral_on_brake)

              # Set controls_allowed_lat rising edge
              self.safety.set_controls_requested_lat(True)
              self._rx(self._speed_msg(0))
              self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())

              # User brake press, validate controls_allowed_lat is false
              self._rx(self._user_brake_msg(True))
              self._rx(self._speed_msg(0))
              self.assertEqual(enable_mads and not disengage_lateral_on_brake, self.safety.get_controls_allowed_lat())

              # User brake release, validate controls_allowed_lat is true
              self._rx(self._user_brake_msg(False))
              self._rx(self._speed_msg(0))
              self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_disengage_lateral_on_brake_persistent_control_allowed_off(self):
    try:
      self._mads_states_cleanup()
      self.safety.set_mads_params(True, True)

      self.safety.set_controls_requested_lat(True)

      # Vehicle moving, validate controls_allowed_lat is true
      for _ in range(10):
        self._rx(self._speed_msg(10))
        self.assertTrue(self.safety.get_controls_allowed_lat())

      # User braked, vehicle slowed down in 10 frames, then stopped for 10 frames
      # Validate controls_allowed_lat is false
      self._rx(self._user_brake_msg(True))
      for _ in range(10):
        self._rx(self._speed_msg(5))
        self.assertFalse(self.safety.get_controls_allowed_lat())
      for _ in range(10):
        self._rx(self._speed_msg(0))
        self.assertFalse(self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_enable_lateral_control_with_controls_allowed_rising_edge(self):
    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", enable_mads=enable_mads):
          self._mads_states_cleanup()
          self.safety.set_mads_params(enable_mads, False)

          self.safety.set_controls_allowed(False)
          self._rx(self._speed_msg(0))
          self.safety.set_controls_allowed(True)
          self._rx(self._speed_msg(0))
          self.assertTrue(self.safety.get_controls_allowed())
    finally:
      self._mads_states_cleanup()

  def test_enable_control_allowed_with_mads_button_and_disable_with_main_cruise(self):
    """Tests main cruise and MADS button state transitions.

      Sequence:
      1. Main cruise off -> on
      2. MADS button engage
      3. Main cruise off

    """
    try:
      self._lkas_button_msg(False)
    except NotImplementedError:
      raise unittest.SkipTest("Skipping test because MADS button is not supported")

    try:
      self._acc_state_msg(False)
    except NotImplementedError:
      raise unittest.SkipTest("Skipping test because _acc_state_msg is not implemented for this car")

    try:
      for enable_mads in (True, False):
        with self.subTest("enable_mads", enable_mads=enable_mads):
          self._mads_states_cleanup()
          self.safety.set_mads_params(enable_mads, False)

          self._rx(self._lkas_button_msg(True))
          self._rx(self._speed_msg(0))
          self._rx(self._lkas_button_msg(False))
          self._rx(self._speed_msg(0))
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())

          self._rx(self._acc_state_msg(True))
          self._rx(self._speed_msg(0))
          self.assertEqual(enable_mads, self.safety.get_controls_allowed_lat())

          self._rx(self._acc_state_msg(False))
          self._rx(self._speed_msg(0))
          self.assertFalse(self.safety.get_controls_allowed_lat())
    finally:
      self._mads_states_cleanup()

  def test_brake_disengage_with_control_request(self):
    """Tests behavior when controls are requested while brake is engaged

    Sequence:
    1. Enable MADS with disengage on brake
    2. Brake to disengage lateral control
    3. Set control request while braking
    4. Release brake
    5. Verify controls become allowed
    """
    try:
      self._mads_states_cleanup()
      self.safety.set_mads_params(True, True)  # enable MADS with disengage on brake

      # Initial state
      self.safety.set_controls_allowed_lat(True)
      self._rx(self._speed_msg(0))
      self.assertTrue(self.safety.get_controls_allowed_lat())

      # Brake press disengages lateral
      self._rx(self._user_brake_msg(True))
      self.assertFalse(self.safety.get_controls_allowed_lat())

      # Request controls while braking
      self.safety.set_controls_requested_lat(True)
      self.assertFalse(self.safety.get_controls_allowed_lat())

      # Release brake - should enable since controls were requested
      self._rx(self._user_brake_msg(False))
      self._rx(self._speed_msg(0))
      self.assertTrue(self.safety.get_controls_allowed_lat())

    finally:
      self._mads_states_cleanup()

  def test_brake_disengage_with_acc_main_off(self):
    """Tests behavior when ACC main is turned off while brake is engaged

    Sequence:
    1. Enable MADS with disengage on brake
    2. Brake to disengage lateral control
    3. Turn ACC main off while braking
    4. Release brake
    5. Verify controls remain disengaged
    """
    try:
      self._mads_states_cleanup()
      self.safety.set_mads_params(True, True)  # enable MADS with disengage on brake

      # Initial state - enable with ACC main
      self.safety.set_acc_main_on(True)
      self._rx(self._speed_msg(0))
      self.assertTrue(self.safety.get_controls_allowed_lat())

      # Brake press disengages lateral
      self._rx(self._user_brake_msg(True))
      self.assertFalse(self.safety.get_controls_allowed_lat())

      # Turn ACC main off while braking
      self.safety.set_acc_main_on(False)
      self._rx(self._speed_msg(0))
      self.assertFalse(self.safety.get_controls_allowed_lat())

      # Release brake - should remain disabled since ACC main is off
      self._rx(self._user_brake_msg(False))
      self._rx(self._speed_msg(0))
      self.assertFalse(self.safety.get_controls_allowed_lat())

    finally:
      self._mads_states_cleanup()
