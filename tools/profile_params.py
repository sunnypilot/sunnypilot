#!/usr/bin/env python3
import os
import sys
import platform
import struct
import random
import select
import time
import ctypes
import argparse
import csv
try:
  import matplotlib.pyplot as plt
except ImportError:
  plt = None
from collections import defaultdict

from openpilot.system.hardware.hw import Paths

from openpilot.sunnypilot.common.param_watcher import ParamWatcher, IN_CLOSE_WRITE, IN_MOVED_TO

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
  parser = argparse.ArgumentParser(description="Profile Params I/O")
  parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds (default: 30 mins)")
  default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params_profile_{random.randrange(99999)}.csv")
  parser.add_argument("--out", type=str, default=default_out, help="Output CSV file")
  args = parser.parse_args()

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

      if args.timeout > 0 and (time.monotonic() - start_time) > args.timeout:
        print("\nTimeout reached.")
        break
  except KeyboardInterrupt:
    print("\n\nStopping...")
  finally:
    cleanup()

  duration = time.monotonic() - start_time

  if args.out:
    with open(args.out, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(['Param Name', 'Reads/sec', 'Writes/sec', 'Total Reads', 'Total Writes'])
      for k in sorted(set(reads) | set(writes), key=lambda k: reads[k] + writes[k], reverse=True):
        writer.writerow([k, f"{reads[k]/duration:.1f}", f"{writes[k]/duration:.1f}", reads[k], writes[k]])
    print(f"\nCSV report saved to {args.out}")

  if plt:
    data = []
    for k in sorted(set(reads) | set(writes), key=lambda k: reads[k] + writes[k], reverse=True):
      data.append((k, reads[k]/duration, writes[k]/duration))

    if data:
      names = [x[0] for x in data]
      read_rates = [x[1] for x in data]
      write_rates = [x[2] for x in data]

      plt.figure(figsize=(10, len(names) * 0.3 + 2))
      y_pos = range(len(names))
      plt.barh(y_pos, read_rates, align='center', alpha=0.7, label='Reads/sec')
      plt.barh(y_pos, write_rates, align='center', alpha=0.7, left=read_rates, label='Writes/sec')
      plt.yticks(y_pos, names)
      plt.xlabel('Rate (Hz)')
      plt.title('Params I/O Profile')
      plt.legend()
      plt.tight_layout()
      plt.gca().invert_yaxis()

      plot_filename = os.path.splitext(args.out)[0] + ".png"
      plt.savefig(plot_filename)
      print(f"Plot saved to {plot_filename}")
  else:
    print("matplotlib not found, skipping plot generation")

if __name__ == "__main__":
  profile_params()
