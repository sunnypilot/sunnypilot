#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Runs achievements and the privacy filter over the drives already saved on the
car, then writes the dry-run preview. It uses its own folder, so live progress
is not touched, and it sends nothing.

On the car (over SSH):
  cd /data/openpilot && python -m openpilot.sunnypilot.achievements.replay
Then on your computer:
  scp comma@<car ip>:/data/media/0/achievements/replay/preview/map.html .

Reads qlogs from /data/media/0/realdata by default (--rlog for full logs, which
also count lane changes; much slower). Each route counts as one drive.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import re
import shutil
import sys
import time
from pathlib import Path

from openpilot.sunnypilot.achievements.community import CommunityLog, Settings
from openpilot.sunnypilot.achievements.engine import (MAX_GPS_ACCURACY_M, AchievementEngine, Sample, State,
                                                      achievements_root)
from openpilot.sunnypilot.achievements.preview import write_preview

SEGMENT = re.compile(r"^(?P<route>.+)--(?P<seg>\d+)$")
GPS_MAX_AGE_S = 2.0
MIN_VALID_UNIX = 1.6e9  # anything earlier is a clock that wasn't set yet


def _now() -> float:
  return datetime.datetime.now(datetime.UTC).timestamp()


def find_routes(log_root: Path, rlog: bool, days: int | None) -> list[list[Path]]:
  names = ("rlog.zst", "rlog.bz2", "rlog") if rlog else ("qlog.zst", "qlog.bz2", "qlog")
  cutoff = _now() - days * 86400 if days else 0
  routes: dict[str, list[tuple[int, float, Path]]] = collections.defaultdict(list)
  for d in log_root.iterdir():
    m = SEGMENT.match(d.name)
    if not m or not d.is_dir():
      continue
    f = next((d / n for n in names if (d / n).exists()), None)
    if f is None or f.stat().st_mtime < cutoff:
      continue
    routes[m["route"]].append((int(m["seg"]), f.stat().st_mtime, f))
  ordered = sorted(routes.values(), key=lambda segs: min(s[1] for s in segs))
  return [[f for _, _, f in sorted(segs)] for segs in ordered]


class RouteFeeder:
  """Turns one route's log messages into Samples, the way achievementsd does live."""

  def __init__(self, engine: AchievementEngine, log: CommunityLog):
    self.engine, self.log = engine, log
    self.op_active = self.mads_active = False
    self.lane_change = self.dm_alert = 0
    self.gps: tuple[float, float, int] | None = None
    self.clock: tuple[int, float] | None = None  # (logMonoTime, unix seconds)
    self.car: str | None = None
    self.samples = 0

  def feed(self, ev) -> None:
    w = ev.which()
    if w == "carState":
      self._sample(ev.logMonoTime, ev.carState.vEgo)
    elif w == "selfdriveState":
      self.op_active = ev.selfdriveState.active
    elif w == "selfdriveStateSP":
      self.mads_active = ev.selfdriveStateSP.mads.active
    elif w == "modelV2":
      self.lane_change = ev.modelV2.meta.laneChangeState.raw
    elif w == "driverMonitoringState":
      self.dm_alert = ev.driverMonitoringState.alertLevel.raw
    elif w in ("gpsLocationExternal", "gpsLocation"):
      g = getattr(ev, w)
      if g.hasFix and 0 < g.horizontalAccuracy < MAX_GPS_ACCURACY_M:
        self.gps = (g.latitude, g.longitude, ev.logMonoTime)
        if g.unixTimestampMillis / 1000.0 > MIN_VALID_UNIX:
          self.clock = (ev.logMonoTime, g.unixTimestampMillis / 1000.0)
    elif w == "initData" and self.clock is None:
      if ev.initData.wallTimeNanos / 1e9 > MIN_VALID_UNIX:
        self.clock = (ev.logMonoTime, ev.initData.wallTimeNanos / 1e9)
    elif w == "carParams" and not self.car:
      self.car = ev.carParams.carFingerprint or None

  def _sample(self, mono: int, v_ego: float) -> None:
    fix = self.gps if self.gps and (mono - self.gps[2]) / 1e9 < GPS_MAX_AGE_S else None
    wall = self.clock[1] + (mono - self.clock[0]) / 1e9 if self.clock else None
    s = Sample(t=mono / 1e9, v_ego=v_ego, op_active=self.op_active, mads_active=self.mads_active,
               lane_change_state=self.lane_change, dm_alert_level=self.dm_alert,
               lat=fix[0] if fix else None, lon=fix[1] if fix else None, wall=wall)
    self.engine.update(s)
    self.log.update(s, self.engine.last_step)
    self.samples += 1


def main(argv: list[str] | None = None) -> int:
  from openpilot.common.hardware.hw import Paths
  from openpilot.tools.lib.logreader import LogReader

  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("--logs", type=Path, default=Path(Paths.log_root()), help="folder with route segments")
  ap.add_argument("--out", type=Path, default=achievements_root() / "replay", help="where to write (wiped first)")
  ap.add_argument("--days", type=int, default=None, help="only routes from the last N days")
  ap.add_argument("--rlog", action="store_true", help="read full rlogs instead of qlogs")
  args = ap.parse_args(argv)

  routes = find_routes(args.logs, args.rlog, args.days)
  if not routes:
    print(f"no {'rlogs' if args.rlog else 'qlogs'} found in {args.logs}")
    return 1
  if args.out.exists():
    shutil.rmtree(args.out)
  args.out.mkdir(parents=True)

  engine = AchievementEngine(State())
  log = CommunityLog(args.out / "community.db")
  car = None
  n_segs = sum(len(r) for r in routes)
  done = 0
  start = time.monotonic()
  for segments in routes:
    feeder = RouteFeeder(engine, log)
    for path in segments:
      try:
        for ev in LogReader(str(path), sort_by_time=True):
          feeder.feed(ev)
      except Exception as e:  # one bad segment shouldn't stop the rest
        print(f"skipping {path}: {e}", file=sys.stderr)
      done += 1
      print(f"\r{done}/{n_segs} segments", end="", file=sys.stderr, flush=True)
    engine.end_drive()
    log.end_drive(engine.utc_offset_h)
    car = feeder.car or car
  print(file=sys.stderr)

  today = engine.local_date(_now())
  out = write_preview(log, engine.state, today, car, Settings.load(), args.out / "preview")
  view = log.tile_view(today)
  print(f"{len(routes)} drives, {n_segs} segments in {time.monotonic() - start:.0f} s")
  print(f"engaged: {engine.state.engaged_m / 1609.344:.0f} mi over {len(engine.state.days)} days")
  kept = len(view.ring & view.driven)
  print(f"tiles: {len(view.driven)} driven, {len(view.shareable)} would be shared, {len(view.held)} waiting, {kept} kept on the car")
  print(f"frequent stops (never sent, with the tiles around them): {len(view.frequent)}")
  print(f"home region: {log.home_region(today)}")
  print(f"preview: {out / 'map.html'}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
