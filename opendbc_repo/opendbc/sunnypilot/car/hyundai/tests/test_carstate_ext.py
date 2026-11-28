"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from opendbc.car import Bus, gen_empty_fingerprint
from opendbc.car.hyundai.hyundaicanfd import CanBus
from opendbc.car.hyundai.interface import CarInterface
from opendbc.car.hyundai.values import CAR, HyundaiFlags
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

CRUISE_BUTTONS = 0x1CF


class TestCcncCarState(unittest.TestCase):
  def _interface(self, alt_buttons):
    # ccNC with LFA steering
    fingerprint = gen_empty_fingerprint()
    can = CanBus(None, fingerprint)
    fingerprint[can.CAM] = {0x161: 32, 0x162: 32}
    fingerprint[can.ECAN] = {0x1AA: 16} if alt_buttons else {CRUISE_BUTTONS: 8}
    CP = CarInterface.get_params(CAR.KIA_EV6, fingerprint, [], False, False, False)
    CP_SP = CarInterface.get_params_sp(CP, CAR.KIA_EV6, fingerprint, [], False, False, False)
    assert CP_SP.flags & HyundaiFlagsSP.CCNC and not CP.flags & HyundaiFlags.CANFD_LKA_STEER_MSG
    assert bool(CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS) == alt_buttons
    return CarInterface(CP, CP_SP)

  def test_lfa_steering_no_cruise_buttons_on_alt_buttons(self):
    # an unsent message in the parser keeps canValid false
    for alt_buttons in (False, True):
      with self.subTest(alt_buttons=alt_buttons):
        CI = self._interface(alt_buttons)
        CI.update([])
        self.assertEqual(not alt_buttons, CRUISE_BUTTONS in CI.can_parsers[Bus.pt].addresses)


if __name__ == "__main__":
  unittest.main()
