"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

from cereal import custom
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import NavWidget, Widget
from openpilot.system.ui.widgets.scroller import Scroller


class ModelsLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self.original_back_callback = back_callback
    self.focused_widget = None

    self.current_model_btn = BigButton(tr("current model"), "", "")
    self.current_model_btn.set_click_callback(self._show_folders)

    self.cancel_download_btn = BigButton(tr("cancel download"), "", "")
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadIndex"))

    self.main_items: list[Widget] = [self.current_model_btn, self.cancel_download_btn]
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

  def _update_state(self):
    super()._update_state()

    manager = self.model_manager
    if manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      self.current_model_btn.set_value("downloading...")
      self.cancel_download_btn.set_visible(True)
    else:
      self.current_model_btn.set_value(manager.activeBundle.internalName.lower() if manager.activeBundle else tr("default model"))
      self.cancel_download_btn.set_visible(False)
    self.current_model_btn.set_enabled(ui_state.is_offroad())
    self.current_model_btn.set_text(tr("current model"))

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
