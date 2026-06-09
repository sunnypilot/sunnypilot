#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass

import cv2
import numpy as np
import pyray as rl

import cereal.messaging as messaging
from opendbc.car.tests.routes import routes
from openpilot.common.basedir import BASEDIR
from openpilot.common.transformations.camera import DEVICE_CAMERAS
from openpilot.tools.replay.custom_routes import CUSTOM_ROUTES
from openpilot.tools.replay.lib.ui_helpers import (
  UP,
  BLACK,
  GREEN,
  YELLOW,
  Calibration,
  get_blank_lid_overlay,
  init_plots,
  plot_lead,
  plot_model,
  to_topdown_pt,
)
from openpilot.tools.replay.radar_helpers import (
  RADAR_SPECS,
  build_seen_address_map,
  decode_radar_track,
  get_radar_can_parser,
  get_radar_spec,
  get_track_storage_key,
  get_track_ts_nanos,
  is_exclusive_full_range_match,
  is_radar_track_valid,
)
from openpilot.selfdrive.controls.radard import RADAR_TO_CAMERA
from msgq.visionipc import VisionIpcClient, VisionStreamType

os.environ['BASEDIR'] = BASEDIR

ANGLE_SCALE = 5.0
RADAR_TRACK_TIMEOUT_FRAMES = 10
RADAR_FORMAT_SWITCH_MISS_FRAMES = 30
RADAR_TRACK_RADIUS = 4
CAMERA_RADAR_Y_OFFSET = 25
RADAR_HEATMAP_DECAY = 0.975
RADAR_HEATMAP_ALPHA = 0.65
CAMERA_RADAR_HEATMAP_ALPHA = 0.45
REPLAY_PATH = os.path.join(os.path.dirname(__file__), "replay")
REPLAY_SOCKET_WAIT_TIMEOUT_SECONDS = 10.0
REPLAY_SPEEDS = (0.2, 0.5, 1.0, 2.0, 4.0, 8.0)
CAMERA_DRAW_WIDTH = 640
CAMERA_DRAW_HEIGHT = 480
TOP_DOWN_DRAW_WIDTH = 384
PLOT_DRAW_WIDTH = 480
PLOT_DRAW_HEIGHT = 480
RADAR_HEATMAP_MODES = ("OFF", "TOP", "CAMERA", "BOTH")
CYAN = (90, 235, 255)
AMBER = (255, 210, 90)
SOFT_WHITE = (235, 235, 235)
SLATE = (140, 180, 210)


@dataclass
class RadarTrackPoint:
  trackId: int
  measured: bool = True
  dRel: float = 0.0
  yRel: float = 0.0
  vRel: float = 0.0
  aRel: float = 0.0
  yvRel: float = float("nan")


def draw_radar_points(tracks, lid_overlay):
  for track in tracks:
    px, py = to_topdown_pt(track.dRel, -track.yRel)
    if px != -1:
      cv2.circle(lid_overlay, (py, px), RADAR_TRACK_RADIUS, 255, thickness=-1, lineType=cv2.LINE_AA)


def update_radar_heatmap(tracks, radar_heatmap):
  radar_heatmap *= RADAR_HEATMAP_DECAY
  for track in tracks:
    px, py = to_topdown_pt(track.dRel, -track.yRel)
    if px != -1:
      cv2.circle(radar_heatmap, (py, px), RADAR_TRACK_RADIUS + 2, 255.0, thickness=-1, lineType=cv2.LINE_AA)


def update_radar_camera_heatmap(tracks, radar_heatmap, calibration, shape):
  radar_heatmap *= RADAR_HEATMAP_DECAY
  if calibration is None:
    return

  height, width = shape[:2]
  for track in tracks:
    if track.dRel <= 0.0:
      continue

    pt = calibration.car_space_to_bb(
      np.asarray([track.dRel - RADAR_TO_CAMERA]),
      np.asarray([-track.yRel]),
      np.asarray([1.0]),
    )
    x, y = np.round(pt[0]).astype(int)
    y += CAMERA_RADAR_Y_OFFSET
    if 0 <= x < width and 0 <= y < height:
      cv2.circle(radar_heatmap, (x, y), RADAR_TRACK_RADIUS + 3, 255.0, thickness=-1, lineType=cv2.LINE_AA)


def overlay_heatmap(img, radar_heatmap, alpha_scale):
  radar_heat_uint8 = np.ascontiguousarray(np.clip(radar_heatmap, 0, 255).astype(np.uint8))
  radar_heat_mask = radar_heat_uint8 > 0
  if not np.any(radar_heat_mask):
    return

  heat_rgb = cv2.cvtColor(cv2.applyColorMap(radar_heat_uint8, cv2.COLORMAP_TURBO), cv2.COLOR_BGR2RGB).astype(np.float32)
  img_rgb = img.astype(np.float32)
  alpha = ((radar_heat_uint8.astype(np.float32) / 255.0) * alpha_scale)[..., None]
  img[:] = np.where(
    radar_heat_mask[..., None],
    np.clip(img_rgb * (1.0 - alpha) + heat_rgb * alpha, 0, 255).astype(np.uint8),
    img,
  )


def draw_radar_points_camera(tracks, img, calibration):
  if calibration is None:
    return

  for track in tracks:
    if track.dRel <= 0.0:
      continue

    # Match the road-space projection convention used by other UI overlays.
    pt = calibration.car_space_to_bb(
      np.asarray([track.dRel - RADAR_TO_CAMERA]),
      np.asarray([-track.yRel]),
      np.asarray([1.0]),
    )
    x, y = np.round(pt[0]).astype(int)
    y += CAMERA_RADAR_Y_OFFSET
    if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
      cv2.circle(img, (x, y), RADAR_TRACK_RADIUS, (255, 255, 255), thickness=-1, lineType=cv2.LINE_AA)


def draw_loading_overlay(font, lines, camera_texture, top_down_texture, hor_mode, panel_x, panel_y):
  rl.draw_texture_pro(
    camera_texture,
    rl.Rectangle(0, 0, camera_texture.width, camera_texture.height),
    rl.Rectangle(0, 0, CAMERA_DRAW_WIDTH, CAMERA_DRAW_HEIGHT),
    rl.Vector2(0, 0),
    0.0,
    rl.WHITE,
  )
  rl.draw_texture(top_down_texture, CAMERA_DRAW_WIDTH, 0, rl.WHITE)  # noqa: TID251

  if hor_mode:
    panel_width = 620
    panel_height = 300
  else:
    panel_width = 700
    panel_height = 320

  rl.draw_rectangle(panel_x - 20, panel_y - 30, panel_width, panel_height, rl.Color(0, 0, 0, 140))
  rl.draw_rectangle_lines(panel_x - 20, panel_y - 30, panel_width, panel_height, rl.Color(255, 255, 255, 90))

  for i, line in enumerate(lines):
    if line:
      rl.draw_text_ex(font, line, rl.Vector2(panel_x, panel_y + i * 40), 28 if i == 0 else 20, 0, rl.WHITE)


def start_replay(route: str, prefix: str, playback: str, data_dir: str | None, start_seconds: int) -> subprocess.Popen:
  cmd = [
    REPLAY_PATH,
    "--playback", playback,
    "--prefix", prefix,
  ]
  if start_seconds > 0:
    cmd.extend(["--start", str(start_seconds)])
  if data_dir:
    cmd.extend(["--data_dir", data_dir])
  cmd.append(route)

  env = os.environ.copy()
  env["OPENPILOT_PREFIX"] = prefix
  return subprocess.Popen(
    cmd,
    cwd=os.path.dirname(REPLAY_PATH),
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    preexec_fn=os.setsid if os.name != "nt" else None,
  )


def stop_replay(proc: subprocess.Popen | None) -> None:
  if proc is not None and proc.poll() is None:
    if os.name != "nt":
      try:
        os.killpg(proc.pid, signal.SIGTERM)
      except ProcessLookupError:
        pass
    else:
      proc.terminate()

    try:
      proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
      if os.name != "nt":
        try:
          os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
          pass
      else:
        proc.kill()
      proc.wait(timeout=5)

  # `replay` can leave helper processes like `replayd` behind, so do one
  # targeted cleanup pass on shutdown as well.
  for pattern in ("/tools/replay/replay", "replayd"):
    try:
      subprocess.run(
        ["pkill", "-f", pattern],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
      )
    except FileNotFoundError:
      pass


def wait_for_can_socket(prefix: str, timeout: float) -> None:
  socket_path = os.path.join("/tmp", f"msgq_{prefix}", "can")
  started = time.monotonic()
  while not os.path.exists(socket_path):
    if time.monotonic() - started > timeout:
      raise TimeoutError(f"Timed out waiting for CAN socket at {socket_path}")
    time.sleep(0.1)


def get_hkg_routes() -> list[tuple[str, str]]:
  hkg_prefixes = ("HYUNDAI_", "KIA_", "GENESIS_")
  return [
    (route.route, getattr(route.car_model, "name", str(route.car_model)))
    for route in routes
    if route.car_model is not None and getattr(route.car_model, "name", str(route.car_model)).startswith(hkg_prefixes)
  ]


def get_custom_routes() -> list[tuple[str, str]]:
  return [(route.route, route.car_model) for route in CUSTOM_ROUTES]


def make_submaster(addr):
  return messaging.SubMaster(
    [
      'carState',
      'longitudinalPlan',
      'carControl',
      'radarState',
      'liveCalibration',
      'controlsState',
      'selfdriveState',
      'liveTracks',
      'modelV2',
      'liveParameters',
      'roadCameraState',
    ],
    addr=addr,
  )


def reset_radar_state():
  return (
    0,
    None,
    0,
    {radar_spec.name: 0 for radar_spec in RADAR_SPECS},
    build_seen_address_map(),
    {},
    0,
    {},
    {},
    {},
  )


def ui_thread(addr, route_entries=None, playback="1.0", data_dir=None, prefix="ui-replay", start_route_idx=0):
  cv2.setNumThreads(1)

  # Get monitor info before creating window
  rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT)
  rl.init_window(1, 1, "")
  max_height = rl.get_monitor_height(0)
  rl.close_window()

  hor_mode = os.getenv("HORIZONTAL") is not None
  hor_mode = True if max_height < 960 + 300 else hor_mode

  if hor_mode:
    size = (CAMERA_DRAW_WIDTH + TOP_DOWN_DRAW_WIDTH + PLOT_DRAW_WIDTH, 960)
    write_x = 5
    write_y = 480
  else:
    size = (CAMERA_DRAW_WIDTH + TOP_DOWN_DRAW_WIDTH, 960 + 300)
    write_x = CAMERA_DRAW_WIDTH + 5
    write_y = 970

  rl.set_trace_log_level(rl.TraceLogLevel.LOG_ERROR)
  rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT)
  rl.init_window(size[0], size[1], "openpilot debug UI")
  rl.set_target_fps(60)

  # Load font
  font_path = os.path.join(BASEDIR, "selfdrive/assets/fonts/JetBrainsMono-Medium.ttf")
  font = rl.load_font_ex(font_path, 32, None, 0)

  # Create textures for camera and top-down view
  camera_image = rl.gen_image_color(640, 480, rl.BLACK)
  camera_texture = rl.load_texture_from_image(camera_image)
  rl.unload_image(camera_image)

  # lid_overlay array is (lidar_x, lidar_y) = (384, 960)
  # pygame treats first axis as width, so texture is 384 wide x 960 tall
  # For raylib, we need to transpose to get (height, width) = (960, 384) for the RGBA array
  top_down_image = rl.gen_image_color(UP.lidar_x, UP.lidar_y, rl.BLACK)
  top_down_texture = rl.load_texture_from_image(top_down_image)
  rl.unload_image(top_down_image)

  current_route_idx = start_route_idx
  current_route_name = None
  current_route_model = None
  replay_proc = None
  current_start_seconds = 0
  paused = False
  state_checks_enabled = False
  radar_heatmap_mode_idx = 0
  current_playback = min(REPLAY_SPEEDS, key=lambda speed: abs(speed - float(playback)))
  last_replay_started_at = time.monotonic()
  playback_ready = False
  loading_status = "Initializing UI"

  def current_offset_seconds() -> int:
    if paused or not playback_ready or replay_proc is None or replay_proc.poll() is not None:
      return current_start_seconds
    return max(0, int(current_start_seconds + (time.monotonic() - last_replay_started_at) * current_playback))

  def connect_streams():
    nonlocal replay_proc, current_route_name, current_route_model, current_route_idx, current_start_seconds, loading_status, paused, last_replay_started_at, current_playback, playback_ready

    if route_entries:
      current_route_name, current_route_model = route_entries[current_route_idx]
      loading_status = f"Starting replay for route {current_route_idx + 1}/{len(route_entries)} at {current_start_seconds}s ({current_playback:.1f}x)"
      stop_replay(replay_proc)
      os.environ["OPENPILOT_PREFIX"] = prefix
      messaging.reset_context()
      replay_proc = start_replay(current_route_name, prefix, f"{current_playback:.1f}", data_dir, current_start_seconds)
      paused = False
      playback_ready = False
      loading_status = "Waiting for CAN socket"
      wait_for_can_socket(prefix, REPLAY_SOCKET_WAIT_TIMEOUT_SECONDS)

    loading_status = "Connecting to messaging streams"
    sm_local = make_submaster(addr)
    logcan_local = messaging.sub_sock("can", addr=addr, conflate=False, timeout=100)
    loading_status = "Waiting for road camera frames"
    return sm_local, logcan_local

  sm, logcan = connect_streams()

  img = np.zeros((480, 640, 3), dtype='uint8')
  imgff = None
  num_px = 0
  calibration = None
  (can_range_msg_count,
   active_radar_format_name,
   active_radar_format_miss_count,
   radar_format_total_counts,
   radar_format_seen_addresses,
   radar_track_ids,
   next_radar_track_id,
   radar_tracks,
   radar_track_last_seen,
   radar_parsers) = reset_radar_state()

  lid_overlay_blank = get_blank_lid_overlay(UP)
  radar_heatmap = np.zeros_like(lid_overlay_blank, dtype=np.float32)
  camera_radar_heatmap = np.zeros(img.shape[:2], dtype=np.float32)

  # plots
  name_to_arr_idx = {
    "gas": 0,
    "computer_gas": 1,
    "user_brake": 2,
    "computer_brake": 3,
    "v_ego": 4,
    "v_pid": 5,
    "angle_steers_des": 6,
    "angle_steers": 7,
    "angle_steers_k": 8,
    "steer_torque": 9,
    "v_override": 10,
    "v_cruise": 11,
    "a_ego": 12,
    "a_target": 13,
  }

  plot_arr = np.zeros((100, len(name_to_arr_idx.values())))

  plot_xlims = [(0, plot_arr.shape[0]), (0, plot_arr.shape[0]), (0, plot_arr.shape[0]), (0, plot_arr.shape[0])]
  plot_ylims = [(-0.1, 1.1), (-ANGLE_SCALE, ANGLE_SCALE), (0.0, 75.0), (-3.0, 2.0)]
  plot_names = [
    ["gas", "computer_gas", "user_brake", "computer_brake"],
    ["angle_steers", "angle_steers_des", "angle_steers_k", "steer_torque"],
    ["v_ego", "v_override", "v_pid", "v_cruise"],
    ["a_ego", "a_target"],
  ]
  plot_colors = [["b", "b", "g", "r", "y"], ["b", "g", "y", "r"], ["b", "g", "r", "y"], ["b", "r"]]
  plot_styles = [["-", "-", "-", "-", "-"], ["-", "-", "-", "-"], ["-", "-", "-", "-"], ["-", "-"]]

  draw_plots = init_plots(plot_arr, name_to_arr_idx, plot_xlims, plot_ylims, plot_names, plot_colors, plot_styles)

  # Palette for converting lid_overlay grayscale indices to RGBA colors
  palette = np.zeros((256, 4), dtype=np.uint8)
  palette[:, 3] = 255  # alpha
  palette[1] = [255, 0, 0, 255]  # RED
  palette[2] = [0, 255, 0, 255]  # GREEN
  palette[3] = [0, 0, 255, 255]  # BLUE
  palette[4] = [255, 255, 0, 255]  # YELLOW
  palette[110] = [110, 110, 110, 255]  # car_color (gray)
  palette[255] = [255, 255, 255, 255]  # WHITE

  vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)
  while not rl.window_should_close():
    # ***** frame *****
    if not vipc_client.is_connected():
      vipc_client.connect(False)

    rl.begin_drawing()
    rl.clear_background(rl.Color(64, 64, 64, 255))

    if rl.is_key_released(rl.KeyboardKey.KEY_Q):
      rl.end_drawing()
      stop_replay(replay_proc)
      replay_proc = None
      break

    shift_down = rl.is_key_down(rl.KeyboardKey.KEY_LEFT_SHIFT) or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)

    if route_entries and rl.is_key_released(rl.KeyboardKey.KEY_SPACE):
      if paused:
        sm, logcan = connect_streams()
        vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)
      else:
        current_start_seconds = current_offset_seconds()
        paused = True
        loading_status = "Paused"
        stop_replay(replay_proc)
        replay_proc = None

    if route_entries and rl.is_key_released(rl.KeyboardKey.KEY_RIGHT):
      current_route_idx = (current_route_idx + 1) % len(route_entries)
      current_start_seconds = 0
      paused = False
      (can_range_msg_count,
       active_radar_format_name,
       active_radar_format_miss_count,
       radar_format_total_counts,
       radar_format_seen_addresses,
       radar_track_ids,
       next_radar_track_id,
       radar_tracks,
       radar_track_last_seen,
       radar_parsers) = reset_radar_state()
      radar_heatmap.fill(0)
      camera_radar_heatmap.fill(0)
      sm, logcan = connect_streams()
      vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if route_entries and rl.is_key_released(rl.KeyboardKey.KEY_LEFT):
      current_route_idx = (current_route_idx - 1) % len(route_entries)
      current_start_seconds = 0
      paused = False
      (can_range_msg_count,
       active_radar_format_name,
       active_radar_format_miss_count,
       radar_format_total_counts,
       radar_format_seen_addresses,
       radar_track_ids,
       next_radar_track_id,
       radar_tracks,
       radar_track_last_seen,
       radar_parsers) = reset_radar_state()
      radar_heatmap.fill(0)
      camera_radar_heatmap.fill(0)
      sm, logcan = connect_streams()
      vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if route_entries and rl.is_key_released(rl.KeyboardKey.KEY_M):
      current_start_seconds = max(0, current_offset_seconds() + (-60 if shift_down else 60))
      paused = False
      (can_range_msg_count,
       active_radar_format_name,
       active_radar_format_miss_count,
       radar_format_total_counts,
       radar_format_seen_addresses,
       radar_track_ids,
       next_radar_track_id,
       radar_tracks,
       radar_track_last_seen,
       radar_parsers) = reset_radar_state()
      radar_heatmap.fill(0)
      camera_radar_heatmap.fill(0)
      sm, logcan = connect_streams()
      vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if route_entries and rl.is_key_released(rl.KeyboardKey.KEY_S):
      current_start_seconds = max(0, current_offset_seconds() + (-10 if shift_down else 10))
      paused = False
      (can_range_msg_count,
       active_radar_format_name,
       active_radar_format_miss_count,
       radar_format_total_counts,
       radar_format_seen_addresses,
       radar_track_ids,
       next_radar_track_id,
       radar_tracks,
       radar_track_last_seen,
       radar_parsers) = reset_radar_state()
      sm, logcan = connect_streams()
      vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if route_entries and (rl.is_key_released(rl.KeyboardKey.KEY_EQUAL) or rl.is_key_released(rl.KeyboardKey.KEY_KP_ADD)):
      for speed in REPLAY_SPEEDS:
        if speed > current_playback:
          current_playback = speed
          break
      if not paused:
        current_start_seconds = current_offset_seconds()
        (can_range_msg_count,
         active_radar_format_name,
         active_radar_format_miss_count,
         radar_format_total_counts,
         radar_format_seen_addresses,
         radar_track_ids,
         next_radar_track_id,
         radar_tracks,
         radar_track_last_seen,
         radar_parsers) = reset_radar_state()
        radar_heatmap.fill(0)
        camera_radar_heatmap.fill(0)
        sm, logcan = connect_streams()
        vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if route_entries and (rl.is_key_released(rl.KeyboardKey.KEY_MINUS) or rl.is_key_released(rl.KeyboardKey.KEY_KP_SUBTRACT)):
      for speed in reversed(REPLAY_SPEEDS):
        if speed < current_playback:
          current_playback = speed
          break
      if not paused:
        current_start_seconds = current_offset_seconds()
        (can_range_msg_count,
         active_radar_format_name,
         active_radar_format_miss_count,
         radar_format_total_counts,
         radar_format_seen_addresses,
         radar_track_ids,
         next_radar_track_id,
         radar_tracks,
         radar_track_last_seen,
         radar_parsers) = reset_radar_state()
        radar_heatmap.fill(0)
        camera_radar_heatmap.fill(0)
        sm, logcan = connect_streams()
        vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)

    if rl.is_key_released(rl.KeyboardKey.KEY_C):
      state_checks_enabled = not state_checks_enabled

    if rl.is_key_released(rl.KeyboardKey.KEY_H):
      radar_heatmap_mode_idx = (radar_heatmap_mode_idx + 1) % len(RADAR_HEATMAP_MODES)
      if RADAR_HEATMAP_MODES[radar_heatmap_mode_idx] == "OFF":
        radar_heatmap.fill(0)
        camera_radar_heatmap.fill(0)

    yuv_img_raw = vipc_client.recv()
    if yuv_img_raw is None or not yuv_img_raw.data.any():
      if replay_proc is not None and replay_proc.poll() is not None:
        loading_status = f"Replay exited with code {replay_proc.poll()}"

      loading_lines = [
        f"{loading_status}{' (paused)' if paused else ''}",
        f"Route {current_route_idx + 1}/{len(route_entries)}" if route_entries else "Connected to external replay",
        f"Platform: {current_route_model}" if current_route_model is not None else "",
        f"Route: {current_route_name}" if current_route_name is not None else "",
        f"Offset: {current_offset_seconds()}s" if route_entries else "",
        f"Playback: {current_playback:.1f}x" if route_entries else "",
        f"Radar state checks: {'ON' if state_checks_enabled else 'OFF'}",
        f"Radar heatmap: {RADAR_HEATMAP_MODES[radar_heatmap_mode_idx]}",
        "Keys: SPACE play/pause, RIGHT next, LEFT prev, M +/-60s, S +/-10s, +/- speed, C checks, H heatmap, Q quit" if route_entries else "Keys: C checks, H heatmap, Q quit",
      ]
      draw_loading_overlay(font, loading_lines, camera_texture, top_down_texture, hor_mode, 80, 160)
      rl.end_drawing()
      continue

    if not playback_ready:
      playback_ready = True
      last_replay_started_at = time.monotonic()
    loading_status = "Streaming"

    lid_overlay = lid_overlay_blank.copy()
    top_down = top_down_texture, lid_overlay

    sm.update(0)

    camera = DEVICE_CAMERAS[("tici", str(sm['roadCameraState'].sensor))]

    # Use received buffer dimensions (full HEVC can have stride != buffer_len/rows due to VENUS padding)
    h, w, stride = yuv_img_raw.height, yuv_img_raw.width, yuv_img_raw.stride
    nv12_size = h * 3 // 2 * stride
    imgff = np.frombuffer(yuv_img_raw.data, dtype=np.uint8, count=nv12_size).reshape((h * 3 // 2, stride))
    num_px = w * h
    rgb = cv2.cvtColor(imgff[: h * 3 // 2, : w], cv2.COLOR_YUV2RGB_NV12)

    qcam = "QCAM" in os.environ
    bb_scale = 0.825 if qcam else 0.8
    calib_scale = camera.fcam.width / 640.0
    zoom_matrix = np.asarray([[bb_scale, 0.0, 0.0], [0.0, bb_scale, 0.0], [0.0, 0.0, 1.0]])
    cv2.warpAffine(rgb, zoom_matrix[:2], (img.shape[1], img.shape[0]), dst=img, flags=cv2.WARP_INVERSE_MAP)

    intrinsic_matrix = camera.fcam.intrinsics

    w = sm['controlsState'].lateralControlState.which()
    if w == 'lqrStateDEPRECATED':
      angle_steers_k = sm['controlsState'].lateralControlState.lqrStateDEPRECATED.steeringAngleDeg
    elif w == 'indiState':
      angle_steers_k = sm['controlsState'].lateralControlState.indiState.steeringAngleDeg
    else:
      angle_steers_k = np.inf

    plot_arr[:-1] = plot_arr[1:]
    plot_arr[-1, name_to_arr_idx['angle_steers']] = sm['carState'].steeringAngleDeg
    plot_arr[-1, name_to_arr_idx['angle_steers_des']] = sm['carControl'].actuators.steeringAngleDeg
    plot_arr[-1, name_to_arr_idx['angle_steers_k']] = angle_steers_k
    plot_arr[-1, name_to_arr_idx['gas']] = sm['carState'].gasDEPRECATED
    # TODO gas is deprecated
    plot_arr[-1, name_to_arr_idx['computer_gas']] = np.clip(sm['carControl'].actuators.accel / 4.0, 0.0, 1.0)
    plot_arr[-1, name_to_arr_idx['user_brake']] = sm['carState'].brake
    plot_arr[-1, name_to_arr_idx['steer_torque']] = sm['carControl'].actuators.torque * ANGLE_SCALE
    # TODO brake is deprecated
    plot_arr[-1, name_to_arr_idx['computer_brake']] = np.clip(-sm['carControl'].actuators.accel / 4.0, 0.0, 1.0)
    plot_arr[-1, name_to_arr_idx['v_ego']] = sm['carState'].vEgo
    plot_arr[-1, name_to_arr_idx['v_cruise']] = sm['carState'].cruiseState.speed
    plot_arr[-1, name_to_arr_idx['a_ego']] = sm['carState'].aEgo

    if len(sm['longitudinalPlan'].accels):
      plot_arr[-1, name_to_arr_idx['a_target']] = sm['longitudinalPlan'].accels[0]

    if sm.recv_frame['modelV2']:
      plot_model(sm['modelV2'], img, calibration, top_down)

    if sm.recv_frame['radarState']:
      plot_lead(sm['radarState'], top_down)

    if sm.updated['liveCalibration'] and num_px:
      rpyCalib = np.asarray(sm['liveCalibration'].rpyCalib)
      calibration = Calibration(num_px, rpyCalib, intrinsic_matrix, calib_scale)

    can_packets = messaging.drain_sock(logcan)
    if can_packets:
      can_strings = [
        (can_packet.logMonoTime, [(msg.address, msg.dat, msg.src) for msg in can_packet.can])
        for can_packet in can_packets
      ]
      detected_format_counts = {radar_spec.name: 0 for radar_spec in RADAR_SPECS}

      for can_packet in can_packets:
        for msg in can_packet.can:
          radar_spec = get_radar_spec(msg.address)
          if radar_spec is not None:
            can_range_msg_count += 1
            detected_format_counts[radar_spec.name] += 1
            radar_format_total_counts[radar_spec.name] += 1
            radar_format_seen_addresses[radar_spec.name].add(msg.address)
            if radar_spec.name not in radar_parsers:
              radar_parsers[radar_spec.name] = {}
            if msg.src not in radar_parsers[radar_spec.name]:
              radar_parsers[radar_spec.name][msg.src] = get_radar_can_parser(radar_spec, msg.src)

      matching_formats = [
        radar_spec.name
        for radar_spec in RADAR_SPECS
        if is_exclusive_full_range_match(radar_spec, radar_format_seen_addresses)
      ]
      if len(matching_formats) == 1:
        if active_radar_format_name == matching_formats[0]:
          active_radar_format_miss_count = 0
        elif active_radar_format_name is None:
          active_radar_format_name = matching_formats[0]
          active_radar_format_miss_count = 0
        else:
          active_radar_format_miss_count += 1
          if active_radar_format_miss_count >= RADAR_FORMAT_SWITCH_MISS_FRAMES:
            active_radar_format_name = matching_formats[0]
            active_radar_format_miss_count = 0
      elif len(matching_formats) == 0 and active_radar_format_name is not None:
        active_radar_format_miss_count += 1
        if active_radar_format_miss_count >= RADAR_FORMAT_SWITCH_MISS_FRAMES:
          active_radar_format_name = None
          active_radar_format_miss_count = 0

      active_radar_spec = next((spec for spec in RADAR_SPECS if spec.name == active_radar_format_name), None)
      if active_radar_spec is not None:
        for bus, parser in radar_parsers.get(active_radar_spec.name, {}).items():
          updated_addrs = parser.update(can_strings)
          relevant_updated_addrs = {
            track_addr for track_addr in updated_addrs
            if active_radar_spec.start_addr <= track_addr <= active_radar_spec.end_addr
          }
          if not relevant_updated_addrs:
            continue

          for track_addr in relevant_updated_addrs:
            msg_name = f"RADAR_TRACK_{track_addr:x}"
            track_msg = parser.vl[msg_name]
            for track_prefix in active_radar_spec.track_prefixes:
              track_key = get_track_storage_key(active_radar_spec, bus, track_addr, track_prefix)
              ts_nanos = get_track_ts_nanos(parser, msg_name, active_radar_spec, track_prefix)
              if ts_nanos == 0:
                continue

              if state_checks_enabled and not is_radar_track_valid(active_radar_spec, track_msg, track_prefix):
                radar_tracks.pop(track_key, None)
                radar_track_last_seen.pop(track_key, None)
                continue

              d_rel, y_rel, v_rel, a_rel = decode_radar_track(active_radar_spec, track_msg, track_prefix)

              if track_key not in radar_track_ids:
                radar_track_ids[track_key] = next_radar_track_id
                next_radar_track_id += 1

              radar_tracks[track_key] = RadarTrackPoint(
                trackId=radar_track_ids[track_key],
                dRel=d_rel,
                yRel=y_rel,
                vRel=v_rel,
                aRel=a_rel,
              )
              radar_track_last_seen[track_key] = sm.frame

      stale_tracks = [
        track_key for track_key, last_seen in radar_track_last_seen.items()
        if (sm.frame - last_seen) > RADAR_TRACK_TIMEOUT_FRAMES
      ]
      for track_key in stale_tracks:
        radar_track_last_seen.pop(track_key, None)
        radar_tracks.pop(track_key, None)

    active_radar_tracks = [
      track for track_key, track in radar_tracks.items()
      if active_radar_format_name is not None and track_key[0] == active_radar_format_name
    ]
    active_radar_buses = sorted({
      track_key[1] for track_key in radar_tracks
      if active_radar_format_name is not None and track_key[0] == active_radar_format_name
    })
    if len(active_radar_tracks) == 0:
      active_radar_tracks = sm['liveTracks'].points
      active_radar_buses = []

    radar_heatmap_mode = RADAR_HEATMAP_MODES[radar_heatmap_mode_idx]
    if radar_heatmap_mode in ("TOP", "BOTH"):
      update_radar_heatmap(active_radar_tracks, radar_heatmap)
    if radar_heatmap_mode in ("CAMERA", "BOTH"):
      update_radar_camera_heatmap(active_radar_tracks, camera_radar_heatmap, calibration, img.shape)
      overlay_heatmap(img, camera_radar_heatmap, CAMERA_RADAR_HEATMAP_ALPHA)

    # draw decoded radar tracks when present, otherwise fall back to liveTracks
    draw_radar_points(active_radar_tracks, top_down[1])
    draw_radar_points_camera(active_radar_tracks, img, calibration)

    # *** blits ***
    # Update camera texture from numpy array
    img_rgba = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    rl.update_texture(camera_texture, rl.ffi.cast("void *", img_rgba.ctypes.data))
    rl.draw_texture_pro(
      camera_texture,
      rl.Rectangle(0, 0, camera_texture.width, camera_texture.height),
      rl.Rectangle(0, 0, CAMERA_DRAW_WIDTH, CAMERA_DRAW_HEIGHT),
      rl.Vector2(0, 0),
      0.0,
      rl.WHITE,
    )

    # display alerts
    rl.draw_text_ex(font, sm['selfdriveState'].alertText1, rl.Vector2(180, 150), 30, 0, rl.RED)
    rl.draw_text_ex(font, sm['selfdriveState'].alertText2, rl.Vector2(180, 190), 20, 0, rl.RED)

    # draw plots (texture is reused internally)
    plot_texture = draw_plots(plot_arr)
    if hor_mode:
      rl.draw_texture_pro(
        plot_texture,
        rl.Rectangle(0, 0, plot_texture.width, plot_texture.height),
        rl.Rectangle(CAMERA_DRAW_WIDTH + TOP_DOWN_DRAW_WIDTH, 0, PLOT_DRAW_WIDTH, PLOT_DRAW_HEIGHT),
        rl.Vector2(0, 0),
        0.0,
        rl.WHITE,
      )
    else:
      rl.draw_texture(plot_texture, 0, 300, rl.WHITE)  # noqa: TID251

    # Convert lid_overlay to RGBA and update top_down texture
    # lid_overlay is (384, 960), need to transpose to (960, 384) for row-major RGBA buffer
    lid_rgba = palette[lid_overlay.T]
    if radar_heatmap_mode in ("TOP", "BOTH"):
      overlay_heatmap(lid_rgba[..., :3], radar_heatmap.T, RADAR_HEATMAP_ALPHA)
    rl.update_texture(top_down_texture, rl.ffi.cast("void *", np.ascontiguousarray(lid_rgba).ctypes.data))
    rl.draw_texture(top_down_texture, CAMERA_DRAW_WIDTH, 0, rl.WHITE)  # noqa: TID251

    SPACING = 20
    lines = [
      ("ENABLED", GREEN if sm['selfdriveState'].enabled else BLACK),
      ("SPEED: " + str(round(sm['carState'].vEgo, 1)) + " m/s", CYAN),
      ("LONG CONTROL STATE: " + str(sm['controlsState'].longControlState), CYAN),
      ("LONG MPC SOURCE: " + str(sm['longitudinalPlan'].longitudinalPlanSource), CYAN),
      (f"RADAR FORMAT: {active_radar_format_name or 'NONE'}", AMBER),
      (f"RADAR CAN MSGS: {can_range_msg_count}", AMBER),
      (f"RADAR TRACKS: {len(active_radar_tracks)}"
       + (f" (BUS {','.join(str(bus) for bus in active_radar_buses)})" if active_radar_buses else ""),
       AMBER),
      (f"RADAR STATE CHECKS: {'ON' if state_checks_enabled else 'OFF'}", AMBER),
      (f"RADAR HEATMAP: {RADAR_HEATMAP_MODES[radar_heatmap_mode_idx]}", AMBER),
      (f"ROUTE: {current_route_name}" if current_route_name is not None else "", SLATE),
      (f"PLATFORM: {current_route_model}" if current_route_model is not None else "", SLATE),
      (f"OFFSET: {current_offset_seconds()}s" if route_entries else "", SOFT_WHITE),
      (f"PLAYBACK: {current_playback:.1f}x" if route_entries else "", SOFT_WHITE),
      (f"STATUS: {'PAUSED' if paused else 'PLAYING'}" if route_entries else "", SOFT_WHITE),
      ("ANGLE OFFSET (AVG): " + str(round(sm['liveParameters'].angleOffsetAverageDeg, 2)) + " deg", SOFT_WHITE),
      ("ANGLE OFFSET (INSTANT): " + str(round(sm['liveParameters'].angleOffsetDeg, 2)) + " deg", SOFT_WHITE),
      ("STIFFNESS: " + str(round(sm['liveParameters'].stiffnessFactor * 100.0, 2)) + " %", SOFT_WHITE),
      ("STEER RATIO: " + str(round(sm['liveParameters'].steerRatio, 2)), SOFT_WHITE),
    ]

    hud_height = len(lines) * SPACING + 18
    rl.draw_rectangle(write_x - 10, write_y - 12, 560, hud_height, rl.Color(8, 12, 18, 155))
    rl.draw_rectangle(write_x - 10, write_y - 12, 4, hud_height, rl.Color(90, 235, 255, 255))
    rl.draw_rectangle_lines(write_x - 10, write_y - 12, 560, hud_height, rl.Color(90, 235, 255, 80))

    for i, line in enumerate(lines):
      if line is not None:
        color = rl.Color(line[1][0], line[1][1], line[1][2], 255)
        rl.draw_text_ex(font, line[0], rl.Vector2(write_x, write_y + i * SPACING), 20, 0, color)

    rl.end_drawing()

  rl.unload_texture(camera_texture)
  rl.unload_texture(top_down_texture)
  rl.unload_font(font)
  rl.close_window()
  stop_replay(replay_proc)


def get_arg_parser():
  parser = argparse.ArgumentParser(description="Show replay data in a UI.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("ip_address", nargs="?", default="127.0.0.1", help="The ip address on which to receive zmq messages.")
  parser.add_argument("--route", default=None, help="Route to replay locally before opening the UI.")
  parser.add_argument("--routes", action="store_true", help="Cycle Hyundai/Kia/Genesis routes from opendbc/car/tests/routes.py.")
  parser.add_argument("--custom-routes", nargs="?", type=int, const=1, default=None,
                      help="Cycle routes from tools/replay/custom_routes.py, optionally starting from a 1-based route index.")
  parser.add_argument("--data-dir", default=None, help="Optional local route data directory to pass to replay.")
  parser.add_argument("--playback", default="1.0", help="Replay playback speed when using --route.")
  parser.add_argument("--prefix", default="ui-replay", help="OPENPILOT_PREFIX to use when launching replay from the UI.")
  parser.add_argument("--frame-address", default=None, help="The frame address (fully qualified ZMQ endpoint for frames) on which to receive zmq messages.")
  return parser


if __name__ == "__main__":
  args = get_arg_parser().parse_args(sys.argv[1:])

  selected_sources = int(args.route is not None) + int(args.routes) + int(args.custom_routes is not None)
  if selected_sources > 1:
    raise SystemExit("Use only one of --route, --routes, or --custom-routes.")

  route_entries = None
  start_route_idx = 0
  if args.route is not None:
    route_entries = [(args.route, "MANUAL_ROUTE")]
  elif args.routes:
    route_entries = get_hkg_routes()
  elif args.custom_routes is not None:
    route_entries = get_custom_routes()
    start_route_idx = max(0, min(len(route_entries) - 1, args.custom_routes - 1))

  if route_entries:
    os.environ["OPENPILOT_PREFIX"] = args.prefix
    messaging.reset_context()
  elif args.ip_address != "127.0.0.1":
    os.environ["ZMQ"] = "1"
    messaging.reset_context()

  ui_thread(args.ip_address, route_entries=route_entries, playback=args.playback, data_dir=args.data_dir, prefix=args.prefix, start_route_idx=start_route_idx)
