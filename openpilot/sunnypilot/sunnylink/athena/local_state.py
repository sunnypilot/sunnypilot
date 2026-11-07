"""Local mode params and shared wire constants."""
from __future__ import annotations

from openpilot.common.params import Params

SUNNYLINK_LOCAL_UDP_PORT = 53133
SUNNYLINK_LOCAL_WS_PORT = 8443

BEACON_PREFIX = "SUNNYLINK1"

LOCAL_APPS_KEY = "SunnylinkLocalApps"
LOCAL_APPS_META_KEY = "SunnylinkLocalAppsMeta"

REVOKE_KEY = "SunnylinkLocalRevoke"
# Value of REVOKE_KEY that drops every grant instead of one.
REVOKE_ALL = "ALL"


def is_locally_paired(params: Params | None = None) -> bool:
  return bool((params or Params()).get(LOCAL_APPS_KEY))


def format_endpoint(host: str, ws_port: int = SUNNYLINK_LOCAL_WS_PORT) -> str:
  return f"ws://{host}:{ws_port}"
