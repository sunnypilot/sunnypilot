from cereal import car
from panda import Panda
from common.conversions import Conversions as CV
from common.params import Params
from selfdrive.car import STD_CARGO_KG, get_safety_config
from selfdrive.car.interfaces import CarInterfaceBase
from selfdrive.car.volkswagen.values import CAR, PQ_CARS, CANBUS, NetworkLocation, TransmissionType, GearShifter, CarControllerParams, \
                                            BUTTON_STATES

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName


class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

    if CP.networkLocation == NetworkLocation.fwdCamera:
      self.ext_bus = CANBUS.pt
      self.cp_ext = self.cp
    else:
      self.ext_bus = CANBUS.cam
      self.cp_ext = self.cp_cam

    self.buttonStatesPrev = BUTTON_STATES.copy()

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long):
    ret.carName = "volkswagen"
    ret.radarOffCan = True

    use_off_car_defaults = len(fingerprint[0]) == 0  # Pick sensible carParams during offline doc generation/CI jobs

    if candidate in PQ_CARS:
      # Set global PQ35/PQ46/NMS parameters
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.volkswagenPq)]
      ret.enableBsm = 0x3BA in fingerprint[0]  # SWA_1

      if 0x440 in fingerprint[0] or use_off_car_defaults:  # Getriebe_1
        ret.transmissionType = TransmissionType.automatic
      else:
        ret.transmissionType = TransmissionType.manual

      if any(msg in fingerprint[1] for msg in (0x1A0, 0xC2)):  # Bremse_1, Lenkwinkel_1
        ret.networkLocation = NetworkLocation.gateway
      else:
        ret.networkLocation = NetworkLocation.fwdCamera

      # The PQ port is in dashcam-only mode due to a fixed six-minute maximum timer on HCA steering. An unsupported
      # EPS flash update to work around this timer, and enable steering down to zero, is available from:
      #   https://github.com/pd0wm/pq-flasher
      # It is documented in a four-part blog series:
      #   https://blog.willemmelching.nl/carhacking/2022/01/02/vw-part1/
      # Panda ALLOW_DEBUG firmware required.
      ret.dashcamOnly = True

    else:
      # Set global MQB parameters
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.volkswagen)]
      ret.enableBsm = 0x30F in fingerprint[0]  # SWA_01

      if 0xAD in fingerprint[0] or use_off_car_defaults:  # Getriebe_11
        ret.transmissionType = TransmissionType.automatic
      elif 0x187 in fingerprint[0]:  # EV_Gearshift
        ret.transmissionType = TransmissionType.direct
      else:
        ret.transmissionType = TransmissionType.manual

      if any(msg in fingerprint[1] for msg in (0x40, 0x86, 0xB2, 0xFD)):  # Airbag_01, LWI_01, ESP_19, ESP_21
        ret.networkLocation = NetworkLocation.gateway
      else:
        ret.networkLocation = NetworkLocation.fwdCamera

    # Global lateral tuning defaults, can be overridden per-vehicle

    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 0.4
    ret.steerRatio = 15.6  # Let the params learner figure this out
    ret.lateralTuning.pid.kpBP = [0.]
    ret.lateralTuning.pid.kiBP = [0.]
    ret.lateralTuning.pid.kf = 0.00006
    ret.lateralTuning.pid.kpV = [0.6]
    ret.lateralTuning.pid.kiV = [0.2]

    # Global longitudinal tuning defaults, can be overridden per-vehicle

    ret.experimentalLongitudinalAvailable = ret.networkLocation == NetworkLocation.gateway or use_off_car_defaults
    if experimental_long:
      # Proof-of-concept, prep for E2E only. No radar points available. Panda ALLOW_DEBUG firmware required.
      ret.openpilotLongitudinalControl = True
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_VOLKSWAGEN_LONG_CONTROL
      if ret.transmissionType == TransmissionType.manual:
        ret.minEnableSpeed = 4.5

    ret.pcmCruise = not ret.openpilotLongitudinalControl
    ret.customStockLongAvailable = True
    ret.pcmCruiseSpeed = False if (Params().get_bool("SpeedLimitControl") or Params().get_bool("TurnVisionControl") or
                                   Params().get_bool("TurnSpeedControl")) and not ret.openpilotLongitudinalControl and \
                                  Params().get_bool("CustomStockLong") and ret.customStockLongAvailable else True
    ret.stoppingControl = True
    ret.startingState = True
    ret.startAccel = 1.0
    ret.vEgoStarting = 1.0
    ret.vEgoStopping = 1.0
    ret.longitudinalTuning.kpV = [0.1]
    ret.longitudinalTuning.kiV = [0.0]

    # Per-chassis tuning values, override tuning defaults here if desired

    if candidate == CAR.ARTEON_MK1:
      ret.mass = 1733 + STD_CARGO_KG
      ret.wheelbase = 2.84

    elif candidate == CAR.ATLAS_MK1:
      ret.mass = 2011 + STD_CARGO_KG
      ret.wheelbase = 2.98

    elif candidate == CAR.GOLF_MK7:
      ret.mass = 1397 + STD_CARGO_KG
      ret.wheelbase = 2.62

    elif candidate == CAR.JETTA_MK7:
      ret.mass = 1328 + STD_CARGO_KG
      ret.wheelbase = 2.71

    elif candidate == CAR.PASSAT_MK8:
      ret.mass = 1551 + STD_CARGO_KG
      ret.wheelbase = 2.79

    elif candidate == CAR.PASSAT_NMS:
      ret.mass = 1503 + STD_CARGO_KG
      ret.wheelbase = 2.80
      ret.minEnableSpeed = 20 * CV.KPH_TO_MS  # ACC "basic", no FtS
      ret.minSteerSpeed = 50 * CV.KPH_TO_MS
      ret.steerActuatorDelay = 0.2
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    elif candidate == CAR.POLO_MK6:
      ret.mass = 1230 + STD_CARGO_KG
      ret.wheelbase = 2.55

    elif candidate == CAR.SHARAN_MK2:
      ret.mass = 1639 + STD_CARGO_KG
      ret.wheelbase = 2.92
      ret.minSteerSpeed = 50 * CV.KPH_TO_MS
      ret.steerActuatorDelay = 0.2

    elif candidate == CAR.TAOS_MK1:
      ret.mass = 1498 + STD_CARGO_KG
      ret.wheelbase = 2.69

    elif candidate == CAR.TCROSS_MK1:
      ret.mass = 1150 + STD_CARGO_KG
      ret.wheelbase = 2.60

    elif candidate == CAR.TIGUAN_MK2:
      ret.mass = 1715 + STD_CARGO_KG
      ret.wheelbase = 2.74

    elif candidate == CAR.TOURAN_MK2:
      ret.mass = 1516 + STD_CARGO_KG
      ret.wheelbase = 2.79

    elif candidate == CAR.TRANSPORTER_T61:
      ret.mass = 1926 + STD_CARGO_KG
      ret.wheelbase = 3.00  # SWB, LWB is 3.40, TBD how to detect difference
      ret.minSteerSpeed = 14.0

    elif candidate == CAR.TROC_MK1:
      ret.mass = 1413 + STD_CARGO_KG
      ret.wheelbase = 2.63

    elif candidate == CAR.AUDI_A3_MK3:
      ret.mass = 1335 + STD_CARGO_KG
      ret.wheelbase = 2.61

    elif candidate == CAR.AUDI_Q2_MK1:
      ret.mass = 1205 + STD_CARGO_KG
      ret.wheelbase = 2.61

    elif candidate == CAR.AUDI_Q3_MK2:
      ret.mass = 1623 + STD_CARGO_KG
      ret.wheelbase = 2.68

    elif candidate == CAR.SEAT_ATECA_MK1:
      ret.mass = 1900 + STD_CARGO_KG
      ret.wheelbase = 2.64

    elif candidate == CAR.SEAT_LEON_MK3:
      ret.mass = 1227 + STD_CARGO_KG
      ret.wheelbase = 2.64

    elif candidate == CAR.SKODA_KAMIQ_MK1:
      ret.mass = 1265 + STD_CARGO_KG
      ret.wheelbase = 2.66

    elif candidate == CAR.SKODA_KAROQ_MK1:
      ret.mass = 1278 + STD_CARGO_KG
      ret.wheelbase = 2.66

    elif candidate == CAR.SKODA_KODIAQ_MK1:
      ret.mass = 1569 + STD_CARGO_KG
      ret.wheelbase = 2.79

    elif candidate == CAR.SKODA_OCTAVIA_MK3:
      ret.mass = 1388 + STD_CARGO_KG
      ret.wheelbase = 2.68

    elif candidate == CAR.SKODA_SCALA_MK1:
      ret.mass = 1192 + STD_CARGO_KG
      ret.wheelbase = 2.65

    elif candidate == CAR.SKODA_SUPERB_MK3:
      ret.mass = 1505 + STD_CARGO_KG
      ret.wheelbase = 2.84

    else:
      raise ValueError(f"unsupported car {candidate}")

    if Params().get_bool("EnforceTorqueLateral"):
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    ret.autoResumeSng = ret.minEnableSpeed == -1
    ret.centerToFront = ret.wheelbase * 0.45
    return ret

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam, self.cp_ext, self.CP.transmissionType)

    ret.madsEnabled = self.CS.madsEnabled
    ret.accEnabled = self.CS.accEnabled
    ret.leftBlinkerOn = self.CS.leftBlinkerOn
    ret.rightBlinkerOn = self.CS.rightBlinkerOn
    ret.belowLaneChangeSpeed = self.CS.belowLaneChangeSpeed

    buttonEvents = []

    #for button in self.CS.button_events:
    #  buttonEvents.append(button)

    # Check for and process state-change events (button press or release) from
    # the turn stalk switch or ACC steering wheel/control stalk buttons.
    for button in self.CS.buttonStates:
      if self.CS.buttonStates[button] != self.buttonStatesPrev[button]:
        be = car.CarState.ButtonEvent.new_message()
        be.type = button
        be.pressed = self.CS.buttonStates[button]
        buttonEvents.append(be)

    # MADS BUTTON
    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.altButton1
      buttonEvents.append(be)

    ret.buttonEvents = buttonEvents

    events = self.create_common_events(ret, extra_gears=[GearShifter.eco, GearShifter.sport, GearShifter.manumatic],
                                       pcm_enable=False,
                                       enable_buttons=(ButtonType.setCruise, ButtonType.resumeCruise))

    # Low speed steer alert hysteresis logic
    if self.CP.minSteerSpeed > 0. and ret.vEgo < (self.CP.minSteerSpeed + 1.):
      self.low_speed_alert = True
    elif ret.vEgo > (self.CP.minSteerSpeed + 2.):
      self.low_speed_alert = False
    if self.low_speed_alert and self.CS.madsEnabled:
      events.add(EventName.belowSteerSpeed)

    if self.CS.CP.openpilotLongitudinalControl:
      if ret.vEgo < self.CP.minEnableSpeed + 0.5:
        events.add(EventName.belowEngageSpeed)
      if c.enabled and ret.vEgo < self.CP.minEnableSpeed:
        events.add(EventName.speedTooLow)

    self.CS.disengageByBrake = self.CS.disengageByBrake or ret.disengageByBrake

    enable_pressed = False
    enable_from_brake = False

    if self.CS.disengageByBrake and not ret.brakePressed and not ret.parkingBrake and self.CS.madsEnabled:
      enable_pressed = True
      enable_from_brake = True

    if not ret.brakePressed and not ret.parkingBrake:
      self.CS.disengageByBrake = False
      ret.disengageByBrake = False

    for b in ret.buttonEvents:
      # do enable on both accel and decel buttons
      if b.type in (ButtonType.setCruise, ButtonType.resumeCruise, ButtonType.accelCruise, ButtonType.decelCruise) and not b.pressed:
        enable_pressed = True
      if b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) and not self.CS.resumeAvailable and (not self.CP.pcmCruise or not self.CP.pcmCruiseSpeed):
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
      if b.type == ButtonType.cancel and b.pressed:
        if not self.CS.madsEnabled:
          events.add(EventName.buttonCancel)
        elif ret.cruiseState.enabled:
          events.add(EventName.manualLongitudinalRequired)
    if (ret.cruiseState.enabled or self.CS.madsEnabled) and enable_pressed:
      if enable_from_brake:
        events.add(EventName.silentButtonEnable)
      else:
        events.add(EventName.buttonEnable)

    self.buttonStatesPrev = self.CS.buttonStates.copy()

    ret.customStockLong = self.CS.update_custom_stock_long(self.CC.cruise_button, self.CC.final_speed_kph,
                                                           self.CC.v_cruise_kph_prev, self.CC.target_speed,
                                                           self.CC.v_set_dis, self.CC.speed_diff, self.CC.button_type)

    ret.events = events.to_msg()

    return ret

  def apply(self, c):
    return self.CC.update(c, self.CS, self.ext_bus)
