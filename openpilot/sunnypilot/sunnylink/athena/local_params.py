"""Param names the local daemon owns, and who may touch them.

`SunnylinkLocal*` (and `_sec_*`) belong to the local daemon: the cloud daemon may not read or write
them, except the two commands an app pushes through the cloud settings-write for it to claim.
"""
from __future__ import annotations

ENROLL = "SunnylinkLocalEnroll"
REVOKE = "SunnylinkLocalCloudRevoke"

CLOUD_COMMANDS = frozenset({ENROLL, REVOKE})
_PREFIXES = ("SunnylinkLocal", "_sec_")


def is_local_param(key: str) -> bool:
  """True for every param the local side owns: hidden from the cloud and from local sessions."""
  return key.startswith(_PREFIXES)


def cloud_may_write(key: str) -> bool:
  """The cloud settings-write may deliver its two local commands and nothing else local."""
  return key in CLOUD_COMMANDS or not is_local_param(key)
