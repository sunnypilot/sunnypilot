from __future__ import annotations

import json
import socket
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

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
  app_id: str
  ws_port: int
  source_ip: str

  @property
  def endpoint(self) -> str:
    return format_endpoint(self.source_ip, self.ws_port)


def parse_beacon(raw: str | bytes, source_ip: str = "") -> AppBeacon | None:
  if isinstance(raw, bytes):
    raw = raw.decode("utf-8", errors="replace")
  raw = raw.strip()
  if not raw.startswith(BEACON_PREFIX + " "):
    return None
  try:
    data = json.loads(raw[len(BEACON_PREFIX) + 1:])
  except ValueError:
    return None
  if not isinstance(data, dict) or data.get("role") != "app" or data.get("v") != 1:
    return None
  app_id, ws_port = data.get("app_id"), data.get("ws_port")
  if not isinstance(app_id, str) or not app_id or not isinstance(ws_port, int) or not 0 < ws_port <= 65535:
    return None
  return AppBeacon(app_id=app_id, ws_port=ws_port, source_ip=source_ip)


class LocalDiscovery(threading.Thread):
  def __init__(self, params: Params | None = None, port: int = SUNNYLINK_LOCAL_UDP_PORT,
               sock: socket.socket | None = None, write_interval_s: float = 5.0,
               pairing_window_cb: Callable[[], bool] | None = None):
    super().__init__(name="local_discovery_listener", daemon=True)
    self.params = params or Params()
    self.port = port
    self._sock = sock
    self.pairing_window_cb = pairing_window_cb
    self._recent: dict[str, float] = {}
    self._recent_lock = threading.Lock()
    self._stop_event = threading.Event()
    self.write_interval_s = write_interval_s
    self._last_write: tuple[str, str, float] | None = None
    self._discovered_cleared = False

  def stop(self) -> None:
    self._stop_event.set()
    if self._sock is not None:
      try:
        self._sock.close()
      except OSError:
        pass

  def fresh_endpoints(self, max_age_s: float = LOCAL_BEACON_FRESH_S) -> list[str]:
    now = time.monotonic()
    with self._recent_lock:
      self._recent = {e: seen for e, seen in self._recent.items() if now - seen <= max_age_s}
      return sorted(self._recent, key=lambda e: self._recent[e], reverse=True)

  def _pairing_window_open(self) -> bool:
    try:
      if self.params.get_bool(PAIRING_REQUEST_KEY):
        return True
      return bool(self.pairing_window_cb and self.pairing_window_cb())
    except Exception:
      cloudlog.exception("local_discovery.pairing_window.exception")
      return False

  def _handle(self, raw: bytes, source_ip: str) -> None:
    beacon = parse_beacon(raw, source_ip)
    if beacon is None:
      return
    with self._recent_lock:
      self._recent[beacon.endpoint] = time.monotonic()
    if not self._pairing_window_open():
      self._sync_param(None)
      return
    self._sync_param(beacon)
    cloudlog.debug(f"local_discovery.app_found {beacon.app_id} at {beacon.endpoint}")

  def _sync_param(self, beacon: AppBeacon | None) -> None:
    if beacon is None:
      if self._discovered_cleared:
        return
      self._discovered_cleared = True
      try:
        self.params.remove(DISCOVERED_APP_KEY)
      except Exception:
        cloudlog.exception("local_discovery.param_clear.exception")
      return
    now = time.monotonic()
    endpoint, app_id, written_at = self._last_write or ("", "", 0.0)
    if (beacon.endpoint, beacon.app_id) == (endpoint, app_id) and now - written_at < self.write_interval_s:
      return
    self._last_write = (beacon.endpoint, beacon.app_id, now)
    self._discovered_cleared = False
    try:
      self.params.put(DISCOVERED_APP_KEY, {"endpoint": beacon.endpoint, "app_id": beacon.app_id, "ts": int(now)}, block=True)
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
  data = (params or Params()).get(DISCOVERED_APP_KEY)
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
  if age < 0 or age > fresh_s:
    return None
  return endpoint, max(0, int(age))


def discovered_status(params: Params | None = None) -> str | None:
  discovered = latest_discovered_app(params)
  if discovered is None:
    return None
  endpoint, age = discovered
  return endpoint if age < 2 else f"{endpoint} ({age}s)"
