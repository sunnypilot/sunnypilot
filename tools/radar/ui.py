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
from datetime import datetime, timedelta
import fcntl

import numpy as np
import pyray as rl

import cereal.messaging as messaging
from msgq.visionipc import VisionStreamType
from openpilot.common.basedir import BASEDIR
from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
from openpilot.common.transformations.orientation import rot_from_euler
from openpilot.selfdrive.ui.mici.onroad.cameraview import CameraView
from openpilot.selfdrive.ui.sunnypilot.onroad.radar_tracks import RELATIVE_SPEED_MOVING_THRESHOLD, radar_track_color, \
                                                                  radar_track_is_stationary
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
RADAR_DETAIL_SIGNALS = {
  "MOTION_STATE", "REL_LAT_SPEED", "ABS_SPEED", "WIDTH", "LENGTH", "ORIENTATION_ANGLE",
  "AGE", "COAST_AGE", "STATE_ALT", "TRACK_COUNTER",
}
TABLE_MODES = ("comparison", "kinematics", "object")
PLAYBACK_SPEEDS = (0.2, 0.5, 1.0, 2.0, 4.0, 8.0)


@dataclass
class ManagedReplay:
  process: subprocess.Popen
  master_fd: int
  paused: bool = False
  playback_speed: float = 1.0
  progress_current: int = 0
  progress_total: int = 0
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

  def close_terminal(self) -> None:
    if self.master_fd >= 0:
      os.close(self.master_fd)
      self.master_fd = -1


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
    return start_route_replay(route), ""
  except OSError as exc:
    return None, f"Could not start replay: {exc}"


def route_start_seconds(route: str) -> float:
  match = re.search(r"(?:--|/)(\d+)(?::[^/]*)?(?:/[qra])?$", route)
  return int(match.group(1)) * 60.0 if match is not None else 0.0


def route_wall_time(route: str, route_seconds: float) -> str:
  match = re.search(r"\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}", route)
  if match is None:
    return "--"
  try:
    route_datetime = datetime.strptime(match.group(), "%Y-%m-%d--%H-%M-%S") + timedelta(seconds=route_seconds)
  except ValueError:
    return "--"
  return route_datetime.strftime("%a %b %d %H:%M:%S %Y")


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


def make_radar_snapshot(radar_data, track_signals: tuple[DisplayTrackSignals, ...] = ()) -> RadarSnapshot:
  return RadarSnapshot(
    points=tuple(DisplayTrack(
      trackId=int(point.trackId),
      dRel=float(point.dRel),
      yRel=float(point.yRel),
      vRel=float(point.vRel),
      aRel=float(point.aRel),
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


def implementation_class(v_rel: float, v_ego: float) -> str:
  if radar_track_is_stationary(v_rel, v_ego):
    return "stationary"
  if abs(v_rel) <= RELATIVE_SPEED_MOVING_THRESHOLD:
    return "speed matched"
  return "approaching" if v_rel < 0.0 else "receding"


def dbc_motion_class(motion_state: int | None) -> str:
  return {0: "unknown", 1: "stationary", 2: "moving"}.get(motion_state, "n/a")


def dbc_motion_color(motion_state: int | None) -> rl.Color:
  return {0: MUTED, 1: WHITE, 2: PURPLE}.get(motion_state, MUTED)


def display_track_color(track, v_ego: float, motion_states: dict[int, int], use_dbc_colors: bool) -> rl.Color:
  if use_dbc_colors:
    return dbc_motion_color(motion_states.get(int(track.trackId)))
  return radar_track_color(track.vRel, v_ego)


def filter_tracks(tracks, motion_states: dict[int, int], hide_unknown: bool, hide_stationary: bool):
  return [
    track for track in tracks
    if not (hide_unknown and motion_states.get(int(track.trackId)) not in (1, 2))
    and not (hide_stationary and motion_states.get(int(track.trackId)) == 1)
  ]


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


def get_dbc_track_details(radar_interface: RadarInterface) -> tuple[dict[int, int], tuple[DisplayTrackSignals, ...]]:
  states = {}
  details = []
  for track_key, point in radar_interface.pts.items():
    if not isinstance(track_key, tuple) or track_key[0] != "RADAR_3A5_3C4":
      continue

    active_bus = radar_interface.active_radar_buses.get(track_key[0])
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
  return states, tuple(details)


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
        motion_states, track_signals = get_dbc_track_details(radar_interface)
        snapshot = make_radar_snapshot(radar_data, track_signals)

    now = time.monotonic()
    if radar_data is not None or now - last_publish_time >= 0.1:
      replace_queued_value(output_queue, (snapshot, motion_states, sm.alive["can"], sm.seen["can"]))
      last_publish_time = now


def draw_text(font, text: str, x: float, y: float, size: float, color: rl.Color = TEXT) -> None:
  rl.draw_text_ex(font, text, rl.Vector2(round(x), round(y)), size, 0, color)


def measure_standalone_text(font, text: str, size: float) -> rl.Vector2:
  return rl.measure_text_ex(font, text, size, 0)  # noqa: TID251 - standalone raylib tool


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


def draw_track_popup(font, track, x: float, y: float, radius: float, bounds: rl.Rectangle, color: rl.Color) -> None:
  label = f"#{track.trackId}  {track.dRel:.1f} m  {track.vRel:+.1f} m/s"
  label_size = measure_text_cached(font, label, 18)
  label_x = float(np.clip(x - label_size.x / 2, bounds.x + 5, bounds.x + bounds.width - label_size.x - 5))
  label_y = max(bounds.y + 5, y - radius - 29)
  rl.draw_rectangle_rounded(
    rl.Rectangle(label_x - 5, label_y - 2, label_size.x + 10, 24), 0.25, 4, rl.Color(0, 0, 0, 220),
  )
  draw_text(font, label, label_x, label_y, 18, color)


def draw_camera_tracks(font, calibration: Calibration | None, tracks, camera_rect: rl.Rectangle, v_ego: float,
                       show_labels: bool, motion_states: dict[int, int], use_dbc_colors: bool,
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

    color = display_track_color(track, v_ego, motion_states, use_dbc_colors)
    is_hovered = int(track.trackId) == hovered_id
    is_selected = int(track.trackId) == selected_id
    is_previewed = int(track.trackId) == preview_id and not is_selected
    rl.draw_circle_v(rl.Vector2(x, y), dot_radius + 3.0, rl.Color(0, 0, 0, 180))
    if is_selected:
      rl.draw_circle_lines_v(rl.Vector2(x, y), dot_radius + 4.0, CYAN)
    elif is_previewed:
      rl.draw_circle_lines_v(rl.Vector2(x, y), dot_radius + 4.0, ORANGE)
    rl.draw_circle_v(rl.Vector2(x, y), dot_radius, color)
    rl.draw_circle_v(rl.Vector2(x, y), max(1.5, dot_radius * 0.32), BACKGROUND)

    if show_labels or is_hovered:
      draw_track_popup(font, track, x, y, dot_radius, camera_rect, color)


def draw_fused_camera_mode(font, road_camera_view: CameraView, wide_camera_view: CameraView, device_camera,
                           rpy_calib: np.ndarray, wide_from_device_euler: np.ndarray, full_rect: rl.Rectangle,
                           tracks, v_ego: float, show_labels: bool, motion_states: dict[int, int],
                           use_dbc_colors: bool, selected_id: int | None) -> int | None:
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

  draw_camera_tracks(font, wide_calibration, wide_tracks, wide_content_rect, v_ego, show_labels, motion_states,
                     use_dbc_colors, wide_projection_height, wide_hovered_id, selected_id)
  draw_camera_tracks(font, road_calibration, road_tracks, road_content_rect, v_ego, show_labels, motion_states,
                     use_dbc_colors, road_projection_height, road_hovered_id, selected_id)
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


def draw_top_down(font, rect: rl.Rectangle, tracks, v_ego: float, show_labels: bool, model,
                  motion_states: dict[int, int], use_dbc_colors: bool, hovered_id: int | None,
                  selected_id: int | None, preview_id: int | None = None) -> None:
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

  if use_dbc_colors:
    legend = ((PURPLE, "moving"), (WHITE, "stationary"), (MUTED, "unknown / n/a"))
  else:
    legend = (
      (radar_track_color(-2.0, 10.0), "approaching"),
      (radar_track_color(0.0, 10.0), "speed matched"),
      (radar_track_color(2.0, 10.0), "receding"),
      (radar_track_color(-10.0, 10.0), "stationary"),
    )
  legend_x = rect.x + rect.width - 150
  legend_y = rect.y + 50
  for index, (color, label) in enumerate(legend):
    y = legend_y + index * 23
    rl.draw_circle(int(legend_x), int(y + 7), 5, color)
    draw_text(font, label, legend_x + 12, y, 15, TEXT)

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

  rl.draw_rectangle_rounded(rl.Rectangle(center_x - 13, car_y - 25, 26, 48), 0.3, 6, CYAN)

  for track in tracks:
    geometry = top_down_track_geometry(rect, track)
    if geometry is None:
      continue
    x, y, radius = geometry
    color = display_track_color(track, v_ego, motion_states, use_dbc_colors)
    is_hovered = int(track.trackId) == hovered_id
    is_selected = int(track.trackId) == selected_id
    is_previewed = int(track.trackId) == preview_id and not is_selected
    rl.draw_circle_v(rl.Vector2(x, y), radius, rl.Color(0, 0, 0, 180))
    if is_selected:
      rl.draw_circle_lines_v(rl.Vector2(x, y), radius + 3.0, CYAN)
    elif is_previewed:
      rl.draw_circle_lines_v(rl.Vector2(x, y), radius + 3.0, ORANGE)
    rl.draw_circle_v(rl.Vector2(x, y), 6.0, color)
    if show_labels:
      draw_text(font, f"{track.trackId}", x + 9, y - 9, 16, color)
    elif is_hovered:
      draw_track_popup(font, track, x, y, radius, rect, color)


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


def draw_track_table(font, rect: rl.Rectangle, tracks, v_ego: float, motion_states: dict[int, int], scroll: int,
                     selected_id: int | None, hovered_id: int | None,
                     track_signals: dict[int, DisplayTrackSignals], table_mode: str) -> None:
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
      ("ID", 0.02), ("DIST", 0.11), ("LAT", 0.23), ("REL V", 0.35), ("LAT V", 0.48), ("REL A", 0.61),
      ("ABS V", 0.74), ("AGE", 0.88),
    )
  elif table_mode == "object":
    columns = (
      ("ID", 0.02), ("WIDTH", 0.12), ("LENGTH", 0.25), ("ANGLE", 0.39), ("STATE", 0.53), ("COAST", 0.72),
      ("UPD", 0.86),
    )
  else:
    columns = (
      ("ID", 0.02), ("DIST", 0.12), ("LAT", 0.25), ("REL V", 0.38), ("IMPLEMENTATION", 0.53),
      ("DBC MOTION", 0.78),
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
    if table_mode == "kinematics":
      values = (
        (str(track.trackId), 0.02, TEXT),
        (f"{track.dRel:.1f}", 0.11, TEXT),
        (f"{track.yRel:+.1f}", 0.23, TEXT),
        (f"{track.vRel:+.1f}", 0.35, TEXT),
        (f"{detail.relLatSpeed:+.1f}" if detail else "n/a", 0.48, TEXT if detail else MUTED),
        (f"{track.aRel:+.1f}" if math.isfinite(track.aRel) else "n/a", 0.61, TEXT),
        (f"{detail.absSpeed:.1f}" if detail else "n/a", 0.74, TEXT if detail else MUTED),
        (str(detail.age) if detail else "n/a", 0.88, TEXT if detail else MUTED),
      )
    elif table_mode == "object":
      values = (
        (str(track.trackId), 0.02, TEXT),
        (f"{detail.width:.1f}" if detail else "n/a", 0.12, TEXT if detail else MUTED),
        (f"{detail.length:.1f}" if detail else "n/a", 0.25, TEXT if detail else MUTED),
        (f"{detail.orientationAngle:+.0f}" if detail else "n/a", 0.39, TEXT if detail else MUTED),
        (dbc_track_state(detail.state) if detail else "n/a", 0.53, TEXT if detail else MUTED),
        (str(detail.coastAge) if detail else "n/a", 0.72, TEXT if detail else MUTED),
        (str(detail.trackCounter) if detail else "n/a", 0.86, TEXT if detail else MUTED),
      )
    else:
      values = (
        (str(track.trackId), 0.02, TEXT),
        (f"{track.dRel:6.1f}", 0.12, TEXT),
        (f"{track.yRel:+6.1f}", 0.25, TEXT),
        (f"{track.vRel:+6.1f}", 0.38, TEXT),
        (implementation_class(track.vRel, v_ego), 0.53, radar_track_color(track.vRel, v_ego)),
        (dbc_motion_class(motion_state), 0.78, dbc_motion_color(motion_state)),
      )
    for value, offset, color in values:
      draw_text(font, value, rect.x + rect.width * offset, y, 15, color)


def draw_status_chip(font, label: str, x: float, y: float, color: rl.Color,
                     mouse_position: rl.Vector2) -> tuple[float, rl.Rectangle, bool]:
  size = measure_text_cached(font, label, 15)
  width = size.x + 16
  chip_rect = rl.Rectangle(x, y, width, 25)
  hovered = rl.check_collision_point_rec(mouse_position, chip_rect)
  alpha = 72 if hovered else 32
  rl.draw_rectangle_rounded(chip_rect, 0.3, 4, rl.Color(color.r, color.g, color.b, alpha))
  if hovered:
    rl.draw_rectangle_rounded_lines_ex(chip_rect, 0.3, 4, 1.0, color)
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


def draw_replay_control_bar(font, bounds: rl.Rectangle, replay: ManagedReplay, route: str, route_seconds: float,
                            v_ego: float, loading: bool, seek_input: str, seek_active: bool) -> str | None:
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

  draw_text(font, "SEEK", chip_x + 2, bounds.y + 14, 14, MUTED)
  field_x = chip_x + measure_standalone_text(font, "SEEK", 14).x + 10
  field = rl.Rectangle(field_x, bounds.y + 8, 66, 27)
  field_hovered = rl.check_collision_point_rec(mouse_position, field)
  rl.draw_rectangle_rounded(field, 0.18, 4, BACKGROUND)
  rl.draw_rectangle_rounded_lines_ex(field, 0.18, 4, 1.0, CYAN if seek_active else MUTED)
  draw_text(font, seek_input, field.x + 7, field.y + 5, 15, TEXT)
  if seek_active and int(time.monotonic() * 2) % 2 == 0:
    cursor_x = field.x + 7 + measure_standalone_text(font, seek_input, 15).x
    rl.draw_line_ex(rl.Vector2(cursor_x + 1, field.y + 4), rl.Vector2(cursor_x + 1, field.y + 22), 1.0, TEXT)
  if field_hovered and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
    clicked_action = "seek-focus"
  _, go_rect, go_hovered = draw_status_chip(font, "GO", field.x + field.width + 6, chip_y, CYAN, mouse_position)
  if go_hovered:
    hovered_tooltip = ("Enter: seek to absolute route seconds", go_rect)
    if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):  # noqa: TID251
      clicked_action = "seek"

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
    f"STATUS {status_text}   ROUTE {route_seconds:.1f}s   TIME {route_wall_time(route, route_seconds)}   ",
    f"SPEED {v_ego:.1f} m/s   PLAYBACK {replay.playback_speed:.1f}x   ",
    f"DOWNLOAD {format_download_progress(replay.progress_current, replay.progress_total)}",
  ))
  draw_text(font, info, bounds.x + 12, bounds.y + 43, 14, TEXT)
  rl.set_mouse_cursor(
    rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND
    if hovered_tooltip is not None or field_hovered or go_hovered
    else rl.MouseCursor.MOUSE_CURSOR_DEFAULT,
  )
  return clicked_action


def apply_replay_control(replay: ManagedReplay, action: str | None, seek_input: str,
                         seek_active: bool) -> tuple[str, bool]:
  if action == "seek-focus":
    return seek_input, True
  if action == "seek":
    if seek_input:
      replay.send(f"\n{seek_input}\n")
    return "", False
  if action is not None:
    replay.send(action)
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


def draw_fused_video_button(font, bounds: rl.Rectangle, data_source: str, use_dbc_colors: bool, show_labels: bool,
                            hide_unknown: bool, hide_stationary: bool) -> bool:
  source_title = "CAN" if data_source == "can" else "LIVE"
  preceding_labels = (
    f"R {source_title}",
    f"C {'DBC' if use_dbc_colors else 'IMPL'}",
    f"L {'ON' if show_labels else 'OFF'}",
    "U UNKNOWN",
    "S STATIONARY",
  )
  chip_x = bounds.x + 14
  for label in preceding_labels:
    chip_x += measure_text_cached(font, label, 15).x + 23

  mouse_position = rl.get_mouse_position()
  _, chip_rect, hovered = draw_status_chip(font, "V FUSE", chip_x, bounds.y + 49, GREEN, mouse_position)
  rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND if hovered else rl.MouseCursor.MOUSE_CURSOR_DEFAULT)
  if hovered:
    draw_status_tooltip(font, "Switch to road camera", chip_rect, bounds)
  return bool(
    hovered
    and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)  # noqa: TID251 - standalone raylib tool
  )


def draw_source_status(font, rect: rl.Rectangle, live_tracks, valid: bool, alive: bool, source_active: bool,
                       v_ego: float, show_labels: bool, data_source: str, use_dbc_colors: bool, camera_mode: str,
                       both_cameras_available: bool, hide_unknown: bool, hide_stationary: bool, visible_track_count: int,
                       table_mode: str, fps: int) -> str | None:
  rl.draw_rectangle_rec(rect, rl.Color(11, 16, 24, 225))
  tracks = live_tracks.points if valid else ()
  sources = sorted(live_tracks.trackSources, key=lambda source: (source.startAddress, source.endAddress, source.bus)) if valid else []
  status_color = GREEN if valid and alive else ORANGE
  source_title = "CAN" if data_source == "can" else "LIVE"

  if sources:
    source = sources[0]
    compact_name = source_name(source.startAddress, source.endAddress).removeprefix("RADAR_")
    source_text = f"{compact_name} / B{source.bus} / {source_details(source.startAddress, source.endAddress)}"
    if len(sources) > 1:
      source_text += f" / +{len(sources) - 1}"
  elif not source_active:
    source_text = "no route loaded"
  elif data_source == "liveTracks":
    source_text = "no source metadata"
  elif valid and live_tracks.radarTracksAvailable:
    source_text = "radar detected / parsing"
  else:
    source_text = "searching for supported radar"
  draw_text(font, source_text, rect.x + 14, rect.y + 14, 16, CYAN if sources else MUTED)

  filtered = hide_unknown or hide_stationary
  track_count = f"{visible_track_count}/{len(tracks)}" if filtered else str(len(tracks))
  summary = f"{track_count} tracks  {v_ego:.1f} m/s  {fps} fps"
  summary_size = measure_text_cached(font, summary, 16)
  draw_text(font, summary, rect.x + rect.width - summary_size.x - 14, rect.y + 14, 16, TEXT)

  chip_x = rect.x + 14
  chip_y = rect.y + 49
  mouse_position = rl.get_mouse_position()
  camera_label = "WIDE" if camera_mode == "wide 180" else "ROAD"
  table_label = {"comparison": "COMP", "kinematics": "KIN", "object": "OBJ"}[table_mode]
  chip_specs = [
    (f"R {source_title}", status_color, "source", "Switch CAN / liveTracks source"),
    (f"C {'DBC' if use_dbc_colors else 'IMPL'}", PURPLE if use_dbc_colors else CYAN, "colors",
     "Switch DBC / implementation colors"),
    (f"L {'ON' if show_labels else 'OFF'}", GREEN if show_labels else MUTED, "labels", "Show / hide all labels"),
    ("U UNKNOWN", MUTED if hide_unknown else CYAN, "unknown",
     "Show unknown tracks" if hide_unknown else "Hide unknown tracks"),
    ("S STATIONARY", MUTED if hide_stationary else CYAN, "stationary",
     "Show stationary tracks" if hide_stationary else "Hide stationary tracks"),
  ]
  if both_cameras_available:
    chip_specs.append((f"V {camera_label}", CYAN, "camera", "Cycle road / wide / fused camera"))
  chip_specs.append((f"T {table_label}", MUTED, "table", "Cycle comparison / kinematics / object table"))
  chip_specs.append(("O OPEN", GREEN, "route", "Open a route, or paste one with Cmd/Ctrl+V"))
  clicked_action = None
  hovered_tooltip = None
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
  hide_unknown = True
  hide_stationary = True
  use_can_source = True
  use_dbc_colors = True
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
  route_message_start_mono: int | None = None
  current_route_seconds = route_start_seconds(route_input)
  if start_route:
    replay_process, route_error = replace_route_replay(replay_process, start_route)
    route_dialog_open = bool(route_error)
    route_loading = replay_process is not None and not route_error
    route_loading_started = time.monotonic()
  composite_mode = composite_mode and not route_dialog_open
  startup_focus_deadline = time.monotonic() + 2.0
  next_startup_focus_request = 0.0

  while not rl.window_should_close() and (replay_process is None or replay_process.poll() is None):
    now = time.monotonic()
    if replay_process is not None:
      replay_process.drain_output()
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
      current_route_seconds = route_start_seconds(route_input)
      composite_mode = composite_mode and not route_dialog_open
      table_scroll = 0
      selected_track_id = None
    elif modifier_down:
      pass
    elif replay_process is not None and rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
      replay_seek_active = True
    elif replay_process is not None and (replay_command := replay_keyboard_command()) is not None:
      replay_process.send(replay_command)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_O):
      route_dialog_open = True
      route_error = ""
      route_select_all = bool(route_input)
      route_cursor = len(route_input)
      composite_mode = False
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_L):
      show_labels = not show_labels
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_R):
      use_can_source = not use_can_source
      table_scroll = 0
      selected_track_id = None
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_C):
      use_dbc_colors = not use_dbc_colors
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_U):
      hide_unknown = not hide_unknown
      table_scroll = 0
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_S):
      hide_stationary = not hide_stationary
      table_scroll = 0
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_T):
      table_mode_index = (table_mode_index + 1) % len(TABLE_MODES)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_V):
      if composite_mode:
        composite_mode = False
        fused_streams_missing_since = None
        camera_view = road_camera_view
      elif both_camera_streams_available(camera_view.available_streams):
        if camera_view is road_camera_view:
          camera_view = wide_camera_view
        else:
          composite_mode = True
          fused_streams_missing_since = None
    if open_entered_route:
      replay_process, route_error = replace_route_replay(replay_process, route_input)
      route_dialog_open = bool(route_error)
      route_select_all = False
      route_loading = replay_process is not None and not route_error
      route_loading_started = time.monotonic()
      route_message_start_mono = None
      current_route_seconds = route_start_seconds(route_input)

    sm.update(0)
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
    if sm.updated["liveTracks"]:
      live_tracks = make_radar_snapshot(sm["liveTracks"])
      live_data_seen = sm.valid["liveTracks"]

    window_width = rl.get_screen_width()
    window_height = rl.get_screen_height()
    replay_bar_height = 70.0 if replay_process is not None else 0.0
    content_height = window_height - replay_bar_height
    left_width = float(round(window_width * 0.58))
    camera_height = float(round(content_height * 0.64))
    camera_rect = rl.Rectangle(0, 0, left_width, camera_height)
    table_rect = rl.Rectangle(0, camera_height, left_width, content_height - camera_height)
    radar_rect = rl.Rectangle(left_width, 0, window_width - left_width, content_height)
    replay_bar_rect = rl.Rectangle(0, content_height, window_width, replay_bar_height)
    status_rect = rl.Rectangle(0, 0, left_width, min(88, camera_height * 0.2))

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
    if use_can_source:
      selected_tracks = can_tracks
      tracks = decoded_tracks
      data_valid = can_data_seen
      data_alive = can_data_alive
      motion_states = decoded_motion_states
      track_signals = decoded_track_signals
      data_source = "can"
    else:
      selected_tracks = live_tracks
      data_valid = live_data_seen
      data_alive = sm.alive["liveTracks"]
      tracks = list(selected_tracks.points) if data_valid else []
      motion_states = match_decoded_track_values(tracks, decoded_tracks, decoded_motion_states)
      track_signals = match_decoded_track_values(tracks, decoded_tracks, decoded_track_signals)
      data_source = "liveTracks"

    tracks = filter_tracks(tracks, motion_states, hide_unknown, hide_stationary)
    capacity = table_capacity(table_rect)
    max_scroll = max(0, len(tracks) - capacity)
    if rl.is_key_pressed(rl.KeyboardKey.KEY_DOWN):
      table_scroll += 1
    if rl.is_key_pressed(rl.KeyboardKey.KEY_UP):
      table_scroll -= 1
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
        fused_bounds, tracks, v_ego, show_labels, motion_states, use_dbc_colors, selected_track_id,
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
      if draw_fused_video_button(
        font, fused_bounds, data_source, use_dbc_colors, show_labels, hide_unknown, hide_stationary,
      ):
        composite_mode = False
        fused_streams_missing_since = None
        camera_view = road_camera_view
      if route_loading:
        draw_route_loading(font, fused_bounds, route_input, time.monotonic() - route_loading_started)
      if replay_process is not None:
        replay_action = draw_replay_control_bar(
          font, replay_bar_rect, replay_process, route_input, current_route_seconds, v_ego, route_loading,
          replay_seek_input, replay_seek_active,
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

    draw_camera_tracks(font, calibration, tracks, camera_draw_rect, v_ego, show_labels, motion_states, use_dbc_colors,
                       camera_projection_height, camera_hovered_id, selected_track_id, table_hover_id)
    draw_top_down(font, radar_rect, tracks, v_ego, show_labels, model, motion_states, use_dbc_colors,
                  top_down_hovered_id, selected_track_id, table_hover_id)
    table_mode = TABLE_MODES[table_mode_index]
    draw_track_table(font, table_rect, tracks, v_ego, motion_states, table_scroll, selected_track_id, table_hover_id,
                     track_signals, table_mode)
    clicked_action = draw_source_status(
      font, status_rect, selected_tracks, data_valid, data_alive,
      replay_process is not None or can_data_seen or live_data_seen, v_ego, show_labels, data_source, use_dbc_colors,
      "wide 180" if camera_view.stream_type == VisionStreamType.VISION_STREAM_WIDE_ROAD else "road",
      both_camera_streams_available(camera_view.available_streams), hide_unknown, hide_stationary,
      len(tracks), table_mode, rl.get_fps(),
    )
    if clicked_action == "source":
      use_can_source = not use_can_source
      table_scroll = 0
      selected_track_id = None
    elif clicked_action == "colors":
      use_dbc_colors = not use_dbc_colors
    elif clicked_action == "labels":
      show_labels = not show_labels
    elif clicked_action == "unknown":
      hide_unknown = not hide_unknown
      table_scroll = 0
    elif clicked_action == "stationary":
      hide_stationary = not hide_stationary
      table_scroll = 0
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
        current_route_seconds = route_start_seconds(route_input)
    if route_loading and not route_dialog_open:
      draw_route_loading(
        font, rl.Rectangle(0, 0, window_width, window_height), route_input, time.monotonic() - route_loading_started,
      )
    if replay_process is not None and not route_dialog_open:
      replay_action = draw_replay_control_bar(
        font, replay_bar_rect, replay_process, route_input, current_route_seconds, v_ego, route_loading,
        replay_seek_input, replay_seek_active,
      )
      replay_seek_input, replay_seek_active = apply_replay_control(
        replay_process, replay_action, replay_seek_input, replay_seek_active,
      )
    if table_hover_id is not None and not route_dialog_open:
      rl.set_mouse_cursor(rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND)
    rl.end_drawing()

  stop_route_replay(replay_process)
  decoder_process.terminate()
  decoder_process.join(timeout=1.0)
  decoder_output.close()
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
