"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The achievements engine: running totals and unlocks, fed one Sample at a time.

Pure Python with no cereal or Params imports, so it can be tested and replayed
anywhere. achievementsd turns live messages into Samples; the UI only reads the
saved state file.

Everything stays on the device. Explorer areas are stored as salted hashes of
~5 km geohash cells, never as coordinates.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import secrets
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from openpilot.sunnypilot.achievements.catalog import Catalog, load_catalog

STATE_VERSION = 1

# plausibility limits for a single update
MAX_DT_S = 1.0          # a longer gap (process stall, suspend) counts nothing
MAX_SPEED_MS = 70.0     # ~250 km/h; above this the reading is not trusted
MIN_SPEED_MS = 0.0

# GPS
GEOHASH_PRECISION = 5   # cells of about 4.9 x 4.9 km
MAX_GPS_ACCURACY_M = 100.0
MODEL_KM_GOAL = 50.0    # Model Hopper: km on a model before it counts

# driver monitoring alertLevel.three is the red, take-control-now alert
DM_ALERT_RED = 3

# modelV2.meta.laneChangeState
LANE_CHANGE_STARTING = 2
LANE_CHANGE_FINISHING = 3

_GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def achievements_root() -> Path:
  """/data/media/0/achievements on the device (survives updates), ~/.comma/... on PC."""
  if "ACHIEVEMENTS_ROOT" in os.environ:
    return Path(os.environ["ACHIEVEMENTS_ROOT"])
  if os.path.isfile("/TICI"):
    return Path("/data/media/0/achievements")
  return Path.home() / (".comma" + os.environ.get("OPENPILOT_PREFIX", "")) / "media" / "0" / "achievements"


def state_path() -> Path:
  return achievements_root() / "state.json"


def seen_path() -> Path:
  """Unlocks the driver has already looked at. Written only by the UI."""
  return achievements_root() / "seen.json"


def geohash(lat: float, lon: float, precision: int = GEOHASH_PRECISION) -> str:
  lat_rng, lon_rng = [-90.0, 90.0], [-180.0, 180.0]
  bits, bit, ch, even = [16, 8, 4, 2, 1], 0, 0, True
  out = []
  while len(out) < precision:
    rng, val = (lon_rng, lon) if even else (lat_rng, lat)
    mid = (rng[0] + rng[1]) / 2
    if val >= mid:
      ch |= bits[bit]
      rng[0] = mid
    else:
      rng[1] = mid
    even = not even
    if bit < 4:
      bit += 1
    else:
      out.append(_GEOHASH_BASE32[ch])
      bit, ch = 0, 0
  return "".join(out)


def season(day: dt.date, southern: bool = False) -> str:
  s = ("winter", "winter", "spring", "spring", "spring", "summer", "summer", "summer", "fall", "fall", "fall", "winter")[day.month - 1]
  if southern:
    s = {"winter": "summer", "summer": "winter", "spring": "fall", "fall": "spring"}[s]
  return s


@dataclass
class Sample:
  """One reading of the car, built by achievementsd from cereal."""
  t: float                        # monotonic seconds, for time between samples
  v_ego: float                    # m/s
  op_active: bool                 # selfdriveState.active (sunnypilot driving, incl. driver override)
  mads_active: bool = False       # selfdriveStateSP.mads.active (lateral)
  lane_change_state: int = 0      # modelV2.meta.laneChangeState
  dm_alert_level: int = 0         # driverMonitoringState.alertLevel
  lat: float | None = None        # only when a good fix is present
  lon: float | None = None
  model_ref: str = ""
  model_name: str = ""
  dev_build: bool = False
  wall: float | None = None       # unix time; None until the device clock is valid

  @property
  def engaged(self) -> bool:
    return self.op_active or self.mads_active

  @property
  def mads_only(self) -> bool:
    return self.mads_active and not self.op_active


@dataclass
class State:
  version: int = STATE_VERSION
  salt: str = field(default_factory=lambda: secrets.token_hex(16))
  engaged_m: float = 0.0
  engaged_s: float = 0.0
  mads_m: float = 0.0
  dev_m: float = 0.0
  lane_changes: int = 0
  days: list[str] = field(default_factory=list)        # ISO dates with engaged driving, sorted
  best_streak_days: int = 0
  today: str = ""
  today_m: float = 0.0
  best_day_m: float = 0.0
  areas: list[str] = field(default_factory=list)       # salted hashes of geohash cells, sorted
  model_m: dict[str, float] = field(default_factory=dict)
  model_names: dict[str, str] = field(default_factory=dict)
  attentive_run_s: float = 0.0
  attentive_best_s: float = 0.0
  seasons: list[str] = field(default_factory=list)
  sunnylink_linked: bool = False
  unlocked: dict[str, float] = field(default_factory=dict)  # unlock id -> unix time

  @classmethod
  def from_dict(cls, d: dict) -> State:
    known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
    return cls(**known)

  def metrics(self) -> dict[str, float]:
    return {
      "engaged_km": self.engaged_m / 1000.0,
      "engaged_h": self.engaged_s / 3600.0,
      "active_days": float(len(self.days)),
      "best_streak_days": float(self.best_streak_days),
      "mads_km": self.mads_m / 1000.0,
      "lane_changes": float(self.lane_changes),
      "best_day_km": max(self.best_day_m, self.today_m) / 1000.0,
      "areas": float(len(self.areas)),
      "models_50km": float(sum(1 for m in self.model_m.values() if m >= MODEL_KM_GOAL * 1000.0)),
      "dev_km": self.dev_m / 1000.0,
      "attentive_best_h": max(self.attentive_best_s, self.attentive_run_s) / 3600.0,
      "seasons": float(len(self.seasons)),
      "sunnylink_linked": 1.0 if self.sunnylink_linked else 0.0,
    }


def _streak_ending(days: list[str], last: str) -> int:
  have = set(days)
  d = dt.date.fromisoformat(last)
  n = 0
  while d.isoformat() in have:
    n += 1
    d -= dt.timedelta(days=1)
  return n


class AchievementEngine:
  def __init__(self, state: State | None = None, catalog: Catalog | None = None):
    self.state = state or State()
    self.catalog = catalog or load_catalog()
    self._last_t: float | None = None
    self._last_lane_change = 0
    self._utc_offset_h: float | None = None  # from GPS longitude, see local_date
    self._southern = False

  # --- time ---

  def local_date(self, wall: float) -> dt.date:
    """Calendar day for streaks and Road Trip.

    Comma devices keep their clock in UTC, which would split an evening drive in
    the Americas across two days. With a GPS fix, use the solar offset from
    longitude (15 degrees per hour); without one, fall back to the system zone.
    """
    if self._utc_offset_h is not None:
      return (dt.datetime.fromtimestamp(wall, dt.UTC) + dt.timedelta(hours=self._utc_offset_h)).date()
    return dt.datetime.fromtimestamp(wall).date()

  # --- updates ---

  def update(self, s: Sample) -> list[str]:
    """Feed one sample. Returns unlock ids that were newly unlocked by it."""
    st = self.state
    dt_s = 0.0 if self._last_t is None else s.t - self._last_t
    self._last_t = s.t
    if not (0.0 < dt_s <= MAX_DT_S) or not (MIN_SPEED_MS <= s.v_ego <= MAX_SPEED_MS):
      dt_s = 0.0

    if s.lat is not None and s.lon is not None:
      self._utc_offset_h = round(s.lon / 15.0)
      self._southern = s.lat < 0

    if s.engaged and dt_s > 0.0:
      dist = s.v_ego * dt_s
      day = self.local_date(s.wall).isoformat() if s.wall is not None else None
      if day is not None and day != st.today:
        st.best_day_m = max(st.best_day_m, st.today_m)
        st.today, st.today_m = day, 0.0

      st.engaged_m += dist
      st.engaged_s += dt_s
      if day is not None:
        st.today_m += dist
      if s.mads_only:
        st.mads_m += dist
      if s.dev_build:
        st.dev_m += dist
      if s.model_ref:
        st.model_m[s.model_ref] = st.model_m.get(s.model_ref, 0.0) + dist
        if s.model_name:
          st.model_names[s.model_ref] = s.model_name

      if day is not None and day not in st.days and s.v_ego > 1.0:
        st.days.append(day)
        st.days.sort()
        st.best_streak_days = max(st.best_streak_days, _streak_ending(st.days, day))
        sn = season(dt.date.fromisoformat(day), self._southern)
        if sn not in st.seasons:
          st.seasons.append(sn)

      if s.dm_alert_level >= DM_ALERT_RED:
        st.attentive_best_s = max(st.attentive_best_s, st.attentive_run_s)
        st.attentive_run_s = 0.0
      else:
        st.attentive_run_s += dt_s

      if s.lat is not None and s.lon is not None:
        area = hashlib.sha256((st.salt + geohash(s.lat, s.lon)).encode()).hexdigest()[:16]
        if area not in st.areas:
          st.areas.append(area)
          st.areas.sort()

    # a lane change counts once, when it reaches its finishing phase while engaged
    if s.engaged and s.lane_change_state == LANE_CHANGE_FINISHING and self._last_lane_change == LANE_CHANGE_STARTING:
      st.lane_changes += 1
    self._last_lane_change = s.lane_change_state

    return self.check_unlocks(s.wall)

  def set_sunnylink_linked(self, linked: bool, wall: float | None) -> list[str]:
    self.state.sunnylink_linked = self.state.sunnylink_linked or linked
    return self.check_unlocks(wall)

  def end_drive(self) -> None:
    """Close out the attentive run so the best is kept, and forget timing between drives."""
    st = self.state
    st.attentive_best_s = max(st.attentive_best_s, st.attentive_run_s)
    self._last_t = None
    self._last_lane_change = 0

  def check_unlocks(self, wall: float | None) -> list[str]:
    """Unlock every tier whose goal is met. The unlock time is 0 when the clock isn't valid yet."""
    metrics = self.state.metrics()
    new = []
    for a in self.catalog.achievements:
      value = metrics.get(a.metric, 0.0)
      for tier in a.tiers:
        uid = a.unlock_id(tier)
        if value >= tier.threshold and uid not in self.state.unlocked:
          self.state.unlocked[uid] = round(wall) if wall is not None else 0
          new.append(uid)
    return new


# --- persistence ---

def load_state(path: Path | None = None) -> State:
  path = path or state_path()
  try:
    with open(path) as f:
      return State.from_dict(json.load(f))
  except FileNotFoundError:
    return State()
  except (ValueError, TypeError):
    # unreadable JSON: keep it aside for debugging instead of silently overwriting it.
    # Other OSErrors propagate, so a transient read failure can never be saved over real progress.
    os.replace(path, path.with_suffix(".corrupt.json"))
    return State()


def save_json(path: Path, data: dict) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
  try:
    with os.fdopen(fd, "w") as f:
      json.dump(data, f, separators=(",", ":"), sort_keys=True)
      f.flush()
      os.fsync(f.fileno())
    os.replace(tmp, path)
  except BaseException:
    try:
      os.unlink(tmp)
    except OSError:
      pass
    raise


def save_state(state: State, path: Path | None = None) -> None:
  save_json(path or state_path(), asdict(state))


def load_seen(path: Path | None = None) -> set[str]:
  try:
    with open(path or seen_path()) as f:
      return set(json.load(f).get("seen", []))
  except (OSError, ValueError, AttributeError):
    return set()


def save_seen(seen: set[str], path: Path | None = None) -> None:
  save_json(path or seen_path(), {"seen": sorted(seen)})
