"""Local trust: keys, grants, cloud enrollment, pinned TLS dial.

Pairing is automatic: the app pushes a self-signed enrollment for this phone's
key through the existing authenticated cloud settings-write transport (the same
channel all settings writes already trust). The device stages it and commits
the grant only after the phone's key proves itself over pinned TLS on the LAN.
There is no code, window, or presence check: account write access authorizes
enrollment, and the paired-devices list on this screen is the audit trail.
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

VERSION = 3
AUTHENTICATE_PURPOSE = "sunnylink-local-authenticate"
MAX_ENROLL_BYTES = 4096
MAX_GRANTS = 8

LOCAL_METHODS = frozenset({"getParams", "getParamsAllKeys", "getParamsMetadata", "getMessage", "saveParams",
                           "updateLocalAppAlias", "unpairLocalApp"})
_TOKEN = re.compile(r"[A-Za-z0-9_-]+\Z")


class AuthorizationError(ValueError):
  pass


class Origin(Enum):
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


def key_id(key: ec.EllipticCurvePublicKey | rsa.RSAPublicKey) -> str:
  """App id is the hash of its key."""
  raw = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
  return encode64(hashlib.sha256(raw).digest())


def text_field(value: Any, maximum: int = 128) -> str:
  if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum or any(ord(c) < 32 or ord(c) == 127 for c in value):
    raise AuthorizationError("invalid field")
  return value


def statement(purpose: str, *fields: str) -> bytes:
  """Length-bounded fields joined by LF."""
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
  app_name: str

  @staticmethod
  def from_dict(data: Mapping[str, Any]) -> Grant:
    if not isinstance(data, Mapping) or set(data) != {"app_id", "public_key", "app_name"}:
      raise AuthorizationError("invalid grant")
    public = text_field(data["public_key"], 256)
    if data["app_id"] != key_id(load_app_key(public)):
      raise AuthorizationError("key mismatch")
    return Grant(data["app_id"], public, text_field(data["app_name"], 80))

  def to_dict(self) -> dict[str, str]:
    return {"app_id": self.app_id, "public_key": self.public_key, "app_name": self.app_name}


class LocalAuthority:
  """All trust changes go through here."""

  def __init__(self, cloud_device_id: str, comma_device_id: str, device_private_key: ec.EllipticCurvePrivateKey | rsa.RSAPrivateKey,
               persist: Callable[[dict[str, Any]], None], registry: Any = None):
    self.cloud_device_id = text_field(cloud_device_id)
    self.comma_device_id = text_field(comma_device_id)
    self.device_key = device_private_key
    self.device_key_id = key_id(device_private_key.public_key())
    self.persist = persist
    self.lock = threading.RLock()
    self.pending: Grant | None = None
    self.grants = _load_grants(registry)

  def enroll(self, raw: str, origin: Origin) -> Grant:
    if origin is not Origin.CLOUD:
      raise AuthorizationError("cloud authorization required")
    data = parse_object(raw)
    required = {"v", "cloud_device_id", "comma_device_id", "device_key_id", "public_key", "key_id", "app_name", "signature"}
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
    name = text_field(data["app_name"], 80)
    signed = statement("enroll", self.cloud_device_id, self.comma_device_id, self.device_key_id, public, app_id, name)
    try:
      key.verify(decode64(data["signature"], max_bytes=72), signed, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as e:
      raise AuthorizationError("invalid proof") from e
    with self.lock:
      stored = self.grants.get(app_id)
      if stored is not None:
        if stored.public_key != public:
          raise AuthorizationError("key mismatch")
        return stored
      if self.pending is not None:
        if (self.pending.public_key, self.pending.app_name) != (public, name):
          raise AuthorizationError("enrollment in progress")
        return self.pending
      if len(self.grants) >= MAX_GRANTS:
        raise AuthorizationError("grant limit")
      self.pending = Grant(app_id, public, name)
      return self.pending

  def confirm(self, grant: Grant, tls_peer_key_id: str) -> Grant:
    with self.lock:
      if not secrets.compare_digest(grant.app_id, tls_peer_key_id):
        raise AuthorizationError("wrong TLS peer")
      if self.pending != grant:
        raise AuthorizationError("no pending enrollment")
      updated = self.grants | {grant.app_id: grant}
      self.persist(_registry(updated))
      self.grants = updated
      self.pending = None
      return grant

  def authenticate_device(self, phone_key_id: str, challenge: str) -> dict[str, str]:
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
      self.revoke(app_id)
      return app_id

    proof = statement("revoke", self.cloud_device_id, self.comma_device_id, app_id)
    try:
      load_app_key(grant.public_key).verify(decode64(data["signature"], max_bytes=72), proof, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as e:
      raise AuthorizationError("invalid proof") from e
    self.revoke(app_id)
    return app_id

  def revoke_all(self) -> int:
    with self.lock:
      removed = len(self.grants)
      if removed == 0:
        return 0
      self.persist(_registry({}))
      self.grants = {}
      self.pending = None
      return removed

  def revoke(self, app_id: str) -> bool:
    with self.lock:
      if self.pending is not None and self.pending.app_id == app_id:
        self.pending = None
      if app_id not in self.grants:
        return False
      updated = {k: g for k, g in self.grants.items() if k != app_id}
      self.persist(_registry(updated))
      self.grants = updated
      return True

  def session(self, grant: Grant, tls_peer_key_id: str) -> AuthorizedSession:
    with self.lock:
      if self.grants.get(grant.app_id) != grant or not secrets.compare_digest(grant.app_id, tls_peer_key_id):
        raise AuthorizationError("unauthorized peer")
      return AuthorizedSession(self, grant)


def _registry(grants: Mapping[str, Grant]) -> dict[str, Any]:
  return {"v": VERSION, "grants": [g.to_dict() for g in grants.values()]}


def _load_grants(registry: Any) -> dict[str, Grant]:
  """Bad storage loads as no grants."""
  if not isinstance(registry, dict) or registry.get("v") != VERSION or set(registry) != {"v", "grants"}:
    return {}
  entries = registry["grants"]
  if not isinstance(entries, list) or len(entries) > MAX_GRANTS:
    return {}
  try:
    grants = [Grant.from_dict(entry) for entry in entries]
  except AuthorizationError:
    return {}
  if len({g.app_id for g in grants}) != len(grants):
    return {}
  return {g.app_id: g for g in grants}


class AuthorizedSession:

  def __init__(self, authority: LocalAuthority, grant: Grant):
    self.authority = authority
    self.grant = grant
    self.closed = False

  def close(self) -> None:
    with self.authority.lock:
      self.closed = True

  def invoke(self, method: str, handler: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    with self.authority.lock:
      if self.closed or self.authority.grants.get(self.grant.app_id) != self.grant or method not in LOCAL_METHODS:
        raise AuthorizationError("request denied")
      return handler(*args, **kwargs)


def connect_pinned(endpoint: str, expected_key_id: str, timeout_s: float = 10) -> WebSocket:
  """Dial with an exact public-key pin. Local sockets only."""
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
  # A new context and no supplied session prevent client resumption/early data.
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
