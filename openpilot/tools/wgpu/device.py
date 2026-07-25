#!/usr/bin/env python3
import argparse
import signal
import subprocess
import time
from pathlib import Path

from openpilot.common.params import Params


MODEL_OUTPUTS = "modelV2,drivingModelData,cameraOdometry,modelDataV2SP"
ROOT = Path(__file__).resolve().parents[3]
BRIDGE = ROOT / "openpilot/cereal/messaging/bridge"


def stop_process(proc: subprocess.Popen) -> None:
  proc.terminate()
  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()


def handle_sigterm(*_) -> None:
  raise KeyboardInterrupt


def main() -> None:
  parser = argparse.ArgumentParser(description="Route modeld traffic between this device and a wireless host.")
  parser.add_argument("host", help="Laptop IP address reachable from this device")
  args = parser.parse_args()

  if not BRIDGE.is_file():
    raise FileNotFoundError(f"build the cereal bridge first: {BRIDGE}")

  params = Params()
  if not params.get_bool("IsOffroad"):
    raise RuntimeError("start the wgpu bridge while offroad")

  procs: list[subprocess.Popen] = []
  try:
    params.put_bool("WgpuEnabled", True, block=True)
    procs = [
      subprocess.Popen([str(BRIDGE)]),
      subprocess.Popen([str(BRIDGE), args.host, MODEL_OUTPUTS]),
    ]
    print(f"wgpu enabled; forwarding camera/state to {args.host}")
    print("keep this process running; Ctrl+C restores local modeld")
    while all(proc.poll() is None for proc in procs):
      time.sleep(0.25)
    failed = next(proc for proc in procs if proc.poll() is not None)
    raise RuntimeError(f"bridge exited with status {failed.returncode}")
  finally:
    params.put_bool("WgpuEnabled", False, block=True)
    for proc in procs:
      if proc.poll() is None:
        stop_process(proc)
    print("wgpu disabled; local modeld restored")


if __name__ == "__main__":
  signal.signal(signal.SIGTERM, handle_sigterm)
  try:
    main()
  except KeyboardInterrupt:
    pass
