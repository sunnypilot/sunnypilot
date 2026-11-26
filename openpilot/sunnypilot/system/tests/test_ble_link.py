"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from openpilot.sunnypilot.system.ble import link

LINK = 0x1234


class TestFraming(unittest.TestCase):
  def test_mtu_23_fragments(self):
    msg = bytes(range(40))
    frames = link.frames(msg, LINK, 20)
    self.assertEqual([len(f) for f in frames], [20, 20, 9])
    self.assertEqual([f[0] for f in frames], [1, 1, 0])
    self.assertEqual({f[1:3] for f in frames}, {LINK.to_bytes(2, "big")})
    r = link.Reassembler(LINK)
    out = [r.feed(f) for f in frames]
    self.assertEqual(out, [None, None, msg])

  def test_single_frame_and_empty_rejected(self):
    self.assertEqual(len(link.frames(b"\x01", LINK, 20)), 1)
    with self.assertRaises(link.LinkError):
      link.frames(b"", LINK, 20)
    with self.assertRaises(link.LinkError):
      link.frames(b"\x01", 0, 20)
    with self.assertRaises(link.LinkError):
      link.frames(b"\x01", LINK, 19)

  def test_frames_never_exceed_att_value_cap(self):
    frames = link.frames(bytes(900), LINK, 517 - 3)
    self.assertEqual([len(f) for f in frames], [512, 3 + 900 - 509])

  def test_cap_before_and_after_session(self):
    r = link.Reassembler(LINK)
    with self.assertRaises(link.LinkError):
      for f in link.frames(bytes(1025), LINK, 244):
        r.feed(f)
    out = None
    for f in link.frames(bytes(1024), LINK, 244):
      out = r.feed(f)
    self.assertEqual(len(out), 1024)
    r.cap = link.SESSION_CAP
    for f in link.frames(bytes(16384), LINK, 244):
      out = r.feed(f)
    self.assertEqual(len(out), 16384)

  def test_malformed_frames_rejected(self):
    r = link.Reassembler(LINK)
    bad = [
      b"\x02" + LINK.to_bytes(2, "big") + b"x",  # bit 1 set
      b"\x80" + LINK.to_bytes(2, "big") + b"x",  # bit 7 set
      b"\x00" + (LINK + 1).to_bytes(2, "big") + b"x",  # other link id
      b"\x00" + LINK.to_bytes(2, "big"),  # no fragment
      b"\x01\x00",  # short
    ]
    for frame in bad:
      with self.assertRaises(link.LinkError):
        r.feed(frame)

  def test_reassembly_resets_after_error(self):
    r = link.Reassembler(LINK)
    r.feed(b"\x01" + LINK.to_bytes(2, "big") + b"ab")
    with self.assertRaises(link.LinkError):
      r.feed(b"\x02" + LINK.to_bytes(2, "big") + b"c")
    self.assertEqual(r.feed(b"\x00" + LINK.to_bytes(2, "big") + b"z"), b"z")


class TestRecords(unittest.TestCase):
  def setUp(self):
    self.k_a, self.k_b = bytes([1]) * 32, bytes([2]) * 32

  def pair(self, interval=link.REKEY_INTERVAL):
    return (link.Records(self.k_a, self.k_b, LINK, rekey_interval=interval),
            link.Records(self.k_b, self.k_a, LINK, rekey_interval=interval))

  def test_round_trip_both_directions(self):
    a, b = self.pair()
    self.assertEqual(b.open(a.seal(b"\x30hi")), b"\x30hi")
    self.assertEqual(a.open(b.seal(b"\x40{}")), b"\x40{}")
    self.assertEqual(a.seal(b"\x30")[0], link.RECORD_TYPE)

  def test_replay_and_reorder_rejected(self):
    a, b = self.pair()
    r0, r1 = a.seal(b"\x30zero"), a.seal(b"\x30one")
    with self.assertRaises(link.LinkError):
      b.open(r1)
    self.assertEqual(b.open(r0), b"\x30zero")
    self.assertEqual(b.open(r1), b"\x30one")
    with self.assertRaises(link.LinkError):
      b.open(r1)

  def test_tamper_and_wrong_link_id_rejected(self):
    a, b = self.pair()
    rec = bytearray(a.seal(b"\x30x"))
    with self.assertRaises(link.LinkError):
      link.Records(self.k_b, self.k_a, LINK + 1).open(bytes(rec))
    rec[-1] ^= 1
    with self.assertRaises(link.LinkError):
      b.open(bytes(rec))
    with self.assertRaises(link.LinkError):
      b.open(b"\x21" + bytes(20))

  def test_rekey_at_boundary(self):
    a, b = self.pair(interval=4)
    recs = [a.seal(bytes([0x30, i])) for i in range(10)]
    self.assertEqual([b.open(r) for r in recs], [bytes([0x30, i]) for i in range(10)])
    old = ChaCha20Poly1305(self.k_a)
    nonce = bytes(4) + (4).to_bytes(8, "little")
    with self.assertRaises(InvalidTag):
      old.decrypt(nonce, recs[4][1:], bytes([link.RECORD_TYPE]) + LINK.to_bytes(2, "big"))
    self.assertNotEqual(link._rekey(self.k_a), self.k_a)


class TestKeysAndSignatures(unittest.TestCase):
  def test_transcript_and_signed_bytes_layout(self):
    with self.assertRaises(ValueError):
      link.transcript(b"\x01", b"")
    th = link.transcript(b"\x01", bytes(26), bytes(32), bytes(32), bytes(64), bytes(64))
    self.assertEqual(len(th), 32)
    signed = link.signed_bytes("D", th, b"spki", bytes(32))
    self.assertEqual(signed[:22], b"sunnylink-ble-keys-v1\x00")
    self.assertEqual(signed[22:23], b"D")
    self.assertEqual(len(signed), 22 + 1 + 32 + 32 + 32)
    with self.assertRaises(ValueError):
      link.signed_bytes("X", th, b"spki", bytes(32))

  def test_session_keys(self):
    k1, k2, code = link.session_keys(bytes(64), bytes(24))
    self.assertEqual((len(k1), len(k2), len(code)), (32, 32, 6))
    self.assertNotEqual(k1, k2)
    self.assertEqual(link.session_keys(bytes(64), bytes(24)), (k1, k2, code))
    self.assertNotEqual(link.session_keys(bytes(64), bytes([1]) * 24)[0], k1)

  def test_sign_verify_rs256_and_es256(self):
    data = b"signed bytes"
    for key in (rsa.generate_private_key(public_exponent=65537, key_size=2048), ec.generate_private_key(ec.SECP256R1())):
      alg, sig = link.sign(key, data)
      spki = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
      self.assertEqual(alg, "RS256" if isinstance(key, rsa.RSAPrivateKey) else "ES256")
      self.assertTrue(link.verify(alg, spki, data, sig))
      self.assertFalse(link.verify(alg, spki, data + b"!", sig))
      self.assertFalse(link.verify(alg, spki, data, sig[:-1]))
      other = "ES256" if alg == "RS256" else "RS256"
      self.assertFalse(link.verify(other, spki, data, sig))
      self.assertFalse(link.verify(alg, b"junk", data, sig))

  def test_unsupported_key_rejected(self):
    with self.assertRaises(ValueError):
      link.sign(ec.generate_private_key(ec.SECP384R1()), b"x")


if __name__ == "__main__":
  unittest.main()
