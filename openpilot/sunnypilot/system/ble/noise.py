"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import hashlib
import hmac

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# Noise revision 34, pattern KK only
PROTOCOL = b"Noise_KK_25519_ChaChaPoly_SHA256"  # exactly 32 bytes, so h starts as the name itself
PROLOGUE = b"sunnylink-ble-v1"


class NoiseError(ValueError):
  pass


def _hkdf2(ck: bytes, ikm: bytes) -> tuple[bytes, bytes]:
  temp = hmac.new(ck, ikm, hashlib.sha256).digest()
  out1 = hmac.new(temp, b"\x01", hashlib.sha256).digest()
  return out1, hmac.new(temp, out1 + b"\x02", hashlib.sha256).digest()


def _nonce(n: int) -> bytes:
  return b"\x00" * 4 + n.to_bytes(8, "little")


def _dh(priv: X25519PrivateKey, pub: bytes) -> bytes:
  try:
    return priv.exchange(X25519PublicKey.from_public_bytes(pub))
  except ValueError as e:
    raise NoiseError("low-order or malformed key") from e


class KKHandshake:
  # Messages: -> e, es, ss   <- e, ee, se   (initiator = phone, responder = comma)
  def __init__(self, initiator: bool, s: X25519PrivateKey, rs: bytes, *, e: X25519PrivateKey | None = None,
               prologue: bytes = PROLOGUE):
    self._initiator = initiator
    self._s = s
    self._rs = rs
    self._e = e
    self._re: bytes | None = None
    self._step = 0  # 0 first message, 1 second, 2 done
    self._h = PROTOCOL
    self._ck = PROTOCOL
    self._k: bytes | None = None
    self._n = 0
    s_pub = s.public_key().public_bytes_raw()
    self._mix_hash(prologue)
    # pre-messages, initiator's static key first
    self._mix_hash(s_pub if initiator else rs)
    self._mix_hash(rs if initiator else s_pub)

  def _mix_hash(self, data: bytes):
    self._h = hashlib.sha256(self._h + data).digest()

  def _mix_key(self, ikm: bytes):
    self._ck, temp = _hkdf2(self._ck, ikm)
    self._k, self._n = temp, 0

  def _encrypt(self, plaintext: bytes) -> bytes:
    ct = ChaCha20Poly1305(self._k).encrypt(_nonce(self._n), plaintext, self._h)
    self._n += 1
    self._mix_hash(ct)
    return ct

  def _decrypt(self, ciphertext: bytes) -> bytes:
    try:
      pt = ChaCha20Poly1305(self._k).decrypt(_nonce(self._n), ciphertext, self._h)
    except InvalidTag as e:
      raise NoiseError("handshake authentication failed") from e
    self._n += 1
    self._mix_hash(ciphertext)
    return pt

  def _local_e(self) -> bytes:
    if self._e is None:
      self._e = X25519PrivateKey.generate()
    e_pub = self._e.public_key().public_bytes_raw()
    self._mix_hash(e_pub)
    return e_pub

  def write(self, payload: bytes = b"") -> bytes:
    if self._initiator and self._step == 0:
      e_pub = self._local_e()
      self._mix_key(_dh(self._e, self._rs))  # es
      self._mix_key(_dh(self._s, self._rs))  # ss
    elif not self._initiator and self._step == 1:
      e_pub = self._local_e()
      self._mix_key(_dh(self._e, self._re))  # ee
      self._mix_key(_dh(self._e, self._rs))  # se
    else:
      raise NoiseError("write out of order")
    self._step += 1
    return e_pub + self._encrypt(payload)

  def read(self, message: bytes) -> bytes:
    if len(message) < 32 + 16:
      raise NoiseError("short handshake message")
    e_pub, body = message[:32], message[32:]
    if not self._initiator and self._step == 0:
      self._re = e_pub
      self._mix_hash(e_pub)
      self._mix_key(_dh(self._s, e_pub))  # es
      self._mix_key(_dh(self._s, self._rs))  # ss
    elif self._initiator and self._step == 1:
      self._mix_hash(e_pub)
      self._mix_key(_dh(self._e, e_pub))  # ee
      self._mix_key(_dh(self._s, e_pub))  # se
    else:
      raise NoiseError("read out of order")
    self._step += 1
    return self._decrypt(body)

  def split(self) -> tuple[bytes, bytes]:
    if self._step != 2:
      raise NoiseError("handshake not finished")
    k1, k2 = _hkdf2(self._ck, b"")
    return (k1, k2) if self._initiator else (k2, k1)
