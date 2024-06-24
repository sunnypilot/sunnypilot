from cereal import car
from panda import Panda
from openpilot.selfdrive.car import get_safety_config, create_mads_event
from openpilot.selfdrive.car.disable_ecu import disable_ecu
from openpilot.selfdrive.car.interfaces import CarInterfaceBase
from openpilot.selfdrive.car.subaru.values import CAR, GLOBAL_ES_ADDR, SubaruFlags, SubaruFlagsSP


ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName
GearShifter = car.CarState.GearShifter

class CarInterface(CarInterfaceBase):

  @staticmethod
  def _get_params(ret, candidate: CAR, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "subaru"
    ret.radarUnavailable = True
    # for HYBRID CARS to be upstreamed, we need:
    # - replacement for ES_Distance so we can cancel the cruise control
    # - to find the Cruise_Activated bit from the car
    # - proper panda safety setup (use the correct cruise_activated bit, throttle from Throttle_Hybrid, etc)
    ret.dashcamOnly = bool(ret.flags & (SubaruFlags.LKAS_ANGLE | SubaruFlags.HYBRID))
    ret.autoResumeSng = False

    # Detect infotainment message sent from the camera
    if not (ret.flags & SubaruFlags.PREGLOBAL) and 0x323 in fingerprint[2]:
      ret.flags |= SubaruFlags.SEND_INFOTAINMENT.value

    if ret.flags & SubaruFlags.PREGLOBAL:
      ret.enableBsm = 0x25c in fingerprint[0]
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaruPreglobal)]
    else:
      ret.enableBsm = 0x228 in fingerprint[0]
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaru)]
      if ret.flags & SubaruFlags.GLOBAL_GEN2:
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_GEN2

    if not bool(ret.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID)):
      ret.autoResumeSng = True
      ret.spFlags |= SubaruFlagsSP.SP_SUBARU_SNG.value
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_SNG

    ret.steerLimitTimer = 0.4
    ret.steerActuatorDelay = 0.1

    if ret.flags & SubaruFlags.LKAS_ANGLE:
      ret.steerControlType = car.CarParams.SteerControlType.angle
    else:
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    if candidate in (CAR.SUBARU_ASCENT, CAR.SUBARU_ASCENT_2023):
      ret.steerActuatorDelay = 0.3  # end-to-end angle controller
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00003
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.0025, 0.1], [0.00025, 0.01]]

    elif candidate == CAR.SUBARU_IMPREZA:
      ret.steerActuatorDelay = 0.4  # end-to-end angle controller
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2, 0.3], [0.02, 0.03]]
      # Certain Impreza / Crosstrek EPS use 3071 max value and do not work with stock value/scaling.
      if any(fw.ecu == "eps" and fw.fwVersion in (b'z\xc0\x00\x00', b'z\xc0\x04\x00', b'z\xc0\x08\x00', b'\x8a\xc0\x00\x00',
                                                  b'\x8a\xc0\x10\x00') for fw in car_fw):
        ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_MAX_STEER_IMPREZA_2018
        ret.steerActuatorDelay = 0.18  # measured
        ret.lateralTuning.pid.kf = 0.00003333
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.133, 0.2], [0.0133, 0.02]]

    elif candidate == CAR.SUBARU_IMPREZA_2020:
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.045, 0.042, 0.20], [0.04, 0.035, 0.045]]

    elif candidate == CAR.SUBARU_CROSSTREK_HYBRID:
      ret.steerActuatorDelay = 0.1

    elif candidate in (CAR.SUBARU_FORESTER, CAR.SUBARU_FORESTER_2022, CAR.SUBARU_FORESTER_HYBRID):
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kf = 0.000038
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.065, 0.2], [0.001, 0.015, 0.025]]

    elif candidate in (CAR.SUBARU_OUTBACK, CAR.SUBARU_LEGACY, CAR.SUBARU_OUTBACK_2023):
      ret.steerActuatorDelay = 0.1

    elif candidate in (CAR.SUBARU_FORESTER_PREGLOBAL, CAR.SUBARU_OUTBACK_PREGLOBAL_2018):
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_PREGLOBAL_REVERSED_DRIVER_TORQUE  # Outback 2018-2019 and Forester have reversed driver torque signal

    elif candidate == CAR.SUBARU_LEGACY_PREGLOBAL:
      ret.steerActuatorDelay = 0.15

    elif candidate == CAR.SUBARU_OUTBACK_PREGLOBAL:
      pass
    else:
      raise ValueError(f"unknown car: {candidate}")

    ret.experimentalLongitudinalAvailable = not (ret.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.PREGLOBAL |
                                                              SubaruFlags.LKAS_ANGLE | SubaruFlags.HYBRID))
    ret.openpilotLongitudinalControl = experimental_long and ret.experimentalLongitudinalAvailable

    if ret.flags & SubaruFlags.GLOBAL_GEN2 and ret.openpilotLongitudinalControl:
      ret.flags |= SubaruFlags.DISABLE_EYESIGHT.value

    if ret.openpilotLongitudinalControl:
      ret.stoppingControl = True
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_SUBARU_LONG

    return ret

  # returns a car.CarState
  def _update(self, c):

    ret = self.CS.update(self.cp, self.cp_cam, self.cp_body)
    self.sp_update_params()

    buttonEvents = []

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret, self.CS)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        if not (self.CP.flags & SubaruFlags.PREGLOBAL):
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
      ret.cruiseState.enabled = ret.cruiseState.enabled if not self.enable_mads else False if self.CP.pcmCruise else self.CS.accEnabled

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

  @staticmethod
  def init(CP, logcan, sendcan):
    if CP.flags & SubaruFlags.DISABLE_EYESIGHT:
      disable_ecu(logcan, sendcan, bus=2, addr=GLOBAL_ES_ADDR, com_cont_req=b'\x28\x03\x01')
