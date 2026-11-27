"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import hashlib
import secrets
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from openpilot.common.api.base import BaseApi
from openpilot.common.params import Params
from openpilot.sunnypilot.system.ble import grants
from openpilot.sunnypilot.system.ble.link import PAKE_SUITE
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID

WINDOW_SECONDS = 120

REQUEST_KEY = "SunnylinkLocalConnectPhoneRequest"
REQUEST_ACTIONS = ("open", "cancel", "allow", "deny", "remove")
WINDOW_KEY = "SunnylinkLocalConnectPhoneWindow"
STATUS_KEY = "SunnylinkLocalBluetoothStatus"

# Matter's IsValidSetupPIN list; 00000000 and 99999999 are outside the drawn range
REFUSED_CODES = frozenset({11111111 * digit for digit in range(1, 9)} | {12345678, 87654321})

def _private_key_pem() -> bytes:
  _, private, _ = BaseApi.get_key_pair()
  if private is None:
    raise RuntimeError("device key unavailable")
  return private.encode() if isinstance(private, str) else private


def generate_code() -> int:
  while (code := secrets.randbelow(99_999_998) + 1) in REFUSED_CODES:
    pass
  return code


def format_code(code: int) -> str:
  digits = f"{code:08d}"
  return f"{digits[:4]} {digits[4:]}"


def device_identity() -> tuple[bytes, rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey]:
  key = serialization.load_pem_private_key(_private_key_pem(), password=None)
  return key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo), key


def device_key_hash() -> bytes:
  return hashlib.sha256(device_identity()[0]).digest()


def qr_text(code: int, nonce: bytes) -> str:
  payload = code.to_bytes(4, "big") + device_key_hash() + nonce
  return f"SLC{PAKE_SUITE}:" + base64.urlsafe_b64encode(payload).rstrip(b"=").decode()


def grant_count() -> int:
  return len(grants.load(Params()))


def display_name(params) -> str:
  # the sunnylink app builds the same name from DEVICE_KEYS: change both together
  dongle_id = params.get("DongleId")
  ident = dongle_id if dongle_id and dongle_id != UNREGISTERED_DONGLE_ID else params.get("HardwareSerial")
  return f"comma {ident[:4]}" if ident else "comma"


def write_request(params, action: str, phone: str | None = None) -> int:
  if action not in REQUEST_ACTIONS:
    raise ValueError(action)
  seq = time.monotonic_ns()
  request = {"seq": seq, "action": action}
  if phone is not None:
    request["phone"] = phone
  params.put(REQUEST_KEY, request)
  return seq


def read_window(params) -> dict | None:
  window = params.get(WINDOW_KEY)
  return window if isinstance(window, dict) else None


def read_status(params) -> dict:
  status = params.get(STATUS_KEY)
  return status if isinstance(status, dict) else {}


def phone_indicator(status: dict) -> str:
  # "hidden" radio off; "connected" at least one authenticated session; otherwise "waiting"
  if not status.get("enabled"):
    return "hidden"
  return "connected" if status.get("connected", 0) >= 1 else "waiting"


class ConnectPhoneWindow:
  def __init__(self):
    self._open = False
    self._ready = False
    self._seq = 0
    self._reason = ""
    self._code = 0
    self._nonce = b""
    self._qr = ""
    self._deadline = 0.0
    self._shown = False
    self._held = False

  @property
  def active(self) -> bool:
    return self._open

  def open(self, now: float, seq: int = 0) -> str:
    if self._open and seq == self._seq:
      return "busy"
    # a new request never inherits the old window's code or what is left of its time
    self._close("replaced")
    self._seq = seq
    code = generate_code()
    nonce = secrets.token_bytes(8)
    self._qr = qr_text(code, nonce)
    self._code = code
    self._nonce = nonce
    self._deadline = now + WINDOW_SECONDS
    self._ready = False
    self._shown = False
    self._held = False
    self._reason = ""
    self._open = True
    return "ok"

  def cancel(self, reason: str = "cancel"):
    self._close(reason)

  def hold(self):
    # a phone proved the code: the Allow prompt has its own timer from here
    self._held = True

  def tick(self, now: float, ready: bool = True):
    if now >= self._deadline and not self._held:
      self._close("timeout")
      return
    if ready and not self._shown:
      # the full time counts from when the code can first be used, not from the radio starting
      self._shown = True
      self._deadline = now + WINDOW_SECONDS
    self._ready = ready

  def secret(self) -> tuple[bytes, bytes] | None:
    # the 8 ASCII digits (the CPace PRS) and the window nonce; None once the window is closed
    if not self._open:
      return None
    return f"{self._code:08d}".encode(), self._nonce

  def state(self) -> dict:
    if not self._open:
      return {"seq": self._seq, "state": "closed", "reason": self._reason}
    return {"seq": self._seq, "state": "open" if self._ready else "starting", "code": f"{self._code:08d}", "qr": self._qr,
            "deadline": self._deadline, "held": self._held, "reason": ""}

  def _close(self, reason: str):
    if self._open:
      self._open = False
      self._code = 0
      self._nonce = b""
      self._qr = ""
      self._reason = reason
