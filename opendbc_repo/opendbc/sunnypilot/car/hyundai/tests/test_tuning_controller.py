"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import unittest
import numpy as np
from unittest.mock import Mock

from opendbc.sunnypilot.car.hyundai.longitudinal import config
from opendbc.sunnypilot.car.hyundai.longitudinal.controller import LongitudinalController, LongitudinalState, SPEED_BP
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP
from opendbc.car import DT_CTRL, structs
from opendbc.car.interfaces import CarStateBase
from opendbc.car.hyundai.values import HyundaiFlags

LongCtrlState = structs.CarControl.Actuators.LongControlState


class TestLongitudinalTuningController(unittest.TestCase):
  def for_all_configs(self, test_func):
    all_configs = list(config.TUNING_CONFIGS.items()) + list(config.CAR_SPECIFIC_CONFIGS.items())
    for name, cfg in all_configs:
      CP = Mock(carFingerprint=name, flags=0)
      CP.radarUnavailable = False
      CP_SP = Mock(flags=0)
      controller = LongitudinalController(CP, CP_SP)
      controller.car_config = cfg
      test_func(controller, CP, CP_SP, name, cfg)

  def test_config_array_length(self):
    """Test that all jerk config arrays are the correct length."""
    def check_lengths(controller, CP, CP_SP, name, cfg):
      bp_len = len(cfg.lookahead_jerk_bp)
      self.assertEqual(bp_len, len(cfg.lookahead_jerk_upper_v), f"{name}: lookahead_jerk_bp and lookahead_jerk_upper_v length mismatch")
      self.assertEqual(bp_len, len(cfg.lookahead_jerk_lower_v), f"{name}: lookahead_jerk_bp and lookahead_jerk_lower_v length mismatch")
      self.assertEqual(len(cfg.upper_jerk_v), len(SPEED_BP), f"{name}: upper_jerk_v and SPEED_BP length mismatch")
      self.assertEqual(len(cfg.lower_jerk_v), len(SPEED_BP), f"{name}: lower_jerk_v and SPEED_BP length mismatch")
    self.for_all_configs(check_lengths)

  def test_config_array_division(self):
    """Test that jerk config calculations do not divide by zero."""
    jerk_arrays = [
      'upper_jerk_v', 'lower_jerk_v',
      'lookahead_jerk_upper_v', 'lookahead_jerk_lower_v',
    ]

    def check_division(controller, CP, CP_SP, name, cfg):
      CS = Mock()
      CS.out = Mock(vEgo=5.0, aEgo=1.0)
      CS.aBasis = 1.0
      CC = Mock()
      CC.actuators = Mock(accel=1.0)
      CC.longActive = True
      CC.hudControl = Mock(visualAlert=None)
      CC.actuators.longControlState = LongCtrlState.pid
      # Check for zeros in jerk arrays
      for array_name in jerk_arrays:
        arr = getattr(cfg, array_name, None)
        if arr is not None:
          for i, val in enumerate(arr):
            self.assertNotEqual(val, 0.0, f"{name}: {array_name}[{i}] cannot be zero")
      self.assertNotEqual(cfg.jerk_limits, 0.0, f"{name}: jerk_limits cannot be zero")

      # Check that lookahead_jerk_bp values are valid
      bp = getattr(cfg, 'lookahead_jerk_bp', None)
      if bp is not None and len(bp) > 1:
        for i in range(1, len(bp)):
          self.assertGreater(bp[i], bp[i-1], f"{name}: lookahead_jerk_bp not valid at index {i}: {bp}")
      # Run config through controller and calculate
      controller.accel_cmd = 1.0
      controller.accel_last = 0.5
      try:
        controller.calculate_jerk(CC, CS, LongCtrlState.pid)
        controller._calculate_dynamic_lower_jerk(-1.0, 5.0)
        controller._calculate_lookahead_jerk(0.5, 5.0)
        controller._calculate_speed_based_jerk_limits(5.0, LongCtrlState.pid)
      except (ZeroDivisionError, ValueError, AssertionError) as e:
        self.fail(f"{name}: {type(e).__name__} in controller calculations: {e}")
    self.for_all_configs(check_division)

  def test_init(self):
    """Test controller initialization"""
    def check_init(controller, CP, CP_SP, name, cfg):
      self.assertIsInstance(controller.tuning, LongitudinalState)
      self.assertEqual(controller.desired_accel, 0.0)
      self.assertEqual(controller.actual_accel, 0.0)
      self.assertEqual(controller.jerk_upper, 0.0)
      self.assertEqual(controller.jerk_lower, 0.0)
      self.assertEqual(controller.comfort_band_upper, 0.0)
      self.assertEqual(controller.comfort_band_lower, 0.0)
    self.for_all_configs(check_init)

  def test_make_jerk_flag_off(self):
    """Test jerk with LONG_TUNING_DYNAMIC flag off"""
    def check_flag_off(controller, CP, CP_SP, name, cfg):
      CC, CS = Mock(spec=structs.CarControl), Mock(spec=CarStateBase)
      CS.out = Mock(vEgo=5.0, aEgo=-2.0)
      CS.aBasis = 0.0
      cases = [
        # (flags, enabled, state, expected_upper, expected_lower)
        (0, None, LongCtrlState.pid,      3.0, 5.0),
        (0, None, LongCtrlState.stopping, 1.0, 5.0),
        (HyundaiFlags.CANFD, True,  LongCtrlState.pid, 3.0, 5.0),
        (HyundaiFlags.CANFD, False, LongCtrlState.pid, 3.0, 1.0),
      ]
      for flags, enabled, state, upper, lower in cases:
        controller.CP.flags = flags
        if enabled is not None:
          CC.enabled = enabled
        controller.calculate_jerk(CC, CS, state)
        self.assertEqual(controller.jerk_upper, upper)
        self.assertEqual(controller.jerk_lower, lower)
    self.for_all_configs(check_flag_off)

  def test_make_jerk_flag_on(self):
    """Only verify that limits update when flags are on."""
    def check_flag_on(controller, CP, CP_SP, name, cfg):
      controller.CP_SP.flags = HyundaiFlagsSP.LONG_TUNING_DYNAMIC
      controller.CP.flags = HyundaiFlags.CANFD
      CC = Mock()
      CC.actuators = Mock(accel=1.0)
      CC.longActive = True
      controller.stopping = False
      CS = Mock()
      CS.out = Mock(aEgo=0.8, vEgo=3.0)
      CS.aBasis = 0.8
      controller.calculate_jerk(CC, CS, LongCtrlState.pid)
      print(f"[FlagOn][{name}] jerk_upper={controller.jerk_upper:.3f}, jerk_lower={controller.jerk_lower:.3f}")
      self.assertGreater(controller.jerk_upper, 0.0)
      self.assertGreater(controller.jerk_lower, 0.0)
    self.for_all_configs(check_flag_on)

  def test_a_value_jerk_scaling(self):
    """Test a_value jerk scaling under tuning branch."""
    def check_a_value(controller, CP, CP_SP, name, cfg):
      controller.CP_SP.flags = HyundaiFlagsSP.LONG_TUNING_DYNAMIC
      controller.CP.radarUnavailable = False
      CC = Mock()
      CC.actuators = Mock(accel=1.0)
      CC.longActive = True
      print(f"[a_value][{name}] starting accel_last:", controller.tuning.accel_last)
      # first pass: limit to jerk_upper * DT_CTRL * 2 = 0.1
      controller.jerk_upper = 0.1 / (DT_CTRL * 2)
      controller.accel_cmd = 1.0
      controller.calculate_accel(CC)
      print(f"[a_value][{name}] pass1 actual_accel={controller.actual_accel:.5f}")
      self.assertAlmostEqual(controller.actual_accel, 0.1, places=5)

      # second pass: limit increment by new jerk_upper
      CC.actuators.accel = 0.7
      controller.jerk_upper = 0.2 / (DT_CTRL * 2)
      controller.accel_cmd = 0.7
      controller.calculate_accel(CC)
      print(f"[a_value][{name}] pass2 actual_accel={controller.actual_accel:.5f}")
      self.assertAlmostEqual(controller.actual_accel, 0.3, places=5)
    self.for_all_configs(check_a_value)

  def test_make_jerk_realistic_profile(self):
    """Test make_jerk with realistic velocity and acceleration profile"""
    def check_realistic(controller, CP, CP_SP, name, cfg):
      np.random.seed(42)
      num_points = 30
      segments = [
        np.random.uniform(0.3, 0.8, num_points//4),
        np.random.uniform(0.8, 1.6, num_points//4),
        np.random.uniform(-0.2, 0.2, num_points//4),
        np.random.uniform(-1.2, -0.5, num_points//8),
        np.random.uniform(-2.2, -1.2, num_points//8)
      ]
      accels = np.concatenate(segments)[:num_points]
      vels = np.zeros_like(accels)
      vels[0] = 5.0
      for i in range(1, len(accels)):
        vels[i] = max(0.0, min(30.0, vels[i-1] + accels[i-1] * (DT_CTRL*2)))
      CC, CS = Mock(), Mock()
      CC.actuators, CS.out = Mock(), Mock()
      CC.longActive = True
      controller.stopping = False

      # Test with LONG_TUNING_DYNAMIC only
      controller.CP_SP.flags = HyundaiFlagsSP.LONG_TUNING_DYNAMIC
      for v, a in zip(vels, accels, strict=True):
        CS.out.vEgo = float(v)
        CS.out.aEgo = float(a)
        CS.aBasis = float(a)
        CC.actuators.accel = float(a)
        controller.calculate_jerk(CC, CS, LongCtrlState.pid)
        print(f"[realistic][LONG_TUNING_DYNAMIC][{name}] v={v:.2f}, a={a:.2f}, jerk_upper={controller.jerk_upper:.2f}, jerk_lower={controller.jerk_lower:.2f}")
        self.assertGreater(controller.jerk_upper, 0.0)

      controller.tuning = LongitudinalState()
      controller.jerk_upper = 0.5
      controller.jerk_lower = 0.5

      # Test with LONG_TUNING_DYNAMIC and LONG_TUNING_PREDICTIVE
      controller.CP_SP.flags = HyundaiFlagsSP.LONG_TUNING_DYNAMIC | HyundaiFlagsSP.LONG_TUNING_PREDICTIVE
      for v, a in zip(vels, accels, strict=True):
        CS.out.vEgo = float(v)
        CS.out.aEgo = float(a)
        CS.aBasis = float(a)
        CC.actuators.accel = float(a)
        controller.calculate_jerk(CC, CS, LongCtrlState.pid)
        print(f"[realistic][LONG_TUNING_PREDICTIVE][{name}] v={v:.2f}, a={a:.2f}, " +
              f"jerk_upper={controller.jerk_upper:.2f}, jerk_lower={controller.jerk_lower:.2f}")
        self.assertGreater(controller.jerk_upper, 0.0)
    self.for_all_configs(check_realistic)

  def test_emergency_control_negative_accel_limit(self):
    """Test that emergency_control method does not allow accel to exceed -3.5 m/s^2 when jerk_lower is 8.0"""
    def check_emergency(controller, CP, CP_SP, name, cfg):
      CC = Mock(spec=structs.CarControl)
      CC.longActive = True
      controller.accel_cmd = -5.0
      controller.accel_last = 0.0
      controller.emergency_control(CC)
      self.assertGreaterEqual(controller.actual_accel, -3.5)
    self.for_all_configs(check_emergency)


if __name__ == "__main__":
  unittest.main()
