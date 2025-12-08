#!/usr/bin/env python3
import os
import sys
import platform
import struct
import select
import time
import ctypes
from collections import defaultdict

from openpilot.system.hardware.hw import Paths

from sunnypilot.common.param_watcher import ParamWatcher, IN_CLOSE_WRITE, IN_MOVED_TO

IN_ACCESS = 0x00000001


def get_linux_monitor(params_path, reads, writes):
  libc = ctypes.CDLL('libc.so.6')
  fd = libc.inotify_init()
  if fd < 0:
    return None

  mask = IN_ACCESS | IN_MOVED_TO | IN_CLOSE_WRITE
  if libc.inotify_add_watch(fd, params_path.encode(), mask) < 0:
    return None

  poll_obj = select.epoll()
  poll_obj.register(fd, select.EPOLLIN)

  def monitor():
    for fileno, _ in poll_obj.poll(0.1):
      if fileno == fd:
        buffer = os.read(fd, 4096)
        i = 0
        while i + 16 <= len(buffer):
          wd, mask, cookie, name_len = struct.unpack_from("iIII", buffer, i)
          name = buffer[i+16:i+16+name_len].rstrip(b"\0").decode('utf-8', 'ignore')
          if name and not name.startswith("."):
            if mask & IN_ACCESS:
              reads[name] += 1
            elif mask & (IN_MOVED_TO | IN_CLOSE_WRITE):
              writes[name] += 1
          i += 16 + name_len

  def cleanup():
    os.close(fd)
  return monitor, cleanup

def get_darwin_monitor(params_path, reads, writes):
  print("WARNING: macOS only reports WRITES.")

  def callback(name):
    writes[name] += 1

  watcher = ParamWatcher()
  watcher.add_watcher(callback)

  def monitor():
    time.sleep(0.1)

  def cleanup():
    if callback in watcher._callbacks:
      watcher._callbacks.remove(callback)
  return monitor, cleanup

def profile_params():
  path = Paths.params_root()
  if not os.path.exists(path):
    return print(f"Error: {path} not found")

  print(f"Profiling Params I/O at: {path}\nPress CTRL+C to stop.")
  reads, writes = defaultdict(int), defaultdict(int)

  setup = get_linux_monitor if platform.system() == "Linux" else \
          get_darwin_monitor if platform.system() == "Darwin" else None

  if not setup:
    return print("Unsupported platform")
  monitor, cleanup = setup(path, reads, writes) or (None, None)

  if not monitor:
    return print("Failed to initialize monitor")

  start_time = time.monotonic()
  last_print = start_time

  try:
    while True:
      monitor()
      if time.monotonic() - last_print > 1.0:
        sys.stdout.write(".")
        sys.stdout.flush()
        last_print = time.monotonic()
  except KeyboardInterrupt:
    print("\n\nStopping...")
  finally:
    cleanup()

  duration = time.monotonic() - start_time
  print(f"\n\n=== Params I/O Profile Report ({duration:.1f}s) ===")
  print(f"{'Param Name':<40} | {'Reads/sec':<10} | {'Writes/sec':<10} | {'Total Reads':<12} | {'Total Writes':<12}")
  print("-" * 95)

  for k in sorted(set(reads) | set(writes), key=lambda k: reads[k] + writes[k], reverse=True):
    print(f"{k:<40} | {reads[k]/duration:<10.1f} | {writes[k]/duration:<10.1f} | {reads[k]:<12} | {writes[k]:<12}")

if __name__ == "__main__":
  profile_params()
