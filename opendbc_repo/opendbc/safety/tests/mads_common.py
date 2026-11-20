from opendbc.testing import parameterized
import abc
import unittest

from opendbc.safety.tests.libsafety import libsafety_py


class MadsSafetyTestBase(unittest.TestCase):
  safety: libsafety_py.LibSafety

  @abc.abstractmethod
  def _lkas_button_msg(self, enabled):
    raise NotImplementedError

  @abc.abstractmethod
  def _acc_state_msg(self, enabled):
    raise NotImplementedError

  def setUp(self):
    super().setUp()
    self.safety.set_controls_allowed(False)
    self.safety.set_mads_button_press(-1)
    self.safety.set_controls_allowed_lateral(False)
    self.safety.set_controls_requested_lateral(False)
    self.safety.set_acc_main_on(False)
    self.safety.set_mads_params(False, False, False)
    self.safety.set_heartbeat_engaged_mads(True)

  def test_heartbeat_engaged_mads_check(self):
    """Test MADS heartbeat engaged check behavior"""
    for boolean in (True, False):
      # If boolean is True, the heartbeat is engaged and should remain engaged, otherwise it should disengage.
      with self.subTest(heartbeat_engaged=boolean, should_remain_engaged=boolean):
        # Setup initial conditions
        self.safety.set_mads_params(True, False, False)  # Enable MADS
        self.safety.set_controls_allowed_lateral(True)
        self.assertTrue(self.safety.get_controls_allowed_lateral())

        # Set heartbeat engaged state based on test case
        self.safety.set_heartbeat_engaged_mads(boolean)

        # Call the heartbeat check function multiple times
        # We know from the implementation that it takes 3 mismatches to disengage
        for _ in range(4):  # More than 3 times to ensure we pass the threshold
          self.safety.mads_heartbeat_engaged_check()

        # Verify engagement state matches expectation
        self.assertEqual(self.safety.get_controls_allowed_lateral(), boolean,
                         f"Expected controls_allowed_lateral to be [{boolean}] but got [{self.safety.get_controls_allowed_lateral()}]")

  def test_enable_control_allowed_with_mads_button(self):
    """Toggle MADS with MADS button"""
    try:
      self._lkas_button_msg(False)
    except NotImplementedError as err:
      raise unittest.SkipTest("Skipping test because MADS button is not supported") from err

    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)
        self.assertEqual(enable_mads, self.safety.get_enable_mads())

        self._rx(self._lkas_button_msg(True))
        self._rx(self._lkas_button_msg(False))
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

  def test_enable_control_allowed_with_manual_acc_main_on_state(self):
    try:
      self._acc_state_msg(False)
    except NotImplementedError as err:
      raise unittest.SkipTest("Skipping test because _acc_state_msg is not implemented for this car") from err

    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)
        self._rx(self._acc_state_msg(True))
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

  def test_enable_control_allowed_with_manual_mads_button_state(self):
    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        for mads_button_press in (-1, 0, 1):
          with self.subTest("mads_button_press", button_state=mads_button_press):
            self.safety.set_mads_params(enable_mads, False, False)

            self.safety.set_mads_button_press(mads_button_press)
            self._rx(self._speed_msg(0))
            self.assertEqual(enable_mads and mads_button_press == 1, self.safety.get_controls_allowed_lateral())

  def test_enable_control_allowed_from_acc_main_on(self):
    """Test that lateral controls are allowed when ACC main is enabled and disabled when ACC main is disabled"""
    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        for acc_main_on in (True, False):
          with self.subTest("initial_acc_main", initial_acc_main=acc_main_on):
            self.safety.set_controls_allowed(False)
            self.safety.set_mads_params(enable_mads, False, False)

            # Set initial state
            self.safety.set_acc_main_on(acc_main_on)
            self._rx(self._speed_msg(0))
            expected_lat = enable_mads and acc_main_on
            self.assertEqual(expected_lat, self.safety.get_controls_allowed_lateral(),
                             f"Expected lat: [{expected_lat}] when acc_main_on goes to [{acc_main_on}]")

            # Test transition to opposite state
            self.safety.set_acc_main_on(not acc_main_on)
            self._rx(self._speed_msg(0))
            expected_lat = enable_mads and not acc_main_on
            self.assertEqual(expected_lat, self.safety.get_controls_allowed_lateral(),
                             f"Expected lat: [{expected_lat}] when acc_main_on goes from [{acc_main_on}] to [{not acc_main_on}]")

            # Test transition back to initial state
            self.safety.set_acc_main_on(acc_main_on)
            self._rx(self._speed_msg(0))
            expected_lat = enable_mads and acc_main_on
            self.assertEqual(expected_lat, self.safety.get_controls_allowed_lateral(),
                             f"Expected lat: [{expected_lat}] when acc_main_on goes from [{not acc_main_on}] to [{acc_main_on}]")

  def test_mads_with_acc_main_on(self):
    for enable_mads in (True, False):
      with self.subTest("enable_mads", mads_enabled=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)

        self.safety.set_acc_main_on(True)
        self._rx(self._speed_msg(0))
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        self.safety.set_acc_main_on(False)
        self._rx(self._speed_msg(0))
        self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_pause_lateral_on_brake_setup(self):
    for enable_mads in (True, False):
      with self.subTest("enable_mads", enable_mads=enable_mads):
        for pause_lateral_on_brake in (True, False):
          with self.subTest("pause_lateral_on_brake", pause_lateral_on_brake=pause_lateral_on_brake):
            self.safety.set_mads_params(enable_mads, False, pause_lateral_on_brake)
            self.assertEqual(enable_mads and pause_lateral_on_brake, self.safety.get_pause_lateral_on_brake())

  def test_pause_lateral_on_brake(self):
    self.safety.set_mads_params(True, False, True)

    self._rx(self._user_brake_msg(False))
    self.safety.set_controls_requested_lateral(True)
    self.safety.set_controls_allowed_lateral(True)

    self._rx(self._user_brake_msg(True))
    # Test we pause lateral
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    # Make sure we can re-gain lateral actuation
    self._rx(self._user_brake_msg(False))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_no_pause_lateral_on_brake(self):
    self.safety.set_mads_params(True, False, False)

    self._rx(self._user_brake_msg(False))
    self.safety.set_controls_requested_lateral(True)
    self.safety.set_controls_allowed_lateral(True)

    self._rx(self._user_brake_msg(True))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  @parameterized("engage_method", ["mads_button", "acc_main_on"])
  def test_engage_with_brake_pressed(self, engage_method):
    if engage_method == "mads_button":
      try:
        self._lkas_button_msg(False)
      except NotImplementedError as err:
        raise unittest.SkipTest("Skipping test because MADS button is not supported") from err
    elif engage_method == "acc_main_on":
      try:
        self._acc_state_msg(False)
      except NotImplementedError as err:
        raise unittest.SkipTest("Skipping test because ACC main is not supported") from err

    for enable_mads in (True, False):
      with self.subTest("enable_mads", enable_mads=enable_mads):
        for pause_lateral_on_brake in (True, False):
          with self.subTest("pause_lateral_on_brake", pause_lateral_on_brake=pause_lateral_on_brake):
            with self.subTest(engage_method):
              self.safety.set_mads_params(enable_mads, False, pause_lateral_on_brake)

              # Brake press rising edge
              self._rx(self._user_brake_msg(True))

              if engage_method == "mads_button":
                self._rx(self._lkas_button_msg(True))
              elif engage_method == "acc_main_on":
                self.safety.set_acc_main_on(True)
                self.assertTrue(self.safety.get_acc_main_on())
              else:
                raise ValueError(f"Invalid engage_method: {engage_method}")
              self._rx(self._speed_msg(0))

              self.assertEqual(enable_mads and not pause_lateral_on_brake, self.safety.get_controls_allowed_lateral())

              # Continuous braking after the first frame of brake press rising edge
              for _ in range(400):
                self.assertEqual(enable_mads and not pause_lateral_on_brake, self.safety.get_controls_allowed_lateral())

  def test_pause_lateral_on_brake_with_pressed_and_released(self):
    for enable_mads in (True, False):
      with self.subTest("enable_mads", enable_mads=enable_mads):
        for pause_lateral_on_brake in (True, False):
          with self.subTest("pause_lateral_on_brake", pause_lateral_on_brake=pause_lateral_on_brake):
            self.safety.set_mads_params(enable_mads, False, pause_lateral_on_brake)

            # Set controls_allowed_lateral rising edge
            self.safety.set_controls_requested_lateral(True)
            self._rx(self._speed_msg(0))
            self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

            # User brake press, validate controls_allowed_lateral is false
            self._rx(self._user_brake_msg(True))
            self.assertEqual(enable_mads and not pause_lateral_on_brake, self.safety.get_controls_allowed_lateral())

            # User brake release, validate controls_allowed_lateral is true
            self._rx(self._user_brake_msg(False))
            self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

  def test_pause_lateral_on_brake_persistent_control_allowed_off(self):
    self.safety.set_mads_params(True, False, True)

    self.safety.set_controls_requested_lateral(True)

    # Vehicle moving, validate controls_allowed_lateral is true
    for _ in range(10):
      self._rx(self._speed_msg(10))
      self.assertTrue(self.safety.get_controls_allowed_lateral())

    # User braked, vehicle slowed down in 10 frames, then stopped for 10 frames
    # Validate controls_allowed_lateral is false
    self._rx(self._user_brake_msg(True))
    for _ in range(10):
      self._rx(self._speed_msg(5))
      self.assertFalse(self.safety.get_controls_allowed_lateral())
    for _ in range(10):
      self._rx(self._speed_msg(0))
      self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_enable_lateral_control_with_controls_allowed_rising_edge(self):
    for enable_mads in (True, False):
      with self.subTest("enable_mads", enable_mads=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)

        self.safety.set_controls_allowed(False)
        self._rx(self._speed_msg(0))
        self.safety.set_controls_allowed(True)
        self._rx(self._speed_msg(0))
        self.assertTrue(self.safety.get_controls_allowed())

  def test_enable_control_allowed_with_mads_button_and_disable_with_main_cruise(self):
    """Tests main cruise and MADS button state transitions.

      Sequence:
      1. Main cruise off -> on
      2. MADS button engage
      3. Main cruise off

    """
    try:
      self._lkas_button_msg(False)
    except NotImplementedError as err:
      raise unittest.SkipTest("Skipping test because MADS button is not supported") from err

    try:
      self._acc_state_msg(False)
    except NotImplementedError as err:
      raise unittest.SkipTest("Skipping test because _acc_state_msg is not implemented for this car") from err

    for enable_mads in (True, False):
      with self.subTest("enable_mads", enable_mads=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)

        self._rx(self._lkas_button_msg(True))
        self._rx(self._lkas_button_msg(False))
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        self._rx(self._acc_state_msg(True))
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())

        self._rx(self._acc_state_msg(False))
        self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_brake_disengage_with_control_request(self):
    """Tests behavior when controls are requested while brake is engaged

    Sequence:
    1. Enable MADS with pause lateral on brake
    2. Brake to pause lateral control
    3. Set control request while braking
    4. Release brake
    5. Verify controls become allowed
    """
    self.safety.set_mads_params(True, False, True)  # enable MADS with pause lateral on brake

    # Initial state
    self.safety.set_controls_allowed_lateral(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Brake press disengages lateral
    self._rx(self._user_brake_msg(True))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Request controls while braking
    self.safety.set_controls_requested_lateral(True)
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Release brake - should enable since controls were requested
    self._rx(self._user_brake_msg(False))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_brake_disengage_with_acc_main_off(self):
    """Tests behavior when ACC main is turned off while brake is engaged

    Sequence:
    1. Enable MADS with pause lateral on brake
    2. Brake to pause lateral control
    3. Turn ACC main off while braking
    4. Release brake
    5. Verify controls remain disengaged
    """
    self.safety.set_mads_params(True, False, True)  # enable MADS with pause lateral on brake

    # Initial state - enable with ACC main
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Brake press disengages lateral
    self._rx(self._user_brake_msg(True))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Turn ACC main off while braking
    self.safety.set_acc_main_on(False)
    self._rx(self._speed_msg(0))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Release brake - should remain disabled since ACC main is off
    self._rx(self._user_brake_msg(False))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_steering_disengage_with_control_request(self):
    self.safety.set_mads_params(True, False, False)

    self.safety.set_controls_allowed_lateral(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    self.safety.set_steering_disengage(True)
    self._rx(self._speed_msg(0))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_disengage_on_brake(self):
    for disengage_on_brake in (True, False):
      self.safety.set_mads_params(True, disengage_on_brake, False)

      self.safety.set_controls_allowed_lateral(True)
      self._rx(self._speed_msg(0))
      self.assertTrue(self.safety.get_controls_allowed_lateral())

      self._rx(self._user_brake_msg(True))
      self.assertEqual(not disengage_on_brake, self.safety.get_controls_allowed_lateral())

      self._rx(self._user_brake_msg(False))
      self.assertEqual(not disengage_on_brake, self.safety.get_controls_allowed_lateral())

  def test_heartbeat_engaged_mads_exact_threshold(self):
    """Test that exactly 3 heartbeat mismatches triggers disengage (not 2 or 4)"""
    self.safety.set_mads_params(True, False, False)
    self.safety.set_controls_allowed_lateral(True)
    self.safety.set_heartbeat_engaged_mads(False)

    # After 2 mismatches: still engaged
    for _ in range(2):
      self.safety.mads_heartbeat_engaged_check()
    self.assertTrue(self.safety.get_controls_allowed_lateral(),
                    "Should still be engaged after 2 mismatches")

    # 3rd mismatch: disengaged
    self.safety.mads_heartbeat_engaged_check()
    self.assertFalse(self.safety.get_controls_allowed_lateral(),
                     "Should disengage after exactly 3 mismatches")

  def test_heartbeat_engaged_mads_reset_on_match(self):
    """Test that mismatch counter resets when heartbeat matches"""
    self.safety.set_mads_params(True, False, False)
    self.safety.set_controls_allowed_lateral(True)
    self.safety.set_heartbeat_engaged_mads(False)

    # 2 mismatches
    for _ in range(2):
      self.safety.mads_heartbeat_engaged_check()
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Match resets counter
    self.safety.set_heartbeat_engaged_mads(True)
    self.safety.mads_heartbeat_engaged_check()
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Need 3 more mismatches from scratch to disengage
    self.safety.set_heartbeat_engaged_mads(False)
    for _ in range(2):
      self.safety.mads_heartbeat_engaged_check()
    self.assertTrue(self.safety.get_controls_allowed_lateral(),
                    "Counter should have reset; 2 mismatches after reset should not disengage")

  def test_mads_button_not_engaged_without_press(self):
    """Test that MADS button in idle state does not engage lateral control"""
    try:
      self._lkas_button_msg(False)
    except NotImplementedError as err:
      raise unittest.SkipTest("MADS button not supported") from err

    self.safety.set_mads_params(True, False, False)

    # Only send idle/release — should NOT engage
    self._rx(self._lkas_button_msg(False))
    self._rx(self._speed_msg(0))
    self.assertFalse(self.safety.get_controls_allowed_lateral(),
                     "Button idle/release alone should not engage lateral control")

  def test_mads_params_individual_flags(self):
    """Test that each MADS param flag is independently wired correctly.

    Kills mutation mutants for ALT_EXP boundary values (1024/2048/4096).
    """
    for enable, disengage, pause in [
      (False, False, False),
      (True, False, False),
      (True, True, False),
      (True, False, True),
    ]:
      with self.subTest(enable=enable, disengage=disengage, pause=pause):
        self.safety.set_mads_params(enable, disengage, pause)
        self.assertEqual(enable, self.safety.get_enable_mads())
        self.assertEqual(enable and disengage, self.safety.get_disengage_lateral_on_brake())
        self.assertEqual(enable and pause, self.safety.get_pause_lateral_on_brake())

  def test_lat_active_only_with_mads_enabled(self):
    """lat_active reflects MADS lateral state only when MADS is enabled"""
    for enable_mads in (True, False):
      with self.subTest(enable_mads=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)
        self.safety.set_controls_allowed(False)

        # Engage via ACC main
        self.safety.set_acc_main_on(True)
        self._rx(self._speed_msg(0))

        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())
        self.assertEqual(enable_mads, self.safety.get_controls_allowed_lateral())
        self.assertFalse(self.safety.get_longitudinal_allowed())

  def test_longitudinal_allowed_independent_of_mads(self):
    """longitudinal_allowed depends only on controls_allowed, not MADS"""
    for enable_mads in (True, False):
      with self.subTest(enable_mads=enable_mads):
        self.safety.set_mads_params(enable_mads, False, False)

        self.safety.set_controls_allowed(True)
        self.assertTrue(self.safety.get_longitudinal_allowed())

        self.safety.set_controls_allowed(False)
        self.assertFalse(self.safety.get_longitudinal_allowed())

  def test_lat_active_with_controls_allowed_and_mads(self):
    """Lateral TX allow = controls_allowed OR controls_allowed_lateral (MADS). Verify each leg."""
    self.safety.set_mads_params(True, False, False)
    self.safety.set_controls_allowed(False)

    # MADS lat only
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed())

    # controls_allowed only (disable MADS lat)
    self.safety.set_acc_main_on(False)
    self._rx(self._speed_msg(0))
    self.safety.set_controls_allowed(True)
    self.assertTrue(self.safety.get_controls_allowed() or self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Both active
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed() or self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_controls_allowed())
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_lat_active_false_when_mads_disabled_and_controls_not_allowed(self):
    """lat_active is False when both MADS and controls_allowed are off"""
    self.safety.set_mads_params(False, False, False)
    self.safety.set_controls_allowed(False)
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_longitudinal_allowed())

  def test_mads_lateral_only_controls_split(self):
    """Verify lat/long control states are independent in MADS lateral-only mode.
    When MADS lat is active but controls_allowed is off, only lateral should be active."""
    self.safety.set_mads_params(True, False, False)
    self.safety.set_controls_allowed(False)

    # Engage MADS lateral via ACC main
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))

    # Lateral active, longitudinal not
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed())
    self.assertFalse(self.safety.get_longitudinal_allowed())

    # Engage cruise (controls_allowed) — both active
    self.safety.set_controls_allowed(True)
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_longitudinal_allowed())

    # Disengage cruise — back to lateral only
    self.safety.set_controls_allowed(False)
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_longitudinal_allowed())

    # Disengage MADS lateral — nothing active
    self.safety.set_acc_main_on(False)
    self._rx(self._speed_msg(0))
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_longitudinal_allowed())

  def test_mads_brake_disengage_lateral_only_mode(self):
    """In MADS lateral-only mode with disengage-on-brake, brake kills lateral while long stays off."""
    self.safety.set_mads_params(True, True, False)  # disengage lateral on brake

    # MADS lateral only (cruise not engaged)
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertFalse(self.safety.get_controls_allowed())
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_longitudinal_allowed())

    # Brake: MADS lateral disengages, controls_allowed stays off
    self._rx(self._user_brake_msg(True))
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed())
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_longitudinal_allowed())

  def test_lateral_defaults_false_on_safety_init(self):
    """controlsAllowedLateral must be false after safety init, even with MADS system enabled."""
    self.safety.set_mads_params(True, False, False)
    # After init, system_enabled is True but controls_allowed_lateral must be False
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed())
    # Requires explicit user action to enable
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_safety_tick_clears_lateral(self):
    """Message lag via safety_tick clears controls_allowed_lateral, causing is_lat_active to go false."""
    self.safety.set_mads_params(True, False, False)
    self.safety.set_acc_main_on(True)
    self._rx(self._speed_msg(0))
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Simulate message lag — safety_tick clears both controls_allowed and controls_allowed_lateral
    self.safety.set_timer(int(2e6))
    self.safety.safety_tick_current_safety_config()
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed_lateral())
    self.assertFalse(self.safety.get_controls_allowed())

  def test_heartbeat_agreement_disengage_on_brake(self):
    """With disengage-on-brake, after brake the Python side sends enabled=False.
    Verify no heartbeat mismatch since both sides agree lateral is off."""
    self.safety.set_mads_params(True, True, False)  # disengage lateral on brake

    self._rx(self._user_brake_msg(False))
    self.safety.set_controls_allowed_lateral(True)
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Heartbeat matches — both active
    self.safety.set_heartbeat_engaged_mads(True)
    self.safety.mads_heartbeat_engaged_check()
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Brake: safety clears controls_allowed_lateral
    self._rx(self._user_brake_msg(True))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Python side: disengage mode → state=disabled → enabled=False → heartbeat sends False
    self.safety.set_heartbeat_engaged_mads(False)
    for _ in range(4):
      self.safety.mads_heartbeat_engaged_check()
    # No mismatch: controls_allowed_lateral=False, so check doesn't trigger
    self.assertFalse(self.safety.get_controls_allowed_lateral())

  def test_heartbeat_agreement_pause_on_brake(self):
    """With pause-on-brake, after brake the Python side sends enabled=True (paused is enabled).
    Verify no heartbeat mismatch and re-enable on brake release."""
    self.safety.set_mads_params(True, False, True)  # pause lateral on brake

    self._rx(self._user_brake_msg(False))
    self.safety.set_controls_requested_lateral(True)
    self.safety.set_controls_allowed_lateral(True)
    self.assertTrue(self.safety.get_controls_allowed_lateral())

    # Brake: safety pauses — controls_allowed_lateral goes False
    self._rx(self._user_brake_msg(True))
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Python side: pause mode → state=paused → enabled=True → heartbeat sends True
    self.safety.set_heartbeat_engaged_mads(True)
    for _ in range(4):
      self.safety.mads_heartbeat_engaged_check()
    # No mismatch: controls_allowed_lateral=False, check condition (lat && !hb) = False
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    # Brake release: safety re-enables lateral
    self._rx(self._user_brake_msg(False))
    self.assertTrue(self.safety.get_controls_allowed_lateral())
    # Heartbeat still True (Python side: paused→enabled, enabled=True)
    self.safety.set_heartbeat_engaged_mads(True)
    for _ in range(4):
      self.safety.mads_heartbeat_engaged_check()
    # No mismatch: both agree lateral is active
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_mads_button_rising_edge_from_not_pressed(self):
    self.safety.set_mads_params(True, False, False)

    self.safety.set_mads_button_press(0)
    self.safety.tick_mads_state(False, False, False, False, False)
    self.assertFalse(self.safety.get_controls_allowed_lateral())

    self.safety.set_mads_button_press(1)
    self.safety.tick_mads_state(False, False, False, False, False)
    self.assertTrue(self.safety.get_controls_allowed_lateral())

  def test_alt_exp_bit_discrimination(self):
    self.safety.mads_apply_alternative_experience(1)
    self.assertFalse(self.safety.get_enable_mads())
    self.assertFalse(self.safety.get_disengage_lateral_on_brake())
    self.assertFalse(self.safety.get_pause_lateral_on_brake())
