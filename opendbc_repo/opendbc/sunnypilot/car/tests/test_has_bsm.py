"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.sunnypilot.car.interfaces import has_bsm
from opendbc.testing import parameterized


class TestHasBsm(unittest.TestCase):

  # car, bus and address of the BSM message upstream detects (None: always available)
  @parameterized("car_name, bus, addr", [("TOYOTA_RAV4_TSS2", 0, 0x3F6), ("RIVIAN_R1", 1, 0x131a), ("TESLA_MODEL_3", None, None)])
  def test_has_bsm(self, car_name, bus, addr):
    for present in (False, True):
      fingerprint = gen_empty_fingerprint()
      if present and addr is not None:
        fingerprint[bus][addr] = 8
      CarInterface = interfaces[car_name]
      CP = CarInterface.get_params(car_name, fingerprint, [], False, False, False)
      CP_SP = CarInterface.get_params_sp(CP, car_name, fingerprint, [], False, False, False)
      self.assertEqual(has_bsm(CP, CP_SP), present or addr is None)
