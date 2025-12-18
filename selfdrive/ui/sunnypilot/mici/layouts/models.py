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
    self.refresh_start_time = 0
    self.focused_widget = None

    self.current_model_btn = BigButton(tr("current model"), "", "")
    self.current_model_btn.set_click_callback(self._show_folders)

    self.refresh_btn = BigButton(tr("refresh model list"), "", "")
    self.refresh_btn.set_click_callback(self._handle_refresh)

    self.clear_cache_btn = BigButton(tr("clear model cache"), "", "")
    self.clear_cache_btn.set_click_callback(self._handle_clear_cache)

    self.cancel_download_btn = BigButton(tr("cancel download"), "", "")
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadIndex"))

    self.lane_turn_toggle = BigToggle(text=tr("use lane turn desires"), initial_state=ui_state.params.get_bool("LaneTurnDesire"),
                                      toggle_callback=lambda state: ui_state.params.put_bool("LaneTurnDesire", state))

    self.lagd_toggle = BigToggle(text=tr("live learning steer delay"), initial_state=ui_state.params.get_bool("LagdToggle"),
                                 toggle_callback=lambda state: ui_state.params.put_bool("LagdToggle", state))

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

  def _get_grouped_bundles(self):
    bundles = self.model_manager.availableBundles
    folders = {}
    for bundle in bundles:
      folder = next((override.value for override in bundle.overrides if override.key == "folder"), "")
      folders.setdefault(folder, []).append(bundle)
    return folders

  def _show_selection_view(self, items: list[Widget], back_callback: Callable):
    self._scroller._items = items
    for item in items:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(back_callback)

  def _show_folders(self):
    self.focused_widget = self.current_model_btn
    folders = self._get_grouped_bundles()
    folder_buttons = []
    default_btn = BigButton(tr("default model"), "", "")
    default_btn.set_click_callback(self._select_default)
    folder_buttons.append(default_btn)

    for folder in sorted(folders.keys(), key=lambda f: max((bundle.index for bundle in folders[f]), default=-1), reverse=True):
      if folder:
        btn = BigButton(folder.lower(), "", "")
        btn.set_click_callback(lambda f=folder: self._select_folder(f))
        folder_buttons.append(btn)
    self._show_selection_view(folder_buttons, self._reset_main_view)

  def _handle_refresh(self):
    self.refresh_btn.set_text(tr("refreshing..."))
    self.refresh_start_time = time.monotonic()
    ui_state.params.put("ModelManager_LastSyncTime", 0)

  def _handle_clear_cache(self):
    gui_app.set_modal_overlay(BigConfirmationDialogV2(tr("clear model cache?"), "icons_mici/settings/device/update.png",
                                                      confirm_callback=lambda: ui_state.params.put_bool("ModelManager_ClearCache", True)))

  def _select_model(self, bundle):
    ui_state.params.put("ModelManager_DownloadIndex", bundle.index)
    self._reset_main_view()

  def _select_default(self):
    ui_state.params.remove("ModelManager_ActiveBundle")
    self._reset_main_view()

  def _select_folder(self, folder_name):
    folders = self._get_grouped_bundles()
    bundles = sorted(folders.get(folder_name, []), key=lambda b: b.index, reverse=True)

    btns = []
    for bundle in bundles:
      txt = bundle.displayName.lower()
      if self.model_manager.activeBundle and self.model_manager.activeBundle.index == bundle.index:
        txt += " (active)"
      elif bundle.status in (custom.ModelManagerSP.DownloadStatus.downloaded, custom.ModelManagerSP.DownloadStatus.cached):
        txt += " (cached)"

      btn = BigButton(txt, "", "")
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      btns.append(btn)
    self._show_selection_view(btns, self._show_folders)

  def _reset_main_view(self):
    self._scroller._items = self.main_items
    self.set_back_callback(self.original_back_callback)
    if self.focused_widget and self.focused_widget in self.main_items:
      x = self._scroller._pad_start
      for item in self.main_items:
        if not item.is_visible:
          continue
        if item == self.focused_widget:
          break
        x += item.rect.width + self._scroller._spacing
      self._scroller.scroll_panel.set_offset(0)
      self._scroller.scroll_to(x)
      self.focused_widget = None
    else:
      self._scroller.scroll_panel.set_offset(0)

  def _create_buttons(self, values, current_val, label, callback):
    buttons = []
    for value in values:
      suffix = " (current)" if value == current_val else ""
      btn = BigButton(f"{label(value)}{suffix}", "", "")
      btn.set_click_callback(lambda v=value: callback(v))
      buttons.append(btn)
    return buttons

  def _adjust_lane_turn(self):
    self.focused_widget = self.lane_turn_value_btn
    lane_turn_value = float(ui_state.params.get("LaneTurnValue", return_default=True))
    is_metric = ui_state.is_metric
    cur = int(round(lane_turn_value * CV.MPH_TO_KPH)) if is_metric else int(round(lane_turn_value))
    values = [8, 16, 24, 32] if is_metric else [5, 10, 15, 20]

    btns = self._create_buttons(values, cur, lambda v: f"{v} {'km/h' if is_metric else 'mph'}", self._set_lane_turn)
    self._show_selection_view(btns, self._reset_main_view)

  def _set_lane_turn(self, value):
    val = value / CV.MPH_TO_KPH if ui_state.is_metric else float(value)
    ui_state.params.put("LaneTurnValue", val)
    self._reset_main_view()

  def _adjust_delay(self):
    self.focused_widget = self.delay_btn
    current_delay = float(ui_state.params.get("LagdToggleDelay", return_default=True))
    values = [round(i * 0.01, 2) for i in range(10, 31)]
    btns = self._create_buttons(values, current_delay, lambda v: f"{v:.2f}s", self._set_delay)
    self._show_selection_view(btns, self._reset_main_view)

  def _set_delay(self, value):
    ui_state.params.put("LagdToggleDelay", value)
    self._reset_main_view()

  def _update_state(self):
    super()._update_state()
    if self.refresh_start_time > 0 and time.monotonic() - self.refresh_start_time > 1:
      self.refresh_btn.set_text(tr("refresh model list"))
      self.refresh_start_time = 0

    manager = self.model_manager
    if manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      self.current_model_btn.set_value(f"downloading {manager.selectedBundle.displayName.lower()}")
      self.cancel_download_btn.set_visible(True)
    else:
      self.current_model_btn.set_value(manager.activeBundle.internalName.lower() if manager.activeBundle else tr("default model"))
      self.cancel_download_btn.set_visible(False)
    self.current_model_btn.set_enabled(ui_state.is_offroad())
    self.current_model_btn.set_text(tr("current model"))

    advanced_controls = ui_state.params.get_bool("ShowAdvancedControls")
    turn_desires = ui_state.params.get_bool("LaneTurnDesire")
    lagd_delay = ui_state.params.get_bool("LagdToggle")

    self.lane_turn_value_btn.set_visible(turn_desires and advanced_controls)
    if turn_desires and advanced_controls:
      lane_turn_value = float(ui_state.params.get("LaneTurnValue", return_default=True))
      val = int(round(lane_turn_value * CV.MPH_TO_KPH)) if ui_state.is_metric else int(round(lane_turn_value))
      self.lane_turn_value_btn.set_text(tr("adjust lane turn speed"))
      self.lane_turn_value_btn.set_value(f"{val} {'km/h' if ui_state.is_metric else 'mph'}")

    self.delay_btn.set_visible(not lagd_delay and advanced_controls)
    if not lagd_delay and advanced_controls:
      toggle_delay = float(ui_state.params.get("LagdToggleDelay", return_default=True))
      self.delay_btn.set_text(tr("adjust software delay"))
      self.delay_btn.set_value(f"{toggle_delay:.2f}s")

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
