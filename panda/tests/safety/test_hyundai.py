#!/usr/bin/env python3
import unittest
import numpy as np
from panda import Panda
from panda.tests.safety import libpandasafety_py
import panda.tests.safety.common as common
from panda.tests.safety.common import CANPackerPanda, make_msg

MAX_RATE_UP = 3
MAX_RATE_DOWN = 7
MAX_STEER = 384

MAX_RT_DELTA = 112
RT_INTERVAL = 250000

DRIVER_TORQUE_ALLOWANCE = 50
DRIVER_TORQUE_FACTOR = 2

MAX_ACCEL = 2.0
MIN_ACCEL = -3.5

class Buttons:
  RESUME = 1
  SET = 2
  CANCEL = 4

# 4 bit checkusm used in some hyundai messages
# lives outside the can packer because we never send this msg
def checksum(msg):
  addr, t, dat, bus = msg

  chksum = 0
  if addr == 902:
    for i, b in enumerate(dat):
      for j in range(8):
        # exclude checksum and counter bits
        if (i != 1 or j < 6) and (i != 3 or j < 6) and (i != 5 or j < 6) and (i != 7 or j < 6):
          bit = (b >> j) & 1
        else:
          bit = 0
        chksum += bit
    chksum = (chksum ^ 9) & 0xF
    ret = bytearray(dat)
    ret[5] |= (chksum & 0x3) << 6
    ret[7] |= (chksum & 0xc) << 4
  else:
    for i, b in enumerate(dat):
      if addr in [608, 1057] and i == 7:
        b &= 0x0F if addr == 1057 else 0xF0
      elif addr == 916 and i == 6:
        b &= 0xF0
      elif addr == 916 and i == 7:
        continue
      chksum += sum(divmod(b, 16))
    chksum = (16 - chksum) % 16
    ret = bytearray(dat)
    ret[6 if addr == 916 else 7] |= chksum << (4 if addr == 1057 else 0)

  return addr, t, ret, bus

class TestHyundaiSafety(common.PandaSafetyTest):
  TX_MSGS = [[832, 0], [1265, 0], [1157, 0]]
  STANDSTILL_THRESHOLD = 30  # ~1kph
  RELAY_MALFUNCTION_ADDR = 832
  RELAY_MALFUNCTION_BUS = 0
  FWD_BLACKLISTED_ADDRS = {2: [832, 1157]}
  FWD_BUS_LOOKUP = {0: 2, 2: 0}

  cnt_gas = 0
  cnt_speed = 0
  cnt_brake = 0
  cnt_cruise = 0

  def setUp(self):
    self.packer = CANPackerPanda("hyundai_kia_generic")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_HYUNDAI, 0)
    self.safety.init_tests()

  def _button_msg(self, buttons):
    values = {"CF_Clu_CruiseSwState": buttons}
    return self.packer.make_can_msg_panda("CLU11", 0, values)

  def _gas_msg(self, gas):
    values = {"CF_Ems_AclAct": gas, "AliveCounter": self.cnt_gas % 4}
    self.__class__.cnt_gas += 1
    return self.packer.make_can_msg_panda("EMS16", 0, values, fix_checksum=checksum)

  def _brake_msg(self, brake):
    values = {"DriverBraking": brake, "AliveCounterTCS": self.cnt_brake % 8}
    self.__class__.cnt_brake += 1
    return self.packer.make_can_msg_panda("TCS13", 0, values, fix_checksum=checksum)

  def _speed_msg(self, speed):
    # panda safety doesn't scale, so undo the scaling
    values = {"WHL_SPD_%s" % s: speed * 0.03125 for s in ["FL", "FR", "RL", "RR"]}
    values["WHL_SPD_AliveCounter_LSB"] = (self.cnt_speed % 16) & 0x3
    values["WHL_SPD_AliveCounter_MSB"] = (self.cnt_speed % 16) >> 2
    self.__class__.cnt_speed += 1
    return self.packer.make_can_msg_panda("WHL_SPD11", 0, values, fix_checksum=checksum)

  def _pcm_status_msg(self, enable):
    values = {"ACCMode": enable, "CR_VSM_Alive": self.cnt_cruise % 16}
    self.__class__.cnt_cruise += 1
    return self.packer.make_can_msg_panda("SCC12", 0, values, fix_checksum=checksum)

  def _set_prev_torque(self, t):
    self.safety.set_desired_torque_last(t)
    self.safety.set_rt_torque_last(t)

  # TODO: this is unused
  def _torque_driver_msg(self, torque):
    values = {"CR_Mdps_StrColTq": torque}
    return self.packer.make_can_msg_panda("MDPS12", 0, values)

  def _torque_msg(self, torque):
    values = {"CR_Lkas_StrToqReq": torque}
    return self.packer.make_can_msg_panda("LKAS11", 0, values)

  def test_steer_safety_check(self):
    for enabled in [0, 1]:
      for t in range(-0x200, 0x200):
        self.safety.set_controls_allowed(enabled)
        self._set_prev_torque(t)
        if abs(t) > MAX_STEER or (not enabled and abs(t) > 0):
          self.assertFalse(self._tx(self._torque_msg(t)))
        else:
          self.assertTrue(self._tx(self._torque_msg(t)))

  def test_non_realtime_limit_up(self):
    self.safety.set_torque_driver(0, 0)
    self.safety.set_controls_allowed(True)

    self._set_prev_torque(0)
    self.assertTrue(self._tx(self._torque_msg(MAX_RATE_UP)))
    self._set_prev_torque(0)
    self.assertTrue(self._tx(self._torque_msg(-MAX_RATE_UP)))

    self._set_prev_torque(0)
    self.assertFalse(self._tx(self._torque_msg(MAX_RATE_UP + 1)))
    self.safety.set_controls_allowed(True)
    self._set_prev_torque(0)
    self.assertFalse(self._tx(self._torque_msg(-MAX_RATE_UP - 1)))

  def test_non_realtime_limit_down(self):
    self.safety.set_torque_driver(0, 0)
    self.safety.set_controls_allowed(True)

  def test_against_torque_driver(self):
    self.safety.set_controls_allowed(True)

    for sign in [-1, 1]:
      for t in np.arange(0, DRIVER_TORQUE_ALLOWANCE + 1, 1):
        t *= -sign
        self.safety.set_torque_driver(t, t)
        self._set_prev_torque(MAX_STEER * sign)
        self.assertTrue(self._tx(self._torque_msg(MAX_STEER * sign)))

      self.safety.set_torque_driver(DRIVER_TORQUE_ALLOWANCE + 1, DRIVER_TORQUE_ALLOWANCE + 1)
      self.assertFalse(self._tx(self._torque_msg(-MAX_STEER)))

    # spot check some individual cases
    for sign in [-1, 1]:
      driver_torque = (DRIVER_TORQUE_ALLOWANCE + 10) * sign
      torque_desired = (MAX_STEER - 10 * DRIVER_TORQUE_FACTOR) * sign
      delta = 1 * sign
      self._set_prev_torque(torque_desired)
      self.safety.set_torque_driver(-driver_torque, -driver_torque)
      self.assertTrue(self._tx(self._torque_msg(torque_desired)))
      self._set_prev_torque(torque_desired + delta)
      self.safety.set_torque_driver(-driver_torque, -driver_torque)
      self.assertFalse(self._tx(self._torque_msg(torque_desired + delta)))

      self._set_prev_torque(MAX_STEER * sign)
      self.safety.set_torque_driver(-MAX_STEER * sign, -MAX_STEER * sign)
      self.assertTrue(self._tx(self._torque_msg((MAX_STEER - MAX_RATE_DOWN) * sign)))
      self._set_prev_torque(MAX_STEER * sign)
      self.safety.set_torque_driver(-MAX_STEER * sign, -MAX_STEER * sign)
      self.assertTrue(self._tx(self._torque_msg(0)))
      self._set_prev_torque(MAX_STEER * sign)
      self.safety.set_torque_driver(-MAX_STEER * sign, -MAX_STEER * sign)
      self.assertFalse(self._tx(self._torque_msg((MAX_STEER - MAX_RATE_DOWN + 1) * sign)))

  def test_realtime_limits(self):
    self.safety.set_controls_allowed(True)

    for sign in [-1, 1]:
      self.safety.init_tests()
      self._set_prev_torque(0)
      self.safety.set_torque_driver(0, 0)
      for t in np.arange(0, MAX_RT_DELTA, 1):
        t *= sign
        self.assertTrue(self._tx(self._torque_msg(t)))
      self.assertFalse(self._tx(self._torque_msg(sign * (MAX_RT_DELTA + 1))))

      self._set_prev_torque(0)
      for t in np.arange(0, MAX_RT_DELTA, 1):
        t *= sign
        self.assertTrue(self._tx(self._torque_msg(t)))

      # Increase timer to update rt_torque_last
      self.safety.set_timer(RT_INTERVAL + 1)
      self.assertTrue(self._tx(self._torque_msg(sign * (MAX_RT_DELTA - 1))))
      self.assertTrue(self._tx(self._torque_msg(sign * (MAX_RT_DELTA + 1))))

  def test_spam_cancel_safety_check(self):
    self.safety.set_controls_allowed(0)
    self.assertTrue(self._tx(self._button_msg(Buttons.CANCEL)))
    self.assertFalse(self._tx(self._button_msg(Buttons.RESUME)))
    self.assertFalse(self._tx(self._button_msg(Buttons.SET)))
    # do not block resume if we are engaged already
    self.safety.set_controls_allowed(1)
    self.assertTrue(self._tx(self._button_msg(Buttons.RESUME)))


class TestHyundaiLegacySafety(TestHyundaiSafety):
  def setUp(self):
    self.packer = CANPackerPanda("hyundai_kia_generic")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_HYUNDAI_LEGACY, 0)
    self.safety.init_tests()


class TestHyundaiLegacySafetyEV(TestHyundaiSafety):
  def setUp(self):
    self.packer = CANPackerPanda("hyundai_kia_generic")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_HYUNDAI_LEGACY, 1)
    self.safety.init_tests()

  def _gas_msg(self, gas):
    values = {"Accel_Pedal_Pos": gas}
    return self.packer.make_can_msg_panda("E_EMS11", 0, values, fix_checksum=checksum)


class TestHyundaiLegacySafetyHEV(TestHyundaiSafety):
  def setUp(self):
    self.packer = CANPackerPanda("hyundai_kia_generic")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_HYUNDAI_LEGACY, 2)
    self.safety.init_tests()

  def _gas_msg(self, gas):
    values = {"CR_Vcu_AccPedDep_Pos": gas}
    return self.packer.make_can_msg_panda("E_EMS11", 0, values, fix_checksum=checksum)

class TestHyundaiLongitudinalSafety(TestHyundaiSafety):
  TX_MSGS = [[832, 0], [1265, 0], [1157, 0], [1056, 0], [1057, 0], [1290, 0], [905, 0], [1186, 0], [909, 0], [1155, 0], [2000, 0]]
  cnt_button = 0

  def setUp(self):
    self.packer = CANPackerPanda("hyundai_kia_generic")
    self.safety = libpandasafety_py.libpandasafety
    self.safety.set_safety_hooks(Panda.SAFETY_HYUNDAI, Panda.FLAG_HYUNDAI_LONG)
    self.safety.init_tests()

  # override these tests from PandaSafetyTest, hyundai longitudinal uses button enable
  def test_disable_control_allowed_from_cruise(self):
    pass

  def test_enable_control_allowed_from_cruise(self):
    pass

  def test_cruise_engaged_prev(self):
    pass

  def _pcm_status_msg(self, enable):
    raise NotImplementedError

  def _button_msg(self, buttons):
    values = {"CF_Clu_CruiseSwState": buttons, "CF_Clu_AliveCnt1": self.cnt_button}
    self.__class__.cnt_button += 1
    return self.packer.make_can_msg_panda("CLU11", 0, values)

  def _send_accel_msg(self, accel, aeb_req=False, aeb_decel=0):
    values = {
      "aReqRaw": accel,
      "aReqValue": accel,
      "AEB_CmdAct": int(aeb_req),
      "CR_VSM_DecCmd": aeb_decel,
    }
    return self.packer.make_can_msg_panda("SCC12", 0, values)

  def _send_fca11_msg(self, idx=0, aeb_req=False, aeb_decel=0):
    values = {
      "CR_FCA_Alive": ((-((idx % 0xF) + 2) % 4) << 2) + 1,
      "Supplemental_Counter": idx % 0xF,
      "FCA_Status": 2,
      "CR_VSM_DecCmd": aeb_decel,
      "CF_VSM_DecCmdAct": int(aeb_req),
      "FCA_CmdAct": int(aeb_req),
    }
    return self.packer.make_can_msg_panda("FCA11", 0, values)

  def test_no_aeb_fca11(self):
    self.assertTrue(self._tx(self._send_fca11_msg()))
    self.assertFalse(self._tx(self._send_fca11_msg(aeb_req=True)))
    self.assertFalse(self._tx(self._send_fca11_msg(aeb_decel=1.0)))

  def test_no_aeb_scc12(self):
    self.assertTrue(self._tx(self._send_accel_msg(0)))
    self.assertFalse(self._tx(self._send_accel_msg(0, aeb_req=True)))
    self.assertFalse(self._tx(self._send_accel_msg(0, aeb_decel=1.0)))

  def test_set_resume_buttons(self):
    for btn in range(8):
      self.safety.set_controls_allowed(0)
      self._rx(self._button_msg(btn))
      self.assertEqual(btn in [Buttons.RESUME, Buttons.SET], self.safety.get_controls_allowed(), msg=f"btn {btn}")

  def test_cancel_button(self):
    self.safety.set_controls_allowed(1)
    self._rx(self._button_msg(Buttons.CANCEL))
    self.assertFalse(self.safety.get_controls_allowed())

  def test_accel_safety_check(self):
    for controls_allowed in [True, False]:
      for accel in np.arange(MIN_ACCEL - 1, MAX_ACCEL + 1, 0.01):
        accel = round(accel, 2) # floats might not hit exact boundary conditions without rounding
        self.safety.set_controls_allowed(controls_allowed)
        send = MIN_ACCEL <= accel <= MAX_ACCEL if controls_allowed else accel == 0
        self.assertEqual(send, self._tx(self._send_accel_msg(accel)), (controls_allowed, accel))

  def test_diagnostics(self):
    tester_present = common.package_can_msg((0x7d0, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", 0))
    self.assertTrue(self.safety.safety_tx_hook(tester_present))

    not_tester_present = common.package_can_msg((0x7d0, 0, b"\x03\xAA\xAA\x00\x00\x00\x00\x00", 0))
    self.assertFalse(self.safety.safety_tx_hook(not_tester_present))

  def test_radar_alive(self):
    # If the radar knockout failed, make sure the relay malfunction is shown
    self.assertFalse(self.safety.get_relay_malfunction())
    self._rx(make_msg(0, 1057, 8))
    self.assertTrue(self.safety.get_relay_malfunction())



if __name__ == "__main__":
  unittest.main()
