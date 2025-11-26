
from cereal import messaging, custom
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.sunnylink_state import SunnylinkState


class UIStateSP:

  def __init__(self):
    self.params = Params()
    self.sp_services = [
      "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
      "gpsLocation", "liveTorqueParameters", "carStateSP", "liveMapDataSP", "carParamsSP"
    ]
    self.sunnylink_state = SunnylinkState()

  def update(self) -> None:
    self.sunnylink_state.start()

  def update_params(self) -> None:
    CP_SP_bytes = self.params.get("CarParamsSPPersistent")
    if CP_SP_bytes is not None:
      self.CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
    self.sunnylink_enabled = self.params.get_bool("SunnylinkEnabled")
