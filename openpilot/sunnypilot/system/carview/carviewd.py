#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

carview test server: a page for the car's own browser, fed live from the comma.

It serves static/index.html on the local network and streams a small snapshot of the car's state to it as server-sent
events. Every few seconds the page posts back what it measured (frame rate, WebGL, how steadily the data arrives), and
each report is logged with the car's state at that moment, so one drive shows whether the car's browser keeps drawing
and receiving while in Drive. It only reads messages and serves HTTP: it can't affect driving, and selfdrived ignores it
if it dies. It runs only while the enabled file in carview_root() exists.
"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from collections.abc import Callable

from openpilot.common.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog

PORT = 8099
SEND_HZ = 20
MAX_STREAMS = 4  # page reloads leave old streams open until their socket errors out
MAX_REPORT_BYTES = 16_384
STATS_MAX_BYTES = 5_000_000  # the log rolls over to stats.jsonl.1 past this
STATIC_DIR = Path(__file__).parent / "static"
# the only files served, by URL path
STATIC_FILES = {
  "/": ("index.html", "text/html; charset=utf-8"),
  "/index.html": ("index.html", "text/html; charset=utf-8"),
  "/garage": ("garage.html", "text/html; charset=utf-8"),
  "/cars.js": ("cars.js", "text/javascript; charset=utf-8"),
}


def carview_root() -> Path:
  return Path(Paths.log_root()).parent / "carview"


def enabled_path() -> Path:
  return carview_root() / "enabled"


def stats_path() -> Path:
  return carview_root() / "stats.jsonl"


class CarSnapshot:
  """The latest car state as a plain dict, refreshed from messaging on a background thread."""

  def __init__(self):
    from openpilot.cereal import messaging
    self.sm = messaging.SubMaster(['carState', 'selfdriveState', 'selfdriveStateSP'])
    self.lock = threading.Lock()
    self.state: dict = {}
    threading.Thread(target=self._run, daemon=True).start()

  def _run(self) -> None:
    while True:
      self.sm.update(0)
      cs, ss, sp = self.sm['carState'], self.sm['selfdriveState'], self.sm['selfdriveStateSP']
      state = {
        'vEgo': round(cs.vEgo, 2), 'gear': str(cs.gearShifter), 'standstill': cs.standstill,
        'vCruise': round(cs.vCruiseCluster, 1), 'leftBlinker': cs.leftBlinker, 'rightBlinker': cs.rightBlinker,
        'engaged': ss.enabled, 'mads': sp.mads.enabled, 'state': str(ss.state), 'alert': ss.alertText1,
        'carStateAlive': self.sm.alive['carState'],
      }
      with self.lock:
        self.state = state
      time.sleep(1. / SEND_HZ)

  def __call__(self) -> dict:
    with self.lock:
      return dict(self.state)


def wall_ms() -> int:
  # wall clock on purpose: reports are lined up afterwards with the drive's own logs
  return int(time.time() * 1000)  # noqa: TID251


def append_report(path: Path, record: dict, max_bytes: int = STATS_MAX_BYTES) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  if path.exists() and path.stat().st_size > max_bytes:
    path.replace(path.with_name(path.name + ".1"))
  with open(path, "a") as f:
    f.write(json.dumps(record, separators=(",", ":")) + "\n")


def make_handler(snapshot: Callable[[], dict], log_path: Path, send_hz: float = SEND_HZ):
  streams = threading.BoundedSemaphore(MAX_STREAMS)
  seq_lock, seq = threading.Lock(), [0]

  class Handler(BaseHTTPRequestHandler):
    server_version = "carview"

    def log_message(self, *args) -> None:  # no stderr line per request
      pass

    def _send(self, code: int, body: bytes, content_type: str) -> None:
      self.send_response(code)
      self.send_header("Content-Type", content_type)
      self.send_header("Content-Length", str(len(body)))
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(body)

    def do_GET(self) -> None:
      path = self.path.split("?", 1)[0]
      if path in STATIC_FILES:
        name, content_type = STATIC_FILES[path]
        self._send(200, (STATIC_DIR / name).read_bytes(), content_type)
      elif path == "/events":
        self._stream()
      elif path == "/state.json":
        self._send(200, json.dumps(snapshot()).encode(), "application/json")
      else:
        self._send(404, b"not found", "text/plain")

    def _stream(self) -> None:
      if not streams.acquire(blocking=False):
        self._send(503, b"too many streams", "text/plain")
        return
      try:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(b"retry: 1000\n\n")
        while True:
          with seq_lock:
            seq[0] += 1
            n = seq[0]
          msg = {'n': n, 'ts': wall_ms(), **snapshot()}
          self.wfile.write(b"data: " + json.dumps(msg, separators=(",", ":")).encode() + b"\n\n")
          self.wfile.flush()
          time.sleep(1. / send_hz)
      except OSError:  # the page went away: broken pipe, reset or timeout
        pass
      finally:
        streams.release()

    def do_POST(self) -> None:
      if self.path.split("?", 1)[0] != "/report":
        self._send(404, b"not found", "text/plain")
        return
      length = int(self.headers.get("Content-Length") or 0)
      if length <= 0 or length > MAX_REPORT_BYTES:
        self._send(413, b"bad length", "text/plain")
        return
      try:
        page = json.loads(self.rfile.read(length))
        if not isinstance(page, dict):
          raise ValueError("not an object")
      except ValueError:
        self._send(400, b"bad json", "text/plain")
        return
      server_ms = wall_ms()
      append_report(log_path, {'serverTime': server_ms, 'client': self.client_address[0], 'car': snapshot(), 'page': page})
      self._send(200, json.dumps({'serverTime': server_ms}).encode(), "application/json")

  return Handler


class CarviewServer(ThreadingHTTPServer):
  daemon_threads = True

  def handle_error(self, request, client_address) -> None:
    # a browser dropping an idle keep-alive connection is normal, anything else goes to the log instead of stderr
    if not isinstance(sys.exc_info()[1], (ConnectionError, TimeoutError)):
      cloudlog.exception(f"carviewd: request from {client_address[0]} failed")


def make_server(snapshot: Callable[[], dict], log_path: Path, host: str = "0.0.0.0", port: int = PORT,
                send_hz: float = SEND_HZ) -> ThreadingHTTPServer:
  return CarviewServer((host, port), make_handler(snapshot, log_path, send_hz))


def main() -> None:
  os.nice(15)  # well below the driving processes
  server = make_server(CarSnapshot(), stats_path())
  cloudlog.warning(f"carviewd serving on port {PORT}")
  server.serve_forever()


if __name__ == "__main__":
  main()
