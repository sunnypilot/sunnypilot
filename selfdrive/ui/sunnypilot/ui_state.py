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
    self.params.start()
    self.sm_services_ext = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP", "liveDelay"
    ]

    self.sunnylink_state = SunnylinkState()
    self.active_layout = None
    self.changed_params = set()

  def set_active_layout(self, layout):
    self.active_layout = layout

  def on_param_change(self, param_name, mask):
    self.changed_params.add(param_name)

  def update_toggles(self, param_name) -> None:
    for item in getattr(self.active_layout, 'items', []):
      action = getattr(item, 'action_item', None)
      if not action:
        continue

      toggle = getattr(action, 'toggle', None)
      toggle_key = getattr(toggle, 'param_key', None)
      if toggle_key == param_name:
        action.set_state(self.params.get_bool(param_name))
        continue

      action_key = getattr(action, 'param_key', None)
      if action_key == param_name:
        value = int(self.params.get(param_name, return_default=True))
        for attribute in ['selected_button', 'current_value']:
          if hasattr(action, attribute):
            setattr(action, attribute, value)

  def update(self) -> None:
    self.sunnylink_state.start()

    if not self.params.is_watching():
      cloudlog.warning("ParamWatcher thread died, restarting...")
      self.params.start()

    params_processed = False
    while self.changed_params:
      try:
        param_name = self.changed_params.pop()
      except KeyError:
        break
      self.update_toggles(param_name)
      params_processed = True

    if self.active_layout and params_processed:
      for method in ['update_settings', '_update_state']:
        if function := getattr(self.active_layout, method, None):
          function()
          break

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
