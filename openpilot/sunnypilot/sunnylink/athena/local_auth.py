"""Sunnylink local security core: keys, grants, the pending window and the pinned TLS dial.

Nothing here is registered with the RPC dispatcher: an enrollment may only be staged from a
cloud-origin payload, never from a local RPC. See sunnylink-mobile/docs/LOCAL_AUTH.md.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import socket
import ssl
import threading
import ipaddress
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import urlsplit

from websocket import WebSocket, create_connection
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

VERSION = 2
AUTHENTICATE_PURPOSE = "sunnylink-local-authenticate"
PAIRING_TTL_S = 120
# A cloud-delivered enrollment is store-and-forward: the gateway queues the settings-write and the
# device's local half claims it on a later tick, which is minutes late when the cloud link was down
# or the device was asleep. The session a code was scanned from therefore stays usable after the
# code stops being displayed, so the enrollment for the code the user actually scanned can still
# land. It stays single-use, stays bound to that code, and is dropped the moment the user cancels
# the window or it outlives this grace.
PAIRING_DELIVERY_GRACE_S = 600
# How many codes stay usable for a late delivery. A user who retries gets a fresh code, and the
# enrollment for the code they scanned first can still be in flight.
MAX_RECENT_SESSIONS = 3
MAX_ENROLL_BYTES = 4096
MAX_GRANTS = 8

# The QR the app scans is a POINTER, not a proof: it names one device and one pairing window and
# carries nothing else. It is unsigned because a signature does not fit the panel a comma device
# has: the device identity key is RSA (`/persist/comma/id_rsa` — KEYS in common/api/base.py tries
# id_rsa first, and hw.h hardcodes that path), so PKCS#1 makes the signature 256 bytes and base64
# makes it 342 characters, i.e. a 461-character code: version 15, 77 modules, 2.73 px/module on the
# 536x240 mici panel, where it does not decode. The same frame unsigned is 52 characters, a
# 29-module code at 6.27 px/module there. Nothing is given up for that:
#
#   * the DEVICE is the gate, not the code: an enrollment is honored only for a nonce this device
#     minted in its own live window (`_fresh`), so a code nobody's device made enrolls nothing;
#   * the app can only enroll a device its own account has settings access to (the authenticated
#     cloud device details are what resolve the key), so a stranger's code points at a device the
#     app refuses to touch;
#   * the device proves the identity key itself to the phone over pinned TLS, against a fresh
#     challenge, before any session exists (`authenticate_device`) — a stronger proof than a
#     signature over a static code, and unlike one it costs the code no characters.
#
# The comma device id is deliberately absent too: the app already gets it from the same
# authenticated cloud details, and a second unauthenticated copy is one more thing to disagree with.
#
# Frame (the whole QR is its base64url):
#
#   "SLEN" | version | len(cloud id) | cloud id | session (16) | ttl (1)
QR_MAGIC = b"SLEN"
QR_VERSION = 4
QR_SESSION_BYTES = 16
MAX_QR_FRAME_BYTES = 256
# The only RPCs an authenticated local session may ask for. Long-running operations are
# deliberately absent.
LOCAL_METHODS = frozenset({"getParams", "getParamsAllKeys", "getParamsMetadata", "getMessage", "saveParams",
                           "updateLocalAppAlias", "unpairLocalApp"})
_TOKEN = re.compile(r"[A-Za-z0-9_-]+\Z")


class AuthorizationError(ValueError):
  """Fail closed without exposing protocol internals to an unauthenticated peer."""


class Origin(Enum):
  """Where a trust mutation came from. Local sessions may never enroll or revoke."""
  CLOUD = "cloud"
  LOCAL = "local"


def encode64(data: bytes) -> str:
  return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def decode64(value: Any, *, max_bytes: int = MAX_ENROLL_BYTES) -> bytes:
  if not isinstance(value, str) or not value or len(value) > (max_bytes * 4 + 2) // 3 or not _TOKEN.fullmatch(value):
    raise AuthorizationError("invalid encoding")
  try:
    raw = base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
  except ValueError as e:
    raise AuthorizationError("invalid encoding") from e
  if len(raw) > max_bytes or encode64(raw) != value:
    raise AuthorizationError("noncanonical encoding")
  return raw


def load_app_key(value: str) -> ec.EllipticCurvePublicKey:
  raw = decode64(value, max_bytes=128)
  try:
    key = serialization.load_der_public_key(raw)
  except ValueError as e:
    raise AuthorizationError("invalid key") from e
  if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
    raise AuthorizationError("unsupported key")
  if key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo) != raw:
    raise AuthorizationError("noncanonical key")
  return key


def key_id_bytes(key: ec.EllipticCurvePublicKey | rsa.RSAPublicKey) -> bytes:
  raw = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
  return hashlib.sha256(raw).digest()


def key_id(key: ec.EllipticCurvePublicKey | rsa.RSAPublicKey) -> str:
  return encode64(key_id_bytes(key))


@dataclass(frozen=True)
class QrPayload:
  """What the app reads out of the scanned frame. Never authority on its own: the device key it
  ends up pinned to comes from authenticated cloud device details, and the nonce only means
  something to the window this device is displaying now."""
  cloud_device_id: str
  session: bytes
  ttl_s: int


def qr_frame(cloud_device_id: str, session: bytes, ttl_s: int) -> bytes:
  if len(session) != QR_SESSION_BYTES:
    raise AuthorizationError("invalid qr session")
  if not 0 < ttl_s < 256:
    raise AuthorizationError("invalid qr ttl")
  encoded = text_field(cloud_device_id).encode("utf-8")
  if not 0 < len(encoded) < 256:
    raise AuthorizationError("invalid cloud device id")
  return QR_MAGIC + bytes([QR_VERSION, len(encoded)]) + encoded + session + bytes([ttl_s])


def decode_qr(raw: str) -> QrPayload:
  """Parse a scanned QR. The app is the side that reads one (it needs the device key from the
  cloud); this validates the framing so no caller can disagree with [qr_frame]."""
  frame = decode64(raw, max_bytes=MAX_QR_FRAME_BYTES)
  header = len(QR_MAGIC) + 2
  if len(frame) < header + 1 + QR_SESSION_BYTES + 1 or not frame.startswith(QR_MAGIC):
    raise AuthorizationError("invalid qr")
  version, id_length = frame[len(QR_MAGIC)], frame[len(QR_MAGIC) + 1]
  if version != QR_VERSION or id_length == 0 or len(frame) != header + id_length + QR_SESSION_BYTES + 1:
    raise AuthorizationError("invalid qr")
  try:
    cloud_device_id = text_field(frame[header:header + id_length].decode("utf-8"))
  except UnicodeDecodeError as e:
    raise AuthorizationError("invalid qr") from e
  session_start = header + id_length
  return QrPayload(cloud_device_id, frame[session_start:session_start + QR_SESSION_BYTES], frame[-1])


def text_field(value: Any, maximum: int = 128) -> str:
  if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum or any(ord(c) < 32 or ord(c) == 127 for c in value):
    raise AuthorizationError("invalid field")
  return value


def statement(purpose: str, *fields: str) -> bytes:
  """Length-bounded UTF-8 fields; LF is forbidden, avoiding JSON canonicalization."""
  return ("sunnylink-local\n" + purpose + "\n" + "\n".join(text_field(f, 1024) for f in fields) + "\n").encode("utf-8")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
  result: dict[str, Any] = {}
  for key, value in pairs:
    if key in result:
      raise AuthorizationError("duplicate field")
    result[key] = value
  return result


def parse_object(raw: str) -> dict[str, Any]:
  if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_ENROLL_BYTES:
    raise AuthorizationError("message too large")
  try:
    obj = json.loads(raw, object_pairs_hook=_unique_object)
  except (ValueError, UnicodeError) as e:
    raise AuthorizationError("invalid message") from e
  if not isinstance(obj, dict):
    raise AuthorizationError("invalid message")
  return obj


@dataclass(frozen=True)
class Grant:
  app_id: str
  public_key: str
  key_id: str
  app_name: str
  revision: str

  @staticmethod
  def from_dict(data: Mapping[str, Any]) -> Grant:
    if set(data) != {"app_id", "public_key", "key_id", "app_name", "revision"}:
      raise AuthorizationError("invalid grant")
    public = text_field(data["public_key"], 256)
    actual_id = key_id(load_app_key(public))
    if data["key_id"] != actual_id or data["app_id"] != actual_id:
      raise AuthorizationError("key mismatch")
    revision = text_field(data["revision"], 43)
    if len(decode64(revision, max_bytes=32)) != 32:
      raise AuthorizationError("invalid revision")
    return Grant(actual_id, public, actual_id, text_field(data["app_name"], 80), revision)

  def to_dict(self) -> dict[str, str]:
    return {"app_id": self.app_id, "public_key": self.public_key, "key_id": self.key_id,
            "app_name": self.app_name, "revision": self.revision}


@dataclass(frozen=True)
class Window:
  nonce: str
  # How long the code is on the device screen and can be scanned.
  deadline: float
  # [deadline] plus [PAIRING_DELIVERY_GRACE_S]: how long an enrollment for this code may still
  # arrive through the cloud after the code itself can no longer be scanned.
  usable_until: float
  qr: str


class LocalAuthority:
  """The daemon-owned authority. Every trust mutation goes through it, and a persistence
  failure never publishes a new grant."""

  def __init__(self, cloud_device_id: str, comma_device_id: str, device_private_key: ec.EllipticCurvePrivateKey | rsa.RSAPrivateKey,
               persist: Callable[[dict[str, Any]], None], registry: Any = None, clock: Callable[[], float] = time.monotonic):
    self.cloud_device_id = text_field(cloud_device_id)
    self.comma_device_id = text_field(comma_device_id)
    self.device_key = device_private_key
    self.device_key_id = key_id(device_private_key.public_key())
    self.persist = persist
    self.clock = clock
    self.lock = threading.RLock()
    self.window: Window | None = None
    # Codes that are no longer displayed but whose enrollment may still be in flight.
    self.recent: list[Window] = []
    self.pending: Grant | None = None
    # The session [pending] was staged from: the grant is committed while that session's delivery
    # grace lasts even if the code has left the screen.
    self.pending_session: str | None = None
    self.grants: dict[str, Grant] = {}
    if isinstance(registry, dict) and type(registry.get("v")) is int and registry.get("v") == VERSION and set(registry) == {"v", "grants"}:
      entries = registry["grants"]
      if isinstance(entries, list) and len(entries) <= MAX_GRANTS:
        try:
          decoded = [Grant.from_dict(entry) for entry in entries if isinstance(entry, dict)]
          if len(decoded) == len(entries) and len({g.key_id for g in decoded}) == len(decoded):
            self.grants = {g.key_id: g for g in decoded}
        except AuthorizationError:
          pass  # Corrupt storage is not authorization.

  def arm(self) -> str:
    """Open one window and publish the code for it (see the frame note at the top of the module:
    the code is a pointer, so minting one does not touch the identity key)."""
    with self.lock:
      session = secrets.token_bytes(QR_SESSION_BYTES)
      qr = encode64(qr_frame(self.cloud_device_id, session, PAIRING_TTL_S))
      now = self.clock()
      self.window = Window(encode64(session), now + PAIRING_TTL_S, now + PAIRING_TTL_S + PAIRING_DELIVERY_GRACE_S, qr)
      self._remember(self.window)
      self.pending = None
      self.pending_session = None
      return qr

  def _remember(self, window: Window) -> None:
    """Keep the newest displayed codes usable for a late cloud delivery."""
    now = self.clock()
    kept = [w for w in self.recent if w.nonce != window.nonce and now < w.usable_until]
    self.recent = (kept + [window])[-MAX_RECENT_SESSIONS:]

  def cancel(self) -> None:
    """The user cancelled (or the window was replaced): every session it could still be used for
    is gone, so a scanned-but-undelivered enrollment cannot land after the fact."""
    with self.lock:
      self.window = None
      self.recent = []
      self.pending = None
      self.pending_session = None

  def expire(self) -> None:
    """The code left the device screen: it can no longer be scanned, but an enrollment for it may
    still be in flight, so only the displayed window is dropped — the session stays in [recent]
    until its delivery grace ends."""
    with self.lock:
      self.window = None

  def prune_sessions(self) -> None:
    with self.lock:
      now = self.clock()
      self.recent = [w for w in self.recent if now < w.usable_until]

  def _fresh(self, nonce: str) -> None:
    """Accept a session that is displayed now, or was displayed recently enough that an enrollment
    for it can still be travelling through the cloud ([PAIRING_DELIVERY_GRACE_S])."""
    now = self.clock()
    with self.lock:
      candidates = ([self.window] if self.window is not None else []) + self.recent
    if not any(w is not None and now < w.usable_until and secrets.compare_digest(w.nonce, nonce) for w in candidates):
      # Name the reason: this line is the only trace of an enrollment that referenced a code the
      # device no longer honors, and the difference between "expired" and "never displayed" is
      # what tells a user to scan a fresh code instead of retrying the same one.
      raise AuthorizationError("pairing code expired")

  def enroll(self, raw: str, origin: Origin) -> Grant:
    if origin is not Origin.CLOUD:
      raise AuthorizationError("cloud authorization required")
    data = parse_object(raw)
    required = {"v", "cloud_device_id", "comma_device_id", "device_key_id", "pairing_session", "public_key", "key_id", "app_name", "signature"}
    if set(data) != required or type(data["v"]) is not int or data["v"] != VERSION:
      raise AuthorizationError("invalid enrollment")
    if (data["cloud_device_id"], data["comma_device_id"], data["device_key_id"]) != \
       (self.cloud_device_id, self.comma_device_id, self.device_key_id):
      raise AuthorizationError("wrong device")
    public = text_field(data["public_key"], 256)
    key = load_app_key(public)
    app_id = key_id(key)
    if data["key_id"] != app_id:
      raise AuthorizationError("wrong key")
    # The nonce is the QR's own session field: the window this device is displaying decides it,
    # and no other length is honored.
    nonce = text_field(data["pairing_session"], 43)
    if len(decode64(nonce, max_bytes=32)) != QR_SESSION_BYTES:
      raise AuthorizationError("invalid nonce")
    name = text_field(data["app_name"], 80)
    signed = statement("enroll", self.cloud_device_id, self.comma_device_id, self.device_key_id, nonce, public, app_id, name)
    try:
      key.verify(decode64(data["signature"], max_bytes=72), signed, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as e:
      raise AuthorizationError("invalid proof") from e
    with self.lock:
      self._fresh(nonce)
      if self.pending is not None:
        if (self.pending.public_key, self.pending.app_name) != (public, name):
          raise AuthorizationError("window already bound")
        return self.pending
      if app_id not in self.grants and len(self.grants) >= MAX_GRANTS:
        raise AuthorizationError("grant limit")
      self.pending = Grant(app_id, public, app_id, name, encode64(secrets.token_bytes(32)))
      self.pending_session = nonce
      return self.pending

  def confirm(self, grant: Grant, tls_peer_key_id: str) -> Grant:
    """Called only after the transport proves the pinned TLS server key."""
    with self.lock:
      if not secrets.compare_digest(grant.key_id, tls_peer_key_id):
        raise AuthorizationError("wrong TLS peer")
      if self.pending != grant:
        raise AuthorizationError("no pending enrollment")
      if self.pending_session is None:
        raise AuthorizationError("window closed")
      # The enrollment may have arrived late, so what has to hold is that the session it was scanned
      # from is still inside its delivery grace — not that the code is still on the screen.
      self._fresh(self.pending_session)
      updated = self.grants | {grant.key_id: grant}
      self.persist({"v": VERSION, "grants": [g.to_dict() for g in updated.values()]})
      self.grants = updated
      self.cancel()
      return grant

  def authenticate_device(self, phone_key_id: str, challenge: str) -> dict[str, str]:
    """Proof of device identity for the phone's fresh challenge, sent only inside a TLS
    channel already pinned to `phone_key_id`."""
    if len(decode64(challenge, max_bytes=32)) != 32:
      raise AuthorizationError("invalid challenge")
    fields = (self.cloud_device_id, self.comma_device_id, self.device_key_id,
              text_field(phone_key_id, 128), text_field(challenge, 128))
    proof = statement("authenticate-device", *fields)
    if isinstance(self.device_key, ec.EllipticCurvePrivateKey):
      signature = self.device_key.sign(proof, ec.ECDSA(hashes.SHA256()))
    else:
      signature = self.device_key.sign(proof, padding.PKCS1v15(), hashes.SHA256())
    return {"cloud_device_id": self.cloud_device_id, "comma_device_id": self.comma_device_id,
            "device_key_id": self.device_key_id, "phone_key_id": phone_key_id,
            "challenge": challenge, "signature": encode64(signature)}

  def revoke_by_self_proof(self, raw: str, origin: Origin) -> str:
    """Cloud-origin self-revocation: a phone drops its OWN grant.

    The proof is signed by the very key being dropped and verified against the grant this device
    already holds, so it can only ever remove an enrolled phone. Removing a key that is not
    enrolled is not an error: there is simply nothing left to drop.
    """
    if origin is not Origin.CLOUD:
      raise AuthorizationError("cloud authorization required")
    data = parse_object(raw)
    if set(data) != {"v", "cloud_device_id", "comma_device_id", "key_id", "signature"} \
       or type(data["v"]) is not int or data["v"] != VERSION:
      raise AuthorizationError("invalid revocation")
    if (data["cloud_device_id"], data["comma_device_id"]) != (self.cloud_device_id, self.comma_device_id):
      raise AuthorizationError("wrong device")
    app_id = text_field(data["key_id"], 128)
    if len(decode64(app_id, max_bytes=32)) != 32:
      raise AuthorizationError("invalid key id")

    with self.lock:
      grant = self.grants.get(app_id)
    if grant is None:
      # Nothing enrolled under this key. `revoke` still drops a matching staged enrollment.
      self.revoke(app_id)
      return app_id

    proof = statement("revoke", self.cloud_device_id, self.comma_device_id, app_id)
    key = load_app_key(grant.public_key)
    try:
      key.verify(decode64(data["signature"], max_bytes=72), proof, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as e:
      raise AuthorizationError("invalid proof") from e
    self.revoke(app_id)
    return app_id

  def revoke_all(self) -> int:
    """Drop every grant in one durable write, leaving an open pairing window alone."""
    with self.lock:
      removed = len(self.grants)
      if removed == 0:
        return 0
      self.persist({"v": VERSION, "grants": []})
      self.grants = {}
      return removed

  def revoke(self, app_key_id: str) -> bool:
    with self.lock:
      if self.pending is not None and self.pending.key_id == app_key_id:
        self.cancel()
      if app_key_id not in self.grants:
        return False
      updated = {k: g for k, g in self.grants.items() if k != app_key_id}
      self.persist({"v": VERSION, "grants": [g.to_dict() for g in updated.values()]})
      self.grants = updated
      return True

  def session(self, grant: Grant, tls_peer_key_id: str) -> AuthorizedSession:
    with self.lock:
      if self.grants.get(grant.key_id) != grant or not secrets.compare_digest(grant.key_id, tls_peer_key_id):
        raise AuthorizationError("unauthorized peer")
      return AuthorizedSession(self, grant)


class AuthorizedSession:
  """Session-owned authorization, checked immediately before each handler executes."""

  def __init__(self, authority: LocalAuthority, grant: Grant):
    self.authority = authority
    self.grant = grant
    self.closed = False

  def close(self) -> None:
    with self.authority.lock:
      self.closed = True

  def invoke(self, method: str, handler: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    with self.authority.lock:
      if self.closed or self.authority.grants.get(self.grant.key_id) != self.grant or method not in LOCAL_METHODS:
        raise AuthorizationError("request denied")
      # Serializes trust revocation with handler execution. Long-running operations
      # are deliberately excluded from LOCAL_METHODS.
      return handler(*args, **kwargs)


def connect_pinned(endpoint: str, expected_key_id: str, timeout_s: float = 10) -> WebSocket:
  """Pin before the HTTP upgrade, so no header or RPC leaves the device unverified.

  PKIX is replaced by an exact public-key pin for this local socket only; never reuse this
  context for cloud traffic. The pin proves private-key possession, nothing else.
  """
  parsed = urlsplit(endpoint)
  if parsed.scheme != "wss" or parsed.username is not None or parsed.password is not None \
     or parsed.query or parsed.fragment or parsed.path not in ("", "/") or parsed.hostname is None:
    raise AuthorizationError("invalid local endpoint")
  try:
    address = ipaddress.ip_address(parsed.hostname)
    port = parsed.port
  except ValueError as e:
    raise AuthorizationError("invalid local endpoint") from e
  if port is None or address.is_unspecified or address.is_multicast:
    raise AuthorizationError("invalid local endpoint")
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
  context.check_hostname = False
  context.verify_mode = ssl.CERT_NONE
  context.minimum_version = ssl.TLSVersion.TLSv1_3
  context.maximum_version = ssl.TLSVersion.TLSv1_3
  # New context and no supplied session prevent client resumption/early data.
  connection = socket.create_connection((str(address), port), timeout=timeout_s)
  tls: ssl.SSLSocket | None = None
  try:
    tls = context.wrap_socket(connection, server_hostname=None)
    certificate = tls.getpeercert(binary_form=True)
    if certificate is None:
      raise AuthorizationError("missing peer certificate")
    verify_tls_peer(certificate, expected_key_id)
    return create_connection(endpoint, socket=tls, enable_multithread=True, timeout=timeout_s,
                             subprotocols=["sunnylink-local"])
  except Exception:
    (tls or connection).close()
    raise


def verify_tls_peer(certificate_der: bytes, expected_key_id: str) -> str:
  try:
    key = x509.load_der_x509_certificate(certificate_der).public_key()
  except ValueError as e:
    raise AuthorizationError("invalid peer certificate") from e
  if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
    raise AuthorizationError("unsupported peer key")
  actual = key_id(key)
  if not secrets.compare_digest(actual, expected_key_id):
    raise AuthorizationError("wrong TLS peer")
  return actual
