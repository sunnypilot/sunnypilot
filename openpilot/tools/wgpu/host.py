#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CAMERASTREAM = ROOT / "openpilot/tools/camerastream/compressed_vipc.py"


def stop_process(proc: subprocess.Popen) -> None:
  try:
    os.killpg(proc.pid, signal.SIGTERM)
  except ProcessLookupError:
    proc.wait()
    return
  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()


def main() -> None:
  parser = argparse.ArgumentParser(description="Run modeld on this host for a remote comma device.")
  parser.add_argument("device", help="comma device hostname or IP address")
  parser.add_argument("--big-model", action="store_true", help="use the locally compiled big driving model")
  args = parser.parse_args()

  camera = subprocess.Popen([sys.executable, str(CAMERASTREAM), args.device, "--cams", "0,2"], start_new_session=True)
  model_args = [sys.executable, "-m", "openpilot.selfdrive.modeld.modeld", "--remote", args.device]
  if args.big_model:
    model_args.append("--big-model")
  model = subprocess.Popen(model_args, cwd=ROOT, start_new_session=True)

  procs = {"camera bridge": camera, "modeld": model}
  try:
    while all(proc.poll() is None for proc in procs.values()):
      time.sleep(0.25)
    failed_name, failed = next((name, proc) for name, proc in procs.items() if proc.poll() is not None)
    raise RuntimeError(f"wgpu {failed_name} exited with status {failed.returncode}")
  finally:
    for proc in procs.values():
      if proc.poll() is None:
        stop_process(proc)
    print("wgpu host stopped")


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    pass
