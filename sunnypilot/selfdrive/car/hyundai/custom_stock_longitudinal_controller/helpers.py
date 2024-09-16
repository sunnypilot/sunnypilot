from openpilot.selfdrive.car.hyundai.values import HyundaiFlags

def create_clu11(packer, clu11, button, CP):
  values = {s: clu11[s] for s in [
    "CF_Clu_CruiseSwState",
    "CF_Clu_CruiseSwMain",
    "CF_Clu_SldMainSW",
    "CF_Clu_ParityBit1",
    "CF_Clu_VanzDecimal",
    "CF_Clu_Vanz",
    "CF_Clu_SPEED_UNIT",
    "CF_Clu_DetentOut",
    "CF_Clu_RheostatLevel",
    "CF_Clu_CluInfo",
    "CF_Clu_AmpInfo",
    "CF_Clu_AliveCnt1",
  ]}
  values["CF_Clu_CruiseSwState"] = button
  values["CF_Clu_AliveCnt1"] = (values["CF_Clu_AliveCnt1"] + 1) % 0x10
  # send buttons to camera on camera-scc based cars
  bus = 2 if CP.flags & HyundaiFlags.CAMERA_SCC else 0
  return packer.make_can_msg("CLU11", bus, values)
