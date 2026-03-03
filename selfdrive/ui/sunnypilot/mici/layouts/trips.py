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
from openpilot.system.ui.widgets.scroller import NavScroller

UPDATE_INTERVAL = 30


class TripsLayoutMici(NavScroller):
  PARAM_KEY = "ApiCache_DriveStats"

  def __init__(self):
    super().__init__()

    self._params = Params()
    self._session = requests.Session()
    self._stats = self._get_stats()

    self._all_drives = BigButton("all time drives")
    self._all_drives.set_enabled(False)
    self._all_distance = BigButton("all time distance")
    self._all_distance.set_enabled(False)
    self._all_hours = BigButton("all time hours")
    self._all_hours.set_enabled(False)
    self._week_drives = BigButton("week drives")
    self._week_drives.set_enabled(False)
    self._week_distance = BigButton("week distance")
    self._week_distance.set_enabled(False)
    self._week_hours = BigButton("week hours")
    self._week_hours.set_enabled(False)

    self._scroller.add_widgets([
      self._all_drives, self._all_distance, self._all_hours,
      self._week_drives, self._week_distance, self._week_hours,
    ])

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
        data = response.json()
        self._stats = data
        self._params.put(self.PARAM_KEY, data)
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

    self._all_drives.set_value(str(int(all_time.get("routes", 0))))
    self._all_distance.set_value(f"{fmt_dist(all_time)} {dist_unit}")
    self._all_hours.set_value(f"{int(all_time.get('minutes', 0) / 60)} hrs")

    self._week_drives.set_value(str(int(week.get("routes", 0))))
    self._week_distance.set_value(f"{fmt_dist(week)} {dist_unit}")
    self._week_hours.set_value(f"{int(week.get('minutes', 0) / 60)} hrs")

  def _update_state(self):
    super()._update_state()
    new_stats = self._get_stats()
    if new_stats != self._stats:
      self._stats = new_stats
      self._format_stats()
