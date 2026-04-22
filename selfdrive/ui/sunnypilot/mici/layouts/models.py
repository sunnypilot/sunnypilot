"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
import os
import pyray as rl

from cereal import custom
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.sunnypilot.models.runners.constants import CUSTOM_MODEL_PATH
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel, TextEffect
from openpilot.system.ui.widgets.scroller import NavScroller

class CurrentModelInfo(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    self.current_model_header = UnifiedLabel(tr("active model"), 48, max_width=max_width, text_color=header_color, font_weight=FontWeight.DISPLAY)
    self.current_model_text = UnifiedLabel(tr("default model"), 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN, scroll=True)

    self.info_header = UnifiedLabel("cache size", 48, max_width=max_width, text_color=header_color, font_weight=FontWeight.DISPLAY)
    self.info_text = UnifiedLabel("0 mb", 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN)

  def _render(self, _):
    self.current_model_header.set_position(self._rect.x + 20, self._rect.y - 10)
    self.current_model_header.render()

    self.current_model_text.set_position(self._rect.x + 20, self._rect.y + 68 - 25)
    self.current_model_text.render()

    self.info_header.set_position(self._rect.x + 20, self._rect.y + 114 - 30)
    self.info_header.render()

    self.info_text.set_position(self._rect.x + 20, self._rect.y + 161 - 25)
    self.info_text.render()

class ModelsLayoutMici(NavScroller):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self.original_back_callback = back_callback
    self.focused_widget = None

    self.current_model_info = CurrentModelInfo()
    self._download_progress = "."
    self._download_frame = 0
    self._was_downloading = False

    self.cached_models_btn = BigButton(tr("cached models"))
    self.cached_models_btn.set_click_callback(self._show_cached_models)

    self.download_models_btn = BigButton(tr("download models"))
    self.download_models_btn.set_click_callback(self._show_download_models)

    self.default_btn = BigButton(tr("default model"))
    self.default_btn.set_click_callback(self._select_default)

    self.cancel_download_btn = BigButton(tr("cancel download"))
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadIndex"))

    self.main_items = [self.current_model_info, self.cached_models_btn, self.download_models_btn, self.default_btn, self.cancel_download_btn]
    self._scroller.add_widgets(self.main_items)

  @property
  def model_manager(self):
    return ui_state.sm["modelManagerSP"]

  def _is_bundle_cached(self, bundle):
    for model in bundle.models:
      artifact_path = os.path.join(CUSTOM_MODEL_PATH, model.artifact.fileName)
      if not os.path.exists(artifact_path):
        return False
      if hasattr(model, 'metadata') and model.metadata.fileName:
        metadata_path = os.path.join(CUSTOM_MODEL_PATH, model.metadata.fileName)
        if not os.path.exists(metadata_path):
          return False
    return True

  def _get_grouped_bundles(self, favorites=None, uncached_only=False):
    bundles = self.model_manager.availableBundles
    if uncached_only:
      bundles = [b for b in bundles if not self._is_bundle_cached(b)]

    folders = {}
    for bundle in bundles:
      folder = next((override.value for override in bundle.overrides if override.key == "folder"), "")
      folders.setdefault(folder, []).append(bundle)

    if favorites:
      fav_bundles = [bundle for bundle in self.model_manager.availableBundles if bundle.ref in favorites]
      if uncached_only:
        fav_bundles = [b for b in fav_bundles if not self._is_bundle_cached(b)]

      if fav_bundles:
        folders["favorites"] = fav_bundles

    return folders

  def _show_selection_view(self, items, back_callback: Callable):
    self._scroller._items = items
    for item in items:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(back_callback)

  def _show_cached_models(self):
    self.focused_widget = self.cached_models_btn
    bundles = [b for b in self.model_manager.availableBundles if self._is_bundle_cached(b)]
    bundles.sort(key=lambda b: b.index, reverse=True)

    btns = []

    for bundle in bundles:
      txt = bundle.displayName.lower()
      btn = BigButton(txt)
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      btns.append(btn)
    self._show_selection_view(btns, self._reset_main_view)

  def _show_download_models(self):
    self.focused_widget = self.download_models_btn

    favs = ui_state.params.get("ModelManager_Favs")
    favorites = set(favs.split(';')) if favs else set()

    folders = self._get_grouped_bundles(favorites, uncached_only=True)
    folder_buttons = []

    for folder in sorted(folders.keys(), key=lambda f: max((bundle.index for bundle in folders[f]), default=-1), reverse=True):
      if folder.lower() in ["release models", "master models", "favorites"]:
        btn = BigButton(folder.lower())
        btn.set_click_callback(lambda f=folder: self._select_folder(f, uncached_only=True))
        if folder.lower() == "favorites":
          folder_buttons.insert(0, btn)
        else:
          folder_buttons.append(btn)
    self._show_selection_view(folder_buttons, self._reset_main_view)

  def _select_model(self, bundle):
    ui_state.params.put("ModelManager_DownloadIndex", bundle.index)
    self._reset_main_view()

  def _select_default(self):
    ui_state.params.remove("ModelManager_ActiveBundle")
    self._reset_main_view()

  def _select_folder(self, folder_name, uncached_only=False):
    favs = ui_state.params.get("ModelManager_Favs")
    favorites = set(favs.split(';')) if favs else set()

    folders = self._get_grouped_bundles(favorites, uncached_only=uncached_only)
    bundles = sorted(folders.get(folder_name, []), key=lambda b: b.index, reverse=True)

    btns = []
    for bundle in bundles:
      txt = bundle.displayName.lower()
      btn = BigButton(txt)
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      btns.append(btn)
    self._show_selection_view(btns, self._show_download_models)

  def _reset_main_view(self):
    self._scroller._items = self.main_items
    self.set_back_callback(self.original_back_callback)
    self._scroller.scroll_panel.set_offset(0)
    self._scroller.scroll_to(0)

  def hide_event(self):
    super().hide_event()
    if self._was_downloading:
      device.set_override_interactive_timeout(None)
      self._was_downloading = False

  def _update_state(self):
    super()._update_state()

    self.cached_models_btn.set_enabled(ui_state.is_offroad())
    self.download_models_btn.set_enabled(ui_state.is_offroad())
    self.default_btn.set_enabled(ui_state.is_offroad())
    self.cancel_download_btn.set_visible(False)
    self.current_model_info.current_model_header.set_effect(TextEffect.NONE)
    self.current_model_info.info_header.set_effect(TextEffect.NONE)

    manager = self.model_manager
    self._download_frame += 1
    should_update = self._download_frame % (gui_app.target_fps / 2) == 0
    if should_update:
      self._download_progress = self._download_progress + "." if len(self._download_progress) < 3 else ""

    is_downloading = (manager.selectedBundle
                      and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading)
    if self._was_downloading and not is_downloading:
      device.set_override_interactive_timeout(None)
    self._was_downloading = is_downloading

    self.current_model_info.current_model_header.set_text(tr("active model"))
    self.current_model_info.current_model_text.set_text(manager.activeBundle.displayName.lower() if manager.activeBundle.index > 0 else tr("default model"))
    self.current_model_info.info_header.set_text(tr("cache size"))
    self.current_model_info.info_text.set_text(f"{ModelsLayout.calculate_cache_size():.2f} MB")

    if manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.failed:
      self.current_model_info.info_header.set_text(tr("error") + self._download_progress)
      self.current_model_info.info_text.set_text(tr("download failed"))

    elif manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      self.cancel_download_btn.set_visible(True)
      device.set_override_interactive_timeout(5)
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
      self.current_model_info.current_model_header.set_effect(TextEffect.SHIMMER)
      self.current_model_info.current_model_text.set_text(f"{manager.selectedBundle.internalName.lower()}")
      self.current_model_info.info_header.set_text(tr("progress") + self._download_progress)
      self.current_model_info.info_header.set_effect(TextEffect.SHIMMER)
      self.current_model_info.info_text.set_text(f"{progress/count:.2f}%")

