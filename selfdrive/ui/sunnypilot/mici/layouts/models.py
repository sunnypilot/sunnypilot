"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
import pyray as rl

from cereal import custom
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import NavWidget, Widget
from openpilot.system.ui.widgets.label import MiciLabel
from openpilot.system.ui.widgets.scroller import Scroller

class CurrentModelInfo(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    self.current_model_header = MiciLabel(tr("active model"), 48, width=max_width, color=header_color, font_weight=FontWeight.DISPLAY)
    self.current_model_text = MiciLabel(tr("default model"), 32, width=max_width, color=subheader_color, font_weight=FontWeight.ROMAN)

    self.info_header = MiciLabel("", 48, color=header_color, font_weight=FontWeight.DISPLAY)
    self.info_text = MiciLabel("", 32, width=max_width, color=subheader_color, font_weight=FontWeight.ROMAN)

  def _render(self, _):
    self.current_model_header.set_position(self._rect.x + 20, self._rect.y - 10)
    self.current_model_header.render()

    self.current_model_text.set_position(self._rect.x + 20, self._rect.y + 68 - 25)
    self.current_model_text.render()

    self.info_header.set_position(self._rect.x + 20, self._rect.y + 114 - 30)
    self.info_header.render()

    self.info_text.set_position(self._rect.x + 20, self._rect.y + 161 - 25)
    self.info_text.render()

class ModelsLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self.original_back_callback = back_callback
    self.focused_widget = None

    self.current_model_info = CurrentModelInfo()
    self._download_progress = "."
    self._download_frame = 0

    self.select_model_btn = BigButton(tr("select model"), "", "")
    self.select_model_btn.set_click_callback(self._show_folders)

    self.cancel_download_btn = BigButton(tr("cancel download"), "", "")
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadIndex"))

    self.main_items: list[Widget] = [
      self.current_model_info,
      self.select_model_btn,
      self.cancel_download_btn
    ]

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
    self.focused_widget = self.select_model_btn
    folders = self._get_grouped_bundles()
    folder_buttons = []
    default_btn = BigButton(tr("default model"), "", "")
    default_btn.set_click_callback(self._select_default)
    folder_buttons.append(default_btn)

    for folder in sorted(folders.keys(), key=lambda f: max((bundle.index for bundle in folders[f]), default=-1), reverse=True):
      if folder.lower() in ["release models", "master models"]:
        btn = BigButton(folder.lower(), "", "")
        btn.set_click_callback(lambda f=folder: self._select_folder(f))
        folder_buttons.append(btn)
    self._show_selection_view(folder_buttons, self._reset_main_view)

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
      btn = BigButton(txt, "", "")
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      btns.append(btn)
    self._show_selection_view(btns, self._show_folders)

  def _reset_main_view(self):
    self._scroller._items = self.main_items
    self.set_back_callback(self.original_back_callback)
    self._scroller.scroll_panel.set_offset(0)
    self._scroller.scroll_to(0)

  def _update_state(self):
    super()._update_state()

    self.select_model_btn.set_enabled(ui_state.is_offroad())
    self.cancel_download_btn.set_visible(False)

    manager = self.model_manager
    self._download_frame += 1
    should_update = self._download_frame % (gui_app.target_fps / 2) == 0
    if should_update:
      self._download_progress = self._download_progress + "." if len(self._download_progress) < 3 else ""

    self.current_model_info.current_model_header.set_text(tr("active model"))
    self.current_model_info.current_model_text.set_text(manager.activeBundle.internalName.lower() if manager.activeBundle.index > 0 else tr("default model"))
    self.current_model_info.info_header.set_text(tr("cache size"))
    self.current_model_info.info_text.set_text(f"{ModelsLayout.calculate_cache_size():.2f} MB")

    if manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.failed:
      self.current_model_info.info_header.set_text(tr("error") + self._download_progress)
      self.current_model_info.info_text.set_text(tr("download failed"))

    elif manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      self.cancel_download_btn.set_visible(True)
      progress = 0.0
      count = 0
      for model in manager.selectedBundle.models:
        count += 1
        p = model.artifact.downloadProgress
        if p.status == custom.ModelManagerSP.DownloadStatus.downloading:
          progress += p.progress
        elif p.status in (custom.ModelManagerSP.DownloadStatus.downloaded,
                          custom.ModelManagerSP.DownloadStatus.cached):
          progress += 100.0

      self.current_model_info.current_model_header.set_text(tr("downloading"))
      self.current_model_info.current_model_text.set_text(f"{manager.selectedBundle.internalName.lower()}")
      self.current_model_info.info_header.set_text(tr("progress") + self._download_progress)
      self.current_model_info.info_text.set_text(f"{progress/count:.2f}%")


  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
