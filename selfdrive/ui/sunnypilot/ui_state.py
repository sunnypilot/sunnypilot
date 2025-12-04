"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging, custom
from openpilot.common.param_watcher import ParamWatcher
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState


class UIStateSP:
  def __init__(self):
    self.params = ParamWatcher()
    self.params.add_watcher(self.on_param_change)
    self.sm_services_ext = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP"
    ]

    self.sunnylink_state = SunnylinkState()
    self.active_layout = None

  def set_active_layout(self, layout):
    self.active_layout = layout

  def on_param_change(self, param_name, mask):
    cloudlog.warning(f"Param changed: {param_name}")  # remove me after testing
    self.update_toggles(param_name)
    if self.active_layout:
      for method in ['update_settings', '_update_state']:
        if funcion := getattr(self.active_layout, method, None):
          funcion()
          break

  def update_toggles(self, param_name) -> None:
    for item in getattr(self.active_layout, 'items', []):
      action = getattr(item, 'action_item', None)
      if not action:
        continue

      toggle = getattr(action, 'toggle', None)
      if getattr(toggle, 'param_key', None) == param_name:
        action.set_state(self.params.get_bool(param_name))
        continue

      if getattr(action, 'param_key', None) == param_name:
        value = int(self.params.get(param_name, return_default=True))
        for attribute in ['selected_button', 'current_value']:
          if hasattr(action, attribute):
            setattr(action, attribute, value)

  def update(self) -> None:
    self.sunnylink_state.start()

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
