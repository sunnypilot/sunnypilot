#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

carview: a driving view for the car's own browser, fed live from the comma.

It serves static/index.html (the view; /test is the original browser test) on the local network and streams the car,
the model's road and path, leads, alerts and cues to it as server-sent events. Every few seconds the page posts back what
it measured (frame rate, WebGL, how steadily the data arrives), and each report is logged with the car's state at that
moment, so a drive shows how well the car's browser kept up. It only reads messages and serves HTTP: it can't affect
driving, and selfdrived ignores it if it dies. It runs only while the enabled file in carview_root() exists.

The car's browser refuses private addresses, so the car joins the comma's own hotspot and opens http://3.3.3.3:8099
(see Hotspot).
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
  "/test": ("test.html", "text/html; charset=utf-8"),
  "/garage": ("garage.html", "text/html; charset=utf-8"),
  "/cars.js": ("cars.js", "text/javascript; charset=utf-8"),
  "/view.js": ("view.js", "text/javascript; charset=utf-8"),
}


def carview_root() -> Path:
  return Path(Paths.log_root()).parent / "carview"


def enabled_path() -> Path:
  return carview_root() / "enabled"


def stats_path() -> Path:
  return carview_root() / "stats.jsonl"


SERVICES = ['carState', 'selfdriveState', 'selfdriveStateSP', 'modelV2', 'radarState', 'longitudinalPlanSP',
            'navInstruction', 'modelDataV2SP']


def _r(xs, places: int = 2) -> list[float]:
  return [round(float(v), places) for v in xs]


def view_state(sm) -> dict:
  """What the page draws, from the latest messages: the car, the model's road and path, leads, alerts and cues."""
  cs, ss, sp = sm['carState'], sm['selfdriveState'], sm['selfdriveStateSP']
  state = {
    'vEgo': round(cs.vEgo, 2), 'gear': str(cs.gearShifter), 'standstill': cs.standstill,
    'vCruise': round(cs.vCruiseCluster, 1), 'leftBlinker': cs.leftBlinker, 'rightBlinker': cs.rightBlinker,
    'leftBlindspot': cs.leftBlindspot, 'rightBlindspot': cs.rightBlindspot, 'steeringAngle': round(cs.steeringAngleDeg, 1),
    'engaged': ss.enabled, 'mads': sp.mads.enabled, 'state': str(ss.state),
    'alert': ss.alertText1, 'alert2': ss.alertText2, 'alertStatus': str(ss.alertStatus),
    'carStateAlive': sm.alive['carState'],
  }

  # the model's road in its own frame: x forward, y right, z down, metres from the camera
  m = sm['modelV2']
  if sm.alive['modelV2'] and len(m.position.x):
    state['model'] = {
      'path': [_r(m.position.x), _r(m.position.y), _r(m.position.z)],
      'lineX': _r(m.laneLines[0].x, 1) if len(m.laneLines) else [],
      'lines': [[_r(line.y), _r(line.z)] for line in m.laneLines],
      'lineProbs': _r(m.laneLineProbs),
      'edges': [[_r(edge.y), _r(edge.z)] for edge in m.roadEdges],
      'edgeStds': _r(m.roadEdgeStds),
    }

  # leads: dRel from our front bumper, yRel positive to the left
  rs = sm['radarState']
  state['leads'] = [{'d': round(lead.dRel, 1), 'y': round(lead.yRel, 2), 'v': round(lead.vLead, 1), 'a': round(lead.aLeadK, 2)}
                    for lead in (rs.leadOne, rs.leadTwo) if sm.alive['radarState'] and lead.present]

  resolver = sm['longitudinalPlanSP'].speedLimit.resolver
  state['speedLimit'] = round(resolver.speedLimit, 2) if resolver.speedLimitValid else 0.

  nav = sm['navInstruction']
  if sm.alive['navInstruction'] and nav.maneuverPrimaryText:
    state['nav'] = {'primary': nav.maneuverPrimaryText, 'secondary': nav.maneuverSecondaryText, 'distance': round(nav.maneuverDistance),
                    'type': nav.maneuverType, 'modifier': nav.maneuverModifier, 'timeRemaining': round(nav.timeRemaining),
                    'distanceRemaining': round(nav.distanceRemaining)}

  md = sm['modelDataV2SP']
  state['turn'] = {'direction': str(md.laneTurnDirection), 'action': round(md.actionCurvature, 4), 'plan': round(md.turnPlanCurvature, 4)}
  return state


class CarSnapshot:
  """The latest view state as a plain dict, refreshed from messaging on a background thread."""

  def __init__(self):
    from openpilot.cereal import messaging
    self.sm = messaging.SubMaster(SERVICES)
    self.lock = threading.Lock()
    self.state: dict = {}
    threading.Thread(target=self._run, daemon=True).start()

  def _run(self) -> None:
    while True:
      self.sm.update(0)
      try:
        state = view_state(self.sm)
      except Exception:
        cloudlog.exception("carviewd: building the view state failed")
        state = {}
      with self.lock:
        self.state = state
      time.sleep(1. / SEND_HZ)

  def __call__(self) -> dict:
    with self.lock:
      return dict(self.state)


TETHER_ADDRESS = "192.168.43.1"  # the comma's own hotspot
CAR_ADDRESS = "3.3.3.3"  # the car's browser refuses private addresses, so on the comma's hotspot the page is also here
HOTSPOT_CHECK_S = 5.


class Hotspot:
  """While the comma's hotspot is on: answer at CAR_ADDRESS, and share the comma's internet with the hotspot.

  NetworkManager tries to share it itself, but with an iptables that this kernel can't run, so the hotspot has no
  internet and a car joining it drops it again. iptables-legacy works. Off the hotspot, CAR_ADDRESS is taken away again so
  it never hides the real host of that address.
  """

  def __init__(self, run: Callable[[list[str]], tuple[int, str]]):
    self.run = run

  def tethering(self) -> bool:
    return f"inet {TETHER_ADDRESS}/" in self.run(["ip", "-4", "-o", "addr", "show"])[1]

  def has_car_address(self) -> bool:
    return f"inet {CAR_ADDRESS}/32" in self.run(["ip", "-4", "-o", "addr", "show", "dev", "lo"])[1]

  def uplink(self) -> str | None:
    words = self.run(["ip", "route", "show", "default"])[1].split()
    return words[words.index("dev") + 1] if "dev" in words[:-1] else None

  def update(self) -> None:
    on = self.tethering()
    if on and not self.has_car_address():
      self.run(["sudo", "-n", "ip", "addr", "add", f"{CAR_ADDRESS}/32", "dev", "lo"])
    elif not on and self.has_car_address():
      self.run(["sudo", "-n", "ip", "addr", "del", f"{CAR_ADDRESS}/32", "dev", "lo"])
    if on and (dev := self.uplink()):
      rule = ["POSTROUTING", "-s", f"{TETHER_ADDRESS.rsplit('.', 1)[0]}.0/24", "-o", dev, "-j", "MASQUERADE"]
      if self.run(["sudo", "-n", "iptables-legacy", "-t", "nat", "-C", *rule])[0] != 0:
        self.run(["sudo", "-n", "iptables-legacy", "-t", "nat", "-A", *rule])
      # NetworkManager doesn't always switch forwarding on either, and without it the rule above passes nothing. Read
      # from /proc: manager starts carviewd with no PATH, and sysctl is in /usr/sbin (sudo has its own search path)
      if self.run(["cat", "/proc/sys/net/ipv4/ip_forward"])[1].strip() != "1":
        self.run(["sudo", "-n", "sysctl", "-w", "net.ipv4.ip_forward=1"])


def run_command(cmd: list[str]) -> tuple[int, str]:
  import subprocess
  try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return p.returncode, p.stdout
  except (OSError, subprocess.TimeoutExpired):
    return 1, ""


def keep_hotspot(hotspot: Hotspot) -> None:
  while True:
    try:
      hotspot.update()
    except Exception:
      cloudlog.exception("carviewd: hotspot setup failed")
    time.sleep(HOTSPOT_CHECK_S)


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
      car = {k: v for k, v in snapshot().items() if k != 'model'}  # the road geometry would make the log 10x bigger
      append_report(log_path, {'serverTime': server_ms, 'client': self.client_address[0], 'car': car, 'page': page})
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
  from openpilot.common.hardware import COMMA_HARDWARE
  os.nice(15)  # well below the driving processes
  if COMMA_HARDWARE:
    threading.Thread(target=keep_hotspot, args=(Hotspot(run_command),), daemon=True).start()
  server = make_server(CarSnapshot(), stats_path())
  cloudlog.warning(f"carviewd serving on port {PORT}")
  server.serve_forever()


if __name__ == "__main__":
  main()
