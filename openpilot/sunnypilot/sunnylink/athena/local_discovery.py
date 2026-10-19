"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Passive discovery of the sunnylink app on this network.

The app broadcasts a beacon every few seconds; this listener records every endpoint it hears and
keeps the freshest one visible to the settings UI while a pairing window is open. A beacon carries
no key material and no capability — it is a locator, and identity is decided by the pinned TLS dial
that follows (`local_auth.py`), so a forged or replayed beacon changes nothing.
"""
from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.sunnylink.athena.local_state import (
  BEACON_PREFIX,
  DISCOVERED_APP_KEY,
  PAIRING_REQUEST_KEY,
  SUNNYLINK_LOCAL_UDP_PORT,
  format_endpoint,
)

LOCAL_BEACON_FRESH_S = 30


@dataclass
class AppBeacon:
  """A parsed app beacon — the app announcing it is acting as the local backend."""
  app_id: str
  ws_port: int
  source_ip: str

  @property
  def endpoint(self) -> str:
    return format_endpoint(self.source_ip, self.ws_port)


def parse_beacon(raw: str | bytes, source_ip: str = "") -> AppBeacon | None:
  """
  Parse one UDP beacon line from the app.

  Wire format: `SUNNYLINK1 {"v":1,"role":"app","app_id":"<uuid>","ws_port":8443}`
  Returns None for anything else. Beacons carry ids + addresses only — no secrets.
  """
  if isinstance(raw, bytes):
    raw = raw.decode("utf-8", errors="replace")
  raw = raw.strip()
  if not raw.startswith(BEACON_PREFIX + " "):
    return None
  try:
    data = json.loads(raw[len(BEACON_PREFIX) + 1:])
  except ValueError:
    return None
  if not isinstance(data, dict):
    return None
  if data.get("role") != "app" or data.get("v") != 1:
    return None
  app_id = data.get("app_id")
  ws_port = data.get("ws_port")
  if not isinstance(app_id, str) or not app_id:
    return None
  if not isinstance(ws_port, int) or not (0 < ws_port <= 65535):
    return None
  return AppBeacon(app_id=app_id, ws_port=ws_port, source_ip=source_ip)


class LocalDiscovery(threading.Thread):
  """Passive UDP listener.

  - Every beacon heard recently is kept as an endpoint a pinned dial may target, keyed by address
    because the dial's job is exactly "can I reach the phone at this address?".
  - While a pairing window is open, the freshest one is mirrored into a status param so the
    settings UI can show that the phone is there.

  IPs are not identity: the app moves between networks, so a new address is simply a new endpoint,
  and the key it proves over TLS is what decides whether the session is allowed.
  """

  def __init__(self, params: Params | None = None, port: int = SUNNYLINK_LOCAL_UDP_PORT,
               sock: socket.socket | None = None, write_interval_s: float = 5.0,
               pairing_window_cb: Callable[[], bool] | None = None):
    super().__init__(name="local_discovery_listener", daemon=True)
    self.params = params or Params()
    self.port = port
    self._sock = sock
    # A window the daemon holds is not visible as a param read the UI can do, so the status line
    # needs to see both.
    self.pairing_window_cb = pairing_window_cb
    self._latest_endpoint: str | None = None
    self._latest_app_id: str | None = None
    self._last_seen_monotonic: float = 0.0
    # Every beacon heard recently, keyed by endpoint: a dial finds its phone by TLS key, not by
    # app_id, so it cannot rely on the pairing-window trackers above.
    self._recent_beacons: dict[str, tuple[str, float]] = {}
    self._recent_lock = threading.Lock()
    self._lock = threading.Lock()
    self._stop_event = threading.Event()
    self.write_interval_s = write_interval_s
    self._last_write_monotonic = 0.0
    self._last_written_endpoint: str | None = None
    self._last_written_app_id: str | None = None
    self._discovered_cleared = False

  def stop(self) -> None:
    self._stop_event.set()
    if self._sock is not None:
      try:
        self._sock.close()
      except OSError:
        pass

  def latest_endpoint(self) -> str | None:
    """The most recently announced app endpoint (None outside a pairing window)."""
    with self._lock:
      return self._latest_endpoint

  def latest_app_id(self) -> str | None:
    """The app_id of the most recently announced beacon (None outside a window)."""
    with self._lock:
      return self._latest_app_id

  def last_seen_ago(self) -> float | None:
    """Seconds since the last app beacon was heard (None when none heard yet)."""
    with self._lock:
      if self._last_seen_monotonic == 0.0:
        return None
      return time.monotonic() - self._last_seen_monotonic

  def fresh_endpoints(self, max_age_s: float = LOCAL_BEACON_FRESH_S) -> list[str]:
    """Endpoints of every beacon heard within max_age_s, freshest first."""
    now = time.monotonic()
    with self._recent_lock:
      self._recent_beacons = {endpoint: entry for endpoint, entry in self._recent_beacons.items()
                              if now - entry[1] <= max_age_s}
      recent = sorted(self._recent_beacons.items(), key=lambda item: item[1][1], reverse=True)
    return [endpoint for endpoint, _ in recent]

  def _record_beacon(self, beacon: AppBeacon) -> None:
    with self._recent_lock:
      self._recent_beacons[beacon.endpoint] = (beacon.app_id, time.monotonic())

  def _pairing_window_open(self) -> bool:
    """True while the settings UI asked for a window, or the daemon is displaying one."""
    if self.params.get_bool(PAIRING_REQUEST_KEY):
      return True
    callback = self.pairing_window_cb
    if callback is None:
      return False
    try:
      return bool(callback())
    except Exception:
      cloudlog.exception("local_discovery.pairing_window_cb.exception")
      return False

  def _handle(self, raw: bytes, source_ip: str) -> None:
    beacon = parse_beacon(raw, source_ip)
    if beacon is None:
      return
    self._record_beacon(beacon)
    if self._pairing_window_open():
      with self._lock:
        self._latest_endpoint = beacon.endpoint
        self._latest_app_id = beacon.app_id
        self._last_seen_monotonic = time.monotonic()
      self._write_discovered_param(beacon)
      cloudlog.debug(f"local_discovery.app_found {beacon.app_id} at {beacon.endpoint}")
    else:
      with self._lock:
        self._latest_endpoint = None
        self._latest_app_id = None
        self._last_seen_monotonic = 0.0
      self._clear_discovered_param()

  def _clear_discovered_param(self) -> None:
    if self._discovered_cleared:
      return
    self._discovered_cleared = True
    try:
      self.params.remove(DISCOVERED_APP_KEY)
    except Exception:
      cloudlog.exception("local_discovery.param_clear.exception")

  def _write_discovered_param(self, beacon: AppBeacon) -> None:
    """Mirror the freshest beacon into a param the settings UI can read."""
    now = time.monotonic()
    changed = beacon.endpoint != self._last_written_endpoint or beacon.app_id != self._last_written_app_id
    if not changed and now - self._last_write_monotonic < self.write_interval_s:
      return
    self._last_write_monotonic = now
    self._last_written_endpoint = beacon.endpoint
    self._last_written_app_id = beacon.app_id
    self._discovered_cleared = False
    payload = {
      "endpoint": beacon.endpoint,
      "app_id": beacon.app_id,
      "ts": int(time.monotonic()),
    }
    try:
      self.params.put(DISCOVERED_APP_KEY, payload, block=True)
    except Exception:
      cloudlog.exception("local_discovery.param_write.exception")

  def _bind(self) -> socket.socket:
    if self._sock is not None:
      return self._sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", self.port))
    sock.settimeout(0.5)
    return sock

  def run(self) -> None:
    sock = self._bind()
    try:
      while not self._stop_event.is_set():
        try:
          data, addr = sock.recvfrom(4096)
          self._handle(data, addr[0] if len(addr) > 0 else "")
        except TimeoutError:
          continue
        except OSError:
          # Socket closed by stop() — exit quietly.
          if self._stop_event.is_set():
            break
          cloudlog.exception("local_discovery.recv.exception")
          break
    finally:
      try:
        sock.close()
      except OSError:
        pass


def latest_discovered_app(params: Params | None = None,
                          fresh_s: float = LOCAL_BEACON_FRESH_S) -> tuple[str, int] | None:
  params = params or Params()
  data = params.get(DISCOVERED_APP_KEY)
  if not isinstance(data, dict):
    return None
  endpoint = str(data.get("endpoint", ""))
  try:
    ts = int(data.get("ts") or 0)
  except (ValueError, TypeError):
    return None
  if not endpoint or ts <= 0:
    return None
  age = time.monotonic() - ts
  # Negative age = written before the last reboot (monotonic restarts at boot).
  if age < 0 or age > fresh_s:
    return None
  return endpoint, max(0, int(age))
