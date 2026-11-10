#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Made-up drives for the tests and for a demo preview without a car:

  python -m openpilot.sunnypilot.achievements.simulate /tmp/demo

writes /tmp/demo/preview/map.html for two weeks of a commute from Hilliard to
Fairborn, Ohio, plus two weekend trips.
"""
from __future__ import annotations

import datetime as dt
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from openpilot.sunnypilot.achievements.community import CommunityLog
from openpilot.sunnypilot.achievements.engine import AchievementEngine, Sample, State

HOME = (40.0334, -83.1588)          # Hilliard
WORK = (39.8209, -84.0194)          # Fairborn
SPRINGFIELD = (39.9242, -83.8088)
CINCINNATI = (39.1031, -84.5120)
DAYTON = (39.7589, -84.1916)
CLEVELAND = (41.4993, -81.6944)
MANSFIELD = (40.7584, -82.5154)
COLUMBUS = (39.9612, -82.9988)


@dataclass
class Drive:
  day: dt.date
  route: list[tuple[float, float]]
  start_utc_h: float = 13.0         # 8 am in Ohio
  engaged: bool = True


def _km(a: tuple[float, float], b: tuple[float, float]) -> float:
  la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
  h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
  return 2 * 6371.0 * math.asin(math.sqrt(h))


def drive_samples(drive: Drive, t0: float, speed_ms: float = 30.0):
  """1 Hz samples along straight lines between the route's points."""
  wall = dt.datetime(drive.day.year, drive.day.month, drive.day.day, tzinfo=dt.UTC).timestamp() + drive.start_utc_h * 3600
  t = t0
  for a, b in zip(drive.route, drive.route[1:], strict=False):
    n = max(1, int(_km(a, b) * 1000 / speed_ms))
    for i in range(n):
      f = i / n
      lat, lon = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
      yield Sample(t=t, v_ego=speed_ms, op_active=drive.engaged, lat=lat, lon=lon, wall=wall)
      t += 1.0
      wall += 1.0
  end = drive.route[-1]
  yield Sample(t=t, v_ego=0.0, op_active=False, lat=end[0], lon=end[1], wall=wall)


def run(drives: list[Drive], engine: AchievementEngine, log: CommunityLog, speed_ms: float = 30.0) -> None:
  t = 1000.0
  for d in drives:
    for s in drive_samples(d, t, speed_ms):
      engine.update(s)
      log.update(s, engine.last_step)
      t = s.t
    engine.end_drive()
    log.end_drive(engine.utc_offset_h)
    t += 3600.0


def commute_weeks(first_monday: dt.date, weeks: int = 2) -> list[Drive]:
  drives = []
  for w in range(weeks):
    monday = first_monday + dt.timedelta(weeks=w)
    for i in range(5):
      day = monday + dt.timedelta(days=i)
      drives.append(Drive(day, [HOME, SPRINGFIELD, WORK], 12.5))
      drives.append(Drive(day, [WORK, SPRINGFIELD, HOME], 21.5))
    saturday = monday + dt.timedelta(days=5)
    trip = [HOME, DAYTON, CINCINNATI] if w % 2 == 0 else [HOME, COLUMBUS, MANSFIELD, CLEVELAND]
    drives.append(Drive(saturday, trip, 14.0))
    drives.append(Drive(saturday, list(reversed(trip)), 20.0))
  return drives


def main(out: str) -> None:
  from openpilot.sunnypilot.achievements.community import Settings
  from openpilot.sunnypilot.achievements.preview import write_preview

  root = Path(out)
  root.mkdir(parents=True, exist_ok=True)
  db = root / "community.db"
  if db.exists():
    os.remove(db)
  first_monday = dt.date(2026, 10, 26)
  engine = AchievementEngine(State())
  log = CommunityLog(db)
  run(commute_weeks(first_monday), engine, log)
  today = first_monday + dt.timedelta(days=15)
  path = write_preview(log, engine.state, today, "HYUNDAI_IONIQ_5", Settings(level=0), root / "preview")
  print(f"wrote {path / 'map.html'}")


if __name__ == "__main__":
  main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/achievements_demo")
