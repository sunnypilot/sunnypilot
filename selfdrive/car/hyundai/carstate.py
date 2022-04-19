import copy
from cereal import car
from selfdrive.car.hyundai.values import DBC, STEER_THRESHOLD, FEATURES, EV_CAR, HYBRID_CAR
from selfdrive.car.interfaces import CarStateBase
from opendbc.can.parser import CANParser
from opendbc.can.can_define import CANDefine
from selfdrive.config import Conversions as CV
from common.params import Params


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    can_define = CANDefine(DBC[CP.carFingerprint]["pt"])

    self.resumeAvailable = False
    self.accEnabled = False
    self.lfaEnabled = False
    self.accMainEnabled = False
    self.leftBlinkerOn = False
    self.rightBlinkerOn = False
    self.disengageByBrake = False
    self.belowLaneChangeSpeed = True
    self.automaticLaneChange = True

    self.lfa_enabled = None
    self.prev_lfa_enabled = None

    self.acc_main_enabled = None
    self.prev_acc_main_enabled = None

    self.acc_mads_combo = None
    self.prev_acc_mads_combo = None

    self.cruiseState_standstill = False

    self.cruise_buttons = 0
    self.prev_cruise_buttons = 0
    self.acc_active = False
    self.cruise_active = False

    if self.CP.carFingerprint in FEATURES["use_cluster_gears"]:
      self.shifter_values = can_define.dv["CLU15"]["CF_Clu_Gear"]
    elif self.CP.carFingerprint in FEATURES["use_tcu_gears"]:
      self.shifter_values = can_define.dv["TCU12"]["CUR_GR"]
    else:  # preferred and elect gear methods use same definition
      self.shifter_values = can_define.dv["LVR12"]["CF_Lvr_Gear"]


  def update(self, cp, cp_cam):
    ret = car.CarState.new_message()

    self.prev_lfa_enabled = self.lfa_enabled
    self.prev_acc_main_enabled = self.acc_main_enabled
    self.prev_cruise_buttons = self.cruise_buttons
    self.cruise_buttons = cp.vl["CLU11"]["CF_Clu_CruiseSwState"]
    ret.cruiseButtons = self.cruise_buttons
    self.disable_mads = Params().get_bool("DisableMADS")
    self.acc_mads_combo = Params().get_bool("ACCMADSCombo")

    ret.doorOpen = any([cp.vl["CGW1"]["CF_Gway_DrvDrSw"], cp.vl["CGW1"]["CF_Gway_AstDrSw"],
                        cp.vl["CGW2"]["CF_Gway_RLDrSw"], cp.vl["CGW2"]["CF_Gway_RRDrSw"]])

    ret.seatbeltUnlatched = cp.vl["CGW1"]["CF_Gway_DrvSeatBeltSw"] == 0

    ret.wheelSpeeds = self.get_wheel_speeds(
      cp.vl["WHL_SPD11"]["WHL_SPD_FL"],
      cp.vl["WHL_SPD11"]["WHL_SPD_FR"],
      cp.vl["WHL_SPD11"]["WHL_SPD_RL"],
      cp.vl["WHL_SPD11"]["WHL_SPD_RR"],
    )
    ret.vEgoRaw = (ret.wheelSpeeds.fl + ret.wheelSpeeds.fr + ret.wheelSpeeds.rl + ret.wheelSpeeds.rr) / 4.
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)

    # TODO: Find brake pressure
    ret.brake = 0
    ret.brakePressed = cp.vl["TCS13"]["DriverBraking"] != 0
    ret.brakeHoldActive = cp.vl["TCS15"]["AVH_LAMP"] == 2 # 0 OFF, 1 ERROR, 2 ACTIVE, 3 READY
    ret.brakeLights = bool(cp.vl["TCS13"]["BrakeLight"] or ret.brakePressed or ret.brakeHoldActive)

    self.belowLaneChangeSpeed = ret.vEgo < (30 * CV.MPH_TO_MS)

    if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
      self.lfa_enabled = cp.vl["BCM_PO_11"]["LFA_Pressed"] == 0
    elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
      self.acc_main_enabled = cp.vl["CLU11"]["CF_Clu_CruiseSwMain"] == 0

    if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
      if self.prev_lfa_enabled is None:
        self.prev_lfa_enabled = self.lfa_enabled
    elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
      if self.prev_acc_main_enabled is None:
        self.prev_acc_main_enabled = self.acc_main_enabled

    ret.standstill = ret.vEgoRaw < 0.1
    ret.standStill = self.CP.standStill

    ret.steeringAngleDeg = cp.vl["SAS11"]["SAS_Angle"]
    ret.steeringRateDeg = cp.vl["SAS11"]["SAS_Speed"]
    ret.yawRate = cp.vl["ESP12"]["YAW_RATE"]
    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_lamp(
      50, cp.vl["CGW1"]["CF_Gway_TurnSigLh"], cp.vl["CGW1"]["CF_Gway_TurnSigRh"])
    ret.steeringTorque = cp.vl["MDPS12"]["CR_Mdps_StrColTq"]
    ret.steeringTorqueEps = cp.vl["MDPS12"]["CR_Mdps_OutTq"]
    ret.steeringPressed = abs(ret.steeringTorque) > STEER_THRESHOLD
    ret.steerWarning = cp.vl["MDPS12"]["CF_Mdps_ToiUnavail"] != 0 or cp.vl["MDPS12"]["CF_Mdps_ToiFlt"] != 0

    self.leftBlinkerOn = cp.vl["CGW1"]["CF_Gway_TurnSigLh"] != 0
    self.rightBlinkerOn = cp.vl["CGW1"]["CF_Gway_TurnSigRh"] != 0

    # cruise state
    if self.CP.openpilotLongitudinalControl:
      # These are not used for engage/disengage since openpilot keeps track of state using the buttons
      ret.cruiseState.available = cp.vl["TCS13"]["ACCEnable"] == 0
      ret.cruiseState.enabled = cp.vl["TCS13"]["ACC_REQ"] == 1
      ret.cruiseState.standstill = False
    else:
      ret.cruiseState.available = cp.vl["SCC11"]["MainMode_ACC"] == 1
      ret.cruiseState.enabled = cp.vl["SCC12"]["ACCMode"] != 0
      self.acc_active = ret.cruiseState.enabled
      self.cruise_active = self.acc_active
      ret.cruiseState.standstill = cp.vl["SCC11"]["SCCInfoDisplay"] == 4.

    self.cruiseState_standstill = ret.cruiseState.standstill

    if ret.cruiseState.available:
      if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
        if self.prev_cruise_buttons == 2: # SET-
          if self.cruise_buttons != 2:
            self.accEnabled = True
        elif self.prev_cruise_buttons == 1 and self.resumeAvailable == True: # RESUME+
          if self.cruise_buttons != 1:
            self.accEnabled = True

      if not self.disable_mads:
        if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
          if self.prev_lfa_enabled != 1: #1 == not LFA button
            if self.lfa_enabled == 1:
              self.lfaEnabled = not self.lfaEnabled
        elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
          if self.prev_acc_main_enabled != 1: #1 == not ACC Main button
            if self.acc_main_enabled == 1:
              self.accMainEnabled = not self.accMainEnabled
        if self.acc_mads_combo:
          if not self.prev_acc_mads_combo and ret.cruiseState.enabled:
            if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
              self.lfaEnabled = True
            elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
              self.accMainEnabled = True
          self.prev_acc_mads_combo = ret.cruiseState.enabled
    else:
      if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
        self.lfaEnabled = False
      elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
        self.accMainEnabled = False
      self.accEnabled = False

    if (not self.CP.pcmCruise) or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.CP.pcmCruiseSpeed:
      if self.prev_cruise_buttons != 4: # CANCEL
        if self.cruise_buttons == 4:
          self.accEnabled = False
          if self.disable_mads:
            if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
              self.lfaEnabled = False
            elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
              self.accMainEnabled = False
      if ret.brakePressed:
        self.accEnabled = False
        if self.disable_mads:
          if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
            self.lfaEnabled = False
          elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
            self.accMainEnabled = False

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.accEnabled = False
      self.accEnabled = ret.cruiseState.enabled or self.accEnabled

    if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
      ret.cruiseState.enabled = self.accEnabled

    if ret.cruiseState.enabled:
      if self.disable_mads:
        if self.CP.carFingerprint in FEATURES["use_lfa_button"]:
          self.lfaEnabled = True
        elif self.CP.carFingerprint not in FEATURES["use_lfa_button"]:
          self.accMainEnabled = True

    if ret.cruiseState.enabled:
      self.resumeAvailable = True

    ret.steerWarning = False
    if self.lfaEnabled or self.accMainEnabled:
      if (self.automaticLaneChange and not self.belowLaneChangeSpeed and (self.rightBlinkerOn or self.leftBlinkerOn)) or not (self.rightBlinkerOn or self.leftBlinkerOn):
        ret.steerWarning = cp.vl["MDPS12"]["CF_Mdps_ToiUnavail"] != 0 or cp.vl["MDPS12"]["CF_Mdps_ToiFlt"] != 0

    if not self.CP.openpilotLongitudinalControl:
      speed_conv = CV.MPH_TO_MS if cp.vl["CLU11"]["CF_Clu_SPEED_UNIT"] else CV.KPH_TO_MS
      ret.cruiseState.speed = cp.vl["SCC11"]["VSetDis"] * speed_conv

    if self.CP.carFingerprint in (HYBRID_CAR | EV_CAR):
      if self.CP.carFingerprint in HYBRID_CAR:
        ret.gas = cp.vl["E_EMS11"]["CR_Vcu_AccPedDep_Pos"] / 254.
      else:
        ret.gas = cp.vl["E_EMS11"]["Accel_Pedal_Pos"] / 254.
      ret.gasPressed = ret.gas > 0
    else:
      ret.gas = cp.vl["EMS12"]["PV_AV_CAN"] / 100.
      ret.gasPressed = bool(cp.vl["EMS16"]["CF_Ems_AclAct"])

    # Gear Selection via Cluster - For those Kia/Hyundai which are not fully discovered, we can use the Cluster Indicator for Gear Selection,
    # as this seems to be standard over all cars, but is not the preferred method.
    if self.CP.carFingerprint in FEATURES["use_cluster_gears"]:
      gear = cp.vl["CLU15"]["CF_Clu_Gear"]
    elif self.CP.carFingerprint in FEATURES["use_tcu_gears"]:
      gear = cp.vl["TCU12"]["CUR_GR"]
    elif self.CP.carFingerprint in FEATURES["use_elect_gears"]:
      gear = cp.vl["ELECT_GEAR"]["Elect_Gear_Shifter"]
    else:
      gear = cp.vl["LVR12"]["CF_Lvr_Gear"]

    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(gear))

    if not self.CP.openpilotLongitudinalControl:
      if self.CP.carFingerprint in FEATURES["use_fca"]:
        ret.stockAeb = cp.vl["FCA11"]["FCA_CmdAct"] != 0
        ret.stockFcw = cp.vl["FCA11"]["CF_VSM_Warn"] == 2
      else:
        ret.stockAeb = cp.vl["SCC12"]["AEB_CmdAct"] != 0
        ret.stockFcw = cp.vl["SCC12"]["CF_VSM_Warn"] == 2

    if self.CP.enableBsm:
      ret.leftBlindspot = cp.vl["LCA11"]["CF_Lca_IndLeft"] != 0
      ret.rightBlindspot = cp.vl["LCA11"]["CF_Lca_IndRight"] != 0

    # save the entire LKAS11 and CLU11
    self.lkas11 = copy.copy(cp_cam.vl["LKAS11"])
    self.clu11 = copy.copy(cp.vl["CLU11"])
    self.park_brake = cp.vl["TCS13"]["PBRAKE_ACT"] == 1
    self.steer_state = cp.vl["MDPS12"]["CF_Mdps_ToiActive"]  # 0 NOT ACTIVE, 1 ACTIVE
    self.brake_error = cp.vl["TCS13"]["ACCEnable"] != 0 # 0 ACC CONTROL ENABLED, 1-3 ACC CONTROL DISABLED

    if not self.CP.openpilotLongitudinalControl:
      ret.radarObjValid = cp.vl["SCC11"]["ObjValid"] == 1
      self.lead_distance = cp.vl["SCC11"]["ACC_ObjDist"]

    return ret

  @staticmethod
  def get_can_parser(CP):
    signals = [
      # sig_name, sig_address, default
      ("WHL_SPD_FL", "WHL_SPD11", 0),
      ("WHL_SPD_FR", "WHL_SPD11", 0),
      ("WHL_SPD_RL", "WHL_SPD11", 0),
      ("WHL_SPD_RR", "WHL_SPD11", 0),

      ("YAW_RATE", "ESP12", 0),

      ("CF_Gway_DrvSeatBeltInd", "CGW4", 1),

      ("CF_Gway_DrvSeatBeltSw", "CGW1", 0),
      ("CF_Gway_DrvDrSw", "CGW1", 0),       # Driver Door
      ("CF_Gway_AstDrSw", "CGW1", 0),       # Passenger door
      ("CF_Gway_RLDrSw", "CGW2", 0),        # Rear reft door
      ("CF_Gway_RRDrSw", "CGW2", 0),        # Rear right door
      ("CF_Gway_TurnSigLh", "CGW1", 0),
      ("CF_Gway_TurnSigRh", "CGW1", 0),
      ("CF_Gway_ParkBrakeSw", "CGW1", 0),

      ("CYL_PRES", "ESP12", 0),

      ("CF_Clu_CruiseSwState", "CLU11", 0),
      ("CF_Clu_CruiseSwMain", "CLU11", 0),
      ("CF_Clu_SldMainSW", "CLU11", 0),
      ("CF_Clu_ParityBit1", "CLU11", 0),
      ("CF_Clu_VanzDecimal" , "CLU11", 0),
      ("CF_Clu_Vanz", "CLU11", 0),
      ("CF_Clu_SPEED_UNIT", "CLU11", 0),
      ("CF_Clu_DetentOut", "CLU11", 0),
      ("CF_Clu_RheostatLevel", "CLU11", 0),
      ("CF_Clu_CluInfo", "CLU11", 0),
      ("CF_Clu_AmpInfo", "CLU11", 0),
      ("CF_Clu_AliveCnt1", "CLU11", 0),

      ("ACCEnable", "TCS13", 0),
      ("ACC_REQ", "TCS13", 0),
      ("BrakeLight", "TCS13", 0),
      ("DriverBraking", "TCS13", 0),
      ("StandStill", "TCS13", 0),
      ("PBRAKE_ACT", "TCS13", 0),

      ("ESC_Off_Step", "TCS15", 0),
      ("AVH_LAMP", "TCS15", 0),

      ("CR_Mdps_StrColTq", "MDPS12", 0),
      ("CF_Mdps_ToiActive", "MDPS12", 0),
      ("CF_Mdps_ToiUnavail", "MDPS12", 0),
      ("CF_Mdps_ToiFlt", "MDPS12", 0),
      ("CR_Mdps_OutTq", "MDPS12", 0),

      ("SAS_Angle", "SAS11", 0),
      ("SAS_Speed", "SAS11", 0),

      ("LFA_Pressed", "BCM_PO_11", 0),
    ]

    checks = [
      # address, frequency
      ("MDPS12", 50),
      ("TCS13", 50),
      ("TCS15", 10),
      ("CLU11", 50),
      ("ESP12", 100),
      ("CGW1", 10),
      ("CGW2", 5),
      ("CGW4", 5),
      ("WHL_SPD11", 50),
      ("SAS11", 100),
    ]

    if not CP.openpilotLongitudinalControl:
      signals += [
        ("MainMode_ACC", "SCC11", 0),
        ("VSetDis", "SCC11", 0),
        ("SCCInfoDisplay", "SCC11", 0),
        ("ACC_ObjDist", "SCC11", 0),
        ("ACCMode", "SCC12", 1),
        ("ObjValid", "SCC11", 0),
      ]

      checks += [
        ("SCC11", 50),
        ("SCC12", 50),
      ]

      if CP.carFingerprint in FEATURES["use_fca"]:
        signals += [
          ("FCA_CmdAct", "FCA11", 0),
          ("CF_VSM_Warn", "FCA11", 0),
        ]
        checks += [("FCA11", 50)]
      else:
        signals += [
          ("AEB_CmdAct", "SCC12", 0),
          ("CF_VSM_Warn", "SCC12", 0),
        ]

    if CP.enableBsm:
      signals += [
        ("CF_Lca_IndLeft", "LCA11", 0),
        ("CF_Lca_IndRight", "LCA11", 0),
      ]
      checks += [("LCA11", 50)]

    if CP.carFingerprint in (HYBRID_CAR | EV_CAR):
      if CP.carFingerprint in HYBRID_CAR:
        signals += [
          ("CR_Vcu_AccPedDep_Pos", "E_EMS11", 0)
        ]
      else:
        signals += [
          ("Accel_Pedal_Pos", "E_EMS11", 0)
        ]
      checks += [
        ("E_EMS11", 50),
      ]
    else:
      signals += [
        ("PV_AV_CAN", "EMS12", 0),
        ("CF_Ems_AclAct", "EMS16", 0),
      ]
      checks += [
        ("EMS12", 100),
        ("EMS16", 100),
      ]

    if CP.carFingerprint in FEATURES["use_cluster_gears"]:
      signals += [
        ("CF_Clu_Gear", "CLU15", 0),
      ]
      checks += [
        ("CLU15", 5)
      ]
    elif CP.carFingerprint in FEATURES["use_tcu_gears"]:
      signals += [
        ("CUR_GR", "TCU12", 0)
      ]
      checks += [
        ("TCU12", 100)
      ]
    elif CP.carFingerprint in FEATURES["use_elect_gears"]:
      signals += [("Elect_Gear_Shifter", "ELECT_GEAR", 0)]
      checks += [("ELECT_GEAR", 20)]
    else:
      signals += [
        ("CF_Lvr_Gear", "LVR12", 0)
      ]
      checks += [
        ("LVR12", 100)
      ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 0, enforce_checks=False)

  @staticmethod
  def get_cam_can_parser(CP):

    signals = [
      # sig_name, sig_address, default
      ("CF_Lkas_LdwsActivemode", "LKAS11", 0),
      ("CF_Lkas_LdwsSysState", "LKAS11", 0),
      ("CF_Lkas_SysWarning", "LKAS11", 0),
      ("CF_Lkas_LdwsLHWarning", "LKAS11", 0),
      ("CF_Lkas_LdwsRHWarning", "LKAS11", 0),
      ("CF_Lkas_HbaLamp", "LKAS11", 0),
      ("CF_Lkas_FcwBasReq", "LKAS11", 0),
      ("CF_Lkas_HbaSysState", "LKAS11", 0),
      ("CF_Lkas_FcwOpt", "LKAS11", 0),
      ("CF_Lkas_HbaOpt", "LKAS11", 0),
      ("CF_Lkas_FcwSysState", "LKAS11", 0),
      ("CF_Lkas_FcwCollisionWarning", "LKAS11", 0),
      ("CF_Lkas_FusionState", "LKAS11", 0),
      ("CF_Lkas_FcwOpt_USM", "LKAS11", 0),
      ("CF_Lkas_LdwsOpt_USM", "LKAS11", 0),
    ]

    checks = [
      ("LKAS11", 100)
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 2)
