#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path
import re
import sys
from urllib.parse import unquote


SUNNYPILOT_ROOT = Path(__file__).resolve().parents[4]
if (SUNNYPILOT_ROOT / "tools/lib/logreader.py").exists():
  sys.path.insert(0, str(SUNNYPILOT_ROOT))


DEFAULT_ROUTES = """
faa815c21279fef7/00000187--ce36ae7c11
faa815c21279fef7/00000191--e5c3ffb55b
ce8a3764a8bb9141/000000f6--775693a6d6
ce8a3764a8bb9141/00000100--ba8bd692f5
32025f26789d8fab/00000022--a499e8ffa3
1618132d68afc876/00000021--bf0f957649
97ca61196eb73e0d/00000052--4555329470
d54302f1d5e7a7cc/00000656--5dae9f54a7
4267ea8a353cdb36/00000262--8a427003c7
7b8cc7bb46000e53/0000000b--2abacaff78
48c27f77f9fd1a9b/00000199--193ee1ba20
ccfd4a1af758ee73/00000091--7fa49719a5
baf39eeaba1217ca/00000002--b36e3fa031
ac30936e794b297a/00000021--dde25fcfda
c4a804b067623789/0000007c--163f831540
80b8e9a6ad0acec3/0000032d--8379197bd3
80b8e9a6ad0acec3/0000032c--0055eeee96
cdde60a79a049bf4/00000002--f448ca40b4
0d4257d1c6741384/00000067--42230e4b8d
343d5e350abaedcf/00000020--1c864750b6
71e4e67d29034771/00000014--25fc6b216f
71e4e67d29034771/0000000e--d3b19ad6f6
07a48901db7b2503/0000012d--61aba9f832
c5a5f79df9b6a084/0000005d--24c0a7a7ee
90950642f47cf05b/00000681--6a904aaa98
102161de13e822d1/0000000d--f74a52a624
17ef028fec0ccf81/00000010--dba8455015
6b8052042ba3ee05/00000199--3ed3fb5799
464ac801173f6dca/00000382--27ce9e4ade
455a0ab75ce5c1e0/000000d1--098f32028c
6d2092783bf67457/0000008c--5caf525813
4961cb0f7bdd77a2/00000105--b636ed2f65
f9522b6cd6e4e621/00000170--ac6979bdda
ed2717e2c1912f87/00000009--d550f4d5b6
78ad5150de133637/2023-09-13--16-15-57
6e7904b03a4aafc2/00000010--31034184b6
26da1db30eff4fcc/00000061--a60470e363
a6d25e95d936fdc4/000002ed--89d7944c52
6722665fbbf2a644/00000534--4ab7b733c5
477e0b6c352e8bba/0000000e--5e3a5c981c
5868ec006e2bb61e/00000021--7d10df95e8
ce05e32158479f42/000003f4--9543087719
ac27c9808ac91710/00000002--e0aab81e4d
74fbff45aa20fe9e/00000010--6f173d5799
b27d9eafeb61976e/00000233--03a9c0858c
f6324c8fb8b6f68d/00000058--5330471811
e174e1a0b92263ed/00000001--18955a967e
26064e18b24ae44c/00000000--4eb95fc137
4709fe68b0cc9c0a/00000125--ed2a02e7a8
4709fe68b0cc9c0a/0000012b--f29c054b05
ce7eada09318e376/0000000e--0cc3d1c6cc
662bedbf8453b81e/00000124--7dc358f20c
4a975fc1d9e71801/00000005--50d176008a
3e4f79d5bf692518/00000001--f53d01f8e3
3e4f79d5bf692518/00000002--b18171f9a9
810a7ca7cb31ed86/00000001--b6f9cdd134
224d1e774b6acc2e/0000001d--0ae7d5fa70
8f52823c702cb300/00000177--177d1aa6ff
e3ae9e987a2a4e57/0000002b--30a6963e88
7bc0de9da607c543/00000031--4cb0d8aca5
7bc0de9da607c543/00000042--302b371266
bf42073ef09e0af2/00000017--3edc1f8259
833262b0c9e4016a/0000004a--0227a058e3
3cce51ba4cc49950/0000003c--51ebc96f4c
3cce51ba4cc49950/0000003e--d78c337cc5
ad9840558640c31d/0000001a--d6cd4871c2
a468064f19bc0267/00000001--6a0c7d2514
a468064f19bc0267/00000012--1feb5188ec
a468064f19bc0267/00000015--27b5b89e1b
a468064f19bc0267/00000016--31baf70a9f
a468064f19bc0267/00000017--c63c64192b
518f8ad60a03f394/00000016--e0300496c8
"""


def import_logreader():
  for mod_name in ("openpilot.tools.lib.logreader", "tools.lib.logreader"):
    try:
      mod = __import__(mod_name, fromlist=["LogReader"])
      return mod.LogReader, mod.ReadMode
    except ImportError:
      pass

  raise SystemExit(
    "Could not import LogReader. Run this from an openpilot/comma tooling environment, "
    + "or install the package that provides openpilot.tools.lib.logreader."
  )


def normalize_route(route: str) -> str:
  return unquote(route.strip()).replace("|", "/")


def add_segment(route: str, segment: int | None) -> str:
  if segment is None:
    return route

  parts = route.split("/")
  if len(parts) == 2:
    return f"{route}/{segment}"
  return route


def parse_routes(text: str, segment: int | None) -> list[str]:
  oneboxes = re.findall(r"onebox=([^) \t\n\r]+)", text)
  routes = oneboxes if oneboxes else [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]

  deduped = dict.fromkeys(add_segment(normalize_route(route), segment) for route in routes)
  return list(deduped)


def event_time_s(event, start_time_ns: int) -> float:
  return (event.logMonoTime - start_time_ns) / 1e9


def can_messages(event) -> Iterable:
  which = event.which()
  if which == "can":
    return event.can
  if which == "sendcan":
    return event.sendcan
  return ()


def similar_count(count: int, reference: float, tolerance: float) -> bool:
  if reference == 0:
    return count == 0
  return abs(count - reference) / reference <= tolerance


def consecutive_ranges(address_counts: Counter[int], min_len: int, count_tolerance: float) -> Iterator[tuple[int, int]]:
  sorted_addresses = sorted(address_counts)
  if not sorted_addresses:
    return

  start = prev = sorted_addresses[0]
  run_counts = [address_counts[start]]
  for addr in sorted_addresses[1:]:
    reference_count = sum(run_counts) / len(run_counts)
    if addr == prev + 1 and similar_count(address_counts[addr], reference_count, count_tolerance):
      run_counts.append(address_counts[addr])
      prev = addr
      continue

    if prev - start + 1 >= min_len:
      yield start, prev
    start = prev = addr
    run_counts = [address_counts[addr]]

  if prev - start + 1 >= min_len:
    yield start, prev


def parse_buses(buses: str) -> set[int]:
  return {int(bus.strip(), 0) for bus in buses.split(",") if bus.strip()}


def scan_route(LogReader, ReadMode, route: str, skip_s: float, duration_s: float | None,
               include_sendcan: bool, buses: set[int]) -> tuple[dict[int, Counter[int]], float]:
  counts_by_bus: dict[int, Counter[int]] = defaultdict(Counter)
  start_time_ns = None
  end_s = None if duration_s is None else skip_s + duration_s
  last_scanned_t = skip_s

  for event in LogReader(route, default_mode=ReadMode.RLOG):
    if start_time_ns is None:
      start_time_ns = event.logMonoTime

    t = event_time_s(event, start_time_ns)
    if t < skip_s:
      continue
    if end_s is not None and t > end_s:
      break
    last_scanned_t = t

    if event.which() == "sendcan" and not include_sendcan:
      continue

    for msg in can_messages(event):
      if msg.src not in buses:
        continue
      counts_by_bus[msg.src][msg.address] += 1

  return counts_by_bus, max(last_scanned_t - skip_s, 0.0)


def range_freq(counts: Counter[int], start: int, end: int, duration_s: float) -> float:
  if duration_s <= 0:
    return 0.0

  freqs = [counts[addr] / duration_s for addr in range(start, end + 1)]
  return sum(freqs) / len(freqs)


def fmt_addr(addr: int) -> str:
  return f"0x{addr:X}"


def sorted_range_counts(counts: Counter[tuple[int | None, int, int]]) -> list[tuple[tuple[int | None, int, int], int]]:
  return sorted(counts.items(), key=lambda item: (-((item[0][2] - item[0][1]) + 1), -item[1], -1 if item[0][0] is None else item[0][0], item[0][1]))


def print_range(bus: int | None, start: int, end: int, count: int, avg_hz: float, example: str | None = None, bus_label: str | None = None) -> None:
  bus_label = bus_label or ("all buses" if bus is None else f"bus {bus}")
  example_text = "" if example is None else f"  e.g. {example}"
  print(f"{count:>4}x  {bus_label:>8}  {fmt_addr(start)}-{fmt_addr(end)}  len={end - start + 1:<3}  freq={avg_hz:>6.1f} Hz{example_text}", flush=True)


def main() -> None:
  parser = argparse.ArgumentParser(description="Find consecutive CAN address ranges observed after a route warm-up period.")
  parser.add_argument("input", nargs="?", help="Optional route, onebox URL, or file containing onebox URLs/routes. Defaults to the pasted side-quest routes.")
  parser.add_argument("--segment", type=int, default=1, help="Segment to append to route identifiers that do not already include one. Defaults to 1.")
  parser.add_argument("--all-segments", action="store_true", help="Do not append a segment; scan all segments selected by each identifier.")
  parser.add_argument("--skip-s", type=float, default=60.0, help="Seconds to skip from the start of each loaded route/segment.")
  parser.add_argument("--duration-s", type=float, default=None, help="Optional scan duration after --skip-s. Defaults to the rest of the log.")
  parser.add_argument("--min-len", type=int, default=4, help="Minimum consecutive address range length.")
  parser.add_argument("--count-tolerance", type=float, default=0.2, help="Maximum relative message-count difference within a range. Defaults to 0.2.")
  parser.add_argument("--buses", default="0,1,2", help="Comma-separated CAN buses to scan. Defaults to 0,1,2.")
  parser.add_argument("--include-sendcan", action="store_true", help="Include sendcan events in addition to received can events.")
  parser.add_argument("--merge-buses", "--no-bus", action="store_true", help="Merge addresses from all CAN buses before finding ranges.")
  parser.add_argument("--split-summary-buses", action="store_true", help="Keep aggregate summary counts separate per bus.")
  args = parser.parse_args()

  if args.input:
    input_path = Path(args.input)
    text = input_path.read_text() if input_path.exists() else args.input
  else:
    text = DEFAULT_ROUTES
  routes = parse_routes(text, None if args.all_segments else args.segment)
  LogReader, ReadMode = import_logreader()
  buses = parse_buses(args.buses)

  counts: Counter[tuple[int | None, int, int]] = Counter()
  freq_sums: Counter[tuple[int | None, int, int]] = Counter()
  examples: dict[tuple[int | None, int, int], str] = {}
  failed: list[tuple[str, str]] = []

  for idx, route in enumerate(routes, 1):
    print(f"[{idx:>3}/{len(routes)}] scanning {route}", file=sys.stderr, flush=True)
    try:
      counts_by_bus, scanned_duration_s = scan_route(LogReader, ReadMode, route, args.skip_s, args.duration_s, args.include_sendcan, buses)
    except Exception as e:
      failed.append((route, f"{type(e).__name__}: {e}"))
      continue

    if args.merge_buses:
      merged = Counter()
      for address_counts in counts_by_bus.values():
        merged.update(address_counts)
      range_sources = {None: merged}
    else:
      range_sources = counts_by_bus

    route_ranges = set()
    route_freqs = {}
    for bus, address_counts in range_sources.items():
      for start, end in consecutive_ranges(address_counts, args.min_len, args.count_tolerance):
        route_ranges.add((bus, start, end))
        route_freqs[(bus, start, end)] = range_freq(address_counts, start, end, scanned_duration_s)

    per_route_counts: Counter[tuple[int | None, int, int]] = Counter(route_ranges)
    print(f"\n{route}", flush=True)
    for (bus, start, end), route_count in sorted_range_counts(per_route_counts):
      print_range(bus, start, end, route_count, route_freqs[(bus, start, end)])

    for range_key in route_ranges:
      counts[range_key] += 1
      freq_sums[range_key] += route_freqs[range_key]
      examples.setdefault(range_key, route)

  print(f"\nScanned routes: {len(routes) - len(failed)}/{len(routes)}", flush=True)
  print(f"Minimum range length: {args.min_len}", flush=True)
  print(f"Count tolerance: {args.count_tolerance:g}", flush=True)
  print(f"Skipped first: {args.skip_s:g}s", flush=True)
  print(f"Buses: {','.join(str(bus) for bus in sorted(buses))}", flush=True)
  if args.duration_s is not None:
    print(f"Scan duration: {args.duration_s:g}s", flush=True)
  print(flush=True)

  if args.split_summary_buses:
    for (bus, start, end), count in sorted_range_counts(counts):
      avg_hz = freq_sums[(bus, start, end)] / count
      print_range(bus, start, end, count, avg_hz, examples[(bus, start, end)])
  else:
    combined_counts: Counter[tuple[int, int]] = Counter()
    combined_freq_sums: Counter[tuple[int, int]] = Counter()
    combined_examples: dict[tuple[int, int], str] = {}
    combined_buses: dict[tuple[int, int], set[int]] = defaultdict(set)

    for (bus, start, end), count in counts.items():
      range_key = (start, end)
      combined_counts[range_key] += count
      combined_freq_sums[range_key] += freq_sums[(bus, start, end)]
      combined_examples.setdefault(range_key, examples[(bus, start, end)])
      if bus is not None:
        combined_buses[range_key].add(bus)

    sorted_combined = sorted(combined_counts.items(), key=lambda item: (-((item[0][1] - item[0][0]) + 1), -item[1], item[0][0]))
    for (start, end), count in sorted_combined:
      avg_hz = combined_freq_sums[(start, end)] / count
      buses_label = "buses " + ",".join(str(bus) for bus in sorted(combined_buses[(start, end)]))
      print_range(None, start, end, count, avg_hz, combined_examples[(start, end)], bus_label=buses_label)

  if failed:
    print("\nFailed routes:", file=sys.stderr)
    for route, error in failed:
      print(f"  {route}: {error}", file=sys.stderr)


if __name__ == "__main__":
  main()
