"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

comma four Achievements screen: a summary card, then one card per achievement.
Reads the state file achievementsd writes; opening the screen marks new unlocks as seen.
"""
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog
from openpilot.selfdrive.ui.sunnypilot.achievements_store import AchievementsStore, achievements_store
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


class AchievementsLayoutMici(NavScroller):
  def __init__(self, store: AchievementsStore = achievements_store):
    super().__init__()
    self._store = store
    self._shown_version = -1
    self._summary_btn = BigButton(tr("achievements"), "")
    self._summary_btn.set_click_callback(self._show_summary)

    self._cards: dict[str, BigButton] = {}
    widgets = [self._summary_btn]
    for a in self._store.catalog.achievements:
      card = BigButton(a.name.lower(), "")
      card.set_click_callback(lambda aid=a.id: self._show_details(aid))
      self._cards[a.id] = card
      widgets.append(card)
    self._scroller.add_widgets(widgets)

  def show_event(self):
    super().show_event()
    self._store.refresh(force=True)
    self._refresh_cards()
    # marked seen after drawing, so the "new" labels stay up while this screen is open
    self._store.mark_all_seen()
    self._shown_version = self._store.version

  def _update_state(self):
    super()._update_state()
    self._store.refresh()
    if self._store.version != self._shown_version:
      self._refresh_cards()
      self._shown_version = self._store.version

  def _refresh_cards(self):
    is_metric = ui_state.is_metric
    new = self._store.new_ids()
    unlocked, total = self._store.unlocked_count()
    self._summary_btn.set_value(f"{unlocked} / {total} unlocked")
    for status in self._store.statuses():
      a = status.achievement
      card = self._cards[a.id]
      is_new = any(uid in new for uid in self._store.unlock_ids(a.id))
      card.set_value(("new · " if is_new else "") + status.summary(is_metric))

  def _show_summary(self):
    gui_app.push_widget(BigDialog("", self._store.totals_text(ui_state.is_metric)))

  def _show_details(self, achievement_id: str):
    status = self._store.status(achievement_id)
    if status is None:
      return
    gui_app.push_widget(BigDialog(status.achievement.name.lower(), f"{status.achievement.description}\n{status.summary(ui_state.is_metric)}"))
