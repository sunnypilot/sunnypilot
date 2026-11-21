"""Params owned by the local daemon."""
from __future__ import annotations

ENROLL = "SunnylinkLocalEnroll"
REVOKE = "SunnylinkLocalCloudRevoke"

CLOUD_COMMANDS = frozenset({ENROLL, REVOKE})
_PREFIXES = ("SunnylinkLocal", "_sec_")


def is_local_param(key: str) -> bool:
  return key.startswith(_PREFIXES)


def cloud_may_write(key: str) -> bool:
  return key in CLOUD_COMMANDS or not is_local_param(key)
