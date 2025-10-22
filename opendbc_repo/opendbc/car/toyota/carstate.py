import copy
from cereal import custom
from openpilot.common.params import Params
from opendbc.can import CANDefine, CANParser
from opendbc.car import Bus, DT_CTRL, create_button_events, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.common.filter_simple import FirstOrderFilter
from opendbc.car.interfaces import CarStateBase
from opendbc.car.toyota.values import ToyotaFlags, CAR, DBC, STEER_THRESHOLD, NO_STOP_TIMER_CAR, \
                                                  TSS2_CAR, RADAR_ACC_CAR, EPS_SCALE, UNSUPPORTED_DSU_CAR, SECOC_CAR
from opendbc.sunnypilot.car.toyota.carstate_ext import CarStateExt
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP

ButtonType = structs.CarState.ButtonEvent.Type
SteerControlType = structs.CarParams.SteerControlType
AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality
# These steering fault definitions seem to be common across LKA (torque) and LTA (angle):
# - high steer rate fault: goes to 21 or 25 for 1 frame, then 9 for 2 seconds
# - lka/lta msg drop out: goes to 9 then 11 for a combined total of 2 seconds, then 3.
#     if using the other control command, goes directly to 3 after 1.5 seconds
# - initializing: LTA can report 0 as long as STEER_TORQUE_SENSOR->STEER_ANGLE_INITIALIZING is 1,
#     and is a catch-all for LKA
TEMP_STEER_FAULTS = (0, 9, 11, 21, 25)
# - lka/lta msg drop out: 3 (recoverable)
# - prolonged high driver torque: 17 (permanent)
PERM_STEER_FAULTS = (3, 17)


class CarState(CarStateBase, CarStateExt):
  def __init__(self, CP, CP_SP):
    CarStateBase.__init__(self, CP, CP_SP)
    CarStateExt.__init__(self, CP, CP_SP)
    can_define = CANDefine(DBC[CP.carFingerprint][Bus.pt])
    self.eps_torque_scale = EPS_SCALE[CP.carFingerprint] / 100.
    self.cluster_speed_hyst_gap = CV.KPH_TO_MS / 2.
    self.cluster_min_speed = CV.KPH_TO_MS / 2.

    if CP.flags & ToyotaFlags.SECOC.value:
      self.shifter_values = can_define.dv["GEAR_PACKET_HYBRID"]["GEAR"]
    else:
      self.shifter_values = can_define.dv["GEAR_PACKET"]["GEAR"]

    # On cars with cp.vl["STEER_TORQUE_SENSOR"]["STEER_ANGLE"]
    # the signal is zeroed to where the steering angle is at start.
    # Need to apply an offset as soon as the steering angle measurements are both received
    self.accurate_steer_angle_seen = False
    self.angle_offset = FirstOrderFilter(None, 60.0, DT_CTRL, initialized=False)

    self.lkas_button = 0
    self.distance_button = 0

    self.pcm_follow_distance = 0

    self.acc_type = 1
    self.lkas_hud = {}
    self.gvc = 0.0
    self.secoc_synchronization = None

    self._left_blindspot = False
    self._left_blindspot_d1 = 0
    self._left_blindspot_d2 = 0
    self._left_blindspot_counter = 0

    self._right_blindspot = False
    self._right_blindspot_d1 = 0
    self._right_blindspot_d2 = 0
    self._right_blindspot_counter = 0

    self.signals_checked = False
    self.sport_signal_seen = False
    self.eco_signal_seen = False
    self.accel_profile = None
    self.prev_accel_profile = None
    self.accel_profile_init = False
    self.toyota_drive_mode = Params().get_bool('ToyotaDriveMode')

    if CP_SP.flags & ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD:
      self.pre_collision_2 = {}

    self.frame = 0

  def update(self, can_parsers) -> tuple[structs.CarState, structs.CarStateSP]:
    cp = can_parsers[Bus.pt]
    cp_cam = can_parsers[Bus.cam]

    ret = structs.CarState()
    ret_sp = structs.CarStateSP()
    cp_acc = cp_cam if self.CP.carFingerprint in (TSS2_CAR - RADAR_ACC_CAR) else cp

    if not self.CP.flags & ToyotaFlags.SECOC.value:
      self.gvc = cp.vl["VSC1S07"]["GVC"]

    ret.doorOpen = any([cp.vl["BODY_CONTROL_STATE"]["DOOR_OPEN_FL"], cp.vl["BODY_CONTROL_STATE"]["DOOR_OPEN_FR"],
                        cp.vl["BODY_CONTROL_STATE"]["DOOR_OPEN_RL"], cp.vl["BODY_CONTROL_STATE"]["DOOR_OPEN_RR"]])
    ret.seatbeltUnlatched = cp.vl["BODY_CONTROL_STATE"]["SEATBELT_DRIVER_UNLATCHED"] != 0
    ret.parkingBrake = cp.vl["BODY_CONTROL_STATE"]["PARKING_BRAKE"] == 1

    ret.brakePressed = cp.vl["BRAKE_MODULE"]["BRAKE_PRESSED"] != 0
    #ret.brakeHoldActive = cp.vl["ESP_CONTROL"]["BRAKE_HOLD_ACTIVE"] == 1

    if self.CP.flags & ToyotaFlags.SECOC.value:
      self.secoc_synchronization = copy.copy(cp.vl["SECOC_SYNCHRONIZATION"])
      ret.gasPressed = cp.vl["GAS_PEDAL"]["GAS_PEDAL_USER"] > 0
      can_gear = int(cp.vl["GEAR_PACKET_HYBRID"]["GEAR"])
    else:
      ret.gasPressed = cp.vl["PCM_CRUISE"]["GAS_RELEASED"] == 0  # TODO: these also have GAS_PEDAL, come back and unify
      can_gear = int(cp.vl["GEAR_PACKET"]["GEAR"])
      if not self.CP.enableDsu and not self.CP.flags & ToyotaFlags.DISABLE_RADAR.value:
        ret.stockAeb = bool(cp_acc.vl["PRE_COLLISION"]["PRECOLLISION_ACTIVE"] and cp_acc.vl["PRE_COLLISION"]["FORCE"] < -1e-5)

    if self.toyota_drive_mode:
      # Determine sport signal based on car model
      sport_signal = 'SPORT_ON_2' if self.CP.carFingerprint in (CAR.TOYOTA_RAV4_TSS2, CAR.LEXUS_ES_TSS2, CAR.TOYOTA_HIGHLANDER_TSS2) else 'SPORT_ON'

      # Check signals once
      if not self.signals_checked:
        self.signals_checked = True

        # Try to detect sport mode signal, handle missing signal with a fallback
        try:
          sport_mode = cp.vl["GEAR_PACKET"][sport_signal]
          self.sport_signal_seen = True
        except KeyError:
          sport_mode = 0
          self.sport_signal_seen = False

        # Try to detect eco mode signal, handle missing signal with a fallback
        try:
          eco_mode = cp.vl["GEAR_PACKET"]['ECON_ON']
          self.eco_signal_seen = True
        except KeyError:
          eco_mode = 0
          self.eco_signal_seen = False
      else:
        # Always re-check the signals to account for mode changes
        sport_mode = cp.vl["GEAR_PACKET"][sport_signal] if self.sport_signal_seen else 0
        eco_mode = cp.vl["GEAR_PACKET"]['ECON_ON'] if self.eco_signal_seen else 0

      # Set acceleration profile based on detected modes, with sport mode having higher priority
      if sport_mode == 1:
        self.accel_profile = AccelPersonality.sport
      elif eco_mode == 1:
        self.accel_profile = AccelPersonality.eco
      else:
        self.accel_profile = AccelPersonality.normal

      #print(f"Accel profile set to: {self.accel_profile}")

      # If not initialized, sync profile with the current mode on the car
      if not self.accel_profile_init or self.accel_profile != self.prev_accel_profile:
        #Params().put_nonblocking('AccelPersonality', str(self.accel_profile))
        Params().put_nonblocking('AccelPersonality', int(self.accel_profile))
        self.accel_profile_init = True
        # Update the previous profile to prevent unnecessary re-syncing
        self.prev_accel_profile = self.accel_profile

    self.parse_wheel_speeds(ret,
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FR"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RR"],
    )
    ret.vEgoCluster = ret.vEgo * 1.015  # minimum of all the cars

    ret.standstill = abs(ret.vEgoRaw) < 1e-3

    ret.steeringAngleDeg = cp.vl["STEER_ANGLE_SENSOR"]["STEER_ANGLE"] + cp.vl["STEER_ANGLE_SENSOR"]["STEER_FRACTION"]
    ret.steeringRateDeg = cp.vl["STEER_ANGLE_SENSOR"]["STEER_RATE"]
    torque_sensor_angle_deg = cp.vl["STEER_TORQUE_SENSOR"]["STEER_ANGLE"]

    # On some cars, the angle measurement is non-zero while initializing
    if abs(torque_sensor_angle_deg) > 1e-3 and not bool(cp.vl["STEER_TORQUE_SENSOR"]["STEER_ANGLE_INITIALIZING"]):
      self.accurate_steer_angle_seen = True

    if self.accurate_steer_angle_seen:
      # Offset seems to be invalid for large steering angles and high angle rates
      if abs(ret.steeringAngleDeg) < 90 and abs(ret.steeringRateDeg) < 100 and cp.can_valid:
        self.angle_offset.update(torque_sensor_angle_deg - ret.steeringAngleDeg)

      if self.angle_offset.initialized:
        ret.steeringAngleOffsetDeg = self.angle_offset.x
        ret.steeringAngleDeg = torque_sensor_angle_deg - self.angle_offset.x

    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(can_gear, None))
    ret.leftBlinker = cp.vl["BLINKERS_STATE"]["TURN_SIGNALS"] == 1
    ret.rightBlinker = cp.vl["BLINKERS_STATE"]["TURN_SIGNALS"] == 2

    ret.steeringTorque = cp.vl["STEER_TORQUE_SENSOR"]["STEER_TORQUE_DRIVER"]
    ret.steeringTorqueEps = cp.vl["STEER_TORQUE_SENSOR"]["STEER_TORQUE_EPS"] * self.eps_torque_scale
    # we could use the override bit from dbc, but it's triggered at too high torque values
    ret.steeringPressed = abs(ret.steeringTorque) > STEER_THRESHOLD

    # Check EPS LKA/LTA fault status
    ret.steerFaultTemporary = cp.vl["EPS_STATUS"]["LKA_STATE"] in TEMP_STEER_FAULTS
    ret.steerFaultPermanent = cp.vl["EPS_STATUS"]["LKA_STATE"] in PERM_STEER_FAULTS

    if self.CP.steerControlType == SteerControlType.angle:
      ret.steerFaultTemporary = ret.steerFaultTemporary or cp.vl["EPS_STATUS"]["LTA_STATE"] in TEMP_STEER_FAULTS
      ret.steerFaultPermanent = ret.steerFaultPermanent or cp.vl["EPS_STATUS"]["LTA_STATE"] in PERM_STEER_FAULTS

      # Lane Tracing Assist control is unavailable (EPS_STATUS->LTA_STATE=0) until
      # the more accurate angle sensor signal is initialized
      ret.vehicleSensorsInvalid = not self.accurate_steer_angle_seen

    if self.CP.carFingerprint in UNSUPPORTED_DSU_CAR:
      # TODO: find the bit likely in DSU_CRUISE that describes an ACC fault. one may also exist in CLUTCH
      ret.cruiseState.available = cp.vl["DSU_CRUISE"]["MAIN_ON"] != 0
      ret.cruiseState.speed = cp.vl["DSU_CRUISE"]["SET_SPEED"] * CV.KPH_TO_MS
      cluster_set_speed = cp.vl["PCM_CRUISE_ALT"]["UI_SET_SPEED"]
    else:
      ret.accFaulted = cp.vl["PCM_CRUISE_2"]["ACC_FAULTED"] != 0
      ret.carFaultedNonCritical = cp.vl["PCM_CRUISE_SM"]["TEMP_ACC_FAULTED"] != 0
      ret.cruiseState.available = cp.vl["PCM_CRUISE_2"]["MAIN_ON"] != 0
      ret.cruiseState.speed = cp.vl["PCM_CRUISE_2"]["SET_SPEED"] * CV.KPH_TO_MS
      cluster_set_speed = cp.vl["PCM_CRUISE_SM"]["UI_SET_SPEED"]

    # UI_SET_SPEED is always non-zero when main is on, hide until first enable
    is_metric = cp.vl["BODY_CONTROL_STATE_2"]["UNITS"] in (1, 2)
    if ret.cruiseState.speed != 0:
      conversion_factor = CV.KPH_TO_MS if is_metric else CV.MPH_TO_MS
      ret.cruiseState.speedCluster = cluster_set_speed * conversion_factor

    if self.CP.carFingerprint in TSS2_CAR and not self.CP.flags & ToyotaFlags.DISABLE_RADAR.value:
      self.acc_type = cp_acc.vl["ACC_CONTROL"]["ACC_TYPE"]
      ret.stockFcw = bool(cp_acc.vl["PCS_HUD"]["FCW"])

    # some TSS2 cars have low speed lockout permanently set, so ignore on those cars
    # these cars are identified by an ACC_TYPE value of 2.
    # TODO: it is possible to avoid the lockout and gain stop and go if you
    # send your own ACC_CONTROL msg on startup with ACC_TYPE set to 1
    if (self.CP.carFingerprint not in TSS2_CAR and self.CP.carFingerprint not in UNSUPPORTED_DSU_CAR) or \
       (self.CP.carFingerprint in TSS2_CAR and self.acc_type == 1):
      if self.CP.openpilotLongitudinalControl:
        ret.accFaulted = ret.accFaulted or cp.vl["PCM_CRUISE_2"]["LOW_SPEED_LOCKOUT"] == 2

    self.pcm_acc_status = cp.vl["PCM_CRUISE"]["CRUISE_STATE"]
    if self.CP.carFingerprint not in (NO_STOP_TIMER_CAR - TSS2_CAR):
      # ignore standstill state in certain vehicles, since pcm allows to restart with just an acceleration request
      ret.cruiseState.standstill = self.pcm_acc_status == 7
    ret.cruiseState.enabled = bool(cp.vl["PCM_CRUISE"]["CRUISE_ACTIVE"])
    ret.cruiseState.nonAdaptive = self.pcm_acc_status in (1, 2, 3, 4, 5, 6)

    ret.genericToggle = bool(cp.vl["LIGHT_STALK"]["AUTO_HIGH_BEAM"])
    ret.espDisabled = cp.vl["ESP_CONTROL"]["TC_DISABLED"] != 0

    if self.CP.enableBsm:
      ret.leftBlindspot = (cp.vl["BSM"]["L_ADJACENT"] == 1) or (cp.vl["BSM"]["L_APPROACHING"] == 1)
      ret.rightBlindspot = (cp.vl["BSM"]["R_ADJACENT"] == 1) or (cp.vl["BSM"]["R_APPROACHING"] == 1)

    if self.CP.carFingerprint != CAR.TOYOTA_PRIUS_V:
      self.lkas_hud = copy.copy(cp_cam.vl["LKAS_HUD"])

    if self.CP.carFingerprint not in UNSUPPORTED_DSU_CAR:
      self.pcm_follow_distance = cp.vl["PCM_CRUISE_2"]["PCM_FOLLOW_DISTANCE"]

    buttonEvents = []
    prev_distance_button = self.distance_button
    if self.CP.carFingerprint in TSS2_CAR:
      # lkas button is wired to the camera
      prev_lkas_button = self.lkas_button
      self.lkas_button = cp_cam.vl["LKAS_HUD"]["LDA_ON_MESSAGE"]

      # Cycles between 1 and 2 when pressing the button, then rests back at 0 after ~3s
      if self.lkas_button != 0 and self.lkas_button != prev_lkas_button:
        buttonEvents.extend(create_button_events(1, 0, {1: ButtonType.lkas}) +
                            create_button_events(0, 1, {1: ButtonType.lkas}))

      if self.CP.carFingerprint not in RADAR_ACC_CAR:
        # distance button is wired to the ACC module (camera or radar)
        self.distance_button = cp_acc.vl["ACC_CONTROL"]["DISTANCE"]

        buttonEvents += create_button_events(self.distance_button, prev_distance_button, {1: ButtonType.gapAdjustCruise})
    elif self.CP_SP.flags & ToyotaFlagsSP.SMART_DSU and not self.CP_SP.flags & ToyotaFlagsSP.RADAR_CAN_FILTER:
      self.distance_button = cp.vl["SDSU"]["FD_BUTTON"]

      buttonEvents += create_button_events(self.distance_button, prev_distance_button, {1: ButtonType.gapAdjustCruise})

    ret.buttonEvents = buttonEvents

    if self.CP_SP.flags & ToyotaFlagsSP.SP_ENHANCED_BSM and self.frame > 199:
      ret.leftBlindspot, ret.rightBlindspot = self.sp_get_enhanced_bsm(cp)

    if self.CP_SP.flags & ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD:
      self.pre_collision_2 = copy.copy(cp_cam.vl["PRE_COLLISION_2"])

    self.frame += 1

    CarStateExt.update(self, ret, ret_sp, can_parsers)

    return ret, ret_sp

  # Enhanced BSM (@arne182, @rav4kumar)
  def sp_get_enhanced_bsm(self, cp):
    # Let's keep all the commented out code for easy debug purposes in the future.
    distance_1 = cp.vl["DEBUG"].get('BLINDSPOTD1')
    distance_2 = cp.vl["DEBUG"].get('BLINDSPOTD2')
    side = cp.vl["DEBUG"].get('BLINDSPOTSIDE')

    if all(val is not None for val in [distance_1, distance_2, side]):
      if side == 65:  # left blind spot
        if distance_1 != self._left_blindspot_d1 or distance_2 != self._left_blindspot_d2:
          self._left_blindspot_d1 = distance_1
          self._left_blindspot_d2 = distance_2
          self._left_blindspot_counter = 100
        self._left_blindspot = distance_1 > 10 or distance_2 > 10

      elif side == 66:  # right blind spot
        if distance_1 != self._right_blindspot_d1 or distance_2 != self._right_blindspot_d2:
          self._right_blindspot_d1 = distance_1
          self._right_blindspot_d2 = distance_2
          self._right_blindspot_counter = 100
        self._right_blindspot = distance_1 > 10 or distance_2 > 10

      # update counters
      self._left_blindspot_counter = max(0, self._left_blindspot_counter - 1)
      self._right_blindspot_counter = max(0, self._right_blindspot_counter - 1)

      # reset blind spot status if counter reaches 0
      if self._left_blindspot_counter == 0:
        self._left_blindspot = False
        self._left_blindspot_d1 = self._left_blindspot_d2 = 0

      if self._right_blindspot_counter == 0:
        self._right_blindspot = False
        self._right_blindspot_d1 = self._right_blindspot_d2 = 0

    return self._left_blindspot, self._right_blindspot

  @staticmethod
  def get_can_parsers(CP, CP_SP):
    pt_messages = [
      ("BLINKERS_STATE", float('nan')),
    ]

    cam_messages = [
      ("RSA1", 0),
      ("RSA2", 0),
    ]

    return {
      Bus.pt: CANParser(DBC[CP.carFingerprint][Bus.pt], pt_messages, 0),
      Bus.cam: CANParser(DBC[CP.carFingerprint][Bus.pt], [] + cam_messages, 2),
    }
