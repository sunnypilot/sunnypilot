"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

What both Achievements screens and the settings buttons read: the state file
achievementsd writes, plus the UI's own list of unlocks already seen.
No pyray here, so it can be tested without a display.
"""
import time
from pathlib import Path

from openpilot.sunnypilot.achievements.catalog import AchievementStatus, Catalog, format_amount, load_catalog, statuses
from openpilot.sunnypilot.achievements.engine import State, load_seen, load_state, save_seen, seen_path, state_path

REFRESH_INTERVAL_S = 5.0


class AchievementsStore:
  def __init__(self, state_file: Path | None = None, seen_file: Path | None = None, catalog: Catalog | None = None):
    self._state_file = state_file
    self._seen_file = seen_file
    self.catalog = catalog or load_catalog()
    self.state = State()
    self._seen: set[str] = set()
    self._mtime: float | None = None
    self._last_check = 0.0
    self.version = 0  # bumps on every reload or seen change, so several screens can share one store

  def _state_path(self) -> Path:
    return self._state_file or state_path()

  def _seen_path(self) -> Path:
    return self._seen_file or seen_path()

  def refresh(self, force: bool = False) -> bool:
    """Reload if the state file changed. Cheap enough to call every frame. Returns True when reloaded."""
    now = time.monotonic()
    if not force and now - self._last_check < REFRESH_INTERVAL_S:
      return False
    self._last_check = now
    try:
      mtime = self._state_path().stat().st_mtime
    except OSError:
      mtime = None
    if not force and mtime == self._mtime:
      return False
    self._mtime = mtime
    try:
      self.state = load_state(self._state_path()) if mtime is not None else State()
    except OSError:
      return False
    self._seen = load_seen(self._seen_path())
    self.version += 1
    return True

  def statuses(self) -> list[AchievementStatus]:
    return statuses(self.catalog, self.state.metrics(), self.state.unlocked)

  def status(self, achievement_id: str) -> AchievementStatus | None:
    return next((s for s in self.statuses() if s.achievement.id == achievement_id), None)

  def unlock_ids(self, achievement_id: str) -> list[str]:
    a = next((a for a in self.catalog.achievements if a.id == achievement_id), None)
    return [a.unlock_id(t) for t in a.tiers] if a else []

  def unlocked_count(self) -> tuple[int, int]:
    all_ids = self.catalog.all_unlock_ids()
    return sum(1 for uid in all_ids if uid in self.state.unlocked), len(all_ids)

  def new_ids(self) -> set[str]:
    return {uid for uid in self.state.unlocked if uid not in self._seen and uid in set(self.catalog.all_unlock_ids())}

  def mark_all_seen(self) -> None:
    new = self.new_ids()
    if not new:
      return
    self._seen |= new
    self.version += 1
    try:
      save_seen(self._seen, self._seen_path())
    except OSError:
      pass

  def totals_text(self, is_metric: bool = True) -> str:
    m = self.state.metrics()
    unlocked, total = self.unlocked_count()
    return "\n".join([
      f"{format_amount(m['engaged_km'], 'km', is_metric)} engaged",
      f"{format_amount(m['engaged_h'], 'h')} engaged",
      f"{int(m['active_days'])} days, best streak {int(m['best_streak_days'])}",
      f"{unlocked} of {total} unlocked",
    ])


achievements_store = AchievementsStore()
