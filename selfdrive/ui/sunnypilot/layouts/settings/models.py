import os
import re
import time
import pyray as rl

from cereal import custom
from openpilot.common.params import Params
from openpilot.common.constants import CV
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.list_view import button_item, ButtonAction, ListItem
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets.toggle import ON_COLOR

from openpilot.sunnypilot.models.runners.constants import CUSTOM_MODEL_PATH
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp
from openpilot.system.ui.sunnypilot.widgets.progress_bar import progress_item
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeOptionDialog, TreeNode, TreeFolder
from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp


class NoElide(ButtonAction):
  def get_width_hint(self):
    return super().get_width_hint() + 20


class ModelsLayout(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()
    self.model_manager = None
    self.download_status = None
    self.prev_download_status = None
    self.model_dialog = None
    self.last_cache_calc_time = 0
    self.cached_size = 0.0

    self.current_model_item = ListItem(tr("Current Model"), "", action_item=NoElide(tr("Select"), enabled=True), callback=self._handle_current_model_clicked)

    self.supercombo_label = progress_item(tr("Driving Model"))
    self.vision_label = progress_item(tr("Vision Model"))
    self.policy_label = progress_item(tr("Policy Model"))

    self.refresh_item = button_item(tr("Refresh Model List"), tr("Refresh"), "", lambda: (
      self._params.put("ModelManager_LastSyncTime", 0),
      gui_app.set_modal_overlay(alert_dialog(tr("Fetching Latest Models")))
    ))
    self.clear_cache_item = ListItem(tr("Clear Model Cache"), "", action_item=NoElide(tr("Clear"), enabled=True), callback=self._clear_cache)
    self.cancel_download_item = button_item(tr("Cancel Download"), tr("Cancel"), "", lambda: self._params.remove("ModelManager_DownloadIndex"))

    self.lane_turn_value_control = option_item_sp(tr("Adjust Lane Turn Speed"), "LaneTurnValue", 500, 2000,
      tr("Set the maximum speed for lane turn desires. Default is 19 mph."),
      int(round(100 / CV.MPH_TO_KPH)), None, True, "", style.BUTTON_WIDTH, None, True,
      lambda v: f"{int(round(v / 100 * (CV.MPH_TO_KPH if self._params.get_bool('IsMetric') else 1)))} {'km/h' if self._params.get_bool('IsMetric') else 'mph'}")

    self.lane_turn_desire_toggle = toggle_item_sp(tr("Use Lane Turn Desires"),
      tr("If you're driving at 20 mph (32 km/h) or below and have your blinker on, the car will plan a turn in that direction at the nearest drivable path. " +
         "This prevents situations (like at red lights) where the car might plan the wrong turn direction."),
      callback=lambda s: self.lane_turn_value_control.set_visible(s), param="LaneTurnDesire")

    self.delay_control = option_item_sp(tr("Adjust Software Delay"), "LagdToggleDelay", 5, 50,
      tr("Adjust the software delay when Live Learning Steer Delay is toggled off. The default software delay value is 0.2"),
      1, None, True, "", style.BUTTON_WIDTH, None, True, lambda v: f"{v/100:.2f}s")

    self.lagd_toggle = toggle_item_sp(tr("Live Learning Steer Delay"), "",
      callback=lambda s: (self.delay_control.set_visible(not s), self._update_lagd_description()), param="LagdToggle")

    self.items = [self.current_model_item, self.cancel_download_item, self.supercombo_label, self.vision_label,
                  self.policy_label, self.refresh_item, self.clear_cache_item, self.lane_turn_desire_toggle,
                  self.lane_turn_value_control, self.lagd_toggle, self.delay_control]

    self.lane_turn_value_control.set_visible(self._params.get_bool("LaneTurnDesire"))
    self.delay_control.set_visible(not self._params.get_bool("LagdToggle"))

    for ctrl, key, default in [(self.lane_turn_value_control, "LaneTurnValue", "19.0"), (self.delay_control, "LagdToggleDelay", "0.2")]:
      ctrl.action_item.set_value(int(float(self._params.get(key, default)) * 100))

    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _update_lagd_description(self):
    desc = tr("Enable this for the car to learn and adapt its steering response time. Disable to use a fixed steering response time. " +
              "Keeping this on provides the stock openpilot experience.")
    if self._params.get_bool("LagdToggle"):
      desc += f"<br>{tr('Live Steer Delay:')} {ui_state_sp.sm['liveDelay'].lateralDelay:.3f} s"
    elif ui_state_sp.CP:
      sw = float(self._params.get("LagdToggleDelay", "0.2"))
      cp = ui_state_sp.CP.steerActuatorDelay
      desc += f"<br>{tr('Actuator Delay:')} {cp:.2f} s + {tr('Software Delay:')} {sw:.2f} s = {tr('Total Delay:')} {cp + sw:.2f} s"
    self.lagd_toggle.set_description(desc)

  def _handle_bundle_download_progress(self):
    labels = {custom.ModelManagerSP.Model.Type.supercombo: self.supercombo_label,
              custom.ModelManagerSP.Model.Type.vision: self.vision_label,
              custom.ModelManagerSP.Model.Type.policy: self.policy_label}
    for label in labels.values():
      label.set_visible(False)
    self.cancel_download_item.set_visible(False)

    if not self.model_manager or (not self.model_manager.selectedBundle and not self.model_manager.activeBundle):
      return

    bundle = self.model_manager.selectedBundle if self._is_downloading() or (
      self.model_manager.selectedBundle and self.model_manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.failed
    ) else self.model_manager.activeBundle
    if not bundle:
      return

    self.download_status = bundle.status
    status_changed = self.prev_download_status != self.download_status
    self.prev_download_status = self.download_status
    self.cancel_download_item.set_visible(bool(self.model_manager.selectedBundle) and bool(self._params.get("ModelManager_DownloadIndex")))

    for model in bundle.models:
      if label := labels.get(getattr(model.type, 'raw', model.type)):
        label.set_visible(True)
        p = model.artifact.downloadProgress
        text, show, color = f"pending - {bundle.displayName}", False, rl.GRAY
        if p.status == custom.ModelManagerSP.DownloadStatus.downloading:
          text, show = f"{int(p.progress)}% - {bundle.displayName}", True
        elif p.status in (custom.ModelManagerSP.DownloadStatus.downloaded, custom.ModelManagerSP.DownloadStatus.cached):
          status_text = tr('from cache' if p.status == custom.ModelManagerSP.DownloadStatus.cached else 'downloaded')
          text, color = f"{bundle.displayName} - {status_text if status_changed else tr('ready')}", ON_COLOR
        elif p.status == custom.ModelManagerSP.DownloadStatus.failed:
          text, color = f"download failed - {bundle.displayName}", rl.RED
        label.action_item.update(p.progress, text, show, color)

  def _is_downloading(self):
    return (self.model_manager and self.model_manager.selectedBundle and
            self.model_manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading)

  def _bundle_to_node(self, bundle):
    return TreeNode(bundle.ref, {'display_name': bundle.displayName, 'short_name': bundle.internalName})

  def _get_folders(self, favorites):
    bundles = self.model_manager.availableBundles
    folders = {}
    for bundle in bundles:
      folders.setdefault(next((ov_ride.value for ov_ride in bundle.overrides if ov_ride.key == "folder"), ""), []).append(bundle)

    folders_list = [TreeFolder("", [TreeNode("Default", {'display_name': tr("Default Model"), 'short_name': "Default"})])]
    for folder, folder_bundles in sorted(folders.items(), key=lambda x: max((bundle.index for bundle in x[1]), default=-1), reverse=True):
      folder_bundles.sort(key=lambda bundle: bundle.index, reverse=True)
      name = folder + (f" - (Updated: {m.group(1)})" if folder_bundles and (m := re.search(r'\(([^)]*)\)[^(]*$', folder_bundles[0].displayName)) else "")
      folders_list.append(TreeFolder(name, [self._bundle_to_node(bundle) for bundle in folder_bundles]))

    if favorites and (fav_bundles := [bundle for bundle in bundles if bundle.ref in favorites]):
      folders_list.insert(1, TreeFolder("Favorites", [self._bundle_to_node(bundle) for bundle in fav_bundles]))
    return folders_list

  def _on_model_selected(self, result):
    if result != DialogResult.CONFIRM:
      return
    selected_ref = self.model_dialog.selection_ref
    if selected_ref == "Default":
      self._params.remove("ModelManager_ActiveBundle")
      self._show_reset_params_dialog()
    elif (selected_bundle := next((bundle for bundle in self.model_manager.availableBundles if bundle.ref == selected_ref), None)):
      self._params.put("ModelManager_DownloadIndex", selected_bundle.index)
      if self.model_manager.activeBundle and selected_bundle.generation != self.model_manager.activeBundle.generation:
        self._show_reset_params_dialog()
    self.model_dialog = None

  def _handle_current_model_clicked(self):
    favs = self._params.get("ModelManager_Favs")
    favorites = set(favs.split(';')) if favs else set()
    folders_list = self._get_folders(favorites)

    active_ref = self.model_manager.activeBundle.ref if self.model_manager.activeBundle else "Default"
    self.model_dialog = TreeOptionDialog(tr("Select a Model"), folders_list, active_ref, "ModelManager_Favs",
                                          search_prompt=tr("Click here to search for a model"),
                                          get_folders_fn=self._get_folders, on_exit=self._on_model_selected)
    gui_app.set_modal_overlay(self.model_dialog, callback=self._on_model_selected)

  def _clear_cache(self):
    def _callback(response):
      if response == DialogResult.CONFIRM:
        self._params.put_bool("ModelManager_ClearCache", True)
    gui_app.set_modal_overlay(ConfirmDialog(tr("This will delete ALL downloaded models from the cache except the currently active model. Are you sure?"),
                                            tr("Clear Cache"), tr("Cancel")), callback=_callback)

  def _show_reset_params_dialog(self):
    def _callback(response):
      if response == DialogResult.CONFIRM:
        self._params.remove("CalibrationParams")
        self._params.remove("LiveTorqueParameters")
    msg = tr("Model download has started in the background. We suggest resetting calibration. Would you like to do that now?")
    gui_app.set_modal_overlay(ConfirmDialog(msg, tr("Reset Calibration"), tr("Cancel")), callback=_callback)

  def _calculate_cache_size(self):
    if (_time := time.monotonic()) - self.last_cache_calc_time > 0.2:
      self.last_cache_calc_time = _time
      self.cached_size = 0
      if os.path.exists(CUSTOM_MODEL_PATH):
        self.cached_size = sum(os.path.getsize(os.path.join(CUSTOM_MODEL_PATH, file)) for file in os.listdir(CUSTOM_MODEL_PATH)) / (1024**2)
    return self.cached_size

  def _update_state(self):
    new_step = int(round(100 / CV.MPH_TO_KPH)) if self._params.get_bool("IsMetric") else 100
    if self.lane_turn_value_control.action_item.value_change_step != new_step:
      self.lane_turn_value_control.action_item.value_change_step = new_step

    self.model_manager = ui_state_sp.sm["modelManagerSP"]
    self._handle_bundle_download_progress()
    active_name = self.model_manager.activeBundle.internalName if self.model_manager and self.model_manager.activeBundle.ref else "Default Model"
    self.current_model_item.action_item.set_value(active_name)
    self.clear_cache_item.action_item.set_value(f"{self._calculate_cache_size():.2f} MB")
    self._update_lagd_description()

    if not ui_state_sp.is_offroad():
      self.current_model_item.action_item.set_enabled(False)
      self.current_model_item.set_description(tr("Only available when vehicle is off, or always offroad mode is on"))
    else:
      self.current_model_item.action_item.set_enabled(True)
      self.current_model_item.set_description("")

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
