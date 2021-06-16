import crcmod
from common.numpy_fast import clip
from selfdrive.car.hyundai.values import CAR, CHECKSUM, FEATURES
from common.params import Params

hyundai_checksum = crcmod.mkCrcFun(0x11D, initCrc=0xFD, rev=False, xorOut=0xdf)


def create_lkas11(packer, frame, car_fingerprint, apply_steer, steer_req,
                  steer_wind_down, lkas11, sys_warning, sys_state, enabled,
                  left_lane, right_lane,
                  left_lane_depart, right_lane_depart, bus, ldws, steerwinddown_enabled):
  values = lkas11
  values["CF_Lkas_LdwsSysState"] = sys_state
  values["CF_Lkas_SysWarning"] = 3 if sys_warning else 0
  values["CF_Lkas_LdwsLHWarning"] = left_lane_depart
  values["CF_Lkas_LdwsRHWarning"] = right_lane_depart
  values["CR_Lkas_StrToqReq"] = apply_steer
  values["CF_Lkas_ActToi"] = steer_req
  values["CF_Lkas_ToiFlt"] = steer_wind_down if steerwinddown_enabled else 0
  values["CF_Lkas_MsgCount"] = frame % 0x10

  if car_fingerprint in FEATURES["send_lfahda_mfa"]:
    values["CF_Lkas_LdwsActivemode"] = int(left_lane) + (int(right_lane) << 1)
    values["CF_Lkas_LdwsOpt_USM"] = 2

    # FcwOpt_USM 5 = Orange blinking car + lanes
    # FcwOpt_USM 4 = Orange car + lanes
    # FcwOpt_USM 3 = Green blinking car + lanes
    # FcwOpt_USM 2 = Green car + lanes
    # FcwOpt_USM 1 = White car + lanes
    # FcwOpt_USM 0 = No car + lanes
    values["CF_Lkas_FcwOpt_USM"] = 2 if enabled else 1

    # SysWarning 4 = keep hands on wheel
    # SysWarning 5 = keep hands on wheel (red)
    # SysWarning 6 = keep hands on wheel (red) + beep
    # Note: the warning is hidden while the blinkers are on
    values["CF_Lkas_SysWarning"] = 4 if sys_warning else 0

  elif car_fingerprint == CAR.GENESIS:
    # This field is actually LdwsActivemode
    # Genesis and Optima fault when forwarding while engaged
    values["CF_Lkas_LdwsActivemode"] = 2

  elif car_fingerprint in [CAR.K5, CAR.K5_HEV, CAR.K7, CAR.K7_HEV]:
    values["CF_Lkas_LdwsActivemode"] = 0

  if ldws:
  	values["CF_Lkas_LdwsOpt_USM"] = 3

  dat = packer.make_can_msg("LKAS11", 0, values)[2]

  if car_fingerprint in CHECKSUM["crc8"]:
    # CRC Checksum as seen on 2019 Hyundai Santa Fe
    dat = dat[:6] + dat[7:8]
    checksum = hyundai_checksum(dat)
  elif car_fingerprint in CHECKSUM["6B"]:
    # Checksum of first 6 Bytes, as seen on 2018 Kia Sorento
    checksum = sum(dat[:6]) % 256
  else:
    # Checksum of first 6 Bytes and last Byte as seen on 2018 Kia Stinger
    checksum = (sum(dat[:6]) + dat[7]) % 256

  values["CF_Lkas_Chksum"] = checksum

  return packer.make_can_msg("LKAS11", bus, values)

def create_clu11(packer, frame, clu11, button, speed = None, bus = 0):
  values = clu11
  if speed != None:
    values["CF_Clu_Vanz"] = speed
  values["CF_Clu_CruiseSwState"] = button
  values["CF_Clu_AliveCnt1"] = frame % 0x10
  return packer.make_can_msg("CLU11", bus, values)

def create_lfahda_mfc(packer, frame, enabled, hda_set_speed=0):
  values = {
    "LFA_Icon_State": 2 if enabled else 0,
    "HDA_Active": 1 if hda_set_speed else 0,
    #"HDA_Icon_State": 2 if hda_set_speed else 0,
    "HDA_Icon_State": 2 if enabled else 0,
    "HDA_VSetReq": hda_set_speed,
  }

  # ACTIVE 1 = Green steering wheel icon

  # LFA_USM 2 & 3 = LFA cancelled, fast loud beeping
  # LFA_USM 0 & 1 = No mesage

  # LFA_SysWarning 1 = "Switching to HDA", short beep
  # LFA_SysWarning 2 = "Switching to Smart Cruise control", short beep
  # LFA_SysWarning 3 =  LFA error

  # ACTIVE2: nothing
  # HDA_USM: nothing

  return packer.make_can_msg("LFAHDA_MFC", 0, values)

def create_scc11(packer, frame, set_speed, lead_visible, scc_live, lead_dist, lead_vrel, lead_yrel, car_fingerprint, speed, standstill, scc11):
  values = scc11
  values["AliveCounterACC"] = frame // 2 % 0x10
  if not scc_live:
    if standstill:
      values["SCCInfoDisplay"] = 4
    else:
      values["SCCInfoDisplay"] = 0
    values["DriverAlertDisplay"] = 0
    values["MainMode_ACC"] = 1
    values["VSetDis"] = set_speed
    values["ObjValid"] = lead_visible
    values["ACC_ObjStatus"] = lead_visible
    values["ACC_ObjRelSpd"] = clip(lead_vrel if lead_visible else 0, -20., 20.)
    values["ACC_ObjDist"] = clip(lead_dist if lead_visible else 204.6, 0., 204.6)
    values["ACC_ObjLatPos"] = clip(-lead_yrel if lead_visible else 0, -170., 170.)

  return packer.make_can_msg("SCC11", 0, values)

def create_scc12(packer, apply_accel, enabled, scc_live, gaspressed, brakepressed, aebcmdact, car_fingerprint, speed, scc12):
  values = scc12
  if not aebcmdact:
    if enabled and car_fingerprint in [CAR.NIRO_EV]:
      values["ACCMode"] = 2 if gaspressed and (apply_accel > -0.2) else 1
      values["aReqRaw"] = apply_accel
      values["aReqValue"] = apply_accel
    elif enabled and not brakepressed:
      values["ACCMode"] = 2 if gaspressed and (apply_accel > -0.2) else 1
      values["aReqRaw"] = apply_accel
      values["aReqValue"] = apply_accel
    else:
      values["ACCMode"] = 0
      values["aReqRaw"] = 0
      values["aReqValue"] = 0
    values["CR_VSM_ChkSum"] = 0
  if not scc_live:
    values["ACCMode"] = 1 if enabled else 0 # 2 if gas padel pressed
    dat = packer.make_can_msg("SCC12", 0, values)[2]
    values["CR_VSM_ChkSum"] = 16 - sum([sum(divmod(i, 16)) for i in dat]) % 16

  return packer.make_can_msg("SCC12", 0, values)

def create_scc13(packer, scc13):
  values = scc13
  return packer.make_can_msg("SCC13", 0, values)

def create_scc14(packer, enabled, scc14, aebcmdact, lead_visible, lead_dist, v_ego, standstill, car_fingerprint):
  values = scc14
  if enabled and not aebcmdact and car_fingerprint in [CAR.NIRO_EV]:
    if standstill:
      values["JerkUpperLimit"] = 0.5
      values["JerkLowerLimit"] = 10.
      values["ComfortBandUpper"] = 0.
      values["ComfortBandLower"] = 0.
      if v_ego > 0.27:
        values["ComfortBandUpper"] = 2.
        values["ComfortBandLower"] = 0.
    else:
      values["JerkUpperLimit"] = 50.
      values["JerkLowerLimit"] = 50.
      values["ComfortBandUpper"] = 50.
      values["ComfortBandLower"] = 50.
  elif enabled and not aebcmdact:
    values["JerkUpperLimit"] = 12.7
    values["JerkLowerLimit"] = 12.7
    values["ComfortBandUpper"] = 0
    values["ComfortBandLower"] = 0
    values["ACCMode"] = 1 if enabled else 4 # stock will always be 4 instead of 0 after first disengage
    values["ObjGap"] = int(min(lead_dist+2, 10)/2) if lead_visible else 0 # 1-5 based on distance to lead vehicle

  return packer.make_can_msg("SCC14", 0, values)

def create_scc42a(packer):
  values = {
    "CF_FCA_Equip_Front_Radar": 1
  }
  return packer.make_can_msg("FRT_RADAR11", 0, values)

def create_fca11(packer, fca11, fca11cnt, fca11supcnt):
  values = fca11
  values["CR_FCA_Alive"] = fca11cnt
  values["Supplemental_Counter"] = fca11supcnt
  values["CR_FCA_ChkSum"] = 0
  dat = packer.make_can_msg("FCA11", 0, values)[2]
  values["CR_FCA_ChkSum"] = 16 - sum([sum(divmod(i, 16)) for i in dat]) % 16
  return packer.make_can_msg("FCA11", 0, values)

def create_fca12(packer):
  values = {
    "FCA_USM": 3,
    "FCA_DrvSetState": 2,
  }
  return packer.make_can_msg("FCA12", 0, values)

def create_mdps12(packer, frame, mdps12):
  values = mdps12
  values["CF_Mdps_ToiActive"] = 0
  values["CF_Mdps_ToiUnavail"] = 1
  values["CF_Mdps_MsgCount2"] = frame % 0x100
  values["CF_Mdps_Chksum2"] = 0

  dat = packer.make_can_msg("MDPS12", 2, values)[2]
  checksum = sum(dat) % 256
  values["CF_Mdps_Chksum2"] = checksum

  return packer.make_can_msg("MDPS12", 2, values)

def create_scc7d0(cmd):
  return[2000, 0, cmd, 0]

