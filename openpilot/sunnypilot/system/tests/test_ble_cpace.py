"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest
from unittest import mock

from openpilot.sunnypilot.system.ble import cpace

# draft-irtf-cfrg-cpace-21 appendix B.1 (identical in -20)
DRAFT_CI = bytes.fromhex("0b415f696e69746961746f720b425f726573706f6e646572")
DRAFT_SID = bytes.fromhex("7e4b4791d6a8ef019b936c79fb7f2c57")
DRAFT_G = "d04bf6d41f6a289632a2e929fa29bebd51092512a7829fdde7d314b62f05a73f"
DRAFT_YA_SCALAR = bytes.fromhex("21b4f4bd9e64ed355c3eb676a28ebedaf6d8f17bdc365995b319097153044080")
DRAFT_YA = "1d13c89278cdadd826f6d8d7f887701430f8380ddc17611cdd6dc989ce0c9f32"
DRAFT_YB_SCALAR = bytes.fromhex("848b0779ff415f0af4ea14df9dd1d3c29ac41d836c7808896c4eba19c51ac40a")
DRAFT_YB = "248cccf6d5cdc3646f0ad593f9e6cef4e69d4945f8372e623512ecea32185623"
DRAFT_K = "5b067effbdc0b2a0e1d907b21ebb25cfedb96a852179a847c37e43ee71322c6b"
DRAFT_ISK = "6e19b875f7a561d6b3ca3dbb9ef42ac55de3e717881018204b8922b4d5e53bb2aa82c300bea7b65d2b671da71922ddf6472301b79bc270adfa8bf413285f2263"

SID = bytes(range(24))


class TestCpace(unittest.TestCase):
  def setUp(self):
    patch = mock.patch.object(cpace, "CI", DRAFT_CI)
    patch.start()
    self.addCleanup(patch.stop)

  def test_lv_encoding(self):
    self.assertEqual(cpace.lv(b"1234") + cpace.lv(b"5") + cpace.lv(b"") + cpace.lv(b"678"),
                     bytes.fromhex("043132333401350003363738"))
    self.assertEqual(cpace.lv(bytes(128))[:2], b"\x80\x01")

  def test_map_matches_draft_a5_reference(self):
    # draft appendix A.5 (Z = 2, A = 486662), an independent formulation of the same map
    p, a, z = cpace.P, cpace.J, 2
    for r in (2, 3, 0x123456789ABCDEF, p - 2):
      v = -a * pow(1 + z * r * r, -1, p) % p
      eps = pow((v**3 + a * v * v + v) % p, (p - 1) // 2, p)
      x = (eps * v - (1 - eps) * a * pow(2, -1, p)) % p
      self.assertEqual(cpace.map_to_curve_elligator2_curve25519(r), x)

  def test_generator_draft_vector(self):
    self.assertEqual(cpace.generator(b"Password", DRAFT_CI, DRAFT_SID).hex(), DRAFT_G)

  def test_shares_and_isk_draft_vector(self):
    a = cpace.Cpace(True, b"Password", DRAFT_SID, b"ADa", b"ADb", scalar=DRAFT_YA_SCALAR)
    b = cpace.Cpace(False, b"Password", DRAFT_SID, b"ADa", b"ADb", scalar=DRAFT_YB_SCALAR)
    self.assertEqual(a.public.hex(), DRAFT_YA)
    self.assertEqual(b.public.hex(), DRAFT_YB)
    self.assertEqual(cpace._scalar_mult(DRAFT_YA_SCALAR, b.public).hex(), DRAFT_K)
    self.assertEqual(cpace._scalar_mult(DRAFT_YB_SCALAR, a.public).hex(), DRAFT_K)
    isk = a.isk(b.public)
    self.assertEqual(isk.hex(), DRAFT_ISK)
    self.assertEqual(b.isk(a.public), isk)

  def test_round_trip_confirmation(self):
    a = cpace.Cpace(True, b"12345678", SID, b"\x01", b"\x02")
    b = cpace.Cpace(False, b"12345678", SID, b"\x01", b"\x02")
    isk = a.isk(b.public)
    self.assertEqual(b.isk(a.public), isk)
    ta, tb = a.tag(isk), b.tag(isk)
    self.assertEqual(len(ta), 64)
    self.assertTrue(b.check(isk, a.public, ta))
    self.assertTrue(a.check(isk, b.public, tb))

  def test_wrong_code_fails_confirmation(self):
    a = cpace.Cpace(True, b"12345678", SID, b"\x01", b"\x02")
    b = cpace.Cpace(False, b"12345678", SID, b"\x01", b"\x02")
    c = cpace.Cpace(False, b"12345679", SID, b"\x01", b"\x02")
    isk = a.isk(c.public)
    self.assertFalse(c.check(c.isk(a.public), a.public, a.tag(isk)))
    self.assertNotEqual(b.isk(a.public), c.isk(a.public))

  def test_tampered_ad_fails_confirmation(self):
    a = cpace.Cpace(True, b"12345678", SID, b"\x01", b"\x02")
    b = cpace.Cpace(False, b"12345678", SID, b"\x01", b"\x03")
    isk_a = a.isk(b.public)
    self.assertFalse(b.check(b.isk(a.public), a.public, a.tag(isk_a)))

  def test_low_order_point_aborts(self):
    a = cpace.Cpace(True, b"12345678", SID, b"\x01", b"\x02")
    for bad in (bytes(32), b"\x01" + bytes(31), bytes.fromhex("e0eb7a7c3b41b8ae1656e3faf19fc46ada098deb9c32b1fd866205165f49b800")):
      with self.assertRaises(cpace.CpaceError):
        a.isk(bad)
    with self.assertRaises(cpace.CpaceError):
      a.isk(bytes(31))


if __name__ == "__main__":
  unittest.main()
