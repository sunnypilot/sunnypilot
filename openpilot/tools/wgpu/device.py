#!/usr/bin/env python3
import argparse
import signal
import subprocess
import time
from pathlib import Path

import openpilot.cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.tools.wgpu.zmq import ZmqSubSocket


MODEL_OUTPUTS = "modelV2,drivingModelData,cameraOdometry,modelDataV2SP"
REMOTE_MODEL_TIMEOUT = 0.35
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


def receive_fresh_model(sock: ZmqSubSocket) -> bool:
  raw = sock.receive(non_blocking=True)
  if raw is None:
    return False
  event = messaging.log_from_bytes(raw)
  if event.which() != "modelV2" or not event.valid:
    return False
  model_age = (time.monotonic_ns() - event.modelV2.timestampEof) / 1e9
  return 0 <= model_age < REMOTE_MODEL_TIMEOUT


def main() -> None:
  parser = argparse.ArgumentParser(description="Route modeld traffic between this device and a wireless host.")
  parser.add_argument("host", help="Laptop IP address reachable from this device")
  args = parser.parse_args()

  if not BRIDGE.is_file():
    raise FileNotFoundError(f"build the cereal bridge first: {BRIDGE}")

  params = Params()
  forward: subprocess.Popen | None = None
  reverse: subprocess.Popen | None = None
  wgpu_enabled = False
  try:
    # Keep local modeld publishing while the remote model connects and warms up.
    forward = subprocess.Popen([str(BRIDGE)])
    remote_model = ZmqSubSocket("modelV2", args.host, conflate=True)
    print(f"forwarding camera/state to {args.host}; waiting for a fresh remote model")
    while not receive_fresh_model(remote_model):
      if forward.poll() is not None:
        raise RuntimeError(f"forward bridge exited with status {forward.returncode}")
      time.sleep(0.05)

    # Local modeld remains warm but stops publishing when this flag changes.
    params.put_bool("WgpuEnabled", True, block=True)
    wgpu_enabled = True
    time.sleep(2 * DT_MDL)
    reverse = subprocess.Popen([str(BRIDGE), args.host, MODEL_OUTPUTS])
    print("wgpu active; Ctrl+C or loss of the remote model restores local modeld")

    last_remote_model = time.monotonic()
    while True:
      if receive_fresh_model(remote_model):
        last_remote_model = time.monotonic()
      if forward.poll() is not None:
        raise RuntimeError(f"forward bridge exited with status {forward.returncode}")
      if reverse.poll() is not None:
        raise RuntimeError(f"reverse bridge exited with status {reverse.returncode}")
      if time.monotonic() - last_remote_model > REMOTE_MODEL_TIMEOUT:
        raise RuntimeError("remote model timed out; restoring local modeld")
      time.sleep(0.05)
  finally:
    # Stop remote publication before allowing the warm local publisher to resume.
    if reverse is not None and reverse.poll() is None:
      stop_process(reverse)
    if wgpu_enabled:
      params.put_bool("WgpuEnabled", False, block=True)
    if forward is not None and forward.poll() is None:
      stop_process(forward)
    print("wgpu disabled; local modeld restored")


if __name__ == "__main__":
  signal.signal(signal.SIGTERM, handle_sigterm)
  try:
    main()
  except KeyboardInterrupt:
    pass
