"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
import pyray as rl

from openpilot.cereal import custom
from openpilot.sunnypilot.models.default_model import DEFAULT_MODEL
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.scroller import NavScroller

def _build_folders() -> dict[str, list]:
  manager = ui_state.sm["modelManagerSP"]
  bundles = manager.availableBundles
  folders = {}
  for bundle in bundles:
    folder = next((override.value for override in bundle.overrides if override.key == "folder"), "")
    folders.setdefault(folder, []).append(bundle)

  favs = ui_state.params.get("ModelManager_Favs")
  favorites = set(favs.split(';')) if favs else set()

  if favorites:
    for fav_bundle in [bundle for bundle in bundles if bundle.ref in favorites]:
      folders.setdefault("favorites", []).append(fav_bundle)

  return folders


class CurrentModelInfo(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    self.current_model_header = UnifiedLabel(tr("active model"), 48, max_width=max_width, text_color=header_color, font_weight=FontWeight.DISPLAY)
    default_text = f"{DEFAULT_MODEL} (Default)".lower()
    self.current_model_text = UnifiedLabel(default_text, 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN, scroll=True)

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


class FolderSelectionMici(NavScroller):
  def __init__(self, select_default_cb: Callable, select_folder_cb: Callable):
    super().__init__()

    folders = _build_folders()
    folder_buttons = []
    default_btn = BigButton(f"{DEFAULT_MODEL} (Default)".lower())
    default_btn.set_click_callback(select_default_cb)
    folder_buttons.append(default_btn)

    for folder in sorted(folders.keys(), key=lambda f: max((bundle.index for bundle in folders[f]), default=-1), reverse=True):
      btn = BigButton(folder.lower())
      btn.set_click_callback(lambda f=folder: select_folder_cb(f))
      if folder.lower() == "favorites":
        folder_buttons.insert(0, btn)
      else:
        folder_buttons.append(btn)

    self._scroller.add_widgets(folder_buttons)


class ModelSelectionMici(NavScroller):
  def __init__(self, folder_name: str, select_model_cb: Callable):
    super().__init__()

    folders = _build_folders()
    bundles_in_folder = sorted(folders.get(folder_name, []), key=lambda b: b.index, reverse=True)

    btns = []
    for bundle in bundles_in_folder:
      txt = bundle.displayName.lower()
      btn = BigButton(txt)
      btn.set_click_callback(lambda b=bundle: select_model_cb(b))
      btns.append(btn)

    self._scroller.add_widgets(btns)


class ModelsLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self.focused_widget = None

    self.current_model_info = CurrentModelInfo()
    self._download_progress = "."
    self._download_frame = 0
    self._was_downloading = False

    self.select_model_btn = BigButton(tr("select model"))
    self.select_model_btn.set_click_callback(self._show_folders)

    self.clear_cache_btn = BigButton(tr("clear cache"), "")
    self.clear_cache_btn.set_click_callback(self._clear_cache)

    self.cancel_download_btn = BigButton(tr("cancel download"))
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadIndex"))

    self.main_items = [self.current_model_info, self.select_model_btn, self.clear_cache_btn, self.cancel_download_btn]
    self._scroller.add_widgets(self.main_items)

  @property
  def model_manager(self):
    return ui_state.sm["modelManagerSP"]

  def _show_folders(self):
    self.focused_widget = self.select_model_btn

    def select_default():
      ui_state.params.remove("ModelManager_ActiveBundle")
      gui_app.pop_widgets_to(self, instant=True)
      self._scroller.scroll_panel.set_offset(0)
      self._scroller.scroll_to(0)

    def select_folder(folder_name):
      def select_model(bundle):
        ui_state.params.put("ModelManager_DownloadIndex", bundle.index)
        gui_app.pop_widgets_to(self, instant=True)
        self._scroller.scroll_panel.set_offset(0)
        self._scroller.scroll_to(0)

      model_selection = ModelSelectionMici(folder_name, select_model)
      gui_app.push_widget(model_selection)

    folder_selection = FolderSelectionMici(select_default, select_folder)
    gui_app.push_widget(folder_selection)

  def _clear_cache(self):
    def confirm_callback():
      ui_state.params.put_bool("ModelManager_ClearCache", True)

    lbl = tr("slide to clear cache")
    icon = gui_app.texture("icons_mici/settings/device/uninstall.png", 64, 64)
    dlg = BigConfirmationDialog(lbl, icon, confirm_callback=confirm_callback, red=True)
    gui_app.push_widget(dlg)

  def hide_event(self):
    super().hide_event()
    if self._was_downloading:
      device.set_override_interactive_timeout(None)
      self._was_downloading = False

  def _update_state(self):
    super()._update_state()

    self.select_model_btn.set_enabled(ui_state.is_offroad())
    self.clear_cache_btn.set_enabled(ui_state.is_offroad())
    self.cancel_download_btn.set_visible(False)
    self.current_model_info.current_model_header._shimmer = False
    self.current_model_info.info_header._shimmer = False

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
    model_text = manager.activeBundle.displayName.lower() if manager.activeBundle.ref else f"{DEFAULT_MODEL} (Default)".lower()
    self.current_model_info.current_model_text.set_text(model_text)
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
      self.current_model_info.current_model_header._shimmer = True
      self.current_model_info.current_model_text.set_text(f"{manager.selectedBundle.internalName.lower()}")
      self.current_model_info.info_header.set_text(tr("progress") + self._download_progress)
      self.current_model_info.info_header._shimmer = True
      self.current_model_info.info_text.set_text(f"{progress/count:.2f}%")
