"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import unittest

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from openpilot.sunnypilot.system.ble import noise

# Cacophony (noiseprotocol test vectors, centromere/cacophony vectors/cacophony.txt), the KK 25519 ChaChaPoly SHA256 entry
VECTOR = {
  "init_prologue": "4a6f686e2047616c74",
  "init_static": "e61ef9919cde45dd5f82166404bd08e38bceb5dfdfded0a34c8df7ed542214d1",
  "init_ephemeral": "893e28b9dc6ca8d611ab664754b8ceb7bac5117349a4439a6b0569da977c464a",
  "init_remote_static": "31e0303fd6418d2f8c0e78b91f22e8caed0fbe48656dcf4767e4834f701b8f62",
  "resp_prologue": "4a6f686e2047616c74",
  "resp_static": "4a3acbfdb163dec651dfa3194dece676d437029c62a408b4c5ea9114246e4893",
  "resp_ephemeral": "bbdb4cdbd309f1a1f2e1456967fe288cadd6f712d65dc7b7793d5e63da6b375b",
  "resp_remote_static": "6bc3822a2aa7f4e6981d6538692b3cdf3e6df9eea6ed269eb41d93c22757b75a",
  "handshake_hash": "24c6b51ecb76277140ca018b5985bc9f03de321dae2d34dcae433dafef0131d9",
  "messages": [
    ("4c756477696720766f6e204d69736573",
     "ca35def5ae56cec33dc2036731ab14896bc4c75dbb07a61f879f8e3afa4c79440177015efc1fe7a37c629af7120a9627" +
      "4e6ab7afcc9261901d0e09ae32a5bb96"),
    ("4d757272617920526f746862617264",
     "95ebc60d2b1fa672c1f46a8aa265ef51bfe38e7ccb39ec5be34069f144808843b274d3429adc47ca093ba63ef90f8da8" +
      "9fda108db471dccfa4894aa7b00003"),
    ("462e20412e20486179656b", "966b05bc69ec01b8454d3160a214e6f24a3d884eb31ec2408af63f"),
    ("4361726c204d656e676572", "0ad887fba4f611bbb4afe44ba3556b8164332ca7d5934634d63d80"),
    ("4a65616e2d426170746973746520536179", "012b28ae646ae7830e2c5472cb023eab071c1db3d8413ec69b513b83832f974c2d"),
    ("457567656e2042f6686d20766f6e2042617765726b", "bb3e6a48160d9c5971d37f975727294e0d868342db31832e54d07191ab0ca3c3703b5ed3d9"),
  ],
}


def _priv(hex_key: str) -> X25519PrivateKey:
  return X25519PrivateKey.from_private_bytes(bytes.fromhex(hex_key))


def _pub(priv: X25519PrivateKey) -> bytes:
  return priv.public_key().public_bytes_raw()


class TestNoiseKK(unittest.TestCase):
  def test_cacophony_vector(self):
    v = VECTOR
    ini = noise.KKHandshake(True, _priv(v["init_static"]), bytes.fromhex(v["init_remote_static"]),
                            e=_priv(v["init_ephemeral"]), prologue=bytes.fromhex(v["init_prologue"]))
    res = noise.KKHandshake(False, _priv(v["resp_static"]), bytes.fromhex(v["resp_remote_static"]),
                            e=_priv(v["resp_ephemeral"]), prologue=bytes.fromhex(v["resp_prologue"]))
    payload0, ct0 = v["messages"][0]
    payload1, ct1 = v["messages"][1]
    self.assertEqual(ini.write(bytes.fromhex(payload0)).hex(), ct0)
    self.assertEqual(res.read(bytes.fromhex(ct0)).hex(), payload0)
    self.assertEqual(res.write(bytes.fromhex(payload1)).hex(), ct1)
    self.assertEqual(ini.read(bytes.fromhex(ct1)).hex(), payload1)
    self.assertEqual(ini._h.hex(), v["handshake_hash"])

    to_resp, to_ini = ini.split()
    self.assertEqual(res.split(), (to_ini, to_resp))
    for i, (payload, ct) in enumerate(v["messages"][2:], start=2):
      key = to_resp if i % 2 == 0 else to_ini
      counter = i // 2 - 1
      self.assertEqual(ChaCha20Poly1305(key).encrypt(bytes(4) + counter.to_bytes(8, "little"), bytes.fromhex(payload), b"").hex(), ct)

  def test_round_trip_and_split_pairing(self):
    si, sr = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    ini = noise.KKHandshake(True, si, _pub(sr))
    res = noise.KKHandshake(False, sr, _pub(si))
    self.assertEqual(res.read(ini.write(b"hello")), b"hello")
    self.assertEqual(ini.read(res.write(b"comma")), b"comma")
    i_send, i_recv = ini.split()
    r_send, r_recv = res.split()
    self.assertEqual((i_send, i_recv), (r_recv, r_send))
    self.assertNotEqual(i_send, i_recv)

  def test_wrong_static_key_rejected(self):
    si, sr, other = (X25519PrivateKey.generate() for _ in range(3))
    ini = noise.KKHandshake(True, si, _pub(sr))
    msg = ini.write(b"")
    with self.assertRaises(noise.NoiseError):
      noise.KKHandshake(False, other, _pub(si)).read(msg)
    with self.assertRaises(noise.NoiseError):
      noise.KKHandshake(False, sr, _pub(other)).read(msg)

  def test_tampered_message_rejected(self):
    si, sr = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    msg = bytearray(noise.KKHandshake(True, si, _pub(sr)).write(b"\x01"))
    msg[-1] ^= 1
    with self.assertRaises(noise.NoiseError):
      noise.KKHandshake(False, sr, _pub(si)).read(bytes(msg))

  def test_low_order_remote_static_rejected(self):
    with self.assertRaises(noise.NoiseError):
      noise.KKHandshake(True, X25519PrivateKey.generate(), bytes(32)).write()

  def test_out_of_order_rejected(self):
    si, sr = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    res = noise.KKHandshake(False, sr, _pub(si))
    with self.assertRaises(noise.NoiseError):
      res.write()
    with self.assertRaises(noise.NoiseError):
      res.split()


if __name__ == "__main__":
  unittest.main()
