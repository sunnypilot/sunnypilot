#!/usr/bin/env python3
import argparse
import signal
import subprocess
import time
from pathlib import Path

import openpilot.cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.tools.wgpu.zmq import ZmqSubSocket


MODEL_OUTPUTS = "modelV2,drivingModelData,cameraOdometry,modelDataV2SP"
MODEL_PROCESSES = {"modeld", "modeld_tinygrad"}
REMOTE_MODEL_TIMEOUT = 1.0
WGPU_STATUS = "wgpuStatus"
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


def receive_model(sock: ZmqSubSocket) -> tuple[bool, float]:
  raw = sock.receive(non_blocking=True)
  if raw is None:
    return False, float("inf")
  event = messaging.log_from_bytes(raw)
  if event.which() != "modelV2" or not event.valid:
    return True, float("inf")
  model_age = (time.monotonic_ns() - event.modelV2.timestampEof) / 1e9
  return True, model_age


def receive_model_name(sock: ZmqSubSocket) -> str | None:
  raw = sock.receive(non_blocking=True)
  if raw is None:
    return None
  model_name = raw.decode(errors="replace").upper()
  return model_name if model_name in ("SMALL", "BIG") else None


def wait_for_local_modeld_stop(timeout: float = 10.) -> None:
  sm = messaging.SubMaster(["managerState"])
  deadline = time.monotonic() + timeout
  while time.monotonic() < deadline:
    sm.update(100)
    if sm.seen["managerState"]:
      running = {p.name for p in sm["managerState"].processes if p.running}
      if not running.intersection(MODEL_PROCESSES):
        return
  raise RuntimeError("timed out waiting for local modeld publisher to stop")


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
    forward = subprocess.Popen([str(BRIDGE)])
    params.put_bool("WgpuReady", True, block=True)
    remote_model = ZmqSubSocket("modelV2", args.host, conflate=True)
    remote_status = ZmqSubSocket(WGPU_STATUS, args.host, conflate=True)

    while True:
      # Keep local modeld publishing while a host connects and warms up.
      print(f"forwarding camera/state to {args.host}; waiting for a fresh remote model")
      model_name = None
      while True:
        received, model_age = receive_model(remote_model)
        model_name = receive_model_name(remote_status) or model_name
        if received and 0 <= model_age < REMOTE_MODEL_TIMEOUT and model_name is not None:
          break
        if forward.poll() is not None:
          raise RuntimeError(f"forward bridge exited with status {forward.returncode}")
        time.sleep(0.05)

      # Stop the local publisher before attaching the reverse bridge. msgq permits
      # only one publisher for each model service.
      params.put("WgpuModelName", model_name, block=True)
      params.put_bool("WgpuEnabled", True, block=True)
      wgpu_enabled = True
      wait_for_local_modeld_stop()
      reverse = subprocess.Popen([str(BRIDGE), args.host, MODEL_OUTPUTS])
      print("wgpu active; Ctrl+C or loss of the remote model restores local modeld")

      last_remote_model = time.monotonic()
      while True:
        received, _ = receive_model(remote_model)
        if received:
          last_remote_model = time.monotonic()
        if forward.poll() is not None:
          raise RuntimeError(f"forward bridge exited with status {forward.returncode}")
        if reverse.poll() is not None:
          print(f"reverse bridge exited with status {reverse.returncode}; restoring local modeld")
          break
        if time.monotonic() - last_remote_model > REMOTE_MODEL_TIMEOUT:
          print("remote model timed out; restoring local modeld")
          break
        time.sleep(0.05)

      stop_process(reverse)
      reverse = None
      params.put_bool("WgpuEnabled", False, block=True)
      wgpu_enabled = False
      params.remove("WgpuModelName")
      print("wgpu disabled; local modeld restored; ready for the next host run")
  finally:
    # Stop remote publication before allowing the local publisher to restart.
    if reverse is not None and reverse.poll() is None:
      stop_process(reverse)
    if wgpu_enabled:
      params.put_bool("WgpuEnabled", False, block=True)
    params.put_bool("WgpuReady", False, block=True)
    params.remove("WgpuModelName")
    if forward is not None and forward.poll() is None:
      stop_process(forward)
    print("wgpu disabled; local modeld restored")


if __name__ == "__main__":
  signal.signal(signal.SIGTERM, handle_sigterm)
  try:
    main()
  except KeyboardInterrupt:
    pass
