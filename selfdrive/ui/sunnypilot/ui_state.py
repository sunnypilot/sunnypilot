"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging, custom
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState
from openpilot.selfdrive.ui.sunnypilot.ui_helpers import sync_layout_params


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

  def update(self) -> None:
    self.sunnylink_state.start()

    if not self.params.is_watching():
      cloudlog.warning("ParamWatcher thread died, restarting...")
      self.params.start()

    if self.changed_params:
      while self.changed_params:
        self.changed_params.pop()

      if self.active_layout:
        sync_layout_params(self.active_layout, None, self.params)

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
