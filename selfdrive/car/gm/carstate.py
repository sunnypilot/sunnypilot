import copy
from cereal import car
from common.conversions import Conversions as CV
from common.numpy_fast import mean
from common.params import Params
from opendbc.can.can_define import CANDefine
from opendbc.can.parser import CANParser
from selfdrive.car.interfaces import CarStateBase
from selfdrive.car.gm.values import DBC, AccState, CanBus, STEER_THRESHOLD
from selfdrive.controls.lib.desire_helper import LANE_CHANGE_SPEED_MIN

TransmissionType = car.CarParams.TransmissionType
NetworkLocation = car.CarParams.NetworkLocation
STANDSTILL_THRESHOLD = 10 * 0.0311 * CV.KPH_TO_MS


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    can_define = CANDefine(DBC[CP.carFingerprint]["pt"])
    self.shifter_values = can_define.dv["ECMPRDNL2"]["PRNDL2"]
    self.loopback_lka_steering_cmd_updated = False
    self.camera_lka_steering_cmd_counter = 0
    self.buttons_counter = 0

    self.param_s = Params()
    self.enable_mads = self.param_s.get_bool("EnableMads")
    self.mads_disengage_lateral_on_brake = self.param_s.get_bool("DisengageLateralOnBrake")
    self.acc_mads_combo = self.param_s.get_bool("AccMadsCombo")
    self.below_speed_pause = self.param_s.get_bool("BelowSpeedPause")
    self.e2eLongStatus = self.param_s.get_bool("ExperimentalMode")
    self.resumeAvailable = False
    self.accEnabled = False
    self.madsEnabled = False
    self.leftBlinkerOn = False
    self.rightBlinkerOn = False
    self.disengageByBrake = False
    self.belowLaneChangeSpeed = True
    self.mainEnabled = False
    self.mads_enabled = None
    self.prev_mads_enabled = None
    self.prev_cruiseState_enabled = False
    self.prev_acc_mads_combo = None
    self.prev_brake_pressed = False

  def update(self, pt_cp, cam_cp, loopback_cp):
    ret = car.CarState.new_message()

    self.prev_cruise_buttons = self.cruise_buttons
    self.cruise_buttons = pt_cp.vl["ASCMSteeringButton"]["ACCButtons"]
    self.buttons_counter = pt_cp.vl["ASCMSteeringButton"]["RollingCounter"]
    self.pscm_status = copy.copy(pt_cp.vl["PSCMStatus"])
    self.moving_backward = pt_cp.vl["EBCMWheelSpdRear"]["MovingBackward"] != 0
    self.prev_mads_enabled = self.mads_enabled
    self.prev_brake_pressed = ret.brakePressed
    self.e2eLongStatus = self.param_s.get_bool("ExperimentalMode")

    # Variables used for avoiding LKAS faults
    self.loopback_lka_steering_cmd_updated = len(loopback_cp.vl_all["ASCMLKASteeringCmd"]["RollingCounter"]) > 0
    if self.CP.networkLocation == NetworkLocation.fwdCamera:
      self.camera_lka_steering_cmd_counter = cam_cp.vl["ASCMLKASteeringCmd"]["RollingCounter"]

    ret.wheelSpeeds = self.get_wheel_speeds(
      pt_cp.vl["EBCMWheelSpdFront"]["FLWheelSpd"],
      pt_cp.vl["EBCMWheelSpdFront"]["FRWheelSpd"],
      pt_cp.vl["EBCMWheelSpdRear"]["RLWheelSpd"],
      pt_cp.vl["EBCMWheelSpdRear"]["RRWheelSpd"],
    )
    ret.vEgoRaw = mean([ret.wheelSpeeds.fl, ret.wheelSpeeds.fr, ret.wheelSpeeds.rl, ret.wheelSpeeds.rr])
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    # sample rear wheel speeds, standstill=True if ECM allows engagement with brake
    ret.standstill = ret.wheelSpeeds.rl <= STANDSTILL_THRESHOLD and ret.wheelSpeeds.rr <= STANDSTILL_THRESHOLD

    self.belowLaneChangeSpeed = ret.vEgo < LANE_CHANGE_SPEED_MIN and self.below_speed_pause

    if pt_cp.vl["ECMPRDNL2"]["ManualMode"] == 1:
      ret.gearShifter = self.parse_gear_shifter("T")
    else:
      ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(pt_cp.vl["ECMPRDNL2"]["PRNDL2"], None))

    ret.brake = pt_cp.vl["ECMAcceleratorPos"]["BrakePedalPos"]
    if self.CP.networkLocation == NetworkLocation.fwdCamera:
      ret.brakePressed = pt_cp.vl["ECMEngineStatus"]["BrakePressed"] != 0
    else:
      # Some Volt 2016-17 have loose brake pedal push rod retainers which causes the ECM to believe
      # that the brake is being intermittently pressed without user interaction.
      # To avoid a cruise fault we need to use a conservative brake position threshold
      # https://static.nhtsa.gov/odi/tsbs/2017/MC-10137629-9999.pdf
      ret.brakePressed = ret.brake >= 8

    # Regen braking is braking
    if self.CP.transmissionType == TransmissionType.direct:
      ret.regenBraking = pt_cp.vl["EBCMRegenPaddle"]["RegenPaddle"] != 0

    ret.gas = pt_cp.vl["AcceleratorPedal2"]["AcceleratorPedal2"] / 254.
    ret.gasPressed = ret.gas > 1e-5

    ret.steeringAngleDeg = pt_cp.vl["PSCMSteeringAngle"]["SteeringWheelAngle"]
    ret.steeringRateDeg = pt_cp.vl["PSCMSteeringAngle"]["SteeringWheelRate"]
    ret.steeringTorque = pt_cp.vl["PSCMStatus"]["LKADriverAppldTrq"]
    ret.steeringTorqueEps = pt_cp.vl["PSCMStatus"]["LKATorqueDelivered"]
    ret.steeringPressed = abs(ret.steeringTorque) > STEER_THRESHOLD

    # 0 inactive, 1 active, 2 temporarily limited, 3 failed
    self.lkas_status = pt_cp.vl["PSCMStatus"]["LKATorqueDeliveredStatus"]

    # 1 - open, 0 - closed
    ret.doorOpen = (pt_cp.vl["BCMDoorBeltStatus"]["FrontLeftDoor"] == 1 or
                    pt_cp.vl["BCMDoorBeltStatus"]["FrontRightDoor"] == 1 or
                    pt_cp.vl["BCMDoorBeltStatus"]["RearLeftDoor"] == 1 or
                    pt_cp.vl["BCMDoorBeltStatus"]["RearRightDoor"] == 1)

    # 1 - latched
    ret.seatbeltUnlatched = pt_cp.vl["BCMDoorBeltStatus"]["LeftSeatBelt"] == 0
    ret.leftBlinker = pt_cp.vl["BCMTurnSignals"]["TurnSignals"] == 1
    ret.rightBlinker = pt_cp.vl["BCMTurnSignals"]["TurnSignals"] == 2

    self.leftBlinkerOn = pt_cp.vl["BCMTurnSignals"]["TurnSignals"] == 1
    self.rightBlinkerOn = pt_cp.vl["BCMTurnSignals"]["TurnSignals"] == 2

    ret.parkingBrake = pt_cp.vl["VehicleIgnitionAlt"]["ParkBrake"] == 1
    ret.cruiseState.available = pt_cp.vl["ECMEngineStatus"]["CruiseMainOn"] != 0
    ret.espDisabled = pt_cp.vl["ESPStatus"]["TractionControlOn"] != 1
    ret.accFaulted = pt_cp.vl["AcceleratorPedal2"]["CruiseState"] == AccState.FAULTED
    ret.brakeLights = bool(ret.brakePressed or ret.parkingBrake)

    ret.cruiseState.enabled = pt_cp.vl["AcceleratorPedal2"]["CruiseState"] != AccState.OFF
    ret.cruiseState.standstill = pt_cp.vl["AcceleratorPedal2"]["CruiseState"] == AccState.STANDSTILL
    if self.CP.networkLocation == NetworkLocation.fwdCamera:
      ret.cruiseState.speed = cam_cp.vl["ASCMActiveCruiseControlStatus"]["ACCSpeedSetpoint"] * CV.KPH_TO_MS
      ret.stockAeb = cam_cp.vl["AEBCmd"]["AEBCmdActive"] != 0
      # openpilot controls nonAdaptive when not pcmCruise
      if self.CP.pcmCruise:
        ret.cruiseState.nonAdaptive = cam_cp.vl["ASCMActiveCruiseControlStatus"]["ACCCruiseState"] not in (2, 3)

    self.mads_enabled = ret.cruiseState.available

    if self.prev_mads_enabled is None:
      self.prev_mads_enabled = self.mads_enabled

    if ret.cruiseState.available:
      if not self.CP.pcmCruise:
        if self.prev_cruise_buttons == 3: # SET-
          if self.cruise_buttons != 3:
            self.accEnabled = True
        elif self.prev_cruise_buttons == 2 and self.resumeAvailable: # RESUME+
          if self.cruise_buttons != 2:
            self.accEnabled = True
      if self.enable_mads:
        if not self.prev_mads_enabled and self.mads_enabled:
          self.madsEnabled = True
        if self.acc_mads_combo:
          if not self.prev_acc_mads_combo and ret.cruiseState.enabled:
            self.madsEnabled = True
          self.prev_acc_mads_combo = ret.cruiseState.enabled
    else:
      self.madsEnabled = False
      self.accEnabled = False
      self.resumeAvailable = False

    ret.endToEndLong = self.e2eLongStatus

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.enable_mads:
      if self.prev_cruise_buttons != 6: # CANCEL
        if self.cruise_buttons == 6:
          self.accEnabled = False
          if not self.enable_mads:
            self.madsEnabled = False
      if ret.brakePressed and (not self.prev_brake_pressed or not ret.standstill):
        self.accEnabled = False
        if not self.enable_mads:
          self.madsEnabled = False

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.accEnabled = False
      self.accEnabled = ret.cruiseState.enabled or self.accEnabled

    if not self.CP.pcmCruise:
      ret.cruiseState.enabled = self.accEnabled
      if ret.cruiseState.enabled:
        self.resumeAvailable = True

    if not self.enable_mads:
      if ret.cruiseState.enabled and not self.prev_cruiseState_enabled:
        self.madsEnabled = True
      elif not ret.cruiseState.enabled:
        self.madsEnabled = False
    self.prev_cruiseState_enabled = ret.cruiseState.enabled

    ret.steerFaultTemporary = False
    ret.steerFaultPermanent = False

    if self.madsEnabled:
      if (not self.belowLaneChangeSpeed and (self.leftBlinkerOn or self.rightBlinkerOn)) or\
        not (self.leftBlinkerOn or self.rightBlinkerOn):
        ret.steerFaultTemporary = self.lkas_status == 2
        ret.steerFaultPermanent = self.lkas_status == 3

    return ret

  @staticmethod
  def get_cam_can_parser(CP):
    signals = []
    checks = []
    if CP.networkLocation == NetworkLocation.fwdCamera:
      signals += [
        ("AEBCmdActive", "AEBCmd"),
        ("RollingCounter", "ASCMLKASteeringCmd"),
        ("ACCSpeedSetpoint", "ASCMActiveCruiseControlStatus"),
        ("ACCCruiseState", "ASCMActiveCruiseControlStatus"),
      ]
      checks += [
        ("AEBCmd", 10),
        ("ASCMLKASteeringCmd", 10),
        ("ASCMActiveCruiseControlStatus", 25),
      ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, CanBus.CAMERA)

  @staticmethod
  def get_can_parser(CP):
    signals = [
      # sig_name, sig_address
      ("BrakePedalPos", "ECMAcceleratorPos"),
      ("FrontLeftDoor", "BCMDoorBeltStatus"),
      ("FrontRightDoor", "BCMDoorBeltStatus"),
      ("RearLeftDoor", "BCMDoorBeltStatus"),
      ("RearRightDoor", "BCMDoorBeltStatus"),
      ("LeftSeatBelt", "BCMDoorBeltStatus"),
      ("RightSeatBelt", "BCMDoorBeltStatus"),
      ("TurnSignals", "BCMTurnSignals"),
      ("AcceleratorPedal2", "AcceleratorPedal2"),
      ("CruiseState", "AcceleratorPedal2"),
      ("ACCButtons", "ASCMSteeringButton"),
      ("RollingCounter", "ASCMSteeringButton"),
      ("SteeringWheelAngle", "PSCMSteeringAngle"),
      ("SteeringWheelRate", "PSCMSteeringAngle"),
      ("FLWheelSpd", "EBCMWheelSpdFront"),
      ("FRWheelSpd", "EBCMWheelSpdFront"),
      ("RLWheelSpd", "EBCMWheelSpdRear"),
      ("RRWheelSpd", "EBCMWheelSpdRear"),
      ("MovingBackward", "EBCMWheelSpdRear"),
      ("PRNDL2", "ECMPRDNL2"),
      ("ManualMode", "ECMPRDNL2"),
      ("LKADriverAppldTrq", "PSCMStatus"),
      ("LKATorqueDelivered", "PSCMStatus"),
      ("LKATorqueDeliveredStatus", "PSCMStatus"),
      ("HandsOffSWlDetectionStatus", "PSCMStatus"),
      ("HandsOffSWDetectionMode", "PSCMStatus"),
      ("LKATotalTorqueDelivered", "PSCMStatus"),
      ("PSCMStatusChecksum", "PSCMStatus"),
      ("RollingCounter", "PSCMStatus"),
      ("TractionControlOn", "ESPStatus"),
      ("ParkBrake", "VehicleIgnitionAlt"),
      ("CruiseMainOn", "ECMEngineStatus"),
      ("BrakePressed", "ECMEngineStatus"),
    ]

    checks = [
      ("BCMTurnSignals", 1),
      ("ECMPRDNL2", 10),
      ("PSCMStatus", 10),
      ("ESPStatus", 10),
      ("BCMDoorBeltStatus", 10),
      ("VehicleIgnitionAlt", 10),
      ("EBCMWheelSpdFront", 20),
      ("EBCMWheelSpdRear", 20),
      ("AcceleratorPedal2", 33),
      ("ASCMSteeringButton", 33),
      ("ECMEngineStatus", 100),
      ("PSCMSteeringAngle", 100),
      ("ECMAcceleratorPos", 80),
    ]

    if CP.transmissionType == TransmissionType.direct:
      signals.append(("RegenPaddle", "EBCMRegenPaddle"))
      checks.append(("EBCMRegenPaddle", 50))

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, CanBus.POWERTRAIN)

  @staticmethod
  def get_loopback_can_parser(CP):
    signals = [
      ("RollingCounter", "ASCMLKASteeringCmd"),
    ]

    checks = [
      ("ASCMLKASteeringCmd", 0),
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], signals, checks, CanBus.LOOPBACK, enforce_checks=False)
