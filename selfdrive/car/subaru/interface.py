#!/usr/bin/env python3
from cereal import car
from selfdrive.car.subaru.values import CAR, Buttons, PREGLOBAL_CARS
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, gen_empty_fingerprint, get_safety_config
from selfdrive.car.interfaces import CarInterfaceBase

EventName = car.CarEvent.EventName
ButtonType = car.CarState.ButtonEvent.Type

class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), car_fw=None):
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint)

    ret.carName = "subaru"
    ret.radarOffCan = True

    if candidate in PREGLOBAL_CARS:
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaruLegacy)]
    elif candidate == CAR.OUTBACK:
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaruGen2)]
    elif candidate == CAR.CROSSTREK_2020H:
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaruHybrid)]
    else:
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.subaru)]

    if candidate in PREGLOBAL_CARS:
      ret.enableBsm = 0x25c in fingerprint[0]
    else:
      ret.enableBsm = 0x228 in fingerprint[0]

    #ret.dashcamOnly = candidate in PREGLOBAL_CARS

    ret.steerRateCost = 0.7
    ret.steerLimitTimer = 0.4

    if candidate == CAR.ASCENT:
      ret.mass = 2031. + STD_CARGO_KG
      ret.wheelbase = 2.89
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 13.5
      ret.steerActuatorDelay = 0.3   # end-to-end angle controller
      ret.lateralTuning.pid.kf = 0.00003
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.0025, 0.1], [0.00025, 0.01]]

    if candidate == CAR.IMPREZA:
      ret.mass = 1568. + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 15
      ret.steerActuatorDelay = 0.4   # end-to-end angle controller
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2, 0.3], [0.02, 0.03]]

    if candidate == CAR.IMPREZA_2020:
      ret.mass = 1480. + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 13
      ret.steerActuatorDelay = 0.1   # end-to-end angle controller
      ret.steerRateCost = 1
      ret.lateralTuning.pid.kf = 0.00003
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 10., 20., 30.], [0., 10., 20., 30.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.05, 0.2, 0.21], [0.0010, 0.004, 0.008, 0.009]]

    if candidate == CAR.CROSSTREK_2020H:
      ret.mass = 1568. + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 15
      ret.steerActuatorDelay = 0.4   # end-to-end angle controller
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2, 0.3], [0.02, 0.03]]

    if candidate == CAR.FORESTER:
      ret.mass = 1568. + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17           # learned, 14 stock
      ret.steerActuatorDelay = 0.1
      ret.lateralTuning.pid.kf = 0.000038
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.065, 0.2], [0.001, 0.015, 0.025]]

    if candidate == CAR.OUTBACK:
      ret.mass = 1568. + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 17           # learned, 14 stock
      ret.steerActuatorDelay = 0.1
      ret.lateralTuning.pid.kf = 0.000038
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 14., 23.], [0., 14., 23.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.065, 0.2], [0.001, 0.015, 0.025]]

    if candidate in [CAR.FORESTER_PREGLOBAL, CAR.OUTBACK_PREGLOBAL_2018]:
      ret.safetyConfigs[0].safetyParam = 1  # Outback 2018-2019 and Forester have reversed driver torque signal
      ret.mass = 1568 + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 20           # learned, 14 stock
      ret.steerActuatorDelay = 0.1
      ret.lateralTuning.pid.kf = 0.000039
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 10., 20.], [0., 10., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.05, 0.2], [0.003, 0.018, 0.025]]

    if candidate == CAR.WRX_PREGLOBAL:
      ret.safetyConfigs[0].safetyParam = 1  # WRX has reversed driver torque signal
      ret.mass = 1568 + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 12.5   # 14.5 stock
      ret.steerActuatorDelay = 0.15
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.1, 0.2], [0.01, 0.02]]

    if candidate == CAR.LEGACY_PREGLOBAL:
      ret.mass = 1568 + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 12.5   # 14.5 stock
      ret.steerActuatorDelay = 0.15
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.1, 0.2], [0.01, 0.02]]

    if candidate == CAR.LEGACY_PREGLOBAL_2018:
      ret.safetyConfigs[0].safetyParam = 1  # Legacy 2018-2019 has reversed driver torque signal
      ret.mass = 1568 + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 12.5   # 14.5 stock
      ret.steerActuatorDelay = 0.15
      ret.lateralTuning.pid.kf = 0.00005
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.1, 0.2], [0.01, 0.02]]

    if candidate == CAR.LEVORG_PREGLOBAL:
       ret.safetyConfigs[0].safetyParam = 1  # Levorg has reversed driver torque signal
       ret.mass = 1568 + STD_CARGO_KG
       ret.wheelbase = 2.67
       ret.centerToFront = ret.wheelbase * 0.5
       ret.steerRatio = 12.5   # 14.5 stock
       ret.steerActuatorDelay = 0.15
       ret.lateralTuning.pid.kf = 0.00005
       ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 20.], [0., 20.]]
       ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.1, 0.2], [0.01, 0.02]]

    if candidate == CAR.OUTBACK_PREGLOBAL:
      ret.mass = 1568 + STD_CARGO_KG
      ret.wheelbase = 2.67
      ret.centerToFront = ret.wheelbase * 0.5
      ret.steerRatio = 20           # learned, 14 stock
      ret.steerActuatorDelay = 0.1
      ret.lateralTuning.pid.kf = 0.000039
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0., 10., 20.], [0., 10., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.01, 0.05, 0.2], [0.003, 0.018, 0.025]]

    # TODO: get actual value, for now starting with reasonable value for
    # civic and scaling by mass and wheelbase
    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront)

    return ret

  # returns a car.CarState
  def update(self, c, can_strings):
    self.cp.update_strings(can_strings)
    self.cp_cam.update_strings(can_strings)
    if self.cp_body:
      self.cp_body.update_strings(can_strings)

    ret = self.CS.update(self.cp, self.cp_cam, self.cp_body)

    ret.canValid = self.cp.can_valid and self.cp_cam.can_valid and (self.cp_body is None or self.cp_body.can_valid)
    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False

    ret.accMainEnabled = self.CS.accMainEnabled
    ret.accEnabled = self.CS.accEnabled
    ret.leftBlinkerOn = self.CS.leftBlinkerOn
    ret.rightBlinkerOn = self.CS.rightBlinkerOn
    ret.automaticLaneChange = self.CS.automaticLaneChange
    ret.belowLaneChangeSpeed = self.CS.belowLaneChangeSpeed

    buttonEvents = []

    # SET / CANCEL
    if ret.cruiseState.enabled and not self.CS.out.cruiseState.enabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = False
      be.type = ButtonType.setCruise
      buttonEvents.append(be)
    elif self.CS.out.cruiseState.enabled and not ret.cruiseState.enabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.cancel
      buttonEvents.append(be)

    # ACCEL / DECEL
    if self.CP.carFingerprint in PREGLOBAL_CARS:
      if self.CS.cruise_button != self.CS.prev_cruise_button:
        be = car.CarState.ButtonEvent.new_message()
        be.type = ButtonType.unknown
        if self.CS.cruise_button in [Buttons.RESUME_SHALLOW, Buttons.RESUME_DEEP, Buttons.SET_SHALLOW, Buttons.SET_DEEP]:
          be.pressed = True
          but = self.CS.cruise_button
        else:
          be.pressed = False
          but = self.CS.prev_cruise_button
        if but in [Buttons.RESUME_SHALLOW, Buttons.RESUME_DEEP]:
          be.type = ButtonType.accelCruise
        elif but in [Buttons.SET_SHALLOW, Buttons.SET_DEEP]:
          be.type = ButtonType.decelCruise
        buttonEvents.append(be)
    elif self.CP.carFingerprint not in [PREGLOBAL_CARS, CAR.CROSSTREK_2020H]:
      if self.CS.cruise_button_global != self.CS.prev_cruise_button_global:
        be = car.CarState.ButtonEvent.new_message()
        be.type = ButtonType.unknown
        if self.CS.cruise_button_global in [Buttons.GLOBAL_RES_ACCEL, Buttons.GLOBAL_SET_DECEL]:
          be.pressed = True
          but = self.CS.cruise_button_global
        else:
          be.pressed = False
          but = self.CS.prev_cruise_button_global
        if but in [Buttons.GLOBAL_RES_ACCEL]:
          be.type = ButtonType.accelCruise
        elif but in [Buttons.GLOBAL_SET_DECEL]:
          be.type = ButtonType.decelCruise
        buttonEvents.append(be)

    # ACC MAIN BUTTON
    if self.CS.out.accMainEnabled != self.CS.accMainEnabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.altButton1
      buttonEvents.append(be)

    ret.buttonEvents = buttonEvents

    extraGears = []
    if not (self.CS.CP.openpilotLongitudinalControl or self.CS.CP.enableGasInterceptor):
      extraGears = [car.CarState.GearShifter.sport, car.CarState.GearShifter.low]

    #events
    events = self.create_common_events(ret, extra_gears=extraGears, pcm_enable=False)

    self.CS.disengageByBrake = self.CS.disengageByBrake or ret.disengageByBrake

    enable_pressed = False
    enable_from_brake = False

    if self.CS.disengageByBrake and not ret.brakePressed and self.CS.accMainEnabled:
      enable_pressed = True
      enable_from_brake = True

    if not ret.brakePressed:
      self.CS.disengageByBrake = False
      ret.disengageByBrake = False

    # handle button presses
    for b in ret.buttonEvents:

      # do enable on both accel and decel buttons
      if b.type in [ButtonType.accelCruise, ButtonType.setCruise] and not b.pressed:
        enable_pressed = True

      # do disable on ACC Main button if ACC is disabled
      if b.type in [ButtonType.altButton1] and b.pressed:
        if not self.CS.accMainEnabled: #disabled ACC Main
          if not ret.cruiseState.enabled:
            events.add(EventName.buttonCancel)
          else:
            events.add(EventName.manualSteeringRequired)
        else: #enabled ACC Main
          if not ret.cruiseState.enabled:
            enable_pressed = True

      # do disable on button down
      if b.type == ButtonType.cancel and b.pressed:
        if not self.CS.accMainEnabled:
          events.add(EventName.buttonCancel)
        else:
          events.add(EventName.manualLongitudinalRequired)

    if (ret.cruiseState.enabled or self.CS.accMainEnabled) and enable_pressed:
      if enable_from_brake:
        events.add(EventName.silentButtonEnable)
      else:
        events.add(EventName.buttonEnable)

    ret.events = events.to_msg()

    self.CS.out = ret.as_reader()
    return self.CS.out

  def apply(self, c):
    can_sends = self.CC.update(c.enabled, self.CS, self.frame, c.actuators,
                               c.cruiseControl.cancel, c.hudControl.visualAlert,
                               c.hudControl.leftLaneVisible, c.hudControl.rightLaneVisible, c.hudControl.leftLaneDepart, c.hudControl.rightLaneDepart)
    self.frame += 1
    return can_sends
