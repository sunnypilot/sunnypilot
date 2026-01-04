"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging, log, custom
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState
from openpilot.system.ui.lib.application import gui_app

OpenpilotState = log.SelfdriveState.OpenpilotState
MADSState = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState


class UIStateSP:
  def __init__(self):
    self.params = Params()
    self.sm_services_ext = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP", "liveDelay"
    ]

    self.sunnylink_state = SunnylinkState()

    self.custom_interactive_timeout: int = self.params.get("InteractivityTimeout", return_default=True)
    self.global_brightness_override: int = self.params.get("Brightness", return_default=True)
    self.onroad_brightness_timer: int = 0

  def update(self) -> None:
    if self.sunnylink_enabled:
      self.sunnylink_state.start()
    else:
      self.sunnylink_state.stop()

  def update_onroad_brightness(self, sm, started: bool) -> None:
    if started and self.onroad_brightness_toggle:
      ss = sm["selfdriveState"]
      if ss.alertSize != log.SelfdriveState.AlertSize.none and \
         ss.alertStatus != log.SelfdriveState.AlertStatus.normal:
        self.reset_onroad_sleep_timer()
      elif self.onroad_brightness_timer > 0:
        self.onroad_brightness_timer -= 1

  def reset_onroad_sleep_timer(self) -> None:
    if self.onroad_brightness_toggle >= 0 and self.onroad_brightness_toggle:
      self.onroad_brightness_timer = self.onroad_brightness_timer_param * gui_app.target_fps
    else:
      self.onroad_brightness_timer = -1

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

    # Onroad Screen Brightness
    self.onroad_brightness_toggle = self.params.get_bool("OnroadScreenOffControl")
    self.onroad_brightness = self.params.get("OnroadScreenOffBrightness", return_default=True)
    self.onroad_brightness_timer_param = self.params.get("OnroadScreenOffTimer", return_default=True)


class DeviceSP:
  def __init__(self):
    self._params = Params()

  def _set_awake(self, on: bool):
    if on and self._params.get("DeviceBootMode", return_default=True) == 1:
      self._params.put_bool("OffroadMode", True)
