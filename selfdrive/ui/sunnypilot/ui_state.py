"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging, custom
from openpilot.common.params import Params

from openpilot.selfdrive.ui.sunnypilot.param_watcher import ParamWatcher


class UIStateSP:
  def __init__(self):
    self.params = Params()
    self.param_watchers = {}
    self.sm_services_ext = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP"
    ]

  def param_watcher(self, panel):
    return self.param_watchers.setdefault(panel, ParamWatcher(self.params))

  def update(self) -> None:
    pass

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
