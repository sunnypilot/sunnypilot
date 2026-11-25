"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import hashlib

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MORE = 0x01
PAKE_SUITE = 1  # CPACE-X25519-SHA512; 0 is a development build with no PAKE
MTU_MIN = 23
FRAME_HEADER = 3
MAX_ATT_VALUE = 512  # Bluetooth caps an attribute value at 512 bytes whatever the MTU
PRE_SESSION_CAP = 1024
SESSION_CAP = 16384
RECORD_TYPE = 0x20
REKEY_INTERVAL = 65536
KEYS_INFO = b"sunnylink-ble-connect-v1 keys"
KEYS_SIGNED_TAG = b"sunnylink-ble-keys-v1\x00"


class LinkError(ValueError):
  pass


def frames(message: bytes, link_id: int, max_frame: int) -> list[bytes]:
  # max_frame is the ATT payload (MTU - 3); each frame carries 3 header bytes of it
  max_frame = min(max_frame, MAX_ATT_VALUE)
  if not 1 <= link_id <= 0xFFFF:
    raise LinkError("link id")
  if max_frame < MTU_MIN - 3 or not message:
    raise LinkError("frame size or empty message")
  size = max_frame - FRAME_HEADER
  chunks = [message[i:i + size] for i in range(0, len(message), size)]
  return [bytes([MORE if i < len(chunks) - 1 else 0]) + link_id.to_bytes(2, "big") + c for i, c in enumerate(chunks)]


class Reassembler:
  def __init__(self, link_id: int, cap: int = PRE_SESSION_CAP):
    self.link_id = link_id
    self.cap = cap  # set to SESSION_CAP once the session is up
    self._buf = bytearray()

  def feed(self, frame: bytes) -> bytes | None:
    if len(frame) <= FRAME_HEADER or frame[0] & ~MORE or int.from_bytes(frame[1:3], "big") != self.link_id:
      self._buf.clear()
      raise LinkError("malformed frame")
    self._buf += frame[FRAME_HEADER:]
    if len(self._buf) > self.cap:
      self._buf.clear()
      raise LinkError("message over cap")
    if frame[0] & MORE:
      return None
    message, self._buf = bytes(self._buf), bytearray()
    return message


def _nonce(n: int) -> bytes:
  return b"\x00" * 4 + n.to_bytes(8, "little")


def _rekey(key: bytes) -> bytes:
  return ChaCha20Poly1305(key).encrypt(_nonce(2**64 - 1), bytes(32), b"")[:32]


class Records:
  def __init__(self, send_key: bytes, recv_key: bytes, link_id: int, *, rekey_interval: int = REKEY_INTERVAL):
    self._send, self._recv = send_key, recv_key
    self._aad = bytes([RECORD_TYPE]) + link_id.to_bytes(2, "big")
    self._interval = rekey_interval
    self._ns = 0
    self._nr = 0

  def seal(self, inner: bytes) -> bytes:
    if self._ns and self._ns % self._interval == 0:
      self._send = _rekey(self._send)
    ct = ChaCha20Poly1305(self._send).encrypt(_nonce(self._ns), inner, self._aad)
    self._ns += 1
    return bytes([RECORD_TYPE]) + ct

  def open(self, record: bytes) -> bytes:
    if len(record) < 1 + 1 + 16 or record[0] != RECORD_TYPE:
      raise LinkError("not a record")
    if self._nr and self._nr % self._interval == 0:
      self._recv = _rekey(self._recv)
    try:
      inner = ChaCha20Poly1305(self._recv).decrypt(_nonce(self._nr), record[1:], self._aad)
    except InvalidTag as e:
      raise LinkError("record authentication failed") from e
    self._nr += 1
    return inner


def transcript(*bodies: bytes) -> bytes:
  # connect_start, connect_window, pake_a, pake_b, confirm_a, confirm_b: clear bodies, fixed sizes, no separators
  if len(bodies) != 6:
    raise ValueError("transcript takes six bodies")
  return hashlib.sha256(b"".join(bodies)).digest()


def session_keys(isk: bytes, sid: bytes) -> tuple[bytes, bytes, str]:
  okm = HKDF(algorithm=hashes.SHA256(), length=68, salt=sid, info=KEYS_INFO).derive(isk)
  check = int.from_bytes(okm[64:68], "big") % 1_000_000
  return okm[:32], okm[32:64], f"{check:06d}"


def signed_bytes(role: str, th: bytes, spki: bytes, static: bytes) -> bytes:
  if role not in ("D", "P") or len(th) != 32 or len(static) != 32:
    raise ValueError("signed bytes")
  return KEYS_SIGNED_TAG + role.encode() + th + hashlib.sha256(spki).digest() + static


def sign(key, data: bytes) -> tuple[str, bytes]:
  if isinstance(key, rsa.RSAPrivateKey):
    return "RS256", key.sign(data, padding.PKCS1v15(), hashes.SHA256())
  if isinstance(key, ec.EllipticCurvePrivateKey) and key.curve.name == "secp256r1":
    return "ES256", key.sign(data, ec.ECDSA(hashes.SHA256()))
  raise ValueError("unsupported key")


def verify(alg: str, spki: bytes, data: bytes, sig: bytes) -> bool:
  try:
    pub = serialization.load_der_public_key(spki)
  except ValueError:
    return False
  try:
    if alg == "RS256" and isinstance(pub, rsa.RSAPublicKey):
      pub.verify(sig, data, padding.PKCS1v15(), hashes.SHA256())
    elif alg == "ES256" and isinstance(pub, ec.EllipticCurvePublicKey) and pub.curve.name == "secp256r1":
      pub.verify(sig, data, ec.ECDSA(hashes.SHA256()))
    else:
      return False
  except InvalidSignature:
    return False
  return True
