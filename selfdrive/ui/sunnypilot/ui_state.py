"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import Enum

from cereal import messaging, log, custom
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState
from openpilot.system.ui.lib.application import gui_app

OpenpilotState = log.SelfdriveState.OpenpilotState
MADSState = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState

ONROAD_BRIGHTNESS_TIMER_DISABLED = -1


class OnroadTimerStatus(Enum):
  NONE = 0
  PAUSE = 1
  RESUME = 2


class UIStateSP:
  def __init__(self):
    self.params = Params()
    self.sm_services_ext = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP", "liveDelay"
    ]

    self.sunnylink_state = SunnylinkState()
    self.update_params()

    self.onroad_brightness_timer: int = 0
    self.custom_interactive_timeout: int = self.params.get("InteractivityTimeout", return_default=True)
    self.global_brightness_override: int = self.params.get("Brightness", return_default=True)
    self.reset_onroad_sleep_timer()

  def update(self) -> None:
    if self.sunnylink_enabled:
      self.sunnylink_state.start()
    else:
      self.sunnylink_state.stop()

  def onroad_brightness_has_event(self, started: bool, alert) -> bool:
    return started and self.onroad_brightness_toggle and alert is not None

  def update_onroad_brightness(self, has_alert: bool) -> None:
    if has_alert:
      return

    if self.onroad_brightness_timer > 0:
      self.onroad_brightness_timer -= 1

  def reset_onroad_sleep_timer(self, timer_status: OnroadTimerStatus = OnroadTimerStatus.NONE) -> None:
    # Toggling from active state to inactive
    if timer_status == OnroadTimerStatus.PAUSE and self.onroad_brightness_timer != ONROAD_BRIGHTNESS_TIMER_DISABLED:
      self.onroad_brightness_timer = ONROAD_BRIGHTNESS_TIMER_DISABLED
    # Toggling from a previously inactive state or resetting an active timer
    elif (self.onroad_brightness_timer_param >= 0 and self.onroad_brightness_toggle and
          self.onroad_brightness_timer != ONROAD_BRIGHTNESS_TIMER_DISABLED) or timer_status == OnroadTimerStatus.RESUME:
      self.onroad_brightness_timer = self.onroad_brightness_timer_param * gui_app.target_fps

  @property
  def onroad_brightness_timer_expired(self) -> bool:
    return self.onroad_brightness_toggle and self.onroad_brightness_timer == 0

  @staticmethod
  def update_state_status(ss, ss_sp, onroad_evt) -> str:
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

  @staticmethod
  def update_custom_global_brightness(brightness_override: int) -> float:
    """
    Updates the custom global brightness by constraining the value to a predefined range.

    The method takes an integer `brightness` value, adjusts it to ensure it is within the
    range of 30 to 100, inclusive, and returns the adjusted value as a float.

    This method only runs if 0 (Auto) is not selected.

    :param brightness_override: The desired brightness level. It is constrained between
                       a minimum of 30 and a maximum of 100.
    :type brightness_override: int
    :return: The brightness value adjusted to fit within the allowable range,
             converted to a float.
    :rtype: float
    """
    return float(min(max(brightness_override, 30), 100))

  @staticmethod
  def set_onroad_brightness(_ui_state, awake: bool, clipped_brightness: float) -> float:
    if awake and _ui_state.started and _ui_state.onroad_brightness_toggle and _ui_state.onroad_brightness_timer == 0:
      return float(max(min(_ui_state.onroad_brightness, clipped_brightness), 0))

    return clipped_brightness

  @staticmethod
  def wake_from_dimmed_onroad_brightness(_ui_state, evs) -> None:
    if _ui_state.started and _ui_state.onroad_brightness_timer_expired:
      if any(ev.left_down for ev in evs):
        gui_app.mouse_events.clear()
      _ui_state.reset_onroad_sleep_timer()
