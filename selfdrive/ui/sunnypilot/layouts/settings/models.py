import os

from cereal import messaging, car, custom
from openpilot.common.params import Params
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.list_view import button_item, text_item
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.selfdrive.ui.ui_state import ui_state

from openpilot.sunnypilot.models.runners.constants import CUSTOM_MODEL_PATH
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp


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
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self.current_model_item = button_item(tr("Current Model"), tr("SELECT"), "", self._handle_current_model_clicked)
    self.refresh_item = button_item(tr("Refresh Model List"), tr("REFRESH"), "", self._refresh_models)
    self.clear_cache_item = button_item(tr("Clear Model Cache"), tr("CLEAR"), "", self._clear_cache)
    self.supercombo_label = text_item("", "")
    self.navigation_label = text_item("", "")
    self.vision_label = text_item("", "")
    self.policy_label = text_item("", "")
    self.lane_turn_desire_toggle = toggle_item_sp(tr("Use Lane Turn Desires"),
                                                  tr("If you're driving at 20 mph (32 km/h) or below and have your blinker on, " +
                                                     "the car will plan a turn in that direction at the nearest drivable path. " +
                                                     "This prevents situations (like at red lights) where the car might plan the wrong turn direction."),
                                                  callback=self._on_lane_turn_desire_changed, param="LaneTurnDesire")
    max_value_mph = 20
    is_metric = self._params.get_bool("IsMetric")
    per_value_change = 100 if not is_metric else int(round(100 / 1.609344))
    self.lane_turn_value_control = option_item_sp(tr("Adjust Lane Turn Speed"), "LaneTurnValue", 5 * 100, max_value_mph * 100,
                                                  tr("Set the maximum speed for lane turn desires. Default is 19 mph."),
                                                  per_value_change, None, True, "", style.BUTTON_WIDTH, None, True,
                                                  lambda v: self._format_lane_turn_label(v / 100))
    self.lagd_toggle = toggle_item_sp(tr("Live Learning Steer Delay"), "", callback=self._on_lagd_changed, param="LagdToggle")
    self.delay_control = option_item_sp(tr("Adjust Software Delay"), "LagdToggleDelay", 5, 50,
                                        tr("Adjust the software delay when Live Learning Steer Delay is toggled off. " +
                                           "The default software delay value is 0.2"),
                                        1, None, True, "", style.BUTTON_WIDTH, None, True,
                                        lambda v: f"{v/100:.2f}s")

    self.items = [
      self.current_model_item,
      self.refresh_item,
      self.clear_cache_item,
      self.lane_turn_desire_toggle,
      self.lane_turn_value_control,
      self.lagd_toggle,
      self.delay_control,
    ]

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
    self.update_labels()

  def update_labels(self):
    self.update_model_manager_state()
    self.handle_bundle_download_progress()
    self.current_model_item.action_item.set_value(self.get_active_model_internal_name())
    self.clear_cache_item.action_item.set_value(f"{self.calculate_cache_size():.2f} MB")
    self._update_lagd_description()

  def _update_lagd_description(self):
    desc = tr("Enable this for the car to learn and adapt its steering response time. " +
              "Disable to use a fixed steering response time. Keeping this on provides the stock openpilot experience.")
    if self._params.get_bool("LagdToggle"):
      live_delay = ui_state.sm["liveDelay"].lateralDelay
      desc += f"<br><br><b>{tr('Live Steer Delay:')} {live_delay:.3f} s"
    else:
      car_params_bytes = self._params.get("CarParamsPersistent")
      if car_params_bytes:
        carparams = messaging.log_from_bytes(car_params_bytes, car.CarParams)
        steer_delay = carparams.steerActuatorDelay
        software_delay = float(self._params.get("LagdToggleDelay", "0.2"))
        total_lag = steer_delay + software_delay
        desc += (f"<br><br><b>{tr('Actuator Delay:')} {steer_delay:.2f} s + " +
                 f"{tr('Software Delay:')} {software_delay:.2f} s = " +
                 f"{tr('Total Delay:')} {total_lag:.2f} s")
    self.lagd_toggle.set_description(desc)

  def _on_lane_turn_desire_changed(self, state):
    self.lane_turn_value_control.set_visible(state)

  def _on_lagd_changed(self, state):
    self.delay_control.set_visible(not state)
    self._update_lagd_description()

  def _format_lane_turn_label(self, mph):
    is_metric = self._params.get_bool("IsMetric")
    unit = "km/h" if is_metric else "mph"
    display_value = mph
    if is_metric:
      display_value *= 1.609344
    return f"{int(round(display_value))} {unit}"

  def update_model_manager_state(self):
    self.model_manager = ui_state.sm["modelManagerSP"]

  def handle_bundle_download_progress(self):
    labels = {
        custom.ModelManagerSP.Model.Type.supercombo: self.supercombo_label,
        custom.ModelManagerSP.Model.Type.navigation: self.navigation_label,
        custom.ModelManagerSP.Model.Type.vision: self.vision_label,
        custom.ModelManagerSP.Model.Type.policy: self.policy_label,
    }

    for label in labels.values():
      if label in self.items:
        self.items.remove(label)

    if not self.model_manager or (not self.model_manager.selectedBundle and not self.model_manager.activeBundle):
      return

    if self.supercombo_label not in self.items:
      index = self.items.index(self.clear_cache_item) + 1
      for i, label in enumerate(labels.values()):
        self.items.insert(index + i, label)

    show_selected = (self.model_manager.selectedBundle and
                     (self.is_downloading() or
                      self.model_manager.selectedBundle.status == custom.ModelManagerSP.DownloadStatus.failed))
    bundle = self.model_manager.selectedBundle if show_selected else self.model_manager.activeBundle
    models = bundle.models
    self.download_status = bundle.status
    download_status_changed = self.prev_download_status != self.download_status

    for model in models:
      model_name = bundle.displayName
      label = labels.get(model.type)
      if label:
        progress = model.artifact.downloadProgress
        if progress.status == custom.ModelManagerSP.DownloadStatus.downloading:
          text = f"{int(progress.progress)}% - {model_name}"
        elif progress.status == custom.ModelManagerSP.DownloadStatus.downloaded:
          status = tr("downloaded") if download_status_changed else tr("ready")
          text = f"{model_name} - {status}"
        elif progress.status == custom.ModelManagerSP.DownloadStatus.cached:
          status = tr("from cache") if download_status_changed else tr("ready")
          text = f"{model_name} - {status}"
        elif progress.status == custom.ModelManagerSP.DownloadStatus.failed:
          text = f"download failed - {model_name}"
        else:
          text = f"pending - {model_name}"
        label.action_item.set_text(text)

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
    options = [tr("Default")] + [bundle.displayName for bundle in bundles]

    dialog = MultiOptionDialog(tr("Select a Model"), options, self.get_active_model_name())

    def callback(result):
      if result == DialogResult.CONFIRM:
        selected_option = dialog.selection
        if selected_option == tr("Default"):
          self._params.remove("ModelManager_ActiveBundle")
          self.show_reset_params_dialog()
        else:
          selected_bundle = next(bundle for bundle in bundles if bundle.displayName == selected_option)
          self._params.put("ModelManager_DownloadIndex", str(selected_bundle.index))
          if self.model_manager.activeBundle and selected_bundle.generation != self.model_manager.activeBundle.generation:
            self.show_reset_params_dialog()

        self.update_labels()

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
    confirm_msg = tr("Model download has started in the background. We STRONGLY suggest you to reset calibration. Would you like to do that now?")
    dialog = ConfirmDialog(confirm_msg, tr("Reset Calibration"), tr("Cancel"))
    gui_app.set_modal_overlay(dialog, callback=self._reset_params_callback)

  def _reset_params_callback(self, result):
    if result == DialogResult.CONFIRM:
      self._params.remove("CalibrationParams")
      self._params.remove("LiveTorqueParameters")

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
