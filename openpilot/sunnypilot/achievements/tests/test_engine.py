import datetime as dt
import json

import pytest

from openpilot.sunnypilot.achievements.catalog import CATALOG_PATH, load_catalog, parse_catalog, statuses
from openpilot.sunnypilot.achievements.engine import (AchievementEngine, LANE_CHANGE_FINISHING, LANE_CHANGE_STARTING, Sample, State,
                                                      geohash, load_seen, load_state, save_seen, save_state, season)

T0 = dt.datetime(2026, 6, 1, 16, 0, tzinfo=dt.UTC).timestamp()  # noon in New York


def drive(engine, seconds, v=20.0, t0=T0, hz=10, **kw):
  """Feed `seconds` of driving at `v` m/s; returns every unlock id along the way."""
  new = []
  n = int(seconds * hz)
  for i in range(n + 1):
    extra = {k: val for k, val in kw.items() if k != "op_active"}
    new += engine.update(Sample(t=t0 + i / hz, wall=t0 + i / hz, v_ego=v, op_active=kw.get("op_active", True), **extra))
  return new


def test_catalog_loads_and_ids_are_unique():
  cat = load_catalog()
  ids = cat.all_unlock_ids()
  assert len(ids) == len(set(ids))
  assert "odometer.silver" in ids and "first_light" in ids
  engine_metrics = set(State().metrics())
  assert cat.metrics <= engine_metrics, f"catalog uses metrics the engine doesn't compute: {cat.metrics - engine_metrics}"


def test_catalog_rejects_decreasing_tiers():
  data = json.loads(CATALOG_PATH.read_text())
  data["achievements"][1]["tiers"][1]["threshold"] = 1
  with pytest.raises(ValueError):
    parse_catalog(data)


def test_engaged_distance_and_first_light():
  e = AchievementEngine()
  new = drive(e, 10, v=20.0)
  assert e.state.engaged_m == pytest.approx(200.0, rel=1e-6)
  assert e.state.engaged_s == pytest.approx(10.0, rel=1e-6)
  assert new == ["first_light"]


def test_not_engaged_counts_nothing():
  e = AchievementEngine()
  drive(e, 10, op_active=False)
  assert e.state.engaged_m == 0.0
  assert e.state.unlocked == {}


def test_gaps_and_bad_speeds_are_ignored():
  e = AchievementEngine()
  e.update(Sample(t=T0, v_ego=20.0, op_active=True))
  e.update(Sample(t=T0 + 30.0, v_ego=20.0, op_active=True))  # 30 s gap: process stalled
  e.update(Sample(t=T0 + 30.1, v_ego=500.0, op_active=True))  # implausible speed
  assert e.state.engaged_m == 0.0


def test_odometer_tiers_unlock_in_order():
  e = AchievementEngine()
  e.state.engaged_m = 99_999.0
  new = drive(e, 1, v=10.0)
  assert "odometer.bronze" in new and "odometer.silver" not in new
  assert set(e.state.unlocked) >= {"first_light", "odometer.bronze"}


def test_unlocks_only_once():
  e = AchievementEngine()
  assert drive(e, 5) == ["first_light"]
  assert drive(e, 5, t0=T0 + 100) == []


def test_mads_only_distance():
  e = AchievementEngine()
  drive(e, 10, v=10.0, op_active=False, mads_active=True)
  drive(e, 10, v=10.0, t0=T0 + 60, op_active=True, mads_active=True)
  assert e.state.mads_m == pytest.approx(100.0, rel=1e-6)
  assert e.state.engaged_m == pytest.approx(200.0, rel=1e-6)


def test_lane_change_counted_once_when_engaged():
  e = AchievementEngine()
  seq = [0, 1, 2, 2, 3, 3, 0, 0, 2, 3, 0]
  for i, lc in enumerate(seq):
    e.update(Sample(t=T0 + i * 0.1, v_ego=25.0, op_active=True, lane_change_state=lc))
  assert e.state.lane_changes == 2
  e.update(Sample(t=T0 + 5, v_ego=25.0, op_active=False, lane_change_state=LANE_CHANGE_STARTING))
  e.update(Sample(t=T0 + 5.1, v_ego=25.0, op_active=False, lane_change_state=LANE_CHANGE_FINISHING))
  assert e.state.lane_changes == 2


def test_days_streak_and_best_day():
  e = AchievementEngine()
  for d in range(8):
    drive(e, 2, t0=T0 + d * 86400)
  assert len(e.state.days) == 8
  assert e.state.best_streak_days == 8
  assert "streak.bronze" in e.state.unlocked and "regular.bronze" in e.state.unlocked
  # a gap day resets the run but keeps the best
  drive(e, 2, t0=T0 + 10 * 86400)
  assert e.state.best_streak_days == 8


def test_local_date_follows_gps_longitude():
  e = AchievementEngine()
  late = dt.datetime(2026, 6, 2, 2, 0, tzinfo=dt.UTC).timestamp()  # 10 pm on June 1 in New York
  e.update(Sample(t=late, wall=late, v_ego=10.0, op_active=True, lat=40.7, lon=-74.0))
  e.update(Sample(t=late + 0.1, wall=late + 0.1, v_ego=10.0, op_active=True, lat=40.7, lon=-74.0))
  assert e.state.days == ["2026-06-01"]


def test_invalid_clock_counts_distance_but_not_days():
  e = AchievementEngine()
  for i in range(11):
    e.update(Sample(t=i / 10, v_ego=10.0, op_active=True))  # wall=None: clock not set yet
  assert e.state.engaged_m == pytest.approx(10.0, rel=1e-6)
  assert e.state.days == [] and e.state.today_m == 0.0
  assert e.state.unlocked == {}


def test_attentive_run_resets_on_red_alert():
  e = AchievementEngine()
  drive(e, 100)
  drive(e, 1, t0=T0 + 200, dm_alert_level=3)
  assert e.state.attentive_run_s < 1.0
  assert e.state.attentive_best_s == pytest.approx(100.0, rel=1e-3)


def test_areas_are_hashed_and_counted():
  e = AchievementEngine()
  drive(e, 1, lat=40.70, lon=-74.00)
  drive(e, 1, t0=T0 + 10, lat=40.701, lon=-74.001)   # same ~5 km cell
  drive(e, 1, t0=T0 + 20, lat=41.50, lon=-73.00)     # different cell
  assert len(e.state.areas) == 2
  raw = json.dumps(e.state.__dict__)
  assert "40.7" not in raw and geohash(40.70, -74.00) not in raw


def test_model_hopper_counts_models_over_50km():
  e = AchievementEngine()
  e.state.model_m = {"a": 50_000.0, "b": 50_000.0, "c": 10.0}
  drive(e, 1, model_ref="c", model_name="Model C")
  assert e.state.metrics()["models_50km"] == 2
  e.state.model_m["c"] = 50_000.0
  assert "model_hopper.bronze" in drive(e, 1, t0=T0 + 10, model_ref="c")
  assert e.state.model_names["c"] == "Model C"


def test_dev_build_and_seasons():
  e = AchievementEngine()
  drive(e, 1, dev_build=True)
  assert e.state.dev_m > 0
  assert season(dt.date(2026, 1, 5)) == "winter"
  assert season(dt.date(2026, 1, 5), southern=True) == "summer"


def test_sunnylink_flag_sticks():
  e = AchievementEngine()
  assert e.set_sunnylink_linked(True, T0) == ["linked_up"]
  e.set_sunnylink_linked(False, T0 + 1)
  assert e.state.sunnylink_linked


def test_state_round_trip(tmp_path):
  e = AchievementEngine()
  drive(e, 10, lat=40.7, lon=-74.0, model_ref="x")
  path = tmp_path / "state.json"
  save_state(e.state, path)
  loaded = load_state(path)
  assert loaded == e.state


def test_corrupt_state_is_moved_aside(tmp_path):
  path = tmp_path / "state.json"
  path.write_text("{not json")
  assert load_state(path).engaged_m == 0.0
  assert (tmp_path / "state.corrupt.json").exists()
  assert not path.exists()


def test_unknown_fields_are_ignored(tmp_path):
  path = tmp_path / "state.json"
  path.write_text(json.dumps({"engaged_m": 5.0, "from_the_future": 1}))
  assert load_state(path).engaged_m == 5.0


def test_seen_round_trip(tmp_path):
  path = tmp_path / "seen.json"
  assert load_seen(path) == set()
  save_seen({"a", "b"}, path)
  assert load_seen(path) == {"a", "b"}


def test_status_summaries():
  cat = load_catalog()
  st = State(engaged_m=1_240_000.0)
  e = AchievementEngine(st)
  e.check_unlocks(T0)
  by_id = {s.achievement.id: s for s in statuses(cat, st.metrics(), st.unlocked)}
  assert by_id["odometer"].summary() == "silver · 1,240 / 10,000 km"
  assert by_id["odometer"].summary(is_metric=False) == "silver · 770 / 6,213 mi"
  assert by_id["first_light"].summary() == "done"
  assert by_id["regular"].summary() == "locked · 0 / 7 days"
  assert by_id["linked_up"].summary() == "locked"
