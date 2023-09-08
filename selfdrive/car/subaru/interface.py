from cereal import car
from panda import Panda
from openpilot.selfdrive.car import get_safety_config, create_mads_event
from openpilot.selfdrive.car.interfaces import CarInterfaceBase
from openpilot.selfdrive.car.subaru.values import CAR, LKAS_ANGLE, GLOBAL_GEN2, PREGLOBAL_CARS, HYBRID_CARS, SubaruFlags

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName
GearShifter = car.CarState.GearShifter


class CarInterface(CarInterfaceBase):

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "subaru"
    ret.radarUnavailable = True
    # for HYBRID CARS to be upstreamed, we need:
    # - replacement for ES_Distance so we can cancel the cruise control
    # - to find the Cruise_Activated bit from the car
    # - proper panda safety setup (use the correct cruise_activated bit, throttle from Throttle_Hybrid, etc)
    ret.dashcamOnly = candidate in (LKAS_ANGLE | HYBRID_CARS)
    ret.autoResumeSng = False

    # Detect infotainment message sent from the camera
    if candidate not in PREGLOBAL_CARS and 0x323 in fingerprint[2]:
      ret.flags |= SubaruFlags.SEND_INFOTAINMENT.value

    if candidate in PREGLOBAL_CARS:
      ret.enableBsm = 0x25c in fingerprint[0]
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaruPreglobal)]
    else:
      ret.enableBsm = 0x228 in fingerprint[0]
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaru)]
      if candidate in GLOBAL_GEN2:
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_GEN2

    ret.steerLimitTimer = 0.4
    ret.steerActuatorDelay = 0.1

    if candidate in LKAS_ANGLE:
      ret.steerControlType = car.CarParams.SteerControlType.angle
    else:
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    if candidate in (CAR.ASCENT, CAR.ASCENT_2023):
      ret.mass = 2031.
      ret.wheelbase = 2.89
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 13.5
      ret.steerActuatorDelay = 0.3   # end-to-end angle controller
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00003
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.0025, 0.1], [0.00025, 0.01]]

    elif candidate == CAR.IMPREZA:
      ret.mass = 1568.
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 15
      ret.steerActuatorDelay = 0.4   # end-to-end angle controller
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2, 0.3], [0.02, 0.03]]
      # Certain Impreza / Crosstrek EPS use 3071 max value and do not work with stock value/scaling.
      if any(fw.ecu == "eps" and fw.fwVersion in (b'z\xc0\x00\x00', b'z\xc0\x04\x00', b'z\xc0\x08\x00', b'\x8a\xc0\x00\x00',
                                                  b'\x8a\xc0\x10\x00') for fw in car_fw):
        ret.safetyConfigs[0].safetyParam = Panda.FLAG_SUBARU_MAX_STEER_IMPREZA_2018
        ret.steerActuatorDelay = 0.18  # measured
        ret.lateralTuning.pid.kf = 0.00003333
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.133, 0.2], [0.0133, 0.02]]

    elif candidate == CAR.IMPREZA_2020:
      ret.mass = 1480.
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17           # learned, 14 stock
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.045, 0.042, 0.20], [0.04, 0.035, 0.045]]

    elif candidate == CAR.CROSSTREK_HYBRID:
      ret.mass = 1668.
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17
      ret.steerActuatorDelay = 0.1

    elif candidate in (CAR.FORESTER, CAR.FORESTER_2022, CAR.FORESTER_HYBRID):
      ret.mass = 1568.
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17           # learned, 14 stock
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.000038
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.065, 0.2], [0.001, 0.015, 0.025]]

    elif candidate in (CAR.OUTBACK, CAR.LEGACY, CAR.OUTBACK_2023):
      ret.mass = 1568.
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17
      ret.steerActuatorDelay = 0.1

    elif candidate in (CAR.FORESTER_PREGLOBAL, CAR.OUTBACK_PREGLOBAL_2018):
      ret.safetyConfigs[0].safetyParam = Panda.FLAG_SUBARU_LEGACY_FLIP_DRIVER_TORQUE  # Outback 2018-2019 and Forester have reversed driver torque signal
      ret.mass = 1568
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 20           # learned, 14 stock

    elif candidate == CAR.LEGACY_PREGLOBAL:
      ret.mass = 1568
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 12.5   # 14.5 stock
      ret.steerActuatorDelay = 0.15

    elif candidate == CAR.OUTBACK_PREGLOBAL:
      ret.mass = 1568
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 20           # learned, 14 stock
    else:
      raise ValueError(f"unknown car: {candidate}")

    #ret.experimentalLongitudinalAvailable = candidate not in (GLOBAL_GEN2 | PREGLOBAL_CARS | LKAS_ANGLE | HYBRID_CARS)
    ret.openpilotLongitudinalControl = experimental_long and ret.experimentalLongitudinalAvailable

    if ret.openpilotLongitudinalControl:
      ret.longitudinalTuning.kpBP = [0., 5., 35.]
      ret.longitudinalTuning.kpV = [0.8, 1.0, 1.5]
      ret.longitudinalTuning.kiBP = [0., 35.]
      ret.longitudinalTuning.kiV = [0.54, 0.36]

      ret.stoppingControl = True
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_LONG

    return ret

  # returns a car.CarState
  def _update(self, c):

    ret = self.CS.update(self.cp, self.cp_cam, self.cp_body)
    self.CS = self.sp_update_params(self.CS)

    buttonEvents = []

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret, self.CS)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        if self.CS.car_fingerprint not in PREGLOBAL_CARS:
          if self.CS.prev_lkas_enabled != self.CS.lkas_enabled and self.CS.lkas_enabled != 2 and not (self.CS.prev_lkas_enabled == 2 and self.CS.lkas_enabled == 1):
            self.CS.madsEnabled = not self.CS.madsEnabled
          elif self.CS.prev_lkas_enabled != self.CS.lkas_enabled and self.CS.prev_lkas_enabled == 2 and self.CS.lkas_enabled != 1:
            self.CS.madsEnabled = not self.CS.madsEnabled
        self.CS.madsEnabled = self.get_acc_mads(ret.cruiseState.enabled, self.CS.accEnabled, self.CS.madsEnabled)
    else:
      self.CS.madsEnabled = False

    if self.CS.out.cruiseState.enabled:  # CANCEL
      if not ret.cruiseState.enabled:
        if not self.enable_mads:
          self.CS.madsEnabled = False
    if self.get_sp_pedal_disengage(ret):
      self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
      ret.cruiseState.enabled = False if self.CP.pcmCruise else self.CS.accEnabled

    ret, self.CS = self.get_sp_common_state(ret, self.CS)

    # CANCEL
    if self.CS.out.cruiseState.enabled and not ret.cruiseState.enabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.cancel
      buttonEvents.append(be)

    # MADS BUTTON
    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      if self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = False
    else:
      if not self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = True

    ret.buttonEvents = buttonEvents

    events = self.create_common_events(ret, c, extra_gears=[GearShifter.sport, GearShifter.low], pcm_enable=False)

    events, ret = self.create_sp_events(self.CS, ret, events)

    ret.events = events.to_msg()

    return ret

  def apply(self, c, now_nanos):
    return self.CC.update(c, self.CS, now_nanos)
