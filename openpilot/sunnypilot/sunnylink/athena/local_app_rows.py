"""One row model for the "Local Connections" screen, shared by both UI panels.

Every row is an enrolled phone, so a row's text and its action cannot drift apart between the two
layouts. It reads no Params and no identity key: the panels pass in what they read. Aliases and
last-seen stamps are display metadata only — the authority decides every connection from the grant
itself.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from openpilot.sunnypilot.sunnylink.athena.local_auth import MAX_GRANTS

# Every grant the authority accepts: a phone the screen hides could never be revoked from the
# device.
MAX_LOCAL_APP_ROWS = MAX_GRANTS

DEFAULT_APP_NAME = "sunnylink mobile"

NEVER_CONNECTED = "not connected yet"


@dataclass(frozen=True)
class LocalAppRow:
  """One enrolled phone in the local-connections list."""
  app_id: str
  title: str
  subtitle: str


def short_key(app_id: str, length: int = 10) -> str:
  """A recognizable, privacy-neutral abbreviation of a key id."""
  return app_id if len(app_id) <= length else app_id[:length] + "…"


def format_age(seconds: float) -> str:
  """Human-readable 'how long ago', for the display-only last-seen stamp."""
  if seconds < 60:
    return "just now"
  if seconds < 3600:
    return f"{int(seconds // 60)}m ago"
  if seconds < 86_400:
    return f"{int(seconds // 3600)}h ago"
  return f"{int(seconds // 86_400)}d ago"


def last_seen_text(entry: Mapping[str, object] | None, now: float) -> str:
  """`last_seen` is monotonic, so a stamp from before the last reboot reads as unknown."""
  last_seen = entry.get("last_seen") if isinstance(entry, Mapping) else None
  if not isinstance(last_seen, (int, float)) or isinstance(last_seen, bool):
    return NEVER_CONNECTED
  age = now - float(last_seen)
  if age < 0:
    return NEVER_CONNECTED
  return format_age(age)


def build_local_app_rows(grants: list[dict[str, str]],
                         meta: Mapping[str, Mapping[str, object]] | None = None,
                         now: float = 0.0,
                         max_rows: int = MAX_LOCAL_APP_ROWS) -> list[LocalAppRow]:
  """One row per enrolled phone, in the order the authority holds them."""
  entries = meta or {}
  rows = []
  for grant in grants:
    if not isinstance(grant, dict):
      continue
    app_id = grant.get("app_id")
    app_name = grant.get("app_name")
    if not isinstance(app_id, str) or not app_id:
      continue
    entry = entries.get(app_id)
    alias = entry.get("alias") if isinstance(entry, Mapping) else None
    if isinstance(alias, str) and alias.strip():
      title = alias.strip()
    elif isinstance(app_name, str) and app_name:
      title = app_name
    else:
      title = DEFAULT_APP_NAME
    rows.append(LocalAppRow(app_id, title,
                            f"secure · {short_key(app_id)} · {last_seen_text(entry, now)}"))
  return rows[:max_rows]
