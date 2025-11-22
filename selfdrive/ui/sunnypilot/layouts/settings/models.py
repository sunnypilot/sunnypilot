import os
import re
import pyray as rl

from cereal import messaging, car, custom
from openpilot.common.params import Params
from openpilot.common.constants import CV
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets.toggle import ON_COLOR
from openpilot.selfdrive.ui.ui_state import ui_state

from openpilot.sunnypilot.models.runners.constants import CUSTOM_MODEL_PATH
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp
from openpilot.system.ui.sunnypilot.widgets.progress_bar import progress_item
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeOptionDialog, TreeNode, TreeFolder


class ModelsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    self.model_manager = None
    self.download_status = None
    self.prev_download_status = None
    self.is_onroad = False
    self._initialize_items()
    self.lane_turn_value_control.set_visible(self._params.get_bool("LaneTurnDesire"))
    self.delay_control.set_visible(not self._params.get_bool("LagdToggle"))

    self._set_init_oc_value(self.lane_turn_value_control, "LaneTurnValue", "19.0")
    self._set_init_oc_value(self.delay_control, "LagdToggleDelay", "0.2")

    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self.current_model_item = button_item(tr("Current Model"), tr("Select"), "", self._handle_current_model_clicked)
    self.refresh_item = button_item(tr("Refresh Model List"), tr("Refresh"), "", self._refresh_models)
    self.clear_cache_item = button_item(tr("Clear Model Cache"), tr("Clear"), "", self._clear_cache)
    self.cancel_download_item = button_item(tr("Cancel Download"), tr("Cancel"), "", self._cancel_download)
    self.supercombo_label = progress_item(tr("Driving Model"))
    self.navigation_label = progress_item(tr("Navigation Model"))
    self.vision_label = progress_item(tr("Vision Model"))
    self.policy_label = progress_item(tr("Policy Model"))

    self.lane_turn_desire_toggle = toggle_item_sp(tr("Use Lane Turn Desires"),
      tr("If you're driving at 20 mph (32 km/h) or below and have your blinker on, the car will plan a turn in that direction at the nearest drivable path. " +
         "This prevents situations (like at red lights) where the car might plan the wrong turn direction."),
      callback=lambda s: self.lane_turn_value_control.set_visible(s), param="LaneTurnDesire")

    self.lane_turn_value_control = option_item_sp(tr("Adjust Lane Turn Speed"), "LaneTurnValue", 500, 2000,
      tr("Set the maximum speed for lane turn desires. Default is 19 mph."),
      int(round(100 / CV.MPH_TO_KPH)), None, True, "", style.BUTTON_WIDTH, None, True,
      lambda v: self._format_lane_turn_label(v / 100))

    self.lagd_toggle = toggle_item_sp(tr("Live Learning Steer Delay"), "",
      callback=lambda s: (self.delay_control.set_visible(not s), self._update_lagd_description()), param="LagdToggle")

    self.delay_control = option_item_sp(tr("Adjust Software Delay"), "LagdToggleDelay", 5, 50,
      tr("Adjust the software delay when Live Learning Steer Delay is toggled off. The default software delay value is 0.2"),
      1, None, True, "", style.BUTTON_WIDTH, None, True, lambda v: f"{v/100:.2f}s")

    self.items = [self.current_model_item, self.refresh_item, self.clear_cache_item, self.cancel_download_item, self.supercombo_label,
                  self.vision_label, self.policy_label, self.lane_turn_desire_toggle, self.lane_turn_value_control,
                  self.lagd_toggle, self.delay_control]

  def _set_init_oc_value(self, control, param_key, default, scale=100):
    value_str = self._params.get(param_key, default)
    value = int(float(value_str) * scale)
    control.action_item.set_value(value)

  def _update_lane_turn_step(self):
    new_step = int(round(100 / CV.MPH_TO_KPH)) if self._params.get_bool("IsMetric") else 100
    if self.lane_turn_value_control.action_item.value_change_step != new_step:
      self.lane_turn_value_control.action_item.value_change_step = new_step

  def _update_lagd_description(self):
    desc = tr("Enable this for the car to learn and adapt its steering response time. Disable to use a fixed steering response time. " +
              "Keeping this on provides the stock openpilot experience.")
    if self._params.get_bool("LagdToggle"):
      desc += f"<br><br><b>{tr('Live Steer Delay:')} {ui_state.sm['liveDelay'].lateralDelay:.3f} s"
    elif (cp := self._params.get("CarParamsPersistent")):
      cp = messaging.log_from_bytes(cp, car.CarParams)
      sw_delay = float(self._params.get("LagdToggleDelay", "0.2"))
      desc += (f"<br><br><b>{tr('Actuator Delay:')} {cp.steerActuatorDelay:.2f} s + {tr('Software Delay:')} {sw_delay:.2f} s = " +
               f"{tr('Total Delay:')} {cp.steerActuatorDelay + sw_delay:.2f} s")
    self.lagd_toggle.set_description(desc)

  def _format_lane_turn_label(self, mph):
    is_metric = self._params.get_bool("IsMetric")
    return f"{int(round(mph * (CV.MPH_TO_KPH if is_metric else 1)))} {'km/h' if is_metric else 'mph'}"

  def update_model_manager_state(self):
    self.model_manager = ui_state.sm["modelManagerSP"]

  def handle_bundle_download_progress(self):
    labels = {custom.ModelManagerSP.Model.Type.supercombo: self.supercombo_label,
              custom.ModelManagerSP.Model.Type.vision: self.vision_label,
              custom.ModelManagerSP.Model.Type.policy: self.policy_label}
    for l in labels.values():
      l.set_visible(False)

    self.cancel_download_item.set_visible(False)

    if not self.model_manager or (not self.model_manager.selectedBundle and not self.model_manager.activeBundle):
      return

    bundle = self.model_manager.activeBundle
    if (sb := self.model_manager.selectedBundle) and (self.is_downloading() or sb.status == custom.ModelManagerSP.DownloadStatus.failed):
      bundle = sb

    self.download_status = bundle.status
    status_changed = self.prev_download_status != self.download_status

    self.cancel_download_item.set_visible(bool(sb) and bool(self._params.get("ModelManager_DownloadIndex")))

    for model in bundle.models:
      if label := labels.get(model.type.raw if hasattr(model.type, 'raw') else model.type):
        label.set_visible(True)
        p = model.artifact.downloadProgress
        name = bundle.displayName

        text, show, color = f"pending - {name}", False, rl.GRAY
        if p.status == custom.ModelManagerSP.DownloadStatus.downloading:
          text, show = f"{int(p.progress)}% - {name}", True
        elif p.status == custom.ModelManagerSP.DownloadStatus.downloaded:
          text, color = f"{name} - {tr('downloaded') if status_changed else tr('ready')}", ON_COLOR
        elif p.status == custom.ModelManagerSP.DownloadStatus.cached:
          text, color = f"{name} - {tr('from cache') if status_changed else tr('ready')}", ON_COLOR
        elif p.status == custom.ModelManagerSP.DownloadStatus.failed:
          text, color = f"download failed - {name}", rl.RED

        label.action_item.update(p.progress, text, show, color)

    self.prev_download_status = self.download_status

  def is_downloading(self):
    if not self.model_manager or not self.model_manager.selectedBundle:
      return False
    return self.model_manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.downloading

  def get_active_model_name(self):
    if self.model_manager and self.model_manager.activeBundle:
      return self.model_manager.activeBundle.displayName
    return "Default"

  def get_active_model_internal_name(self):
    if self.model_manager and self.model_manager.activeBundle:
      return self.model_manager.activeBundle.internalName
    return "Default"

  def get_active_model_ref(self):
    if self.model_manager and self.model_manager.activeBundle:
      return self.model_manager.activeBundle.ref
    return "Default"

  def _handle_current_model_clicked(self):
    bundles = self.model_manager.availableBundles
    folders = {}
    for bundle in bundles:
      overrides = {override.key: override.value for override in bundle.overrides}
      folder = overrides.get("folder", "")
      folders.setdefault(folder, []).append(bundle)

    sorted_folders = sorted(folders.items(), key=lambda item: max((b.index for b in item[1]), default=-1), reverse=True)

    folders_list = [TreeFolder("", [TreeNode("", tr("Default"), "Default", -1)])]
    for folder, bundles_in_folder in sorted_folders:
      bundles_in_folder.sort(key=lambda b: b.index, reverse=True)
      folder_display = folder
      if bundles_in_folder:
        latest_bundle = bundles_in_folder[0]
        match = re.search(r'\(([^)]*)\)[^(]*$', latest_bundle.displayName)
        if match:
          folder_display += f" - (Updated: {match.group(1)})"
      nodes = [TreeNode(folder, bundle.displayName, bundle.ref, bundle.index) for bundle in bundles_in_folder]
      folders_list.append(TreeFolder(folder_display, nodes))

    if (fav_str := self._params.get("ModelManager_Favs")):
      fav_refs = set(fav_str.split(';'))
      if fav_bundles := [b for b in bundles if b.ref in fav_refs]:
        folders_list.insert(1, TreeFolder("Favorites", [TreeNode("", b.displayName, b.ref, b.index) for b in fav_bundles]))

    dialog = TreeOptionDialog(tr("Select a Model"), folders_list, self.get_active_model_ref(), "ModelManager_Favs")

    def callback(result):
      if result == DialogResult.CONFIRM:
        selected_ref = dialog.selection_ref
        if selected_ref == "Default":
          self._params.remove("ModelManager_ActiveBundle")
          self.show_reset_params_dialog()
        else:
          selected_bundle = next(b for b in bundles if b.ref == selected_ref)
          self._params.put("ModelManager_DownloadIndex", selected_bundle.index)
          if self.model_manager.activeBundle and selected_bundle.generation != self.model_manager.activeBundle.generation:
            self.show_reset_params_dialog()

    gui_app.set_modal_overlay(dialog, callback=callback)

  def _refresh_models(self):
    self._params.put("ModelManager_LastSyncTime", 0)
    gui_app.set_modal_overlay(alert_dialog(tr("Fetching Latest Models")))

  def _clear_cache(self):
    confirm_msg = tr("This will delete ALL downloaded models from the cache except the currently active model. Are you sure?")
    dialog = ConfirmDialog(confirm_msg, tr("Clear Cache"), tr("Cancel"))
    gui_app.set_modal_overlay(dialog, callback=self._clear_cache_callback)

  def _clear_cache_callback(self, result):
    if result == DialogResult.CONFIRM:
      self._params.put_bool("ModelManager_ClearCache", True)

  def show_reset_params_dialog(self):
    confirm_msg = tr("Model download has started in the background. We suggest you to reset calibration. Would you like to do that now?")
    dialog = ConfirmDialog(confirm_msg, tr("Reset Calibration"), tr("Cancel"))
    gui_app.set_modal_overlay(dialog, callback=self._reset_params_callback)

  def _reset_params_callback(self, result):
    if result == DialogResult.CONFIRM:
      self._params.remove("CalibrationParams")
      self._params.remove("LiveTorqueParameters")

  def _cancel_download(self):
    self._params.remove("ModelManager_DownloadIndex")

  def calculate_cache_size(self):
    model_dir = CUSTOM_MODEL_PATH
    if not os.path.exists(model_dir):
      return 0.0
    total_size = 0
    for file in os.listdir(model_dir):
      path = os.path.join(model_dir, file)
      if os.path.isfile(path):
        total_size += os.path.getsize(path)
    return total_size / (1024 * 1024)

  def _update_state(self):
    self.update_labels()

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()

  def update_labels(self):
    self._update_lane_turn_step()
    self.update_model_manager_state()
    self.handle_bundle_download_progress()
    self.current_model_item.action_item.set_value(self.get_active_model_internal_name())
    self.clear_cache_item.action_item.set_value(f"{self.calculate_cache_size():.2f} MB")
    self._update_lagd_description()
