"""Serve Sunnydrive telemetry and comma-side APIs to the phone app."""

import argparse
import functools
import json
import zlib
import math
import os
import re
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from openpilot.cereal import messaging  # noqa: E402
from openpilot.sunnypilot.sunnydrive import pairing  # noqa: E402

SERVICES = ["carState", "selfdriveState", "selfdriveStateSP", "carControl", "gpsLocationExternal", "deviceState", "carParams", "modelV2", "driverMonitoringState", "longitudinalPlanSP", "liveMapDataSP", "extrinsicsCalibration"]
LLM_GET = {"/v1/models", "/api/v0/models"}
LLM_POST = {"/v1/chat/completions"}
SUNNYLINK_WIDGETS = {"toggle", "option", "multiple_button"}   # the setting kinds the app can change
DISCOVERY_PORT = 53134
DISCOVERY_PREFIX = b"SUNNYDRIVE1 "


def fresh(sm, service, seconds=3):
  return sm.seen[service] and time.monotonic() - sm.recv_time[service] < seconds


def finite_values(value):
  if isinstance(value, float):
    return value if math.isfinite(value) else None
  if isinstance(value, dict):
    return {key: finite_values(item) for key, item in value.items()}
  if isinstance(value, list):
    return [finite_values(item) for item in value]
  return value


@functools.lru_cache(maxsize=8)
def road_camera(device_type, rpy, height, wide_from_device=None):
  """A road camera's ground plane (road x forward, y left, 1) -> sensor pixels, so the phone can put its car detections on the road.
  wide_from_device (calibration's wideFromDeviceEuler) selects the wide camera, which sits at a slight angle to the narrow one."""
  import numpy as np
  import openpilot.common.transformations.orientation as orient
  from openpilot.common.transformations.camera import DEVICE_CAMERAS, get_view_frame_from_road_frame, view_frame_from_device_frame
  cameras = DEVICE_CAMERAS.get((device_type, "os04c10" if device_type == "mici" else "ox03c10"))
  if cameras is None:
    return None
  cam = cameras.wide_road if wide_from_device else cameras.narrow_road
  intrinsic = np.array([[cam.focal_length, 0, cam.width / 2], [0, cam.focal_length, cam.height / 2], [0, 0, 1]])
  view_from_road = get_view_frame_from_road_frame(*rpy, height)
  if wide_from_device:   # view <- wide <- device <- road, instead of view <- device <- road
    device_from_view = view_frame_from_device_frame.T
    view_from_road = np.hstack((view_frame_from_device_frame @ orient.rot_from_euler(list(wide_from_device)) @ device_from_view @ view_from_road[:, :3], view_from_road[:, 3:]))
  ground = intrinsic @ view_from_road[:, [0, 1, 3]]
  return {"width": cam.width, "height": cam.height, "focal": cam.focal_length, "ground": [round(float(v), 6) for v in ground.flatten()]}


def snapshot(sm):
  data = {"timestampMs": round(time.time() * 1000), "car": None, "selfdrive": None, "mads": None, "lateral": None, "gps": None, "device": None, "vehicle": None, "model": None, "driverMonitoring": None, "speedLimit": None, "map": None, "dec": None}
  if sm.seen["carParams"]:
    params = sm["carParams"]
    data["vehicle"] = {"brand": params.brand, "fingerprint": params.carFingerprint, "openpilotLongitudinal": params.openpilotLongitudinalControl}
  if fresh(sm, "carState"):
    car = sm["carState"]
    data["car"] = {
      "speedMps": car.vEgo, "clusterSpeedMps": car.vEgoCluster, "accelMps2": car.aEgo,
      "gear": str(car.gearShifter), "standstill": car.standstill,
      "steeringAngleDeg": car.steeringAngleDeg, "steeringPressed": car.steeringPressed,
      "gasPressed": car.gasPressed, "brakePressed": car.brakePressed,
      "parkingBrake": car.parkingBrake, "brakeHold": car.brakeHoldActive,
      "leftBlinker": car.leftBlinker, "rightBlinker": car.rightBlinker,
      "doorOpen": car.doorOpen, "seatbeltUnlatched": car.seatbeltUnlatched,
      "leftBlindspot": car.leftBlindspot, "rightBlindspot": car.rightBlindspot,
      "cruiseEnabled": car.cruiseState.enabled, "cruiseSpeedMps": car.cruiseState.speed,
      "fuelGauge": car.fuelGauge, "charging": car.charging,
      "canValid": car.canValid, "canTimeout": car.canTimeout,
    }
  if fresh(sm, "selfdriveState"):
    state = sm["selfdriveState"]
    data["selfdrive"] = {
      "enabled": state.enabled, "active": state.active, "engageable": state.engageable,
      "state": str(state.state), "experimentalMode": state.experimentalMode,
      "personality": str(state.personality), "alertText1": state.alertText1,
      "alertText2": state.alertText2, "alertStatus": str(state.alertStatus),
    }
  if fresh(sm, "selfdriveStateSP"):
    mads = sm["selfdriveStateSP"].mads
    data["mads"] = {"available": mads.available, "enabled": mads.enabled, "active": mads.active, "state": str(mads.state)}
  if fresh(sm, "carControl"):
    control = sm["carControl"]
    data["lateral"] = {"active": control.latActive, "longitudinalActive": control.longActive, "torque": control.actuators.torque}
  if fresh(sm, "gpsLocationExternal", 5):
    gps = sm["gpsLocationExternal"]
    fix_age_ms = round(time.time() * 1000) - gps.unixTimestampMillis
    if math.isfinite(gps.latitude) and math.isfinite(gps.longitude) and (gps.latitude or gps.longitude) and 0 <= fix_age_ms < 30000:
      data["gps"] = {
        "latitude": gps.latitude, "longitude": gps.longitude,
        "altitudeM": gps.altitude, "speedMps": gps.speed,
        "bearingDeg": gps.bearingDeg, "horizontalAccuracy": gps.horizontalAccuracy,
        "unixTimestampMillis": gps.unixTimestampMillis,
      }
  if fresh(sm, "deviceState", 5):
    device = sm["deviceState"]
    data["device"] = {
      "onroad": device.started, "networkType": str(device.networkType),
      "networkStrength": str(device.networkStrength),
      "freeSpacePercent": device.freeSpacePercent,
    }
  if fresh(sm, "modelV2", 2):
    model = sm["modelV2"]
    def line(points):
      return {"x": list(points.x), "y": list(points.y)}
    data["model"] = {
      "frameId": model.frameId,
      "path": line(model.position),
      "acceleration": list(model.acceleration.x),
      "laneLines": [line(item) for item in model.laneLines],
      "laneLineProbs": list(model.laneLineProbs),
      "roadEdges": [line(item) for item in model.roadEdges],
      "roadEdgeStds": list(model.roadEdgeStds),
      "leads": [{"x": item.x[0], "y": item.y[0], "prob": item.prob, "v": item.v[0] if item.v else None, "a": item.a[0] if item.a else None}
                for item in model.leadsV3 if item.x and item.y],
      "laneChange": {"state": str(model.meta.laneChangeState), "direction": str(model.meta.laneChangeDirection)},
    }
  if fresh(sm, "driverMonitoringState", 3):
    dm = sm["driverMonitoringState"]
    data["driverMonitoring"] = {
      "policy": str(dm.activePolicy), "alertLevel": str(dm.alertLevel),
      "lockout": dm.lockout, "faceDetected": dm.visionPolicyState.faceDetected,
      "distracted": dm.visionPolicyState.isDistracted,
      "awarenessPercent": dm.visionPolicyState.awarenessPercent if str(dm.activePolicy).endswith("vision") else dm.wheeltouchPolicyState.awarenessPercent,
      "driverInteracting": dm.wheeltouchPolicyState.driverInteracting,
    }
  if sm.seen["extrinsicsCalibration"] and sm.seen["deviceState"] and len(sm["extrinsicsCalibration"].rpyCalib) == 3 and len(sm["extrinsicsCalibration"].height):
    calib = sm["extrinsicsCalibration"]
    device, rpy, height = str(sm["deviceState"].deviceType), tuple(round(v, 4) for v in calib.rpyCalib), round(calib.height[0], 3)   # rounded: cached while calibration holds
    data["roadCamera"] = road_camera(device, rpy, height)
    if len(calib.wideFromDeviceEuler) == 3:
      data["wideRoadCamera"] = road_camera(device, rpy, height, tuple(round(v, 4) for v in calib.wideFromDeviceEuler))
  if fresh(sm, "longitudinalPlanSP"):
    plan = sm["longitudinalPlanSP"]
    limit = plan.speedLimit
    data["dec"] = {"enabled": plan.dec.enabled, "active": plan.dec.active, "state": str(plan.dec.state)}
    curves = [(name, item) for name, item in (("vision", plan.smartCruiseControl.vision), ("map", plan.smartCruiseControl.map)) if item.active]
    data["curve"] = {"source": curves[0][0], "vTargetMps": min(item.vTarget for _, item in curves)} if curves else None
    data["speedLimit"] = {
      "valid": limit.resolver.speedLimitValid, "limitMps": limit.resolver.speedLimit, "offsetMps": limit.resolver.speedLimitOffset,
      "source": str(limit.resolver.source), "assist": str(limit.assist.state),
    }
  if fresh(sm, "liveMapDataSP", 5):
    road = sm["liveMapDataSP"]
    data["map"] = {"roadName": road.roadName, "aheadMps": road.speedLimitAhead if road.speedLimitAheadValid else None, "aheadDistanceM": road.speedLimitAheadDistance}
  return finite_values(data)


def _sunnylink_walk(node, found):
  """Every settings item (has key + widget) and every param a rule reads, anywhere in the schema."""
  if isinstance(node, dict):
    if node.get("key") and node.get("widget"):
      found["items"][node["key"]] = node
    if node.get("type") == "param" and node.get("key"):
      found["keys"].add(node["key"])
    for value in node.values():
      _sunnylink_walk(value, found)
  elif isinstance(node, list):
    for value in node:
      _sunnylink_walk(value, found)
  return found


def _setting_has_rule(rule, kind):
  if rule.get("type") == kind:
    return True
  if rule.get("type") == "not":
    return _setting_has_rule(rule["condition"], kind)
  if rule.get("type") in ("any", "all"):
    return any(_setting_has_rule(child, kind) for child in rule["conditions"])
  return False


@functools.lru_cache(maxsize=1)
def _setting_safety_rules():
  from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
  rules_by_key = {}

  def collect(node, inherited=()):
    if isinstance(node, list):
      for child in node:
        collect(child, inherited)
    elif isinstance(node, dict):
      rules = (*inherited, *(node.get("enablement") or []))
      if node.get("key") and node.get("widget"):
        safety = [rule for rule in rules if _setting_has_rule(rule, "offroad_only") or _setting_has_rule(rule, "not_engaged")]
        if safety:
          rules_by_key.setdefault(node["key"], []).append(safety)
      for name, child in node.items():
        if name not in ("enablement", "visibility", "options"):
          collect(child, rules)

  collect(generate_schema())
  return rules_by_key


def _setting_engaged():
  """Treat missing control-state messages as engaged so onroad writes fail closed."""
  sm = messaging.SubMaster(["selfdriveState", "selfdriveStateSP"])
  deadline = time.monotonic() + 0.5
  while not all(sm.seen.values()) and time.monotonic() < deadline:
    sm.update(50)
  return not all(sm.seen.values()) or sm["selfdriveState"].enabled or sm["selfdriveStateSP"].mads.enabled


def _setting_rule_allows(rule, offroad, engaged, params):
  kind = rule.get("type")
  if kind == "offroad_only":
    return offroad
  if kind == "not_engaged":
    return offroad or engaged is False
  if kind == "param":
    try:
      value = params.get(rule["key"], return_default=True)
      if isinstance(value, bytes):
        value = value.decode()
      expected = rule.get("equals")
      if isinstance(expected, bool):
        return (value is True or str(value).lower() in ("1", "true")) == expected
      return str(value) == str(expected)
    except Exception:
      return False
  if kind == "any":
    return any(_setting_rule_allows(child, offroad, engaged, params) for child in rule["conditions"])
  if kind == "all":
    return all(_setting_rule_allows(child, offroad, engaged, params) for child in rule["conditions"])
  if kind == "not":
    return not _setting_rule_allows(rule["condition"], offroad, engaged, params)
  return False


def _json_value(value):
  return value.decode("utf-8", "ignore") if isinstance(value, bytes) else value


def sunnylink_settings():
  """sunnylink's settings menus straight from the device: layout, car capabilities and current values."""
  from openpilot.common.params import Params
  from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
  params = Params()
  schema = generate_schema()
  try:
    from openpilot.sunnypilot.sunnylink.capabilities import generate_capabilities
    capabilities = generate_capabilities(params)
  except Exception:
    capabilities = {}
  found = _sunnylink_walk(schema, {"items": {}, "keys": set()})
  values = {}
  for key in set(found["items"]) | found["keys"]:
    try:
      values[key] = _json_value(params.get(key, return_default=True))
    except Exception:
      pass
  values["CarPlatformBundle"] = params.get("CarPlatformBundle")   # the Vehicle tab: manual selection...
  try:   # ...and what the car fingerprinted as, decoded like the device's own capabilities code
    from openpilot.sunnypilot.sunnylink import capabilities as caps_module
    values["CarFingerprint"] = str(caps_module.messaging.log_from_bytes(params.get("CarParamsPersistent"), caps_module.car.CarParams).carFingerprint)
  except Exception:
    values["CarFingerprint"] = None
  return {"schema": schema, "capabilities": capabilities, "values": values, "offroad": params.get_bool("IsOffroad")}


REALDATA = Path(os.environ.get("SUNNYDRIVE_REALDATA", "/data/media/0/realdata" if Path("/data").is_dir() else str(Path.home() / ".cache/sunnydrive/realdata")))   # off-device: drives copied over for demos
CONNECT_ROUTE = re.compile(r"[0-9a-f]{8}--[0-9a-f]{10}")   # the device's local route names, e.g. 00000451--ae1df09a9c


CONNECT_CAMERAS = {"q": "qcamera.ts", "f": "fcamera.hevc", "e": "ecamera.hevc", "d": "dcamera.hevc"}   # low-res, road, wide, driver


def _mpeg_crc32(data):
  crc = 0xFFFFFFFF
  for byte in data:
    crc ^= byte << 24
    for _ in range(8):
      crc = ((crc << 1) ^ 0x04C11DB7 if crc & 0x80000000 else crc << 1) & 0xFFFFFFFF
  return crc


CONNECT_PART_FRAMES = 40   # 2 s pieces at 20 fps (a keyframe every second): playback starts after ~1 MB instead of a whole minute


@functools.lru_cache(maxsize=48)
def _hevc_index(path, mtime):
  """Where each frame of a raw HEVC segment (Annex-B, as loggerd writes it) lives: one fast scan, then parts read only their bytes."""
  import mmap
  with open(path, "rb") as file:
    data = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
  starts = []
  i = data.find(b"\x00\x00\x01")
  while i >= 0:
    starts.append(i)
    i = data.find(b"\x00\x00\x01", i + 3)
  frames, current, has_vcl, params = [], [], False, []
  for n, s in enumerate(starts):
    end = starts[n + 1] if n + 1 < len(starts) else len(data)
    if n + 1 < len(starts) and data[end - 1] == 0:
      end -= 1   # 4-byte start code of the next NAL
    kind = (data[s + 3] >> 1) & 0x3F
    if kind in (32, 33, 34) and len(params) < 3:
      params.append((s, end))
    if has_vcl and (kind in (32, 33, 34, 35, 39) or (kind < 32 and data[s + 5] >> 7)):
      frames.append(current)
      current, has_vcl = [], False
    current.append((s, end))
    has_vcl |= kind < 32
  if current:
    frames.append(current)
  return data, frames, params


def hevc_frame_count(path):
  path = Path(path)
  return len(_hevc_index(str(path), path.stat().st_mtime)[1])


@functools.lru_cache(maxsize=256)
def _qcamera_duration(path, mtime):
  def timestamps(data):
    for i in range(0, len(data) - 187, 188):
      packet = data[i:i + 188]
      if packet[0] != 0x47 or not packet[1] & 0x40 or not packet[3] & 0x10:
        continue
      start = 4 + (1 + packet[4] if packet[3] & 0x20 else 0)
      if start + 14 > 188:
        continue
      if packet[start:start + 3] != b"\0\0\1" or not 0xE0 <= packet[start + 3] <= 0xEF or not packet[start + 7] & 0x80:
        continue
      p = packet[start + 9:start + 14]
      if len(p) == 5:
        yield ((p[0] & 0x0E) << 29) | (p[1] << 22) | ((p[2] & 0xFE) << 14) | (p[3] << 7) | (p[4] >> 1)

  with open(path, "rb") as file:
    first = next(timestamps(file.read(188 * 500)), None)
    file.seek(max(0, (Path(path).stat().st_size - 188 * 500) // 188 * 188))
    last = next(reversed(list(timestamps(file.read()))), None)
  return ((last - first) % (1 << 33)) / 90000 + .05 if first is not None and last is not None else None


def connect_segment_duration(route, seg):
  folder = REALDATA / f"{route}--{seg}"
  qcamera = folder / "qcamera.ts"
  if qcamera.is_file():
    duration = _qcamera_duration(str(qcamera), qcamera.stat().st_mtime)
    if duration is not None:
      return duration
  for name in ("fcamera.hevc", "ecamera.hevc", "dcamera.hevc"):
    camera = folder / name
    if camera.is_file():
      return hevc_frame_count(camera) / 20
  return 60


def hevc_part_ts(path, segment, part, last=False):
  """One 2-second piece of a raw HEVC camera segment as MPEG-TS for hls.js. No re-encode: frames are wrapped as they are,
  one PES per frame, stream setup (VPS/SPS/PPS) repeated at the piece start, timestamps continuing across the whole drive."""
  path = Path(path)
  data, frames, params = _hevc_index(str(path), path.stat().st_mtime)
  first = part * CONNECT_PART_FRAMES
  chunk = frames[first:first + CONNECT_PART_FRAMES]
  frame_ticks = 4500 if last or len(frames) < 1100 else 90000 * 60 // max(1, len(frames))   # the final segment ends after its actual frame count
  out, cc = [], {0: 0, 0x1000: 0, 0x100: 0}

  def packets(pid, payload, pcr=None, psi=False):
    first_packet = True
    while payload or first_packet:
      header = bytes([0x47, (0x40 if first_packet else 0) | pid >> 8, pid & 0xFF])
      adaptation = b""
      if first_packet and pcr is not None:
        adaptation = bytes([7, 0x10, pcr >> 25 & 0xFF, pcr >> 17 & 0xFF, pcr >> 9 & 0xFF, pcr >> 1 & 0xFF, (pcr & 1) << 7 | 0x7E, 0])
      room = 184 - len(adaptation)
      body, payload = payload[:room], payload[room:]
      if len(body) < room:   # pad the last packet with adaptation stuffing (PSI pads with 0xFF instead)
        if psi:
          body += b"\xff" * (room - len(body))
        else:
          stuffing = room - len(body)
          if adaptation:
            adaptation = bytes([adaptation[0] + stuffing]) + adaptation[1:] + b"\xff" * stuffing
          elif stuffing == 1:
            adaptation = b"\x00"
          else:
            adaptation = bytes([stuffing - 1, 0]) + b"\xff" * (stuffing - 2)
      out.append(header + bytes([(0x30 if adaptation else 0x10) | cc[pid]]) + adaptation + body)
      cc[pid] = (cc[pid] + 1) & 0xF
      first_packet = False

  def section(table_id, body):
    sec = bytes([table_id, 0xB0 | (len(body) + 9) >> 8, (len(body) + 9) & 0xFF, 0, 1, 0xC1, 0, 0]) + body
    return b"\x00" + sec + _mpeg_crc32(sec).to_bytes(4, "big")

  pat = section(0x00, b"\x00\x01\xf0\x00")
  pmt = section(0x02, b"\xe1\x00\xf0\x00" + b"\x24\xe1\x00\xf0\x00")   # PCR on PID 0x100; one HEVC stream (type 0x24)
  aud = b"\x00\x00\x00\x01\x46\x01\x50"
  setup = b"".join(b"\x00" + data[s:e] if data[s:s + 3] == b"\x00\x00\x01" else data[s:e] for s, e in params)
  base = 126000 + segment * 60 * 90000
  for n, frame in enumerate(chunk):
    pts = base + (first + n) * frame_ticks
    kinds = [(data[s + 3] >> 1) & 0x3F for s, _ in frame]
    key = any(k in (19, 20, 21, 32) for k in kinds)
    if n == 0 or key:
      packets(0, pat, psi=True)
      packets(0x1000, pmt, psi=True)
    stamp = bytes([0x21 | (pts >> 29 & 0x0E), pts >> 22 & 0xFF, 0x01 | (pts >> 14 & 0xFE), pts >> 7 & 0xFF, 0x01 | (pts << 1 & 0xFE)])
    body = aud + (setup if n == 0 and 32 not in kinds else b"") + b"".join(b"\x00" + data[s:e] if data[s:s + 3] == b"\x00\x00\x01" else data[s:e] for s, e in frame)
    packets(0x100, b"\x00\x00\x01\xe0\x00\x00\x80\x80\x05" + stamp + body, pcr=pts - 63000 if key else None)
  return b"".join(out)


CONNECT_CACHE = Path(os.environ.get("SUNNYDRIVE_CONNECT_CACHE", "/data/sunnydrive_cache" if Path("/data").is_dir() else str(Path.home() / ".cache/sunnydrive/connect")))   # never inside realdata: the uploader must not see it
_summary_queue, _summary_busy = [], threading.Event()


CONNECT_SPANS = ("engaged", "long", "lat", "override", "prompt", "critical", "bookmark")   # the drives-list timeline colours


def summarize_segment(route, seg):
  """One minute's qlog boiled down for the drives list: timeline spans, distance, first/last GPS.
  Spans follow comma connect (engaged/override/alerts/bookmarks) plus sunnypilot's MADS lat-only and long-only."""
  from openpilot.tools.lib.logreader import LogReader
  samples, bookmarks, gps, meters, t0, last, lat_active, mads, alerts = [], [], [], 0.0, None, None, False, None, []
  for m in LogReader(str(REALDATA / f"{route}--{seg}" / "qlog.zst")):
    t = m.logMonoTime / 1e9
    kind = m.which()
    if t0 is None and kind in ("selfdriveState", "carState"):
      t0 = t   # time within the minute counts from the first control message (initData can be much older)
    if t0 is None:
      continue
    if kind == "carControl":
      lat_active = bool(m.carControl.latActive)
    elif kind == "selfdriveStateSP":
      mads = m.selfdriveStateSP.mads
    elif kind == "selfdriveState":
      s = m.selfdriveState
      state, alert = str(s.state), str(s.alertStatus) if s.alertText1 else "normal"
      mads_on = bool(mads and mads.active)
      overriding = state in ("overriding", "preEnabled") or bool(mads and str(mads.state) == "overriding")
      lateral = lat_active or mads_on
      tag = {"engaged": s.enabled and lateral, "long": s.enabled and not lateral, "lat": not s.enabled and lateral, "override": overriding,
             "prompt": alert == "userPrompt", "critical": alert == "critical"}
      samples.append((min(60.0, round(t - t0, 1)), tag))
      if alert == "critical" and (not alerts or alerts[-1][1] != s.alertText1):
        alerts.append([min(59.0, round(t - t0, 1)), s.alertText1, s.alertText2])   # for the phone's alerts
    elif kind in ("userBookmark", "bookmarkButton"):
      bookmarks.append(min(59.0, round(t - t0, 1)))
    elif kind == "carState":
      if last is not None:
        meters += max(0.0, m.carState.vEgo) * (t - last)
      last = t
    elif kind == "gpsLocationExternal" and m.gpsLocationExternal.hasFix:
      gps.append((m.gpsLocationExternal.latitude, m.gpsLocationExternal.longitude))

  spans = {}
  for name in CONNECT_SPANS[:-1]:
    out, start = [], None
    for at, tag in samples + [(60.0, {})]:
      if tag.get(name) and start is None:
        start = at
      elif not tag.get(name) and start is not None:
        out.append([start, at])
        start = None
    spans[name] = out
  spans["bookmark"] = [[b, b + 1] for b in bookmarks]
  return {"spans": spans, "meters": round(meters), "start": gps[0] if gps else None, "end": gps[-1] if gps else None, "alerts": alerts}


def _summary_worker():
  """Background, lowest priority, only with the car off: summarise queued segments into CONNECT_CACHE."""
  try:
    os.setpriority(os.PRIO_PROCESS, threading.get_native_id(), 19)
  except (AttributeError, OSError):
    pass
  while True:
    _summary_busy.wait()
    try:
      from openpilot.common.params import Params
      offroad = Params().get_bool("IsOffroad")
    except Exception:
      offroad = True   # dev machine
    if not offroad or not _summary_queue:
      _summary_busy.clear() if not _summary_queue else time.sleep(30)
      continue
    route, seg = _summary_queue.pop(0)
    target = CONNECT_CACHE / f"{route}--{seg}.json"
    if target.exists():
      continue
    try:
      summary = summarize_segment(route, seg)
    except Exception as error:   # a missing or damaged qlog still gets a (blank) entry so it isn't retried forever
      summary = {"error": str(error)[:200]}
    target.write_text(json.dumps(summary))
    time.sleep(0.3)   # breathe between minutes so page requests never queue behind the summariser


def _route_summary(info):
  """A drive's timeline from its cached minutes; queues the minutes still missing."""
  CONNECT_CACHE.mkdir(parents=True, exist_ok=True)
  spans, meters, start, end, done, alerts = {name: [] for name in CONNECT_SPANS}, 0, None, None, 0, []
  for seg in info["segments"]:
    target = CONNECT_CACHE / f"{info['id']}--{seg}.json"
    try:
      s = _summaries.get(target.name) or _summaries.setdefault(target.name, json.loads(target.read_text()))
    except (OSError, ValueError):
      if (info["id"], seg) not in _summary_queue and (REALDATA / f"{info['id']}--{seg}" / "qlog.zst").is_file():
        _summary_queue.append((info["id"], seg))
      continue
    done += 1
    for name, items in s.get("spans", {}).items():
      spans.setdefault(name, []).extend([seg * 60 + a, seg * 60 + b] for a, b in items)
    meters += s.get("meters", 0)
    alerts += [[seg * 60 + a[0], *a[1:]] for a in s.get("alerts", [])]
    start = start or s.get("start")
    end = s.get("end") or end
  if _summary_queue:
    _summary_busy.set()
  return {"done": done, "spans": spans, "meters": meters, "startGps": start, "endGps": end, "alerts": alerts}


threading.Thread(target=_summary_worker, daemon=True, name="connect-summaries").start()


_segment_files, _summaries = {}, {}   # per-folder file list/size, and per-minute summaries, kept once read


def phone_alerts():
  """What the phone app notifies about: each drive once it's fully summarised, and critical alerts during it. Newest first; ids are stable."""
  events = []
  for r in connect_routes()[:20]:
    s = r.get("summary") or {}
    if not r["segments"] or s.get("done", 0) < len(r["segments"]):
      continue   # still driving, or still being summarised
    if s.get("meters", 0) < 200 and not s.get("alerts"):
      continue   # parked with the car on: not a drive
    minutes, km = round((r["end"] - r["start"]) / 60), s.get("meters", 0) / 1000
    for at, text1, *rest in s.get("alerts", []):
      events.append({"id": f"{r['id']}:alert:{at}", "kind": "critical", "at": r["start"] + at, "title": "Critical alert: " + text1,
                     "body": " ".join(x for x in rest if x) or "During your drive"})
    events.append({"id": f"{r['id']}:drive", "kind": "drive", "at": r["end"], "title": "Drive saved", "from": s.get("startGps"), "to": s.get("endGps"),
                   "body": f"{minutes} min · {km:.1f} km" + (f" · {len(s.get('alerts', []))} critical alert" + ("s" if len(s.get("alerts", [])) != 1 else "") if s.get("alerts") else "")})
  return sorted(events, key=lambda e: -e["at"])


def connect_routes():
  """Drives stored on this device, newest first: segments on disk and when they were recorded."""
  return _connect_routes(int(time.monotonic() // 3))


@functools.lru_cache(maxsize=1)
def _connect_routes(_tick):
  # ponytail: drive list can lag disk by three seconds; use filesystem events if instant updates become necessary.
  routes = {}
  for entry in REALDATA.iterdir() if REALDATA.is_dir() else []:
    route, _, segment = entry.name.rpartition("--")
    if not CONNECT_ROUTE.fullmatch(route) or not segment.isdigit() or not entry.is_dir():
      continue
    info = routes.setdefault(route, {"id": route, "segments": [], "video": [], "cams": {c: [] for c in CONNECT_CAMERAS}, "start": None, "end": None, "bytes": 0})
    seg, mtime = int(segment), entry.stat().st_mtime
    key = (entry.name, mtime)
    if key not in _segment_files:   # a finished segment folder never changes: look inside it once
      files = {f.name: f.stat().st_size for f in os.scandir(entry) if f.is_file()}
      _segment_files[key] = (set(files), sum(files.values()))
    names, size = _segment_files[key]
    info["segments"].append(seg)
    for cam, name in CONNECT_CAMERAS.items():
      if name in names:
        info["cams"][cam].append(seg)
    if "qcamera.ts" in names:
      info["video"].append(seg)
    info["start"] = min(info["start"] or mtime, mtime)
    info["end"] = max(info["end"] or 0, mtime)
    info["bytes"] += size
  for info in routes.values():
    info["segments"].sort()
    info["video"].sort()
    for segs in info["cams"].values():
      segs.sort()
    info["start"] -= 60   # a segment folder's time is when it finished; each holds a minute
    info["duration"] = info["segments"][-1] * 60 + connect_segment_duration(info["id"], info["segments"][-1])
  ordered = sorted(routes.values(), key=lambda r: r["start"], reverse=True)
  for info in ordered:   # newest drives get summarised first
    info["summary"] = _route_summary(info)
  return ordered


def connect_playlist(route, cam="q", auth=""):
  """HLS playlist of one camera's segments for a drive; missing minutes become discontinuities."""
  name = CONNECT_CAMERAS[cam]
  segments = sorted(int(p.name.rpartition("--")[2]) for p in REALDATA.glob(f"{route}--*") if p.name.rpartition("--")[2].isdigit() and (p / name).is_file())
  if not segments:
    raise FileNotFoundError(route)
  lines = ["#EXTM3U", "#EXT-X-VERSION:3", f"#EXT-X-TARGETDURATION:{61 if cam == 'q' else 3}", "#EXT-X-MEDIA-SEQUENCE:0", "#EXT-X-PLAYLIST-TYPE:VOD"]
  previous = None
  for seg in segments:
    if previous is not None and seg != previous + 1:
      lines.append("#EXT-X-DISCONTINUITY")
    if cam == "q":   # low-res is already small: one piece per minute
      seconds = connect_segment_duration(route, seg) if seg == segments[-1] else 60
      lines += [f"#EXTINF:{seconds:.2f},", f"qcamera?route={route}&seg={seg}&cam={cam}" + (f"&auth={quote(auth)}" if auth else "")]
    else:   # full-res: 2 s pieces; only the drive's last (possibly short) minute is counted exactly
      frames = hevc_frame_count(REALDATA / f"{route}--{seg}" / name) if seg == segments[-1] else 1200
      for part in range((frames + CONNECT_PART_FRAMES - 1) // CONNECT_PART_FRAMES):
        seconds = min(CONNECT_PART_FRAMES, frames - part * CONNECT_PART_FRAMES) / 20
        path = f"qcamera?route={route}&seg={seg}&cam={cam}&part={part}" + ("&last=1" if seg == segments[-1] else "")
        lines += [f"#EXTINF:{seconds:.2f},", path + (f"&auth={quote(auth)}" if auth else "")]
    previous = seg
  return "\n".join(lines + ["#EXT-X-ENDLIST", ""])


def sunnylink_cars():
  """The device's selectable cars ({name: {platform, make, brand, model, year, ...}})."""
  from openpilot.common.params import Params
  cars = Params().get("CarList")
  if isinstance(cars, (str, bytes)):
    cars = json.loads(cars)
  if not cars:
    with open(ROOT / "openpilot/sunnypilot/selfdrive/car/car_list.json") as f:
      cars = json.load(f)
  return cars


def sunnylink_set_vehicle(name):
  """Pick a car by its list name, or None for auto-detect, only while offroad."""
  from openpilot.common.params import Params
  params = Params()
  if not params.get_bool("IsOffroad"):
    raise PermissionError("only while the car is off")
  if name is None:
    bundle = {}
  else:
    car = sunnylink_cars().get(name)
    if car is None:
      raise KeyError(name)
    bundle = {**{k: v for k, v in car.items() if k != "id"}, "name": name}
  try:
    params.put("CarPlatformBundle", bundle, block=True)
  except TypeError:
    params.put("CarPlatformBundle", bundle)
  return params.get("CarPlatformBundle")


LIVE_SOCKETS = {"road": "livestreamNarrowRoadEncodeData", "wideRoad": "livestreamWideRoadEncodeData", "driver": "livestreamCabinEncodeData"}
V4L2_BUF_FLAG_KEYFRAME = 0x8
_live_viewers = 0
_live_lock = threading.Lock()


def _live_keepalive():
  """Keep the livestream encoders up while anyone watches. Plain HTTP, not webrtcd: WebView's WebRTC never offers the phone's
  hotspot interface, so a phone that is the comma's hotspot can't reach it, while TCP routes fine. Re-asserted because ignition-on clears it."""
  from openpilot.common.params import Params
  params, owned, idle_since = Params(), False, 0.0
  while True:
    with _live_lock:
      watching = _live_viewers > 0
    if watching:
      if not params.get_bool("IsLiveStreaming"):
        params.put_bool("IsLiveStreaming", True)
      owned, idle_since = True, 0.0
    elif owned:
      idle_since = idle_since or time.monotonic()
      if time.monotonic() - idle_since > 10:   # grace for switching views
        params.put_bool("IsLiveStreaming", False)
        owned = False
    time.sleep(2)


def live_frames(camera, params):
  """Yield (keyframe, annexb) access units for one camera, starting at a keyframe."""
  sock = messaging.sub_sock(LIVE_SOCKETS[camera], conflate=False, timeout=1000)
  seen_key = False
  params.put_bool("LivestreamRequestKeyframe", True)
  while True:
    msg = messaging.recv_one(sock)
    if msg is None:
      yield None   # lets the caller notice a dead client between frames
      continue
    frame = getattr(msg, msg.which())
    key = bool(frame.idx.flags & V4L2_BUF_FLAG_KEYFRAME)
    if not seen_key:
      if not key:
        continue
      seen_key = True
      params.put_bool("LivestreamRequestKeyframe", False)   # left on, the encoder would emit only keyframes
    yield key, frame.header + frame.data


def sunnylink_set(key, value):
  """Write one setting using the driving-state rules in sunnylink's schema."""
  from openpilot.common.params import Params
  from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
  params = Params()
  item = _sunnylink_walk(generate_schema(), {"items": {}, "keys": set()})["items"].get(key)
  if item is None or item.get("widget") not in SUNNYLINK_WIDGETS or item.get("readonly") or item.get("blocked"):   # blocked = device-only (e.g. SSH/ADB)
    raise PermissionError("not a changeable setting")
  offroad = params.get_bool("IsOffroad")
  item_rules = _setting_safety_rules().get(key, [])
  is_engaged = _setting_engaged() if not offroad and any(_setting_has_rule(rule, "not_engaged") for rules in item_rules for rule in rules) else None
  if any(not all(_setting_rule_allows(rule, offroad, is_engaged, params) for rule in rules) for rules in item_rules):
    raise PermissionError("setting unavailable while onroad or engaged")
  if value in ("", None):
    params.remove(key)
  else:
    cast = {1: lambda v: v in (True, 1, "1", "true"), 2: lambda v: int(float(v)), 3: float}.get(int(params.get_type(key)), str)
    try:
      params.put(key, cast(value), block=True)   # newer params write in the background; wait so the read-back below is current
    except TypeError:
      params.put(key, cast(value))
  return _json_value(params.get(key, return_default=True))


class SunnydriveServer(ThreadingHTTPServer):
  daemon_threads = True

  def __init__(self, address, allowed_origin=None, llm_upstream="", allow_loopback=True):
    super().__init__(address, SunnydriveHandler)
    # The Android apps bundle the WUI and request these APIs across origins.
    self.allowed_origins = {"https://ai.sunnypilot.sunnydrive", "https://ai.sunnypilot.sunnydrive.parked", "http://localhost:8766", "http://127.0.0.1:8766"} | ({allowed_origin} if allowed_origin else set())
    self.llm_upstream = llm_upstream.rstrip("/")
    self.allow_loopback = allow_loopback
    self.telemetry_changed = threading.Condition()
    self.telemetry_version = 0
    self.publish_telemetry({"timestampMs": 0, "car": None, "selfdrive": None, "mads": None, "lateral": None, "gps": None, "device": None, "vehicle": None, "model": None, "driverMonitoring": None, "speedLimit": None, "map": None, "dec": None})

  def publish_telemetry(self, sample):
    event = b"data: " + json.dumps(compact(sample), allow_nan=False, separators=(",", ":")).encode() + b"\n\n"
    with self.telemetry_changed:
      self.telemetry = sample
      self.telemetry_event = event
      self.telemetry_version += 1
      self.telemetry_changed.notify_all()


class SunnydriveHandler(BaseHTTPRequestHandler):
  def log_message(self, _format, *_args):
    pass   # authenticated media URLs carry a token in the query; never put it in logs

  def send_header(self, keyword, value):
    if keyword.lower() == "access-control-allow-origin":
      self._cors_sent = True
    super().send_header(keyword, value)

  def end_headers(self):
    # every reply to the app's origins carries CORS, errors included, so the page sees the real status instead of a CORS block
    origin = getattr(self, "headers", None) and self.headers.get("Origin")   # absent on requests too broken to parse
    if not getattr(self, "_cors_sent", False) and origin in self.server.allowed_origins:
      super().send_header("Access-Control-Allow-Origin", origin)
    self._cors_sent = False
    super().end_headers()

  def do_GET(self):
    parsed = urlsplit(self.path)
    path = parsed.path
    query = parse_qs(parsed.query)
    if path == "/pair/info":
      client_id = query.get("client_id", [""])[0]
      return self.send_json({"deviceId": pairing.device_id(), "name": pairing.device_name(), "apiVersion": 1,
                             "paired": pairing.is_paired(client_id), "offroad": pairing.is_offroad()})
    if path == "/pair/status":
      return self.send_json(pairing.consume_request(query.get("request", [""])[0]))
    if not self.authorized(query):
      return self.send_error(401, "Pair this phone first")
    if path == "/connect/routes":
      try:
        from openpilot.common.params import Params
        offroad = Params().get_bool("IsOffroad")
      except Exception:
        offroad = True   # off-device: no params, summaries run whenever
      return self.send_json({"routes": connect_routes(), "offroad": offroad})
    if path == "/alerts":
      return self.send_json({"alerts": phone_alerts()})
    if path in ("/connect/playlist.m3u8", "/connect/qcamera"):
      route = query.get("route", [""])[0]
      cam = query.get("cam", ["q"])[0]
      if not CONNECT_ROUTE.fullmatch(route) or cam not in CONNECT_CAMERAS:
        return self.send_error(400, "Unknown route or camera")
      if path == "/connect/qcamera":
        segment = query.get("seg", [""])[0]
        video = REALDATA / f"{route}--{segment}" / CONNECT_CAMERAS[cam]
        if not segment.isdigit() or not video.is_file():
          return self.send_error(404, "No video for that segment")
        if cam == "q":
          return self.send_video(video, content_type="video/mp2t")
        part = query.get("part", ["0"])[0]
        if not part.isdigit():
          return self.send_error(400, "Bad part")
        body = hevc_part_ts(video, int(segment), int(part), query.get("last", [""])[0] == "1")   # full-res cameras: raw HEVC, a 2 s piece repackaged per request
        self.send_response(200)
        self.send_header("Content-Type", "video/mp2t")
        self.send_header("Cache-Control", "private, max-age=86400")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
          self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
          pass
        return
      try:
        body = connect_playlist(route, cam, query.get("auth", [""])[0]).encode()
      except FileNotFoundError:
        return self.send_error(404, "No video for that route")
      self.send_response(200)
      self.send_header("Content-Type", "application/vnd.apple.mpegurl")
      self.send_header("Cache-Control", "no-store")
      if self.headers.get("Origin") in self.server.allowed_origins:
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      return self.wfile.write(body)
    if path == "/sunnylink/cars":
      try:
        return self.send_json(sunnylink_cars())
      except Exception as error:
        return self.send_error(503, f"car list unavailable: {error}")
    if path == "/sunnylink/settings":
      try:
        return self.send_json(sunnylink_settings())
      except Exception as error:   # not a sunnypilot device (e.g. the Mac dev server)
        return self.send_error(503, f"sunnylink settings unavailable: {error}")
    if path in LLM_GET:
      return self.proxy_llm(path)
    if path == "/connect/live":   # one camera: [u32 length][u8 keyframe][H.264 Annex B access unit], repeated
      camera = query.get("cam", ["road"])[0]
      if camera not in LIVE_SOCKETS:
        return self.send_error(400, "unknown camera")
      return self.send_live(camera)
    if path == "/telemetry/stream":   # push each new sample the moment it exists: no poll interval, one connection
      self.send_response(200)
      self.send_header("Content-Type", "text/event-stream")
      self.send_header("Cache-Control", "no-store")
      self.send_header("X-Accel-Buffering", "no")
      gz = zlib.compressobj(6, zlib.DEFLATED, 31) if "gzip" in self.headers.get("Accept-Encoding", "") else None   # JSON compresses ~4x; each event is flushed whole
      if gz:
        self.send_header("Content-Encoding", "gzip")
      if self.headers.get("Origin") in self.server.allowed_origins:
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
      self.end_headers()
      version = -1
      try:
        while True:
          with self.server.telemetry_changed:
            self.server.telemetry_changed.wait_for(lambda: self.server.telemetry_version != version, timeout=15)
            changed = self.server.telemetry_version != version
            if changed:
              version = self.server.telemetry_version
              event = self.server.telemetry_event
            else:
              event = b": keepalive\n\n"   # proxies (tailscale serve) keep idle streams open
          if not self.still_authorized():
            return
          self.wfile.write(gz.compress(event) + gz.flush(zlib.Z_SYNC_FLUSH) if gz else event)
          self.wfile.flush()
      except (BrokenPipeError, ConnectionResetError, OSError, ValueError):
        return
    if path != "/telemetry":
      return self.send_error(404, "Not Found")
    return self.send_json(self.server.telemetry)

  def send_live(self, camera):
    global _live_viewers
    from openpilot.common.params import Params
    self.send_response(200)
    self.send_header("Content-Type", "application/octet-stream")
    self.send_header("Cache-Control", "no-store")
    self.end_headers()
    with _live_lock:
      _live_viewers += 1
    try:
      for item in live_frames(camera, Params()):
        if not self.still_authorized():
          return
        key, data = item or (False, b"")   # empty frame each idle second: a gone client is noticed even with no video
        self.wfile.write(len(data).to_bytes(4, "big") + bytes([key]) + data)
        self.wfile.flush()
    except (BrokenPipeError, ConnectionResetError, OSError, ValueError):
      pass
    finally:
      with _live_lock:
        _live_viewers -= 1

  def send_json(self, data):
    body = json.dumps(data, allow_nan=False).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Cache-Control", "no-store")
    if self.headers.get("Origin") in self.server.allowed_origins:
      self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def send_video(self, video_file, head_only=False, content_type="video/mp4"):
    size = video_file.stat().st_size
    requested = self.headers.get("Range", "")
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested) if requested else None
    if requested and not match:
      self.send_response(416)
      self.send_header("Content-Range", f"bytes */{size}")
      return self.end_headers()
    if match and not match[1] and not match[2]:
      self.send_response(416)
      self.send_header("Content-Range", f"bytes */{size}")
      return self.end_headers()
    start = int(match[1]) if match and match[1] else max(0, size - int(match[2])) if match else 0
    end = min(size - 1, int(match[2])) if match and match[1] and match[2] else size - 1
    if start >= size or end < start:
      self.send_response(416)
      self.send_header("Content-Range", f"bytes */{size}")
      return self.end_headers()
    self.send_response(206 if match else 200)
    self.send_header("Content-Type", content_type)
    self.send_header("Accept-Ranges", "bytes")
    self.send_header("Cache-Control", "private, max-age=86400")
    if match:
      self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    if self.headers.get("Origin") in self.server.allowed_origins:
      self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
    self.send_header("Content-Length", str(end - start + 1))
    self.end_headers()
    if head_only:
      return
    try:
      with video_file.open("rb") as video:
        video.seek(start)
        remaining = end - start + 1
        while remaining:
          chunk = video.read(min(1024 * 1024, remaining))
          if not chunk:
            break
          self.wfile.write(chunk)
          remaining -= len(chunk)
    except (BrokenPipeError, ConnectionResetError):
      pass

  def do_OPTIONS(self):
    if self.headers.get("Origin") not in self.server.allowed_origins:
      return self.send_error(403)
    self.send_response(204)
    self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
    self.send_header("Access-Control-Allow-Methods", "GET, POST")
    self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
    self.send_header("Access-Control-Max-Age", "600")
    self.end_headers()

  def do_POST(self):
    path = urlsplit(self.path).path
    if path == "/pair/request":
      try:
        body = self.read_json()
        return self.send_json({"request": pairing.request_pairing(str(body["clientId"]), body.get("name"))})
      except PermissionError as error:
        return self.send_error(403, str(error))
      except (ValueError, KeyError, TypeError) as error:
        return self.send_error(400, str(error))
    if not self.authorized(parse_qs(urlsplit(self.path).query)):
      return self.send_error(401, "Pair this phone first")
    if path == "/pair/unpair":
      try:
        body = self.read_json()
        return self.send_json({"removed": pairing.unpair(str(body["clientId"]))})
      except (ValueError, KeyError, TypeError) as error:
        return self.send_error(400, str(error))
    if path in ("/sunnylink/param", "/sunnylink/vehicle"):
      origin = self.headers.get("Origin")
      if origin not in self.server.allowed_origins and urlsplit(origin or "").netloc != self.headers.get("Host"):   # browser origin filter; non-browser clients can forge Origin
        return self.send_error(403)
      try:
        body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", "0")), 65536)))
        if path == "/sunnylink/vehicle":
          return self.send_json({"value": sunnylink_set_vehicle(body.get("name"))})
        return self.send_json({"key": body["key"], "value": sunnylink_set(str(body["key"]), body.get("value"))})
      except PermissionError as error:
        return self.send_error(409, str(error))
      except (ValueError, KeyError, TypeError) as error:
        return self.send_error(400, str(error))
    if path not in LLM_POST:
      return self.send_error(404)
    try:
      length = int(self.headers.get("Content-Length", "0"))
    except ValueError:
      return self.send_error(400)
    if length <= 0 or length > 2_000_000:
      return self.send_error(413)
    self.proxy_llm(path, self.rfile.read(length))

  def proxy_llm(self, path, body=None):
    upstream = self.server.llm_upstream
    if not upstream:
      return self.send_error(502, "No model server configured")
    request = Request(upstream + path, data=body,
                      headers={"Content-Type": "application/json"} if body is not None else {},
                      method="POST" if body is not None else "GET")
    try:
      with urlopen(request, timeout=65 if body is not None else 5) as response:
        status, result = response.status, response.read()
    except HTTPError as error:
      status, result = error.code, error.read()
    except (URLError, TimeoutError, OSError):
      return self.send_error(502, "LM Studio unavailable")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Cache-Control", "no-store")
    if self.headers.get("Origin") in self.server.allowed_origins:
      self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin"))
    self.send_header("Content-Length", str(len(result)))
    self.end_headers()
    self.wfile.write(result)

  def read_json(self):
    length = int(self.headers.get("Content-Length", "0"))
    if length <= 0 or length > 65536:
      raise ValueError("invalid request size")
    return json.loads(self.rfile.read(length))

  def authorized(self, query):
    self._auth_query = query
    if self.server.allow_loopback and self.client_address[0] in ("127.0.0.1", "::1"):
      return True
    header = self.headers.get("Authorization", "")
    token = header[7:] if header.startswith("Bearer ") else query.get("auth", [""])[0]
    return pairing.authorized(token)

  def still_authorized(self):
    """Streams outlive their request: re-check once a second so an unpaired phone is cut off right away."""
    now = time.monotonic()
    if now < getattr(self, "_auth_until", 0.0):
      return True
    self._auth_until = now + 1
    return self.authorized(self._auth_query)


def compact(sample):
  """Road model numbers to centimetres for the stream (17-digit floats were ~80% of every sample); GPS stays exact."""
  def r(v):
    return round(v, 2) if isinstance(v, float) else [r(x) for x in v] if isinstance(v, list) else {k: r(x) for k, x in v.items()} if isinstance(v, dict) else v
  return {**sample, "model": r(sample["model"])} if isinstance(sample, dict) and sample.get("model") else sample


def discovery_response(packet, http_port=8766):
  """Return a small discovery reply, or None for malformed/foreign datagrams."""
  if not packet.startswith(DISCOVERY_PREFIX) or len(packet) > 1024:
    return None
  try:
    request = json.loads(packet[len(DISCOVERY_PREFIX):])
    nonce, client_id = str(request["nonce"]), str(request.get("clientId", ""))
  except (ValueError, KeyError, TypeError):
    return None
  if request.get("v") != 1 or not 8 <= len(nonce) <= 128:
    return None
  body = {"v": 1, "nonce": nonce, "deviceId": pairing.device_id(), "name": pairing.device_name(),
          "httpPort": http_port, "apiVersion": 1, "paired": pairing.is_paired(client_id), "offroad": pairing.is_offroad()}
  return DISCOVERY_PREFIX + json.dumps(body, separators=(",", ":")).encode()


def discovery_loop(http_port=8766, udp_port=DISCOVERY_PORT):
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", udp_port))
    while True:
      try:
        packet, sender = sock.recvfrom(1024)
        reply = discovery_response(packet, http_port)
        if reply:
          sock.sendto(reply, sender)
      except OSError:
        time.sleep(1)


def sample_loop(server):
  sm = messaging.SubMaster(SERVICES)
  while True:
    start = time.monotonic()
    sm.update(50)
    server.publish_telemetry(snapshot(sm))   # 20 Hz, the road model's own rate; streamed to the car screen as it changes
    time.sleep(max(0.0, 0.05 - (time.monotonic() - start)))   # new messages wake update() early: hold the rate


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: all interfaces for iPad access)")
  parser.add_argument("--port", type=int, default=8766)
  parser.add_argument("--allow-origin", help="Optional exact origin for a separately hosted WUI")
  parser.add_argument("--llm-upstream", default=os.environ.get("SUNNYDRIVE_LLM", ""), help="Optional OpenAI-compatible model server URL")
  args = parser.parse_args()
  os.nice(10)
  server = SunnydriveServer((args.host, args.port), args.allow_origin, args.llm_upstream)
  threading.Thread(target=sample_loop, args=(server,), daemon=True).start()
  threading.Thread(target=_live_keepalive, daemon=True, name="sunnydrive-live").start()
  threading.Thread(target=discovery_loop, args=(args.port,), daemon=True, name="sunnydrive-discovery").start()
  print(f"Sunnydrive API: http://{args.host}:{args.port}/", flush=True)
  server.serve_forever()


if __name__ == "__main__":
  main()
