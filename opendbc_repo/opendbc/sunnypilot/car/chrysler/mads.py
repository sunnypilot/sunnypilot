from collections import namedtuple

from opendbc.car import structs
from opendbc.car.chrysler.values import RAM_CARS

from opendbc.sunnypilot import SunnypilotParamFlags
from opendbc.sunnypilot.mads_base import MadsCarStateBase

MadsDataSP = namedtuple("MadsDataSP",
                        ["enable_mads", "paused", "lkas_disabled"])

ButtonType = structs.CarState.ButtonEvent.Type


class MadsCarController:
  def __init__(self):
    super().__init__()
    self.mads = MadsDataSP(False, False, False)

  @staticmethod
  def create_lkas_heartbit(packer, lkas_heartbit, mads):
    # LKAS_HEARTBIT (0x2D9) LKAS heartbeat
    values = {s: lkas_heartbit[s] for s in [
      "LKAS_DISABLED",
      "AUTO_HIGH_BEAM",
      "FORWARD_1",
      "FORWARD_2",
      "FORWARD_3",
    ]}

    if mads.enable_mads:
      values["LKAS_DISABLED"] = 1 if mads.lkas_disabled else 0

    return packer.make_can_msg("LKAS_HEARTBIT", 0, values)

  def mads_status_update(self, CC: structs.CarControl, CS) -> MadsDataSP:
    enable_mads = CC.sunnypilotParams & SunnypilotParamFlags.ENABLE_MADS
    paused = CC.madsEnabled and not CC.latActive

    if any(be.type == ButtonType.lkas and be.pressed for be in CS.out.buttonEvents):
      CS.lkas_disabled = not CS.lkas_disabled

    return MadsDataSP(enable_mads, paused, CS.lkas_disabled)

  def update(self, CC: structs.CarControl, CS):
    self.mads = self.mads_status_update(CC, CS)


class MadsCarState(MadsCarStateBase):
  def __init__(self):
    super().__init__()
    self.lkas_heartbit = 0

    self.init_lkas_disabled = False
    self.lkas_disabled = False

  def get_lkas_button(self, CP, cp, cp_cam):
    if CP.carFingerprint in RAM_CARS:
      lkas_button = cp.vl["Center_Stack_1"]["LKAS_Button"] or cp.vl["Center_Stack_2"]["LKAS_Button"]
    else:
      lkas_button = cp.vl["TRACTION_BUTTON"]["TOGGLE_LKAS"]
      self.lkas_heartbit = cp_cam.vl["LKAS_HEARTBIT"]
      if not self.init_lkas_disabled:
        self.lkas_disabled = cp_cam.vl["LKAS_HEARTBIT"]["LKAS_DISABLED"]
        self.init_lkas_disabled = True

    return lkas_button
