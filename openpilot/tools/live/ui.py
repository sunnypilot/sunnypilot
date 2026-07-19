#!/usr/bin/env python3
import argparse
from collections import deque
import os
from pathlib import Path
import queue
import secrets
import select
import shlex
import signal
import struct
import subprocess
import sys
import threading
import time
import zlib

ROOT = Path(__file__).resolve().parents[3]
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / "bin/python"
if Path(sys.prefix).resolve() != VENV.resolve() and VENV_PYTHON.is_file():
  os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from openpilot.cereal.services import SERVICE_LIST


BRIDGE = ROOT / "openpilot/cereal/messaging/bridge"

ROAD_ENCODE_SERVICE = "narrowRoadEncodeData"
LOCAL_UI_PUBLISHERS = {"bookmarkButton", "uiDebug"}
UNUSED_CAMERA_SERVICES = {"cabinEncodeData", "wideRoadEncodeData"}
V4L2_BUF_FLAG_KEYFRAME = 8
CONNECTION_TIMEOUT = 3.0
EXACT_DISCONNECT_MIN_TIMEOUT = 1.0
EXACT_DISCONNECT_FRAME_INTERVALS = 3.0
EXACT_CAPTURE_FPS = 15
SSH_OPTIONS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]

REMOTE_CAPTURE_SCRIPT = r"""
import array
import ctypes as C
import fcntl
import mmap
import os
import select
import signal
import socket
import struct
import sys
import time
import zlib

import numpy as np

CREATE_DUMB = 0xC02064B2
MAP_DUMB = 0xC01064B3
DESTROY_DUMB = 0xC00464B4
NONBLOCK = 0x0200
ALLOW_MODESET = 0x0400
CONNECTOR_OBJECT = 0xC0C0C0C0
CRTC_OBJECT = 0xCCCCCCCC
CLIENT_CAP_ATOMIC = 3


class Mode(C.Structure):
  _fields_ = [
    ("clock", C.c_uint32),
    ("hdisplay", C.c_uint16), ("hsync_start", C.c_uint16), ("hsync_end", C.c_uint16),
    ("htotal", C.c_uint16), ("hskew", C.c_uint16),
    ("vdisplay", C.c_uint16), ("vsync_start", C.c_uint16), ("vsync_end", C.c_uint16),
    ("vtotal", C.c_uint16), ("vscan", C.c_uint16),
    ("vrefresh", C.c_uint32), ("flags", C.c_uint32), ("type", C.c_uint32),
    ("name", C.c_char * 32),
  ]


class Resources(C.Structure):
  _fields_ = [
    ("count_fbs", C.c_int), ("fbs", C.POINTER(C.c_uint32)),
    ("count_crtcs", C.c_int), ("crtcs", C.POINTER(C.c_uint32)),
    ("count_connectors", C.c_int), ("connectors", C.POINTER(C.c_uint32)),
    ("count_encoders", C.c_int), ("encoders", C.POINTER(C.c_uint32)),
    ("min_width", C.c_uint32), ("max_width", C.c_uint32),
    ("min_height", C.c_uint32), ("max_height", C.c_uint32),
  ]


class Crtc(C.Structure):
  _fields_ = [
    ("crtc_id", C.c_uint32), ("buffer_id", C.c_uint32),
    ("x", C.c_uint32), ("y", C.c_uint32),
    ("width", C.c_uint32), ("height", C.c_uint32),
    ("mode_valid", C.c_int), ("mode", Mode), ("gamma_size", C.c_int),
  ]


class ObjectProperties(C.Structure):
  _fields_ = [
    ("count_props", C.c_uint32),
    ("props", C.POINTER(C.c_uint32)),
    ("prop_values", C.POINTER(C.c_uint64)),
  ]


class PropertyEnum(C.Structure):
  _fields_ = [("value", C.c_uint64), ("name", C.c_char * 32)]


class Property(C.Structure):
  _fields_ = [
    ("prop_id", C.c_uint32), ("flags", C.c_uint32), ("name", C.c_char * 32),
    ("count_values", C.c_int), ("values", C.POINTER(C.c_uint64)),
    ("count_enums", C.c_int), ("enums", C.POINTER(PropertyEnum)),
    ("count_blobs", C.c_int), ("blob_ids", C.POINTER(C.c_uint32)),
  ]


def receive_drm_master():
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  sock.connect("/tmp/drmfd.sock")
  _, ancillary, _, _ = sock.recvmsg(1, socket.CMSG_SPACE(array.array("i").itemsize))
  fds = array.array("i")
  for level, kind, data in ancillary:
    if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
      fds.frombytes(data[:len(data) - (len(data) % fds.itemsize)])
  if not fds:
    raise RuntimeError("DRM broker did not provide a file descriptor")
  return sock, fds[0]


lib = C.CDLL("libdrm.so.2", use_errno=True)
lib.drmModeGetResources.argtypes = [C.c_int]
lib.drmModeGetResources.restype = C.POINTER(Resources)
lib.drmModeFreeResources.argtypes = [C.POINTER(Resources)]
lib.drmModeGetCrtc.argtypes = [C.c_int, C.c_uint32]
lib.drmModeGetCrtc.restype = C.POINTER(Crtc)
lib.drmModeFreeCrtc.argtypes = [C.POINTER(Crtc)]
lib.drmModeObjectGetProperties.argtypes = [C.c_int, C.c_uint32, C.c_uint32]
lib.drmModeObjectGetProperties.restype = C.POINTER(ObjectProperties)
lib.drmModeFreeObjectProperties.argtypes = [C.POINTER(ObjectProperties)]
lib.drmModeGetProperty.argtypes = [C.c_int, C.c_uint32]
lib.drmModeGetProperty.restype = C.POINTER(Property)
lib.drmModeFreeProperty.argtypes = [C.POINTER(Property)]
lib.drmModeAddFB2.argtypes = [
  C.c_int, C.c_uint32, C.c_uint32, C.c_uint32,
  C.POINTER(C.c_uint32), C.POINTER(C.c_uint32), C.POINTER(C.c_uint32),
  C.POINTER(C.c_uint32), C.c_uint32,
]
lib.drmModeAddFB2.restype = C.c_int
lib.drmModeRmFB.argtypes = [C.c_int, C.c_uint32]
lib.drmModeAtomicAlloc.restype = C.c_void_p
lib.drmModeAtomicAddProperty.argtypes = [C.c_void_p, C.c_uint32, C.c_uint32, C.c_uint64]
lib.drmModeAtomicAddProperty.restype = C.c_int
lib.drmModeAtomicCommit.argtypes = [C.c_int, C.c_void_p, C.c_uint32, C.c_void_p]
lib.drmModeAtomicCommit.restype = C.c_int
lib.drmModeAtomicFree.argtypes = [C.c_void_p]
lib.drmSetClientCap.argtypes = [C.c_int, C.c_uint64, C.c_uint64]
lib.drmSetClientCap.restype = C.c_int


def properties(fd, object_id, object_type):
  result = {}
  object_props = lib.drmModeObjectGetProperties(fd, object_id, object_type)
  if not object_props:
    return result
  try:
    for i in range(object_props.contents.count_props):
      prop = lib.drmModeGetProperty(fd, object_props.contents.props[i])
      if prop:
        try:
          result[prop.contents.name.decode()] = prop.contents.prop_id
        finally:
          lib.drmModeFreeProperty(prop)
  finally:
    lib.drmModeFreeObjectProperties(object_props)
  return result


def atomic_commit(fd, values, nonblocking=False, allow_modeset=False):
  request = lib.drmModeAtomicAlloc()
  if not request:
    raise RuntimeError("failed to allocate DRM atomic request")
  try:
    for object_id, property_id, value in values:
      if lib.drmModeAtomicAddProperty(request, object_id, property_id, value) < 0:
        raise OSError(C.get_errno(), os.strerror(C.get_errno()))
    for attempt in range(5):
      flags = (NONBLOCK if nonblocking else 0) | (ALLOW_MODESET if allow_modeset else 0)
      if lib.drmModeAtomicCommit(fd, request, flags, None) == 0:
        return
      error = C.get_errno()
      if error != 16 or attempt == 4:
        raise OSError(error, os.strerror(error))
      time.sleep(0.005)
  finally:
    lib.drmModeAtomicFree(request)


def stop(*_):
  raise SystemExit


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGHUP, stop)

fps = max(1.0, float(sys.argv[1]))
session_token = sys.argv[2]
session_path = f"/tmp/sunnypilot-live-ui-{session_token}.pid"
capture_lock = -1
broker = None
drm_fd = -1
handles = []
framebuffers = []
mapped_buffers = []
buffer_pitches = []
attached = False

try:
  with open(session_path, "w") as session_file:
    session_file.write(str(os.getpid()))

  capture_lock = os.open("/tmp/sunnypilot-live-ui.lock", os.O_CREAT | os.O_RDWR, 0o600)
  try:
    fcntl.flock(capture_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except BlockingIOError as error:
    raise RuntimeError("another exact-screen session is already running") from error

  broker, drm_fd = receive_drm_master()
  if lib.drmSetClientCap(drm_fd, CLIENT_CAP_ATOMIC, 1):
    raise OSError(C.get_errno(), os.strerror(C.get_errno()))
  resources_ptr = lib.drmModeGetResources(drm_fd)
  if not resources_ptr:
    raise OSError(C.get_errno(), os.strerror(C.get_errno()))
  try:
    resources = resources_ptr.contents
    active_crtc = None
    for i in range(resources.count_crtcs):
      crtc = lib.drmModeGetCrtc(drm_fd, resources.crtcs[i])
      if crtc:
        if crtc.contents.mode_valid and crtc.contents.width and crtc.contents.height:
          active_crtc = (crtc.contents.crtc_id, crtc.contents.width, crtc.contents.height)
        lib.drmModeFreeCrtc(crtc)
        if active_crtc:
          break
    if not active_crtc:
      raise RuntimeError("no active DRM display found")

    writeback = None
    required = {"CRTC_ID", "FB_ID", "DST_X", "DST_Y", "DST_W", "DST_H"}
    for i in range(resources.count_connectors):
      connector_id = resources.connectors[i]
      connector_props = properties(drm_fd, connector_id, CONNECTOR_OBJECT)
      if required <= connector_props.keys():
        writeback = (connector_id, connector_props)
        break
    if not writeback:
      raise RuntimeError("no DRM writeback connector found")
  finally:
    lib.drmModeFreeResources(resources_ptr)

  crtc_id, width, height = active_crtc
  connector_id, connector_props = writeback
  crtc_props = properties(drm_fd, crtc_id, CRTC_OBJECT)

  pixel_format = struct.unpack("<I", b"AB24")[0]
  for _ in range(2):
    create = bytearray(struct.pack("<6IQ", height, width, 32, 0, 0, 0, 0))
    fcntl.ioctl(drm_fd, CREATE_DUMB, create, True)
    _, _, _, _, handle, pitch, size = struct.unpack("<6IQ", create)
    handles.append(handle)
    buffer_pitches.append(pitch)

    mapping = bytearray(struct.pack("<IIQ", handle, 0, 0))
    fcntl.ioctl(drm_fd, MAP_DUMB, mapping, True)
    _, _, offset = struct.unpack("<IIQ", mapping)
    mapped_buffers.append(mmap.mmap(
      drm_fd, size, flags=mmap.MAP_SHARED,
      prot=mmap.PROT_READ | mmap.PROT_WRITE, offset=offset,
    ))

    framebuffer_handles = (C.c_uint32 * 4)(handle, 0, 0, 0)
    framebuffer_pitches = (C.c_uint32 * 4)(pitch, 0, 0, 0)
    framebuffer_offsets = (C.c_uint32 * 4)(0, 0, 0, 0)
    framebuffer_id = C.c_uint32()
    if lib.drmModeAddFB2(
      drm_fd, width, height, pixel_format,
      framebuffer_handles, framebuffer_pitches, framebuffer_offsets,
      C.byref(framebuffer_id), 0,
    ):
      raise OSError(C.get_errno(), os.strerror(C.get_errno()))
    framebuffers.append(framebuffer_id.value)

  capture_values = [
    (connector_id, connector_props["CRTC_ID"], crtc_id),
    (connector_id, connector_props["DST_X"], 0),
    (connector_id, connector_props["DST_Y"], 0),
    (connector_id, connector_props["DST_W"], width),
    (connector_id, connector_props["DST_H"], height),
  ]
  if "capture_mode" in crtc_props:
    # Capture after display post-processing. This most closely matches the
    # physical panel and avoids the mixer-output writeback path that can time
    # out when the device UI changes.
    capture_values.append((crtc_id, crtc_props["capture_mode"], 1))

  rotation = 2 if height > width else 0
  output_width, output_height = (height, width) if rotation else (width, height)
  sys.stdout.buffer.write(struct.pack("!4sHHB", b"LUI1", output_width, output_height, rotation))
  sys.stdout.buffer.flush()

  frame_interval = 1.0 / fps
  buffer_index = 0
  while True:
    frame_started_at = time.monotonic()
    readable, _, _ = select.select([sys.stdin.buffer], [], [], 0)
    if readable:
      sys.stdin.buffer.read(1)
      break

    frame_values = [
      *capture_values,
      (connector_id, connector_props["FB_ID"], framebuffers[buffer_index]),
    ]
    retire_fence = C.c_int(-1)
    if "RETIRE_FENCE" in connector_props:
      frame_values.append((connector_id, connector_props["RETIRE_FENCE"], C.addressof(retire_fence)))
    # Attaching the writeback connector may require a modeset. Routine capture
    # frames must not permit one: it can stall Qualcomm's physical display
    # pipeline when the device UI changes.
    atomic_commit(drm_fd, frame_values, nonblocking=True, allow_modeset=not attached)
    attached = True
    stop_after_frame = False
    if retire_fence.value >= 0:
      deadline = time.monotonic() + 1.0
      while True:
        timeout = max(0.0, deadline - time.monotonic())
        readable, _, _ = select.select([retire_fence.value, sys.stdin.buffer], [], [], timeout)
        if retire_fence.value in readable:
          break
        if sys.stdin.buffer in readable:
          sys.stdin.buffer.read(1)
          stop_after_frame = True
        if time.monotonic() >= deadline:
          raise TimeoutError("timed out waiting for DRM writeback")
      os.close(retire_fence.value)
    else:
      time.sleep(0.02)
    if stop_after_frame:
      break
    raw = np.ndarray(
      (height, buffer_pitches[buffer_index]),
      dtype=np.uint8,
      buffer=mapped_buffers[buffer_index],
    )[:, :width * 4]
    frame = raw.reshape(height, width, 4).copy()
    if rotation:
      frame = np.rot90(frame, -1)
    compressed = zlib.compress(frame.tobytes(), 1)
    sys.stdout.buffer.write(struct.pack("!I", len(compressed)))
    sys.stdout.buffer.write(compressed)
    sys.stdout.buffer.flush()
    buffer_index = (buffer_index + 1) % len(framebuffers)

    # Limit the start-to-start capture rate without trying to catch up after a
    # slow DRM commit. Catch-up bursts can overwhelm Qualcomm's writeback path.
    time.sleep(max(0.0, frame_interval - (time.monotonic() - frame_started_at)))
except (BrokenPipeError, ConnectionResetError):
  pass
finally:
  if attached:
    try:
      atomic_commit(drm_fd, [
        (connector_id, connector_props["CRTC_ID"], 0),
        (connector_id, connector_props["FB_ID"], 0),
      ], allow_modeset=True)
    except Exception:
      pass
  for mapped in mapped_buffers:
    mapped.close()
  for framebuffer in framebuffers:
    lib.drmModeRmFB(drm_fd, framebuffer)
  for handle in handles:
    try:
      fcntl.ioctl(drm_fd, DESTROY_DUMB, struct.pack("<I", handle))
    except OSError:
      pass
  if broker is not None:
    try:
      broker.send(b"x")
    except OSError:
      pass
    broker.close()
  if drm_fd >= 0:
    os.close(drm_fd)
  if capture_lock >= 0:
    os.close(capture_lock)
  try:
    os.unlink(session_path)
  except FileNotFoundError:
    pass
"""

REMOTE_STOP_EXACT_SCRIPT = r"""
import glob
import os
import signal

capture_marker = b"CREATE_DUMB = 0xC02064B2"
python_marker = b"/usr/local/venv/bin/python"
excluded = {os.getpid(), os.getppid()}
stopped = 0

for cmdline_path in glob.glob("/proc/[0-9]*/cmdline"):
  pid = int(cmdline_path.split("/")[2])
  if pid in excluded:
    continue
  try:
    with open(cmdline_path, "rb") as cmdline_file:
      cmdline = cmdline_file.read()
    if capture_marker in cmdline and python_marker in cmdline:
      os.kill(pid, signal.SIGKILL)
      stopped += 1
  except (FileNotFoundError, PermissionError, ProcessLookupError):
    pass

for session_path in glob.glob("/tmp/sunnypilot-live-ui-*.pid"):
  try:
    os.unlink(session_path)
  except FileNotFoundError:
    pass

print(stopped)
"""

REMOTE_TOUCH_SCRIPT = r"""
import glob
import os
import struct
import sys
import time

EV_SYN = 0
EV_KEY = 1
EV_ABS = 3
SYN_REPORT = 0
BTN_TOUCH = 330
ABS_MT_SLOT = 47
ABS_MT_TOUCH_MAJOR = 48
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
ABS_MT_PRESSURE = 58


def find_touchscreen():
  for event in glob.glob("/sys/class/input/event*"):
    try:
      with open(f"{event}/device/name") as name:
        if name.read().strip() == "fts_ts":
          return f"/dev/input/{os.path.basename(event)}"
    except OSError:
      pass
  raise RuntimeError("device touchscreen was not found")


def input_event(event_type, code, value):
  now = time.time()
  sec = int(now)
  usec = int((now - sec) * 1_000_000)
  return struct.pack("llHHi", sec, usec, event_type, code, value)


def write_events(fd, events):
  payload = b"".join(input_event(*event) for event in events)
  payload += input_event(EV_SYN, SYN_REPORT, 0)
  os.write(fd, payload)


def read_exact(size):
  data = bytearray()
  while len(data) < size:
    chunk = sys.stdin.buffer.read(size - len(data))
    if not chunk:
      return None
    data.extend(chunk)
  return bytes(data)


touch_fd = os.open(find_touchscreen(), os.O_WRONLY)
tracking_id = 1
pressed = False
sys.stdout.write("READY\n")
sys.stdout.flush()
try:
  while packet := read_exact(5):
    action, x, y = struct.unpack("!BHH", packet)
    if action == 0:
      # Type-B multitouch slots retain their last position after release. Move
      # the inactive slot by one pixel first so a repeated tap still emits X/Y.
      write_events(touch_fd, [
        (EV_ABS, ABS_MT_SLOT, 0),
        (EV_ABS, ABS_MT_POSITION_X, x + 1 if x < 240 else x - 1),
        (EV_ABS, ABS_MT_POSITION_Y, y + 1 if y < 536 else y - 1),
      ])
      write_events(touch_fd, [
        (EV_ABS, ABS_MT_SLOT, 0),
        (EV_ABS, ABS_MT_TRACKING_ID, tracking_id),
        (EV_ABS, ABS_MT_POSITION_X, x),
        (EV_ABS, ABS_MT_POSITION_Y, y),
        (EV_ABS, ABS_MT_TOUCH_MAJOR, 8),
        (EV_ABS, ABS_MT_PRESSURE, 128),
        (EV_KEY, BTN_TOUCH, 1),
      ])
      tracking_id = (tracking_id + 1) & 0xffff
      pressed = True
    elif action == 1 and pressed:
      write_events(touch_fd, [
        (EV_ABS, ABS_MT_SLOT, 0),
        (EV_ABS, ABS_MT_POSITION_X, x),
        (EV_ABS, ABS_MT_POSITION_Y, y),
        (EV_ABS, ABS_MT_PRESSURE, 128),
      ])
    elif action == 2 and pressed:
      write_events(touch_fd, [
        (EV_ABS, ABS_MT_SLOT, 0),
        (EV_ABS, ABS_MT_PRESSURE, 0),
        (EV_ABS, ABS_MT_TRACKING_ID, -1),
        (EV_KEY, BTN_TOUCH, 0),
      ])
      pressed = False
finally:
  if pressed:
    write_events(touch_fd, [
      (EV_ABS, ABS_MT_SLOT, 0),
      (EV_ABS, ABS_MT_PRESSURE, 0),
      (EV_ABS, ABS_MT_TRACKING_ID, -1),
      (EV_KEY, BTN_TOUCH, 0),
    ])
  os.close(touch_fd)
"""


def road_camera_worker() -> None:
  import av
  import numpy as np

  from openpilot.cereal import messaging
  from msgq.visionipc import VisionIpcServer
  from openpilot.cereal.visionipc import VisionStreamType

  # The PC-side bridge republishes the remote stream into local MSGQ.
  os.environ.pop("ZMQ", None)
  messaging.reset_context()

  print("Waiting for live road camera metadata...", flush=True)
  sm = messaging.SubMaster([ROAD_ENCODE_SERVICE])
  while sm.recv_frame[ROAD_ENCODE_SERVICE] == 0:
    sm.update(100)

  encode_data = sm[ROAD_ENCODE_SERVICE]
  width, height = encode_data.width, encode_data.height

  vipc_server = VisionIpcServer("camerad")
  stream_type = VisionStreamType.VISION_STREAM_NARROW_ROAD
  vipc_server.create_buffers(stream_type, 4, width, height)
  vipc_server.start_listener()

  codec = av.CodecContext.create("hevc", "r")
  sock = messaging.sub_sock(ROAD_ENCODE_SERVICE, conflate=False)
  seen_iframe = False
  frame_id = 0

  print(f"Live road camera ready: {width}x{height}", flush=True)
  while True:
    for event in messaging.drain_sock(sock, wait_for_one=True):
      data = getattr(event, ROAD_ENCODE_SERVICE)
      if not seen_iframe and not (data.idx.flags & V4L2_BUF_FLAG_KEYFRAME):
        continue

      if not seen_iframe:
        codec.decode(av.packet.Packet(data.header))
        seen_iframe = True

      frames = codec.decode(av.packet.Packet(data.data))
      if not frames:
        continue

      frame = frames[-1]
      yuv420 = frame.to_ndarray(format=av.video.format.VideoFormat("yuv420p")).flatten()
      uv_offset = height * width
      y = yuv420[:uv_offset]
      uv = yuv420[uv_offset:].reshape(2, -1).ravel("F")
      nv12 = np.hstack((y, uv))

      now = time.monotonic_ns()
      vipc_server.send(stream_type, nv12.data, frame_id, now, now)
      frame_id += 1


def ssh_python_command(address: str, script: str, *args: object) -> list[str]:
  command = f"/usr/local/venv/bin/python -u -c {shlex.quote(script)}"
  if args:
    command += " " + " ".join(shlex.quote(str(arg)) for arg in args)
  return ["ssh", *SSH_OPTIONS, f"comma@{address}", command]


def read_exact(stream, size: int) -> bytes | None:
  data = bytearray()
  while len(data) < size:
    chunk = stream.read(size - len(data))
    if not chunk:
      return None
    data.extend(chunk)
  return bytes(data)


class ExactScreen:
  HEADER_SIZE = struct.calcsize("!4sHHB")

  def __init__(self, address: str, fps: int):
    self.address = address
    self.fps = fps
    self.disconnect_timeout = max(EXACT_DISCONNECT_MIN_TIMEOUT, EXACT_DISCONNECT_FRAME_INTERVALS / fps)
    self.session_token = secrets.token_hex(16)
    self.process: subprocess.Popen | None = None
    self.reader_thread: threading.Thread | None = None
    self.frames: queue.Queue[bytes] = queue.Queue(maxsize=2)
    self.width = 0
    self.height = 0
    self.rotation = 0
    self.last_frame_at = 0.0
    self.reader_error: Exception | None = None

  def start(self) -> None:
    self.process = subprocess.Popen(
      ssh_python_command(self.address, REMOTE_CAPTURE_SCRIPT, self.fps, self.session_token),
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      cwd=ROOT,
      start_new_session=True,
    )
    assert self.process.stdout is not None
    readable, _, _ = select.select([self.process.stdout], [], [], 10)
    if not readable:
      self.stop()
      raise TimeoutError("timed out waiting for the device screen capture")

    header = read_exact(self.process.stdout, self.HEADER_SIZE)
    if header is None:
      return_code = self.process.wait(timeout=2)
      assert self.process.stderr is not None
      error_lines = self.process.stderr.read().decode(errors="replace").strip().splitlines()
      if error_lines:
        raise RuntimeError(error_lines[-1].removeprefix("RuntimeError: "))
      raise RuntimeError(f"device screen capture exited with status {return_code}")

    magic, self.width, self.height, self.rotation = struct.unpack("!4sHHB", header)
    if magic != b"LUI1" or not self.width or not self.height:
      raise RuntimeError("device screen capture returned an invalid header")

    self.reader_thread = threading.Thread(target=self._read_frames, daemon=True)
    self.reader_thread.start()

  def _read_frames(self) -> None:
    assert self.process is not None and self.process.stdout is not None
    expected_size = self.width * self.height * 4
    try:
      while True:
        size_data = read_exact(self.process.stdout, 4)
        if size_data is None:
          break
        compressed_size, = struct.unpack("!I", size_data)
        if compressed_size > expected_size * 2:
          raise RuntimeError(f"invalid compressed screen frame size: {compressed_size}")
        compressed = read_exact(self.process.stdout, compressed_size)
        if compressed is None:
          break
        frame = zlib.decompress(compressed)
        if len(frame) != expected_size:
          raise RuntimeError(f"invalid screen frame size: {len(frame)}")

        if self.frames.full():
          try:
            self.frames.get_nowait()
          except queue.Empty:
            pass
        self.frames.put_nowait(frame)
        self.last_frame_at = time.monotonic()
    except Exception as error:
      self.reader_error = error

  def latest_frame(self) -> bytes | None:
    frame = None
    while True:
      try:
        frame = self.frames.get_nowait()
      except queue.Empty:
        return frame

  def check(self) -> None:
    if self.reader_error is not None:
      raise self.reader_error
    if self.process is not None:
      return_code = self.process.poll()
      if return_code is not None:
        raise RuntimeError(f"device screen capture exited with status {return_code}")

  def stop(self, force_remote: bool = False) -> None:
    if self.process is None:
      return

    if force_remote:
      # A Qualcomm DRM atomic commit can block inside the kernel and freeze the
      # physical display. Kill the token-verified remote helper before waiting
      # for SSH so the writeback connector is released as quickly as possible.
      self._stop_remote()
    elif self.process.poll() is None and self.process.stdin is not None:
      try:
        self.process.stdin.write(b"q")
        self.process.stdin.flush()
        self.process.stdin.close()
      except OSError:
        pass
    try:
      self.process.wait(timeout=2 if force_remote else 5)
    except subprocess.TimeoutExpired:
      self.process.terminate()
      try:
        self.process.wait(timeout=2)
      except subprocess.TimeoutExpired:
        self.process.kill()
        self.process.wait()

    if self.reader_thread is not None:
      self.reader_thread.join(timeout=1)
    self.process = None
    if not force_remote:
      self._stop_remote()

  def _stop_remote(self) -> None:
    session_path = f"/tmp/sunnypilot-live-ui-{self.session_token}.pid"
    command = "".join((
      f"session_path={shlex.quote(session_path)}; ",
      'if test -r "$session_path"; then ',
      'pid=$(cat "$session_path"); ',
      'case "$pid" in ""|*[!0-9]*) exit 1;; esac; ',
      f'if tr "\\0" " " < "/proc/$pid/cmdline" 2>/dev/null | grep -Fq -- {shlex.quote(self.session_token)}; ',
      'then kill -9 "$pid" 2>/dev/null || true; fi; ',
      'rm -f "$session_path"; fi',
    ))
    try:
      subprocess.run(
        ["ssh", *SSH_OPTIONS, f"comma@{self.address}", command],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=8,
        check=False,
      )
    except subprocess.TimeoutExpired:
      pass


class TouchForwarder:
  DOWN = 0
  MOVE = 1
  UP = 2

  def __init__(self, address: str, logical_width: int, logical_height: int, rotation: int):
    self.logical_width = logical_width
    self.logical_height = logical_height
    self.rotation = rotation
    self.raw_width = logical_height if rotation else logical_width
    self.raw_height = logical_width if rotation else logical_height
    self.enabled = False
    self.pressed = False
    self.process = subprocess.Popen(
      ssh_python_command(address, REMOTE_TOUCH_SCRIPT),
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      cwd=ROOT,
      start_new_session=True,
    )
    assert self.process.stdout is not None
    readable, _, _ = select.select([self.process.stdout], [], [], 10)
    ready = self.process.stdout.readline() if readable else b""
    if ready != b"READY\n":
      return_code = self.process.poll()
      self.stop()
      if return_code is None:
        raise TimeoutError("timed out waiting for remote touch control")
      raise RuntimeError(f"remote touch control exited with status {return_code}")
    self.enabled = True
    print("Remote touch control enabled over SSH", flush=True)

  def _coordinates(self, x: float, y: float) -> tuple[int, int]:
    x_ratio = min(max(x / max(self.logical_width - 1, 1), 0.0), 1.0)
    y_ratio = min(max(y / max(self.logical_height - 1, 1), 0.0), 1.0)
    if self.rotation == 1:
      raw_x = round((1.0 - y_ratio) * (self.raw_width - 1))
      raw_y = round(x_ratio * (self.raw_height - 1))
    elif self.rotation == 2:
      raw_x = round(y_ratio * (self.raw_width - 1))
      raw_y = round((1.0 - x_ratio) * (self.raw_height - 1))
    else:
      raw_x = round(x_ratio * (self.raw_width - 1))
      raw_y = round(y_ratio * (self.raw_height - 1))
    return raw_x, raw_y

  def send(self, action: int, x: float, y: float) -> None:
    if not self.enabled or self.process.stdin is None:
      return
    raw_x, raw_y = self._coordinates(x, y)
    try:
      self.process.stdin.write(struct.pack("!BHH", action, raw_x, raw_y))
      self.process.stdin.flush()
      self.pressed = action != self.UP
    except (BrokenPipeError, OSError):
      self.enabled = False
      print("Remote touch control disconnected", flush=True)

  def stop(self) -> None:
    if self.pressed:
      self.send(self.UP, 0, 0)
    if self.process.stdin is not None:
      try:
        self.process.stdin.close()
      except OSError:
        pass
    try:
      self.process.wait(timeout=3)
    except subprocess.TimeoutExpired:
      self.process.terminate()
      self.process.wait(timeout=2)


class TouchScheduler:
  REFERENCE_WIDTH = 536
  REFERENCE_HEIGHT = 240
  TAP_SECONDS = 0.04
  TAP_GAP_SECONDS = 0.04

  def __init__(self, touch: TouchForwarder, width: int, height: int):
    self.touch = touch
    self.width = width
    self.height = height
    self.actions: deque[tuple[float, int, float, float]] = deque()
    self.available_at = time.monotonic()

  @property
  def idle(self) -> bool:
    return not self.actions and time.monotonic() >= self.available_at

  def _point(self, x: float, y: float) -> tuple[float, float]:
    return x * self.width / self.REFERENCE_WIDTH, y * self.height / self.REFERENCE_HEIGHT

  def tap(self, x: float, y: float, delay: float = 0.0) -> None:
    start = max(time.monotonic() + delay, self.available_at)
    logical_x, logical_y = self._point(x, y)
    self.actions.append((start, TouchForwarder.DOWN, logical_x, logical_y))
    self.actions.append((start + self.TAP_SECONDS, TouchForwarder.UP, logical_x, logical_y))
    self.available_at = start + self.TAP_SECONDS + self.TAP_GAP_SECONDS

  def swipe(self, start: tuple[float, float], end: tuple[float, float], duration: float = 0.3) -> None:
    start_at = max(time.monotonic(), self.available_at)
    start_x, start_y = self._point(*start)
    end_x, end_y = self._point(*end)
    steps = 8
    self.actions.append((start_at, TouchForwarder.DOWN, start_x, start_y))
    for step in range(1, steps):
      fraction = step / steps
      x = start_x + (end_x - start_x) * fraction
      y = start_y + (end_y - start_y) * fraction
      self.actions.append((start_at + duration * fraction, TouchForwarder.MOVE, x, y))
    self.actions.append((start_at + duration, TouchForwarder.UP, end_x, end_y))
    self.available_at = start_at + duration + 0.12

  def update(self) -> None:
    now = time.monotonic()
    while self.actions and self.actions[0][0] <= now:
      _, action, x, y = self.actions.popleft()
      self.touch.send(action, x, y)


class ExactInputController:
  LETTER_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
  SPECIAL_ROWS = ("1234567890", "-/:;()$&@\"", "~.,?!'#%")
  SUPER_SPECIAL_ROWS = ("1234567890", "`[]{}^*+=_", "\\|<>¥€£•")
  ROW_Y = (113.0, 165.0, 217.0)
  ENTER = (50.0, 30.0)
  BACKSPACE = (490.0, 30.0)
  CAPS = (52.0, 217.0)
  NUMBERS = (484.0, 217.0)
  MORE_SYMBOLS = (52.0, 217.0)
  LETTERS = (484.0, 217.0)
  SPACE = (495.0, 165.0)

  def __init__(self, touch: TouchForwarder, width: int, height: int):
    self.scheduler = TouchScheduler(touch, width, height)
    self.width = width
    self.height = height
    self._np = None
    self._keyboard_expected = None
    self._keyboard_mask = None
    self._keyboard_seen_at = 0.0
    self._keyboard_active = False
    self._keyboard_forced = False
    self._layout = "lower"
    self._load_screen_references()

  def _load_screen_references(self) -> None:
    print("Keyboard: type directly when the device keyboard is visible", flush=True)
    print("Shortcuts: Down Back · Left/Right Swipe · Cmd/Ctrl+K Keyboard", flush=True)

    if (self.width, self.height) != (TouchScheduler.REFERENCE_WIDTH, TouchScheduler.REFERENCE_HEIGHT):
      print("Automatic keyboard detection requires a 536x240 mici screen; Cmd/Ctrl+K remains available", flush=True)
      return

    try:
      import numpy as np
      from PIL import Image
    except ImportError:
      print("Automatic keyboard detection unavailable: Pillow or NumPy is missing; Cmd/Ctrl+K remains available",
            flush=True)
      return

    def composite_reference(path: Path, size: tuple[int, int]):
      image = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
      pixels = np.asarray(image, dtype=np.float32)
      alpha = pixels[:, :, 3] / 255.0
      gray = pixels[:, :, :3].mean(axis=2) * alpha
      return gray

    self._np = np
    keyboard_path = ROOT / "openpilot/selfdrive/assets/icons_mici/settings/keyboard/keyboard_background.png"
    self._keyboard_expected = composite_reference(keyboard_path, (520, 170))
    self._keyboard_mask = self._keyboard_expected > 25

  @staticmethod
  def _row_positions(row: str, row_index: int) -> dict[str, tuple[float, float]]:
    padding = (44.0, 33.0, 44.0)[row_index]
    start = 8.0 + padding
    leading_controls = 1 if row_index == 2 else 0
    trailing_controls = 1 if row_index in (1, 2) else 0
    total_keys = len(row) + leading_controls + trailing_controls
    step = (520.0 - 2 * padding) / max(total_keys - 1, 1)
    return {char: (start + (index + leading_controls) * step, ExactInputController.ROW_Y[row_index])
            for index, char in enumerate(row)}

  def _screen_gray(self, frame: bytes):
    assert self._np is not None
    pixels = self._np.frombuffer(frame, dtype=self._np.uint8).reshape(self.height, self.width, 4)
    return pixels[:, :, :3].mean(axis=2)

  def update_frame(self, frame: bytes) -> None:
    if self._np is None:
      return
    screen = self._screen_gray(frame)
    keyboard_crop = screen[70:240, 8:528]
    difference = self._np.abs(keyboard_crop - self._keyboard_expected)
    detected = float(self._np.median(difference[self._keyboard_mask])) < 18.0
    now = time.monotonic()
    if detected:
      self._keyboard_seen_at = now
    keyboard_active = self._keyboard_forced or now - self._keyboard_seen_at < 0.5
    if keyboard_active and not self._keyboard_active:
      self._layout = "lower"
      print("Device keyboard detected; local typing enabled", flush=True)
    self._keyboard_active = keyboard_active

  def _ensure_layout(self, layout: str) -> None:
    if self._layout == layout:
      return
    if layout == "lower":
      self.scheduler.tap(*self.LETTERS)
    elif layout == "special":
      if self._layout == "super":
        self.scheduler.tap(*self.MORE_SYMBOLS)
      else:
        self.scheduler.tap(*self.NUMBERS)
    elif layout == "super":
      if self._layout == "lower":
        self.scheduler.tap(*self.NUMBERS)
      self.scheduler.tap(*self.MORE_SYMBOLS)
    self._layout = layout

  def _type_character(self, char: str) -> None:
    lower_positions = {}
    for row_index, row in enumerate(self.LETTER_ROWS):
      lower_positions.update(self._row_positions(row, row_index))

    if char == " ":
      self._ensure_layout("lower")
      self.scheduler.tap(*self.SPACE)
    elif char.lower() in lower_positions:
      self._ensure_layout("lower")
      if char.isupper():
        self.scheduler.tap(*self.CAPS)
      self.scheduler.tap(*lower_positions[char.lower()])
    else:
      special_positions = {}
      for row_index, row in enumerate(self.SPECIAL_ROWS):
        special_positions.update(self._row_positions(row, row_index))
      super_positions = {}
      for row_index, row in enumerate(self.SUPER_SPECIAL_ROWS):
        super_positions.update(self._row_positions(row, row_index))

      if char in special_positions:
        self._ensure_layout("special")
        self.scheduler.tap(*special_positions[char])
        self.scheduler.tap(*self.LETTERS)
        self._layout = "lower"
      elif char in super_positions:
        self._ensure_layout("super")
        self.scheduler.tap(*super_positions[char])
        self.scheduler.tap(*self.LETTERS)
        self._layout = "lower"
      else:
        print(f"Keyboard character not supported: {char!r}", flush=True)

  def handle_keyboard(self, rl) -> None:
    shortcut_modifier_down = (
      rl.is_key_down(rl.KEY_LEFT_SUPER)
      or rl.is_key_down(rl.KEY_RIGHT_SUPER)
      or rl.is_key_down(rl.KEY_LEFT_CONTROL)
      or rl.is_key_down(rl.KEY_RIGHT_CONTROL)
    )

    if shortcut_modifier_down and rl.is_key_pressed(rl.KEY_K):
      self._keyboard_forced = not self._keyboard_forced
      if self._keyboard_forced:
        self._layout = "lower"
      self._keyboard_active = self._keyboard_forced or time.monotonic() - self._keyboard_seen_at < 0.5
      label = "forced on" if self._keyboard_forced else "automatic"
      print(f"Local keyboard forwarding: {label}", flush=True)
      while rl.get_char_pressed():
        pass
      return
    down_pressed = rl.is_key_pressed(rl.KEY_DOWN)
    if self.scheduler.idle and (down_pressed or rl.is_key_down(rl.KEY_DOWN)):
      self.scheduler.swipe((268.0, 25.0), (268.0, 220.0))
      while rl.get_char_pressed():
        pass
      return
    left_pressed = rl.is_key_pressed(rl.KEY_LEFT)
    if self.scheduler.idle and (left_pressed or rl.is_key_down(rl.KEY_LEFT)):
      self.scheduler.swipe((106.0, 120.0), (430.0, 120.0))
      while rl.get_char_pressed():
        pass
      return
    right_pressed = rl.is_key_pressed(rl.KEY_RIGHT)
    if self.scheduler.idle and (right_pressed or rl.is_key_down(rl.KEY_RIGHT)):
      self.scheduler.swipe((430.0, 120.0), (106.0, 120.0))
      while rl.get_char_pressed():
        pass
      return

    if shortcut_modifier_down or not self._keyboard_active:
      while rl.get_char_pressed():
        pass
      return
    if rl.is_key_pressed(rl.KEY_BACKSPACE):
      self.scheduler.tap(*self.BACKSPACE)
    if rl.is_key_pressed(rl.KEY_ENTER) or rl.is_key_pressed(rl.KEY_KP_ENTER):
      self.scheduler.tap(*self.ENTER)

    while codepoint := rl.get_char_pressed():
      self._type_character(chr(codepoint))

  @property
  def keyboard_enabled(self) -> bool:
    return self._keyboard_active

  def update(self) -> None:
    self.scheduler.update()


class ConnectionStatus:
  STATES = {
    "connected": "connected",
    "no_camera": "no camera",
    "disconnected": "disconnected",
  }

  def __init__(self):
    from msgq.visionipc import VisionIpcClient
    from openpilot.cereal.visionipc import VisionStreamType

    self.last_telemetry_at = 0.0
    self.last_camera_at = 0.0
    self.last_camera_connect_attempt = 0.0
    self.state = ""
    self.camera_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_NARROW_ROAD, conflate=True)

  def update(self, sm) -> None:
    import pyray as rl

    now = time.monotonic()
    if sm.updated["deviceState"]:
      self.last_telemetry_at = now

    if not self.camera_client.is_connected() and now - self.last_camera_connect_attempt >= 0.5:
      self.last_camera_connect_attempt = now
      self.camera_client.connect(False)
    if self.camera_client.is_connected() and self.camera_client.recv(timeout_ms=0):
      self.last_camera_at = now

    telemetry_connected = now - self.last_telemetry_at < CONNECTION_TIMEOUT
    camera_connected = now - self.last_camera_at < CONNECTION_TIMEOUT
    if telemetry_connected and camera_connected:
      state = "connected"
    elif telemetry_connected:
      state = "no_camera"
    else:
      state = "disconnected"

    if state != self.state:
      self.state = state
      label = self.STATES[state]
      print(f"Live UI connection: {label}", flush=True)
      rl.set_window_title(f"sunnypilot live — {label}")


class LiveUi:
  def __init__(self, address: str):
    self.address = address
    self.processes: list[tuple[str, subprocess.Popen]] = []

  def _start(self, name: str, command: list[str]) -> None:
    process = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    self.processes.append((name, process))

  def check(self) -> None:
    for name, process in self.processes:
      return_code = process.poll()
      if return_code is not None:
        raise RuntimeError(f"{name} exited unexpectedly with status {return_code}")

  def start(self) -> int:
    if not BRIDGE.is_file():
      raise FileNotFoundError(f"{BRIDGE} is not built; run `scons -u openpilot/cereal/messaging/bridge` first")

    # Keep upstream files unchanged: bridge remote cereal messages into local
    # MSGQ, turn encoded road video into local VisionIPC, then run its normal layout.
    services = [
      name for name in SERVICE_LIST
      if name not in LOCAL_UI_PUBLISHERS and name not in UNUSED_CAMERA_SERVICES
    ]
    self._start("messaging bridge", [str(BRIDGE), self.address, ",".join(services)])
    self._start("road camera", [sys.executable, str(Path(__file__).resolve()), "--camera-worker"])

    print(f"Streaming the live onroad UI from {self.address}", flush=True)
    return run_ui(self)

  def stop(self) -> None:
    for _name, process in reversed(self.processes):
      if process.poll() is not None:
        continue

      process.send_signal(signal.SIGTERM)
      try:
        process.wait(timeout=3)
      except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

    self.processes.clear()


def run_ui(live_ui: LiveUi) -> int:
  import pyray as rl

  from openpilot.cereal import messaging
  from openpilot.common.hardware import COMMA_HARDWARE
  from openpilot.common.realtime import Priority, config_realtime_process, set_core_affinity
  from openpilot.selfdrive.ui.layouts.main import MainLayout
  from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.application import gui_app

  cores = {5, }
  config_realtime_process(0, Priority.CTRL_HIGH)

  gui_app.init_window("sunnypilot live")
  if gui_app.big_ui():
    MainLayout()
  else:
    MiciMainLayout()

  connection_status = ConnectionStatus()
  pm = messaging.PubMaster(["uiDebug"])
  for should_render, frame_time, cpu_time in gui_app.render():
    live_ui.check()
    extra_start = time.monotonic()
    ui_state.update()
    connection_status.update(ui_state.sm)

    if should_render:
      if COMMA_HARDWARE and os.sched_getaffinity(0) != cores:
        try:
          set_core_affinity(list(cores))
        except OSError:
          pass

      extra_cpu = time.monotonic() - extra_start
      msg = messaging.new_message("uiDebug")
      msg.uiDebug.cpuTimeMillis = (cpu_time + extra_cpu) * 1000
      msg.uiDebug.frameTimeMillis = frame_time * 1000
      pm.send("uiDebug", msg)

  rl.set_window_title("sunnypilot live")
  return 0


def run_exact_ui(address: str, control: bool, fps: int) -> int:
  import pyray as rl

  capture = ExactScreen(address, fps)
  touch = None
  input_controller = None
  texture = None

  try:
    capture.start()
    scale = float(os.getenv("SCALE", "1.0"))
    window_width = max(1, round(capture.width * scale))
    window_height = max(1, round(capture.height * scale))

    rl.set_config_flags(rl.ConfigFlags.FLAG_VSYNC_HINT)
    rl.init_window(window_width, window_height, "sunnypilot exact")
    rl.set_exit_key(rl.KEY_NULL)
    rl.set_target_fps(60)
    image = rl.gen_image_color(capture.width, capture.height, rl.BLACK)
    texture = rl.load_texture_from_image(image)
    rl.unload_image(image)

    if control:
      touch = TouchForwarder(address, capture.width, capture.height, capture.rotation)
      input_controller = ExactInputController(touch, capture.width, capture.height)

    state = ""
    window_title = ""
    while not rl.window_should_close():
      capture.check()
      frame = capture.latest_frame()
      if frame is not None:
        frame_buffer = rl.ffi.from_buffer(frame)
        rl.update_texture(texture, rl.ffi.cast("void *", frame_buffer))
        if input_controller is not None:
          input_controller.update_frame(frame)

      now = time.monotonic()
      new_state = ""
      if capture.last_frame_at:
        if now - capture.last_frame_at >= capture.disconnect_timeout:
          print("Exact UI capture stalled; stopping it to protect the device display", flush=True)
          capture.stop(force_remote=True)
          raise RuntimeError("screen capture stalled and was stopped")
        new_state = "connected"
      if new_state and new_state != state:
        state = new_state
        print(f"Exact UI connection: {state}", flush=True)

      if touch is not None:
        assert input_controller is not None
        input_controller.handle_keyboard(rl)
        input_controller.update()

        if input_controller.scheduler.idle:
          position = rl.get_mouse_position()
          logical_x = position.x / scale
          logical_y = position.y / scale
          button = rl.MouseButton.MOUSE_BUTTON_LEFT
          if rl.is_mouse_button_pressed(button):  # noqa: TID251
            touch.send(TouchForwarder.DOWN, logical_x, logical_y)
          elif rl.is_mouse_button_released(button):  # noqa: TID251
            touch.send(TouchForwarder.UP, logical_x, logical_y)
          elif rl.is_mouse_button_down(button):
            touch.send(TouchForwarder.MOVE, logical_x, logical_y)

      new_window_title = f"sunnypilot exact — {state}" if state else "sunnypilot exact"
      if input_controller is not None and input_controller.keyboard_enabled:
        new_window_title += " — keyboard"
      if new_window_title != window_title:
        window_title = new_window_title
        rl.set_window_title(window_title)

      rl.begin_drawing()
      rl.clear_background(rl.BLACK)
      rl.draw_texture_pro(
        texture,
        rl.Rectangle(0, 0, capture.width, capture.height),
        rl.Rectangle(0, 0, window_width, window_height),
        rl.Vector2(0, 0),
        0,
        rl.WHITE,
      )
      rl.end_drawing()
  finally:
    if touch is not None:
      touch.stop()
    capture.stop()
    if texture is not None:
      rl.unload_texture(texture)
    if rl.is_window_ready():
      rl.close_window()
  return 0


def stop_exact_sessions(address: str) -> int:
  result = subprocess.run(
    ssh_python_command(address, REMOTE_STOP_EXACT_SCRIPT),
    cwd=ROOT,
    capture_output=True,
    text=True,
    timeout=10,
    check=False,
  )
  if result.returncode:
    message = result.stderr.strip() or f"remote cleanup exited with status {result.returncode}"
    raise RuntimeError(message)

  stopped = int(result.stdout.strip())
  noun = "helper" if stopped == 1 else "helpers"
  print(f"Stopped {stopped} exact-screen {noun} on {address}")
  return 0


def get_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Show or control the live sunnypilot UI over Wi-Fi; replay is not used."
  )
  parser.add_argument("address", nargs="?", help="comma device IP address or hostname")
  parser.add_argument("--ip", dest="ip_address", metavar="ADDRESS", help="comma device IP address or hostname")
  parser.add_argument("--exact", action="store_true", help="show the device's actual DRM screen instead of a local UI")
  parser.add_argument("--stop-exact", "--kill-exact", dest="stop_exact", action="store_true",
                      help="stop orphaned exact-screen capture helpers on the device")
  parser.add_argument("--control", action="store_true",
                      help="with --exact, forward mouse and keyboard input to the device")
  parser.add_argument("--exact-fps", type=int, default=EXACT_CAPTURE_FPS, metavar="FPS",
                      help=f"exact-screen capture rate (default: {EXACT_CAPTURE_FPS})")
  parser.add_argument("--camera-worker", action="store_true", help=argparse.SUPPRESS)
  return parser


def main() -> int:
  args = get_arg_parser().parse_args()
  if args.camera_worker:
    road_camera_worker()
    return 0

  if args.address and args.ip_address:
    get_arg_parser().error("provide the device address either positionally or with --ip, not both")
  address = args.ip_address or args.address
  if not address:
    get_arg_parser().error("a device address is required")
  if not 1 <= args.exact_fps <= 60:
    get_arg_parser().error("--exact-fps must be between 1 and 60")
  if args.control and not args.exact:
    get_arg_parser().error("--control requires --exact")

  if args.stop_exact:
    if args.exact:
      get_arg_parser().error("--stop-exact cannot be combined with --exact")
    try:
      return stop_exact_sessions(address)
    except (OSError, RuntimeError) as error:
      print(f"Unable to stop exact UI: {error}", file=sys.stderr)
      return 1

  if args.exact:
    try:
      return run_exact_ui(address, args.control, args.exact_fps)
    except KeyboardInterrupt:
      return 130
    except (OSError, RuntimeError) as error:
      print(f"Exact UI unavailable: {error}", file=sys.stderr)
      return 1

  live_ui = LiveUi(address)
  try:
    return live_ui.start()
  except KeyboardInterrupt:
    return 130
  finally:
    live_ui.stop()


if __name__ == "__main__":
  sys.exit(main())
