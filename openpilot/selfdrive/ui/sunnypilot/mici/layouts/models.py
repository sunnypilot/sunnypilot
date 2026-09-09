"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.cereal import custom
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog
from openpilot.sunnypilot.models.helpers import ACTIVE_BUNDLE_KEYS, get_selected_bundle
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.selfdrive.ui.sunnypilot.model_info import (active_source, big_model_state, bundles_for_source, carrying_model,
                                                           default_model_name, model_info, queued_name)
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.scroller import NavScroller

def _model_info() -> tuple[str, str, str]:
  """(active model, info header, info text) for the panel. Runner-matched: the
  active line names what actually drives, and a notable big-model state takes
  the info pair."""
  source, active_name, other_name = model_info()
  state = big_model_state()
  _, _, carry_display = carrying_model()
  if carry_display is None:
    big = get_selected_bundle(ui_state.params, "chestnut")
    carry_display = big.displayName if big else default_model_name("chestnut")
  active_text = (carry_display or active_name).lower()
  if state == 'failed':
    return active_text, tr("big model"), tr("unavailable")
  if state == 'loading':
    return active_text, tr("big model"), tr("getting ready")
  header = tr("small model") if source == "chestnut" else tr("big model")
  return active_text, header, other_name.lower()


class CurrentModelInfo(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    active_text, info_header, info_text = _model_info()
    self.current_model_header = UnifiedLabel(tr("active model"), 48, max_width=max_width, text_color=header_color, font_weight=FontWeight.DISPLAY)
    self.current_model_text = UnifiedLabel(active_text, 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN, scroll=True)

    self.info_header = UnifiedLabel(info_header, 48, max_width=max_width, text_color=header_color, font_weight=FontWeight.DISPLAY)
    self.info_text = UnifiedLabel(info_text, 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN, scroll=True)

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
  def __init__(self):
    super().__init__()
    self.focused_widget = None

    self.current_model_info = CurrentModelInfo()
    self._download_progress = "."
    self._download_frame = 0
    self._was_downloading = False
    self._selection_source: str | None = None

    self.select_model_btn = BigButton(tr("select model"))
    self.select_model_btn.set_click_callback(self._show_folders)

    self.cancel_download_btn = BigButton(tr("cancel download"))
    self.cancel_download_btn.set_click_callback(lambda: ui_state.params.remove("ModelManager_DownloadRef"))

    self.main_items = [self.current_model_info, self.select_model_btn, self.cancel_download_btn]
    self._scroller.add_widgets(self.main_items)

  @property
  def model_manager(self):
    return ui_state.sm["modelManagerSP"]

  def _get_grouped_bundles(self, bundles, favorites = None):
    folders = {}
    for bundle in bundles:
      folder = next((override.value for override in bundle.overrides if override.key == "folder"), "")
      folders.setdefault(folder, []).append(bundle)

    if favorites:
      for fav_bundle in [bundle for bundle in bundles if bundle.ref in favorites]:
        folders.setdefault("favorites", []).append(fav_bundle)

    return folders

  def _push_selection_view(self, items):
    scroller = NavScroller()
    scroller._scroller.add_widgets(items)
    gui_app.push_widget(scroller)

  def _show_folders(self):
    self.focused_widget = self.select_model_btn

    hardware_btns = []
    active = active_source()
    for source, label in (("qcom", tr("small models")), ("chestnut", tr("big models"))):
      bundle = get_selected_bundle(ui_state.params, source)
      value = (bundle.internalName if bundle else default_model_name(source)).lower()
      if source == active:
        value += f" ({tr('active')})"
      btn = BigButton(label.lower(), value=value)
      btn.set_click_callback(lambda s=source: self._select_hardware(s))
      hardware_btns.append(btn)
    self._push_selection_view(hardware_btns)

  def _select_hardware(self, source):
    self._selection_source = source

    favs = ui_state.params.get("ModelManager_Favs")
    favorites = set(favs.split(';')) if favs else set()

    bundles = bundles_for_source(source)
    if not bundles:
      gui_app.push_widget(BigDialog(title=tr("No models available"),
                                    description=tr("No models are available for this hardware yet. Connect to the internet and refresh the model list.")))
      return
    folders = self._get_grouped_bundles(bundles, favorites)

    folder_buttons = []
    default_btn = BigButton(default_model_name(source).lower())
    default_btn.set_click_callback(lambda s=source: self._select_default(s))
    folder_buttons.append(default_btn)

    for folder in sorted(folders.keys(), key=lambda f: max((bundle.index for bundle in folders[f]), default=-1), reverse=True):
      btn = BigButton(folder.lower())
      btn.set_click_callback(lambda f=folder: self._select_folder(f))
      if folder.lower() == "favorites":
        folder_buttons.insert(0, btn)
      else:
        folder_buttons.append(btn)
    self._push_selection_view(folder_buttons)

  def _pop_to_main(self):
    gui_app.pop_widgets_to(self)
    self._scroller.scroll_panel.set_offset(0.0)

  def _select_model(self, bundle):
    ui_state.params.put("ModelManager_DownloadRef", bundle.ref)
    self._pop_to_main()

  def _select_default(self, source):
    ui_state.params.remove(ACTIVE_BUNDLE_KEYS[source])
    self._pop_to_main()

  def _select_folder(self, folder_name):
    source = self._selection_source
    if source is None:  # folders are only reachable after picking a hardware
      return
    favs = ui_state.params.get("ModelManager_Favs")
    favorites = set(favs.split(';')) if favs else set()

    folders = self._get_grouped_bundles(bundles_for_source(source), favorites)
    bundles = sorted(folders.get(folder_name, []), key=lambda b: b.index, reverse=True)

    btns = []
    for bundle in bundles:
      btn = BigButton(bundle.displayName.lower())
      btn.set_click_callback(lambda b=bundle: self._select_model(b))
      btns.append(btn)
    self._push_selection_view(btns)

  def hide_event(self):
    super().hide_event()
    if self._was_downloading:
      device.set_override_interactive_timeout(None)
      self._was_downloading = False

  def _update_state(self):
    super()._update_state()

    self.select_model_btn.set_enabled(ui_state.is_offroad())
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
    active_text, info_header, info_text = _model_info()
    self.current_model_info.current_model_text.set_text(active_text)
    self.current_model_info.info_header.set_text(info_header)
    self.current_model_info.info_text.set_text(info_text)

    if manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.failed:
      # a failed bundle stays on the row until the next request, so it names the model and does not animate
      self.current_model_info.info_header.set_text(tr("error"))
      self.current_model_info.info_text.set_text(f"{manager.selectedBundle.internalName.lower()}  |  {tr('download failed')}")

    elif manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading:
      self.cancel_download_btn.set_visible(True)
      device.set_override_interactive_timeout(5)
      progress = 0.0
      count = 0
      verifying = False
      speed = 0.0  # max, not sum: artifacts sharing a file mirror the same transfer, and only one file is in flight
      for model in manager.selectedBundle.models:
        count += 1
        p = model.artifact.downloadProgress
        if p.status in (custom.ModelManagerSP.DownloadStatus.downloading,
                        custom.ModelManagerSP.DownloadStatus.verifying):
          progress += p.progress
          verifying = verifying or p.status == custom.ModelManagerSP.DownloadStatus.verifying
          speed = max(speed, p.speed)
        elif p.status in (custom.ModelManagerSP.DownloadStatus.downloaded,
                          custom.ModelManagerSP.DownloadStatus.cached):
          progress += 100.0

      self.current_model_info.current_model_header.set_text(tr("verifying") if verifying else tr("downloading"))
      self.cancel_download_btn.set_text(tr("cancel verification") if verifying else tr("cancel download"))
      self.current_model_info.current_model_header._shimmer = True
      name_text = manager.selectedBundle.internalName.lower()
      if queued := queued_name(manager.selectedBundle.ref):
        name_text += f"  |  {queued.lower()} {tr('queued')}"
      self.current_model_info.current_model_text.set_text(name_text)
      self.current_model_info.info_header.set_text(tr("progress") + self._download_progress)
      self.current_model_info.info_header._shimmer = True
      progress_text = f"{progress/count:.2f}%"
      if speed > 0:
        progress_text += f"  |  {speed / 1048576:.1f} MB/s"
      self.current_model_info.info_text.set_text(progress_text)

    elif manager.selectedBundle and manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloaded:
      self.current_model_info.info_header.set_text(tr("downloaded"))
      self.current_model_info.info_text.set_text(tr("downloaded"))
