#!/usr/bin/env python3
from cereal import car
from panda import Panda
from common.conversions import Conversions as CV
from common.params import Params
from selfdrive.car.hyundai.values import HyundaiFlags, CAR, DBC, CANFD_CAR, CAMERA_SCC_CAR, CANFD_RADAR_SCC_CAR, EV_CAR, HYBRID_CAR, LEGACY_SAFETY_MODE_CAR, NON_SCC_CAR, Buttons
from selfdrive.car.hyundai.radar_interface import RADAR_START_ADDR
from selfdrive.car import STD_CARGO_KG, create_button_event, scale_tire_stiffness, get_safety_config
from selfdrive.car.interfaces import CarInterfaceBase
from selfdrive.car.disable_ecu import disable_ecu

Ecu = car.CarParams.Ecu
ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName
ENABLE_BUTTONS = (Buttons.RES_ACCEL, Buttons.SET_DECEL, Buttons.CANCEL)
BUTTONS_DICT = {Buttons.RES_ACCEL: ButtonType.accelCruise, Buttons.SET_DECEL: ButtonType.decelCruise,
                Buttons.GAP_DIST: ButtonType.gapAdjustCruise, Buttons.CANCEL: ButtonType.cancel}


class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long):
    ret.carName = "hyundai"
    ret.radarOffCan = RADAR_START_ADDR not in fingerprint[1] or DBC[ret.carFingerprint]["radar"] is None

    # These cars have been put into dashcam only due to both a lack of users and test coverage.
    # These cars likely still work fine. Once a user confirms each car works and a test route is
    # added to selfdrive/car/tests/routes.py, we can remove it from this list.
    ret.dashcamOnly = candidate in {CAR.KIA_OPTIMA_H, }

    if candidate in CANFD_CAR:
      # detect HDA2 with ADAS Driving ECU
      if Ecu.adas in [fw.ecu for fw in car_fw]:
        ret.flags |= HyundaiFlags.CANFD_HDA2.value
      else:
        # non-HDA2
        if 0x1cf not in fingerprint[4]:
          ret.flags |= HyundaiFlags.CANFD_ALT_BUTTONS.value
        # ICE cars do not have 0x130; GEARS message on 0x40 instead
        if 0x130 not in fingerprint[4]:
          ret.flags |= HyundaiFlags.CANFD_ALT_GEARS.value
        if candidate not in CANFD_RADAR_SCC_CAR:
          ret.flags |= HyundaiFlags.CANFD_CAMERA_SCC.value

    ret.steerActuatorDelay = 0.1  # Default delay
    ret.steerLimitTimer = 0.4
    tire_stiffness_factor = 1.
    CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    if candidate in (CAR.SANTA_FE, CAR.SANTA_FE_2022, CAR.SANTA_FE_HEV_2022, CAR.SANTA_FE_PHEV_2022):
      ret.mass = 3982. * CV.LB_TO_KG + STD_CARGO_KG
      ret.wheelbase = 2.766
      # Values from optimizer
      ret.steerRatio = 16.55  # 13.8 is spec end-to-end
      tire_stiffness_factor = 0.82
    elif candidate in (CAR.SONATA, CAR.SONATA_HYBRID):
      ret.mass = 1513. + STD_CARGO_KG
      ret.wheelbase = 2.84
      ret.steerRatio = 13.27 * 1.15   # 15% higher at the center seems reasonable
      tire_stiffness_factor = 0.65
    elif candidate == CAR.SONATA_LF:
      ret.mass = 4497. * CV.LB_TO_KG
      ret.wheelbase = 2.804
      ret.steerRatio = 13.27 * 1.15   # 15% higher at the center seems reasonable
    elif candidate == CAR.PALISADE:
      ret.mass = 1999. + STD_CARGO_KG
      ret.wheelbase = 2.90
      ret.steerRatio = 15.6 * 1.15
      tire_stiffness_factor = 0.63
    elif candidate == CAR.ELANTRA:
      ret.mass = 1275. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 15.4            # 14 is Stock | Settled Params Learner values are steerRatio: 15.401566348670535
      tire_stiffness_factor = 0.385    # stiffnessFactor settled on 1.0081302973865127
      ret.minSteerSpeed = 32 * CV.MPH_TO_MS
    elif candidate in (CAR.ELANTRA_2021, CAR.ELANTRA_2022_NON_SCC):
      ret.mass = (2800. * CV.LB_TO_KG) + STD_CARGO_KG
      ret.wheelbase = 2.72
      ret.steerRatio = 12.9
      tire_stiffness_factor = 0.65
    elif candidate == CAR.ELANTRA_HEV_2021:
      ret.mass = (3017. * CV.LB_TO_KG) + STD_CARGO_KG
      ret.wheelbase = 2.72
      ret.steerRatio = 12.9
      tire_stiffness_factor = 0.65
    elif candidate == CAR.HYUNDAI_GENESIS:
      ret.mass = 2060. + STD_CARGO_KG
      ret.wheelbase = 3.01
      ret.steerRatio = 16.5
      ret.minSteerSpeed = 60 * CV.KPH_TO_MS
    elif candidate in (CAR.KONA, CAR.KONA_EV, CAR.KONA_HEV, CAR.KONA_EV_2022):
      ret.mass = {CAR.KONA_EV: 1685., CAR.KONA_HEV: 1425., CAR.KONA_EV_2022: 1743.}.get(candidate, 1275.) + STD_CARGO_KG
      ret.wheelbase = 2.6
      ret.steerRatio = 13.42  # Spec
      tire_stiffness_factor = 0.385
    elif candidate in (CAR.IONIQ, CAR.IONIQ_EV_LTD, CAR.IONIQ_EV_2020, CAR.IONIQ_PHEV, CAR.IONIQ_HEV_2022):
      ret.mass = 1490. + STD_CARGO_KG  # weight per hyundai site https://www.hyundaiusa.com/ioniq-electric/specifications.aspx
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73  # Spec
      tire_stiffness_factor = 0.385
      if candidate not in (CAR.IONIQ_EV_2020, CAR.IONIQ_PHEV, CAR.IONIQ_HEV_2022):
        ret.minSteerSpeed = 32 * CV.MPH_TO_MS
    elif candidate == CAR.IONIQ_PHEV_2019:
      ret.mass = 1550. + STD_CARGO_KG  # weight per hyundai site https://www.hyundaiusa.com/us/en/vehicles/2019-ioniq-plug-in-hybrid/compare-specs
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73
      ret.minSteerSpeed = 32 * CV.MPH_TO_MS
    elif candidate == CAR.VELOSTER:
      ret.mass = 3558. * CV.LB_TO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 13.75 * 1.15
      tire_stiffness_factor = 0.5
    elif candidate == CAR.TUCSON:
      ret.mass = 3520. * CV.LB_TO_KG
      ret.wheelbase = 2.67
      ret.steerRatio = 14.00 * 1.15
      tire_stiffness_factor = 0.385
    elif candidate == CAR.TUCSON_HYBRID_4TH_GEN:
      ret.mass = 1680. + STD_CARGO_KG  # average of all 3 trims
      ret.wheelbase = 2.756
      ret.steerRatio = 16.
      tire_stiffness_factor = 0.385
    elif candidate == CAR.SANTA_CRUZ_1ST_GEN:
      ret.mass = 1870. + STD_CARGO_KG  # weight from Limited trim - the only supported trim
      ret.wheelbase = 3.000
      ret.steerRatio = 14.2  # steering ratio according to Hyundai News https://www.hyundainews.com/assets/documents/original/48035-2022SantaCruzProductGuideSpecsv2081521.pdf

    # Kia
    elif candidate == CAR.KIA_SORENTO:
      ret.mass = 1985. + STD_CARGO_KG
      ret.wheelbase = 2.78
      ret.steerRatio = 14.4 * 1.1   # 10% higher at the center seems reasonable
    elif candidate in (CAR.KIA_NIRO_EV, CAR.KIA_NIRO_PHEV, CAR.KIA_NIRO_HEV_2021):
      ret.mass = 1737. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 13.9 if CAR.KIA_NIRO_HEV_2021 else 13.73  # Spec
      tire_stiffness_factor = 0.385
      if candidate == CAR.KIA_NIRO_PHEV:
        ret.minSteerSpeed = 32 * CV.MPH_TO_MS
    elif candidate == CAR.KIA_SELTOS:
      ret.mass = 1337. + STD_CARGO_KG
      ret.wheelbase = 2.63
      ret.steerRatio = 14.56
      tire_stiffness_factor = 1
    elif candidate == CAR.KIA_SPORTAGE_5TH_GEN:
      ret.mass = 1700. + STD_CARGO_KG  # weight from SX and above trims, average of FWD and AWD versions
      ret.wheelbase = 2.756
      ret.steerRatio = 13.6  # steering ratio according to Kia News https://www.kiamedia.com/us/en/models/sportage/2023/specifications
    elif candidate in (CAR.KIA_OPTIMA_G4, CAR.KIA_OPTIMA_G4_FL, CAR.KIA_OPTIMA_H):
      ret.mass = 3558. * CV.LB_TO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 13.75
      tire_stiffness_factor = 0.5
      if candidate == CAR.KIA_OPTIMA_G4:
        ret.minSteerSpeed = 32 * CV.MPH_TO_MS
    elif candidate in (CAR.KIA_STINGER, CAR.KIA_STINGER_2022):
      ret.mass = 1825. + STD_CARGO_KG
      ret.wheelbase = 2.78
      ret.steerRatio = 14.4 * 1.15   # 15% higher at the center seems reasonable
    elif candidate in (CAR.KIA_FORTE, CAR. KIA_FORTE_2019_NON_SCC, CAR.KIA_FORTE_2021_NON_SCC):
      ret.mass = 3558. * CV.LB_TO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 13.75
      tire_stiffness_factor = 0.5
    elif candidate == CAR.KIA_CEED:
      ret.mass = 1450. + STD_CARGO_KG
      ret.wheelbase = 2.65
      ret.steerRatio = 13.75
      tire_stiffness_factor = 0.5
    elif candidate == CAR.KIA_K5_2021:
      ret.mass = 3228. * CV.LB_TO_KG
      ret.wheelbase = 2.85
      ret.steerRatio = 13.27  # 2021 Kia K5 Steering Ratio (all trims)
      tire_stiffness_factor = 0.5
    elif candidate == CAR.KIA_EV6:
      ret.mass = 2055 + STD_CARGO_KG
      ret.wheelbase = 2.9
      ret.steerRatio = 16.
      tire_stiffness_factor = 0.65
    elif candidate == CAR.IONIQ_5:
      ret.mass = 2012 + STD_CARGO_KG
      ret.wheelbase = 3.0
      ret.steerRatio = 16.
      tire_stiffness_factor = 0.65
    elif candidate == CAR.KIA_SPORTAGE_HYBRID_5TH_GEN:
      ret.mass = 1767. + STD_CARGO_KG  # SX Prestige trim support only
      ret.wheelbase = 2.756
      ret.steerRatio = 13.6
    elif candidate == CAR.KIA_SORENTO_PHEV_4TH_GEN:
      ret.mass = 4095.8 * CV.LB_TO_KG + STD_CARGO_KG # weight from EX and above trims, average of FWD and AWD versions (EX, X-Line EX AWD, SX, SX Pestige, X-Line SX Prestige AWD)
      ret.wheelbase = 2.81
      ret.steerRatio = 13.27 # steering ratio according to Kia News https://www.kiamedia.com/us/en/models/sorento-phev/2022/specifications

    # Genesis
    elif candidate == CAR.GENESIS_G70:
      ret.steerActuatorDelay = 0.1
      ret.mass = 1640.0 + STD_CARGO_KG
      ret.wheelbase = 2.84
      ret.steerRatio = 13.56
    elif candidate in (CAR.GENESIS_G70_2020, CAR.GENESIS_G70_2021_NON_SCC):
      ret.mass = 3673.0 * CV.LB_TO_KG + STD_CARGO_KG
      ret.wheelbase = 2.83
      ret.steerRatio = 12.9
    elif candidate == CAR.GENESIS_GV70_1ST_GEN:
      ret.mass = 1950. + STD_CARGO_KG
      ret.wheelbase = 2.87
      ret.steerRatio = 14.6
    elif candidate == CAR.GENESIS_G80:
      ret.mass = 2060. + STD_CARGO_KG
      ret.wheelbase = 3.01
      ret.steerRatio = 16.5
    elif candidate == CAR.GENESIS_G90:
      ret.mass = 2200
      ret.wheelbase = 3.15
      ret.steerRatio = 12.069

    if Params().get_bool("EnforceTorqueLateral"):
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    # *** longitudinal control ***
    if candidate in CANFD_CAR:
      ret.longitudinalTuning.kpV = [0.1]
      ret.longitudinalTuning.kiV = [0.0]
      ret.experimentalLongitudinalAvailable = candidate in (HYBRID_CAR | EV_CAR) and candidate not in CANFD_RADAR_SCC_CAR
    else:
      ret.longitudinalTuning.kpV = [0.5]
      ret.longitudinalTuning.kiV = [0.0]
      ret.experimentalLongitudinalAvailable = candidate not in (LEGACY_SAFETY_MODE_CAR | CAMERA_SCC_CAR)
    ret.openpilotLongitudinalControl = experimental_long and ret.experimentalLongitudinalAvailable
    ret.pcmCruise = not ret.openpilotLongitudinalControl
    ret.customStockLongAvailable = True
    ret.pcmCruiseSpeed = False if (Params().get_bool("SpeedLimitControl") or Params().get_bool("TurnVisionControl") or
                                   Params().get_bool("TurnSpeedControl")) and not ret.openpilotLongitudinalControl and \
                                  Params().get_bool("CustomStockLong") and ret.customStockLongAvailable else True

    ret.stoppingControl = True
    ret.startingState = True
    ret.vEgoStarting = 0.1
    ret.startAccel = 1.0
    ret.longitudinalActuatorDelayLowerBound = 0.5
    ret.longitudinalActuatorDelayUpperBound = 0.5

    # *** feature detection ***
    if candidate in CANFD_CAR:
      bus = 5 if ret.flags & HyundaiFlags.CANFD_HDA2 else 4
      ret.enableBsm = 0x1e5 in fingerprint[bus]
    else:
      ret.enableBsm = 0x58b in fingerprint[0]

    # *** panda safety config ***
    if candidate in CANFD_CAR:
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.noOutput),
                           get_safety_config(car.CarParams.SafetyModel.hyundaiCanfd)]

      if ret.flags & HyundaiFlags.CANFD_HDA2:
        ret.safetyConfigs[1].safetyParam |= Panda.FLAG_HYUNDAI_CANFD_HDA2
      if ret.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
        ret.safetyConfigs[1].safetyParam |= Panda.FLAG_HYUNDAI_CANFD_ALT_BUTTONS
      if ret.flags & HyundaiFlags.CANFD_CAMERA_SCC:
        ret.safetyConfigs[1].safetyParam |= Panda.FLAG_HYUNDAI_CAMERA_SCC
    else:
      if candidate in LEGACY_SAFETY_MODE_CAR:
        # these cars require a special panda safety mode due to missing counters and checksums in the messages
        ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.hyundaiLegacy)]
      else:
        ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.hyundai, 0)]

      if candidate in CAMERA_SCC_CAR:
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_HYUNDAI_CAMERA_SCC

      if 0x391 in fingerprint[0]:
        ret.flags |= HyundaiFlags.SP_CAN_LFA_BTN.value
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_HYUNDAI_LFA_BTN

      enhanced_scc = 0x2AB in fingerprint[0] and ret.openpilotLongitudinalControl and Params().get_bool("EnhancedScc")
      if enhanced_scc:
        ret.flags |= HyundaiFlags.SP_ENHANCED_SCC.value
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_HYUNDAI_ESCC

      if candidate in NON_SCC_CAR:
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_HYUNDAI_NON_SCC

      if 0x544 in fingerprint[0]:
        ret.flags |= HyundaiFlags.SP_CAN_NAV_MSG.value

    if ret.openpilotLongitudinalControl:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_LONG
    if candidate in HYBRID_CAR:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_HYBRID_GAS
    elif candidate in EV_CAR:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_EV_GAS

    if candidate in (CAR.KONA, CAR.KONA_EV, CAR.KONA_HEV, CAR.KONA_EV_2022):
      ret.flags |= HyundaiFlags.ALT_LIMITS.value
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_ALT_LIMITS

    ret.centerToFront = ret.wheelbase * 0.4

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)
    return ret

  @staticmethod
  def init(CP, logcan, sendcan):
    if CP.openpilotLongitudinalControl and not ((CP.flags & HyundaiFlags.CANFD_CAMERA_SCC.value) or (CP.flags & HyundaiFlags.SP_ENHANCED_SCC)):
      addr, bus = 0x7d0, 0
      if CP.flags & HyundaiFlags.CANFD_HDA2.value:
        addr, bus = 0x730, 5
      disable_ecu(logcan, sendcan, bus=bus, addr=addr, com_cont_req=b'\x28\x83\x01')

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)

    ret.madsEnabled = self.CS.madsEnabled
    ret.accEnabled = self.CS.accEnabled
    ret.leftBlinkerOn = self.CS.leftBlinkerOn
    ret.rightBlinkerOn = self.CS.rightBlinkerOn
    ret.belowLaneChangeSpeed = self.CS.belowLaneChangeSpeed

    buttonEvents = []

    #if ret.cruiseState.enabled and not self.CS.out.cruiseState.enabled:
    #  be = car.CarState.ButtonEvent.new_message()
    #  be.pressed = False
    #  be.type = ButtonType.setCruise
    #  buttonEvents.append(be)

    if self.CS.cruise_buttons[-1] != self.CS.prev_cruise_buttons:
      be = car.CarState.ButtonEvent.new_message()
      be.type = ButtonType.unknown
      if self.CS.cruise_buttons[-1] != 0:
        be.pressed = True
        but = self.CS.cruise_buttons[-1]
      else:
        be.pressed = False
        but = self.CS.prev_cruise_buttons
      if but == Buttons.RES_ACCEL:
        be.type = ButtonType.accelCruise
      elif but == Buttons.SET_DECEL:
        be.type = ButtonType.decelCruise
      elif but == Buttons.GAP_DIST:
        be.type = ButtonType.gapAdjustCruise
      elif but == Buttons.CANCEL:
        be.type = ButtonType.cancel
      buttonEvents.append(be)

    # MADS BUTTON
    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.altButton1
      buttonEvents.append(be)

    if self.CS.main_buttons[-1] != self.CS.prev_main_buttons:
      be = car.CarState.ButtonEvent.new_message()
      be.type = ButtonType.unknown
      if self.CS.main_buttons[-1] != 0:
        be.pressed = True
        but = self.CS.main_buttons[-1]
      else:
        be.pressed = False
        but = self.CS.prev_main_buttons
      if but == 1:
        be.type = ButtonType.setCruise
      buttonEvents.append(be)

    ret.buttonEvents = buttonEvents

    extraGears = []
    if not self.CS.CP.openpilotLongitudinalControl:
      extraGears = [car.CarState.GearShifter.sport, car.CarState.GearShifter.low, car.CarState.GearShifter.manumatic]

    # On some newer model years, the CANCEL button acts as a pause/resume button based on the PCM state
    # To avoid re-engaging when openpilot cancels, check user engagement intention via buttons
    # Main button also can trigger an engagement on these cars
    allow_enable = any(btn in ENABLE_BUTTONS for btn in self.CS.cruise_buttons) or any(self.CS.main_buttons)
    events = self.create_common_events(ret, extra_gears=extraGears, pcm_enable=False, allow_enable=allow_enable)

    if self.CS.brake_error:
      events.add(EventName.brakeUnavailable)

    # low speed steer alert hysteresis logic (only for cars with steer cut off above 10 m/s)
    if ret.vEgo < (self.CP.minSteerSpeed + 2.) and self.CP.minSteerSpeed > 10.:
      self.low_speed_alert = True
    if ret.vEgo > (self.CP.minSteerSpeed + 4.):
      self.low_speed_alert = False
    if self.low_speed_alert and self.CS.madsEnabled:
      events.add(car.CarEvent.EventName.belowSteerSpeed)

    self.CS.disengageByBrake = self.CS.disengageByBrake or ret.disengageByBrake

    enable_pressed = False
    enable_from_brake = False

    if self.CS.disengageByBrake and not ret.brakePressed and not ret.brakeHoldActive and not ret.parkingBrake and self.CS.madsEnabled:
      enable_pressed = True
      enable_from_brake = True

    if not ret.brakePressed and not ret.brakeHoldActive and not ret.parkingBrake:
      self.CS.disengageByBrake = False
      ret.disengageByBrake = False

    for b in ret.buttonEvents:
      # do enable on both accel and decel buttons
      if (b.type in (ButtonType.accelCruise, ButtonType.decelCruise) and not b.pressed and self.CP.pcmCruiseSpeed) or \
        (self.CS.pcm_enabled and not self.CS.prev_pcm_enabled and allow_enable and not self.CP.pcmCruiseSpeed):
         enable_pressed = True
      if b.type == ButtonType.accelCruise and not self.CS.resumeAvailable and (not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed):
        enable_pressed = False
      # do disable on MADS button if ACC is disabled
      if b.type == ButtonType.altButton1 and b.pressed:
        if not self.CS.madsEnabled: # disabled MADS
          if not ret.cruiseState.enabled:
            events.add(EventName.buttonCancel)
          else:
            events.add(EventName.manualSteeringRequired)
        else: # enabled MADS
          if not ret.cruiseState.enabled:
            enable_pressed = True
      # do disable on button down
      if (b.type == ButtonType.cancel and b.pressed and not self.CP.pcmCruise) or \
        (b.type in (ButtonType.cancel, ButtonType.setCruise) and not (self.CS.pcm_enabled and not self.CS.prev_pcm_enabled) and not self.CS.pcm_enabled and self.CP.pcmCruise):
        if not self.CS.madsEnabled:
          events.add(EventName.buttonCancel)
        elif ret.cruiseState.enabled:
          events.add(EventName.manualLongitudinalRequired)
    if ((ret.cruiseState.enabled and self.CP.pcmCruiseSpeed) or (self.CS.pcm_enabled and not self.CP.pcmCruiseSpeed) or self.CS.madsEnabled) and enable_pressed:
      if enable_from_brake:
        events.add(EventName.silentButtonEnable)
      else:
        events.add(EventName.buttonEnable)

    ret.customStockLong = self.CS.update_custom_stock_long(self.CC.cruise_button, self.CC.final_speed_kph,
                                                           self.CC.v_cruise_kph_prev, self.CC.target_speed,
                                                           self.CC.v_set_dis, self.CC.speed_diff, self.CC.button_type)

    ret.events = events.to_msg()

    return ret

  def apply(self, c):
    return self.CC.update(c, self.CS)
