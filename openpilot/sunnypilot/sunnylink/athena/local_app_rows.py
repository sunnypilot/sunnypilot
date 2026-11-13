from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from openpilot.sunnypilot.sunnylink.athena.local_auth import MAX_GRANTS

MAX_LOCAL_APP_ROWS = MAX_GRANTS
DEFAULT_APP_NAME = "sunnylink mobile"
NEVER_CONNECTED = "not connected yet"


@dataclass(frozen=True)
class LocalAppRow:
  app_id: str
  title: str
  subtitle: str


def short_key(app_id: str, length: int = 10) -> str:
  return app_id if len(app_id) <= length else app_id[:length] + "…"


def format_age(seconds: float) -> str:
  if seconds < 60:
    return "just now"
  if seconds < 3600:
    return f"{int(seconds // 60)}m ago"
  if seconds < 86_400:
    return f"{int(seconds // 3600)}h ago"
  return f"{int(seconds // 86_400)}d ago"


def last_seen_text(entry: Mapping[str, object] | None, now: float) -> str:
  seen = entry.get("last_seen") if isinstance(entry, Mapping) else None
  if not isinstance(seen, (int, float)) or isinstance(seen, bool) or now - float(seen) < 0:
    return NEVER_CONNECTED
  return format_age(now - float(seen))


def _title(app_id: str, grant: dict, entry: Mapping[str, object] | None) -> str:
  alias = entry.get("alias") if isinstance(entry, Mapping) else None
  if isinstance(alias, str) and alias.strip():
    return alias.strip()
  name = grant.get("app_name")
  return name if isinstance(name, str) and name else DEFAULT_APP_NAME


def build_local_app_rows(grants: list[dict[str, str]],
                         meta: Mapping[str, Mapping[str, object]] | None = None,
                         now: float = 0.0) -> list[LocalAppRow]:
  entries = meta or {}
  rows = []
  for grant in grants:
    if not isinstance(grant, dict):
      continue
    app_id = grant.get("app_id")
    if not isinstance(app_id, str) or not app_id:
      continue
    entry = entries.get(app_id)
    entry = entry if isinstance(entry, Mapping) else None
    rows.append(LocalAppRow(app_id, _title(app_id, grant, entry),
                            f"{last_seen_text(entry, now)}"))
  return rows[:MAX_LOCAL_APP_ROWS]
