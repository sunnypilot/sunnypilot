"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import datetime
import os
import platform
import requests
import shutil
import threading
from pathlib import Path
from time import monotonic

from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import device, ui_state
from openpilot.selfdrive.ui.layouts.settings.software import time_ago
from openpilot.system.hardware.hw import Paths
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.list_view import text_item
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.system.ui.sunnypilot.lib.utils import NoElideButtonAction
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeFolder, TreeNode, TreeOptionDialog
from openpilot.system.ui.sunnypilot.widgets.progress_bar import progress_item

MAP_PATH = Path(Paths.mapd_root()) / "offline"


class OSMLayout(Widget):
  def __init__(self):
    super().__init__()
    self._current_percent = 0
    self._last_map_size_update = 0
    self._mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else ui_state.params
    self._initialize_items()
    self._update_map_size()
    self._progress.set_visible(False)
    self._state_btn.set_visible(False)
    self._mapd_version.action_item.set_text(ui_state.params.get("MapdVersion") or "Loading...")
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._mapd_version = text_item(tr("Mapd Version"), lambda: ui_state.params.get("MapdVersion") or "Loading...")
    self._delete_maps_btn = ListItemSP(tr("Downloaded Maps"), action_item=NoElideButtonAction(tr("DELETE"), enabled=True), callback=self._delete_maps)
    self._progress = progress_item(tr("Downloading Map"))
    self._update_btn = ListItemSP(tr("Database Update"), action_item=NoElideButtonAction(tr("CHECK"), enabled=True), callback=self._update_db)
    self._country_btn = ListItemSP(tr("Country"), action_item=NoElideButtonAction(tr("SELECT"), enabled=True), callback=lambda: self._select_region("Country"))
    self._state_btn = ListItemSP(tr("State"), action_item=NoElideButtonAction(tr("SELECT"), enabled=True), callback=lambda: self._select_region("State"))

    self.items = [self._mapd_version, self._delete_maps_btn, self._progress, self._update_btn, self._country_btn, self._state_btn]

  def _show_confirm(self, msg, confirm_text, func):
    gui_app.set_modal_overlay(ConfirmDialog(msg, confirm_text), lambda res: func() if res == DialogResult.CONFIRM else None)

  def calculate_size(self):
    total_size = 0
    directories_to_scan = [MAP_PATH] if MAP_PATH.exists() else []
    while directories_to_scan:
      try:
        for entry in os.scandir(directories_to_scan.pop()):
          if entry.is_file():
            total_size += entry.stat().st_size
          elif entry.is_dir():
            directories_to_scan.append(entry.path)
      except OSError:
        pass
    self._delete_maps_btn.action_item.set_value(f"{total_size / 1024 ** 2:.2f} MB" if total_size < 1024 ** 3 else f"{total_size / 1024 ** 3:.2f} GB")

  def _update_map_size(self):
    threading.Thread(target=self.calculate_size, daemon=True).start()

  def _do_delete_maps(self):
    if MAP_PATH.exists():
      shutil.rmtree(MAP_PATH)

    for param in ("OsmDownloadedDate", "OsmLocal", "OsmLocationName", "OsmLocationTitle", "OsmStateName", "OsmStateTitle"):
      ui_state.params.remove(param)

    self._delete_maps_btn.action_item.set_enabled(True)
    self._delete_maps_btn.action_item.set_text(tr("DELETE"))
    self._update_map_size()

  def _on_confirm_delete_maps(self):
    self._delete_maps_btn.action_item.set_enabled(False)
    self._delete_maps_btn.action_item.set_text("DELETING...")
    threading.Thread(target=self._do_delete_maps).start()

  def _delete_maps(self):
    self._show_confirm(tr("This will delete ALL downloaded maps\n\nAre you sure you want to delete all maps?"),
                       tr("Yes, delete all maps"), self._on_confirm_delete_maps)

  def _update_db(self):
    self._show_confirm(tr("This will start the download process and it might take a while to complete."), tr("Start Download"),
                       lambda: ui_state.params.put_bool("OsmDbUpdatesCheck", True))

  def _select_region(self, region_type):
    is_country = region_type == "Country"
    btn = self._country_btn if is_country else self._state_btn
    btn.action_item.set_enabled(False)
    btn.action_item.set_text(tr("FETCHING..."))
    threading.Thread(target=self._do_select_region, args=(region_type, btn)).start()

  def _handle_region_selection(self, region_type, locations, key, res, ref):
    if res != DialogResult.CONFIRM or not ref:
      if region_type == "State" and res == DialogResult.CANCEL:
        if ui_state.params.get("OsmLocationName") == "US" and not ui_state.params.get("OsmStateName"):
          ui_state.params.remove("OsmLocationName")
          ui_state.params.remove("OsmLocationTitle")
          ui_state.params.remove("OsmLocal")
          self._update_labels()
      return

    if region_type == "Country":
      ui_state.params.put_bool("OsmLocal", True)
      ui_state.params.remove("OsmStateName")
      ui_state.params.remove("OsmStateTitle")

    ui_state.params.put(f"{key}Name", ref)
    name = next((n.data['display_name'] for n in locations if n.ref == ref), ref)
    ui_state.params.put(f"{key}Title", name)

    if ref == "US" and region_type == "Country":
      self._select_region("State")
    else:
      self._update_db()

  def _do_select_region(self, region_type, btn):
    base_url = "https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/"
    url = base_url + ("nation_bounding_boxes.json" if region_type == "Country" else "us_states_bounding_boxes.json")
    try:
      data = requests.get(url, timeout=10).json()
      locations = sorted([TreeNode(ref=k, data={'display_name': v['full_name']}) for k, v in data.items()], key=lambda n: n.data['display_name'])
    except Exception:
      locations = []

    if region_type == "State":
      locations.insert(0, TreeNode(ref="All", data={'display_name': tr("All states (~6.0 GB)")}))

    btn.action_item.set_enabled(True)
    btn.action_item.set_text(tr("SELECT"))

    key = "OsmLocation" if region_type == "Country" else "OsmState"
    current = ui_state.params.get(f"{key}Name") or ""

    dialog = TreeOptionDialog(tr(f"Select {region_type}"), [TreeFolder(folder="", nodes=locations)], current_ref=current, search_prompt="Perform a search")
    dialog.on_exit = lambda res: self._handle_region_selection(region_type, locations, key, res, dialog.selection_ref)
    gui_app.set_modal_overlay(dialog, callback=lambda res: self._handle_region_selection(region_type, locations, key, res, dialog.selection_ref))

  def _update_labels(self):
    downloading = bool(self._mem_params.get("OSMDownloadLocations"))
    self._country_btn.set_enabled(not downloading)
    self._state_btn.set_enabled(not downloading)
    self._state_btn.set_visible(ui_state.params.get("OsmLocationName") == "US")
    self._update_btn.set_visible(bool(ui_state.params.get("OsmLocationName")))

    self._country_btn.action_item.set_value(ui_state.params.get("OsmLocationTitle") or "")
    self._state_btn.action_item.set_value(ui_state.params.get("OsmStateTitle") or "")

    pending = ui_state.params.get_bool("OsmDbUpdatesCheck")
    if downloading or pending:
      if downloading:
        device._reset_interactive_timeout()
        self._update_map_size()
      self._progress.set_visible(True)
      progress = ui_state.params.get("OSMDownloadProgress")
      total = progress.get('total_files', 0) if progress else 0
      done = progress.get('downloaded_files', 0) if progress else 0
      failed = total > 0 and not downloading and done < total

      if total > 0:
        progress_perc = max(0.0, min(100.0, (done / total) * 100.0))
      else:
        progress_perc = 0.0

      if failed:
        text = "0% - Downloading Maps"
        btn_text = tr("Error: Invalid download. Retry.")
        self._current_percent = 0.0
      elif total > 0 and downloading:
        self._current_percent = progress_perc
        perc_int = int(progress_perc)
        text = f"{perc_int}% - Downloading Maps"
        btn_text = f"{done}/{total} ({perc_int}%)"
      else:
        self._current_percent = 0.0
        text = "0% - Downloading Maps"
        btn_text = tr("Downloading Maps...")

      self._progress.action_item.update(self._current_percent, text, show_progress=total > 0 and downloading and not failed)
      self._update_btn.action_item.set_enabled(not downloading)  # TODO-SP: introduce CANCEL database download with mapd
      self._update_btn.action_item.set_value(btn_text)
      self._country_btn.action_item.set_enabled(not downloading)
      self._state_btn.action_item.set_enabled(not downloading)
      self._delete_maps_btn.action_item.set_enabled(not downloading)
    else:
      self._progress.set_visible(False)
      self._update_btn.action_item.set_enabled(True)
      self._country_btn.action_item.set_enabled(True)
      self._state_btn.action_item.set_enabled(True)
      self._delete_maps_btn.action_item.set_enabled(True)

      ts = ui_state.params.get("OsmDownloadedDate")
      dt: datetime.datetime | None = None

      if ts:
        try:
          ts_f = float(ts)
          if ts_f > 0:
            dt = datetime.datetime.fromtimestamp(ts_f, tz=datetime.UTC)
        except (ValueError, TypeError):
          dt = None

      formatted = time_ago(dt)
      self._update_btn.action_item.set_value(tr("Last checked {}").format(formatted))

  def show_event(self):
    self._scroller.show_event()

  def _update_state(self):
    now = monotonic()
    if now - self._last_map_size_update >= 1.0:
      self._last_map_size_update = now
      self._update_labels()

  def _render(self, rect):
    self._scroller.render(rect)
