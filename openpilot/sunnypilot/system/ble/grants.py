"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import secrets

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

GRANTS_KEY = "SunnylinkLocalBleGrants"
KEY_KEY = "SunnylinkLocalBleKey"
MAX_PHONES = 8


def b64(data: bytes) -> str:
  return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def unb64(text: str) -> bytes:
  return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def load(params) -> list[dict]:
  grants = params.get(GRANTS_KEY)
  return grants if isinstance(grants, list) else []


def save(params, grants: list[dict]):
  params.put(GRANTS_KEY, grants, block=True)


def static_private(params) -> X25519PrivateKey:
  raw = params.get(KEY_KEY)
  if not isinstance(raw, bytes) or len(raw) != 32:
    raw = secrets.token_bytes(32)
    params.put(KEY_KEY, raw, block=True)
  return X25519PrivateKey.from_private_bytes(raw)
