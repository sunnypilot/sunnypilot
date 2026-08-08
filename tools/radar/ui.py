#!/usr/bin/env python3
import argparse
import atexit
import ipaddress
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
import threading
import time
import warnings
from dataclasses import dataclass
import fcntl
from typing import Any

import numpy as np
import pyray as rl

import openpilot.cereal.messaging as messaging
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
REMOTE_BRIDGE_TIMEOUT_SECONDS = 1.5
REPLAY_EXECUTABLE = os.path.join(BASEDIR, "openpilot/tools/replay/replay")
MESSAGING_BRIDGE_EXECUTABLE = os.path.join(BASEDIR, "openpilot/cereal/messaging/bridge")
CAMERA_RELAY_EXECUTABLE = os.path.join(BASEDIR, "openpilot/tools/camerastream/compressed_vipc.py")
CAMERA_RELAY_BOOTSTRAP = "from tools.radar.ui import run_camera_relay; run_camera_relay()"
DARWIN_FFMPEG_LIBRARY_NAMES = {
  "libavutil.so.59": "libavutil.59.dylib",
  "libavcodec.so.61": "libavcodec.61.dylib",
  "libswscale.so.8": "libswscale.8.dylib",
}
REMOTE_SERVICES = (
  "can", "carParams", "carState", "liveCalibration", "liveTracks", "modelV2", "radarState",
  "roadCameraState", "wideRoadCameraState", "roadEncodeData", "wideRoadEncodeData",
)
ACTIVE_REMOTE_RELAYS: list[subprocess.Popen] = []

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
  (spec.start_addr, end_addr): spec
  for spec in HYUNDAI_RADAR_TRACK_SPECS
  for end_addr in {spec.required_end_addr, spec.end_addr}
}
SPEC_BY_NAME = {spec.name: spec for spec in HYUNDAI_RADAR_TRACK_SPECS}
PREFERRED_RADAR_SOURCE = "RADAR_3A5_3C4"
DEFAULT_SOURCE_FILTERS = (False, True, True)  # hide moving, stationary, unknown
RESEARCH_BUSES = (0, 1, 2)
RadarSourceKey = tuple[int, int, int]
RADAR_DETAIL_SIGNALS = {
  "RADAR_500_53F": {
    "UNKNOWN_1", "ONCOMING_ESR", "GROUPING_CHANGED_ESR", "REL_LAT_SPEED_ESR", "AZIMUTH", "STATE",
    "LONG_DIST", "REL_ACCEL", "REL_ACCEL_ESR", "WIDTH_ESR", "COUNTER", "BRIDGE_OBJECT_ESR", "REL_SPEED",
    "MED_RANGE_MODE_ESR",
  },
  "RADAR_210_21F": {
    f"{prefix}{signal}"
    for prefix in ("1_", "2_")
    for signal in (
      "STATE_ALT", "MOTION_STATE", "TRACK_QUALITY", "AGE", "COAST_AGE", "STATE", "RCS",
      "LONG_DIST", "LAT_DIST", "REL_SPEED", "NEW_SIGNAL_4", "REL_LAT_SPEED", "REL_ACCEL",
      "NEW_SIGNAL_18", "OBJECT_ID",
    )
  } | {"CHECKSUM", "COUNTER"},
  "RADAR_235_248": {
    "CHECKSUM", "COUNTER", "QUALITY", "AGE", "MOTION_STATE", "OBJECT_ID", "WIDTH", "CLASSIFICATION",
    "LONG_DIST", "LAT_DIST", "REL_SPEED", "REL_LAT_SPEED", "REL_ACCEL", "UNKNOWN_1", "UNKNOWN_2",
    "UNKNOWN_3", "AZIMUTH",
  },
  "RADAR_3A5_3C4": {
    "CHECKSUM", "COUNTER", "STATE_ALT", "MOTION_STATE", "TRACK_COUNTER", "TRACK_QUALITY", "AGE",
    "COAST_AGE", "STATE", "RCS", "LONG_DIST", "LAT_DIST", "REL_SPEED", "REL_LAT_SPEED", "REL_ACCEL",
    "ABS_SPEED", "WIDTH", "LENGTH", "ORIENTATION_ANGLE",
    "NEW_SIGNAL_4", "NEW_SIGNAL_5", "NEW_SIGNAL_12", "NEW_SIGNAL_13", "NEW_SIGNAL_14",
    "NEW_SIGNAL_15", "NEW_SIGNAL_16", "NEW_SIGNAL_17", "NEW_SIGNAL_18",
  },
  "RADAR_602_617": {
    f"{prefix}{signal}"
    for prefix in ("1_", "2_")
    for signal in ("DISTANCE", "LATERAL", "SPEED")
  } | {"UNKNOWN_2", "COUNTER"},
}
TABLE_MODES = ("motion", "kinematics", "object", "signals")
PLAYBACK_SPEEDS = (0.2, 0.5, 1.0, 2.0, 4.0, 8.0)
AUDIO_PACKET_SECONDS = 0.05
AUDIO_PREBUFFER_SECONDS = 0.15
AUDIO_FADE_SECONDS = 0.005
AUDIO_MAX_BUFFER_SECONDS = 0.75
TRACK_COUNT_FIELD_WIDTH = 3
SOURCE_CIRCLE_RADIUS_SCALE = 0.8


@dataclass(frozen=True)
class ResearchSourceSpec:
  name: str
  start_address: int
  end_address: int
  message_sizes: tuple[int, ...]
  details: str


RESEARCH_SOURCE_SPECS = (
  ResearchSourceSpec("CCNC_FUSED_OBJECTS", 0x162, 0x162, (32,), "fused cluster objects, not raw radar  32 B"),
  ResearchSourceSpec("RADAR_500_STATUS_CORE", 0x4E0, 0x4E1, (8,) * 2, "front-radar status  20 Hz  ESR/shared 4E0"),
  ResearchSourceSpec("RADAR_500_BUILD", 0x4E2, 0x4E2, (8,), "optional build metadata  20 Hz"),
  ResearchSourceSpec("RADAR_500_PATHS", 0x4E3, 0x4E3, (8,), "front-radar path selectors/status  20 Hz"),
  ResearchSourceSpec("RADAR_500_HEALTH", 0x4E4, 0x4E5, (8,) * 2, "optional ADC/alignment status  20 Hz"),
  ResearchSourceSpec("RADAR_602_ALT", 0x612, 0x617, (8,) * 6, "alternate legacy front objects  8 B"),
  ResearchSourceSpec("CORNER_A_OBJECTS", 0x240, 0x24F, (16, *([24] * 15)), "right-front corner objects (inferred)  20 Hz"),
  ResearchSourceSpec("CORNER_A_DETECTIONS", 0x270, 0x277, (32,) * 8, "right-front compact scan bins (inferred)  20 Hz"),
  ResearchSourceSpec("CORNER_B_OBJECTS", 0x278, 0x287, (8, *([24] * 15)), "left-front corner objects (inferred)  20 Hz"),
  ResearchSourceSpec("CORNER_B_DETECTIONS", 0x288, 0x28F, (32,) * 8, "left-front compact scan bins (inferred)  20 Hz"),
  ResearchSourceSpec("RADAR_RAW_DETECTIONS", 0x3D0, 0x3D4, (32,) * 5, "front-radar auxiliary scan records  20 Hz  32 B"),
  ResearchSourceSpec("CAMERA_LANE_PATH", 0x360, 0x366, (32,) * 7, "forward-camera lane/path geometry  32 B"),
)
RESEARCH_SPEC_BY_RANGE = {(spec.start_address, spec.end_address): spec for spec in RESEARCH_SOURCE_SPECS}


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


def resample_audio_for_speed(data: bytes, playback_speed: float) -> bytes:
  samples = np.frombuffer(data, dtype=np.int16)
  if samples.size <= 1 or playback_speed == 1.0:
    return data
  output_size = max(1, round(samples.size / max(playback_speed, 0.01)))
  source_positions = np.linspace(0, samples.size - 1, output_size)
  return np.interp(source_positions, np.arange(samples.size), samples).astype(np.int16).tobytes()


class ReplayAudioPlayer:
  def __init__(self) -> None:
    self.enabled = False
    self.available = False
    self.error = ""
    self._stream: Any = None
    self._sample_rate = 0
    self._last_log_mono_time = 0
    self._buffer = bytearray()
    self._lock = threading.Lock()
    self._prebuffer_size = 0
    self._fade_samples = 0
    self._rebuffering = True
    self._fade_out_pending = False
    self._last_output_sample = 0

  def _callback(self, outdata, frames, time_info, status) -> None:
    del frames, time_info
    output = np.frombuffer(outdata, dtype=np.int16)
    output.fill(0)
    output_size = len(outdata)
    chunk = b""
    fade_in = False
    fade_out_from = 0
    with self._lock:
      if status:
        self._rebuffering = True
        self._fade_out_pending = True

      if self._fade_out_pending:
        fade_out_from = self._last_output_sample
        self._last_output_sample = 0
        self._fade_out_pending = False
      else:
        if self._rebuffering and len(self._buffer) >= self._prebuffer_size:
          self._rebuffering = False
          fade_in = True
        if not self._rebuffering:
          if len(self._buffer) >= output_size:
            chunk = bytes(self._buffer[:output_size])
            del self._buffer[:output_size]
            self._last_output_sample = int(np.frombuffer(chunk, dtype=np.int16)[-1])
          else:
            self._rebuffering = True
            fade_out_from = self._last_output_sample
            self._last_output_sample = 0

    if chunk:
      output[:] = np.frombuffer(chunk, dtype=np.int16)
      if fade_in:
        fade_samples = min(self._fade_samples, output.size)
        output[:fade_samples] = (
          output[:fade_samples].astype(np.float64) * np.linspace(0.0, 1.0, fade_samples)
        ).astype(np.int16)
    elif fade_out_from:
      fade_samples = min(self._fade_samples, output.size)
      output[:fade_samples] = np.linspace(fade_out_from, 0, fade_samples).astype(np.int16)

  def _close_stream(self) -> None:
    if self._stream is not None:
      try:
        self._stream.stop()
        self._stream.close()
      except Exception:
        pass
      self._stream = None
    self._sample_rate = 0

  def _open_stream(self, sample_rate: int) -> bool:
    if self._stream is not None and self._sample_rate == sample_rate:
      return True
    self._close_stream()
    try:
      import sounddevice as sd
      with self._lock:
        self._prebuffer_size = round(sample_rate * np.dtype(np.int16).itemsize * AUDIO_PREBUFFER_SECONDS)
        self._fade_samples = max(1, round(sample_rate * AUDIO_FADE_SECONDS))
        self._rebuffering = True
      self._stream = sd.RawOutputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        blocksize=round(sample_rate * AUDIO_PACKET_SECONDS),
        latency="high",
        callback=self._callback,
      )
      self._stream.start()
      self._sample_rate = sample_rate
      self.error = ""
      return True
    except Exception as exc:
      self.error = str(exc)
      self._close_stream()
      return False

  def clear(self) -> None:
    with self._lock:
      self._buffer.clear()
      self._rebuffering = True
      self._fade_out_pending = self._stream is not None
    self._last_log_mono_time = 0

  def reset(self) -> None:
    self.clear()
    self._close_stream()
    with self._lock:
      self._fade_out_pending = False
      self._last_output_sample = 0
    self.available = False
    self.error = ""

  def close(self) -> None:
    self.enabled = False
    self.reset()

  def toggle(self) -> None:
    self.enabled = not self.enabled
    self.clear()
    if not self.enabled:
      self._close_stream()
    self.error = ""

  def push(self, data: bytes, sample_rate: int, log_mono_time: int, playback_speed: float) -> None:
    self.available = True
    if not self.enabled or not data or sample_rate <= 0 or self.error:
      return
    if (self._last_log_mono_time
        and (log_mono_time <= self._last_log_mono_time
             or log_mono_time - self._last_log_mono_time > 500_000_000)):
      self.clear()
    self._last_log_mono_time = log_mono_time
    if self._sample_rate not in (0, sample_rate):
      self.reset()
      self.available = True
    if self._sample_rate == 0:
      self._sample_rate = sample_rate
    audio = resample_audio_for_speed(data, playback_speed)
    max_buffer_size = round(sample_rate * np.dtype(np.int16).itemsize * AUDIO_MAX_BUFFER_SECONDS)
    open_stream = False
    with self._lock:
      self._buffer.extend(audio)
      if len(self._buffer) > max_buffer_size:
        overflow = len(self._buffer) - max_buffer_size
        overflow += overflow % np.dtype(np.int16).itemsize
        del self._buffer[:overflow]
        self._rebuffering = True
        self._fade_out_pending = self._stream is not None
      prebuffer_size = round(sample_rate * np.dtype(np.int16).itemsize * AUDIO_PREBUFFER_SECONDS)
      open_stream = self._stream is None and len(self._buffer) >= prebuffer_size
    if open_stream:
      self._open_stream(sample_rate)


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


def stop_remote_relays(processes: list[subprocess.Popen]) -> None:
  stopped_processes = list(processes)
  for process in reversed(stopped_processes):
    if process.poll() is not None:
      continue
    process.send_signal(signal.SIGINT)
    try:
      process.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
      process.kill()
      process.wait(timeout=1.0)
  ACTIVE_REMOTE_RELAYS[:] = [
    process for process in ACTIVE_REMOTE_RELAYS
    if all(process is not stopped_process for stopped_process in stopped_processes)
  ]
  if processes is not ACTIVE_REMOTE_RELAYS:
    processes.clear()


def run_camera_relay() -> None:
  import ctypes
  import runpy

  original_cdll = ctypes.CDLL

  def load_library(name, *args, **kwargs):
    if sys.platform == "darwin" and isinstance(name, str):
      directory, filename = os.path.split(name)
      if dylib_name := DARWIN_FFMPEG_LIBRARY_NAMES.get(filename):
        name = os.path.join(directory, dylib_name)
    return original_cdll(name, *args, **kwargs)

  ctypes.CDLL = load_library  # ty: ignore[invalid-assignment]  # macOS library-name compatibility shim
  multiprocessing.set_start_method("fork", force=True)
  script_path = sys.argv.pop(1)
  runpy.run_path(script_path, run_name="__main__")


def start_remote_relays(address: str) -> list[subprocess.Popen]:
  processes: list[subprocess.Popen] = []
  try:
    processes.append(subprocess.Popen([
      MESSAGING_BRIDGE_EXECUTABLE,
      address,
      ",".join(REMOTE_SERVICES),
    ], cwd=BASEDIR))
    processes.append(subprocess.Popen([
      sys.executable,
      "-c",
      CAMERA_RELAY_BOOTSTRAP,
      CAMERA_RELAY_EXECUTABLE,
      "127.0.0.1",
      "--cams", "0,2",
      "--silent",
    ], cwd=BASEDIR))
  except BaseException:
    stop_remote_relays(processes)
    raise
  ACTIVE_REMOTE_RELAYS.extend(processes)
  return processes


atexit.register(stop_remote_relays, ACTIVE_REMOTE_RELAYS)


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


def parse_live_ip(value: str) -> str | None:
  try:
    return str(ipaddress.ip_address(value.strip()))
  except ValueError:
    return None


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
    # The qlog may still be downloading when this metadata worker starts.
    # LogReader reports the incomplete tail as corruption even though replay can
    # continue streaming the available prefix.
    with warnings.catch_warnings():
      warnings.filterwarnings("ignore", message="Corrupted events detected", category=RuntimeWarning)
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
  signalSummary: str
  allSignals: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class DisplayRawSignal:
  startAddress: int
  endAddress: int
  address: int
  bus: int
  label: str
  signalSummary: str


@dataclass(frozen=True)
class RadarSnapshot:
  points: tuple[DisplayTrack, ...] = ()
  trackSources: tuple[DisplaySource, ...] = ()
  trackSignals: tuple[DisplayTrackSignals, ...] = ()
  rawSignals: tuple[DisplayRawSignal, ...] = ()
  radarTracksAvailable: bool = False


class ResearchCanDecoder:
  """Inventory auxiliary families without publishing them as control-facing radar tracks."""

  def __init__(self):
    self.payloads: dict[tuple[str, int], dict[int, bytes]] = {}

  def update(self, can_messages) -> None:
    for address, dat, bus in can_messages:
      if int(bus) not in RESEARCH_BUSES:
        continue
      for spec in RESEARCH_SOURCE_SPECS:
        if not spec.start_address <= address <= spec.end_address:
          continue
        expected_size = spec.message_sizes[address - spec.start_address]
        if len(dat) == expected_size:
          self.payloads.setdefault((spec.name, int(bus)), {})[int(address)] = bytes(dat)

  @staticmethod
  def _packed_detection_records(payload: bytes) -> tuple[int, ...]:
    return tuple(
      int.from_bytes(payload[offset:offset + 4], "little")
      for offset in (3, 8, 12, 16, 20, 24, 28)
    )

  @staticmethod
  def _signed(raw: int, size: int) -> int:
    return raw - (1 << size) if raw & (1 << (size - 1)) else raw

  @classmethod
  def _little(cls, raw: int, start: int, size: int, *, signed: bool = False) -> int:
    value = (raw >> start) & ((1 << size) - 1)
    return cls._signed(value, size) if signed else value

  @classmethod
  def _big(cls, raw: int, start: int, size: int, *, signed: bool = False) -> int:
    value = 0
    bit = start
    for _ in range(size):
      value = (value << 1) | ((raw >> bit) & 1)
      bit = bit + 15 if bit % 8 == 0 else bit - 1
    return cls._signed(value, size) if signed else value

  @classmethod
  def _corner_object(cls, payload: bytes) -> tuple[float, float, float] | None:
    raw = int.from_bytes(payload, "little")
    raw_dist = (raw >> 63) & 0x1FFF
    if raw_dist == 0xFFE:
      return None

    d_rel = raw_dist * 0.05
    # Exclude the high-range default/sentinel region and points outside the debugger plot.
    if not 0 < d_rel <= MAX_FORWARD_DISTANCE:
      return None

    y_rel = cls._signed((raw >> 76) & 0x7FF, 11) * 0.05
    v_rel = cls._signed((raw >> 88) & 0x3FF, 10) * 0.2
    return d_rel, y_rel, v_rel

  @classmethod
  def _radar_500_status_summary(cls, address: int, raw: int) -> str:
    if address == 0x4E0:
      return " ".join((
        f"CTR:{cls._little(raw, 6, 2)}",
        f"TS:{cls._big(raw, 5, 7) * 2}ms",
        f"SCAN:{cls._big(raw, 31, 16)}",
        f"SPD:{cls._big(raw, 50, 11) * 0.0625:.2f}m/s",
        f"YAW:{cls._big(raw, 47, 12, signed=True) * 0.0625:.2f}deg/s",
        f"CURV:{cls._big(raw, 13, 14, signed=True)}m",
        f"COMM:{cls._big(raw, 14, 1)}",
      ))
    if address == 0x4E1:
      return " ".join((
        f"CTR:{cls._big(raw, 1, 2)}",
        f"MAX:{cls._big(raw, 7, 6) + 1}",
        f"STEER:{cls._big(raw, 10, 11)}",
        f"RAW:{cls._big(raw, 11, 1)}",
        f"OP:{cls._big(raw, 12, 1)}",
        f"ERR:{cls._big(raw, 13, 1)}/{cls._big(raw, 14, 1)}/{cls._big(raw, 15, 1)}",
        f"TEMP:{cls._big(raw, 31, 8, signed=True)}C",
        f"GROUP:{cls._big(raw, 33, 2)}",
        f"VER:{cls._big(raw, 55, 16):04X}",
      ))
    if address == 0x4E2:
      values = tuple(cls._little(raw, byte * 8, 8) for byte in range(8))
      return " ".join((
        f"BUILD:{values[0]:02X}-{values[1]:02X}-{values[2]:02X}",
        f"{values[3]:02X}:{values[4]:02X}",
        f"U5-7:{values[5]:02X}/{values[6]:02X}/{values[7]:02X}",
      ))
    if address == 0x4E3:
      return " ".join((
        f"CTR:{cls._big(raw, 1, 2)}",
        f"MODE:{cls._big(raw, 3, 2)}",
        f"BLOCK:{cls._big(raw, 4, 1)}/{cls._big(raw, 5, 1)}/{cls._big(raw, 6, 1)}",
        f"TRUCK:{cls._big(raw, 7, 1)}",
        f"PATHS:{'/'.join(str(cls._big(raw, start, 8)) for start in (15, 23, 31, 39, 47, 63))}",
        f"ALIGN:{cls._big(raw, 55, 8, signed=True) * 0.0625:.2f}deg",
      ))
    if address == 0x4E4:
      names = ("BAT", "IGN", "T1", "T2", "5VA", "5VDX", "3V3", "10V")
      return " ".join(f"{name}:{cls._little(raw, byte * 8, 8):02X}" for byte, name in enumerate(names))
    if address == 0x4E5:
      return " ".join((
        f"1V8:{cls._little(raw, 0, 8):02X}",
        f"N5V:{cls._little(raw, 8, 8):02X}",
        f"WAVE:{cls._little(raw, 16, 8):02X}",
        f"PWR:{cls._little(raw, 24, 3)}",
        f"VUP:{cls._little(raw, 27, 1)}",
        f"FACT:{cls._little(raw, 32, 3)}/{cls._little(raw, 35, 3)}",
        f"FLAGS:{cls._little(raw, 38, 1)}/{cls._little(raw, 39, 1)}",
        f"MISC:{cls._little(raw, 40, 8, signed=True)}/{cls._little(raw, 56, 8, signed=True)}",
        f"UPDATES:{cls._little(raw, 48, 8)}",
      ))
    return f"RAW:{raw:016X}"

  def snapshot(
    self,
  ) -> tuple[
    tuple[DisplaySource, ...],
    tuple[DisplayTrack, ...],
    tuple[DisplayTrackSignals, ...],
    tuple[DisplayRawSignal, ...],
    dict[int, tuple[int, int]],
  ]:
    sources = []
    tracks = []
    track_signals = []
    raw_signals = []
    track_locations = {}
    for spec in RESEARCH_SOURCE_SPECS:
      for (name, bus), payloads in self.payloads.items():
        if name != spec.name or any(address not in payloads for address in range(spec.start_address, spec.end_address + 1)):
          continue

        track_count = 0
        if spec.name == "RADAR_602_ALT":
          for address in range(spec.start_address, spec.end_address + 1):
            raw = int.from_bytes(payloads[address], "little")
            d_rel = self._little(raw, 0, 10) * 0.25
            if not 0 < d_rel < 255.75:
              continue
            y_rel = self._little(raw, 10, 11) * 0.03 - 30.705
            v_rel = self._little(raw, 21, 10) * 0.25 - 128
            object_id = self._little(raw, 31, 9)
            track_id = 800_000 + bus * 0x10000 + address
            tracks.append(DisplayTrack(
              trackId=track_id,
              dRel=d_rel,
              yRel=y_rel,
              vRel=v_rel,
              aRel=float("nan"),
              canAddress=address,
              canBus=bus,
            ))
            track_signals.append(DisplayTrackSignals(
              trackId=track_id,
              relLatSpeed=float("nan"),
              absSpeed=float("nan"),
              width=float("nan"),
              length=float("nan"),
              orientationAngle=float("nan"),
              age=-1,
              coastAge=-1,
              state=-1,
              stateAlt=-1,
              trackCounter=-1,
              signalSummary=" ".join((
                f"ID:{object_id}",
                f"S1:{self._little(raw, 42, 8) - 128}",
                f"S2:{self._little(raw, 50, 6) - 32}",
                f"CTR:{self._little(raw, 56, 4)}",
                f"CRC:{self._little(raw, 60, 4):X}",
              )),
              allSignals=(
                ("DISTANCE", format_signal_value(d_rel)),
                ("LATERAL", format_signal_value(y_rel)),
                ("SPEED", format_signal_value(v_rel)),
                ("ID", str(object_id)),
                ("SOMETHING_1", str(self._little(raw, 42, 8) - 128)),
                ("SOMETHING_2", str(self._little(raw, 50, 6) - 32)),
                ("COUNTER", str(self._little(raw, 56, 4))),
                ("CHECKSUM", str(self._little(raw, 60, 4))),
              ),
            ))
            track_locations[track_id] = (address, bus)
            track_count += 1
        elif spec.name in ("CORNER_A_OBJECTS", "CORNER_B_OBJECTS"):
          object_start = 0x241 if spec.name == "CORNER_A_OBJECTS" else 0x279
          for address in range(object_start, object_start + 15):
            decoded = self._corner_object(payloads[address])
            if decoded is None:
              continue
            track_id = 900_000 + bus * 0x10000 + address
            d_rel, y_rel, v_rel = decoded
            tracks.append(DisplayTrack(
              trackId=track_id,
              dRel=d_rel,
              yRel=y_rel,
              vRel=v_rel,
              aRel=float("nan"),
              canAddress=address,
              canBus=bus,
            ))
            raw = int.from_bytes(payloads[address], "little")
            category = (raw >> 24) & 0x3
            rcs = self._signed((raw >> 56) & 0x7F, 7)
            unknown_87 = (raw >> 87) & 0x1
            unknown_108 = (raw >> 108) & 0x3FF
            unknown_118 = (raw >> 118) & 0x3FF
            unknown_128 = (raw >> 128) & 0xFFFFFFFFFFFFFFFF
            track_signals.append(DisplayTrackSignals(
              trackId=track_id,
              relLatSpeed=self._signed((raw >> 98) & 0x3FF, 10) * 0.05,
              absSpeed=float("nan"),
              width=float("nan"),
              length=float("nan"),
              orientationAngle=float("nan"),
              age=-1,
              coastAge=-1,
              state=-1,
              stateAlt=-1,
              trackCounter=-1,
              signalSummary=" ".join((
                f"CAT:{category}", f"RCS:{rcs}", f"U87:{unknown_87}",
                f"U108:{unknown_108:03X}", f"U118:{unknown_118:03X}", f"U128:{unknown_128:016X}",
              )),
              allSignals=(
                ("CHECKSUM", str(raw & 0xFFFF)),
                ("COUNTER", str((raw >> 16) & 0xFF)),
                ("UNKNOWN_CATEGORY", str(category)),
                ("UNKNOWN_BITS_26_55", str((raw >> 26) & 0x3FFFFFFF)),
                ("RCS", str(rcs)),
                ("LONG_DIST", format_signal_value(d_rel)),
                ("LAT_DIST", format_signal_value(y_rel)),
                ("UNKNOWN_BIT_87", str(unknown_87)),
                ("REL_SPEED", format_signal_value(v_rel)),
                ("REL_LAT_SPEED", format_signal_value(self._signed((raw >> 98) & 0x3FF, 10) * 0.05)),
                ("UNKNOWN_BITS_108_117", str(unknown_108)),
                ("UNKNOWN_BITS_118_127", str(unknown_118)),
                ("UNKNOWN_BITS_128_191", str(unknown_128)),
              ),
            ))
            track_locations[track_id] = (address, bus)
            track_count += 1
        elif spec.name == "CCNC_FUSED_OBJECTS":
          raw = int.from_bytes(payloads[0x162], "little")
          fused_slots = (
            ("FRONT", self._little(raw, 64, 5), self._little(raw, 69, 11) * 0.1, self._little(raw, 80, 7) * 0.1),
            ("FRONT_ALT", self._little(raw, 88, 5), self._little(raw, 93, 11) * 0.1, self._little(raw, 104, 7) * 0.1),
            ("LEFT", self._little(raw, 112, 5), self._little(raw, 117, 11) * 0.1, self._little(raw, 128, 7) * 0.1),
            ("RIGHT", self._little(raw, 136, 5), self._little(raw, 141, 11) * 0.1, self._little(raw, 152, 7) * 0.1),
            ("LEFT_REAR", self._big(raw, 167, 5), self._big(raw, 175, 8) * 0.1, self._big(raw, 182, 7) * 0.1),
            ("RIGHT_REAR", self._big(raw, 196, 5), self._little(raw, 197, 8) * 0.1, self._little(raw, 205, 7) * 0.1),
          )
          for label, status, distance, lateral in fused_slots:
            raw_signals.append(DisplayRawSignal(
              spec.start_address, spec.end_address, 0x162, bus, label,
              f"STATUS:{status} DIST:{distance:.1f}m LAT:{lateral:.1f}m",
            ))
            track_count += status != 0
          raw_signals.append(DisplayRawSignal(
            spec.start_address, spec.end_address, 0x162, bus, "FAULTS",
            " ".join((
              f"FSS:{self._little(raw, 213, 3)}", f"FCA:{self._little(raw, 216, 3)}",
              f"LSS:{self._little(raw, 219, 3)}", f"SLA:{self._little(raw, 222, 3)}",
              f"DAW:{self._little(raw, 225, 3)}", f"HBA:{self._little(raw, 228, 3)}",
              f"SCC:{self._little(raw, 231, 3)}", f"LFA:{self._little(raw, 234, 3)}",
            )),
          ))
        elif spec.name in ("CORNER_A_DETECTIONS", "CORNER_B_DETECTIONS", "RADAR_RAW_DETECTIONS"):
          for address in range(spec.start_address, spec.end_address + 1):
            for record, raw in enumerate(self._packed_detection_records(payloads[address])):
              if raw == 0:
                continue
              if spec.name in ("CORNER_A_DETECTIONS", "CORNER_B_DETECTIONS"):
                if (raw & 0x1FFF) == 8000:
                  continue
                raw_signals.append(DisplayRawSignal(
                  spec.start_address, spec.end_address, address, bus, f"REC{record}",
                  " ".join((
                    f"DIST?:{(raw & 0x1FFF) * 0.05:.2f}",
                    f"RSV:{(raw >> 13) & 0x7}",
                    f"PROP:{(raw >> 16) & 0x7F}",
                    f"AUX:{(raw >> 23) & 0x1FF}",
                    f"RAW:{raw:08X}",
                  )),
                ))
                track_count += 1
                continue
              if raw == 0xC8782EE0:
                continue
              raw_signals.append(DisplayRawSignal(
                spec.start_address, spec.end_address, address, bus, f"REC{record}",
                " ".join((
                  f"DIST?:{(raw & 0xFFF) * 0.05:.2f}",
                  f"FLAGS:{(raw >> 12) & 0xF}",
                  f"U16:{(raw >> 16) & 0xFF:02X}",
                  f"U24:{(raw >> 24) & 0xFF:02X}",
                  f"RAW:{raw:08X}",
                )),
              ))
              track_count += 1
        elif spec.name.startswith("RADAR_500_"):
          for address in range(spec.start_address, spec.end_address + 1):
            raw = int.from_bytes(payloads[address], "little")
            raw_signals.append(DisplayRawSignal(
              spec.start_address, spec.end_address, address, bus, f"{address:X}",
              self._radar_500_status_summary(address, raw),
            ))
        elif spec.name == "CAMERA_LANE_PATH":
          for address in range(spec.start_address, spec.end_address + 1):
            payload = payloads[address]
            raw_signals.append(DisplayRawSignal(
              spec.start_address, spec.end_address, address, bus, f"{address:X}",
              f"CTR:{payload[2]} DATA:{payload[3:].hex().upper()}",
            ))
        sources.append(DisplaySource(spec.start_address, spec.end_address, bus, track_count))
    return tuple(sources), tuple(tracks), tuple(track_signals), tuple(raw_signals), track_locations


def make_radar_snapshot(radar_data, track_signals: tuple[DisplayTrackSignals, ...] = (),
                        raw_signals: tuple[DisplayRawSignal, ...] = (),
                        track_locations: dict[int, tuple[int, int]] | None = None) -> RadarSnapshot:
  track_locations = track_locations or {}
  return RadarSnapshot(
    points=tuple(DisplayTrack(
      trackId=int(point.trackId),
      dRel=float(point.dRel),
      yRel=float(point.yRel),
      vRel=float(point.vRel),
      aRel=float("nan"),
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
    rawSignals=raw_signals,
    radarTracksAvailable=bool(radar_data.radarTracksAvailable),
  )


def source_name(start_address: int, end_address: int) -> str:
  spec = SPEC_BY_RANGE.get((start_address, end_address))
  if spec is not None:
    return "CAMERA_OBJECTS_235_248" if spec.source_kind == "camera" else spec.name
  research_spec = RESEARCH_SPEC_BY_RANGE.get((start_address, end_address))
  return research_spec.name if research_spec is not None else f"RADAR_{start_address:X}_{end_address:X}"


def source_details(start_address: int, end_address: int) -> str:
  spec = SPEC_BY_RANGE.get((start_address, end_address))
  if spec is not None:
    prefix = "forward-camera objects  " if spec.source_kind == "camera" else ""
    return f"{prefix}{spec.frequency} Hz  {spec.message_size} B"
  research_spec = RESEARCH_SPEC_BY_RANGE.get((start_address, end_address))
  return research_spec.details if research_spec is not None else "unknown format"


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
  return {0: "unknown (raw 0)", 1: "stationary", 2: "moving", 3: "stopped", 4: "oncoming"}.get(
    motion_state, f"unknown (raw {motion_state})",
  )


def dbc_motion_category(motion_state: int | None) -> str:
  if motion_state in (2, 4):
    return "moving"
  if motion_state in (1, 3):
    return "stationary"
  return "unknown"


def dbc_motion_color(motion_state: int | None) -> rl.Color:
  return {"moving": PURPLE, "stationary": WHITE}.get(dbc_motion_category(motion_state), MUTED)


def dbc_unknown_raw_label(motion_state: int | None) -> str | None:
  if dbc_motion_category(motion_state) != "unknown":
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
    category = dbc_motion_category(motion_states.get(int(track.trackId)))
    if ((filters[0] and category == "moving")
        or (filters[1] and category == "stationary")
        or (filters[2] and category == "unknown")):
      continue
    filtered_tracks.append(track)
  return filtered_tracks


def enable_dbc_detail_signals(radar_interface: RadarInterface, enhanced_parsers: set[tuple[str, int]]) -> None:
  """Add visualization-only signals to the branch parser without maintaining a second CAN decoder."""
  for radar_parser in radar_interface.radar_parsers:
    parser_key = (radar_parser.spec.name, radar_parser.bus)
    detail_signals = RADAR_DETAIL_SIGNALS.get(radar_parser.spec.name)
    if parser_key in enhanced_parsers or detail_signals is None:
      continue

    # This UI can intentionally run slower than replay and uses conflated CAN, so don't apply parser liveness checks here.
    messages = [(f"RADAR_TRACK_{addr:x}", 0) for addr in radar_parser.spec.address_range]
    parser = CANParser(
      radar_parser.spec.dbc_name,
      messages,
      radar_parser.bus,
      signals={*radar_parser.spec.signals, *detail_signals},
    )
    for message_state in parser.message_states.values():
      message_state.ignore_alive = True
    radar_parser.parser = parser
    enhanced_parsers.add(parser_key)


def dbc_signal_value(message, prefix: str, name: str, default=0):
  return message.get(f"{prefix}{name}", default)


def format_signal_value(value) -> str:
  if isinstance(value, float):
    if not math.isfinite(value):
      return "n/a"
    if value.is_integer():
      return str(int(value))
    return f"{value:.6g}"
  return str(value)


def dbc_signal_rows(message, prefix: str = "") -> tuple[tuple[str, str], ...]:
  rows = []
  for name, value in message.items():
    if prefix and name.startswith(("1_", "2_")) and not name.startswith(prefix):
      continue
    rows.append((name.removeprefix(prefix), format_signal_value(value)))
  return tuple(rows)


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

    if track_key[0] not in RADAR_DETAIL_SIGNALS:
      continue

    radar_parser = next((parser for parser in radar_interface.radar_parsers
                         if parser.spec.name == track_key[0] and parser.bus == active_bus), None)
    if radar_parser is None:
      continue

    prefix = f"{stored_address % 2 + 1}_" if len(spec.track_prefixes) > 1 else ""
    message = radar_parser.parser.vl[f"RADAR_TRACK_{can_address:x}"]
    motion_signal = f"{prefix}MOTION_STATE"
    if motion_signal in message:
      motion_state = int(message[motion_signal])
      if spec.name == "RADAR_235_248":
        motion_state = 1 if motion_state in (1, 2, 3, 6) else 2 if motion_state in (5, 8, 9) else 0
      states[int(point.trackId)] = motion_state
    elif spec.name == "RADAR_500_53F" and int(message.get("ONCOMING_ESR", 0)):
      states[int(point.trackId)] = 4

    if spec.name == "RADAR_210_21F":
      signal_summary = " ".join((
        f"Q:{int(dbc_signal_value(message, prefix, 'TRACK_QUALITY'))}",
        f"RCS:{int(dbc_signal_value(message, prefix, 'RCS'))}",
        f"U4:{int(dbc_signal_value(message, prefix, 'NEW_SIGNAL_4'))}",
        f"U18:{int(dbc_signal_value(message, prefix, 'NEW_SIGNAL_18'))}",
        f"ID:{int(dbc_signal_value(message, prefix, 'OBJECT_ID'))}",
      ))
    elif spec.name == "RADAR_3A5_3C4":
      geometry = "/".join(
        str(int(dbc_signal_value(message, prefix, f"NEW_SIGNAL_{index}"))) for index in range(12, 18)
      )
      signal_summary = " ".join((
        f"Q:{int(dbc_signal_value(message, prefix, 'TRACK_QUALITY'))}",
        f"RCS:{int(dbc_signal_value(message, prefix, 'RCS'))}",
        f"U4:{int(dbc_signal_value(message, prefix, 'NEW_SIGNAL_4'))}",
        f"U5:{int(dbc_signal_value(message, prefix, 'NEW_SIGNAL_5'))}",
        f"U18:{int(dbc_signal_value(message, prefix, 'NEW_SIGNAL_18'))}",
        f"G12-17:{geometry}",
      ))
    else:
      signal_summary = " ".join(f"{name}:{value}" for name, value in dbc_signal_rows(message, prefix)[:6])
    details.append(DisplayTrackSignals(
      trackId=int(point.trackId),
      relLatSpeed=float(dbc_signal_value(message, prefix, "REL_LAT_SPEED", float("nan"))),
      absSpeed=float(dbc_signal_value(message, prefix, "ABS_SPEED", float("nan"))),
      width=float(dbc_signal_value(message, prefix, "WIDTH", float("nan"))),
      length=float(dbc_signal_value(message, prefix, "LENGTH", float("nan"))),
      orientationAngle=float(dbc_signal_value(message, prefix, "ORIENTATION_ANGLE", float("nan"))),
      age=int(dbc_signal_value(message, prefix, "AGE", -1)),
      coastAge=int(dbc_signal_value(message, prefix, "COAST_AGE", -1)),
      state=int(dbc_signal_value(message, prefix, "STATE", -1)),
      stateAlt=int(dbc_signal_value(message, prefix, "STATE_ALT", -1)),
      trackCounter=int(dbc_signal_value(message, prefix, "TRACK_COUNTER", -1)),
      signalSummary=signal_summary,
      allSignals=dbc_signal_rows(message, prefix),
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
  research_decoder = ResearchCanDecoder()
  enhanced_parsers: set[tuple[str, int]] = set()
  radar_snapshot = RadarSnapshot()
  snapshot = radar_snapshot
  motion_states: dict[int, int] = {}
  last_publish_time = 0.0
  last_can_message_time = 0.0

  while True:
    sm.update(100)
    radar_data = None
    if sm.updated["can"]:
      last_can_message_time = time.monotonic()
      can_messages = [(message.address, bytes(message.dat), message.src) for message in sm["can"]]
      research_decoder.update(can_messages)
      radar_data = radar_interface.update([(sm.logMonoTime["can"], can_messages)])
      enable_dbc_detail_signals(radar_interface, enhanced_parsers)
      if radar_data is not None:
        motion_states, track_signals, track_locations = get_dbc_track_details(radar_interface)
        radar_snapshot = make_radar_snapshot(radar_data, track_signals, track_locations=track_locations)
      research_sources, research_tracks, research_signals, raw_signals, _ = research_decoder.snapshot()
      snapshot = RadarSnapshot(
        points=(*radar_snapshot.points, *research_tracks),
        trackSources=(*radar_snapshot.trackSources, *research_sources),
        trackSignals=(*radar_snapshot.trackSignals, *research_signals),
        rawSignals=raw_signals,
        radarTracksAvailable=radar_snapshot.radarTracksAvailable,
      )

    now = time.monotonic()
    if radar_data is not None or now - last_publish_time >= 0.1:
      replace_queued_value(
        output_queue, (snapshot, motion_states, sm.alive["can"], sm.seen["can"], last_can_message_time),
      )
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
    (rl.KeyboardKey.KEY_A, "audio"),
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
  del hovered_id
  if selected_id is not None and any(int(track.trackId) == selected_id for track in tracks):
    return selected_id
  return None


def toggle_selected_track_id(selected_id: int | None, clicked_id: int | None, tracks) -> int | None:
  selected_id = retain_selected_track_id(selected_id, None, tracks)
  if clicked_id is None:
    return selected_id
  return None if selected_id == clicked_id else clicked_id


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
  selected_id = retain_selected_track_id(selected_id, None, tracks)
  if current_hovered_id is not None and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
    selected_id = toggle_selected_track_id(selected_id, current_hovered_id, tracks)

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


def selected_signal_row_count(detail: DisplayTrackSignals | None) -> int:
  return math.ceil(len(detail.allSignals) / 2) if detail is not None else 0


def draw_selected_signal_inspector(font, rect: rl.Rectangle, track, detail: DisplayTrackSignals,
                                   can_location: str, motion_state: int | None, scroll: int) -> None:
  rows = tuple(detail.allSignals[index:index + 2] for index in range(0, len(detail.allSignals), 2))
  capacity = table_capacity(rect)
  visible_rows = rows[scroll:scroll + capacity]
  title = f"TRACK {track.trackId}  ALL SIGNALS"
  subtitle = " ".join((
    can_location, dbc_motion_class(motion_state),
    f"DIST {track.dRel:.2f}m", f"LAT {track.yRel:+.2f}m", f"REL V {track.vRel:+.2f}m/s",
  ))
  draw_text(font, title, rect.x + 12, rect.y + 8, 21, CYAN)
  draw_text(font, subtitle, rect.x + 300, rect.y + 11, 15, TEXT)
  draw_text(font, "click selected point again to close", rect.x + 12, rect.y + 36, 14, MUTED)
  if rows:
    draw_text(font, f"{scroll + 1}-{scroll + len(visible_rows)} / {len(rows)} rows",
              rect.x + rect.width - 150, rect.y + 36, 14, MUTED)
  header_y = rect.y + 58
  columns = (("SIGNAL", 0.02), ("VALUE", 0.31), ("SIGNAL", 0.52), ("VALUE", 0.81))
  for label, offset in columns:
    draw_text(font, label, rect.x + rect.width * offset, header_y, 14, MUTED)
  for row, signal_pairs in enumerate(visible_rows):
    y = header_y + 22 + row * 24
    if row % 2:
      rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(255, 255, 255, 8))
    for pair_index, (name, value) in enumerate(signal_pairs):
      base = 0.02 if pair_index == 0 else 0.52
      draw_text(font, name, rect.x + rect.width * base, y, 15, TEXT)
      draw_text(font, value, rect.x + rect.width * (base + 0.29), y, 15, CYAN)


def draw_track_table(font, rect: rl.Rectangle, tracks, motion_states: dict[int, int], scroll: int,
                     selected_id: int | None, hovered_id: int | None,
                     track_signals: dict[int, DisplayTrackSignals], track_locations: dict[int, tuple[int, int]],
                     table_mode: str, raw_signals: tuple[DisplayRawSignal, ...] = ()) -> None:
  rl.draw_rectangle_rec(rect, BACKGROUND)
  rl.draw_line_ex(rl.Vector2(rect.x, rect.y), rl.Vector2(rect.x + rect.width, rect.y), 2.0, GRID)
  sorted_tracks = sorted(tracks, key=lambda track: (track.dRel, track.trackId))
  capacity = table_capacity(rect)

  selected_track = next((track for track in sorted_tracks if int(track.trackId) == selected_id), None)
  selected_detail = track_signals.get(selected_id) if selected_id is not None else None
  if selected_track is not None and selected_detail is not None and selected_detail.allSignals:
    can_address, can_bus = track_locations.get(int(selected_track.trackId), (-1, -1))
    can_location = f"{can_address:X}/B{can_bus}" if can_address >= 0 and can_bus >= 0 else "n/a"
    draw_selected_signal_inspector(
      font, rect, selected_track, selected_detail, can_location,
      motion_states.get(int(selected_track.trackId)), scroll,
    )
    return

  if table_mode == "signals":
    rows = [
      (
        "{:X}/B{}".format(*track_locations.get(int(track.trackId), (-1, -1))),
        f"TRACK {track.trackId}",
        track_signals[int(track.trackId)].signalSummary,
        int(track.trackId),
      )
      for track in sorted_tracks
      if int(track.trackId) in track_signals
    ]
    rows.extend(
      (
        f"{signal.address:X}/B{signal.bus}",
        f"{source_name(signal.startAddress, signal.endAddress).removeprefix('RADAR_')} {signal.label}",
        signal.signalSummary,
        None,
      )
      for signal in sorted(raw_signals, key=lambda item: (
        item.startAddress, item.bus, item.address, item.label,
      ))
    )
    visible_rows = rows[scroll:scroll + capacity]
    draw_text(font, "SIGNALS", rect.x + 12, rect.y + 8, 21, TEXT)
    if rows:
      draw_text(font, f"{scroll + 1}-{scroll + len(visible_rows)} / {len(rows)}",
                rect.x + rect.width - 112, rect.y + 11, 16, MUTED)
    columns = (("CAN", 0.02), ("SOURCE / ITEM", 0.12), ("DECODED / RAW SIGNALS", 0.36))
    header_y = rect.y + 36
    for title, offset in columns:
      draw_text(font, title, rect.x + rect.width * offset, header_y, 15, MUTED)
    for row, (can_location, label, summary, track_id) in enumerate(visible_rows):
      y = header_y + 23 + row * 24
      if track_id == selected_id:
        rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(CYAN.r, CYAN.g, CYAN.b, 42))
      elif row % 2:
        rl.draw_rectangle_rec(rl.Rectangle(rect.x, y - 3, rect.width, 24), rl.Color(255, 255, 255, 8))
      draw_text(font, can_location, rect.x + rect.width * 0.02, y, 15, TEXT)
      draw_text(font, label, rect.x + rect.width * 0.12, y, 15, CYAN if track_id is None else TEXT)
      draw_text(font, summary, rect.x + rect.width * 0.36, y, 15, TEXT)
    return

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
        (f"{detail.relLatSpeed:+.1f}" if detail and math.isfinite(detail.relLatSpeed) else "n/a",
         0.50, TEXT if detail and math.isfinite(detail.relLatSpeed) else MUTED),
        (f"{track.aRel:+.1f}" if math.isfinite(track.aRel) else "n/a", 0.61, TEXT),
        (f"{detail.absSpeed:.1f}" if detail and math.isfinite(detail.absSpeed) else "n/a",
         0.73, TEXT if detail and math.isfinite(detail.absSpeed) else MUTED),
        (str(detail.age) if detail and detail.age >= 0 else "n/a", 0.88, TEXT if detail and detail.age >= 0 else MUTED),
      )
    elif table_mode == "object":
      values = (
        (str(track.trackId), 0.02, TEXT),
        (can_location, 0.09, TEXT if can_address >= 0 else MUTED),
        (f"{detail.width:.1f}" if detail and math.isfinite(detail.width) else "n/a",
         0.21, TEXT if detail and math.isfinite(detail.width) else MUTED),
        (f"{detail.length:.1f}" if detail and math.isfinite(detail.length) else "n/a",
         0.33, TEXT if detail and math.isfinite(detail.length) else MUTED),
        (f"{detail.orientationAngle:+.0f}" if detail and math.isfinite(detail.orientationAngle) else "n/a",
         0.45, TEXT if detail and math.isfinite(detail.orientationAngle) else MUTED),
        (dbc_track_state(detail.state) if detail and detail.state >= 0 else "n/a",
         0.57, TEXT if detail and detail.state >= 0 else MUTED),
        (str(detail.coastAge) if detail and detail.coastAge >= 0 else "n/a",
         0.74, TEXT if detail and detail.coastAge >= 0 else MUTED),
        (str(detail.trackCounter) if detail and detail.trackCounter >= 0 else "n/a",
         0.87, TEXT if detail and detail.trackCounter >= 0 else MUTED),
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
  draw_text(font, "Open route or live car", dialog.x + 20, dialog.y + 17, 22, TEXT)
  draw_text(font, "Paste a route, segment ID, or IP address, then press Enter.",
            dialog.x + 20, dialog.y + 48, 15, MUTED)

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
                            seek_active: bool, scrub: ReplayScrubState, audio_player: ReplayAudioPlayer) -> str | None:
  rl.draw_rectangle_rec(bounds, rl.Color(8, 12, 18, 248))
  rl.draw_line_ex(rl.Vector2(bounds.x, bounds.y), rl.Vector2(bounds.x + bounds.width, bounds.y), 1.0, MUTED)
  if audio_player.error:
    audio_label = "AUDIO ERR"
    audio_color = RED
    audio_tooltip = f"Audio output failed: {audio_player.error}"
  elif audio_player.enabled and audio_player.available:
    audio_label = "AUDIO ON"
    audio_color = GREEN
    audio_tooltip = "A: disable recorded video audio"
  elif audio_player.enabled:
    audio_label = "AUDIO WAIT"
    audio_color = ORANGE
    audio_tooltip = "Waiting for recorded audio in this route"
  else:
    audio_label = "AUDIO"
    audio_color = MUTED
    audio_tooltip = "A: play recorded audio from the route video"
  controls = (
    ("-60s", "M", CYAN, "Shift+M: back 60 seconds"),
    ("-10s", "S", CYAN, "Shift+S: back 10 seconds"),
    ("PAUSE", " ", GREEN, "Space: pause / resume"),
    (audio_label, "audio", audio_color, audio_tooltip),
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


def apply_replay_control(replay: ManagedReplay, audio_player: ReplayAudioPlayer, action: str | None,
                         seek_input: str, seek_active: bool) -> tuple[str, bool]:
  if action == "audio":
    audio_player.toggle()
    return seek_input, False
  if action is not None and action.startswith("seek-time:"):
    audio_player.clear()
    replay.send(f"\n{action.removeprefix('seek-time:')}\n")
    return "", False
  if action == "seek-focus":
    return seek_input, True
  if action == "seek-blur":
    return seek_input, False
  if action == "seek":
    if seek_input:
      audio_player.clear()
      replay.send(f"\n{seek_input}\n")
    return "", False
  if action is not None:
    if action in {" ", "+", "-", "s", "S", "m", "M", "e", "d", "t", "i", "w", "c", "q"}:
      audio_player.clear()
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
                       both_cameras_available: bool, remote_address: str | None, bridge_connected: bool,
                       visible_tracks, motion_states: dict[int, int], track_locations: dict[int, tuple[int, int]],
                       source_filters: dict[RadarSourceKey, tuple[bool, bool, bool]],
                       table_mode: str, fps: int, show_inactive_sources: bool) -> str | tuple[str, RadarSourceKey] | None:
  rl.draw_rectangle_rec(rect, rl.Color(11, 16, 24, 225))
  tracks = live_tracks.points if valid else ()
  all_sources = sorted(live_tracks.trackSources, key=radar_source_sort_key) if valid else []
  sources = all_sources if show_inactive_sources else [source for source in all_sources if source.trackCount > 0]
  hidden_source_count = len(all_sources) - len(sources)
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
        (compact_name, f"CAN address range 0x{source.startAddress:X}-0x{source.endAddress:X}"),
        (f"B{source.bus}", f"CAN bus {source.bus} carrying this source"),
      ]
      if spec is not None:
        source_parts.extend((
          (f"{spec.frequency} Hz", "Expected radar message frequency"),
          (f"{spec.message_size} B", "Radar CAN message payload size"),
        ))
      else:
        details = source_details(source.startAddress, source.endAddress)
        source_parts.append((details, details))
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
      moving_count = sum(dbc_motion_category(motion_states.get(track_id)) == "moving" for track_id in source_track_ids)
      stationary_count = sum(
        dbc_motion_category(motion_states.get(track_id)) == "stationary" for track_id in source_track_ids
      )
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
  elif all_sources:
    source_text = f"{hidden_source_count} inactive source{'s' if hidden_source_count != 1 else ''} hidden"
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
  table_label = {"motion": "MOTION", "kinematics": "KIN", "object": "OBJ", "signals": "SIGNALS"}[table_mode]
  chip_specs = [
    ("OPEN", GREEN, "route", "Open a route or live-car IP, or paste one with Cmd/Ctrl+V"),
    (source_title, CYAN, "source", "Switch CAN / liveTracks source"),
    ("LABELS ON" if show_labels else "LABELS", GREEN if show_labels else MUTED, "labels", "Show / hide all labels"),
  ]
  if remote_address is not None:
    bridge_label = f"BRIDGE {'OK' if bridge_connected else '--'}  {remote_address}"
    bridge_tooltip = (
      f"Receiving live messages from {remote_address}"
      if bridge_connected
      else f"Waiting for remote bridge messages from {remote_address}"
    )
    chip_specs.insert(1, (bridge_label, GREEN if bridge_connected else ORANGE, None, bridge_tooltip))
  if both_cameras_available:
    chip_specs.append((camera_label, CYAN, "camera", "Cycle road / wide / fused camera"))
  if hidden_source_count or show_inactive_sources:
    source_list_label = "ACTIVE ONLY" if show_inactive_sources else f"RANGES +{hidden_source_count}"
    source_list_tooltip = (
      "Hide inactive and empty source ranges"
      if show_inactive_sources
      else "Show inactive and empty source ranges"
    )
    chip_specs.append((source_list_label, MUTED, "sources", source_list_tooltip))
  chip_specs.append((table_label, MUTED, "table", "Cycle motion / kinematics / object / signals table"))
  clicked_action = source_clicked_action
  hovered_tooltip = source_hovered_tooltip or top_hovered_tooltip
  for label, color, action, tooltip in chip_specs:
    chip_x, chip_rect, hovered = draw_status_chip(font, label, chip_x, chip_y, color, mouse_position)
    if hovered:
      hovered_tooltip = (tooltip, chip_rect)
      if action is not None and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
        clicked_action = action
  rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND if hovered_tooltip is not None
                      else rl.MouseCursor.MOUSE_CURSOR_DEFAULT)
  if hovered_tooltip is not None:
    draw_status_tooltip(font, hovered_tooltip[0], hovered_tooltip[1], rect)
  return clicked_action


def ui_thread(addr: str, start_wide: bool = False, start_fused: bool = False, start_route: str | None = None) -> None:
  remote_relays = start_remote_relays(addr) if addr != "127.0.0.1" else []
  remote_address = addr if remote_relays else None
  remote_bridge_last_message = 0.0
  bridge_connected = False
  messaging_addr = "127.0.0.1"
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

  font_path = os.path.join(BASEDIR, "openpilot/selfdrive/assets/fonts/JetBrainsMono-Medium.ttf")
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
  ], addr=messaging_addr)
  # SubMaster conflates messages, but every 50 ms audio packet is needed for gapless playback.
  audio_socket = messaging.sub_sock("rawAudioData", addr=messaging_addr, conflate=False)

  process_context = multiprocessing.get_context("spawn")
  decoder_output = process_context.Queue(maxsize=1)
  decoder_process = process_context.Process(
    target=radar_decoder_worker, args=(messaging_addr, decoder_output), daemon=True,
  )
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
  show_inactive_sources = False
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
  route_dialog_open = start_route is None and addr == "127.0.0.1"
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
  audio_player = ReplayAudioPlayer()
  route_message_start_mono: int | None = None
  route_fingerprint = ""
  current_route_seconds = route_start_seconds(route_input)

  def open_target(target: str) -> str:
    nonlocal remote_relays, remote_address, remote_bridge_last_message, bridge_connected
    nonlocal replay_process, timeline_process, replay_timeline, replay_scrub
    nonlocal route_input, route_loading, route_loading_started, route_message_start_mono
    nonlocal route_fingerprint, current_route_seconds, replay_seek_input, replay_seek_active
    nonlocal can_tracks, live_tracks, can_data_seen, live_data_seen, can_data_alive, decoded_motion_states
    nonlocal table_scroll, selected_track_id, calibration, calibration_key, overlay_dirty, show_inactive_sources
    nonlocal decoder_process

    target = target.strip()
    if not target:
      return "Enter a route, segment ID, or IP address."

    stop_route_replay(replay_process)
    replay_process = None
    stop_timeline_process(timeline_process)
    timeline_process = None
    stop_remote_relays(remote_relays)
    remote_relays = []
    remote_address = None
    remote_bridge_last_message = 0.0
    bridge_connected = False
    decoder_process.terminate()
    decoder_process.join(timeout=1.0)

    for output_queue in (decoder_output, timeline_output):
      while True:
        try:
          output_queue.get_nowait()
        except queue.Empty:
          break

    can_tracks = RadarSnapshot()
    live_tracks = RadarSnapshot()
    can_data_seen = False
    live_data_seen = False
    can_data_alive = False
    decoded_motion_states = {}
    replay_timeline = ReplayTimeline()
    replay_scrub = ReplayScrubState()
    audio_player.reset()
    messaging.drain_sock(audio_socket)
    replay_seek_input = ""
    replay_seek_active = False
    route_loading = False
    route_message_start_mono = None
    route_fingerprint = ""
    current_route_seconds = 0.0
    table_scroll = 0
    selected_track_id = None
    show_inactive_sources = False
    source_filters.clear()
    calibration = None
    calibration_key = None
    overlay_dirty = True

    if (live_ip := parse_live_ip(target)) is not None:
      route_input = live_ip
      remote_relays = start_remote_relays(live_ip)
      remote_address = live_ip
      decoder_process = process_context.Process(
        target=radar_decoder_worker, args=(messaging_addr, decoder_output), daemon=True,
      )
      decoder_process.start()
      print(f"Radar debugger opened live car: {live_ip}", flush=True)
      return ""

    route_input = target
    replay_process, error = replace_route_replay(None, target)
    route_loading = replay_process is not None and not error
    route_loading_started = time.monotonic()
    current_route_seconds = route_start_seconds(target)
    if route_loading:
      replay_timeline = ReplayTimeline(current_route_seconds, current_route_seconds)
      timeline_process = start_timeline_process(process_context, timeline_process, timeline_output, target)
    decoder_process = process_context.Process(
      target=radar_decoder_worker, args=(messaging_addr, decoder_output), daemon=True,
    )
    decoder_process.start()
    return error

  if start_route:
    route_error = open_target(start_route)
    route_dialog_open = bool(route_error)
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
          replay_process, audio_player, "seek", replay_seek_input, replay_seek_active,
        )
      elif rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
        replay_seek_active = False
    elif modifier_down and rl.is_key_pressed(rl.KeyboardKey.KEY_V):
      clipboard_text = rl.get_clipboard_text() or ""
      route_input = "".join(character for character in clipboard_text if 32 <= ord(character) <= 126)[:180]
      route_cursor = len(route_input)
      route_select_all = False
      route_error = open_target(route_input)
      route_dialog_open = bool(route_error)
      composite_mode = composite_mode and not route_dialog_open
    elif modifier_down:
      pass
    elif replay_process is not None and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
      replay_seek_active = True
    elif replay_process is not None and (replay_command := replay_keyboard_command()) is not None:
      replay_seek_input, replay_seek_active = apply_replay_control(
        replay_process, audio_player, replay_command, replay_seek_input, replay_seek_active,
      )
    if open_entered_route:
      route_error = open_target(route_input)
      route_dialog_open = bool(route_error)
      route_select_all = False

    sm.update(0)
    for audio_event in messaging.drain_sock(audio_socket):
      if replay_process is not None:
        raw_audio = audio_event.rawAudioData
        audio_player.push(
          bytes(raw_audio.data),
          int(raw_audio.sampleRate),
          int(audio_event.logMonoTime),
          replay_process.playback_speed,
        )
    if remote_address is not None and any(sm.updated.values()):
      remote_bridge_last_message = time.monotonic()
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
        can_tracks, decoded_motion_states, can_data_alive, can_data_seen, last_can_message_time = decoder_output.get_nowait()
        remote_bridge_last_message = max(remote_bridge_last_message, last_can_message_time)
      except queue.Empty:
        break
    bridge_connected = (
      remote_address is not None
      and bool(remote_relays)
      and remote_relays[0].poll() is None
      and time.monotonic() - remote_bridge_last_message < REMOTE_BRIDGE_TIMEOUT_SECONDS
    )
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
    visible_status_sources = (
      status_sources
      if show_inactive_sources
      else tuple(source for source in status_sources if source.trackCount > 0)
    )
    status_height = 88 + max(0, len(visible_status_sources) - 1) * 30
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
      raw_signals = can_tracks.rawSignals
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
      raw_signals = ()
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
    current_table_mode = TABLE_MODES[table_mode_index]
    capacity = table_capacity(table_rect)
    selected_detail = track_signals.get(selected_track_id) if selected_track_id is not None else None
    if selected_detail is not None and selected_detail.allSignals:
      table_row_count = selected_signal_row_count(selected_detail)
    elif current_table_mode == "signals":
      table_row_count = sum(int(track.trackId) in track_signals for track in tracks) + len(raw_signals)
    else:
      table_row_count = len(tracks)
    max_scroll = max(0, table_row_count - capacity)
    if rl.check_collision_point_rec(rl.get_mouse_position(), table_rect):
      table_scroll -= int(rl.get_mouse_wheel_move() * 3)
    table_scroll = int(np.clip(table_scroll, 0, max_scroll))
    table_hover_id = None if (
      composite_mode or current_table_mode == "signals" or selected_detail is not None
    ) else table_hovered_track_id(
      tracks, table_rect, table_scroll, rl.get_mouse_position(),
    )
    if (table_hover_id is not None
        and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)):  # noqa: TID251 - standalone raylib tool
      next_selected_id = toggle_selected_track_id(selected_track_id, table_hover_id, tracks)
      if next_selected_id != selected_track_id:
        table_scroll = 0
      selected_track_id = next_selected_id

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
      previous_selected_track_id = selected_track_id
      selected_track_id = draw_fused_camera_mode(
        font, road_camera_view, wide_camera_view, fused_device_camera, rpy_calib, wide_from_device_euler,
        fused_bounds, tracks, show_labels, motion_states,
        track_locations, selected_tracks.trackSources, selected_track_id,
      )
      if selected_track_id != previous_selected_track_id:
        table_scroll = 0
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
        "fused", both_camera_streams_available(fused_available_streams), remote_address, bridge_connected,
        tracks, motion_states, track_locations, source_filters, table_mode, rl.get_fps(), show_inactive_sources,
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
      elif clicked_action == "sources":
        show_inactive_sources = not show_inactive_sources
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
          replay_timeline, v_ego, route_loading, replay_seek_input, replay_seek_active, replay_scrub, audio_player,
        )
        replay_seek_input, replay_seek_active = apply_replay_control(
          replay_process, audio_player, replay_action, replay_seek_input, replay_seek_active,
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
    selected_track_id = retain_selected_track_id(selected_track_id, None, tracks)
    if current_hovered_id is not None and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
      next_selected_id = toggle_selected_track_id(selected_track_id, current_hovered_id, tracks)
      if next_selected_id != selected_track_id:
        table_scroll = 0
      selected_track_id = next_selected_id

    selected_detail = track_signals.get(selected_track_id) if selected_track_id is not None else None
    if selected_track_id is not None and current_table_mode != "signals" and selected_detail is None:
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
      if sm.valid["modelV2"] and calibration is not None:
        # Partially downloaded/corrupt model events can contain points on the
        # projection plane. ui_helpers safely discards their out-of-bounds
        # integer results, but NumPy otherwise emits noisy divide/cast warnings.
        with warnings.catch_warnings(), np.errstate(divide="ignore", invalid="ignore", over="ignore"):
          warnings.filterwarnings("ignore", message="invalid value encountered in cast", category=RuntimeWarning)
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
                     track_signals, track_locations, table_mode, raw_signals)
    clicked_action = draw_source_status(
      font, status_rect, selected_tracks, data_valid, data_alive,
      replay_process is not None or can_data_seen or live_data_seen, show_labels, data_source,
      "wide 180" if camera_view.stream_type == VisionStreamType.VISION_STREAM_WIDE_ROAD else "road",
      both_camera_streams_available(camera_view.available_streams), remote_address, bridge_connected,
      tracks, motion_states, track_locations, source_filters, table_mode, rl.get_fps(), show_inactive_sources,
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
    elif clicked_action == "sources":
      show_inactive_sources = not show_inactive_sources
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
        route_error = open_target(route_input)
        route_dialog_open = bool(route_error)
        route_select_all = False
    if route_loading and not route_dialog_open:
      draw_route_loading(
        font, rl.Rectangle(0, 0, window_width, window_height), route_input, time.monotonic() - route_loading_started,
      )
    if replay_process is not None and not route_dialog_open:
      replay_action = draw_replay_control_bar(
        font, replay_bar_rect, replay_process, current_route_seconds, route_fingerprint,
        replay_timeline, v_ego, route_loading, replay_seek_input, replay_seek_active, replay_scrub, audio_player,
      )
      replay_seek_input, replay_seek_active = apply_replay_control(
        replay_process, audio_player, replay_action, replay_seek_input, replay_seek_active,
      )
    if table_hover_id is not None and not route_dialog_open:
      rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND)
    rl.end_drawing()

  stop_route_replay(replay_process)
  audio_player.close()
  stop_timeline_process(timeline_process)
  stop_remote_relays(remote_relays)
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
    description="Decode live or replay CAN with Hyundai auto radar discovery and visualize the resulting tracks.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("target", nargs="?", default="127.0.0.1", help="Route, segment ID, or live-car IP address.")
  parser.add_argument("--route", help="Route or segment ID to open in replay when the debugger starts.")
  parser.add_argument("--wide", action="store_true", help="Start with the wide/full field-of-view road camera.")
  parser.add_argument("--fused", action="store_true", help="Start with the full-screen fused road and wide cameras.")
  return parser


if __name__ == "__main__":
  args = get_arg_parser().parse_args(sys.argv[1:])
  address = args.target
  route = args.route
  if route is None and parse_live_ip(address) is None:
    address, route = "127.0.0.1", address
  try:
    ui_thread(address, args.wide, args.fused, route)
  except KeyboardInterrupt:
    pass
