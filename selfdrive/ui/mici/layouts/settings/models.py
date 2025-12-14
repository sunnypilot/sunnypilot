"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
from collections.abc import Callable

from cereal import custom
from openpilot.common.constants import CV
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialogV2
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import NavWidget, Widget
from openpilot.system.ui.widgets.scroller import Scroller


class ModelsLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self.original_back_callback = back_callback
    self.selecting_model = False
    self.adjusting_lane = False
    self.adjusting_delay = False
    self.selecting_folder = False
    self.current_folder = None
    self.refresh_start_time = 0

    self.current_model_btn = BigButton(tr("current model"), "", "")
    self.current_model_btn.set_click_callback(self._handle_current_model_clicked)

    self.refresh_btn = BigButton(tr("refresh model list"), "", "")
    self.refresh_btn.set_click_callback(self._handle_refresh)

    self.clear_cache_btn = BigButton(tr("clear model cache"), "", "")
    self.clear_cache_btn.set_click_callback(self._handle_clear_cache)

    self.cancel_download_btn = BigButton(tr("cancel download"), "", "")
    self.cancel_download_btn.set_click_callback(self._handle_cancel_download)

    self.lane_turn_toggle = BigToggle(text=tr("use lane turn desires"), initial_state=ui_state.params.get_bool("LaneTurnDesire"),
                                      toggle_callback=self._lane_turn_callback)

    self.lagd_toggle = BigToggle(text=tr("live learning steer delay"), initial_state=ui_state.params.get_bool("LagdToggle"),
                                 toggle_callback=self._lagd_callback)

    self.lane_turn_value_btn = BigButton(tr("adjust lane turn speed"), "", "")
    self.lane_turn_value_btn.set_click_callback(self._adjust_lane_turn)
    self.delay_btn = BigButton(tr("adjust software delay"), "", "")
    self.delay_btn.set_click_callback(self._adjust_delay)

    self.main_items: list[Widget] = [self.current_model_btn, self.cancel_download_btn, self.refresh_btn, self.clear_cache_btn, self.lane_turn_toggle,
                       self.lane_turn_value_btn, self.lagd_toggle, self.delay_btn]
    self._scroller = Scroller(self.main_items, snap_items=False)

  @property
  def model_manager(self):
    return ui_state.sm["modelManagerSP"]

  def _lane_turn_callback(self, state: bool):
    ui_state.params.put_bool("LaneTurnDesire", state)

  def _lagd_callback(self, state: bool):
    ui_state.params.put_bool("LagdToggle", state)

  def _update_state(self):
    super()._update_state()
    if self.refresh_start_time > 0 and time.monotonic() - self.refresh_start_time > 2:
      self.refresh_btn.set_text(tr("refresh model list"))
      self.refresh_start_time = 0
    show_cancel = False

    if self.model_manager.selectedBundle and self.model_manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      active_name = f"Downloading {self.model_manager.selectedBundle.displayName.lower()}"
      show_cancel = True
    elif self.model_manager.activeBundle:
      active_name = self.model_manager.activeBundle.internalName.lower()
    else:
      active_name = tr("default model")
    self.current_model_btn.set_enabled(ui_state.is_offroad())
    self.current_model_btn.set_text(tr("current model"))
    self.current_model_btn.set_value(active_name)
    self.cancel_download_btn.set_visible(show_cancel)

    advanced_controls = ui_state.params.get_bool("ShowAdvancedControls")
    turn_desire = ui_state.params.get_bool("LaneTurnDesire")
    live_delay = ui_state.params.get_bool("LagdToggle")

    if turn_desire and advanced_controls:
      parameter_value = float(ui_state.params.get("LaneTurnValue", return_default=True))
      if ui_state.is_metric:
        display_value = int(round(parameter_value * CV.MPH_TO_KPH))
      else:
        display_value = int(round(parameter_value))
      unit = 'km/h' if ui_state.is_metric else 'mph'
      self.lane_turn_value_btn.set_text(tr("adjust lane turn speed"))
      self.lane_turn_value_btn.set_value(f"{display_value} {unit}")
      self.lane_turn_value_btn.set_visible(True)
    else:
      self.lane_turn_value_btn.set_visible(False)

    if not live_delay and advanced_controls:
      software_delay = float(ui_state.params.get("LagdToggleDelay", return_default=True))
      self.delay_btn.set_text(tr("adjust software delay"))
      self.delay_btn.set_value(f"{software_delay:.2f}s")
      self.delay_btn.set_visible(True)
    else:
      self.delay_btn.set_visible(False)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    ui_state.update_params()

  def _render(self, rect):
    self._scroller.render(rect)

  def _get_grouped_bundles(self):
    bundles = self.model_manager.availableBundles
    folders = {}
    for bundle in bundles:
      folder = next((override.value for override in bundle.overrides if override.key == "folder"), "")
      folders.setdefault(folder, []).append(bundle)
    return folders

  def _handle_current_model_clicked(self):
    if self.selecting_model:
      return
    self.selecting_model = True
    self._show_folders()

  def _show_folders(self):
    self.selecting_folder = True
    folders = self._get_grouped_bundles()
    folder_buttons = []
    default_btn = BigButton(tr("default model"), "", "")
    default_btn.set_click_callback(self._select_default)
    folder_buttons.append(default_btn)

    for folder in sorted(folders.keys(), key=lambda f: max((b.index for b in folders[f]), default=-1), reverse=True):
      if folder:
        btn = BigButton(folder.lower(), "", "")
        btn.set_click_callback(lambda f=folder: self._select_folder(f))
        folder_buttons.append(btn)

    self._scroller._items = folder_buttons
    for item in folder_buttons:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(self._back_from_selection)

  def _handle_refresh(self):
    self.refresh_btn.set_text(tr("refreshing..."))
    self.refresh_start_time = time.monotonic()
    ui_state.params.put("ModelManager_LastSyncTime", 0)

  def _handle_clear_cache(self):
    gui_app.set_modal_overlay(BigConfirmationDialogV2(tr("clear model cache?"), "icons_mici/settings/device/update.png",
                                                      confirm_callback=lambda: ui_state.params.put_bool("ModelManager_ClearCache", True)))

  def _handle_cancel_download(self):
    ui_state.params.remove("ModelManager_DownloadIndex")

  def _select_model(self, bundle):
    ui_state.params.put("ModelManager_DownloadIndex", bundle.index)
    self._reset_main_view()

  def _select_default(self):
    ui_state.params.remove("ModelManager_ActiveBundle")
    self._reset_main_view()

  def _select_folder(self, folder_name):
    self.selecting_folder = False
    self.current_folder = folder_name

    folders = self._get_grouped_bundles()
    bundles_in_folder = folders.get(folder_name, [])
    bundles_in_folder.sort(key=lambda b: b.index, reverse=True)

    bundle_buttons = []
    for bundle in bundles_in_folder:
      text = bundle.displayName.lower()
      btn = BigButton(text, "", "")
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      is_active = self.model_manager.activeBundle and self.model_manager.activeBundle.index == bundle.index
      is_downloaded = False
      if bundle.status in (custom.ModelManagerSP.DownloadStatus.downloaded, custom.ModelManagerSP.DownloadStatus.cached):
        is_downloaded = True

      if is_active:
        btn.set_text(text + " (Active)")
      elif is_downloaded:
        btn.set_text(text + " (Cached)")

      bundle_buttons.append(btn)

    self._scroller._items = bundle_buttons
    for item in bundle_buttons:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(self._back_from_selection)

  def _reset_main_view(self):
    self.selecting_model = False
    self.adjusting_lane = False
    self.adjusting_delay = False
    self.selecting_folder = False
    self.current_folder = None
    self._scroller._items = self.main_items
    self.set_back_callback(self.original_back_callback)

  def _back_from_selection(self):
    if self.selecting_folder:
      self._reset_main_view()
    else:
      self._show_folders()

  def _adjust_lane_turn(self):
    if self.adjusting_lane:
      return
    self.adjusting_lane = True
    parameter_value = float(ui_state.params.get("LaneTurnValue", return_default=True))
    if ui_state.is_metric:
      current_display = int(round(parameter_value * CV.MPH_TO_KPH))
    else:
      current_display = int(round(parameter_value))
    values = [5, 10, 15, 20] if not ui_state.is_metric else [8, 16, 24, 32]
    adjust_buttons = []
    for value in values:
      unit = 'mph' if not ui_state.is_metric else 'km/h'
      suffix = " (current)" if value == current_display else ""
      btn = BigButton(f"{value} {unit}{suffix}", "", "")
      btn.set_click_callback(lambda v=value: self._set_lane_turn(v))
      adjust_buttons.append(btn)
    self._scroller._items = adjust_buttons
    for item in adjust_buttons:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(self._reset_main_view)

  def _set_lane_turn(self, value):
    if ui_state.is_metric:
      parameter_value = value / CV.MPH_TO_KPH
    else:
      parameter_value = float(value)
    ui_state.params.put("LaneTurnValue", parameter_value)
    self._reset_main_view()

  def _adjust_delay(self):
    if self.adjusting_delay:
      return
    self.adjusting_delay = True
    current_software_delay = float(ui_state.params.get("LagdToggleDelay", return_default=True))
    values = [round(i * 0.01, 2) for i in range(10, 31)]  # 0.10 to 0.30 in 0.01 increments
    adjust_buttons = []
    for value in values:
      suffix = " (current)" if value == current_software_delay else ""
      btn = BigButton(f"{value:.2f}s{suffix}", "", "")
      btn.set_click_callback(lambda v=value: self._set_delay(v))
      adjust_buttons.append(btn)
    self._scroller._items = adjust_buttons
    for item in adjust_buttons:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(self._reset_main_view)

  def _set_delay(self, value):
    ui_state.params.put("LagdToggleDelay", value)
    self._reset_main_view()
