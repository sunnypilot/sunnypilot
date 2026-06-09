#!/usr/bin/env python3
import argparse
import concurrent.futures
import os
import signal
import subprocess
import sys
import time
from collections import Counter, defaultdict

import cereal.messaging as messaging
from msgq.ipc_pyx import IpcError
from opendbc.car.tests.routes import CarTestRoute, routes
from openpilot.tools.replay.custom_routes import CUSTOM_ROUTES
from openpilot.tools.replay.radar_helpers import (
  RADAR_SPECS,
  build_seen_address_map,
  get_radar_spec,
  is_exclusive_full_range_match,
)


REPLAY_PATH = os.path.join(os.path.dirname(__file__), "replay")
REPLAY_PLAYBACK_SPEED = "3.0"
REPLAY_ALLOW_SERVICES = "can"
DETECTION_TIMEOUT_SECONDS = 20.0
DETECTION_MIN_HITS = 10
SOCKET_WAIT_TIMEOUT_SECONDS = 10.0
CAR_MODEL_WIDTH = 38
RADAR_TYPE_WIDTH = 10

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"

RADAR_FAMILY_COLORS = {
  "RADAR_500_51F": ANSI_CYAN,
  "RADAR_210_21F": ANSI_YELLOW,
  "RADAR_3A5_3C4": ANSI_GREEN,
  "RADAR_602_611": ANSI_BLUE,
}


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Replay Hyundai/Kia/Genesis test routes and auto-detect radar type.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("--routes", action="store_true",
                      help="Use Hyundai/Kia/Genesis routes from opendbc/car/tests/routes.py.")
  parser.add_argument("--custom-routes", action="store_true",
                      help="Use routes from tools/replay/custom_routes.py.")
  parser.add_argument("--route", action="append", default=[],
                      help="Specific route(s) to test. If omitted, use Hyundai/Kia/Genesis routes from opendbc/car/tests/routes.py.")
  parser.add_argument("--data-dir", default=None,
                      help="Optional local directory of route data to pass through to replay.")
  parser.add_argument("--timeout", type=float, default=DETECTION_TIMEOUT_SECONDS,
                      help="Seconds to wait for a radar-family detection before giving up on a route.")
  parser.add_argument("--min-hits", type=int, default=DETECTION_MIN_HITS,
                      help="Minimum CAN hits in a radar-family address range before considering it detected.")
  parser.add_argument("--playback", default=REPLAY_PLAYBACK_SPEED,
                      help="Replay playback speed.")
  parser.add_argument("--limit", type=int, default=None,
                      help="Only process the first N matching routes.")
  parser.add_argument("--jobs", type=int, default=1,
                      help="Number of routes to process in parallel.")
  parser.add_argument("--prefix", default="auto-radar-detect",
                      help="Base OPENPILOT_PREFIX to isolate replay sockets.")
  return parser


def get_hkg_routes() -> list[CarTestRoute]:
  hkg_prefixes = ("HYUNDAI_", "KIA_", "GENESIS_")
  return [
    route for route in routes
    if route.car_model is not None and getattr(route.car_model, "name", str(route.car_model)).startswith(hkg_prefixes)
  ]


def get_selected_routes(args: argparse.Namespace) -> list[CarTestRoute]:
  selected_sources = int(bool(args.route)) + int(bool(args.routes)) + int(bool(args.custom_routes))
  if selected_sources > 1:
    raise ValueError("Use only one of --route, --routes, or --custom-routes.")

  if args.route:
    route_map = {route.route: route for route in get_hkg_routes()}
    selected = []
    for route_name in args.route:
      selected.append(route_map.get(route_name, CarTestRoute(route_name, None)))
    return selected[:args.limit] if args.limit is not None else selected

  if args.custom_routes:
    selected = [CarTestRoute(route.route, route.car_model) for route in CUSTOM_ROUTES]
    return selected[:args.limit] if args.limit is not None else selected

  selected = get_hkg_routes()
  return selected[:args.limit] if args.limit is not None else selected


def terminate_process(proc: subprocess.Popen) -> None:
  if proc.poll() is not None:
    return

  proc.terminate()
  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait(timeout=5)


def start_replay(route: str, prefix: str, args: argparse.Namespace) -> subprocess.Popen:
  cmd = [
    REPLAY_PATH,
    "--no-vipc",
    "--no-loop",
    "--playback", args.playback,
    "--allow", REPLAY_ALLOW_SERVICES,
    "--prefix", prefix,
  ]
  if args.data_dir:
    cmd.extend(["--data_dir", args.data_dir])
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


def stop_replay(proc: subprocess.Popen) -> None:
  if proc.poll() is not None:
    return

  if os.name != "nt":
    try:
      os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
      return
  else:
    proc.terminate()

  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    if os.name != "nt":
      try:
        os.killpg(proc.pid, signal.SIGKILL)
      except ProcessLookupError:
        return
    else:
      proc.kill()
    proc.wait(timeout=5)


def wait_for_can_socket(prefix: str, timeout: float) -> messaging.SubSocket:
  socket_path = os.path.join("/tmp", f"msgq_{prefix}", "can")
  started = time.monotonic()
  while True:
    if os.path.exists(socket_path):
      break
    if time.monotonic() - started > timeout:
      raise TimeoutError(f"Timed out waiting for CAN socket at {socket_path}")
    time.sleep(0.1)

  while True:
    try:
      return messaging.sub_sock("can", conflate=False, timeout=100)
    except IpcError:
      if time.monotonic() - started > timeout:
        raise
      time.sleep(0.1)


def detect_radar_family(route: CarTestRoute, route_idx: int, args: argparse.Namespace) -> dict:
  prefix = f"{args.prefix}-{os.getpid()}-{route_idx}"
  os.environ["OPENPILOT_PREFIX"] = prefix
  messaging.reset_context()
  proc = start_replay(route.route, prefix, args)
  logcan = wait_for_can_socket(prefix, min(args.timeout, SOCKET_WAIT_TIMEOUT_SECONDS))
  counts = Counter()
  buses = defaultdict(set)
  seen_addresses = build_seen_address_map()
  started = time.monotonic()
  detected = None

  try:
    while True:
      if proc.poll() is not None and (time.monotonic() - started) > 1.0:
        break
      if time.monotonic() - started > args.timeout:
        break

      msgs = messaging.drain_sock(logcan, wait_for_one=True)
      for msg in msgs:
        for can_msg in msg.can:
          radar_spec = get_radar_spec(can_msg.address)
          if radar_spec is not None:
            counts[radar_spec.name] += 1
            buses[radar_spec.name].add(can_msg.src)
            seen_addresses[radar_spec.name].add(can_msg.address)
            if counts[radar_spec.name] >= args.min_hits and is_exclusive_full_range_match(radar_spec, seen_addresses):
              detected = radar_spec.name
          if detected is not None:
            break
        if detected is not None:
          break
      if detected is not None:
        break
  finally:
    stop_replay(proc)

  dominant_family = detected

  return {
    "route": route.route,
    "car_model": str(route.car_model) if route.car_model is not None else "UNKNOWN",
    "detected": dominant_family or "NONE",
    "counts": dict(counts),
    "buses": {name: sorted(bus_set) for name, bus_set in buses.items()},
    "seen_addresses": {name: sorted(addresses) for name, addresses in seen_addresses.items()},
  }


def print_results(results: list[dict]) -> None:
  print(f"{'Car Model':<{CAR_MODEL_WIDTH}}  {'Detected':<{RADAR_TYPE_WIDTH}}  Route")
  print("-" * (CAR_MODEL_WIDTH + RADAR_TYPE_WIDTH + 9 + 60))
  for result in results:
    detected_plain = "" if result["detected"] == "NONE" else result["detected"]
    model = format_car_model(result["car_model"])[:CAR_MODEL_WIDTH]
    detected = f"{detected_plain:<{RADAR_TYPE_WIDTH}}"
    if supports_color() and detected_plain:
      detected = f"{colorize_detected(detected_plain)}" + " " * max(0, RADAR_TYPE_WIDTH - len(detected_plain))
    print(f"{model:<{CAR_MODEL_WIDTH}}  {detected}  {result['route']}")


def supports_color() -> bool:
  return sys.stdout.isatty() and os.getenv("TERM") not in (None, "dumb")


def format_car_model(car_model: object) -> str:
  return str(car_model) if car_model is not None else "UNKNOWN"


def colorize_detected(detected: str) -> str:
  if detected == "NONE":
    return ""

  if not supports_color():
    return detected

  color = RADAR_FAMILY_COLORS.get(detected, ANSI_MAGENTA)
  return f"{color}{detected}{ANSI_RESET}"


def print_progress_line(index: int, total: int, route: CarTestRoute, detected: str) -> None:
  left = f"[{index}/{total}]"
  model = format_car_model(route.car_model)[:CAR_MODEL_WIDTH]
  detected_plain = "" if detected == "NONE" else detected
  route_text = route.route
  if supports_color():
    left = f"{ANSI_DIM}{left}{ANSI_RESET}"
    model = f"{ANSI_CYAN}{model:<{CAR_MODEL_WIDTH}}{ANSI_RESET}"
    detected_text = colorize_detected(detected_plain).ljust(len(colorize_detected(detected_plain)))
    route_text = f"{ANSI_DIM}{route_text}{ANSI_RESET}"
  else:
    model = f"{model:<{CAR_MODEL_WIDTH}}"
    detected_text = detected_plain

  detected_text = f"{detected_plain:<{RADAR_TYPE_WIDTH}}" if not supports_color() else (
    f"{colorize_detected(detected_plain)}" + " " * max(0, RADAR_TYPE_WIDTH - len(detected_plain))
  )

  print(f"{left} {model}  {detected_text}  {route_text}")


def main() -> int:
  args = build_arg_parser().parse_args(sys.argv[1:])
  try:
    selected_routes = get_selected_routes(args)
  except ValueError as e:
    print(str(e), file=sys.stderr)
    return 2
  if not selected_routes:
    print("No matching routes found.", file=sys.stderr)
    return 1

  results = []
  total = len(selected_routes)
  jobs = max(1, min(args.jobs, total))

  header_model = "Car Model"
  header_detected = "Radar"
  if supports_color():
    header_model = f"{ANSI_BOLD}{header_model:<{CAR_MODEL_WIDTH}}{ANSI_RESET}"
    header_detected = f"{ANSI_BOLD}{header_detected:<{RADAR_TYPE_WIDTH}}{ANSI_RESET}"
  else:
    header_model = f"{header_model:<{CAR_MODEL_WIDTH}}"
    header_detected = f"{header_detected:<{RADAR_TYPE_WIDTH}}"
  print(f"     {header_model}  {header_detected}  Route")

  if jobs == 1:
    for idx, route in enumerate(selected_routes):
      result = detect_radar_family(route, idx, args)
      print_progress_line(idx + 1, total, route, result['detected'])
      results.append((idx, result))
  else:
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
      future_to_job = {
        executor.submit(detect_radar_family, route, idx, args): (idx, route)
        for idx, route in enumerate(selected_routes)
      }
      completed = 0
      for future in concurrent.futures.as_completed(future_to_job):
        idx, route = future_to_job[future]
        result = future.result()
        completed += 1
        print_progress_line(completed, total, route, result['detected'])
        results.append((idx, result))

  results = sorted(
    (result for _, result in results),
    key=lambda result: (result["car_model"], result["route"]),
  )

  print()
  print_results(results)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
