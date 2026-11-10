from openpilot.selfdrive.ui.sunnypilot.achievements_store import AchievementsStore
from openpilot.sunnypilot.achievements.engine import AchievementEngine, State, save_state

T0 = 1_780_000_000.0


def make_store(tmp_path):
  return AchievementsStore(state_file=tmp_path / "state.json", seen_file=tmp_path / "seen.json")


def write_state(tmp_path, engaged_km):
  e = AchievementEngine(State(engaged_m=engaged_km * 1000.0))
  e.check_unlocks(T0)
  save_state(e.state, tmp_path / "state.json")


def test_no_state_file_shows_everything_locked(tmp_path):
  store = make_store(tmp_path)
  assert store.refresh(force=True)
  unlocked, total = store.unlocked_count()
  assert unlocked == 0 and total > 10
  assert store.new_ids() == set()


def test_new_unlocks_until_seen(tmp_path):
  write_state(tmp_path, 150)
  store = make_store(tmp_path)
  store.refresh(force=True)
  assert store.new_ids() == {"first_light", "odometer.bronze"}
  v = store.version
  store.mark_all_seen()
  assert store.new_ids() == set() and store.version > v

  # a second store (the other screen, or after a reboot) sees them as seen too
  other = make_store(tmp_path)
  other.refresh(force=True)
  assert other.new_ids() == set()


def test_refresh_picks_up_new_unlocks(tmp_path):
  write_state(tmp_path, 150)
  store = make_store(tmp_path)
  store.refresh(force=True)
  store.mark_all_seen()
  write_state(tmp_path, 1500)
  assert store.refresh(force=True)
  assert store.new_ids() == {"odometer.silver"}


def test_totals_and_status(tmp_path):
  write_state(tmp_path, 1240)
  store = make_store(tmp_path)
  store.refresh(force=True)
  assert store.status("odometer").summary() == "silver · 1,240 / 10,000 km"
  assert "1,240 km engaged" in store.totals_text()
  assert store.unlock_ids("odometer") == ["odometer.bronze", "odometer.silver", "odometer.gold", "odometer.platinum"]
  assert store.status("nope") is None
