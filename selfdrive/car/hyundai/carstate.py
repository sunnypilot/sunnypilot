from collections import deque
import copy
import math

from cereal import car
from common.conversions import Conversions as CV
from common.params import Params
from opendbc.can.parser import CANParser
from opendbc.can.can_define import CANDefine
from selfdrive.car.hyundai.values import HyundaiFlags, DBC, FEATURES, CAMERA_SCC_CAR, CANFD_CAR, EV_CAR, HYBRID_CAR, NON_SCC_CAR, NON_SCC_NO_FCA_CAR, Buttons, CarControllerParams
from selfdrive.car.interfaces import CarStateBase

PREV_BUTTON_SAMPLES = 8
CLUSTER_SAMPLE_RATE = 20  # frames


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    can_define = CANDefine(DBC[CP.carFingerprint]["pt"])

    self.cruise_buttons = deque([Buttons.NONE] * PREV_BUTTON_SAMPLES, maxlen=PREV_BUTTON_SAMPLES)
    self.main_buttons = deque([Buttons.NONE] * PREV_BUTTON_SAMPLES, maxlen=PREV_BUTTON_SAMPLES)

    if CP.carFingerprint in CANFD_CAR:
      self.shifter_values = can_define.dv["GEAR_SHIFTER"]["GEAR"]
    elif self.CP.carFingerprint in FEATURES["use_cluster_gears"]:
      self.shifter_values = can_define.dv["CLU15"]["CF_Clu_Gear"]
    elif self.CP.carFingerprint in FEATURES["use_tcu_gears"]:
      self.shifter_values = can_define.dv["TCU12"]["CUR_GR"]
    else:  # preferred and elect gear methods use same definition
      self.shifter_values = can_define.dv["LVR12"]["CF_Lvr_Gear"]

    self.is_metric = False
    self.brake_error = False
    self.buttons_counter = 0

    self.cruise_info = {}

    # On some cars, CLU15->CF_Clu_VehicleSpeed can oscillate faster than the dash updates. Sample at 5 Hz
    self.cluster_speed = 0
    self.cluster_speed_counter = CLUSTER_SAMPLE_RATE

    self.params = CarControllerParams(CP)

    self.param_s = Params()
    self.enable_mads = self.param_s.get_bool("EnableMads")
    self.mads_disengage_lateral_on_brake = self.param_s.get_bool("DisengageLateralOnBrake")
    self.acc_mads_combo = self.param_s.get_bool("AccMadsCombo")
    self.below_speed_pause = self.param_s.get_bool("BelowSpeedPause")
    self.accEnabled = False
    self.madsEnabled = False
    self.leftBlinkerOn = False
    self.rightBlinkerOn = False
    self.disengageByBrake = False
    self.belowLaneChangeSpeed = True
    self.mainEnabled = False
    self.mads_enabled = None
    self.prev_mads_enabled = None
    self.lfa_enabled = None
    self.prev_lfa_enabled = None
    self.prev_cruiseState_enabled = False
    self.prev_acc_mads_combo = None
    self.prev_brake_pressed = False
    self.gap_adjust_cruise_tr = 4
    self.gap_adjust_cruise_counter = 0.
    self.e2e_long_hold_counter = 0.
    self.e2e_long_hold_gap = False
    self.e2eLongStatus = self.param_s.get_bool("EndToEndLong")
    self.escc_aeb_warning = 0
    self.escc_aeb_dec_cmd_act = 0
    self.escc_cmd_act = 0
    self.escc_aeb_dec_cmd = 0
    self.pcm_enabled = False
    self.prev_pcm_enabled = False

  def update(self, cp, cp_cam):
    if self.CP.carFingerprint in CANFD_CAR:
      return self.update_canfd(cp, cp_cam)

    ret = car.CarState.new_message()

    self.prev_mads_enabled = self.mads_enabled
    self.prev_lfa_enabled = self.lfa_enabled
    self.prev_brake_pressed = ret.brakePressed
    self.prev_main_buttons = self.main_buttons[-1]
    self.prev_cruise_buttons = self.cruise_buttons[-1]
    self.cruise_buttons.extend(cp.vl_all["CLU11"]["CF_Clu_CruiseSwState"])
    self.main_buttons.extend(cp.vl_all["CLU11"]["CF_Clu_CruiseSwMain"])
    self.gap_adjust_cruise = self.param_s.get_bool("GapAdjustCruise")
    self.gap_adjust_cruise_mode = int(self.param_s.get("GapAdjustCruiseMode"))
    self.gap_adjust_cruise_tr = int(self.param_s.get("GapAdjustCruiseTr"))
    self.e2eLongStatus = self.param_s.get_bool("EndToEndLong")

    cp_cruise = cp_cam if self.CP.carFingerprint in (CAMERA_SCC_CAR | NON_SCC_CAR) else cp
    self.is_metric = cp.vl["CLU11"]["CF_Clu_SPEED_UNIT"] == 0
    speed_conv = CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS

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
    ret.parkingBrake = cp.vl["TCS13"]["PBRAKE_ACT"] == 1
    ret.brakeLights = bool(cp.vl["TCS13"]["BrakeLight"] or ret.brakePressed or ret.brakeHoldActive or ret.parkingBrake)

    self.belowLaneChangeSpeed = ret.vEgo < (15 * CV.MPH_TO_MS) and self.below_speed_pause

    if self.CP.flags & HyundaiFlags.SP_CAN_LFA_BTN:
      self.lfa_enabled = cp.vl["BCM_PO_11"]["LFA_Pressed"] == 0

    if self.prev_lfa_enabled is None:
      self.prev_lfa_enabled = self.lfa_enabled

    ret.standstill = ret.vEgoRaw < 0.1

    self.cluster_speed_counter += 1
    if self.cluster_speed_counter > CLUSTER_SAMPLE_RATE:
      self.cluster_speed = cp.vl["CLU15"]["CF_Clu_VehicleSpeed"]
      self.cluster_speed_counter = 0

      # mimic how dash converts to imperial
      if not self.is_metric:
        self.cluster_speed = math.floor(self.cluster_speed * CV.KPH_TO_MPH + CV.KPH_TO_MPH)

    ret.vEgoCluster = self.cluster_speed * speed_conv

    ret.steeringAngleDeg = cp.vl["SAS11"]["SAS_Angle"]
    ret.steeringRateDeg = cp.vl["SAS11"]["SAS_Speed"]
    ret.yawRate = cp.vl["ESP12"]["YAW_RATE"]
    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_lamp(
      50, cp.vl["CGW1"]["CF_Gway_TurnSigLh"], cp.vl["CGW1"]["CF_Gway_TurnSigRh"])
    ret.steeringTorque = cp.vl["MDPS12"]["CR_Mdps_StrColTq"]
    ret.steeringTorqueEps = cp.vl["MDPS12"]["CR_Mdps_OutTq"]
    ret.steeringPressed = abs(ret.steeringTorque) > self.params.STEER_THRESHOLD

    self.leftBlinkerOn = cp.vl["CGW1"]["CF_Gway_TurnSigLh"] != 0
    self.rightBlinkerOn = cp.vl["CGW1"]["CF_Gway_TurnSigRh"] != 0

    # cruise state
    if self.CP.openpilotLongitudinalControl:
      if self.prev_main_buttons != 1:
        if self.main_buttons[-1] == 1:
          self.mainEnabled = not self.mainEnabled
      # These are not used for engage/disengage since openpilot keeps track of state using the buttons
      ret.cruiseState.available = cp.vl["TCS13"]["ACCEnable"] == 0 and self.mainEnabled
      ret.cruiseState.enabled = cp.vl["TCS13"]["ACC_REQ"] == 1 and self.accEnabled
      ret.cruiseState.standstill = False
    elif self.CP.carFingerprint in NON_SCC_CAR:
      ret.cruiseState.available = cp.vl['EMS16']['CRUISE_LAMP_M'] != 0
      ret.cruiseState.enabled = cp.vl["LVR12"]['CF_Lvr_CruiseSet'] != 0
      self.pcm_enabled = cp.vl["LVR12"]['CF_Lvr_CruiseSet'] != 0
      ret.cruiseState.speed = cp.vl["LVR12"]["CF_Lvr_CruiseSet"] * speed_conv
      ret.cruiseState.standstill = False
    else:
      ret.cruiseState.available = cp_cruise.vl["SCC11"]["MainMode_ACC"] == 1
      ret.cruiseState.enabled = cp_cruise.vl["SCC12"]["ACCMode"] != 0
      self.pcm_enabled = cp_cruise.vl["SCC12"]["ACCMode"] != 0
      ret.cruiseState.standstill = cp_cruise.vl["SCC11"]["SCCInfoDisplay"] == 4.
      ret.cruiseState.speed = cp_cruise.vl["SCC11"]["VSetDis"] * speed_conv

    self.mads_enabled = ret.cruiseState.available

    if self.prev_mads_enabled is None:
      self.prev_mads_enabled = self.mads_enabled

    if ret.cruiseState.available:
      if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
        if self.prev_cruise_buttons == 2: # SET-
          if self.cruise_buttons[-1] != 2:
            self.accEnabled = True
        elif self.prev_cruise_buttons == 1: # RESUME+
          if self.cruise_buttons[-1] != 1:
            self.accEnabled = True
        if not self.CP.pcmCruiseSpeed:
          if self.prev_main_buttons == 1: # ACC MAIN
            if self.main_buttons[-1] != 1:
              self.accEnabled = True
          elif self.prev_cruise_buttons == 4: # PAUSE
            if self.cruise_buttons[-1] != 4:
              self.accEnabled = True
      if self.CP.openpilotLongitudinalControl:
        if self.gap_adjust_cruise:
          if self.gap_adjust_cruise_mode in (0, 2):
            if self.cruise_buttons[-1] == 3:  # GAP
              self.gap_adjust_cruise_counter += 1
            elif self.prev_cruise_buttons == 3 and self.cruise_buttons[-1] != 3 and self.gap_adjust_cruise_counter < 50:  # GAP
              self.gap_adjust_cruise_counter = 0
              self.gap_adjust_cruise_tr -= 1
              if self.gap_adjust_cruise_tr < 1:
                self.gap_adjust_cruise_tr = 4
              self.param_s.put("GapAdjustCruiseTr", str(self.gap_adjust_cruise_tr))
            else:
              self.gap_adjust_cruise_counter = 0
        else:
          self.gap_adjust_cruise_tr = 4
        if self.cruise_buttons[-1] == 3:
          self.e2e_long_hold_counter += 1
          if self.e2e_long_hold_counter > 100 and not self.e2e_long_hold_gap:
            self.e2e_long_hold_counter = 0
            self.e2e_long_hold_gap = True
            self.e2eLongStatus = not self.e2eLongStatus
            self.param_s.put_bool("EndToEndLong", self.e2eLongStatus)
        else:
          self.e2e_long_hold_counter = 0
          self.e2e_long_hold_gap = False
      if self.enable_mads:
        if not self.prev_mads_enabled and self.mads_enabled:
          self.madsEnabled = True
        if self.prev_lfa_enabled != 1 and self.lfa_enabled == 1:
          self.madsEnabled = not self.madsEnabled
        if self.acc_mads_combo:
          if not self.prev_acc_mads_combo and ret.cruiseState.enabled:
            self.madsEnabled = True
          self.prev_acc_mads_combo = ret.cruiseState.enabled
    else:
      self.madsEnabled = False
      self.accEnabled = False
      self.e2e_long_hold_counter = 0
      self.e2e_long_hold_gap = False
      self.gap_adjust_cruise_counter = 0

    ret.gapAdjustCruiseTr = self.gap_adjust_cruise_tr
    ret.endToEndLong = self.e2eLongStatus

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.enable_mads or not self.CP.pcmCruiseSpeed:
      if not self.CP.pcmCruise:
        if self.prev_cruise_buttons != 4: # CANCEL
          if self.cruise_buttons[-1] == 4:
            self.accEnabled = False
            if not self.enable_mads:
              self.madsEnabled = False
      if not self.CP.pcmCruiseSpeed:
        if not self.pcm_enabled:
          self.accEnabled = False
          if not self.enable_mads:
            self.madsEnabled = False
      if ret.brakePressed and (not self.prev_brake_pressed or not ret.standstill):
        self.accEnabled = False
        if not self.enable_mads:
          self.madsEnabled = False

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.accEnabled = False
      self.accEnabled = ret.cruiseState.enabled or self.accEnabled

    if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
      ret.cruiseState.enabled = self.accEnabled

    if not self.enable_mads:
      if ret.cruiseState.enabled and not self.prev_cruiseState_enabled:
        self.madsEnabled = True
      elif not ret.cruiseState.enabled:
        self.madsEnabled = False
    self.prev_cruiseState_enabled = ret.cruiseState.enabled
    self.prev_pcm_enabled = self.pcm_enabled

    ret.steerFaultTemporary = False

    if self.madsEnabled:
      if (not self.belowLaneChangeSpeed and (self.leftBlinkerOn or self.rightBlinkerOn)) or\
        not (self.leftBlinkerOn or self.rightBlinkerOn):
        ret.steerFaultTemporary = cp.vl["MDPS12"]["CF_Mdps_ToiUnavail"] != 0 or cp.vl["MDPS12"]["CF_Mdps_ToiFlt"] != 0

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

    if not self.CP.openpilotLongitudinalControl and self.CP.carFingerprint not in NON_SCC_NO_FCA_CAR:
      aeb_src = "FCA11" if self.CP.carFingerprint in FEATURES["use_fca"] else "SCC12"
      aeb_sig = "FCA_CmdAct" if self.CP.carFingerprint in FEATURES["use_fca"] else "AEB_CmdAct"
      aeb_warning = cp_cruise.vl[aeb_src]["CF_VSM_Warn"] != 0
      aeb_braking = cp_cruise.vl[aeb_src]["CF_VSM_DecCmdAct"] != 0 or cp_cruise.vl[aeb_src][aeb_sig] != 0
      ret.stockFcw = aeb_warning and not aeb_braking
      ret.stockAeb = aeb_warning and aeb_braking
    elif self.CP.flags & HyundaiFlags.SP_ENHANCED_SCC:
      aeb_src = "ESCC"
      aeg_sig = "FCA_CmdAct" if self.CP.carFingerprint in FEATURES["use_fca"] else "AEB_CmdAct"
      aeb_warning_sig = "CF_VSM_Warn_FCA11" if self.CP.carFingerprint in FEATURES["use_fca"] else "CF_VSM_Warn_SCC12"
      aeb_braking_sig = "CF_VSM_DecCmdAct_FCA11" if self.CP.carFingerprint in FEATURES["use_fca"] else "CF_VSM_DecCmdAct_SCC12"
      aeb_braking_cmd = "CR_VSM_DecCmd_FCA11" if self.CP.carFingerprint in FEATURES["use_fca"] else "CR_VSM_DecCmd_SCC12"
      aeb_warning = cp.vl[aeb_src][aeb_warning_sig] != 0
      aeb_braking = cp.vl[aeb_src][aeb_braking_sig] != 0 or cp.vl[aeb_src][aeg_sig] != 0
      ret.stockFcw = aeb_warning and not aeb_braking
      ret.stockAeb = aeb_warning and aeb_braking
      self.escc_aeb_warning = cp.vl[aeb_src][aeb_warning_sig]
      self.escc_aeb_dec_cmd_act = cp.vl[aeb_src][aeb_braking_sig]
      self.escc_cmd_act = cp.vl[aeb_src][aeg_sig]
      self.escc_aeb_dec_cmd = cp.vl[aeb_src][aeb_braking_cmd]

    if self.CP.enableBsm:
      ret.leftBlindspot = cp.vl["LCA11"]["CF_Lca_IndLeft"] != 0
      ret.rightBlindspot = cp.vl["LCA11"]["CF_Lca_IndRight"] != 0

    # save the entire LKAS11 and CLU11
    self.lkas11 = copy.copy(cp_cam.vl["LKAS11"])
    self.clu11 = copy.copy(cp.vl["CLU11"])
    self.steer_state = cp.vl["MDPS12"]["CF_Mdps_ToiActive"]  # 0 NOT ACTIVE, 1 ACTIVE
    self.brake_error = cp.vl["TCS13"]["ACCEnable"] != 0  # 0 ACC CONTROL ENABLED, 1-3 ACC CONTROL DISABLED

    return ret

  def update_canfd(self, cp, cp_cam):
    ret = car.CarState.new_message()

    cruise_btn_msg = "CRUISE_BUTTONS_ALT" if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS else "CRUISE_BUTTONS"

    self.prev_mads_enabled = self.mads_enabled
    self.prev_main_buttons = self.main_buttons[-1]
    self.prev_cruise_buttons = self.cruise_buttons[-1]
    self.prev_brake_pressed = ret.brakePressed
    self.cruise_buttons.extend(cp.vl_all[cruise_btn_msg]["CRUISE_BUTTONS"])
    self.main_buttons.extend(cp.vl_all[cruise_btn_msg]["ADAPTIVE_CRUISE_MAIN_BTN"])

    if self.CP.carFingerprint in EV_CAR:
      ret.gas = cp.vl["ACCELERATOR"]["ACCELERATOR_PEDAL"] / 255.
    elif self.CP.carFingerprint in HYBRID_CAR:
      ret.gas = cp.vl["ACCELERATOR_ALT"]["ACCELERATOR_PEDAL"] / 1023.
    ret.gasPressed = ret.gas > 1e-5
    ret.brakePressed = cp.vl["TCS"]["DriverBraking"] == 1
    ret.brakeLights = bool(ret.brakePressed)

    self.mads_enabled = cp.vl[cruise_btn_msg]["LFA_BTN"] == 0

    if self.prev_mads_enabled is None:
      self.prev_mads_enabled = self.mads_enabled

    ret.doorOpen = cp.vl["DOORS_SEATBELTS"]["DRIVER_DOOR_OPEN"] == 1
    ret.seatbeltUnlatched = cp.vl["DOORS_SEATBELTS"]["DRIVER_SEATBELT_LATCHED"] == 0

    gear = cp.vl["GEAR_SHIFTER"]["GEAR"]
    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(gear))

    # TODO: figure out positions
    ret.wheelSpeeds = self.get_wheel_speeds(
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_1"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_2"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_3"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_4"],
    )
    ret.vEgoRaw = (ret.wheelSpeeds.fl + ret.wheelSpeeds.fr + ret.wheelSpeeds.rl + ret.wheelSpeeds.rr) / 4.
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = ret.vEgoRaw < 0.1

    self.belowLaneChangeSpeed = ret.vEgo < (15 * CV.MPH_TO_MS) and self.below_speed_pause

    ret.steeringRateDeg = cp.vl["STEERING_SENSORS"]["STEERING_RATE"]
    ret.steeringAngleDeg = cp.vl["STEERING_SENSORS"]["STEERING_ANGLE"] * -1
    ret.steeringTorque = cp.vl["MDPS"]["STEERING_COL_TORQUE"]
    ret.steeringTorqueEps = cp.vl["MDPS"]["STEERING_OUT_TORQUE"]
    ret.steeringPressed = abs(ret.steeringTorque) > self.params.STEER_THRESHOLD
    ret.steerFaultTemporary = cp.vl["MDPS"]["LKA_FAULT"] != 0

    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_lamp(50, cp.vl["BLINKERS"]["LEFT_LAMP"],
                                                                      cp.vl["BLINKERS"]["RIGHT_LAMP"])
    if self.CP.enableBsm:
      ret.leftBlindspot = cp.vl["BLINDSPOTS_REAR_CORNERS"]["FL_INDICATOR"] != 0
      ret.rightBlindspot = cp.vl["BLINDSPOTS_REAR_CORNERS"]["FR_INDICATOR"] != 0

    self.leftBlinkerOn = cp.vl["BLINKERS"]["LEFT_LAMP"] != 0
    self.rightBlinkerOn = cp.vl["BLINKERS"]["RIGHT_LAMP"] != 0

    ret.cruiseState.available = True
    self.is_metric = cp.vl["CLUSTER_INFO"]["DISTANCE_UNIT"] != 1
    if not self.CP.openpilotLongitudinalControl:
      speed_factor = CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS
      cp_cruise_info = cp if self.CP.flags & HyundaiFlags.CANFD_HDA2 else cp_cam
      ret.cruiseState.speed = cp_cruise_info.vl["CRUISE_INFO"]["SET_SPEED"] * speed_factor
      ret.cruiseState.standstill = cp_cruise_info.vl["CRUISE_INFO"]["CRUISE_STANDSTILL"] == 1
      ret.cruiseState.enabled = cp_cruise_info.vl["CRUISE_INFO"]["CRUISE_STATUS"] != 0
      self.pcm_enabled = cp_cruise_info.vl["CRUISE_INFO"]["CRUISE_STATUS"] != 0
      self.cruise_info = copy.copy(cp_cruise_info.vl["CRUISE_INFO"])

    if ret.cruiseState.available:
      if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
        if self.prev_cruise_buttons == 2: # SET-
          if self.cruise_buttons[-1] != 2:
            self.accEnabled = True
        elif self.prev_cruise_buttons == 1: # RESUME+
          if self.cruise_buttons[-1] != 1:
            self.accEnabled = True
        if not self.CP.pcmCruiseSpeed:
          if self.prev_main_buttons == 1: # ACC MAIN
            if self.main_buttons[-1] != 1:
              self.accEnabled = True
          elif self.prev_cruise_buttons == 4: # PAUSE
            if self.cruise_buttons[-1] != 4:
              self.accEnabled = True
      if self.enable_mads:
        if (self.prev_mads_enabled != 1 and self.mads_enabled == 1) or \
          (self.prev_main_buttons != 1 and self.main_buttons[-1] == 1):
          self.madsEnabled = not self.madsEnabled
        if self.acc_mads_combo:
          if not self.prev_acc_mads_combo and ret.cruiseState.enabled:
            self.madsEnabled = True
          self.prev_acc_mads_combo = ret.cruiseState.enabled
    else:
      self.madsEnabled = False
      self.accEnabled = False

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.enable_mads or not self.CP.pcmCruiseSpeed:
      if not self.CP.pcmCruise:
        if self.prev_cruise_buttons != 4: # CANCEL
          if self.cruise_buttons[-1] == 4:
            self.accEnabled = False
            if not self.enable_mads:
              self.madsEnabled = False
      if not self.CP.pcmCruiseSpeed:
        if not self.pcm_enabled:
          self.accEnabled = False
          if not self.enable_mads:
            self.madsEnabled = False
      if ret.brakePressed and (not self.prev_brake_pressed or not ret.standstill):
        self.accEnabled = False
        if not self.enable_mads:
          self.madsEnabled = False

    if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
      ret.cruiseState.enabled = self.accEnabled

    if not self.enable_mads:
      if ret.cruiseState.enabled and not self.prev_cruiseState_enabled:
        self.madsEnabled = True
      elif not ret.cruiseState.enabled:
        self.madsEnabled = False
    self.prev_cruiseState_enabled = ret.cruiseState.enabled
    self.prev_pcm_enabled = self.pcm_enabled

    self.buttons_counter = cp.vl[cruise_btn_msg]["COUNTER"]

    if self.CP.flags & HyundaiFlags.CANFD_HDA2:
      self.cam_0x2a4 = copy.copy(cp_cam.vl["CAM_0x2a4"])

    return ret

  @staticmethod
  def get_can_parser(CP):
    if CP.carFingerprint in CANFD_CAR:
      return CarState.get_can_parser_canfd(CP)

    signals = [
      # signal_name, signal_address
      ("WHL_SPD_FL", "WHL_SPD11"),
      ("WHL_SPD_FR", "WHL_SPD11"),
      ("WHL_SPD_RL", "WHL_SPD11"),
      ("WHL_SPD_RR", "WHL_SPD11"),

      ("YAW_RATE", "ESP12"),

      ("CF_Gway_DrvSeatBeltInd", "CGW4"),

      ("CF_Gway_DrvSeatBeltSw", "CGW1"),
      ("CF_Gway_DrvDrSw", "CGW1"),       # Driver Door
      ("CF_Gway_AstDrSw", "CGW1"),       # Passenger Door
      ("CF_Gway_RLDrSw", "CGW2"),        # Rear left Door
      ("CF_Gway_RRDrSw", "CGW2"),        # Rear right Door
      ("CF_Gway_TurnSigLh", "CGW1"),
      ("CF_Gway_TurnSigRh", "CGW1"),
      ("CF_Gway_ParkBrakeSw", "CGW1"),

      ("CYL_PRES", "ESP12"),

      ("CF_Clu_CruiseSwState", "CLU11"),
      ("CF_Clu_CruiseSwMain", "CLU11"),
      ("CF_Clu_SldMainSW", "CLU11"),
      ("CF_Clu_ParityBit1", "CLU11"),
      ("CF_Clu_VanzDecimal" , "CLU11"),
      ("CF_Clu_Vanz", "CLU11"),
      ("CF_Clu_SPEED_UNIT", "CLU11"),
      ("CF_Clu_DetentOut", "CLU11"),
      ("CF_Clu_RheostatLevel", "CLU11"),
      ("CF_Clu_CluInfo", "CLU11"),
      ("CF_Clu_AmpInfo", "CLU11"),
      ("CF_Clu_AliveCnt1", "CLU11"),

      ("CF_Clu_VehicleSpeed", "CLU15"),

      ("ACCEnable", "TCS13"),
      ("ACC_REQ", "TCS13"),
      ("BrakeLight", "TCS13"),
      ("DriverBraking", "TCS13"),
      ("StandStill", "TCS13"),
      ("PBRAKE_ACT", "TCS13"),

      ("ESC_Off_Step", "TCS15"),
      ("AVH_LAMP", "TCS15"),

      ("CR_Mdps_StrColTq", "MDPS12"),
      ("CF_Mdps_ToiActive", "MDPS12"),
      ("CF_Mdps_ToiUnavail", "MDPS12"),
      ("CF_Mdps_ToiFlt", "MDPS12"),
      ("CR_Mdps_OutTq", "MDPS12"),

      ("SAS_Angle", "SAS11"),
      ("SAS_Speed", "SAS11"),
    ]
    checks = [
      # address, frequency
      ("MDPS12", 50),
      ("TCS13", 50),
      ("TCS15", 10),
      ("CLU11", 50),
      ("CLU15", 5),
      ("ESP12", 100),
      ("CGW1", 10),
      ("CGW2", 5),
      ("CGW4", 5),
      ("WHL_SPD11", 50),
      ("SAS11", 100),
    ]

    if not CP.openpilotLongitudinalControl and CP.carFingerprint not in (CAMERA_SCC_CAR | NON_SCC_CAR):
      signals += [
        ("MainMode_ACC", "SCC11"),
        ("VSetDis", "SCC11"),
        ("SCCInfoDisplay", "SCC11"),
        ("ACC_ObjDist", "SCC11"),
        ("ACCMode", "SCC12"),
      ]
      checks += [
        ("SCC11", 50),
        ("SCC12", 50),
      ]

      if CP.carFingerprint in FEATURES["use_fca"]:
        signals += [
          ("FCA_CmdAct", "FCA11"),
          ("CF_VSM_Warn", "FCA11"),
          ("CF_VSM_DecCmdAct", "FCA11"),
        ]
        checks.append(("FCA11", 50))
      else:
        signals += [
          ("AEB_CmdAct", "SCC12"),
          ("CF_VSM_Warn", "SCC12"),
          ("CF_VSM_DecCmdAct", "SCC12"),
        ]

    if not CP.openpilotLongitudinalControl and CP.carFingerprint in NON_SCC_CAR:
      signals += [
        ("CRUISE_LAMP_M", "EMS16"),
        ("CF_Lvr_CruiseSet", "LVR12"),
      ]

    if CP.enableBsm:
      signals += [
        ("CF_Lca_IndLeft", "LCA11"),
        ("CF_Lca_IndRight", "LCA11"),
      ]
      checks.append(("LCA11", 50))

    if CP.carFingerprint in (HYBRID_CAR | EV_CAR):
      if CP.carFingerprint in HYBRID_CAR:
        signals.append(("CR_Vcu_AccPedDep_Pos", "E_EMS11"))
      else:
        signals.append(("Accel_Pedal_Pos", "E_EMS11"))
      checks.append(("E_EMS11", 50))
    else:
      signals += [
        ("PV_AV_CAN", "EMS12"),
        ("CF_Ems_AclAct", "EMS16"),
      ]
      checks += [
        ("EMS12", 100),
        ("EMS16", 100),
      ]

    if CP.carFingerprint in FEATURES["use_cluster_gears"]:
      signals.append(("CF_Clu_Gear", "CLU15"))
    elif CP.carFingerprint in FEATURES["use_tcu_gears"]:
      signals.append(("CUR_GR", "TCU12"))
      checks.append(("TCU12", 100))
    elif CP.carFingerprint in FEATURES["use_elect_gears"]:
      signals.append(("Elect_Gear_Shifter", "ELECT_GEAR"))
      checks.append(("ELECT_GEAR", 20))
    else:
      signals.append(("CF_Lvr_Gear", "LVR12"))
      checks.append(("LVR12", 100))

    if CP.flags & HyundaiFlags.SP_CAN_LFA_BTN:
      signals.append(("LFA_Pressed", "BCM_PO_11"))
      checks.append(("BCM_PO_11", 50))

    if CP.flags & HyundaiFlags.SP_ENHANCED_SCC:
      if CP.carFingerprint in FEATURES["use_fca"]:
        signals += [
          ("FCA_CmdAct", "ESCC"),
          ("CF_VSM_Warn_FCA11", "ESCC"),
          ("CF_VSM_DecCmdAct_FCA11", "ESCC"),
          ("CR_VSM_DecCmd_FCA11", "ESCC"),
        ]
      else:
        signals += [
          ("AEB_CmdAct", "ESCC"),
          ("CF_VSM_Warn_SCC12", "ESCC"),
          ("CF_VSM_DecCmdAct_SCC12", "ESCC"),
          ("CR_VSM_DecCmd_SCC12", "ESCC"),
        ]
      checks.append(("ESCC", 50))

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 0)

  @staticmethod
  def get_cam_can_parser(CP):
    if CP.carFingerprint in CANFD_CAR:
      return CarState.get_cam_can_parser_canfd(CP)

    signals = [
      # signal_name, signal_address
      ("CF_Lkas_LdwsActivemode", "LKAS11"),
      ("CF_Lkas_LdwsSysState", "LKAS11"),
      ("CF_Lkas_SysWarning", "LKAS11"),
      ("CF_Lkas_LdwsLHWarning", "LKAS11"),
      ("CF_Lkas_LdwsRHWarning", "LKAS11"),
      ("CF_Lkas_HbaLamp", "LKAS11"),
      ("CF_Lkas_FcwBasReq", "LKAS11"),
      ("CF_Lkas_HbaSysState", "LKAS11"),
      ("CF_Lkas_FcwOpt", "LKAS11"),
      ("CF_Lkas_HbaOpt", "LKAS11"),
      ("CF_Lkas_FcwSysState", "LKAS11"),
      ("CF_Lkas_FcwCollisionWarning", "LKAS11"),
      ("CF_Lkas_FusionState", "LKAS11"),
      ("CF_Lkas_FcwOpt_USM", "LKAS11"),
      ("CF_Lkas_LdwsOpt_USM", "LKAS11"),
    ]
    checks = [
      ("LKAS11", 100)
    ]

    if not CP.openpilotLongitudinalControl and CP.carFingerprint in (CAMERA_SCC_CAR | (NON_SCC_CAR - NON_SCC_NO_FCA_CAR)):
      if CP.carFingerprint in CAMERA_SCC_CAR:
        signals += [
          ("MainMode_ACC", "SCC11"),
          ("VSetDis", "SCC11"),
          ("SCCInfoDisplay", "SCC11"),
          ("ACC_ObjDist", "SCC11"),
          ("ACCMode", "SCC12"),
        ]
        checks += [
          ("SCC11", 50),
          ("SCC12", 50),
        ]

      if CP.carFingerprint in FEATURES["use_fca"]:
        signals += [
          ("FCA_CmdAct", "FCA11"),
          ("CF_VSM_Warn", "FCA11"),
          ("CF_VSM_DecCmdAct", "FCA11"),
        ]
        checks.append(("FCA11", 50))
      elif CP.carFingerprint in CAMERA_SCC_CAR:
        signals += [
          ("AEB_CmdAct", "SCC12"),
          ("CF_VSM_Warn", "SCC12"),
          ("CF_VSM_DecCmdAct", "SCC12"),
        ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 2)

  @staticmethod
  def get_can_parser_canfd(CP):

    cruise_btn_msg = "CRUISE_BUTTONS_ALT" if CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS else "CRUISE_BUTTONS"
    signals = [
      ("WHEEL_SPEED_1", "WHEEL_SPEEDS"),
      ("WHEEL_SPEED_2", "WHEEL_SPEEDS"),
      ("WHEEL_SPEED_3", "WHEEL_SPEEDS"),
      ("WHEEL_SPEED_4", "WHEEL_SPEEDS"),

      ("GEAR", "GEAR_SHIFTER"),

      ("STEERING_RATE", "STEERING_SENSORS"),
      ("STEERING_ANGLE", "STEERING_SENSORS"),
      ("STEERING_COL_TORQUE", "MDPS"),
      ("STEERING_OUT_TORQUE", "MDPS"),
      ("LKA_FAULT", "MDPS"),

      ("DriverBraking", "TCS"),

      ("COUNTER", cruise_btn_msg),
      ("CRUISE_BUTTONS", cruise_btn_msg),
      ("ADAPTIVE_CRUISE_MAIN_BTN", cruise_btn_msg),
      ("LFA_BTN", cruise_btn_msg),

      ("DISTANCE_UNIT", "CLUSTER_INFO"),

      ("LEFT_LAMP", "BLINKERS"),
      ("RIGHT_LAMP", "BLINKERS"),

      ("DRIVER_DOOR_OPEN", "DOORS_SEATBELTS"),
      ("DRIVER_SEATBELT_LATCHED", "DOORS_SEATBELTS"),
    ]

    checks = [
      ("WHEEL_SPEEDS", 100),
      ("GEAR_SHIFTER", 100),
      ("BRAKE", 100),
      ("STEERING_SENSORS", 100),
      ("MDPS", 100),
      ("TCS", 50),
      (cruise_btn_msg, 50),
      ("CLUSTER_INFO", 4),
      ("BLINKERS", 4),
      ("DOORS_SEATBELTS", 4),
    ]

    if CP.enableBsm:
      signals += [
        ("FL_INDICATOR", "BLINDSPOTS_REAR_CORNERS"),
        ("FR_INDICATOR", "BLINDSPOTS_REAR_CORNERS"),
      ]
      checks += [
        ("BLINDSPOTS_REAR_CORNERS", 20),
      ]

    if CP.flags & HyundaiFlags.CANFD_HDA2 and not CP.openpilotLongitudinalControl:
      signals += [
        ("CRUISE_STATUS", "CRUISE_INFO"),
        ("SET_SPEED", "CRUISE_INFO"),
        ("CRUISE_STANDSTILL", "CRUISE_INFO"),
      ]
      checks += [
        ("CRUISE_INFO", 50),
      ]

    if CP.carFingerprint in EV_CAR:
      signals += [
        ("ACCELERATOR_PEDAL", "ACCELERATOR"),
      ]
      checks += [
        ("ACCELERATOR", 100),
      ]
    elif CP.carFingerprint in HYBRID_CAR:
      signals += [
        ("ACCELERATOR_PEDAL", "ACCELERATOR_ALT"),
      ]
      checks += [
        ("ACCELERATOR_ALT", 100),
      ]

    bus = 5 if CP.flags & HyundaiFlags.CANFD_HDA2 else 4
    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, bus)

  @staticmethod
  def get_cam_can_parser_canfd(CP):
    if CP.flags & HyundaiFlags.CANFD_HDA2:
      signals = [(f"BYTE{i}", "CAM_0x2a4") for i in range(3, 24)]
      checks = [("CAM_0x2a4", 20)]
    else:
      signals = [
        ("COUNTER", "CRUISE_INFO"),
        ("NEW_SIGNAL_1", "CRUISE_INFO"),
        ("CRUISE_MAIN", "CRUISE_INFO"),
        ("CRUISE_STATUS", "CRUISE_INFO"),
        ("CRUISE_INACTIVE", "CRUISE_INFO"),
        ("ZEROS_9", "CRUISE_INFO"),
        ("CRUISE_STANDSTILL", "CRUISE_INFO"),
        ("ZEROS_5", "CRUISE_INFO"),
        ("DISTANCE_SETTING", "CRUISE_INFO"),
        ("SET_SPEED", "CRUISE_INFO"),
        ("NEW_SIGNAL_4", "CRUISE_INFO"),
      ]

      checks = [
        ("CRUISE_INFO", 50),
      ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 6)
