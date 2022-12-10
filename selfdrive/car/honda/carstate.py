from collections import defaultdict

from cereal import car
from common.conversions import Conversions as CV
from common.numpy_fast import interp
from common.params import Params
from opendbc.can.can_define import CANDefine
from opendbc.can.parser import CANParser
from selfdrive.car.honda.hondacan import get_pt_bus
from selfdrive.car.honda.values import CAR, DBC, STEER_THRESHOLD, HONDA_BOSCH, HONDA_NIDEC_ALT_SCM_MESSAGES, HONDA_BOSCH_ALT_BRAKE_SIGNAL, HONDA_BOSCH_RADARLESS
from selfdrive.car.interfaces import CarStateBase
from selfdrive.controls.lib.desire_helper import LANE_CHANGE_SPEED_MIN

TransmissionType = car.CarParams.TransmissionType


def get_can_signals(CP, gearbox_msg, main_on_sig_msg):
  signals = [
    ("XMISSION_SPEED", "ENGINE_DATA"),
    ("WHEEL_SPEED_FL", "WHEEL_SPEEDS"),
    ("WHEEL_SPEED_FR", "WHEEL_SPEEDS"),
    ("WHEEL_SPEED_RL", "WHEEL_SPEEDS"),
    ("WHEEL_SPEED_RR", "WHEEL_SPEEDS"),
    ("STEER_ANGLE", "STEERING_SENSORS"),
    ("STEER_ANGLE_RATE", "STEERING_SENSORS"),
    ("MOTOR_TORQUE", "STEER_MOTOR_TORQUE"),
    ("STEER_TORQUE_SENSOR", "STEER_STATUS"),
    ("IMPERIAL_UNIT", "CAR_SPEED"),
    ("ROUGH_CAR_SPEED_2", "CAR_SPEED"),
    ("LEFT_BLINKER", "SCM_FEEDBACK"),
    ("RIGHT_BLINKER", "SCM_FEEDBACK"),
    ("SEATBELT_DRIVER_LAMP", "SEATBELT_STATUS"),
    ("SEATBELT_DRIVER_LATCHED", "SEATBELT_STATUS"),
    ("BRAKE_PRESSED", "POWERTRAIN_DATA"),
    ("BRAKE_SWITCH", "POWERTRAIN_DATA"),
    ("CRUISE_BUTTONS", "SCM_BUTTONS"),
    ("ESP_DISABLED", "VSA_STATUS"),
    ("USER_BRAKE", "VSA_STATUS"),
    ("BRAKE_HOLD_ACTIVE", "VSA_STATUS"),
    ("STEER_STATUS", "STEER_STATUS"),
    ("GEAR_SHIFTER", gearbox_msg),
    ("GEAR", gearbox_msg),
    ("PEDAL_GAS", "POWERTRAIN_DATA"),
    ("CRUISE_SETTING", "SCM_BUTTONS"),
    ("ACC_STATUS", "POWERTRAIN_DATA"),
    ("MAIN_ON", main_on_sig_msg),
  ]

  checks = [
    ("ENGINE_DATA", 100),
    ("WHEEL_SPEEDS", 50),
    ("STEERING_SENSORS", 100),
    ("SEATBELT_STATUS", 10),
    ("CRUISE", 10),
    ("POWERTRAIN_DATA", 100),
    ("CAR_SPEED", 10),
    ("VSA_STATUS", 50),
    ("STEER_STATUS", 100),
    ("STEER_MOTOR_TORQUE", 0),  # TODO: not on every car
  ]

  if CP.carFingerprint == CAR.ODYSSEY_CHN:
    checks += [
      ("SCM_FEEDBACK", 25),
      ("SCM_BUTTONS", 50),
    ]
  else:
    checks += [
      ("SCM_FEEDBACK", 10),
      ("SCM_BUTTONS", 25),
    ]

  if CP.carFingerprint in (CAR.CRV_HYBRID, CAR.CIVIC_BOSCH_DIESEL, CAR.ACURA_RDX_3G, CAR.HONDA_E):
    checks.append((gearbox_msg, 50))
  else:
    checks.append((gearbox_msg, 100))

  if CP.carFingerprint in HONDA_BOSCH_ALT_BRAKE_SIGNAL:
    signals.append(("BRAKE_PRESSED", "BRAKE_MODULE"))
    checks.append(("BRAKE_MODULE", 50))

  if CP.carFingerprint in (HONDA_BOSCH | {CAR.CIVIC, CAR.ODYSSEY, CAR.ODYSSEY_CHN}):
    signals.append(("EPB_STATE", "EPB_STATUS"))
    checks.append(("EPB_STATUS", 50))

  if CP.carFingerprint in HONDA_BOSCH:
    # these messages are on camera bus on radarless cars
    if not CP.openpilotLongitudinalControl and CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
      signals += [
        ("CRUISE_CONTROL_LABEL", "ACC_HUD"),
        ("CRUISE_SPEED", "ACC_HUD"),
        ("ACCEL_COMMAND", "ACC_CONTROL"),
        ("AEB_STATUS", "ACC_CONTROL"),
        ("BRAKE_LIGHTS", "ACC_CONTROL"),
      ]
      checks += [
        ("ACC_HUD", 10),
        ("ACC_CONTROL", 50),
      ]
  else:  # Nidec signals
    signals += [("CRUISE_SPEED_PCM", "CRUISE"),
                ("CRUISE_SPEED_OFFSET", "CRUISE_PARAMS")]

    if CP.carFingerprint == CAR.ODYSSEY_CHN:
      checks.append(("CRUISE_PARAMS", 10))
    else:
      checks.append(("CRUISE_PARAMS", 50))

  if CP.carFingerprint in (CAR.ACCORD, CAR.ACCORDH, CAR.CIVIC_BOSCH, CAR.CIVIC_BOSCH_DIESEL, CAR.CRV_HYBRID, CAR.INSIGHT, CAR.ACURA_RDX_3G, CAR.HONDA_E, CAR.CIVIC_2022):
    signals.append(("DRIVERS_DOOR_OPEN", "SCM_FEEDBACK"))
  elif CP.carFingerprint in (CAR.ODYSSEY_CHN, CAR.FREED, CAR.HRV):
    signals.append(("DRIVERS_DOOR_OPEN", "SCM_BUTTONS"))
  else:
    signals += [("DOOR_OPEN_FL", "DOORS_STATUS"),
                ("DOOR_OPEN_FR", "DOORS_STATUS"),
                ("DOOR_OPEN_RL", "DOORS_STATUS"),
                ("DOOR_OPEN_RR", "DOORS_STATUS")]
    checks.append(("DOORS_STATUS", 3))

  # add gas interceptor reading if we are using it
  if CP.enableGasInterceptor:
    signals.append(("INTERCEPTOR_GAS", "GAS_SENSOR"))
    signals.append(("INTERCEPTOR_GAS2", "GAS_SENSOR"))
    checks.append(("GAS_SENSOR", 50))

  if CP.openpilotLongitudinalControl:
    signals += [
      ("BRAKE_ERROR_1", "STANDSTILL"),
      ("BRAKE_ERROR_2", "STANDSTILL")
    ]
    checks.append(("STANDSTILL", 50))

  return signals, checks


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    can_define = CANDefine(DBC[CP.carFingerprint]["pt"])
    self.gearbox_msg = "GEARBOX"
    if CP.carFingerprint == CAR.ACCORD and CP.transmissionType == TransmissionType.cvt:
      self.gearbox_msg = "GEARBOX_15T"

    self.main_on_sig_msg = "SCM_FEEDBACK"
    if CP.carFingerprint in HONDA_NIDEC_ALT_SCM_MESSAGES:
      self.main_on_sig_msg = "SCM_BUTTONS"

    self.shifter_values = can_define.dv[self.gearbox_msg]["GEAR_SHIFTER"]
    self.steer_status_values = defaultdict(lambda: "UNKNOWN", can_define.dv["STEER_STATUS"]["STEER_STATUS"])

    self.brake_error = False
    self.brake_switch_prev = False
    self.brake_switch_active = False
    self.cruise_setting = 0
    self.v_cruise_pcm_prev = 0

    # When available we use cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] to populate vEgoCluster
    # However, on cars without a digital speedometer this is not always present (HRV, FIT, CRV 2016, ILX and RDX)
    self.dash_speed_seen = False

    self.param_s = Params()
    self.enable_mads = self.param_s.get_bool("EnableMads")
    self.mads_disengage_lateral_on_brake = self.param_s.get_bool("DisengageLateralOnBrake")
    self.acc_mads_combo = self.param_s.get_bool("AccMadsCombo")
    self.below_speed_pause = self.param_s.get_bool("BelowSpeedPause")
    self.resumeAvailable = False
    self.accEnabled = False
    self.madsEnabled = False
    self.leftBlinkerOn = False
    self.rightBlinkerOn = False
    self.disengageByBrake = False
    self.belowLaneChangeSpeed = True
    self.mads_enabled = False
    self.prev_mads_enabled = False
    self.prev_cruiseState_enabled = False
    self.prev_acc_mads_combo = None
    self.prev_brake_pressed = False
    self.gap_adjust_cruise_tr = 0
    self.gap_adjust_cruise_counter = 0.
    self.e2e_long_hold_counter = 0.
    self.e2e_long_hold_gap = False
    self.e2eLongStatus = self.param_s.get_bool("ExperimentalMode")

  def update(self, cp, cp_cam, cp_body):
    ret = car.CarState.new_message()

    # car params
    v_weight_v = [0., 1.]  # don't trust smooth speed at low values to avoid premature zero snapping
    v_weight_bp = [1., 6.]   # smooth blending, below ~0.6m/s the smooth speed snaps to zero

    # update prevs, update must run once per loop
    self.prev_cruise_buttons = self.cruise_buttons
    self.prev_cruise_setting = self.cruise_setting
    self.prev_mads_enabled = self.mads_enabled
    self.prev_brake_pressed = ret.brakePressed
    self.gap_adjust_cruise = self.param_s.get_bool("GapAdjustCruise")
    self.gap_adjust_cruise_mode = int(self.param_s.get("GapAdjustCruiseMode"))
    self.gap_adjust_cruise_tr = int(self.param_s.get("GapAdjustCruiseTr"))
    self.e2eLongStatus = self.param_s.get_bool("ExperimentalMode")
    self.cruise_setting = cp.vl["SCM_BUTTONS"]["CRUISE_SETTING"]
    self.cruise_buttons = cp.vl["SCM_BUTTONS"]["CRUISE_BUTTONS"]

    # used for car hud message
    self.is_metric = not cp.vl["CAR_SPEED"]["IMPERIAL_UNIT"]

    # ******************* parse out can *******************
    # STANDSTILL->WHEELS_MOVING bit can be noisy around zero, so use XMISSION_SPEED
    # panda checks if the signal is non-zero
    ret.standstill = cp.vl["ENGINE_DATA"]["XMISSION_SPEED"] < 1e-5
    # TODO: find a common signal across all cars
    if self.CP.carFingerprint in (CAR.ACCORD, CAR.ACCORDH, CAR.CIVIC_BOSCH, CAR.CIVIC_BOSCH_DIESEL, CAR.CRV_HYBRID, CAR.INSIGHT, CAR.ACURA_RDX_3G, CAR.HONDA_E, CAR.CIVIC_2022):
      ret.doorOpen = bool(cp.vl["SCM_FEEDBACK"]["DRIVERS_DOOR_OPEN"])
    elif self.CP.carFingerprint in (CAR.ODYSSEY_CHN, CAR.FREED, CAR.HRV):
      ret.doorOpen = bool(cp.vl["SCM_BUTTONS"]["DRIVERS_DOOR_OPEN"])
    else:
      ret.doorOpen = any([cp.vl["DOORS_STATUS"]["DOOR_OPEN_FL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_FR"],
                          cp.vl["DOORS_STATUS"]["DOOR_OPEN_RL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_RR"]])
    ret.seatbeltUnlatched = bool(cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LAMP"] or not cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LATCHED"])

    if self.CP.openpilotLongitudinalControl:
      self.brake_error = cp.vl["STANDSTILL"]["BRAKE_ERROR_1"] or cp.vl["STANDSTILL"]["BRAKE_ERROR_2"]
    ret.espDisabled = cp.vl["VSA_STATUS"]["ESP_DISABLED"] != 0

    ret.wheelSpeeds = self.get_wheel_speeds(
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FR"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RR"],
    )
    v_wheel = (ret.wheelSpeeds.fl + ret.wheelSpeeds.fr + ret.wheelSpeeds.rl + ret.wheelSpeeds.rr) / 4.0

    # blend in transmission speed at low speed, since it has more low speed accuracy
    v_weight = interp(v_wheel, v_weight_bp, v_weight_v)
    ret.vEgoRaw = (1. - v_weight) * cp.vl["ENGINE_DATA"]["XMISSION_SPEED"] * CV.KPH_TO_MS * self.CP.wheelSpeedFactor + v_weight * v_wheel
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)

    self.dash_speed_seen = self.dash_speed_seen or cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] > 1e-3
    if self.dash_speed_seen:
      conversion = CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS
      ret.vEgoCluster = cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] * conversion

    self.belowLaneChangeSpeed = ret.vEgo < LANE_CHANGE_SPEED_MIN and self.below_speed_pause

    ret.steeringAngleDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE"]
    ret.steeringRateDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE_RATE"]

    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_stalk(
      250, cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"], cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"])
    ret.brakeHoldActive = cp.vl["VSA_STATUS"]["BRAKE_HOLD_ACTIVE"] == 1

    self.leftBlinkerOn = cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"] != 0
    self.rightBlinkerOn = cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"] != 0

    # TODO: set for all cars
    if self.CP.carFingerprint in (HONDA_BOSCH | {CAR.CIVIC, CAR.ODYSSEY, CAR.ODYSSEY_CHN}):
      ret.parkingBrake = cp.vl["EPB_STATUS"]["EPB_STATE"] != 0

    gear = int(cp.vl[self.gearbox_msg]["GEAR_SHIFTER"])
    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(gear, None))

    if self.CP.enableGasInterceptor:
      # Same threshold as panda, equivalent to 1e-5 with previous DBC scaling
      ret.gas = (cp.vl["GAS_SENSOR"]["INTERCEPTOR_GAS"] + cp.vl["GAS_SENSOR"]["INTERCEPTOR_GAS2"]) // 2
      ret.gasPressed = ret.gas > 492
    else:
      ret.gas = cp.vl["POWERTRAIN_DATA"]["PEDAL_GAS"]
      ret.gasPressed = ret.gas > 1e-5

    ret.steeringTorque = cp.vl["STEER_STATUS"]["STEER_TORQUE_SENSOR"]
    ret.steeringTorqueEps = cp.vl["STEER_MOTOR_TORQUE"]["MOTOR_TORQUE"]
    ret.steeringPressed = abs(ret.steeringTorque) > STEER_THRESHOLD.get(self.CP.carFingerprint, 1200)

    if self.CP.carFingerprint in HONDA_BOSCH:
      if not self.CP.openpilotLongitudinalControl:
        # ACC_HUD is on camera bus on radarless cars
        acc_hud = cp_cam.vl["ACC_HUD"] if self.CP.carFingerprint in HONDA_BOSCH_RADARLESS else cp.vl["ACC_HUD"]
        ret.cruiseState.nonAdaptive = acc_hud["CRUISE_CONTROL_LABEL"] != 0
        ret.cruiseState.standstill = acc_hud["CRUISE_SPEED"] == 252.

        # on certain cars, CRUISE_SPEED changes to imperial with car's unit setting
        conversion = CV.MPH_TO_MS if self.CP.carFingerprint in HONDA_BOSCH_RADARLESS and not self.is_metric else CV.KPH_TO_MS
        # On set, cruise set speed pulses between 254~255 and the set speed prev is set to avoid this.
        ret.cruiseState.speed = self.v_cruise_pcm_prev if acc_hud["CRUISE_SPEED"] > 160.0 else acc_hud["CRUISE_SPEED"] * conversion
        self.v_cruise_pcm_prev = ret.cruiseState.speed
    else:
      ret.cruiseState.speed = cp.vl["CRUISE"]["CRUISE_SPEED_PCM"] * CV.KPH_TO_MS

    if self.CP.carFingerprint in HONDA_BOSCH_ALT_BRAKE_SIGNAL:
      ret.brakePressed = cp.vl["BRAKE_MODULE"]["BRAKE_PRESSED"] != 0
    else:
      # brake switch has shown some single time step noise, so only considered when
      # switch is on for at least 2 consecutive CAN samples
      # brake switch rises earlier than brake pressed but is never 1 when in park
      brake_switch_vals = cp.vl_all["POWERTRAIN_DATA"]["BRAKE_SWITCH"]
      if len(brake_switch_vals):
        brake_switch = cp.vl["POWERTRAIN_DATA"]["BRAKE_SWITCH"] != 0
        if len(brake_switch_vals) > 1:
          self.brake_switch_prev = brake_switch_vals[-2] != 0
        self.brake_switch_active = brake_switch and self.brake_switch_prev
        self.brake_switch_prev = brake_switch
      ret.brakePressed = (cp.vl["POWERTRAIN_DATA"]["BRAKE_PRESSED"] != 0) or self.brake_switch_active

    ret.brake = cp.vl["VSA_STATUS"]["USER_BRAKE"]
    ret.cruiseState.enabled = cp.vl["POWERTRAIN_DATA"]["ACC_STATUS"] != 0
    ret.cruiseState.available = bool(cp.vl[self.main_on_sig_msg]["MAIN_ON"])

    self.mads_enabled = ret.cruiseState.available

    # Gets rid of Pedal Grinding noise when brake is pressed at slow speeds for some models
    if self.CP.carFingerprint in (CAR.PILOT, CAR.PASSPORT, CAR.RIDGELINE):
      if ret.brake > 0.1:
        ret.brakePressed = True

    if self.CP.carFingerprint in (CAR.CIVIC, CAR.ODYSSEY, CAR.ODYSSEY_CHN, CAR.CRV_5G, CAR.ACCORD, CAR.ACCORDH, CAR.CIVIC_BOSCH,
                                    CAR.CIVIC_BOSCH_DIESEL, CAR.CRV_HYBRID, CAR.INSIGHT, CAR.ACURA_RDX_3G, CAR.HONDA_E):
      ret.brakeLights = bool(ret.brakePressed or cp.vl["ACC_CONTROL"]['BRAKE_LIGHTS'] != 0 or ret.brake > 0.4 or ret.parkingBrake) if not self.CP.openpilotLongitudinalControl else \
                         bool(ret.brakePressed or ret.brake > 0.4 or ret.parkingBrake)
    elif self.CP.carFingerprint in HONDA_BOSCH and self.CP.carFingerprint not in (CAR.CIVIC, CAR.ODYSSEY, CAR.ODYSSEY_CHN, CAR.CRV_5G, CAR.ACCORD, CAR.ACCORDH, CAR.CIVIC_BOSCH,
                                    CAR.CIVIC_BOSCH_DIESEL, CAR.CRV_HYBRID, CAR.INSIGHT, CAR.ACURA_RDX_3G, CAR.HONDA_E) and self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
      ret.brakeLights = bool(ret.brakePressed or cp.vl["ACC_CONTROL"]['BRAKE_LIGHTS'] != 0 or ret.brake > 0.4) if not self.CP.openpilotLongitudinalControl else \
                         bool(ret.brakePressed or ret.brake > 0.4)
    else:
      ret.brakeLights = bool(ret.brakePressed)

    if ret.cruiseState.available:
      if not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed:
        if self.prev_cruise_buttons == 3:  # SET-
          if self.cruise_buttons != 3:
            self.accEnabled = True
        elif self.prev_cruise_buttons == 4 and self.resumeAvailable:  # RESUME+
          if self.cruise_buttons != 4:
            self.accEnabled = True
      if self.CP.openpilotLongitudinalControl:
        if self.gap_adjust_cruise:
          if self.gap_adjust_cruise_mode in (0, 2):
            if self.cruise_setting == 3:  # DISTANCE_ADJ
              self.gap_adjust_cruise_counter += 1
            elif self.prev_cruise_setting == 3 and self.cruise_setting != 3 and self.gap_adjust_cruise_counter < 50:  # DISTANCE_ADJ
              self.gap_adjust_cruise_counter = 0
              self.gap_adjust_cruise_tr -= 1
              if self.gap_adjust_cruise_tr < 0:
                self.gap_adjust_cruise_tr = 3
              self.param_s.put("GapAdjustCruiseTr", str(self.gap_adjust_cruise_tr))
            else:
              self.gap_adjust_cruise_counter = 0
        else:
          self.gap_adjust_cruise_tr = 0
        if self.cruise_setting == 3:
          self.e2e_long_hold_counter += 1
          if self.e2e_long_hold_counter > 50 and not self.e2e_long_hold_gap:
            self.e2e_long_hold_counter = 0
            self.e2e_long_hold_gap = True
            self.e2eLongStatus = not self.e2eLongStatus
            self.param_s.put_bool("ExperimentalMode", self.e2eLongStatus)
        else:
          self.e2e_long_hold_counter = 0
          self.e2e_long_hold_gap = False
      if self.enable_mads:
        if not self.prev_mads_enabled and self.mads_enabled:
          self.madsEnabled = True
        if self.prev_cruise_setting != 1 and self.cruise_setting == 1:
          self.madsEnabled = not self.madsEnabled
        if self.acc_mads_combo:
          if not self.prev_acc_mads_combo and ret.cruiseState.enabled:
            self.madsEnabled = True
          self.prev_acc_mads_combo = ret.cruiseState.enabled
    else:
      self.madsEnabled = False
      self.accEnabled = False
      self.resumeAvailable = False
      self.e2e_long_hold_counter = 0
      self.e2e_long_hold_gap = False
      self.gap_adjust_cruise_counter = 0

    ret.gapAdjustCruiseTr = self.gap_adjust_cruise_tr
    ret.endToEndLong = self.e2eLongStatus

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.enable_mads or not self.CP.pcmCruiseSpeed:
      if self.prev_cruise_buttons != 2:  # CANCEL
        if self.cruise_buttons == 2:
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
      if ret.cruiseState.enabled:
        self.resumeAvailable = True

    if not self.enable_mads:
      if ret.cruiseState.enabled and not self.prev_cruiseState_enabled:
        self.madsEnabled = True
      elif not ret.cruiseState.enabled:
        self.madsEnabled = False
    self.prev_cruiseState_enabled = ret.cruiseState.enabled

    ret.steerFaultPermanent = False
    ret.steerFaultTemporary = False

    if self.madsEnabled:
      steer_status = self.steer_status_values[cp.vl["STEER_STATUS"]["STEER_STATUS"]]
      ret.steerFaultPermanent = steer_status not in ("NORMAL", "NO_TORQUE_ALERT_1", "NO_TORQUE_ALERT_2", "LOW_SPEED_LOCKOUT", "TMP_FAULT")
      if (not self.belowLaneChangeSpeed and (ret.leftBlinker or ret.rightBlinker)) or \
        not (ret.leftBlinker or ret.rightBlinker):
        # LOW_SPEED_LOCKOUT is not worth a warning
        # NO_TORQUE_ALERT_2 can be caused by bump or steering nudge from driver
        ret.steerFaultTemporary = steer_status not in ("NORMAL", "LOW_SPEED_LOCKOUT", "NO_TORQUE_ALERT_2")

    if self.CP.carFingerprint in HONDA_BOSCH:
      # TODO: find the radarless AEB_STATUS bit and make sure ACCEL_COMMAND is correct to enable AEB alerts
      if self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
        ret.stockAeb = (not self.CP.openpilotLongitudinalControl) and bool(cp.vl["ACC_CONTROL"]["AEB_STATUS"] and cp.vl["ACC_CONTROL"]["ACCEL_COMMAND"] < -1e-5)
    else:
      ret.stockAeb = bool(cp_cam.vl["BRAKE_COMMAND"]["AEB_REQ_1"] and cp_cam.vl["BRAKE_COMMAND"]["COMPUTER_BRAKE"] > 1e-5)

    self.acc_hud = False
    self.lkas_hud = False
    if self.CP.carFingerprint not in HONDA_BOSCH:
      ret.stockFcw = cp_cam.vl["BRAKE_COMMAND"]["FCW"] != 0
      self.acc_hud = cp_cam.vl["ACC_HUD"]
      self.stock_brake = cp_cam.vl["BRAKE_COMMAND"]
    if self.CP.carFingerprint in HONDA_BOSCH_RADARLESS:
      self.lkas_hud = cp_cam.vl["LKAS_HUD"]

    if self.CP.enableBsm and self.CP.carFingerprint in (CAR.CRV_5G, ):
      # BSM messages are on B-CAN, requires a panda forwarding B-CAN messages to CAN 0
      # more info here: https://github.com/commaai/openpilot/pull/1867
      ret.leftBlindspot = cp_body.vl["BSM_STATUS_LEFT"]["BSM_ALERT"] == 1
      ret.rightBlindspot = cp_body.vl["BSM_STATUS_RIGHT"]["BSM_ALERT"] == 1

    return ret

  def get_can_parser(self, CP):
    signals, checks = get_can_signals(CP, self.gearbox_msg, self.main_on_sig_msg)
    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, get_pt_bus(CP.carFingerprint))

  @staticmethod
  def get_cam_can_parser(CP):
    signals = []
    checks = [
      ("STEERING_CONTROL", 100),
    ]

    if CP.carFingerprint in HONDA_BOSCH_RADARLESS:
      signals.append(("LKAS_PROBLEM", "LKAS_HUD"))
      checks.append(("LKAS_HUD", 10))
      if not CP.openpilotLongitudinalControl:
        signals += [
          ("CRUISE_SPEED", "ACC_HUD"),
          ("CRUISE_CONTROL_LABEL", "ACC_HUD"),
        ]
        checks.append(("ACC_HUD", 10))

    elif CP.carFingerprint not in HONDA_BOSCH:
      signals += [("COMPUTER_BRAKE", "BRAKE_COMMAND"),
                  ("AEB_REQ_1", "BRAKE_COMMAND"),
                  ("FCW", "BRAKE_COMMAND"),
                  ("CHIME", "BRAKE_COMMAND"),
                  ("FCM_OFF", "ACC_HUD"),
                  ("FCM_OFF_2", "ACC_HUD"),
                  ("FCM_PROBLEM", "ACC_HUD"),
                  ("ICONS", "ACC_HUD")]
      checks += [
        ("ACC_HUD", 10),
        ("BRAKE_COMMAND", 50),
      ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, 2)

  @staticmethod
  def get_body_can_parser(CP):
    if CP.enableBsm and CP.carFingerprint == CAR.CRV_5G:
      signals = [("BSM_ALERT", "BSM_STATUS_RIGHT"),
                 ("BSM_ALERT", "BSM_STATUS_LEFT")]

      checks = [
        ("BSM_STATUS_LEFT", 3),
        ("BSM_STATUS_RIGHT", 3),
      ]
      bus_body = 0 # B-CAN is forwarded to ACC-CAN radar side (CAN 0 on fake ethernet port)
      return CANParser(DBC[CP.carFingerprint]["body"], signals, checks, bus_body)
    return None
