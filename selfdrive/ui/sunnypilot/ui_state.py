from openpilot.selfdrive.ui.ui_state import UIState
from cereal import messaging
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState


class UIStateSP(UIState):
  _instance: 'UIStateSP | None' = None

  def _initialize(self):
    UIState._initialize(self)
    self.params = Params()
    self.sunnylink_state = SunnylinkState()
    self.sm = messaging.SubMaster(
      [
        "modelV2", "controlsState", "liveCalibration", "deviceState", "carParams",
        "driverMonitoringState", "carState", "roadCameraState", "managerState",
        "selfdriveState", "longitudinalPlan", "rawAudioData",
        "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
        "carControl", "gpsLocationExternal", "gpsLocation", "liveTorqueParameters",
        "carStateSP", "liveParameters", "liveMapDataSP", "carParamsSP"
      ])

  def update(self) -> None:
    UIState.update(self)
    self.sunnylink_state.start()

  def _update_status(self) -> None:
    UIState._update_status(self)

  def update_params(self) -> None:
    UIState.update_params(self)

# Global instance
ui_state_sp = UIStateSP()
