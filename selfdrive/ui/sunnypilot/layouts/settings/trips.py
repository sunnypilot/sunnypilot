import requests
import threading
import time
import pyray as rl

from openpilot.common.api import api_get
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.lib.api_helpers import get_token
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget

MILE_TO_KM = 1.60934


class TripsLayout(Widget):
  PARAM_KEY = "ApiCache_DriveStats"
  UPDATE_INTERVAL = 30  # seconds

  def __init__(self):
    super().__init__()
    self._params = Params()
    self._session = requests.Session()
    self._stats = self._get_stats()

    self._running = True
    self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
    self._update_thread.start()

  def __del__(self):
    self._running = False
    try:
      if self._update_thread and self._update_thread.is_alive():
        self._update_thread.join(timeout=1.0)
    except Exception:
      pass

  def _get_stats(self):
    stats = self._params.get(self.PARAM_KEY)
    if not stats:
      return {}
    if isinstance(stats, dict):
      return stats
    try:
      import json
      return json.loads(stats)
    except Exception:
      return {}

  def _fetch_drive_stats(self):
    try:
      dongle_id = self._params.get("DongleId")
      if not dongle_id:
        return

      if isinstance(dongle_id, bytes):
        dongle_id = dongle_id.decode('utf-8')

      if dongle_id == UNREGISTERED_DONGLE_ID:
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
      if not ui_state.started and device._awake:
        self._fetch_drive_stats()
      time.sleep(self.UPDATE_INTERVAL)

  def _render_stat_group(self, x, y, width, title, data, is_metric):
    # Title
    title_font = gui_app.font(FontWeight.BOLD)
    rl.draw_text_ex(title_font, title, rl.Vector2(x, y), 51 * FONT_SCALE, 0, rl.WHITE)
    y += 80 * FONT_SCALE

    # Stats: Routes, Distance, Hours
    # Replicating grid layout manually
    # Col 1: Routes, Col 2: Distance, Col 3: Hours

    col_width = width / 3

    # Values
    number_font = gui_app.font(FontWeight.BOLD)
    unit_font = gui_app.font(FontWeight.LIGHT)
    number_size = 78 * FONT_SCALE
    unit_size = 51 * FONT_SCALE
    color_unit = rl.Color(160, 160, 160, 255)

    routes = int(data.get("routes", 0))
    distance = data.get("distance", 0)
    distance_str = str(int(distance * MILE_TO_KM)) if is_metric else str(int(distance))
    hours = int(data.get("minutes", 0) / 60)

    # Row 1: Numbers
    rl.draw_text_ex(number_font, str(routes), rl.Vector2(x, y), number_size, 0, rl.WHITE)
    rl.draw_text_ex(number_font, distance_str, rl.Vector2(x + col_width, y), number_size, 0, rl.WHITE)
    rl.draw_text_ex(number_font, str(hours), rl.Vector2(x + col_width * 2, y), number_size, 0, rl.WHITE)

    y += 85 * FONT_SCALE

    # Row 2: Units
    dist_unit = tr("KM") if is_metric else tr("Miles")

    rl.draw_text_ex(unit_font, tr("Drives"), rl.Vector2(x, y), unit_size, 0, color_unit)
    rl.draw_text_ex(unit_font, dist_unit, rl.Vector2(x + col_width, y), unit_size, 0, color_unit)
    rl.draw_text_ex(unit_font, tr("Hours"), rl.Vector2(x + col_width * 2, y), unit_size, 0, color_unit)

    y += 80 * FONT_SCALE
    return y

  def _render(self, rect: rl.Rectangle):
    x = rect.x + 50
    y = rect.y + 50
    w = rect.width - 100

    is_metric = self._params.get_bool("IsMetric")

    all_time = self._stats.get("all", {})
    week = self._stats.get("week", {})

    y = self._render_stat_group(x, y, w, tr("ALL TIME"), all_time, is_metric)
    y += 100 * FONT_SCALE # Spacing
    y = self._render_stat_group(x, y, w, tr("PAST WEEK"), week, is_metric)

    return -1
