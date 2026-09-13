"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, UTC
from typing import Any
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

SUNNYLINK_LOCAL_UDP_PORT = 53133
SUNNYLINK_LOCAL_WS_PORT = 8443

LOCAL_APPS_KEY = "SunnylinkLocalApps"
PAIRING_CODE_KEY = "SunnylinkLocalPairingCode"
PAIRING_REQUEST_KEY = "SunnylinkLocalPairingRequest"
DISCOVERED_APP_KEY = "SunnylinkLocalDiscoveredApp"

PAIRING_CODE_LENGTH = 6
PAIRING_CODE_ALPHABET = "0123456789"
DEFAULT_CODE_ROTATION_S = 10 * 60  # re-roll the displayed code every 10 min
PAIRING_WINDOW_S = 5 * 60

BEACON_PREFIX = "SUNNYLINK1"


@dataclass
class LocalApp:
  """One app paired with this device (the app runs the local "backend")."""
  app_id: str
  endpoint: str
  app_name: str = ""
  alias: str = ""
  paired_at: int = 0  # epoch seconds

  @staticmethod
  def from_dict(data: dict[str, Any]) -> LocalApp:
    return LocalApp(
      app_id=str(data.get("app_id", "")),
      endpoint=str(data.get("endpoint", "")),
      app_name=str(data.get("app_name", "")),
      alias=str(data.get("alias", "")),
      paired_at=int(data.get("paired_at") or 0),
    )


def local_app_display_name(app: LocalApp) -> str:
  return app.alias or app.app_name or app.app_id


def is_locally_paired(params: Params | None = None) -> bool:
  return len(get_local_apps(params)) > 0


def get_local_apps(params: Params | None = None) -> list[LocalApp]:
  """The paired-app registry (a JSON list persisted in `SunnylinkLocalApps`)."""
  params = params or Params()
  data = params.get(LOCAL_APPS_KEY)
  if not isinstance(data, list):
    return []
  return [LocalApp.from_dict(item) for item in data if isinstance(item, dict) and item.get("app_id")]


def _save_local_apps(apps: list[LocalApp], params: Params | None = None) -> None:
  params = params or Params()
  if apps:
    params.put(LOCAL_APPS_KEY, [asdict(app) for app in apps], block=True)
  else:
    params.remove(LOCAL_APPS_KEY)


def add_local_app(app: LocalApp, params: Params | None = None) -> None:
  """Append (or update by app_id) and persist."""
  if not app.paired_at:
    app.paired_at = int(datetime.now(UTC).replace(tzinfo=None).timestamp())
  apps = [existing for existing in get_local_apps(params) if existing.app_id != app.app_id]
  apps.append(app)
  _save_local_apps(apps, params)
  cloudlog.event("local_pairing.app_paired", app_id=app.app_id, endpoint=app.endpoint)


def update_local_app_endpoint(app_id: str, endpoint: str, params: Params | None = None) -> bool:
  """Refresh a PAIRED app's cached endpoint from its beacon."""
  apps = get_local_apps(params)
  for i, app in enumerate(apps):
    if app.app_id != app_id or app.endpoint == endpoint:
      continue
    apps[i] = LocalApp(app_id=app.app_id, endpoint=endpoint,
                       app_name=app.app_name, alias=app.alias, paired_at=app.paired_at)
    _save_local_apps(apps, params)
    cloudlog.event("local_pairing.app_endpoint_refreshed", app_id=app_id, endpoint=endpoint)
    return True
  return False


def set_local_app_alias(app_id: str, alias: str, params: Params | None = None) -> bool:
  apps = get_local_apps(params)
  for i, app in enumerate(apps):
    if app.app_id != app_id:
      continue
    if app.alias == alias:
      return False
    apps[i] = LocalApp(app_id=app.app_id, endpoint=app.endpoint,
                       app_name=app.app_name, alias=alias, paired_at=app.paired_at)
    _save_local_apps(apps, params)
    cloudlog.event("local_pairing.app_alias_updated", app_id=app_id, alias=alias)
    return True
  return False


def remove_local_app(app_id: str, params: Params | None = None) -> bool:
  """Unpair an app by id. Returns True when an app was removed."""
  apps = get_local_apps(params)
  remaining = [app for app in apps if app.app_id != app_id]
  if len(remaining) == len(apps):
    return False
  _save_local_apps(remaining, params)
  cloudlog.event("local_pairing.app_unpaired", app_id=app_id)
  return True


def remove_all_local_apps(params: Params | None = None) -> None:
  """Unpair every app."""
  _save_local_apps([], params)
  cloudlog.event("local_pairing.all_apps_unpaired")


def generate_pairing_code() -> str:
  """A 6-digit numeric pairing code."""
  return "".join(secrets.choice(PAIRING_CODE_ALPHABET) for _ in range(PAIRING_CODE_LENGTH))


def _write_pairing_code(code: str, params: Params) -> None:
  """Persist the code with its armed-at monotonic timestamp — the window is derived from it."""
  params.put(PAIRING_CODE_KEY, {"code": code, "ts": int(time.monotonic())}, block=True)


def read_pairing_code(params: Params | None = None) -> str | None:
  """The stored pairing code, or None when cleared / not yet generated."""
  params = params or Params()
  data = params.get(PAIRING_CODE_KEY)
  if not isinstance(data, dict):
    return None
  code = data.get("code")
  return str(code) if code else None


def get_pairing_code(params: Params | None = None) -> str:
  """The displayed pairing code, generating and persisting one on first use."""
  params = params or Params()
  code = read_pairing_code(params)
  if code is None:
    code = generate_pairing_code()
    _write_pairing_code(code, params)
  return code


def pairing_requested(params: Params | None = None) -> bool:
  """True while the pairing window is armed and fresh.

  Self-expiring: if the code (which carries the armed-at timestamp) is missing
  or older than PAIRING_WINDOW_S, the flag is dropped here."""
  params = params or Params()
  if not params.get_bool(PAIRING_REQUEST_KEY):
    return False
  data = params.get(PAIRING_CODE_KEY)
  ts = data.get("ts") if isinstance(data, dict) else None
  if not isinstance(ts, (int, float)):
    clear_pairing_request(params)
    return False
  age = time.monotonic() - ts
  # Negative age = armed before the last reboot (monotonic restarts at boot).
  if age < 0 or age > PAIRING_WINDOW_S:
    clear_pairing_request(params)
    return False
  return True


def arm_pairing(params: Params | None = None) -> str:
  """Arm a pairing window and return the code for the app.

  Rolls a fresh code first, then sets the flag, so pairing_requested never
  sees an armed flag without a valid code."""
  params = params or Params()
  code = generate_pairing_code()
  _write_pairing_code(code, params)
  params.put_bool(PAIRING_REQUEST_KEY, True, block=True)
  return code


def clear_pairing_request(params: Params | None = None) -> None:
  """Close the pairing window: drop the request flag and the code together."""
  params = params or Params()
  params.remove(PAIRING_REQUEST_KEY)
  params.remove(PAIRING_CODE_KEY)


def verify_pairing_code(code: str, params: Params | None = None) -> bool:
  """Constant-time check of a code typed into the app against the displayed one."""
  params = params or Params()
  current = read_pairing_code(params)
  if current is None:
    return False
  return secrets.compare_digest(str(code).strip().upper(), current)


class PairingCodeRotator(threading.Thread):
  """Re-roll the displayed code while a pairing window is armed; clear it
  otherwise — the code is never generated outside a window."""

  def __init__(self, params: Params | None = None, rotation_s: float = DEFAULT_CODE_ROTATION_S,
               stop_event: threading.Event | None = None, tick_cb: Callable[[], None] | None = None):
    super().__init__(name="local_pairing_code_rotator", daemon=True)
    self.params = params or Params()
    self.rotation_s = rotation_s
    self.stop_event = stop_event or threading.Event()
    # Test seam: invoked once per loop iteration after state is updated.
    self.tick_cb = tick_cb

  def rotate(self) -> None:
    """Re-roll the code while the window is armed, clear it otherwise."""
    if pairing_requested(self.params):
      _write_pairing_code(generate_pairing_code(), self.params)
    else:
      self.params.remove(PAIRING_CODE_KEY)

  def run(self) -> None:
    self.rotate()
    while not self.stop_event.wait(self.rotation_s):
      try:
        self.rotate()
        if self.tick_cb is not None:
          self.tick_cb()
      except Exception:
        cloudlog.exception("local_pairing.code_rotator.exception")


def format_endpoint(host: str, ws_port: int = SUNNYLINK_LOCAL_WS_PORT) -> str:
  return f"ws://{host}:{ws_port}"


def local_identity(params: Params | None = None) -> str:
  """Identity claim on local connections. DongleId always exists on comma
  hardware (SunnylinkDongleId is "UnregisteredDevice" until cloud
  registration) and is what the app matches against the backend device list
  to dedupe cloud + local entries."""
  params = params or Params()
  return params.get("DongleId") or params.get("HardwareSerial") or ""
