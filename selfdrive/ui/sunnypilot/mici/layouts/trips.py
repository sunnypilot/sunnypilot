"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import requests
import threading
import time


from openpilot.common.api import api_get
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.lib.api_helpers import get_token
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller

UPDATE_INTERVAL = 30


class TripsLayoutMici(NavScroller):
  PARAM_KEY = "ApiCache_DriveStats"

  def __init__(self):
    super().__init__()

    self._params = Params()
    self._session = requests.Session()
    self._stats = self._get_stats()

    STAT_LABELS = [
      tr("all time drives"), tr("all time distance"), tr("all time hours"),
      tr("week drives"), tr("week distance"), tr("week hours"),
    ]
    self._stat_buttons = []
    for label in STAT_LABELS:
      btn = BigButton(label)
      btn.set_enabled(False)
      self._stat_buttons.append(btn)

    self._scroller.add_widgets(self._stat_buttons)

    self._format_stats()

    self._running = False
    self._update_thread: threading.Thread | None = None

  def show_event(self):
    super().show_event()
    if not self._running:
      self._running = True
      if self._update_thread is None or not self._update_thread.is_alive():
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

  def hide_event(self):
    super().hide_event()
    self._running = False

  def _get_stats(self):
    return self._params.get(self.PARAM_KEY) or {}

  def _fetch_drive_stats(self):
    try:
      dongle_id = self._params.get("DongleId")
      if not dongle_id or dongle_id == UNREGISTERED_DONGLE_ID:
        return
      identity_token = get_token(dongle_id)
      response = api_get(f"v1.1/devices/{dongle_id}/stats", access_token=identity_token, session=self._session)
      if response.status_code == 200:
        self._params.put(self.PARAM_KEY, response.json())
    except Exception as e:
      cloudlog.error(f"Failed to fetch drive stats: {e}")

  def _update_loop(self):
    while self._running:
      if not ui_state.started and device.awake:
        self._fetch_drive_stats()
      time.sleep(UPDATE_INTERVAL)

  def _format_stats(self):
    is_metric = self._params.get_bool("IsMetric")
    dist_unit = "km" if is_metric else "mi"

    all_time = self._stats.get("all", {})
    week = self._stats.get("week", {})

    def fmt_dist(data):
      distance = data.get("distance", 0)
      return str(int(distance * CV.MPH_TO_KPH)) if is_metric else str(int(distance))

    def fmt_period(data):
      return [
        str(int(data.get("routes", 0))),
        f"{fmt_dist(data)} {dist_unit}",
        f"{int(data.get('minutes', 0) / 60)} " + tr("hrs"),
      ]

    values = fmt_period(all_time) + fmt_period(week)
    for btn, val in zip(self._stat_buttons, values, strict=True):
      btn.set_value(val)

  def _update_state(self):
    super()._update_state()
    new_stats = self._get_stats()
    if new_stats != self._stats:
      self._stats = new_stats
      self._format_stats()
