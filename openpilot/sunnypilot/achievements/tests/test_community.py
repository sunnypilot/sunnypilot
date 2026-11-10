"""
The privacy filter, on made-up drives: two weeks of a Hilliard -> Fairborn
commute plus two Saturday trips (see simulate.py).
"""
import datetime as dt
import re
import sqlite3

import pytest

from openpilot.sunnypilot.achievements import h3lite
from openpilot.sunnypilot.achievements.community import (LEVEL_ACHIEVEMENTS, LEVEL_DAILY, LEVEL_MAP, LEVEL_OFF,
                                                         CommunityLog, Settings, public_block, ring_of, tile_of)
from openpilot.sunnypilot.achievements.engine import AchievementEngine, State
from openpilot.sunnypilot.achievements.preview import build_preview, write_preview
from openpilot.sunnypilot.achievements.regions import table
from openpilot.sunnypilot.achievements.simulate import (CINCINNATI, CLEVELAND, HOME, WORK, Drive, commute_weeks,
                                                        run)

FIRST_MONDAY = dt.date(2026, 10, 26)
TODAY = FIRST_MONDAY + dt.timedelta(days=15)  # Tuesday after the second week
HEX = re.compile(r"^86[0-9a-f]{13}$")


@pytest.fixture(scope="module")
def world(tmp_path_factory):
  engine = AchievementEngine(State())
  log = CommunityLog(tmp_path_factory.mktemp("community") / "community.db")
  run(commute_weeks(FIRST_MONDAY), engine, log, speed_ms=60.0)
  return engine, log


def test_home_and_work_never_leave(world):
  _, log = world
  view = log.tile_view(TODAY)
  home, work = tile_of(*HOME), tile_of(*WORK)
  assert view.frequent == {home, work}
  assert ring_of(home) | ring_of(work) <= view.ring
  assert len(ring_of(home)) == 7
  assert not view.shareable & view.ring
  batch = log.tile_batch(TODAY)
  assert not set(batch["tiles"]) & view.ring


def test_trip_ends_wait_14_days(world):
  _, log = world
  cincinnati = tile_of(*CINCINNATI)  # Saturday Oct 31
  cleveland = tile_of(*CLEVELAND)    # Saturday Nov 7
  view = log.tile_view(TODAY)
  assert view.held == {cincinnati: "2026-11-14", cleveland: "2026-11-21"}
  assert cincinnati not in view.shareable

  later = log.tile_view(dt.date(2026, 11, 14))
  assert cincinnati in later.shareable
  assert cleveland in later.held


def test_tile_batch_has_no_dates(world):
  _, log = world
  batch = log.tile_batch(TODAY)
  assert set(batch) == {"v", "device", "tiles"}
  assert batch["tiles"] == sorted(batch["tiles"])
  assert all(HEX.match(t) for t in batch["tiles"])
  assert len(batch["tiles"]) == len(log.tile_view(TODAY).shareable)


def test_nothing_finer_than_a_tile_is_stored(world):
  _, log = world
  db = sqlite3.connect(log.path)
  assert all(HEX.match(c) for (c,) in db.execute("SELECT cell FROM tiles UNION SELECT cell FROM stops"))
  days = {d for (d,) in db.execute("SELECT first_day FROM tiles UNION SELECT day FROM stops UNION SELECT day FROM days")}
  assert all(re.fullmatch(r"\d{4}-\d\d-\d\d", d) for d in days)


def test_others_see_45km_blocks(world):
  _, log = world
  data = build_preview(log, world[0].state, TODAY, None, Settings())
  shareable = log.tile_view(TODAY).shareable
  assert set(data["map"]["blocks"]) == {public_block(t) for t in shareable}
  assert all(h3lite.get_resolution(h3lite.str_to_cell(b)) == 4 for b in data["map"]["blocks"])
  # the commute fills in the blocks around home and work, so no hole points at them
  home_block, work_block = public_block(tile_of(*HOME)), public_block(tile_of(*WORK))
  assert {home_block, work_block} <= set(data["map"]["blocks"])


def test_daily_report_levels(world):
  engine, log = world
  day = "2026-11-06"
  assert log.daily_report(day, engine.state, LEVEL_OFF) is None

  r1 = log.daily_report(day, engine.state, LEVEL_ACHIEVEMENTS)
  assert set(r1) == {"v", "device", "day", "unlocks", "totals"}
  assert r1["totals"]["engaged_mi"] % 10 == 0 and r1["totals"]["engaged_h"] % 10 == 0

  r2 = log.daily_report(day, engine.state, LEVEL_DAILY, profile={"region": "US-OH"})
  assert set(r2) == {"v", "device", "day", "unlocks", "totals", "daily", "profile"}
  assert set(r2["daily"]) == {"engaged_mi", "engaged_min", "new_places"}
  assert all(isinstance(v, int) for v in r2["daily"].values())
  assert 80 < r2["daily"]["engaged_mi"] < 110  # two ~47 mile legs
  assert LEVEL_MAP > LEVEL_DAILY


def test_unlocks_go_in_the_report_for_their_day(world):
  engine, log = world
  days = {}
  for uid in engine.state.unlocked:
    for day in log.driven_days():
      if any(u["id"] == uid for u in log.daily_report(day, engine.state, LEVEL_ACHIEVEMENTS)["unlocks"]):
        days.setdefault(uid, []).append(day)
  assert days and all(len(v) == 1 for v in days.values())


def test_home_region(world):
  _, log = world
  assert log.home_region(TODAY) == "US-OH"
  assert log.shared_region(TODAY, Settings(region="country")) == "US"
  assert log.shared_region(TODAY, Settings(region="hidden")) is None
  assert log.shared_region(TODAY, Settings(region="US-KY")) == "US-KY"


def test_profile_only_when_changed(tmp_path):
  engine, log = AchievementEngine(State()), CommunityLog(tmp_path / "c.db")
  run([Drive(dt.date(2026, 11, 2), [HOME, WORK])], engine, log, speed_ms=60.0)
  today = dt.date(2026, 11, 3)
  auto = Settings()
  first = log.profile_update(today, "HYUNDAI_IONIQ_5", auto)
  assert first == {"car": "HYUNDAI_IONIQ_5", "region": "US-OH"}
  log.mark_profile_sent(today, first, auto)
  assert log.profile_update(today, "HYUNDAI_IONIQ_5", auto) is None

  # a road trip that moves the automatic home region waits 30 days after the last send
  for i in range(3):
    run([Drive(dt.date(2026, 11, 4 + i), [CINCINNATI, (38.25, -85.76)])], engine, log, speed_ms=60.0)  # into Kentucky
  assert log.home_region(dt.date(2026, 11, 7)) != "US-OH"
  assert log.profile_update(dt.date(2026, 11, 7), "HYUNDAI_IONIQ_5", auto) is None
  assert "region" in log.profile_update(dt.date(2026, 12, 3), "HYUNDAI_IONIQ_5", auto)
  # a region the driver picks goes right away; hiding sends an empty region
  assert log.profile_update(today, "HYUNDAI_IONIQ_5", Settings(region="US-MI")) == {"region": "US-MI"}
  assert log.profile_update(today, "HYUNDAI_IONIQ_5", Settings(region="hidden")) == {"region": None}


def test_late_catches_and_hidden_tiles_are_deleted(tmp_path):
  engine, log = AchievementEngine(State()), CommunityLog(tmp_path / "c.db")
  friend = (39.95, -82.85)  # east Columbus
  run([Drive(dt.date(2026, 10, 1), [HOME, friend])], engine, log, speed_ms=60.0)
  today = dt.date(2026, 10, 20)
  view = log.tile_view(today)
  assert tile_of(*friend) in view.shareable  # one visit, held 14 days, then shared
  log.mark_sent(view.to_send)
  assert log.tile_batch(today) is None

  # three more days ending there: it's a regular stop now, so ask the server to delete it
  run([Drive(dt.date(2026, 10, 21 + i), [HOME, friend]) for i in range(3)], engine, log, speed_ms=60.0)
  deletes = log.tile_deletes(dt.date(2026, 10, 25))
  assert tile_of(*friend) in deletes["delete_tiles"]
  assert set(deletes["delete_tiles"]) <= ring_of(tile_of(*friend)) | ring_of(tile_of(*HOME))

  middle = sorted(log.tile_view(dt.date(2026, 10, 25)).shareable)[0]
  log.hide_tile(middle)
  view = log.tile_view(dt.date(2026, 10, 25))
  assert middle not in view.shareable and middle in view.to_delete


def test_no_gps_no_tiles(tmp_path):
  engine, log = AchievementEngine(State()), CommunityLog(tmp_path / "c.db")
  drive = Drive(dt.date(2026, 11, 2), [HOME, WORK])
  from openpilot.sunnypilot.achievements.simulate import drive_samples
  for s in drive_samples(drive, 0.0, 60.0):
    s.lat = s.lon = None
    engine.update(s)
    log.update(s, engine.last_step)
  log.end_drive()
  assert log.tile_view(dt.date(2026, 11, 3)).driven == set()
  m, secs, _ = log.day_stats("2026-11-02")
  assert m > 50_000 and secs > 0  # engaged miles still count


def test_write_preview(world, tmp_path):
  engine, log = world
  out = write_preview(log, engine.state, TODAY, "HYUNDAI_IONIQ_5", Settings(), tmp_path / "preview")
  names = sorted(p.name for p in out.iterdir())
  assert "map.html" in names and "tiles.json" in names
  assert "daily-2026-11-07.json" in names
  html = (out / "map.html").read_text()
  assert "What your car would share" in html and tile_of(*HOME) in html


def test_region_table():
  t = table()
  assert t.lookup(*HOME) == "US-OH"
  assert t.lookup(43.65, -79.38) == "CA-ON"     # Toronto
  assert t.lookup(40.76, -73.98) == "US-NY"     # Manhattan, next to New Jersey
  assert t.lookup(38.90, -77.04) == "US-DC"
  assert t.lookup(51.50, -0.12) == "GB"         # countries without subdivisions in the table
  assert t.lookup(35.0, -40.0) is None          # mid-Atlantic
