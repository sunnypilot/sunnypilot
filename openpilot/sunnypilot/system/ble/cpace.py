"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import hashlib
import hmac
import secrets

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

# draft-irtf-cfrg-cpace-21, CPACE-X25519-SHA512 (the same test vectors as -20)
PAKE_SUITE = 1
DSI = b"CPace255"
CI = b"sunnylink-ble-connect-v1"

P = 2**255 - 19
J = 486662
C2 = pow(2, (P + 3) // 8, P)
C3 = pow(2, (P - 1) // 4, P)  # sqrt(-1)
C4 = (P - 5) // 8


class CpaceError(ValueError):
  pass


def lv(data: bytes) -> bytes:
  # LEB128 length prefix, as the draft's prepend_len
  n = len(data)
  head = bytearray()
  while True:
    head.append((n & 0x7F) | (0x80 if n >> 7 else 0))
    n >>= 7
    if not n:
      return bytes(head) + data


def _cmov(a: int, b: int, cond: bool) -> int:
  # b if cond else a, as a mask select; Python bigints are not constant time regardless
  mask = -int(cond)
  return (a & ~mask) | (b & mask)


def map_to_curve_elligator2_curve25519(u: int) -> int:
  # RFC 9380 G.2.1 straight-line map, Z = 2. Only x is returned: the RFC's y, x2 sign fix and y2 steps
  # feed nothing CPace uses, and x only depends on e3 (which needs y1).
  tv1 = 2 * u * u % P
  xd = (tv1 + 1) % P
  x1n = -J % P
  tv2 = xd * xd % P
  gxd = tv2 * xd % P
  gx1 = J * tv1 % P * x1n % P
  gx1 = (gx1 + tv2) % P * x1n % P
  tv3 = gxd * gxd % P
  tv2 = tv3 * tv3 % P
  tv3 = tv3 * gxd % P
  tv3 = tv3 * gx1 % P
  tv2 = tv2 * tv3 % P
  y11 = pow(tv2, C4, P) * tv3 % P
  y12 = y11 * C3 % P
  e1 = (y11 * y11 % P * gxd - gx1) % P == 0
  y1 = _cmov(y12, y11, e1)
  x2n = x1n * tv1 % P
  e3 = (y1 * y1 % P * gxd - gx1) % P == 0
  xn = _cmov(x2n, x1n, e3)
  return xn * pow(xd, P - 2, P) % P


def generator(prs: bytes, ci: bytes, sid: bytes) -> bytes:
  zpad = max(0, 128 - len(lv(prs)) - len(lv(DSI)) - 1)
  gen_str = lv(DSI) + lv(prs) + lv(bytes(zpad)) + lv(ci) + lv(sid)
  u = int.from_bytes(hashlib.sha512(gen_str).digest()[:32], "little") & ((1 << 255) - 1)
  return map_to_curve_elligator2_curve25519(u % P).to_bytes(32, "little")


def _scalar_mult(scalar: bytes, point: bytes) -> bytes:
  try:
    k = X25519PrivateKey.from_private_bytes(scalar).exchange(X25519PublicKey.from_public_bytes(point))
  except ValueError as e:
    raise CpaceError("low-order or malformed point") from e
  if k == bytes(32):
    raise CpaceError("low-order point")
  return k


def _tag(isk: bytes, sid: bytes, share: bytes, ad: bytes) -> bytes:
  mac_key = hashlib.sha512(b"CPaceMac" + sid + isk).digest()
  return hmac.new(mac_key, lv(share) + lv(ad), hashlib.sha512).digest()


class Cpace:
  def __init__(self, initiator: bool, prs: bytes, sid: bytes, ad_a: bytes, ad_b: bytes, *, scalar: bytes | None = None):
    self._initiator = initiator
    self._sid = sid
    self._ad_a, self._ad_b = ad_a, ad_b
    self._scalar = scalar if scalar is not None else secrets.token_bytes(32)
    self.public = _scalar_mult(self._scalar, generator(prs, CI, sid))

  def isk(self, peer_share: bytes) -> bytes:
    k = _scalar_mult(self._scalar, peer_share)
    ya, yb = (self.public, peer_share) if self._initiator else (peer_share, self.public)
    transcript = lv(ya) + lv(self._ad_a) + lv(yb) + lv(self._ad_b)
    return hashlib.sha512(lv(DSI + b"_ISK") + lv(self._sid) + lv(k) + transcript).digest()

  def tag(self, isk: bytes) -> bytes:
    own_ad = self._ad_a if self._initiator else self._ad_b
    return _tag(isk, self._sid, self.public, own_ad)

  def check(self, isk: bytes, peer_share: bytes, peer_tag: bytes) -> bool:
    peer_ad = self._ad_b if self._initiator else self._ad_a
    return hmac.compare_digest(_tag(isk, self._sid, peer_share, peer_ad), peer_tag)
