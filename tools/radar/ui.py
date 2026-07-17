#!/usr/bin/env python3
import argparse
import logging
import math
import multiprocessing
import os
import pty
import queue
import re
import signal
import struct
import subprocess
import sys
import termios
import time
from dataclasses import dataclass
import fcntl

import numpy as np
import pyray as rl

import cereal.messaging as messaging
from msgq.visionipc import VisionStreamType
from openpilot.common.basedir import BASEDIR
from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
from openpilot.common.transformations.orientation import rot_from_euler
from openpilot.selfdrive.ui.mici.onroad.cameraview import CameraView
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.tools.replay.lib.ui_helpers import Calibration, plot_model
from opendbc.can import CANParser
from opendbc.car import structs
from opendbc.car.hyundai.radar_interface import HYUNDAI_RADAR_TRACK_SPECS, RadarInterface
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

os.environ["BASEDIR"] = BASEDIR

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
CAMERA_WIDTH = 960
CONTENT_HEIGHT = 720
CAMERA_BUFFER_WIDTH = 640
CAMERA_BUFFER_HEIGHT = 480
MAX_FORWARD_DISTANCE = 160.0
MAX_LATERAL_DISTANCE = 30.0
FUSED_CAMERA_ZOOM = 1.7
FUSED_STREAM_GRACE_SECONDS = 1.0
REPLAY_EXECUTABLE = os.path.join(BASEDIR, "tools/replay/replay")

BACKGROUND = rl.Color(11, 16, 24, 255)
PANEL = rl.Color(17, 25, 36, 255)
GRID = rl.Color(69, 82, 99, 110)
TEXT = rl.Color(236, 241, 247, 255)
MUTED = rl.Color(154, 168, 184, 255)
CYAN = rl.Color(72, 220, 255, 255)
GREEN = rl.Color(0, 255, 126, 255)
ORANGE = rl.Color(255, 164, 48, 255)
RED = rl.Color(255, 76, 89, 255)
WHITE = rl.Color(255, 255, 255, 255)
PURPLE = rl.Color(190, 125, 255, 255)

SPEC_BY_RANGE = {
  (spec.start_addr, spec.end_addr): spec
  for spec in HYUNDAI_RADAR_TRACK_SPECS
}
SPEC_BY_NAME = {spec.name: spec for spec in HYUNDAI_RADAR_TRACK_SPECS}
PREFERRED_RADAR_SOURCE = "RADAR_3A5_3C4"
DEFAULT_SOURCE_FILTERS = (False, True, True)  # hide moving, stationary, unknown
RadarSourceKey = tuple[int, int, int]
RADAR_DETAIL_SIGNALS = {
  "MOTION_STATE", "REL_LAT_SPEED", "ABS_SPEED", "WIDTH", "LENGTH", "ORIENTATION_ANGLE",
  "AGE", "COAST_AGE", "STATE_ALT", "TRACK_COUNTER",
}
TABLE_MODES = ("motion", "kinematics", "object")
PLAYBACK_SPEEDS = (0.2, 0.5, 1.0, 2.0, 4.0, 8.0)
TRACK_COUNT_FIELD_WIDTH = 3
SOURCE_CIRCLE_RADIUS_SCALE = 0.8


@dataclass
class ManagedReplay:
  process: subprocess.Popen
  master_fd: int
  paused: bool = False
  playback_speed: float = 1.0
  progress_current: int = 0
  progress_total: int = 0
  car_fingerprint: str = ""
  terminal_buffer: str = ""

  def poll(self):
    return self.process.poll()

  def send(self, keys: str) -> None:
    if self.master_fd >= 0 and self.poll() is None:
      try:
        os.write(self.master_fd, keys.encode())
      except OSError:
        pass
      if keys == " ":
        self.paused = not self.paused
      elif keys == "+":
        self.playback_speed = next(
          (speed for speed in PLAYBACK_SPEEDS if speed > self.playback_speed),
          self.playback_speed,
        )
      elif keys == "-":
        self.playback_speed = next(
          (speed for speed in reversed(PLAYBACK_SPEEDS) if speed < self.playback_speed),
          self.playback_speed,
        )

  def drain_output(self) -> None:
    if self.master_fd < 0:
      return
    output = bytearray()
    while True:
      try:
        chunk = os.read(self.master_fd, 65536)
        if not chunk:
          break
        output.extend(chunk)
      except BlockingIOError:
        break
      except OSError:
        break
    if output:
      self.terminal_buffer = (self.terminal_buffer + output.decode(errors="ignore"))[-65536:]
      progress_matches = list(re.finditer(r"PROGRESS:(\d+):(\d+)", self.terminal_buffer))
      if progress_matches:
        self.progress_current = int(progress_matches[-1].group(1))
        self.progress_total = int(progress_matches[-1].group(2))
      fingerprint_matches = list(re.finditer(r"Car Fingerprint:\s*([^\r\n\x1b]+)", self.terminal_buffer))
      if fingerprint_matches:
        self.car_fingerprint = fingerprint_matches[-1].group(1).strip()

  def close_terminal(self) -> None:
    if self.master_fd >= 0:
      os.close(self.master_fd)
      self.master_fd = -1


@dataclass(frozen=True)
class ReplayTimelineEntry:
  start: float
  end: float
  kind: str
  title: str = ""
  detail: str = ""


@dataclass(frozen=True)
class ReplayTimeline:
  start: float = 0.0
  end: float = 0.0
  entries: tuple[ReplayTimelineEntry, ...] = ()
  car_fingerprint: str = ""


@dataclass
class ReplayScrubState:
  active: bool = False
  preview_seconds: float | None = None
  last_seek_at: float = 0.0
  last_seek_second: int | None = None
  pending_seconds: float | None = None


def start_route_replay(route: str) -> ManagedReplay:
  master_fd, slave_fd = pty.openpty()
  try:
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 140, 0, 0))
    os.set_blocking(master_fd, False)
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    process = subprocess.Popen(
      [REPLAY_EXECUTABLE, "--ecam", route],
      cwd=BASEDIR,
      env=env,
      stdin=slave_fd,
      stdout=slave_fd,
      stderr=slave_fd,
      close_fds=True,
    )
  except Exception:
    os.close(master_fd)
    raise
  finally:
    os.close(slave_fd)
  return ManagedReplay(process, master_fd)


def stop_route_replay(replay: ManagedReplay | None) -> None:
  if replay is None:
    return
  if replay.poll() is None:
    replay.process.terminate()
    try:
      replay.process.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
      replay.process.kill()
      replay.process.wait(timeout=1.0)
  replay.close_terminal()


def replace_route_replay(process: ManagedReplay | None, route: str) -> tuple[ManagedReplay | None, str]:
  route = route.strip()
  if not route:
    return process, "Enter a route or segment ID."
  stop_route_replay(process)
  try:
    replay = start_route_replay(route)
    print(f"Radar debugger opened route: {route}", flush=True)
    return replay, ""
  except OSError as exc:
    return None, f"Could not start replay: {exc}"


def route_start_seconds(route: str) -> float:
  match = re.search(r"(?:--|/)(\d+)(?::[^/]*)?(?:/[qra])?$", route)
  return int(match.group(1)) * 60.0 if match is not None else 0.0


def replay_timeline_worker(route: str, output_queue) -> None:
  from openpilot.tools.lib.logreader import LogReader, ReadMode

  entries: list[list[float | str]] = []
  engagement_index = None
  alert_index = None
  alert_signature = None
  first_mono_time = None
  route_offset = route_start_seconds(route)
  end_time = route_offset
  car_fingerprint = ""
  try:
    for message in LogReader(route, default_mode=ReadMode.QLOG, only_union_types=True):
      mono_time = int(message.logMonoTime)
      if first_mono_time is None:
        first_mono_time = mono_time
      seconds = route_offset + (mono_time - first_mono_time) / 1e9
      end_time = max(end_time, seconds)
      message_type = message.which()
      if message_type == "carParams":
        car_fingerprint = str(message.carParams.carFingerprint)
      elif message_type == "userBookmark":
        entries.append([seconds, seconds, "bookmark", "USER TAG", ""])
      elif message_type == "selfdriveState":
        state = message.selfdriveState
        if engagement_index is not None:
          entries[engagement_index][1] = seconds
        if state.enabled:
          if engagement_index is None:
            engagement_index = len(entries)
            entries.append([seconds, seconds, "engaged", "", ""])
        else:
          engagement_index = None

        if alert_index is not None:
          entries[alert_index][1] = seconds
        if int(state.alertSize.raw) != 0:
          alert_kind = ("info", "warning", "critical")[int(state.alertStatus.raw)]
          next_signature = (alert_kind, str(state.alertText1), str(state.alertText2))
          if alert_signature != next_signature:
            alert_index = len(entries)
            alert_signature = next_signature
            entries.append([seconds, seconds, alert_kind, str(state.alertText1), str(state.alertText2)])
        else:
          alert_index = None
          alert_signature = None
    timeline_entries = tuple(
      ReplayTimelineEntry(float(start), float(end), str(kind), str(title), str(detail))
      for start, end, kind, title, detail in entries
    )
    output_queue.put(ReplayTimeline(route_offset, end_time, timeline_entries, car_fingerprint))
  except Exception:
    output_queue.put(ReplayTimeline(route_offset, end_time, (), car_fingerprint))


def stop_timeline_process(process) -> None:
  if process is not None and process.is_alive():
    process.terminate()
    process.join(timeout=1.0)


def start_timeline_process(process_context, process, output_queue, route: str):
  stop_timeline_process(process)
  while True:
    try:
      output_queue.get_nowait()
    except queue.Empty:
      break
  process = process_context.Process(target=replay_timeline_worker, args=(route, output_queue), daemon=True)
  process.start()
  return process


def format_download_progress(current: int, total: int) -> str:
  if total <= 0:
    return "--"
  percent = int(np.clip(current / total, 0.0, 1.0) * 100)
  return f"{current / (1024 * 1024):.1f}/{total / (1024 * 1024):.1f} MB ({percent}%)"


@dataclass(frozen=True)
class DisplayTrack:
  trackId: int
  dRel: float
  yRel: float
  vRel: float
  aRel: float
  canAddress: int = -1
  canBus: int = -1


@dataclass(frozen=True)
class DisplaySource:
  startAddress: int
  endAddress: int
  bus: int
  trackCount: int


@dataclass(frozen=True)
class DisplayTrackSignals:
  trackId: int
  relLatSpeed: float
  absSpeed: float
  width: float
  length: float
  orientationAngle: float
  age: int
  coastAge: int
  state: int
  stateAlt: int
  trackCounter: int


@dataclass(frozen=True)
class RadarSnapshot:
  points: tuple[DisplayTrack, ...] = ()
  trackSources: tuple[DisplaySource, ...] = ()
  trackSignals: tuple[DisplayTrackSignals, ...] = ()
  radarTracksAvailable: bool = False


def make_radar_snapshot(radar_data, track_signals: tuple[DisplayTrackSignals, ...] = (),
                        track_locations: dict[int, tuple[int, int]] | None = None) -> RadarSnapshot:
  track_locations = track_locations or {}
  return RadarSnapshot(
    points=tuple(DisplayTrack(
      trackId=int(point.trackId),
      dRel=float(point.dRel),
      yRel=float(point.yRel),
      vRel=float(point.vRel),
      aRel=float(point.aRel),
      canAddress=track_locations.get(int(point.trackId), (-1, -1))[0],
      canBus=track_locations.get(int(point.trackId), (-1, -1))[1],
    ) for point in radar_data.points),
    trackSources=tuple(DisplaySource(
      startAddress=int(source.startAddress),
      endAddress=int(source.endAddress),
      bus=int(source.bus),
      trackCount=int(source.trackCount),
    ) for source in radar_data.trackSources),
    trackSignals=track_signals,
    radarTracksAvailable=bool(radar_data.radarTracksAvailable),
  )


def source_name(start_address: int, end_address: int) -> str:
  spec = SPEC_BY_RANGE.get((start_address, end_address))
  return spec.name if spec is not None else f"RADAR_{start_address:X}_{end_address:X}"


def source_details(start_address: int, end_address: int) -> str:
  spec = SPEC_BY_RANGE.get((start_address, end_address))
  if spec is None:
    return "unknown format"
  return f"{spec.frequency} Hz  {spec.message_size} B"


def radar_source_sort_key(source) -> tuple[bool, int, int, int]:
  spec = SPEC_BY_RANGE.get((source.startAddress, source.endAddress))
  return (
    spec is None or spec.name != PREFERRED_RADAR_SOURCE,
    source.startAddress,
    source.endAddress,
    source.bus,
  )


def radar_source_key(source) -> RadarSourceKey:
  return int(source.startAddress), int(source.endAddress), int(source.bus)


def source_filter_state(source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]],
                        source_key: RadarSourceKey) -> tuple[bool, bool, bool]:
  return source_filters.get(source_key, DEFAULT_SOURCE_FILTERS)


def toggle_source_filter(source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]],
                         source_key: RadarSourceKey, filter_index: int) -> None:
  filters = list(source_filter_state(source_filters, source_key))
  filters[filter_index] = not filters[filter_index]
  source_filters[source_key] = (filters[0], filters[1], filters[2])


def dbc_motion_class(motion_state: int | None) -> str:
  if motion_state is None:
    return "unknown"
  return {0: "unknown (raw 0)", 1: "stationary", 2: "moving"}.get(
    motion_state, f"unknown (raw {motion_state})",
  )


def dbc_motion_color(motion_state: int | None) -> rl.Color:
  return {0: MUTED, 1: WHITE, 2: PURPLE}.get(motion_state, MUTED)


def dbc_unknown_raw_label(motion_state: int | None) -> str | None:
  if motion_state in (1, 2):
    return None
  return "DBC unknown" if motion_state is None else f"DBC raw={motion_state}"


def display_track_color(track, motion_states: dict[int, int]) -> rl.Color:
  return dbc_motion_color(motion_states.get(int(track.trackId)))


def filter_tracks(tracks, motion_states: dict[int, int], track_locations: dict[int, tuple[int, int]], sources,
                  source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]]):
  filtered_tracks = []
  for track in tracks:
    address, bus = track_locations.get(int(track.trackId), (-1, -1))
    source = next((
      source for source in sources
      if source.startAddress <= address <= source.endAddress and source.bus == bus
    ), None)
    filters = source_filter_state(source_filters, radar_source_key(source)) if source is not None else DEFAULT_SOURCE_FILTERS
    motion_state = motion_states.get(int(track.trackId))
    if ((filters[0] and motion_state == 2)
        or (filters[1] and motion_state == 1)
        or (filters[2] and motion_state not in (1, 2))):
      continue
    filtered_tracks.append(track)
  return filtered_tracks


def enable_dbc_detail_signals(radar_interface: RadarInterface, enhanced_parsers: set[tuple[str, int]]) -> None:
  """Add visualization-only signals to the branch parser without maintaining a second CAN decoder."""
  for radar_parser in radar_interface.radar_parsers:
    parser_key = (radar_parser.spec.name, radar_parser.bus)
    if parser_key in enhanced_parsers or radar_parser.spec.name != "RADAR_3A5_3C4":
      continue

    # This UI can intentionally run slower than replay and uses conflated CAN, so don't apply parser liveness checks here.
    messages = [(f"RADAR_TRACK_{addr:x}", 0) for addr in radar_parser.spec.address_range]
    parser = CANParser(
      radar_parser.spec.dbc_name,
      messages,
      radar_parser.bus,
      signals={*radar_parser.spec.signals, *RADAR_DETAIL_SIGNALS},
    )
    for message_state in parser.message_states.values():
      message_state.ignore_alive = True
    radar_parser.parser = parser
    enhanced_parsers.add(parser_key)


def get_dbc_track_details(
  radar_interface: RadarInterface,
) -> tuple[dict[int, int], tuple[DisplayTrackSignals, ...], dict[int, tuple[int, int]]]:
  states = {}
  details = []
  locations = {}
  for track_key, point in radar_interface.pts.items():
    if not isinstance(track_key, tuple):
      continue

    spec = SPEC_BY_NAME.get(track_key[0])
    if spec is None:
      continue
    stored_address = track_key[1]
    can_address = stored_address // 2 if len(spec.track_prefixes) > 1 else stored_address
    active_bus = radar_interface.active_radar_buses.get(track_key[0])
    locations[int(point.trackId)] = (can_address, active_bus if active_bus is not None else -1)

    if track_key[0] != "RADAR_3A5_3C4":
      continue

    radar_parser = next((parser for parser in radar_interface.radar_parsers
                         if parser.spec.name == track_key[0] and parser.bus == active_bus), None)
    if radar_parser is None:
      continue

    message = radar_parser.parser.vl[f"RADAR_TRACK_{track_key[1]:x}"]
    if "MOTION_STATE" in message:
      states[int(point.trackId)] = int(message["MOTION_STATE"])
      details.append(DisplayTrackSignals(
        trackId=int(point.trackId),
        relLatSpeed=float(message["REL_LAT_SPEED"]),
        absSpeed=float(message["ABS_SPEED"]),
        width=float(message["WIDTH"]),
        length=float(message["LENGTH"]),
        orientationAngle=float(message["ORIENTATION_ANGLE"]),
        age=int(message["AGE"]),
        coastAge=int(message["COAST_AGE"]),
        state=int(message["STATE"]),
        stateAlt=int(message["STATE_ALT"]),
        trackCounter=int(message["TRACK_COUNTER"]),
      ))
  return states, tuple(details), locations


def match_decoded_track_values(tracks, decoded_tracks, decoded_values: dict):
  """Match liveTracks points to the independent CAN decoder for side-by-side comparison."""
  matched = {}
  for track in tracks:
    best_track = None
    best_score = math.inf
    for decoded in decoded_tracks:
      score = abs(track.dRel - decoded.dRel) + 2.0 * abs(track.yRel - decoded.yRel) + 0.25 * abs(track.vRel - decoded.vRel)
      if score < best_score:
        best_track, best_score = decoded, score
    if best_track is not None and best_score < 2.0 and int(best_track.trackId) in decoded_values:
      matched[int(track.trackId)] = decoded_values[int(best_track.trackId)]
  return matched


def replace_queued_value(output_queue, value) -> None:
  try:
    output_queue.put_nowait(value)
  except queue.Full:
    try:
      output_queue.get_nowait()
    except queue.Empty:
      return
    try:
      output_queue.put_nowait(value)
    except queue.Full:
      # The queue feeder can still own the slot briefly; the next publish will replace it.
      pass


def radar_decoder_worker(addr: str, output_queue) -> None:
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  logging.getLogger("carlog").setLevel(logging.ERROR)
  messaging.reset_context()
  sm = messaging.SubMaster(["can"], addr=addr)
  radar_cp = structs.CarParams.new_message()
  radar_cp.carFingerprint = "RADAR_UI"
  radar_cp.flags = 0
  radar_cp_sp = structs.CarParamsSP(flags=HyundaiFlagsSP.RADAR_FULL_RADAR.value)
  radar_interface = RadarInterface(radar_cp, radar_cp_sp)
  enhanced_parsers: set[tuple[str, int]] = set()
  snapshot = RadarSnapshot()
  motion_states: dict[int, int] = {}
  last_publish_time = 0.0

  while True:
    sm.update(100)
    radar_data = None
    if sm.updated["can"]:
      can_messages = [(message.address, bytes(message.dat), message.src) for message in sm["can"]]
      radar_data = radar_interface.update([(sm.logMonoTime["can"], can_messages)])
      enable_dbc_detail_signals(radar_interface, enhanced_parsers)
      if radar_data is not None:
        motion_states, track_signals, track_locations = get_dbc_track_details(radar_interface)
        snapshot = make_radar_snapshot(radar_data, track_signals, track_locations)

    now = time.monotonic()
    if radar_data is not None or now - last_publish_time >= 0.1:
      replace_queued_value(output_queue, (snapshot, motion_states, sm.alive["can"], sm.seen["can"]))
      last_publish_time = now


def draw_text(font, text: str, x: float, y: float, size: float, color: rl.Color = TEXT) -> None:
  rl.draw_text_ex(font, text, rl.Vector2(round(x), round(y)), size, 0, color)


def measure_standalone_text(font, text: str, size: float) -> rl.Vector2:
  return rl.measure_text_ex(font, text, size, 0)  # noqa: TID251 - standalone raylib tool


def fit_overlay_text(font, text: str, size: float, max_width: float) -> str:
  text = " ".join(text.split())
  if measure_standalone_text(font, text, size).x <= max_width:
    return text
  suffix = "..."
  while text and measure_standalone_text(font, text + suffix, size).x > max_width:
    text = text[:-1]
  return text.rstrip() + suffix if text else suffix


def current_replay_events(timeline: ReplayTimeline, route_seconds: float) -> list[ReplayTimelineEntry]:
  events = []
  for entry in timeline.entries:
    if entry.kind == "bookmark" and 0.0 <= route_seconds - entry.start <= 2.0:
      events.append(entry)
    elif entry.kind in ("info", "warning", "critical"):
      visible_end = max(entry.end + 0.25, entry.start + 1.0)
      if entry.start - 0.1 <= route_seconds <= visible_end:
        events.append(entry)
  priority = {"critical": 3, "warning": 2, "info": 1, "bookmark": 0}
  return sorted(events, key=lambda entry: (priority[entry.kind], entry.start), reverse=True)[:2]


def draw_replay_event_overlay(font, bounds: rl.Rectangle, top: float,
                              timeline: ReplayTimeline, route_seconds: float) -> None:
  events = current_replay_events(timeline, route_seconds)
  if not events:
    return

  event_colors = {
    "bookmark": CYAN,
    "info": GREEN,
    "warning": ORANGE,
    "critical": RED,
  }
  event_labels = {
    "bookmark": "USER TAG",
    "info": "INFO ALERT",
    "warning": "WARNING",
    "critical": "CRITICAL ALERT",
  }
  width = min(max(340.0, bounds.width * 0.62), bounds.width - 24.0)
  y = max(bounds.y + 12.0, top)
  for entry in events:
    body_lines = [line for line in (entry.title, entry.detail) if line and line != event_labels[entry.kind]]
    height = 42.0 + len(body_lines) * 22.0
    if y + height > bounds.y + bounds.height - 12.0:
      break
    rect = rl.Rectangle(bounds.x + (bounds.width - width) / 2, y, width, height)
    color = event_colors[entry.kind]
    rl.draw_rectangle_rounded(rect, 0.12, 6, rl.Color(4, 8, 14, 225))
    rl.draw_rectangle_rounded_lines_ex(rect, 0.12, 6, 1.0, color)
    rl.draw_rectangle_rec(rl.Rectangle(rect.x, rect.y, 5, rect.height), color)
    draw_text(font, event_labels[entry.kind], rect.x + 16, rect.y + 10, 16, color)
    for index, line in enumerate(body_lines):
      fitted = fit_overlay_text(font, line, 18 if index == 0 else 15, rect.width - 32)
      draw_text(font, fitted, rect.x + 16, rect.y + 34 + index * 22, 18 if index == 0 else 15, TEXT)
    y += height + 8


def edit_key_pressed(key) -> bool:
  return rl.is_key_pressed(key) or rl.is_key_pressed_repeat(key)


def replay_keyboard_command() -> str | None:
  shift_down = (
    rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT)
    or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)
  )
  for key, command in (
    (rl.KeyboardKey.KEY_S, "S" if shift_down else "s"),
    (rl.KeyboardKey.KEY_M, "M" if shift_down else "m"),
    (rl.KeyboardKey.KEY_SPACE, " "),
    (rl.KeyboardKey.KEY_E, "e"),
    (rl.KeyboardKey.KEY_D, "d"),
    (rl.KeyboardKey.KEY_T, "t"),
    (rl.KeyboardKey.KEY_I, "i"),
    (rl.KeyboardKey.KEY_W, "w"),
    (rl.KeyboardKey.KEY_C, "c"),
    (rl.KeyboardKey.KEY_EQUAL, "+"),
    (rl.KeyboardKey.KEY_KP_ADD, "+"),
    (rl.KeyboardKey.KEY_MINUS, "-"),
    (rl.KeyboardKey.KEY_KP_SUBTRACT, "-"),
    (rl.KeyboardKey.KEY_Q, "q"),
  ):
    if rl.is_key_pressed(key):
      return command
  return None


def camera_content_rect(camera_view: CameraView, rect: rl.Rectangle) -> rl.Rectangle:
  if camera_view.frame is None:
    return rect

  widget_aspect = rect.width / rect.height
  frame_aspect = camera_view.frame.width / camera_view.frame.height
  width = rect.width * min(frame_aspect / widget_aspect, 1.0)
  height = rect.height * min(widget_aspect / frame_aspect, 1.0)
  return rl.Rectangle(
    rect.x + (rect.width - width) / 2,
    rect.y + (rect.height - height) / 2,
    width,
    height,
  )


def build_camera_calibration(camera, rpy_calib: np.ndarray, wide_from_device_euler: np.ndarray | None = None):
  calibration_scale = camera.width / CAMERA_BUFFER_WIDTH
  calibration = Calibration(1, rpy_calib, camera.intrinsics, calibration_scale)
  if wide_from_device_euler is not None:
    calibration.extrinsics_matrix = (
      view_frame_from_device_frame @ rot_from_euler(wide_from_device_euler) @ rot_from_euler(rpy_calib)
    )
  projection_height = float(np.clip(camera.height / calibration_scale, 1, CAMERA_BUFFER_HEIGHT))
  return calibration, projection_height


def aligned_road_camera_rect(device_camera, wide_content_rect: rl.Rectangle,
                             wide_from_device_euler: np.ndarray) -> rl.Rectangle:
  road_camera = device_camera.fcam
  wide_camera = device_camera.ecam
  wide_from_road_view = (
    view_frame_from_device_frame @ rot_from_euler(wide_from_device_euler) @ view_frame_from_device_frame.T
  )
  homography = wide_camera.intrinsics @ wide_from_road_view @ np.linalg.inv(road_camera.intrinsics)
  road_corners = np.asarray([
    [0.0, 0.0, 1.0],
    [road_camera.width, 0.0, 1.0],
    [road_camera.width, road_camera.height, 1.0],
    [0.0, road_camera.height, 1.0],
  ]).T
  mapped = homography @ road_corners
  mapped = (mapped[:2] / mapped[2]).T
  x = wide_content_rect.x + mapped[:, 0] / wide_camera.width * wide_content_rect.width
  y = wide_content_rect.y + mapped[:, 1] / wide_camera.height * wide_content_rect.height
  left = float(np.clip(np.min(x), wide_content_rect.x, wide_content_rect.x + wide_content_rect.width))
  right = float(np.clip(np.max(x), wide_content_rect.x, wide_content_rect.x + wide_content_rect.width))
  top = float(np.clip(np.min(y), wide_content_rect.y, wide_content_rect.y + wide_content_rect.height))
  bottom = float(np.clip(np.max(y), wide_content_rect.y, wide_content_rect.y + wide_content_rect.height))
  return rl.Rectangle(left, top, max(1.0, right - left), max(1.0, bottom - top))


def camera_track_geometry(calibration: Calibration | None, track, camera_rect: rl.Rectangle,
                          projection_height: float) -> tuple[float, float, float] | None:
  if calibration is None or not (math.isfinite(track.dRel) and math.isfinite(track.yRel) and math.isfinite(track.vRel)):
    return None
  projected = calibration.car_space_to_bb(
    np.asarray([track.dRel]),
    np.asarray([-track.yRel]),
    np.asarray([1.2]),
  )[0]
  if not np.all(np.isfinite(projected)):
    return None

  x = camera_rect.x + float(projected[0]) * camera_rect.width / CAMERA_BUFFER_WIDTH
  y = camera_rect.y + float(projected[1]) * camera_rect.height / projection_height
  if not rl.check_collision_point_rec(rl.Vector2(x, y), camera_rect):
    return None
  return x, y, float(np.clip(18.0 - track.dRel / 18.0, 7.0, 16.0))


def top_down_track_geometry(rect: rl.Rectangle, track) -> tuple[float, float, float] | None:
  if not (math.isfinite(track.dRel) and math.isfinite(track.yRel) and math.isfinite(track.vRel)):
    return None
  if not (0 <= track.dRel <= MAX_FORWARD_DISTANCE and abs(track.yRel) <= MAX_LATERAL_DISTANCE):
    return None
  plot = rl.Rectangle(rect.x + 48, rect.y + 44, rect.width - 72, rect.height - 72)
  center_x = plot.x + plot.width / 2
  car_y = plot.y + plot.height - 18
  return (
    center_x - track.yRel * plot.width / (MAX_LATERAL_DISTANCE * 2),
    car_y - track.dRel * (plot.height - 18) / MAX_FORWARD_DISTANCE,
    9.0,
  )


def hovered_track_id(tracks, geometry, mouse: rl.Vector2) -> int | None:
  best_id = None
  best_distance = math.inf
  for track in tracks:
    point = geometry(track)
    if point is None:
      continue
    x, y, radius = point
    distance = math.hypot(mouse.x - x, mouse.y - y)
    if distance <= radius + 6.0 and distance < best_distance:
      best_id = int(track.trackId)
      best_distance = distance
  return best_id


def retain_selected_track_id(selected_id: int | None, hovered_id: int | None, tracks) -> int | None:
  if hovered_id is not None:
    return hovered_id
  if selected_id is not None and any(int(track.trackId) == selected_id for track in tracks):
    return selected_id
  return None


def track_source_index(track, track_locations: dict[int, tuple[int, int]], sources) -> int:
  address, bus = track_locations.get(int(track.trackId), (-1, -1))
  return next((
    index for index, source in enumerate(sorted(sources, key=radar_source_sort_key))
    if source.startAddress <= address <= source.endAddress and source.bus == bus
  ), -1)


def draw_track_source_marker(center: rl.Vector2, radius: float, color: rl.Color, source_index: int) -> None:
  if source_index <= 0:
    rl.draw_circle_v(center, radius * SOURCE_CIRCLE_RADIUS_SCALE, color)
    return
  sides = (4, 3, 5, 6)[(source_index - 1) % 4]
  rotation = 45.0 if sides == 4 else -90.0
  rl.draw_poly(center, sides, radius, rotation, color)


def draw_track_popup(font, track, x: float, y: float, radius: float, bounds: rl.Rectangle, color: rl.Color,
                     motion_state: int | None) -> None:
  label = f"#{track.trackId}  {track.dRel:.1f} m  {track.vRel:+.1f} m/s"
  if (raw_label := dbc_unknown_raw_label(motion_state)) is not None:
    label += f"  {raw_label}"
  label_size = measure_text_cached(font, label, 18)
  label_x = float(np.clip(x - label_size.x / 2, bounds.x + 5, bounds.x + bounds.width - label_size.x - 5))
  label_y = max(bounds.y + 5, y - radius - 29)
  rl.draw_rectangle_rounded(
    rl.Rectangle(label_x - 5, label_y - 2, label_size.x + 10, 24), 0.25, 4, rl.Color(0, 0, 0, 220),
  )
  draw_text(font, label, label_x, label_y, 18, color)


def draw_camera_tracks(font, calibration: Calibration | None, tracks, camera_rect: rl.Rectangle,
                       show_labels: bool, motion_states: dict[int, int],
                       track_locations: dict[int, tuple[int, int]], sources,
                       projection_height: float, hovered_id: int | None, selected_id: int | None,
                       preview_id: int | None = None) -> None:
  if calibration is None:
    return

  for track in tracks:
    geometry = camera_track_geometry(calibration, track, camera_rect, projection_height)
    if geometry is None:
      continue
    x, y, radius = geometry
    dot_radius = max(4.5, radius * 0.68)

    color = display_track_color(track, motion_states)
    is_hovered = int(track.trackId) == hovered_id
    is_selected = int(track.trackId) == selected_id
    is_previewed = int(track.trackId) == preview_id and not is_selected
    center = rl.Vector2(x, y)
    source_index = track_source_index(track, track_locations, sources)
    draw_track_source_marker(center, dot_radius + 3.0, rl.Color(0, 0, 0, 180), source_index)
    if is_selected:
      rl.draw_circle_lines_v(center, dot_radius + 4.0, CYAN)
    elif is_previewed:
      rl.draw_circle_lines_v(center, dot_radius + 4.0, ORANGE)
    draw_track_source_marker(center, dot_radius, color, source_index)
    rl.draw_circle_v(center, max(1.5, dot_radius * 0.32), BACKGROUND)

    if show_labels or is_hovered:
      draw_track_popup(font, track, x, y, dot_radius, camera_rect, color, motion_states.get(int(track.trackId)))


def draw_fused_camera_mode(font, road_camera_view: CameraView, wide_camera_view: CameraView, device_camera,
                           rpy_calib: np.ndarray, wide_from_device_euler: np.ndarray, full_rect: rl.Rectangle,
                           tracks, show_labels: bool, motion_states: dict[int, int],
                           track_locations: dict[int, tuple[int, int]], sources,
                           selected_id: int | None) -> int | None:
  wide_render_rect = rl.Rectangle(
    full_rect.x - full_rect.width * (FUSED_CAMERA_ZOOM - 1.0) / 2,
    full_rect.y - full_rect.height * (FUSED_CAMERA_ZOOM - 1.0) / 2,
    full_rect.width * FUSED_CAMERA_ZOOM,
    full_rect.height * FUSED_CAMERA_ZOOM,
  )
  wide_camera_view.render(wide_render_rect)
  wide_content_rect = camera_content_rect(wide_camera_view, wide_render_rect)
  if device_camera is None:
    return retain_selected_track_id(selected_id, None, tracks)

  road_rect = aligned_road_camera_rect(device_camera, wide_content_rect, wide_from_device_euler)
  road_camera_view.render(road_rect)
  road_content_rect = camera_content_rect(road_camera_view, road_rect)
  road_calibration, road_projection_height = build_camera_calibration(device_camera.fcam, rpy_calib)
  wide_calibration, wide_projection_height = build_camera_calibration(
    device_camera.ecam, rpy_calib, wide_from_device_euler,
  )

  road_track_ids = {
    int(track.trackId) for track in tracks
    if camera_track_geometry(road_calibration, track, road_content_rect, road_projection_height) is not None
  }
  road_tracks = [track for track in tracks if int(track.trackId) in road_track_ids]
  wide_tracks = [track for track in tracks if int(track.trackId) not in road_track_ids]

  mouse_position = rl.get_mouse_position()
  road_hovered_id = hovered_track_id(
    road_tracks,
    lambda track: camera_track_geometry(road_calibration, track, road_content_rect, road_projection_height),
    mouse_position,
  ) if rl.check_collision_point_rec(mouse_position, road_content_rect) else None
  wide_hovered_id = hovered_track_id(
    wide_tracks,
    lambda track: camera_track_geometry(wide_calibration, track, wide_content_rect, wide_projection_height),
    mouse_position,
  ) if road_hovered_id is None and rl.check_collision_point_rec(mouse_position, wide_content_rect) else None
  current_hovered_id = road_hovered_id if road_hovered_id is not None else wide_hovered_id
  selected_id = retain_selected_track_id(selected_id, current_hovered_id, tracks)

  draw_camera_tracks(font, wide_calibration, wide_tracks, wide_content_rect, show_labels, motion_states,
                     track_locations, sources, wide_projection_height, wide_hovered_id, selected_id)
  draw_camera_tracks(font, road_calibration, road_tracks, road_content_rect, show_labels, motion_states,
                     track_locations, sources, road_projection_height, road_hovered_id, selected_id)
  return selected_id


def draw_model_line(points_x, points_y, center_x: float, car_y: float, longitudinal_scale: float,
                    lateral_scale: float, color: rl.Color, width: float) -> None:
  previous = None
  for forward, lateral in zip(points_x, points_y, strict=True):
    if not (0.0 <= forward <= MAX_FORWARD_DISTANCE and abs(lateral) <= MAX_LATERAL_DISTANCE):
      previous = None
      continue
    current = rl.Vector2(center_x + lateral * lateral_scale, car_y - forward * longitudinal_scale)
    if previous is not None:
      edge_alpha = min(80, color.a)
      rl.draw_line_ex(previous, current, width + 2.0, rl.Color(color.r, color.g, color.b, edge_alpha))
      rl.draw_line_ex(previous, current, width, color)
    previous = current


def draw_top_down(font, rect: rl.Rectangle, tracks, show_labels: bool, model,
                  motion_states: dict[int, int], hide_moving: bool, hide_stationary: bool,
                  hide_unknown: bool, track_locations: dict[int, tuple[int, int]], sources,
                  hovered_id: int | None, selected_id: int | None,
                  preview_id: int | None = None) -> None:
  rl.draw_rectangle_rec(rect, PANEL)
  plot = rl.Rectangle(rect.x + 48, rect.y + 44, rect.width - 72, rect.height - 72)
  center_x = plot.x + plot.width / 2
  car_y = plot.y + plot.height - 18
  longitudinal_scale = (plot.height - 18) / MAX_FORWARD_DISTANCE
  lateral_scale = plot.width / (MAX_LATERAL_DISTANCE * 2)

  scale_x = plot.x - 5
  scale_top = car_y - MAX_FORWARD_DISTANCE * longitudinal_scale
  rl.draw_line_ex(rl.Vector2(scale_x, scale_top), rl.Vector2(scale_x, car_y), 1.0, rl.Color(MUTED.r, MUTED.g, MUTED.b, 110))
  for distance in range(0, int(MAX_FORWARD_DISTANCE) + 1, 20):
    y = car_y - distance * longitudinal_scale
    rl.draw_line_ex(rl.Vector2(scale_x - 7, y), rl.Vector2(scale_x, y), 1.0, MUTED)
    label = f"{distance}m"
    label_size = measure_text_cached(font, label, 14)
    draw_text(font, label, scale_x - label_size.x - 10, y - 7, 14, MUTED)

  legend = (
    (PURPLE, "moving", hide_moving),
    (WHITE, "stationary", hide_stationary),
    (MUTED, "unknown", hide_unknown),
  )
  legend_x = rect.x + rect.width - 150
  legend_y = rect.y + 50
  for index, (color, label, disabled) in enumerate(legend):
    y = legend_y + index * 23
    rl.draw_circle(int(legend_x), int(y + 7), 5, color)
    draw_text(font, label, legend_x + 12, y, 15, TEXT)
    if disabled:
      label_width = measure_standalone_text(font, label, 15).x
      rl.draw_line_ex(
        rl.Vector2(legend_x + 10, y + 8),
        rl.Vector2(legend_x + 14 + label_width, y + 8),
        1.5,
        MUTED,
      )

  if model is not None:
    for lane_line, probability in zip(model.laneLines, model.laneLineProbs, strict=True):
      alpha = int(np.clip(probability, 0.15, 1.0) * 210)
      draw_model_line(lane_line.x, lane_line.y, center_x, car_y, longitudinal_scale, lateral_scale,
                      rl.Color(0, 255, 126, alpha), 2.0)
    for road_edge, std in zip(model.roadEdges, model.roadEdgeStds, strict=True):
      alpha = int(np.clip(1.0 - std, 0.1, 1.0) * 150)
      draw_model_line(road_edge.x, road_edge.y, center_x, car_y, longitudinal_scale, lateral_scale,
                      rl.Color(255, 76, 89, alpha), 1.0)
    draw_model_line(model.position.x, model.position.y, center_x, car_y, longitudinal_scale, lateral_scale,
                    rl.Color(72, 220, 255, 45), 0.75)

  ego_car_rect = rl.Rectangle(center_x - 13, car_y - 25, 26, 48)
  rl.draw_rectangle_rounded(ego_car_rect, 0.3, 6, rl.Color(82, 94, 108, 210))
  rl.draw_rectangle_rounded_lines_ex(
    ego_car_rect, 0.3, 6, 1.0, rl.Color(MUTED.r, MUTED.g, MUTED.b, 150),
  )

  for track in tracks:
    geometry = top_down_track_geometry(rect, track)
    if geometry is None:
      continue
    x, y, radius = geometry
    color = display_track_color(track, motion_states)
    is_hovered = int(track.trackId) == hovered_id
    is_selected = int(track.trackId) == selected_id
    is_previewed = int(track.trackId) == preview_id and not is_selected
    center = rl.Vector2(x, y)
    source_index = track_source_index(track, track_locations, sources)
    draw_track_source_marker(center, radius, rl.Color(0, 0, 0, 180), source_index)
    if is_selected:
      rl.draw_circle_lines_v(rl.Vector2(x, y), radius + 3.0, CYAN)
    elif is_previewed:
      rl.draw_circle_lines_v(rl.Vector2(x, y), radius + 3.0, ORANGE)
    draw_track_source_marker(center, 6.0, color, source_index)
    if show_labels:
      raw_label = dbc_unknown_raw_label(motion_states.get(int(track.trackId)))
      label = f"{track.trackId}  {raw_label}" if raw_label is not None else f"{track.trackId}"
      draw_text(font, label, x + 9, y - 9, 16, color)
    elif is_hovered:
      draw_track_popup(font, track, x, y, radius, rect, color, motion_states.get(int(track.trackId)))


def table_capacity(rect: rl.Rectangle) -> int:
  return max(1, int((rect.height - 62) // 24))


def table_hovered_track_id(tracks, rect: rl.Rectangle, scroll: int, mouse: rl.Vector2) -> int | None:
  if not rl.check_collision_point_rec(mouse, rect):
    return None
  row_top = rect.y + 56
  if mouse.y < row_top:
    return None
  row = int((mouse.y - row_top) // 24)
  sorted_tracks = sorted(tracks, key=lambda track: (track.dRel, track.trackId))
  visible = sorted_tracks[scroll:scroll + table_capacity(rect)]
  return int(visible[row].trackId) if 0 <= row < len(visible) else None


def dbc_track_state(state: int) -> str:
  return {0: "empty", 1: "tent 1", 2: "tent 2", 3: "measured", 4: "coasted", 7: "unresolved"}.get(state, str(state))


def draw_track_table(font, rect: rl.Rectangle, tracks, motion_states: dict[int, int], scroll: int,
                     selected_id: int | None, hovered_id: int | None,
                     track_signals: dict[int, DisplayTrackSignals], track_locations: dict[int, tuple[int, int]],
                     table_mode: str) -> None:
  rl.draw_rectangle_rec(rect, BACKGROUND)
  rl.draw_line_ex(rl.Vector2(rect.x, rect.y), rl.Vector2(rect.x + rect.width, rect.y), 2.0, GRID)
  sorted_tracks = sorted(tracks, key=lambda track: (track.dRel, track.trackId))
  capacity = table_capacity(rect)
  visible = sorted_tracks[scroll:scroll + capacity]

  draw_text(font, f"TRACK {table_mode.upper()}", rect.x + 12, rect.y + 8, 21, TEXT)
  if sorted_tracks:
    draw_text(font, f"{scroll + 1}-{scroll + len(visible)} / {len(sorted_tracks)}", rect.x + rect.width - 112, rect.y + 11, 16, MUTED)

  if table_mode == "kinematics":
    columns = (
      ("ID", 0.02), ("CAN", 0.08), ("DIST", 0.19), ("LAT", 0.29), ("REL V", 0.39), ("LAT V", 0.50),
      ("REL A", 0.61), ("ABS V", 0.73), ("AGE", 0.88),
    )
  elif table_mode == "object":
    columns = (
      ("ID", 0.02), ("CAN", 0.09), ("WIDTH", 0.21), ("LENGTH", 0.33), ("ANGLE", 0.45), ("STATE", 0.57),
      ("COAST", 0.74), ("UPD", 0.87),
    )
  else:
    columns = (
      ("ID", 0.02), ("CAN", 0.10), ("DIST", 0.24), ("LAT", 0.38), ("REL V", 0.52),
      ("DBC MOTION", 0.70),
    )
  header_y = rect.y + 36
  for title, offset in columns:
    draw_text(font, title, rect.x + rect.width * offset, header_y, 15, MUTED)

  for row, track in enumerate(visible):
    y = header_y + 23 + row * 24
    if int(track.trackId) == selected_id:
      rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(CYAN.r, CYAN.g, CYAN.b, 42))
      rl.draw_rectangle_lines_ex(rl.Rectangle(rect.x, y - 3, rect.width, 24), 1.0, CYAN)
    elif int(track.trackId) == hovered_id:
      rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(ORANGE.r, ORANGE.g, ORANGE.b, 32))
      rl.draw_rectangle_lines_ex(rl.Rectangle(rect.x, y - 3, rect.width, 24), 1.0, ORANGE)
    elif row % 2:
      rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(255, 255, 255, 8))
    motion_state = motion_states.get(int(track.trackId))
    detail = track_signals.get(int(track.trackId))
    can_address, can_bus = track_locations.get(int(track.trackId), (-1, -1))
    can_location = f"{can_address:X}/B{can_bus}" if can_address >= 0 and can_bus >= 0 else "n/a"
    if table_mode == "kinematics":
      values = (
        (str(track.trackId), 0.02, TEXT),
        (can_location, 0.08, TEXT if can_address >= 0 else MUTED),
        (f"{track.dRel:.1f}", 0.19, TEXT),
        (f"{track.yRel:+.1f}", 0.29, TEXT),
        (f"{track.vRel:+.1f}", 0.39, TEXT),
        (f"{detail.relLatSpeed:+.1f}" if detail else "n/a", 0.50, TEXT if detail else MUTED),
        (f"{track.aRel:+.1f}" if math.isfinite(track.aRel) else "n/a", 0.61, TEXT),
        (f"{detail.absSpeed:.1f}" if detail else "n/a", 0.73, TEXT if detail else MUTED),
        (str(detail.age) if detail else "n/a", 0.88, TEXT if detail else MUTED),
      )
    elif table_mode == "object":
      values = (
        (str(track.trackId), 0.02, TEXT),
        (can_location, 0.09, TEXT if can_address >= 0 else MUTED),
        (f"{detail.width:.1f}" if detail else "n/a", 0.21, TEXT if detail else MUTED),
        (f"{detail.length:.1f}" if detail else "n/a", 0.33, TEXT if detail else MUTED),
        (f"{detail.orientationAngle:+.0f}" if detail else "n/a", 0.45, TEXT if detail else MUTED),
        (dbc_track_state(detail.state) if detail else "n/a", 0.57, TEXT if detail else MUTED),
        (str(detail.coastAge) if detail else "n/a", 0.74, TEXT if detail else MUTED),
        (str(detail.trackCounter) if detail else "n/a", 0.87, TEXT if detail else MUTED),
      )
    else:
      values = (
        (str(track.trackId), 0.02, TEXT),
        (can_location, 0.10, TEXT if can_address >= 0 else MUTED),
        (f"{track.dRel:6.1f}", 0.24, TEXT),
        (f"{track.yRel:+6.1f}", 0.38, TEXT),
        (f"{track.vRel:+6.1f}", 0.52, TEXT),
        (dbc_motion_class(motion_state), 0.70, dbc_motion_color(motion_state)),
      )
    for value, offset, color in values:
      draw_text(font, value, rect.x + rect.width * offset, y, 15, color)


def draw_status_chip(font, label: str, x: float, y: float, color: rl.Color,
                     mouse_position: rl.Vector2, selected: bool | None = None,
                     selection_color: "rl.Color | None" = None) -> tuple[float, rl.Rectangle, bool]:
  size = measure_standalone_text(font, label, 15)
  width = size.x + 16
  chip_rect = rl.Rectangle(x, y, width, 25)
  hovered = rl.check_collision_point_rec(mouse_position, chip_rect)
  alpha = 72 if hovered else (52 if selected else 18) if selected is not None else 32
  rl.draw_rectangle_rounded(chip_rect, 0.3, 4, rl.Color(color.r, color.g, color.b, alpha))
  if hovered:
    rl.draw_rectangle_rounded_lines_ex(chip_rect, 0.3, 4, 1.0, color)
  elif selected:
    rl.draw_rectangle_rounded_lines_ex(chip_rect, 0.3, 4, 1.0, selection_color or color)
  draw_text(font, label, x + 8, y + 4, 15, color)
  return x + width + 7, chip_rect, hovered


def draw_status_tooltip(font, text: str, chip_rect: rl.Rectangle, bounds: rl.Rectangle) -> None:
  size = measure_text_cached(font, text, 15)
  width = size.x + 18
  x = float(np.clip(chip_rect.x, bounds.x + 5, bounds.x + bounds.width - width - 5))
  y = chip_rect.y + chip_rect.height + 6
  tooltip_rect = rl.Rectangle(x, y, width, 27)
  rl.draw_rectangle_rounded(tooltip_rect, 0.25, 4, rl.Color(0, 0, 0, 235))
  rl.draw_rectangle_rounded_lines_ex(tooltip_rect, 0.25, 4, 1.0, MUTED)
  draw_text(font, text, x + 9, y + 5, 15, TEXT)


def draw_status_parts(font, parts: tuple[tuple[str, str], ...], x: float, y: float, size: float, color: rl.Color,
                      mouse_position: rl.Vector2, separator: str) -> tuple[str, rl.Rectangle] | None:
  hovered_tooltip = None
  for index, (text, tooltip) in enumerate(parts):
    if index:
      draw_text(font, separator, x, y, size, color)
      x += measure_standalone_text(font, separator, size).x
    text_size = measure_standalone_text(font, text, size)
    text_rect = rl.Rectangle(x, y, text_size.x, max(size + 4, text_size.y))
    draw_text(font, text, x, y, size, color)
    if rl.check_collision_point_rec(mouse_position, text_rect):
      hovered_tooltip = (tooltip, text_rect)
    x += text_size.x
  return hovered_tooltip


def draw_route_dialog(font, bounds: rl.Rectangle, route: str, cursor_index: int, error: str,
                      select_all: bool) -> str | None:
  rl.draw_rectangle_rec(bounds, rl.Color(0, 0, 0, 190))
  width = min(760.0, bounds.width - 40.0)
  dialog = rl.Rectangle(bounds.x + (bounds.width - width) / 2, bounds.y + (bounds.height - 190.0) / 2, width, 190.0)
  rl.draw_rectangle_rounded(dialog, 0.08, 8, PANEL)
  rl.draw_rectangle_rounded_lines_ex(dialog, 0.08, 8, 1.0, MUTED)
  draw_text(font, "Open route", dialog.x + 20, dialog.y + 17, 22, TEXT)
  draw_text(font, "Paste a route or segment ID, then press Enter.", dialog.x + 20, dialog.y + 48, 15, MUTED)

  input_rect = rl.Rectangle(dialog.x + 20, dialog.y + 76, dialog.width - 40, 38)
  rl.draw_rectangle_rounded(input_rect, 0.15, 4, BACKGROUND)
  rl.draw_rectangle_rounded_lines_ex(input_rect, 0.15, 4, 1.0, CYAN)
  cursor_index = int(np.clip(cursor_index, 0, len(route)))
  view_start = 0
  view_end = len(route)
  while view_start < cursor_index and measure_standalone_text(font, route[view_start:cursor_index], 18).x > input_rect.width - 24:
    view_start += 1
  while view_end > cursor_index and measure_standalone_text(font, route[view_start:view_end], 18).x > input_rect.width - 24:
    view_end -= 1
  display_route = route[view_start:view_end]
  input_text = display_route
  if route and select_all:
    selection_width = min(measure_standalone_text(font, display_route, 18).x + 4, input_rect.width - 20)
    rl.draw_rectangle_rec(
      rl.Rectangle(input_rect.x + 8, input_rect.y + 7, selection_width, 24),
      rl.Color(CYAN.r, CYAN.g, CYAN.b, 70),
    )
  draw_text(font, input_text, input_rect.x + 10, input_rect.y + 9, 18, TEXT)
  if not select_all and int(time.monotonic() * 2) % 2 == 0:
    text_before_cursor = route[view_start:cursor_index]
    cursor_x = input_rect.x + 10 + measure_standalone_text(font, text_before_cursor, 18).x
    rl.draw_line_ex(rl.Vector2(cursor_x + 1, input_rect.y + 8), rl.Vector2(cursor_x + 1, input_rect.y + 30), 1.0, TEXT)

  if error:
    draw_text(font, error, dialog.x + 20, dialog.y + 124, 14, RED)

  mouse_position = rl.get_mouse_position()
  cancel_size = measure_standalone_text(font, "Cancel", 16)
  open_size = measure_standalone_text(font, "Open", 16)
  open_rect = rl.Rectangle(dialog.x + dialog.width - open_size.x - 44, dialog.y + 137, open_size.x + 24, 34)
  cancel_rect = rl.Rectangle(open_rect.x - cancel_size.x - 34, dialog.y + 137, cancel_size.x + 24, 34)
  cancel_hovered = rl.check_collision_point_rec(mouse_position, cancel_rect)
  open_hovered = rl.check_collision_point_rec(mouse_position, open_rect)
  rl.draw_rectangle_rounded(cancel_rect, 0.2, 4, rl.Color(MUTED.r, MUTED.g, MUTED.b, 55 if cancel_hovered else 28))
  rl.draw_rectangle_rounded(open_rect, 0.2, 4, rl.Color(CYAN.r, CYAN.g, CYAN.b, 75 if open_hovered else 42))
  draw_text(font, "Cancel", cancel_rect.x + (cancel_rect.width - cancel_size.x) / 2, cancel_rect.y + 8, 16, TEXT)
  draw_text(font, "Open", open_rect.x + (open_rect.width - open_size.x) / 2, open_rect.y + 8, 16, CYAN)
  rl.set_mouse_cursor(
    rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND if cancel_hovered or open_hovered else rl.MouseCursor.MOUSE_CURSOR_IBEAM,
  )
  if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251 - standalone raylib tool
    if cancel_hovered:
      return "cancel"
    if open_hovered:
      return "open"
  return None


def draw_route_loading(font, bounds: rl.Rectangle, route: str, elapsed: float) -> None:
  rl.draw_rectangle_rec(bounds, rl.Color(0, 0, 0, 175))
  width = min(580.0, bounds.width - 40.0)
  card = rl.Rectangle(bounds.x + (bounds.width - width) / 2, bounds.y + (bounds.height - 154.0) / 2, width, 154.0)
  rl.draw_rectangle_rounded(card, 0.1, 8, PANEL)
  rl.draw_rectangle_rounded_lines_ex(card, 0.1, 8, 1.0, MUTED)
  draw_text(font, "Loading route", card.x + 22, card.y + 19, 22, TEXT)
  draw_text(font, "Waiting for replay data...", card.x + 22, card.y + 51, 15, MUTED)

  route_text = route
  while route_text and measure_standalone_text(font, route_text, 15).x > card.width - 44:
    route_text = route_text[1:]
  draw_text(font, route_text, card.x + 22, card.y + 77, 15, CYAN)

  bar = rl.Rectangle(card.x + 22, card.y + 112, card.width - 44, 12)
  rl.draw_rectangle_rounded(bar, 0.5, 6, rl.Color(MUTED.r, MUTED.g, MUTED.b, 35))
  segment_width = min(140.0, bar.width * 0.3)
  segment_left = (elapsed * 190.0) % (bar.width + segment_width) - segment_width
  visible_left = max(0.0, segment_left)
  visible_right = min(bar.width, segment_left + segment_width)
  if visible_right > visible_left:
    progress = rl.Rectangle(bar.x + visible_left, bar.y, visible_right - visible_left, bar.height)
    rl.draw_rectangle_rounded(progress, 0.5, 6, CYAN)


def draw_replay_timeline(font, bounds: rl.Rectangle, timeline: ReplayTimeline,
                         route_seconds: float, scrub: ReplayScrubState,
                         download_current: int, download_total: int) -> tuple[str | None, bool]:
  timeline_rect = rl.Rectangle(bounds.x + 12, bounds.y + 68, bounds.width - 24, 16)
  rl.draw_rectangle_rounded(timeline_rect, 0.25, 4, rl.Color(25, 65, 135, 150))
  duration = timeline.end - timeline.start
  if duration <= 0.0:
    scrub.active = False
    scrub.preview_seconds = None
    return None, False

  mouse_position = rl.get_mouse_position()
  hovered = rl.check_collision_point_rec(mouse_position, timeline_rect)
  download_ratio = float(np.clip(download_current / download_total, 0.0, 1.0)) if download_total > 0 else 1.0
  downloaded_end = timeline.start + duration * download_ratio
  pressed = hovered and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)  # noqa: TID251
  if pressed:
    scrub.active = True

  action = None
  if scrub.active:
    scrub_ratio = float(np.clip((mouse_position.x - timeline_rect.x) / timeline_rect.width, 0.0, 1.0))
    scrub.preview_seconds = timeline.start + scrub_ratio * duration
    seek_second = round(scrub.preview_seconds)
    now = time.monotonic()
    released = rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT)  # noqa: TID251
    if (pressed or released
        or (rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT)
            and seek_second != scrub.last_seek_second and now - scrub.last_seek_at >= 0.15)):
      action = f"seek-time:{seek_second}"
      scrub.last_seek_at = now
      scrub.last_seek_second = seek_second
      scrub.pending_seconds = scrub.preview_seconds if scrub.preview_seconds > downloaded_end else None
    if released:
      scrub.active = False

  for entry in timeline.entries:
    start_ratio = float(np.clip((entry.start - timeline.start) / duration, 0.0, 1.0))
    end_ratio = float(np.clip((entry.end - timeline.start) / duration, start_ratio, 1.0))
    start_x = timeline_rect.x + start_ratio * timeline_rect.width
    end_x = timeline_rect.x + end_ratio * timeline_rect.width
    width = max(2.0, end_x - start_x)
    if entry.kind == "engaged":
      rl.draw_rectangle_rec(rl.Rectangle(start_x, timeline_rect.y, width, 10), GREEN)
    elif entry.kind == "bookmark":
      rl.draw_rectangle_rec(rl.Rectangle(start_x, timeline_rect.y + 10, 2, 6), CYAN)
    else:
      alert_color = {"info": GREEN, "warning": ORANGE, "critical": RED}[entry.kind]
      rl.draw_rectangle_rec(rl.Rectangle(start_x, timeline_rect.y + 11, width, 5), alert_color)

  if download_ratio < 1.0:
    downloaded_x = timeline_rect.x + download_ratio * timeline_rect.width
    rl.draw_rectangle_rec(
      rl.Rectangle(downloaded_x, timeline_rect.y, timeline_rect.x + timeline_rect.width - downloaded_x,
                   timeline_rect.height),
      rl.Color(5, 9, 15, 105),
    )
    rl.draw_line_ex(
      rl.Vector2(downloaded_x, timeline_rect.y),
      rl.Vector2(downloaded_x, timeline_rect.y + timeline_rect.height),
      1.0,
      MUTED,
    )

  if scrub.pending_seconds is not None:
    if abs(route_seconds - scrub.pending_seconds) <= 1.0:
      scrub.pending_seconds = None
    else:
      pending_ratio = float(np.clip((scrub.pending_seconds - timeline.start) / duration, 0.0, 1.0))
      pending_x = timeline_rect.x + pending_ratio * timeline_rect.width
      for dash_y in np.arange(timeline_rect.y - 3, timeline_rect.y + timeline_rect.height + 3, 5):
        rl.draw_line_ex(
          rl.Vector2(pending_x, float(dash_y)),
          rl.Vector2(pending_x, float(min(dash_y + 3, timeline_rect.y + timeline_rect.height + 3))),
          2.0,
          ORANGE,
        )
      rl.draw_triangle(
        rl.Vector2(pending_x, timeline_rect.y - 4),
        rl.Vector2(pending_x - 5, timeline_rect.y - 10),
        rl.Vector2(pending_x + 5, timeline_rect.y - 10),
        ORANGE,
      )

  display_seconds = scrub.preview_seconds if scrub.active and scrub.preview_seconds is not None else route_seconds
  current_ratio = float(np.clip((display_seconds - timeline.start) / duration, 0.0, 1.0))
  current_x = timeline_rect.x + current_ratio * timeline_rect.width
  rl.draw_line_ex(
    rl.Vector2(current_x, timeline_rect.y - 2),
    rl.Vector2(current_x, timeline_rect.y + timeline_rect.height + 2),
    2.0,
    WHITE,
  )
  if scrub.active and scrub.preview_seconds is not None:
    preview = f"{scrub.preview_seconds:.1f}s"
    preview_size = measure_text_cached(font, preview, 14)
    preview_x = float(np.clip(current_x - preview_size.x / 2, timeline_rect.x, timeline_rect.x + timeline_rect.width - preview_size.x - 10))
    preview_rect = rl.Rectangle(preview_x, timeline_rect.y - 27, preview_size.x + 10, 22)
    rl.draw_rectangle_rounded(preview_rect, 0.25, 4, rl.Color(0, 0, 0, 220))
    draw_text(font, preview, preview_rect.x + 5, preview_rect.y + 3, 14, TEXT)
  if not scrub.active:
    scrub.preview_seconds = None
  return action, hovered or scrub.active


def draw_replay_control_bar(font, bounds: rl.Rectangle, replay: ManagedReplay, route_seconds: float,
                            route_fingerprint: str, timeline: ReplayTimeline, v_ego: float, loading: bool, seek_input: str,
                            seek_active: bool, scrub: ReplayScrubState) -> str | None:
  rl.draw_rectangle_rec(bounds, rl.Color(8, 12, 18, 248))
  rl.draw_line_ex(rl.Vector2(bounds.x, bounds.y), rl.Vector2(bounds.x + bounds.width, bounds.y), 1.0, MUTED)
  controls = (
    ("-60s", "M", CYAN, "Shift+M: back 60 seconds"),
    ("-10s", "S", CYAN, "Shift+S: back 10 seconds"),
    ("PAUSE", " ", GREEN, "Space: pause / resume"),
    ("+10s", "s", CYAN, "S: forward 10 seconds"),
    ("+60s", "m", CYAN, "M: forward 60 seconds"),
    ("SPD-", "-", MUTED, "-: slower playback"),
    ("SPD+", "+", MUTED, "+: faster playback"),
    ("ENG", "e", GREEN, "E: next engagement"),
    ("DIS", "d", GREEN, "D: next disengagement"),
    ("TAG", "t", ORANGE, "T: next user tag"),
    ("INFO", "i", ORANGE, "I: next info alert"),
    ("WARN", "w", ORANGE, "W: next warning alert"),
    ("CRIT", "c", RED, "C: next critical alert"),
    ("EXIT", "q", RED, "Q: exit replay"),
  )
  mouse_position = rl.get_mouse_position()
  chip_x = bounds.x + 10
  chip_y = bounds.y + 9
  clicked_action = None
  hovered_tooltip = None
  for label, action, color, tooltip in controls:
    chip_x, chip_rect, hovered = draw_status_chip(font, label, chip_x, chip_y, color, mouse_position)
    if hovered:
      hovered_tooltip = (tooltip, chip_rect)
      if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
        clicked_action = action

  field_x = chip_x + 2
  field = rl.Rectangle(field_x, bounds.y + 8, measure_standalone_text(font, "SEEK", 15).x + 14, 27)
  field_hovered = rl.check_collision_point_rec(mouse_position, field)
  rl.draw_rectangle_rounded(field, 0.18, 4, BACKGROUND)
  rl.draw_rectangle_rounded_lines_ex(field, 0.18, 4, 1.0, CYAN if seek_active else MUTED)
  draw_text(font, seek_input or "SEEK", field.x + 7, field.y + 5, 15, TEXT if seek_input else MUTED)
  if seek_active and int(time.monotonic() * 2) % 2 == 0:
    cursor_x = field.x + 7 + measure_standalone_text(font, seek_input, 15).x
    rl.draw_line_ex(rl.Vector2(cursor_x + 1, field.y + 4), rl.Vector2(cursor_x + 1, field.y + 22), 1.0, TEXT)
  if field_hovered and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
    clicked_action = "seek-focus"
  elif seek_active and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
    clicked_action = clicked_action or "seek-blur"

  if hovered_tooltip is not None:
    tooltip, chip_rect = hovered_tooltip
    size = measure_text_cached(font, tooltip, 15)
    tooltip_x = float(np.clip(chip_rect.x, bounds.x + 5, bounds.x + bounds.width - size.x - 23))
    tooltip_rect = rl.Rectangle(tooltip_x, bounds.y - 33, size.x + 18, 27)
    rl.draw_rectangle_rounded(tooltip_rect, 0.25, 4, rl.Color(0, 0, 0, 235))
    rl.draw_rectangle_rounded_lines_ex(tooltip_rect, 0.25, 4, 1.0, MUTED)
    draw_text(font, tooltip, tooltip_rect.x + 9, tooltip_rect.y + 5, 15, TEXT)

  status_text = "loading" if loading else ("paused" if replay.paused else "playing")
  info = "".join((
    f"STATUS {status_text}   ROUTE {route_seconds:.1f}s   FINGERPRINT {route_fingerprint or '--'}   ",
    f"SPEED {v_ego:.1f} m/s   PLAYBACK {replay.playback_speed:.1f}x   ",
    f"DOWNLOAD {format_download_progress(replay.progress_current, replay.progress_total)}",
  ))
  draw_text(font, info, bounds.x + 12, bounds.y + 43, 14, TEXT)
  timeline_action, timeline_hovered = draw_replay_timeline(
    font, bounds, timeline, route_seconds, scrub, replay.progress_current, replay.progress_total,
  )
  if timeline_action is not None:
    clicked_action = timeline_action
  rl.set_mouse_cursor(
    rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND
    if hovered_tooltip is not None or field_hovered or timeline_hovered
    else rl.MouseCursor.MOUSE_CURSOR_DEFAULT,
  )
  return clicked_action


def apply_replay_control(replay: ManagedReplay, action: str | None, seek_input: str,
                         seek_active: bool) -> tuple[str, bool]:
  if action is not None and action.startswith("seek-time:"):
    replay.send(f"\n{action.removeprefix('seek-time:')}\n")
    return "", False
  if action == "seek-focus":
    return seek_input, True
  if action == "seek-blur":
    return seek_input, False
  if action == "seek":
    if seek_input:
      replay.send(f"\n{seek_input}\n")
    return "", False
  if action is not None:
    replay.send(action)
    return seek_input, False
  return seek_input, seek_active


def both_camera_streams_available(available_streams) -> bool:
  return (
    VisionStreamType.VISION_STREAM_ROAD in available_streams
    and VisionStreamType.VISION_STREAM_WIDE_ROAD in available_streams
  )


def fused_stream_loss_state(available_streams, missing_since: float | None,
                            now: float) -> tuple[float | None, bool]:
  if both_camera_streams_available(available_streams):
    return None, False
  missing_since = now if missing_since is None else missing_since
  return missing_since, now - missing_since >= FUSED_STREAM_GRACE_SECONDS


def draw_source_status(font, rect: rl.Rectangle, live_tracks, valid: bool, alive: bool, source_active: bool,
                       show_labels: bool, data_source: str, camera_mode: str,
                       both_cameras_available: bool,
                       visible_tracks, motion_states: dict[int, int], track_locations: dict[int, tuple[int, int]],
                       source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]],
                       table_mode: str, fps: int) -> str | tuple[str, RadarSourceKey] | None:
  rl.draw_rectangle_rec(rect, rl.Color(11, 16, 24, 225))
  tracks = live_tracks.points if valid else ()
  sources = sorted(live_tracks.trackSources, key=radar_source_sort_key) if valid else []
  status_color = GREEN if valid and alive else ORANGE
  source_title = "CAN" if data_source == "can" else "LIVE"
  mouse_position = rl.get_mouse_position()
  top_hovered_tooltip = None
  source_clicked_action = None
  source_hovered_tooltip = None
  fps_text = f"{fps} fps"
  fps_size = measure_standalone_text(font, fps_text, 16)
  source_tooltip_anchor_y = rect.y + 49 + max(0, len(sources) - 1) * 30

  if sources:
    for row, source in enumerate(sources):
      row_y = rect.y + 14 + row * 30
      source_x = rect.x + 34
      draw_track_source_marker(rl.Vector2(rect.x + 20, row_y + 8), 6.0, CYAN, row)
      spec = SPEC_BY_RANGE.get((source.startAddress, source.endAddress))
      compact_name = source_name(source.startAddress, source.endAddress).removeprefix("RADAR_")
      source_parts = [
        (compact_name, f"Radar CAN address range 0x{source.startAddress:X}-0x{source.endAddress:X}"),
        (f"B{source.bus}", f"CAN bus {source.bus} carrying this radar source"),
      ]
      if spec is not None:
        source_parts.extend((
          (f"{spec.frequency} Hz", "Expected radar message frequency"),
          (f"{spec.message_size} B", "Radar CAN message payload size"),
        ))
      else:
        source_parts.append(("unknown format", "No supported radar format matches this address range"))
      source_hovered_tooltip = draw_status_parts(
        font, tuple(source_parts), source_x, row_y, 16, CYAN, mouse_position, " / ",
      )
      if source_hovered_tooltip is not None:
        top_hovered_tooltip = source_hovered_tooltip

      source_key = radar_source_key(source)
      hide_moving, hide_stationary, hide_unknown = source_filter_state(source_filters, source_key)
      source_text = " / ".join(text for text, _ in source_parts)
      source_track_ids = [
        int(track.trackId)
        for track in tracks
        if (
          source.startAddress
          <= track_locations.get(int(track.trackId), (-1, -1))[0]
          <= source.endAddress
          and track_locations.get(int(track.trackId), (-1, -1))[1] == source.bus
        )
      ]
      moving_count = sum(motion_states.get(track_id) == 2 for track_id in source_track_ids)
      stationary_count = sum(motion_states.get(track_id) == 1 for track_id in source_track_ids)
      unknown_count = max(0, source.trackCount - moving_count - stationary_count)
      visible_source_tracks = sum(
        source.startAddress <= address <= source.endAddress and bus == source.bus
        for track in visible_tracks
        for address, bus in (track_locations.get(int(track.trackId), (-1, -1)),)
      )
      count_text = f"{visible_source_tracks:>{TRACK_COUNT_FIELD_WIDTH}}/{source.trackCount:<{TRACK_COUNT_FIELD_WIDTH}}"
      count_x = source_x + measure_standalone_text(font, source_text, 16).x + measure_standalone_text(font, " / ", 16).x
      count_size = measure_standalone_text(font, count_text, 16)
      count_rect = rl.Rectangle(count_x, row_y, count_size.x, count_size.y + 4)
      draw_text(font, count_text, count_x, row_y, 16, TEXT)
      if rl.check_collision_point_rec(mouse_position, count_rect):
        top_hovered_tooltip = (
          f"{visible_source_tracks} visible tracks out of {source.trackCount} decoded from this radar source",
          count_rect,
        )
      filter_x = count_rect.x + count_rect.width + 9
      filter_specs = (
        (f"MOVING {moving_count:>{TRACK_COUNT_FIELD_WIDTH}}",
         PURPLE, "moving", hide_moving, moving_count),
        (f"STATIONARY {stationary_count:>{TRACK_COUNT_FIELD_WIDTH}}",
         WHITE, "stationary", hide_stationary, stationary_count),
        (f"UNKNOWN {unknown_count:>{TRACK_COUNT_FIELD_WIDTH}}",
         MUTED, "unknown", hide_unknown, unknown_count),
      )
      for label, color, action, hidden, category_count in filter_specs:
        filter_x, chip_rect, hovered = draw_status_chip(
          font, label, filter_x, row_y - 4, color, mouse_position,
          selected=not hidden, selection_color=MUTED,
        )
        if hovered:
          tooltip_anchor = rl.Rectangle(chip_rect.x, source_tooltip_anchor_y, chip_rect.width, chip_rect.height)
          source_hovered_tooltip = (
            f"{'Show' if hidden else 'Hide'} {category_count} {action} tracks from {compact_name} on bus {source.bus}",
            tooltip_anchor,
          )
          if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
            source_clicked_action = (action, source_key)
      if row == 0:
        fps_x = rect.x + rect.width - fps_size.x - 14
        fps_rect = rl.Rectangle(fps_x, row_y, fps_size.x, fps_size.y + 4)
        draw_text(font, fps_text, fps_x, row_y, 16, TEXT)
        if rl.check_collision_point_rec(mouse_position, fps_rect):
          top_hovered_tooltip = ("Debugger rendering frame rate", fps_rect)
  elif not source_active:
    source_text = "no route loaded"
  elif data_source == "liveTracks":
    source_text = "no source metadata"
  elif valid and live_tracks.radarTracksAvailable:
    source_text = "radar detected / parsing"
  else:
    source_text = "searching for supported radar"
  if not sources:
    draw_text(font, source_text, rect.x + 14, rect.y + 14, 16, MUTED)
    fallback_summary = f"{len(visible_tracks)}/{len(tracks)}  {fps_text}"
    summary_size = measure_standalone_text(font, fallback_summary, 16)
    draw_text(font, fallback_summary, rect.x + rect.width - summary_size.x - 14, rect.y + 14, 16, TEXT)

  chip_x = rect.x + 14
  chip_y = source_tooltip_anchor_y
  camera_label = {"fused": "FUSED", "wide 180": "WIDE"}.get(camera_mode, "ROAD")
  table_label = {"motion": "MOTION", "kinematics": "KIN", "object": "OBJ"}[table_mode]
  chip_specs = [
    ("OPEN", GREEN, "route", "Open a route, or paste one with Cmd/Ctrl+V"),
    (source_title, status_color, "source", "Switch CAN / liveTracks source"),
    ("LABELS ON" if show_labels else "LABELS", GREEN if show_labels else MUTED, "labels", "Show / hide all labels"),
  ]
  if both_cameras_available:
    chip_specs.append((camera_label, CYAN, "camera", "Cycle road / wide / fused camera"))
  chip_specs.append((table_label, MUTED, "table", "Cycle motion / kinematics / object table"))
  clicked_action = source_clicked_action
  hovered_tooltip = source_hovered_tooltip or top_hovered_tooltip
  for label, color, action, tooltip in chip_specs:
    chip_x, chip_rect, hovered = draw_status_chip(font, label, chip_x, chip_y, color, mouse_position)
    if hovered:
      hovered_tooltip = (tooltip, chip_rect)
      if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251 - standalone raylib tool
        clicked_action = action
  rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND if hovered_tooltip is not None
                      else rl.MouseCursor.MOUSE_CURSOR_DEFAULT)
  if hovered_tooltip is not None:
    draw_status_tooltip(font, hovered_tooltip[0], hovered_tooltip[1], rect)
  return clicked_action


def ui_thread(addr: str, start_wide: bool = False, start_fused: bool = False, start_route: str | None = None) -> None:
  rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
  rl.set_config_flags(rl.ConfigFlags.FLAG_VSYNC_HINT | rl.ConfigFlags.FLAG_WINDOW_RESIZABLE)
  rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Radar Tracks Debugger")
  primary_position = rl.get_monitor_position(0)
  primary_width = rl.get_monitor_width(0)
  primary_height = rl.get_monitor_height(0)
  rl.set_window_position(
    int(primary_position.x + (primary_width - WINDOW_WIDTH) / 2),
    int(primary_position.y + (primary_height - WINDOW_HEIGHT) / 2),
  )
  rl.maximize_window()
  rl.set_window_focused()
  rl.set_target_fps(max(60, rl.get_monitor_refresh_rate(0)))

  font_path = os.path.join(BASEDIR, "selfdrive/assets/fonts/JetBrainsMono-Medium.ttf")
  font = rl.load_font_ex(font_path, 64, None, 0)
  rl.gen_texture_mipmaps(font.texture)
  rl.set_texture_filter(font.texture, rl.TextureFilter.TEXTURE_FILTER_TRILINEAR)
  road_camera_view = CameraView("camerad", VisionStreamType.VISION_STREAM_ROAD)
  wide_camera_view = CameraView("camerad", VisionStreamType.VISION_STREAM_WIDE_ROAD)
  camera_view = wide_camera_view if start_wide else road_camera_view

  overlay_pixels = np.zeros((CAMERA_BUFFER_HEIGHT, CAMERA_BUFFER_WIDTH, 4), dtype=np.uint8)
  overlay_image = rl.gen_image_color(CAMERA_BUFFER_WIDTH, CAMERA_BUFFER_HEIGHT, rl.BLANK)
  overlay_texture = rl.load_texture_from_image(overlay_image)
  rl.set_texture_filter(overlay_texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
  rl.unload_image(overlay_image)

  sm = messaging.SubMaster([
    "carParams",
    "carState",
    "liveCalibration",
    "liveTracks",
    "modelV2",
    "radarState",
    "roadCameraState",
    "wideRoadCameraState",
  ], addr=addr)

  process_context = multiprocessing.get_context("spawn")
  decoder_output = process_context.Queue(maxsize=1)
  decoder_process = process_context.Process(target=radar_decoder_worker, args=(addr, decoder_output), daemon=True)
  decoder_process.start()
  timeline_output = process_context.Queue(maxsize=1)
  timeline_process = None
  replay_timeline = ReplayTimeline()

  can_tracks = RadarSnapshot()
  live_tracks = RadarSnapshot()
  can_data_seen = False
  live_data_seen = False
  can_data_alive = False
  decoded_motion_states: dict[int, int] = {}

  calibration = None
  calibration_key = None
  camera_projection_height = float(CAMERA_BUFFER_HEIGHT)
  show_labels = False
  source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]] = {}
  use_can_source = True
  table_mode_index = 0
  table_scroll = 0
  selected_track_id = None
  composite_mode = start_fused
  fused_streams_missing_since = None
  model_pixels = np.zeros((CAMERA_BUFFER_HEIGHT, CAMERA_BUFFER_WIDTH, 3), dtype=np.uint8)
  dummy_top_down = np.zeros((384, 960), dtype=np.uint8)
  overlay_dirty = True
  route_dialog_open = start_route is None
  route_input = start_route or ""
  route_cursor = len(route_input)
  route_error = ""
  route_select_all = False
  replay_process = None
  route_loading = False
  route_loading_started = 0.0
  replay_seek_input = ""
  replay_seek_active = False
  replay_scrub = ReplayScrubState()
  route_message_start_mono: int | None = None
  route_fingerprint = ""
  current_route_seconds = route_start_seconds(route_input)
  if start_route:
    replay_process, route_error = replace_route_replay(replay_process, start_route)
    route_dialog_open = bool(route_error)
    route_loading = replay_process is not None and not route_error
    route_loading_started = time.monotonic()
    if route_loading:
      replay_timeline = ReplayTimeline(route_start_seconds(start_route), route_start_seconds(start_route))
      timeline_process = start_timeline_process(process_context, timeline_process, timeline_output, start_route)
  composite_mode = composite_mode and not route_dialog_open
  startup_focus_deadline = time.monotonic() + 2.0
  next_startup_focus_request = 0.0

  while not rl.window_should_close() and (replay_process is None or replay_process.poll() is None):
    now = time.monotonic()
    if replay_process is not None:
      replay_process.drain_output()
      if replay_process.car_fingerprint:
        route_fingerprint = replay_process.car_fingerprint
    if now < startup_focus_deadline and now >= next_startup_focus_request:
      rl.set_window_focused()
      next_startup_focus_request = now + 0.1
    open_entered_route = False
    modifier_down = (
      rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SUPER)
      or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SUPER)
      or rl.is_key_down(rl.KeyboardKey.KEY_LEFT_CONTROL)
      or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_CONTROL)
    )
    if route_dialog_open:
      paste_pressed = modifier_down and rl.is_key_pressed(rl.KeyboardKey.KEY_V)
      select_all_pressed = modifier_down and rl.is_key_pressed(rl.KeyboardKey.KEY_A)
      codepoint = rl.get_char_pressed()
      while codepoint > 0:
        if not (paste_pressed or select_all_pressed) and 32 <= codepoint <= 126 and len(route_input) < 180:
          if route_select_all:
            route_input = ""
            route_cursor = 0
            route_select_all = False
          route_input = route_input[:route_cursor] + chr(codepoint) + route_input[route_cursor:]
          route_cursor += 1
          route_error = ""
        codepoint = rl.get_char_pressed()
      if select_all_pressed:
        route_select_all = bool(route_input)
        route_cursor = len(route_input)
      elif paste_pressed:
        clipboard_text = rl.get_clipboard_text() or ""
        printable_text = "".join(character for character in clipboard_text if 32 <= ord(character) <= 126)
        if route_select_all:
          route_input = ""
          route_cursor = 0
        inserted_text = printable_text[:180 - len(route_input)]
        route_input = route_input[:route_cursor] + inserted_text + route_input[route_cursor:]
        route_cursor += len(inserted_text)
        route_select_all = False
        route_error = ""
      elif edit_key_pressed(rl.KeyboardKey.KEY_BACKSPACE):
        if route_select_all:
          route_input = ""
          route_cursor = 0
        elif route_cursor > 0:
          route_input = route_input[:route_cursor - 1] + route_input[route_cursor:]
          route_cursor -= 1
        route_select_all = False
        route_error = ""
      elif edit_key_pressed(rl.KeyboardKey.KEY_DELETE):
        if route_select_all:
          route_input = ""
          route_cursor = 0
        elif route_cursor < len(route_input):
          route_input = route_input[:route_cursor] + route_input[route_cursor + 1:]
        route_select_all = False
        route_error = ""
      elif edit_key_pressed(rl.KeyboardKey.KEY_LEFT):
        route_cursor = 0 if route_select_all else max(0, route_cursor - 1)
        route_select_all = False
      elif edit_key_pressed(rl.KeyboardKey.KEY_RIGHT):
        route_cursor = len(route_input) if route_select_all else min(len(route_input), route_cursor + 1)
        route_select_all = False
      elif edit_key_pressed(rl.KeyboardKey.KEY_HOME):
        route_cursor = 0
        route_select_all = False
      elif edit_key_pressed(rl.KeyboardKey.KEY_END):
        route_cursor = len(route_input)
        route_select_all = False
      if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
        open_entered_route = True
      if rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
        route_dialog_open = False
        route_error = ""
        route_select_all = False
    elif replay_seek_active:
      codepoint = rl.get_char_pressed()
      while codepoint > 0:
        if chr(codepoint).isdigit() and len(replay_seek_input) < 7:
          replay_seek_input += chr(codepoint)
        codepoint = rl.get_char_pressed()
      if edit_key_pressed(rl.KeyboardKey.KEY_BACKSPACE):
        replay_seek_input = replay_seek_input[:-1]
      elif rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) and replay_process is not None:
        replay_seek_input, replay_seek_active = apply_replay_control(
          replay_process, "seek", replay_seek_input, replay_seek_active,
        )
      elif rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
        replay_seek_active = False
    elif modifier_down and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
      clipboard_text = rl.get_clipboard_text() or ""
      route_input = "".join(character for character in clipboard_text if 32 <= ord(character) <= 126)[:180]
      route_cursor = len(route_input)
      route_select_all = False
      replay_process, route_error = replace_route_replay(replay_process, route_input)
      route_dialog_open = bool(route_error)
      route_loading = replay_process is not None and not route_error
      route_loading_started = time.monotonic()
      route_message_start_mono = None
      route_fingerprint = ""
      current_route_seconds = route_start_seconds(route_input)
      if route_loading:
        replay_scrub = ReplayScrubState()
        replay_timeline = ReplayTimeline(current_route_seconds, current_route_seconds)
        timeline_process = start_timeline_process(process_context, timeline_process, timeline_output, route_input)
      composite_mode = composite_mode and not route_dialog_open
      table_scroll = 0
      selected_track_id = None
    elif modifier_down:
      pass
    elif replay_process is not None and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
      replay_seek_active = True
    elif replay_process is not None and (replay_command := replay_keyboard_command()) is not None:
      replay_process.send(replay_command)
    if open_entered_route:
      replay_process, route_error = replace_route_replay(replay_process, route_input)
      route_dialog_open = bool(route_error)
      route_select_all = False
      route_loading = replay_process is not None and not route_error
      route_loading_started = time.monotonic()
      route_message_start_mono = None
      route_fingerprint = ""
      current_route_seconds = route_start_seconds(route_input)
      if route_loading:
        replay_scrub = ReplayScrubState()
        replay_timeline = ReplayTimeline(current_route_seconds, current_route_seconds)
        timeline_process = start_timeline_process(process_context, timeline_process, timeline_output, route_input)

    sm.update(0)
    if sm.updated["carParams"]:
      message_fingerprint = str(sm["carParams"].carFingerprint)
      if message_fingerprint:
        route_fingerprint = message_fingerprint
    route_message_times = [
      sm.logMonoTime[service]
      for service in ("carState", "modelV2", "roadCameraState", "liveTracks")
      if sm.updated[service] and sm.logMonoTime[service] > 0
    ]
    if replay_process is not None and route_message_times:
      current_route_mono = max(route_message_times)
      if route_message_start_mono is None:
        route_message_start_mono = current_route_mono
      current_route_seconds = (
        route_start_seconds(route_input) + (current_route_mono - route_message_start_mono) / 1e9
      )
    if (route_loading
        and time.monotonic() - route_loading_started > 0.15
        and any(sm.updated[service] for service in ("carState", "modelV2", "roadCameraState", "liveTracks"))):
      route_loading = False
    while True:
      try:
        can_tracks, decoded_motion_states, can_data_alive, can_data_seen = decoder_output.get_nowait()
      except queue.Empty:
        break
    while True:
      try:
        replay_timeline = timeline_output.get_nowait()
        if replay_timeline.car_fingerprint:
          route_fingerprint = replay_timeline.car_fingerprint
      except queue.Empty:
        break
    if sm.updated["liveTracks"]:
      live_tracks = make_radar_snapshot(sm["liveTracks"])
      live_data_seen = sm.valid["liveTracks"]

    window_width = rl.get_screen_width()
    window_height = rl.get_screen_height()
    replay_bar_height = 94.0 if replay_process is not None else 0.0
    content_height = window_height - replay_bar_height
    left_width = float(round(window_width * 0.58))
    camera_height = float(round(content_height * 0.64))
    camera_rect = rl.Rectangle(0, 0, left_width, camera_height)
    table_rect = rl.Rectangle(0, camera_height, left_width, content_height - camera_height)
    radar_rect = rl.Rectangle(left_width, 0, window_width - left_width, content_height)
    replay_bar_rect = rl.Rectangle(0, content_height, window_width, replay_bar_height)
    status_sources = can_tracks.trackSources if use_can_source else live_tracks.trackSources
    status_height = 88 + max(0, len(status_sources) - 1) * 30
    status_rect = rl.Rectangle(0, 0, left_width, min(status_height, camera_height))

    if sm.valid["roadCameraState"] and sm.valid["liveCalibration"] and camera_view.frame:
      camera_key = ("tici", str(sm["roadCameraState"].sensor))
      device_camera = DEVICE_CAMERAS.get(camera_key)
      is_wide_camera = camera_view.stream_type == VisionStreamType.VISION_STREAM_WIDE_ROAD
      rpy_calib = np.asarray(sm["liveCalibration"].rpyCalib)
      wide_from_device_euler = np.asarray(sm["liveCalibration"].wideFromDeviceEuler)
      next_calibration_key = (
        camera_key, camera_view.stream_type, camera_view.frame.width, camera_view.frame.height,
        *rpy_calib, *wide_from_device_euler,
      )
      if device_camera is not None and next_calibration_key != calibration_key:
        camera = device_camera.ecam if is_wide_camera else device_camera.fcam
        calibration, camera_projection_height = build_camera_calibration(
          camera, rpy_calib, wide_from_device_euler if is_wide_camera else None,
        )
        calibration_key = next_calibration_key
        overlay_dirty = True
    if sm.updated["modelV2"]:
      overlay_dirty = True

    decoded_tracks = list(can_tracks.points) if can_data_seen else []
    decoded_track_signals = {signals.trackId: signals for signals in can_tracks.trackSignals}
    decoded_track_locations = {
      int(track.trackId): (track.canAddress, track.canBus)
      for track in decoded_tracks
      if track.canAddress >= 0 and track.canBus >= 0
    }
    if use_can_source:
      selected_tracks = can_tracks
      tracks = decoded_tracks
      data_valid = can_data_seen
      data_alive = can_data_alive
      motion_states = decoded_motion_states
      track_signals = decoded_track_signals
      track_locations = decoded_track_locations
      data_source = "can"
    else:
      selected_tracks = live_tracks
      data_valid = live_data_seen
      data_alive = sm.alive["liveTracks"]
      tracks = list(selected_tracks.points) if data_valid else []
      motion_states = match_decoded_track_values(tracks, decoded_tracks, decoded_motion_states)
      track_signals = match_decoded_track_values(tracks, decoded_tracks, decoded_track_signals)
      track_locations = match_decoded_track_values(tracks, decoded_tracks, decoded_track_locations)
      data_source = "liveTracks"

    source_filter_values = [
      source_filter_state(source_filters, radar_source_key(source))
      for source in selected_tracks.trackSources
    ] or [DEFAULT_SOURCE_FILTERS]
    hide_moving = all(filters[0] for filters in source_filter_values)
    hide_stationary = all(filters[1] for filters in source_filter_values)
    hide_unknown = all(filters[2] for filters in source_filter_values)
    tracks = filter_tracks(
      tracks, motion_states, track_locations, selected_tracks.trackSources, source_filters,
    )
    capacity = table_capacity(table_rect)
    max_scroll = max(0, len(tracks) - capacity)
    if rl.check_collision_point_rec(rl.get_mouse_position(), table_rect):
      table_scroll -= int(rl.get_mouse_wheel_move() * 3)
    table_scroll = int(np.clip(table_scroll, 0, max_scroll))
    table_hover_id = None if composite_mode else table_hovered_track_id(
      tracks, table_rect, table_scroll, rl.get_mouse_position(),
    )
    if (table_hover_id is not None
        and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)):  # noqa: TID251 - standalone raylib tool
      selected_track_id = table_hover_id

    v_ego = float(sm["carState"].vEgo) if sm.valid["carState"] else 0.0
    model = sm["modelV2"] if sm.valid["modelV2"] else None

    rl.begin_drawing()
    rl.clear_background(BACKGROUND)
    if composite_mode:
      rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_DEFAULT)
      fused_bounds = rl.Rectangle(0, 0, window_width, content_height)
      fused_device_camera = None
      rpy_calib = np.zeros(3)
      wide_from_device_euler = np.zeros(3)
      if sm.valid["roadCameraState"] and sm.valid["liveCalibration"]:
        fused_device_camera = DEVICE_CAMERAS.get(("tici", str(sm["roadCameraState"].sensor)))
        rpy_calib = np.asarray(sm["liveCalibration"].rpyCalib)
        wide_from_device_euler = np.asarray(sm["liveCalibration"].wideFromDeviceEuler)
      selected_track_id = draw_fused_camera_mode(
        font, road_camera_view, wide_camera_view, fused_device_camera, rpy_calib, wide_from_device_euler,
        fused_bounds, tracks, show_labels, motion_states,
        track_locations, selected_tracks.trackSources, selected_track_id,
      )
      fused_available_streams = set(road_camera_view.available_streams) | set(wide_camera_view.available_streams)
      fused_streams_missing_since, streams_timed_out = fused_stream_loss_state(
        fused_available_streams, fused_streams_missing_since, time.monotonic(),
      )
      if streams_timed_out:
        composite_mode = False
        fused_streams_missing_since = None
        if VisionStreamType.VISION_STREAM_ROAD in fused_available_streams:
          camera_view = road_camera_view
        elif VisionStreamType.VISION_STREAM_WIDE_ROAD in fused_available_streams:
          camera_view = wide_camera_view
      table_mode = TABLE_MODES[table_mode_index]
      clicked_action = draw_source_status(
        font, status_rect, selected_tracks, data_valid, data_alive,
        replay_process is not None or can_data_seen or live_data_seen, show_labels, data_source,
        "fused", both_camera_streams_available(fused_available_streams),
        tracks, motion_states, track_locations, source_filters, table_mode, rl.get_fps(),
      )
      if isinstance(clicked_action, tuple):
        action, source_key = clicked_action
        toggle_source_filter(source_filters, source_key, {"moving": 0, "stationary": 1, "unknown": 2}[action])
        table_scroll = 0
      elif clicked_action == "source":
        use_can_source = not use_can_source
        table_scroll = 0
        selected_track_id = None
      elif clicked_action == "labels":
        show_labels = not show_labels
      elif clicked_action == "camera":
        composite_mode = False
        fused_streams_missing_since = None
        camera_view = road_camera_view
      elif clicked_action == "table":
        table_mode_index = (table_mode_index + 1) % len(TABLE_MODES)
      elif clicked_action == "route":
        composite_mode = False
        route_dialog_open = True
        route_error = ""
        route_select_all = bool(route_input)
        route_cursor = len(route_input)
      if replay_process is not None:
        draw_replay_event_overlay(
          font, fused_bounds, status_rect.y + status_rect.height + 10,
          replay_timeline, current_route_seconds,
        )
      if route_loading:
        draw_route_loading(font, fused_bounds, route_input, time.monotonic() - route_loading_started)
      if replay_process is not None:
        replay_action = draw_replay_control_bar(
          font, replay_bar_rect, replay_process, current_route_seconds, route_fingerprint,
          replay_timeline, v_ego, route_loading, replay_seek_input, replay_seek_active, replay_scrub,
        )
        replay_seek_input, replay_seek_active = apply_replay_control(
          replay_process, replay_action, replay_seek_input, replay_seek_active,
        )
      rl.end_drawing()
      continue

    fused_streams_missing_since = None
    camera_view.render(camera_rect)
    camera_draw_rect = camera_content_rect(camera_view, camera_rect)

    mouse_position = rl.get_mouse_position()
    camera_hovered_id = None
    if (rl.check_collision_point_rec(mouse_position, camera_draw_rect)
        and not rl.check_collision_point_rec(mouse_position, status_rect)):
      camera_hovered_id = hovered_track_id(
        tracks,
        lambda track, calibration=calibration, camera_draw_rect=camera_draw_rect,
        camera_projection_height=camera_projection_height: camera_track_geometry(
          calibration, track, camera_draw_rect, camera_projection_height,
        ),
        mouse_position,
      )
    top_down_hovered_id = None
    if camera_hovered_id is None and rl.check_collision_point_rec(mouse_position, radar_rect):
      top_down_hovered_id = hovered_track_id(
        tracks, lambda track, radar_rect=radar_rect: top_down_track_geometry(radar_rect, track), mouse_position,
      )
    current_hovered_id = camera_hovered_id if camera_hovered_id is not None else top_down_hovered_id
    selected_track_id = retain_selected_track_id(selected_track_id, current_hovered_id, tracks)

    if selected_track_id is not None:
      sorted_tracks = sorted(tracks, key=lambda track: (track.dRel, track.trackId))
      hovered_row = next((index for index, track in enumerate(sorted_tracks)
                          if int(track.trackId) == selected_track_id), None)
      if hovered_row is not None:
        if hovered_row < table_scroll:
          table_scroll = hovered_row
        elif hovered_row >= table_scroll + capacity:
          table_scroll = hovered_row - capacity + 1
        table_scroll = int(np.clip(table_scroll, 0, max_scroll))

    if overlay_dirty:
      model_pixels.fill(0)
      dummy_top_down.fill(0)
      if sm.valid["modelV2"]:
        plot_model(sm["modelV2"], model_pixels, calibration, (None, dummy_top_down))
      model_mask = np.any(model_pixels > 0, axis=2)
      overlay_pixels[:, :, :3] = model_pixels
      overlay_pixels[:, :, 3] = model_mask * 220
      rl.update_texture(overlay_texture, rl.ffi.cast("void *", overlay_pixels.ctypes.data))
      overlay_dirty = False
    rl.draw_texture_pro(
      overlay_texture,
      rl.Rectangle(0, 0, CAMERA_BUFFER_WIDTH, camera_projection_height),
      camera_draw_rect,
      rl.Vector2(0, 0),
      0,
      WHITE,
    )

    draw_camera_tracks(font, calibration, tracks, camera_draw_rect, show_labels, motion_states,
                       track_locations, selected_tracks.trackSources,
                       camera_projection_height, camera_hovered_id, selected_track_id, table_hover_id)
    draw_top_down(
      font, radar_rect, tracks, show_labels, model, motion_states,
      hide_moving, hide_stationary, hide_unknown, track_locations, selected_tracks.trackSources,
      top_down_hovered_id, selected_track_id, table_hover_id,
    )
    table_mode = TABLE_MODES[table_mode_index]
    draw_track_table(font, table_rect, tracks, motion_states, table_scroll, selected_track_id, table_hover_id,
                     track_signals, track_locations, table_mode)
    clicked_action = draw_source_status(
      font, status_rect, selected_tracks, data_valid, data_alive,
      replay_process is not None or can_data_seen or live_data_seen, show_labels, data_source,
      "wide 180" if camera_view.stream_type == VisionStreamType.VISION_STREAM_WIDE_ROAD else "road",
      both_camera_streams_available(camera_view.available_streams),
      tracks, motion_states, track_locations, source_filters, table_mode, rl.get_fps(),
    )
    if isinstance(clicked_action, tuple):
      action, source_key = clicked_action
      toggle_source_filter(source_filters, source_key, {"moving": 0, "stationary": 1, "unknown": 2}[action])
      table_scroll = 0
    elif clicked_action == "source":
      use_can_source = not use_can_source
      table_scroll = 0
      selected_track_id = None
    elif clicked_action == "labels":
      show_labels = not show_labels
    elif clicked_action == "camera":
      if camera_view is road_camera_view:
        camera_view = wide_camera_view
      elif both_camera_streams_available(camera_view.available_streams):
        composite_mode = True
        fused_streams_missing_since = None
    elif clicked_action == "table":
      table_mode_index = (table_mode_index + 1) % len(TABLE_MODES)
    elif clicked_action == "route":
      route_dialog_open = True
      route_error = ""
      route_select_all = bool(route_input)
      route_cursor = len(route_input)
    if replay_process is not None:
      draw_replay_event_overlay(
        font, camera_draw_rect, status_rect.y + status_rect.height + 10,
        replay_timeline, current_route_seconds,
      )
    if route_dialog_open:
      route_action = draw_route_dialog(
        font, rl.Rectangle(0, 0, window_width, window_height), route_input, route_cursor, route_error, route_select_all,
      )
      if route_action == "cancel":
        route_dialog_open = False
        route_error = ""
        route_select_all = False
      elif route_action == "open":
        replay_process, route_error = replace_route_replay(replay_process, route_input)
        route_dialog_open = bool(route_error)
        route_select_all = False
        route_loading = replay_process is not None and not route_error
        route_loading_started = time.monotonic()
        route_message_start_mono = None
        route_fingerprint = ""
        current_route_seconds = route_start_seconds(route_input)
        if route_loading:
          replay_scrub = ReplayScrubState()
          replay_timeline = ReplayTimeline(current_route_seconds, current_route_seconds)
          timeline_process = start_timeline_process(process_context, timeline_process, timeline_output, route_input)
    if route_loading and not route_dialog_open:
      draw_route_loading(
        font, rl.Rectangle(0, 0, window_width, window_height), route_input, time.monotonic() - route_loading_started,
      )
    if replay_process is not None and not route_dialog_open:
      replay_action = draw_replay_control_bar(
        font, replay_bar_rect, replay_process, current_route_seconds, route_fingerprint,
        replay_timeline, v_ego, route_loading, replay_seek_input, replay_seek_active, replay_scrub,
      )
      replay_seek_input, replay_seek_active = apply_replay_control(
        replay_process, replay_action, replay_seek_input, replay_seek_active,
      )
    if table_hover_id is not None and not route_dialog_open:
      rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND)
    rl.end_drawing()

  stop_route_replay(replay_process)
  stop_timeline_process(timeline_process)
  decoder_process.terminate()
  decoder_process.join(timeout=1.0)
  decoder_output.close()
  timeline_output.close()
  rl.unload_texture(overlay_texture)
  rl.unload_font(font)
  road_camera_view.close()
  wide_camera_view.close()
  rl.close_window()


def get_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Decode replay CAN with Hyundai auto radar discovery and visualize the resulting tracks.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("ip_address", nargs="?", default="127.0.0.1", help="Address publishing replay or on-car messages.")
  parser.add_argument("--route", help="Route or segment ID to open in replay when the debugger starts.")
  parser.add_argument("--wide", action="store_true", help="Start with the wide/full field-of-view road camera.")
  parser.add_argument("--fused", action="store_true", help="Start with the full-screen fused road and wide cameras.")
  return parser


if __name__ == "__main__":
  args = get_arg_parser().parse_args(sys.argv[1:])
  if args.ip_address != "127.0.0.1":
    os.environ["ZMQ"] = "1"
    messaging.reset_context()
  try:
    ui_thread(args.ip_address, args.wide, args.fused, args.route)
  except KeyboardInterrupt:
    pass
