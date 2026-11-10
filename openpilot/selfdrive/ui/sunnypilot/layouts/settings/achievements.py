"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

comma 3X Achievements panel: a totals row, then one row per achievement.
Tap a row to read what it is for. Opening the panel marks new unlocks as seen.
"""
from openpilot.selfdrive.ui.sunnypilot.achievements_store import AchievementsStore, achievements_store
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import text_item
from openpilot.system.ui.widgets.scroller_tici import Scroller


class AchievementsLayout(Widget):
  def __init__(self, store: AchievementsStore = achievements_store):
    super().__init__()
    self._store = store
    self._new: set[str] = set()

    unlocked = text_item(tr("Unlocked"), self._unlocked_text, description=lambda: self._store.totals_text(ui_state.is_metric))
    items = [unlocked]
    for a in self._store.catalog.achievements:
      items.append(text_item(a.name, lambda aid=a.id: self._row_value(aid), description=a.description))
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _unlocked_text(self) -> str:
    unlocked, total = self._store.unlocked_count()
    return f"{unlocked} / {total}"

  def _row_value(self, achievement_id: str) -> str:
    status = self._store.status(achievement_id)
    if status is None:
      return ""
    is_new = any(uid in self._new for uid in self._store.unlock_ids(achievement_id))
    return (tr("NEW") + " · " if is_new else "") + status.summary(ui_state.is_metric)

  def show_event(self):
    self._scroller.show_event()
    self._store.refresh(force=True)
    # remembered for this visit, so the NEW labels stay up while the panel is open
    self._new = self._store.new_ids()
    self._store.mark_all_seen()

  def _update_state(self):
    self._store.refresh()

  def _render(self, rect):
    self._scroller.render(rect)
