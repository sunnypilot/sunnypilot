"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from opendbc.testing import parameterized

from opendbc.car import gen_empty_fingerprint
from opendbc.car.structs import CarParams
from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.eps_mod import EpsModCarController

CarFw = CarParams.CarFw


class TestHondaEpsMod(unittest.TestCase):

  @parameterized("car_name, fw", [(CAR.HONDA_CIVIC, b'39990-TBA,A030\x00\x00'), (CAR.HONDA_CIVIC, b'39990-TBA-A030\x00\x00'),
                                  (CAR.HONDA_CLARITY, b'39990-TRW-A020\x00\x00'), (CAR.HONDA_CLARITY, b'39990,TRW,A020\x00\x00')])
  def test_eps_mod_fingerprint(self, car_name, fw):
    fingerprint = gen_empty_fingerprint()
    car_fw = [CarFw(ecu="eps", fwVersion=fw)]

    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, car_fw, False, False, False)
    _ = CarInterface.get_params_sp(CP, car_name, fingerprint, car_fw, False, False, False)

    self.assertFalse(CP.dashcamOnly)

  @parameterized("fw, expected", [(b'39990-TBA,A030\x00\x00', [3840, 2560, -2898, -3840]),  # modified: nonlinear lookup
                                  (b'39990-TBA-A030\x00\x00', None)])  # stock: no lookup, upstream STEER_MAX applies
  def test_eps_mod_apply_torque(self, fw, expected):
    car_name = CAR.HONDA_CIVIC
    fingerprint = gen_empty_fingerprint()
    car_fw = [CarFw(ecu="eps", fwVersion=fw)]

    CarInterface = interfaces[car_name]
    CP = CarInterface.get_params(car_name, fingerprint, car_fw, False, False, False)
    CP.carFw = car_fw
    CP_SP = CarInterface.get_params_sp(CP, car_name, fingerprint, car_fw, False, False, False)

    CC = EpsModCarController(CP, CP_SP)
    if expected is None:
      self.assertIsNone(CC.eps_mod_lookup)
      return
    for limited_torque, exp in zip([-1.0, -0.32, 0.5, 1.2], expected, strict=True):
      self.assertEqual(CC.get_apply_torque(limited_torque), exp)
