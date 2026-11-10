"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The community log and the privacy filter.

While driving, achievementsd hands every sample to CommunityLog, which keeps in
community.db on the car:
- the 6 km map tiles (H3 resolution 6) you drove through, with the day each was
  first seen,
- the tile where each drive started and ended, per day,
- engaged distance and time per day,
- engaged distance per region per day.
Positions only ever become tiles: no coordinates, times of day or routes are
stored here.

The privacy filter (tile_view, daily_report, tile_batch, profile_update) then
decides what could leave the car, following the Privacy spec in the build plan:
- A tile holding a drive's start or end on 3+ different days is a frequent stop
  (home, work, school). It and the 6 tiles around it never leave the car.
- Any other start or end tile waits 14 days.
- Tiles the driver hid never leave the car.
- Tiles go out as a sorted list with no dates, apart from the daily report.
- The home region is where you drove most on most days over 90 days. It is sent
  only when it changes, and an automatic change at most every 30 days.

Nothing in this file sends anything.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from openpilot.sunnypilot.achievements import h3lite
from openpilot.sunnypilot.achievements.engine import Sample, State, Step, achievements_root
from openpilot.sunnypilot.achievements.regions import RegionTable, country_of
from openpilot.sunnypilot.achievements.regions import table as region_table

REPORT_VERSION = 1
TILE_RES = 6                 # about 6 km across; only the owner sees these
PUBLIC_RES = 4               # about 45 km across; what crews and the public see
STOP_HOLD_DAYS = 14
FREQUENT_STOP_DAYS = 3
REGION_WINDOW_DAYS = 90
REGION_RESEND_DAYS = 30
MOVING_MS = 1.0
METERS_PER_MILE = 1609.344
UNLINKED_DEVICE = "c_" + "0" * 16  # the real id comes from the community key made at linking

LEVEL_OFF, LEVEL_ACHIEVEMENTS, LEVEL_DAILY, LEVEL_MAP = range(4)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tiles (cell TEXT PRIMARY KEY, first_day TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS stops (cell TEXT NOT NULL, day TEXT NOT NULL, PRIMARY KEY (cell, day));
CREATE TABLE IF NOT EXISTS days (day TEXT PRIMARY KEY, engaged_m REAL NOT NULL, engaged_s REAL NOT NULL);
CREATE TABLE IF NOT EXISTS day_regions (day TEXT NOT NULL, region TEXT NOT NULL, engaged_m REAL NOT NULL,
                                        PRIMARY KEY (day, region));
CREATE TABLE IF NOT EXISTS hidden (cell TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def db_path() -> Path:
  return achievements_root() / "community.db"


def settings_path() -> Path:
  return achievements_root() / "community_settings.json"


@dataclass
class Settings:
  level: int = LEVEL_OFF   # 0 off (default), 1 achievements, 2 daily stats, 3 map
  region: str = "auto"     # "auto", "country", "hidden", or a region code the driver picked

  @classmethod
  def load(cls, path: Path | None = None) -> Settings:
    try:
      with open(path or settings_path()) as f:
        d = json.load(f)
      return cls(level=int(d.get("level", LEVEL_OFF)), region=str(d.get("region", "auto")))
    except (OSError, ValueError, TypeError, AttributeError):
      return cls()


def round_to(x: float, step: int) -> int:
  return int(round(x / step)) * step


def tile_of(lat: float, lon: float) -> str:
  return h3lite.cell_to_str(h3lite.latlng_to_cell(lat, lon, TILE_RES))


def ring_of(tile: str) -> set[str]:
  """The tile and the tiles touching it: an area about 18 km across."""
  return {h3lite.cell_to_str(c) for c in h3lite.grid_disk1(h3lite.str_to_cell(tile))}


def public_block(tile: str) -> str:
  return h3lite.cell_to_str(h3lite.cell_to_parent(h3lite.str_to_cell(tile), PUBLIC_RES))


@dataclass
class TileView:
  """Every driven tile, sorted by what the privacy filter does with it."""
  driven: set[str] = field(default_factory=set)
  frequent: set[str] = field(default_factory=set)     # home, work, school...
  ring: set[str] = field(default_factory=set)         # frequent stops and the tiles around them: never sent
  held: dict[str, str] = field(default_factory=dict)  # recent stop tile -> first day it may be sent
  hidden: set[str] = field(default_factory=set)
  shareable: set[str] = field(default_factory=set)
  sent: set[str] = field(default_factory=set)

  @property
  def to_send(self) -> set[str]:
    return self.shareable - self.sent

  @property
  def to_delete(self) -> set[str]:
    """Tiles already sent that later became private (moved house, new job, hidden)."""
    return self.sent & (self.ring | self.hidden)


class CommunityLog:
  def __init__(self, path: Path | None = None, regions: RegionTable | None = None):
    self.path = path or db_path()
    self.path.parent.mkdir(parents=True, exist_ok=True)
    self.db = sqlite3.connect(self.path)
    self.db.executescript(SCHEMA)
    self._regions = regions
    self._known: set[str] = {r[0] for r in self.db.execute("SELECT cell FROM tiles")}
    self._region_of: dict[str, str | None] = {}
    self._utc_offset_h: float | None = None
    self._reset_pending()
    self._reset_drive()

  def close(self) -> None:
    self.db.close()

  @property
  def regions(self) -> RegionTable:
    if self._regions is None:
      self._regions = region_table()
    return self._regions

  def _reset_pending(self) -> None:
    self._new_tiles: dict[str, str] = {}
    self._stops: set[tuple[str, str]] = set()
    self._days: dict[str, list[float]] = collections.defaultdict(lambda: [0.0, 0.0])
    self._day_regions: dict[tuple[str, str], float] = collections.defaultdict(float)

  def _reset_drive(self) -> None:
    self._started = False
    self._last_fix: tuple[str, str] | None = None

  # --- while driving ---

  def update(self, s: Sample, step: Step) -> None:
    day = step.day
    if day is None:
      return
    if s.engaged and step.dt_s > 0.0:
      d = self._days[day]
      d[0] += step.engaged_m
      d[1] += step.dt_s

    if s.lat is None or s.lon is None:
      return
    tile = tile_of(s.lat, s.lon)
    if not self._started:
      self._started = True
      self._stops.add((tile, day))
    self._last_fix = (tile, day)

    if s.v_ego > MOVING_MS and tile not in self._known and tile not in self._new_tiles:
      self._new_tiles[tile] = day

    if step.engaged_m > 0.0:
      if tile not in self._region_of:
        self._region_of[tile] = self.regions.lookup_cell(h3lite.str_to_cell(tile))
      region = self._region_of[tile]
      if region is not None:
        self._day_regions[(day, region)] += step.engaged_m

  def end_drive(self, utc_offset_h: float | None = None) -> None:
    """Record where the drive ended and save. Safe to call more than once."""
    if self._last_fix is not None:
      self._stops.add(self._last_fix)
    if utc_offset_h is not None:
      self._utc_offset_h = utc_offset_h
    self._reset_drive()
    self.flush()

  def flush(self) -> None:
    with self.db:
      self.db.executemany("INSERT OR IGNORE INTO tiles (cell, first_day) VALUES (?, ?)", self._new_tiles.items())
      self.db.executemany("INSERT OR IGNORE INTO stops (cell, day) VALUES (?, ?)", self._stops)
      self.db.executemany("""INSERT INTO days (day, engaged_m, engaged_s) VALUES (?, ?, ?)
                             ON CONFLICT(day) DO UPDATE SET engaged_m = engaged_m + excluded.engaged_m,
                                                            engaged_s = engaged_s + excluded.engaged_s""",
                          [(day, m, s) for day, (m, s) in self._days.items()])
      self.db.executemany("""INSERT INTO day_regions (day, region, engaged_m) VALUES (?, ?, ?)
                             ON CONFLICT(day, region) DO UPDATE SET engaged_m = engaged_m + excluded.engaged_m""",
                          [(day, region, m) for (day, region), m in self._day_regions.items()])
      if self._utc_offset_h is not None:
        self._set_meta("utc_offset_h", self._utc_offset_h)
    self._known.update(self._new_tiles)
    self._reset_pending()

  # --- settings kept with the data ---

  def _get_meta(self, key: str, default=None):
    row = self.db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return json.loads(row[0]) if row else default

  def _set_meta(self, key: str, value) -> None:
    self.db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, json.dumps(value)))

  def hide_tile(self, tile: str) -> None:
    with self.db:
      self.db.execute("INSERT OR IGNORE INTO hidden (cell) VALUES (?)", (tile,))

  def unhide_tile(self, tile: str) -> None:
    with self.db:
      self.db.execute("DELETE FROM hidden WHERE cell = ?", (tile,))

  def mark_sent(self, tiles: set[str], sent: bool = True) -> None:
    """For the uploader: tiles the server now has (or, with sent=False, has deleted)."""
    with self.db:
      self.db.executemany("UPDATE tiles SET sent = ? WHERE cell = ?", [(int(sent), t) for t in tiles])

  # --- the privacy filter ---

  def tile_view(self, today: dt.date) -> TileView:
    v = TileView()
    for cell, sent in self.db.execute("SELECT cell, sent FROM tiles"):
      v.driven.add(cell)
      if sent:
        v.sent.add(cell)

    stop_days: dict[str, set[str]] = collections.defaultdict(set)
    for cell, day in self.db.execute("SELECT cell, day FROM stops"):
      stop_days[cell].add(day)
    v.frequent = {c for c, days in stop_days.items() if len(days) >= FREQUENT_STOP_DAYS}
    for c in v.frequent:
      v.ring |= ring_of(c)
    for c, days in stop_days.items():
      if c in v.ring:
        continue
      release = dt.date.fromisoformat(max(days)) + dt.timedelta(days=STOP_HOLD_DAYS)
      if release > today:
        v.held[c] = release.isoformat()

    v.hidden = {r[0] for r in self.db.execute("SELECT cell FROM hidden")}
    v.shareable = v.driven - v.ring - set(v.held) - v.hidden
    return v

  def driven_days(self, since: dt.date | None = None) -> list[str]:
    rows = self.db.execute("SELECT day FROM days WHERE day >= ? ORDER BY day", ((since or dt.date.min).isoformat(),))
    return [r[0] for r in rows]

  def day_stats(self, day: str) -> tuple[float, float, int]:
    """Engaged meters, engaged seconds and new tiles on a day."""
    row = self.db.execute("SELECT engaged_m, engaged_s FROM days WHERE day = ?", (day,)).fetchone()
    new = self.db.execute("SELECT COUNT(*) FROM tiles WHERE first_day = ?", (day,)).fetchone()[0]
    return (row[0], row[1], new) if row else (0.0, 0.0, new)

  def region_days(self, today: dt.date) -> collections.Counter:
    """How many of the last 90 days each region was where you drove most, engaged."""
    since = (today - dt.timedelta(days=REGION_WINDOW_DAYS)).isoformat()
    best: dict[str, tuple[float, str]] = {}
    for day, region, m in self.db.execute("SELECT day, region, engaged_m FROM day_regions WHERE day > ? ORDER BY region",
                                          (since,)):
      if day not in best or m > best[day][0]:
        best[day] = (m, region)
    return collections.Counter(region for _, region in best.values())

  def home_region(self, today: dt.date) -> str | None:
    tally = self.region_days(today)
    if not tally:
      return None
    return max(sorted(tally), key=lambda r: tally[r])

  def shared_region(self, today: dt.date, settings: Settings) -> str | None:
    if settings.region == "hidden":
      return None
    if settings.region not in ("auto", "country"):
      return settings.region
    home = self.home_region(today)
    if home is None:
      return None
    return country_of(home) if settings.region == "country" else home

  def profile_update(self, today: dt.date, car: str | None, settings: Settings) -> dict | None:
    """Car model and home region, only when they changed since they were last sent."""
    last = self._get_meta("profile_sent", {})
    out: dict = {}
    if car and car != last.get("car"):
      out["car"] = car
    region = self.shared_region(today, settings)
    if region != last.get("region") and (region is not None or "region" in last):
      # the driver changing the setting goes right away; a change the car detected waits
      chosen = settings.region != last.get("choice", "auto")
      last_day = last.get("region_day")
      if chosen or last_day is None or (today - dt.date.fromisoformat(last_day)).days >= REGION_RESEND_DAYS:
        out["region"] = region
    return out or None

  def mark_profile_sent(self, today: dt.date, profile: dict, settings: Settings) -> None:
    last = self._get_meta("profile_sent", {})
    if "car" in profile:
      last["car"] = profile["car"]
    if "region" in profile:
      last["region"] = profile["region"]
      last["region_day"] = today.isoformat()
      last["choice"] = settings.region
    with self.db:
      self._set_meta("profile_sent", last)

  # --- uploads ---

  def unlock_day(self, unix: float) -> str | None:
    if not unix:
      return None  # unlocked before the clock was valid
    offset = self._utc_offset_h if self._utc_offset_h is not None else self._get_meta("utc_offset_h", 0)
    return (dt.datetime.fromtimestamp(unix, dt.UTC) + dt.timedelta(hours=offset)).date().isoformat()

  def daily_report(self, day: str, state: State, level: int, profile: dict | None = None,
                   include_undated: bool = False, device: str = UNLINKED_DEVICE) -> dict | None:
    """The daily report for one day, with only the parts the sharing level allows."""
    if level < LEVEL_ACHIEVEMENTS:
      return None
    unlocks = []
    for uid, unix in sorted(state.unlocked.items()):
      d = self.unlock_day(unix)
      if d == day or (d is None and include_undated):
        unlocks.append({"id": uid, "day": day})
    report: dict = {
      "v": REPORT_VERSION,
      "device": device,
      "day": day,
      "unlocks": unlocks,
      "totals": {"engaged_mi": round_to(state.engaged_m / METERS_PER_MILE, 10),
                 "engaged_h": round_to(state.engaged_s / 3600.0, 10)},
    }
    if level >= LEVEL_DAILY:
      m, s, new = self.day_stats(day)
      report["daily"] = {"engaged_mi": round(m / METERS_PER_MILE), "engaged_min": round(s / 60.0), "new_places": new}
      if profile:
        report["profile"] = profile
    return report

  def tile_batch(self, today: dt.date, device: str = UNLINKED_DEVICE) -> dict | None:
    """The weekly tile batch: new shareable tiles, sorted, with no dates."""
    tiles = self.tile_view(today).to_send
    if not tiles:
      return None
    return {"v": REPORT_VERSION, "device": device, "tiles": sorted(tiles)}

  def tile_deletes(self, today: dt.date, device: str = UNLINKED_DEVICE) -> dict | None:
    tiles = self.tile_view(today).to_delete
    if not tiles:
      return None
    return {"v": REPORT_VERSION, "device": device, "delete_tiles": sorted(tiles)}
