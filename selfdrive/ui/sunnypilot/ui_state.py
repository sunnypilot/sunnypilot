from collections.abc import Callable

from openpilot.selfdrive.ui.ui_state import UIState
from cereal import messaging, custom
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState


class UIStateSP(UIState):
  _instance: 'UIStateSP | None' = None

  def _initialize(self):
    UIState._initialize(self)
    self.params = Params()
    self.sunnylink_state = SunnylinkState()
    op_services = self.sm.services
    sp_services = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "carControl", "gpsLocationExternal", "gpsLocation", "liveTorqueParameters",
      "carStateSP", "liveParameters", "liveMapDataSP", "carParamsSP"
    ]
    self.sm = messaging.SubMaster(op_services + sp_services)

    # Callbacks
    self._ui_update_callbacks: list[Callable[[], None]] = []

  def add_ui_update_callback(self, callback: Callable[[], None]):
    self._ui_update_callbacks.append(callback)

  def update(self) -> None:
    UIState.update(self)
    self.sunnylink_state.start()
    for callback in self._ui_update_callbacks:
      callback()

  def _update_status(self) -> None:
    UIState._update_status(self)

  def update_params(self) -> None:
    UIState.update_params(self)
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")

# Global instance
ui_state_sp = UIStateSP()
