#!/usr/bin/env python3
import unittest
import numpy as np
import random
from panda import Panda
from panda.tests.safety import libpandasafety_py
import panda.tests.safety.common as common
from panda.tests.safety.common import CANPackerPanda, make_msg, UNSAFE_MODE

MAX_ACCEL = 2.0
MIN_ACCEL = -3.5

class TestToyotaSafety(common.PandaSafetyTest, common.InterceptorSafetyTest,
                       common.TorqueSteeringSafetyTest):

  TX_MSGS = [[0x283, 0], [0x2E6, 0], [0x2E7, 0], [0x33E, 0], [0x344, 0], [0x365, 0], [0x366, 0], [0x4CB, 0],  # DSU bus 0
             [0x128, 1], [0x141, 1], [0x160, 1], [0x161, 1], [0x470, 1],  # DSU bus 1
             [0x2E4, 0], [0x191, 0], [0x411, 0], [0x412, 0], [0x343, 0], [0x1D2, 0],  # LKAS + ACC
             [0x200, 0], [0x750, 0]]  # interceptor + blindspot monitor
  STANDSTILL_THRESHOLD = 1  # 1kph
  RELAY_MALFUNCTION_ADDR = 0x2E4
  RELAY_MALFUNCTION_BUS = 0
  FWD_BLACKLISTED_ADDRS = {2: [0x2E4, 0x412, 0x191, 0x343]}
  FWD_BUS_LOOKUP = {0: 2, 2: 0}
  INTERCEPTOR_THRESHOLD = 845

  MAX_RATE_UP = 10
  MAX_RATE_DOWN = 25
  MAX_TORQUE = 1500
  MAX_RT_DELTA = 375
  RT_INTERVAL = 250000
  MAX_TORQUE_ERROR = 350
  TORQUE_MEAS_TOLERANCE = 1  # toyota safety adds one to be conversative for rounding

  def setUp(self):
    self.packer = CANPackerPanda("toyota_nodsu_pt_generated")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_TOYOTA, 73)
    self.safety.init_tests()

  def _torque_meas_msg(self, torque):
    values = {"STEER_TORQUE_EPS": torque}
    return self.packer.make_can_msg_panda("STEER_TORQUE_SENSOR", 0, values)

  def _torque_msg(self, torque):
    values = {"STEER_TORQUE_CMD": torque}
    return self.packer.make_can_msg_panda("STEERING_LKA", 0, values)

  def _lta_msg(self, req, req2, angle_cmd):
    values = {"STEER_REQUEST": req, "STEER_REQUEST_2": req2, "STEER_ANGLE_CMD": angle_cmd}
    return self.packer.make_can_msg_panda("STEERING_LTA", 0, values)

  def _accel_msg(self, accel):
    values = {"ACCEL_CMD": accel}
    return self.packer.make_can_msg_panda("ACC_CONTROL", 0, values)

  def _speed_msg(self, speed):
    values = {("WHEEL_SPEED_%s" % n): speed for n in ["FR", "FL", "RR", "RL"]}
    return self.packer.make_can_msg_panda("WHEEL_SPEEDS", 0, values)

  def _brake_msg(self, brake):
    values = {"BRAKE_PRESSED": brake}
    return self.packer.make_can_msg_panda("BRAKE_MODULE", 0, values)

  def _gas_msg(self, gas):
    cruise_active = self.safety.get_controls_allowed()
    values = {"GAS_RELEASED": not gas, "CRUISE_ACTIVE": cruise_active}
    return self.packer.make_can_msg_panda("PCM_CRUISE", 0, values)

  def _pcm_status_msg(self, enable):
    values = {"CRUISE_ACTIVE": enable}
    return self.packer.make_can_msg_panda("PCM_CRUISE", 0, values)

  # Toyota gas gains are the same
  def _interceptor_msg(self, gas, addr):
    to_send = make_msg(0, addr, 6)
    to_send[0].data[0] = (gas & 0xFF00) >> 8 
    to_send[0].data[1] = gas & 0xFF
    to_send[0].data[2] = (gas & 0xFF00) >> 8
    to_send[0].data[3] = gas & 0xFF
    return to_send

  def test_accel_actuation_limits(self):
    limits = ((MIN_ACCEL, MAX_ACCEL, UNSAFE_MODE.DEFAULT),
              (MIN_ACCEL, MAX_ACCEL, UNSAFE_MODE.RAISE_LONGITUDINAL_LIMITS_TO_ISO_MAX))

    for min_accel, max_accel, unsafe_mode in limits:
      for accel in np.arange(min_accel - 1, max_accel + 1, 0.1):
        for controls_allowed in [True, False]:
          self.safety.set_controls_allowed(controls_allowed)
          self.safety.set_unsafe_mode(unsafe_mode)
          if controls_allowed:
            should_tx = int(min_accel * 1000) <= int(accel * 1000) <= int(max_accel * 1000)
          else:
            should_tx = np.isclose(accel, 0, atol=0.0001)
          self.assertEqual(should_tx, self._tx(self._accel_msg(accel)))

  # Only allow LTA msgs with no actuation
  def test_lta_steer_cmd(self):
    for engaged in [True, False]:
      self.safety.set_controls_allowed(engaged)

      # good msg
      self.assertTrue(self._tx(self._lta_msg(0, 0, 0)))

      # bad msgs
      self.assertFalse(self._tx(self._lta_msg(1, 0, 0)))
      self.assertFalse(self._tx(self._lta_msg(0, 1, 0)))
      self.assertFalse(self._tx(self._lta_msg(0, 0, 1)))

      for _ in range(20):
        req = random.choice([0, 1])
        req2 = random.choice([0, 1])
        angle = random.randint(-50, 50)
        should_tx = not req and not req2 and angle == 0
        self.assertEqual(should_tx, self._tx(self._lta_msg(req, req2, angle)))

  def test_rx_hook(self):
    # checksum checks
    for msg in ["trq", "pcm"]:
      self.safety.set_controls_allowed(1)
      if msg == "trq":
        to_push = self._torque_meas_msg(0)
      if msg == "pcm":
        to_push = self._pcm_status_msg(True)
      self.assertTrue(self._rx(to_push))
      to_push[0].data[4] = 0
      to_push[0].data[5] = 0
      to_push[0].data[6] = 0
      to_push[0].data[7] = 0
      self.assertFalse(self._rx(to_push))
      self.assertFalse(self.safety.get_controls_allowed())


if __name__ == "__main__":
  unittest.main()
