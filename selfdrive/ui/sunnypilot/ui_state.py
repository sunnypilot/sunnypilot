"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging, log, custom
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState
from openpilot.selfdrive.ui.sunnypilot.ui_helpers import sync_layout_params

OpenpilotState = log.SelfdriveState.OpenpilotState
MADSState = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState


class UIStateSP:
  def __init__(self):
    self.params = Params()
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
    if layout:
      sync_layout_params(layout, None, self.params)

  def on_param_change(self, param_name):
    self.changed_params.add(param_name)

    self.custom_interactive_timeout: int = self.params.get("InteractivityTimeout", return_default=True)
    self.global_brightness_override: int = self.params.get("Brightness", return_default=True)

  def update(self) -> None:
    if self.sunnylink_enabled:
      self.sunnylink_state.start()
    else:
      self.sunnylink_state.stop()

    if not self.params.is_watching():
      cloudlog.warning("ParamWatcher thread died, restarting...")
      self.params.start()

    if self.changed_params:
      while self.changed_params:
        self.changed_params.pop()

      if self.active_layout:
        sync_layout_params(self.active_layout, None, self.params)

  @staticmethod
  def update_status(ss, ss_sp, onroad_evt) -> str:
    state = ss.state
    mads = ss_sp.mads
    mads_state = mads.state

    if state == OpenpilotState.preEnabled:
      return "override"

    if state == OpenpilotState.overriding:
      if not mads.available:
        return "override"

      if any(e.overrideLongitudinal for e in onroad_evt):
        return "override"

    if mads_state in (MADSState.paused, MADSState.overriding):
      return "override"

    # MADS specific statuses
    if not mads.available:
      return "engaged" if ss.enabled else "disengaged"

    if not mads.enabled and not ss.enabled:
      return "disengaged"

    if mads.enabled and ss.enabled:
      return "engaged"

    if mads.enabled:
      return "lat_only"

    if ss.enabled:
      return "long_only"

    return "disengaged"

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
    self.developer_ui = self.params.get("DevUIInfo")
    self.rainbow_path = self.params.get_bool("RainbowMode")
    self.chevron_metrics = self.params.get("ChevronInfo")
    self.active_bundle = self.params.get("ModelManager_ActiveBundle")
    self.custom_interactive_timeout = self.params.get("InteractivityTimeout", return_default=True)
    self.global_brightness_override = self.params.get("Brightness", return_default=True)


class DeviceSP:
  def __init__(self):
    self._params = Params()

  def _set_awake(self, on: bool):
    if on and self._params.get("DeviceBootMode", return_default=True) == 1:
      self._params.put_bool("OffroadMode", True)
