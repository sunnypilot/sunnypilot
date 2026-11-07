from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass

from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.sunnylink.athena.local_state import (
  BEACON_PREFIX,
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
  def __init__(self, port: int = SUNNYLINK_LOCAL_UDP_PORT, sock: socket.socket | None = None):
    super().__init__(name="local_discovery_listener", daemon=True)
    self.port = port
    self._sock = sock
    self._recent: dict[str, tuple[float, str]] = {}
    self._recent_lock = threading.Lock()
    self._stop_event = threading.Event()

  def stop(self) -> None:
    self._stop_event.set()
    if self._sock is not None:
      try:
        self._sock.close()
      except OSError:
        pass

  def fresh_peers(self, max_age_s: float = LOCAL_BEACON_FRESH_S) -> list[tuple[str, str]]:
    now = time.monotonic()
    with self._recent_lock:
      self._recent = {e: v for e, v in self._recent.items() if now - v[0] <= max_age_s}
      return [(e, app_id) for e, (_, app_id) in sorted(self._recent.items(), key=lambda kv: kv[1][0], reverse=True)]

  def fresh_endpoints(self, max_age_s: float = LOCAL_BEACON_FRESH_S) -> list[str]:
    return [endpoint for endpoint, _ in self.fresh_peers(max_age_s)]

  def _handle(self, raw: bytes, source_ip: str) -> None:
    beacon = parse_beacon(raw, source_ip)
    if beacon is None:
      return
    with self._recent_lock:
      self._recent[beacon.endpoint] = (time.monotonic(), beacon.app_id)
    cloudlog.debug(f"local_discovery.app_found {beacon.app_id} at {beacon.endpoint}")

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
