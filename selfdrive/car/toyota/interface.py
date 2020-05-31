#!/usr/bin/env python3
from cereal import car
from common.conversions import Conversions as CV
from panda import Panda
from selfdrive.car.toyota.tunes import LatTunes, LongTunes, set_long_tune, set_lat_tune
from selfdrive.car.toyota.values import Ecu, CAR, ToyotaFlags, TSS2_CAR, RADAR_ACC_CAR, NO_DSU_CAR, MIN_ACC_SPEED, EPS_SCALE, EV_HYBRID_CAR, CarControllerParams, CruiseButtons, FEATURES
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, gen_empty_fingerprint, get_safety_config
from selfdrive.car.interfaces import CarInterfaceBase
from common.params import Params
from selfdrive.controls.lib.latcontrol_torque import set_torque_tune
from decimal import Decimal

EventName = car.CarEvent.EventName
ButtonType = car.CarState.ButtonEvent.Type


class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)
  @staticmethod
  def get_pid_accel_limits(CP, current_speed, cruise_speed):
    return CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), car_fw=[], disable_radar=False):  # pylint: disable=dangerous-default-value
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint)

    ret.carName = "toyota"
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.toyota)]
    ret.safetyConfigs[0].safetyParam = EPS_SCALE[candidate]

    if candidate in (CAR.RAV4, CAR.PRIUS_V, CAR.COROLLA, CAR.LEXUS_ESH, CAR.LEXUS_CTH):
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_ALT_BRAKE

    ret.steerActuatorDelay = 0.12  # Default delay, Prius has larger delay
    ret.steerLimitTimer = 0.4
    ret.stoppingControl = False  # Toyota starts braking more when it thinks you want to stop

    stop_and_go = False

    if candidate == CAR.PRIUS:
      stop_and_go = True
      ret.wheelbase = 2.70
      ret.steerRatio = 15.74   # unknown end-to-end spec
      tire_stiffness_factor = 0.6371   # hand-tune
      ret.mass = 3045. * CV.LB_TO_KG + STD_CARGO_KG
      ret.maxLateralAccel = 1.7
      set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.06, steering_angle_deadzone_deg=1.0)

    elif candidate == CAR.PRIUS_V:
      stop_and_go = True
      ret.wheelbase = 2.78
      ret.steerRatio = 17.4
      tire_stiffness_factor = 0.5533
      ret.mass = 3340. * CV.LB_TO_KG + STD_CARGO_KG
      ret.maxLateralAccel = 1.8
      set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.06)

    elif candidate in (CAR.RAV4, CAR.RAV4H):
      stop_and_go = True if (candidate in CAR.RAV4H) else False
      ret.wheelbase = 2.65
      ret.steerRatio = 16.88   # 14.5 is spec end-to-end
      tire_stiffness_factor = 0.5533
      ret.mass = 3650. * CV.LB_TO_KG + STD_CARGO_KG  # mean between normal and hybrid
      ret.maxLateralAccel = 1.8
      set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.06)

    elif candidate == CAR.COROLLA:
      ret.wheelbase = 2.70
      ret.steerRatio = 18.27
      tire_stiffness_factor = 0.444  # not optimized yet
      ret.mass = 2860. * CV.LB_TO_KG + STD_CARGO_KG  # mean between normal and hybrid
      ret.maxLateralAccel = 2.8
      set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.024)

    elif candidate in (CAR.LEXUS_RX, CAR.LEXUS_RXH, CAR.LEXUS_RX_TSS2, CAR.LEXUS_RXH_TSS2):
      stop_and_go = True
      ret.wheelbase = 2.79
      ret.steerRatio = 16.  # 14.8 is spec end-to-end
      ret.wheelSpeedFactor = 1.035
      tire_stiffness_factor = 0.5533
      ret.mass = 4481. * CV.LB_TO_KG + STD_CARGO_KG  # mean between min and max
      set_lat_tune(ret.lateralTuning, LatTunes.PID_C)

    elif candidate in (CAR.CHR, CAR.CHRH):
      stop_and_go = True
      ret.wheelbase = 2.63906
      ret.steerRatio = 13.6
      tire_stiffness_factor = 0.7933
      ret.mass = 3300. * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_F)

    elif candidate in (CAR.CAMRY, CAR.CAMRYH, CAR.CAMRY_TSS2, CAR.CAMRYH_TSS2):
      stop_and_go = True
      ret.wheelbase = 2.82448
      ret.steerRatio = 13.7
      tire_stiffness_factor = 0.7933
      ret.mass = 3400. * CV.LB_TO_KG + STD_CARGO_KG  # mean between normal and hybrid
      if candidate in (CAR.CAMRY_TSS2, CAR.CAMRYH_TSS2):
        ret.maxLateralAccel = 2.4
        set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.05)
      else:
        set_lat_tune(ret.lateralTuning, LatTunes.PID_C)

    elif candidate in (CAR.HIGHLANDER_TSS2, CAR.HIGHLANDERH_TSS2):
      stop_and_go = True
      ret.wheelbase = 2.84988  # 112.2 in = 2.84988 m
      ret.steerRatio = 16.0
      tire_stiffness_factor = 0.8
      ret.mass = 4700. * CV.LB_TO_KG + STD_CARGO_KG  # 4260 + 4-5 people
      set_lat_tune(ret.lateralTuning, LatTunes.PID_G)

    elif candidate in (CAR.HIGHLANDER, CAR.HIGHLANDERH):
      stop_and_go = True
      ret.wheelbase = 2.78
      ret.steerRatio = 16.0
      tire_stiffness_factor = 0.8
      ret.mass = 4607. * CV.LB_TO_KG + STD_CARGO_KG  # mean between normal and hybrid limited
      set_lat_tune(ret.lateralTuning, LatTunes.PID_G)

    elif candidate in (CAR.AVALON, CAR.AVALON_2019, CAR.AVALONH_2019, CAR.AVALON_TSS2, CAR.AVALONH_TSS2):
      # starting from 2019, all Avalon variants have stop and go
      # https://engage.toyota.com/static/images/toyota_safety_sense/TSS_Applicability_Chart.pdf
      stop_and_go = candidate != CAR.AVALON
      ret.wheelbase = 2.82
      ret.steerRatio = 14.8  # Found at https://pressroom.toyota.com/releases/2016+avalon+product+specs.download
      tire_stiffness_factor = 0.7983
      ret.mass = 3505. * CV.LB_TO_KG + STD_CARGO_KG  # mean between normal and hybrid
      set_lat_tune(ret.lateralTuning, LatTunes.PID_H)

    elif candidate in (CAR.RAV4_TSS2, CAR.RAV4_TSS2_2022, CAR.RAV4H_TSS2, CAR.RAV4H_TSS2_2022):
      stop_and_go = True
      ret.wheelbase = 2.68986
      ret.steerRatio = 14.3
      tire_stiffness_factor = 0.7933
      ret.mass = 3585. * CV.LB_TO_KG + STD_CARGO_KG  # Average between ICE and Hybrid
      set_lat_tune(ret.lateralTuning, LatTunes.PID_D)

      # 2019+ RAV4 TSS2 uses two different steering racks and specific tuning seems to be necessary.
      # See https://github.com/commaai/openpilot/pull/21429#issuecomment-873652891
      for fw in car_fw:
        if fw.ecu == "eps" and (fw.fwVersion.startswith(b'\x02') or fw.fwVersion in [b'8965B42181\x00\x00\x00\x00\x00\x00']):
          set_lat_tune(ret.lateralTuning, LatTunes.PID_I)
          break

    elif candidate in (CAR.COROLLA_TSS2, CAR.COROLLAH_TSS2):
      stop_and_go = True
      ret.wheelbase = 2.67  # Average between 2.70 for sedan and 2.64 for hatchback
      ret.steerRatio = 13.9
      tire_stiffness_factor = 0.444  # not optimized yet
      ret.mass = 3060. * CV.LB_TO_KG + STD_CARGO_KG
      ret.maxLateralAccel = 2.0
      if Params().get_bool("CorollaIndi"):
        ret.lateralTuning.init('indi')
        ret.lateralTuning.indi.innerLoopGainBP = [18, 22, 26]
        ret.lateralTuning.indi.innerLoopGainV = [9, 12, 15]
        ret.lateralTuning.indi.outerLoopGainBP = [18, 22, 26]
        ret.lateralTuning.indi.outerLoopGainV = [8, 11, 14.99]
        ret.lateralTuning.indi.timeConstantBP = [18, 22, 26]
        ret.lateralTuning.indi.timeConstantV = [1, 3, 4.5]
        ret.lateralTuning.indi.actuatorEffectivenessBP = [18, 22, 26]
        ret.lateralTuning.indi.actuatorEffectivenessV = [9, 12, 15]
        ret.steerActuatorDelay = 0.42 - 0.2
      else:
        set_lat_tune(ret.lateralTuning, LatTunes.TORQUE, MAX_LAT_ACCEL=ret.maxLateralAccel, FRICTION=0.07)

    elif candidate in (CAR.LEXUS_ES_TSS2, CAR.LEXUS_ESH_TSS2, CAR.LEXUS_ESH):
      stop_and_go = True
      ret.wheelbase = 2.8702
      ret.steerRatio = 16.0  # not optimized
      tire_stiffness_factor = 0.444  # not optimized yet
      ret.mass = 3677. * CV.LB_TO_KG + STD_CARGO_KG  # mean between min and max
      set_lat_tune(ret.lateralTuning, LatTunes.PID_D)

    elif candidate == CAR.SIENNA:
      stop_and_go = True
      ret.wheelbase = 3.03
      ret.steerRatio = 15.5
      tire_stiffness_factor = 0.444
      ret.mass = 4590. * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_J)

    elif candidate in (CAR.LEXUS_IS, CAR.LEXUS_RC):
      ret.wheelbase = 2.79908
      ret.steerRatio = 13.3
      tire_stiffness_factor = 0.444
      ret.mass = 3736.8 * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_L)

    elif candidate == CAR.LEXUS_CTH:
      stop_and_go = True
      ret.wheelbase = 2.60
      ret.steerRatio = 18.6
      tire_stiffness_factor = 0.517
      ret.mass = 3108 * CV.LB_TO_KG + STD_CARGO_KG  # mean between min and max
      set_lat_tune(ret.lateralTuning, LatTunes.PID_M)

    elif candidate in (CAR.LEXUS_NXH, CAR.LEXUS_NX, CAR.LEXUS_NX_TSS2):
      stop_and_go = True
      ret.wheelbase = 2.66
      ret.steerRatio = 14.7
      tire_stiffness_factor = 0.444  # not optimized yet
      ret.mass = 4070 * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_C)

    elif candidate == CAR.PRIUS_TSS2:
      stop_and_go = True
      ret.wheelbase = 2.70002  # from toyota online sepc.
      ret.steerRatio = 13.4   # True steerRatio from older prius
      tire_stiffness_factor = 0.6371   # hand-tune
      ret.mass = 3115. * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_N)

    elif candidate == CAR.MIRAI:
      stop_and_go = True
      ret.wheelbase = 2.91
      ret.steerRatio = 14.8
      tire_stiffness_factor = 0.8
      ret.mass = 4300. * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_C)

    elif candidate in (CAR.ALPHARD_TSS2, CAR.ALPHARDH_TSS2):
      stop_and_go = True
      ret.wheelbase = 3.00
      ret.steerRatio = 14.2
      tire_stiffness_factor = 0.444
      ret.mass = 4305. * CV.LB_TO_KG + STD_CARGO_KG
      set_lat_tune(ret.lateralTuning, LatTunes.PID_J)

    torque_max_lat_accel = float(Decimal(Params().get("TorqueMaxLatAccel", encoding="utf8")) * Decimal('0.1'))
    torque_friction = float(Decimal(Params().get("TorqueFriction", encoding="utf8")) * Decimal('0.01'))
    torque_deadzone_deg = float(Decimal(Params().get("TorqueDeadzoneDeg", encoding="utf8")) * Decimal('0.1'))

    if Params().get_bool("CustomTorqueLateral"):
      set_torque_tune(ret.lateralTuning, torque_max_lat_accel, torque_friction, torque_deadzone_deg)

    ret.steerRateCost = 1.
    ret.centerToFront = ret.wheelbase * 0.44

    # TODO: get actual value, for now starting with reasonable value for
    # civic and scaling by mass and wheelbase
    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)

    ret.enableBsm = 0x3F6 in fingerprint[0] and candidate in TSS2_CAR
    # Detect smartDSU, which intercepts ACC_CMD from the DSU allowing openpilot to send it
    ret.smartDsu = 0x2FF in fingerprint[0]
    # In TSS2 cars the camera does long control
    found_ecus = [fw.ecu for fw in car_fw]
    ret.enableDsu = (len(found_ecus) > 0) and (Ecu.dsu not in found_ecus) and (candidate not in NO_DSU_CAR) and (not ret.smartDsu)
    ret.enableGasInterceptor = 0x201 in fingerprint[0]
    # if the smartDSU is detected, openpilot can send ACC_CMD (and the smartDSU will block it from the DSU) or not (the DSU is "connected")
    ret.openpilotLongitudinalControl = (ret.smartDsu or ret.enableDsu or candidate in (TSS2_CAR - RADAR_ACC_CAR)) and \
                                       not Params().get_bool("StockLongToyota")

    if not ret.openpilotLongitudinalControl:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_STOCK_LONGITUDINAL

    # we can't use the fingerprint to detect this reliably, since
    # the EV gas pedal signal can take a couple seconds to appear
    if candidate in EV_HYBRID_CAR:
      ret.flags |= ToyotaFlags.HYBRID.value

    # min speed to enable ACC. if car can do stop and go, then set enabling speed
    # to a negative value, so it won't matter.
    ret.minEnableSpeed = -1. if (stop_and_go or ret.enableGasInterceptor) else MIN_ACC_SPEED

    if ret.enableGasInterceptor:
      set_long_tune(ret.longitudinalTuning, LongTunes.PEDAL)
    elif candidate in TSS2_CAR:
      set_long_tune(ret.longitudinalTuning, LongTunes.TSS2)
      ret.stoppingDecelRate = 0.3  # reach stopping target smoothly
    else:
      set_long_tune(ret.longitudinalTuning, LongTunes.TSS)

    ret.latActive = False

    ret.standStill = False

    Params().put("CarMake", "2")

    return ret

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)

    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False

    ret.madsEnabled = self.CS.madsEnabled
    ret.accEnabled = self.CS.accEnabled
    ret.leftBlinkerOn = self.CS.leftBlinkerOn
    ret.rightBlinkerOn = self.CS.rightBlinkerOn
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
    if self.CS.cruise_buttons != self.CS.prev_cruise_buttons:
      be = car.CarState.ButtonEvent.new_message()
      be.type = ButtonType.unknown
      if self.CS.cruise_buttons in [CruiseButtons.ACCEL_ACC, CruiseButtons.ACCEL_CC,CruiseButtons.DECEL_ACC, CruiseButtons.DECEL_CC]:
        be.pressed = True
        but = self.CS.cruise_buttons
      else:
        be.pressed = False
        but = self.CS.prev_cruise_buttons
      if but in [CruiseButtons.ACCEL_ACC, CruiseButtons.ACCEL_CC]:
        be.type = ButtonType.accelCruise
      elif but in [CruiseButtons.DECEL_ACC, CruiseButtons.DECEL_CC]:
        be.type = ButtonType.decelCruise
      buttonEvents.append(be)

    # MADS BUTTON
    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.altButton1
      buttonEvents.append(be)

    ret.buttonEvents = buttonEvents

    extraGears = []
    if not (self.CS.CP.openpilotLongitudinalControl or self.CS.CP.enableGasInterceptor):
      extraGears = [car.CarState.GearShifter.sport, car.CarState.GearShifter.low, car.CarState.GearShifter.brake]

    # events
    events = self.create_common_events(ret, extra_gears=extraGears, pcm_enable=False)

    #if self.CS.low_speed_lockout and self.CP.openpilotLongitudinalControl:
    #  events.add(EventName.lowSpeedLockout)
    #if ret.vEgo < self.CP.minEnableSpeed and self.CP.openpilotLongitudinalControl:
    #  events.add(EventName.belowEngageSpeed)
    #  if c.actuators.accel > 0.3:
    #    # some margin on the actuator to not false trigger cancellation while stopping
    #    events.add(EventName.speedTooLow)
    #  if ret.vEgo < 0.001:
    #    # while in standstill, send a user alert
    #    events.add(EventName.manualRestart)

    self.CS.disengageByBrake = self.CS.disengageByBrake or ret.disengageByBrake

    enable_pressed = False
    enable_from_brake = False

    if self.CS.disengageByBrake and not ret.brakePressed and not ret.brakeHoldActive and not ret.parkingBrake and self.CS.madsEnabled:
      enable_pressed = True
      enable_from_brake = True

    if not ret.brakePressed and not ret.brakeHoldActive and not ret.parkingBrake:
      self.CS.disengageByBrake = False
      ret.disengageByBrake = False

    # handle button presses
    for b in ret.buttonEvents:
      # do enable on both accel and decel buttons
      if b.type in [ButtonType.setCruise] and not b.pressed:
        enable_pressed = True
      # do disable on MADS button if ACC is disabled
      if b.type in [ButtonType.altButton1] and b.pressed:
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
        else:
          events.add(EventName.manualLongitudinalRequired)
    if (ret.cruiseState.enabled or self.CS.madsEnabled) and enable_pressed:
      if enable_from_brake:
        events.add(EventName.silentButtonEnable)
      else:
        events.add(EventName.buttonEnable)

    self.CP.latActive = True if self.CC.lat_active else False

    if self.CS.cruiseState_standstill or self.CC.standstill_status == 1:
      self.CP.standStill = True
    else:
      self.CP.standStill = False

    ret.events = events.to_msg()

    return ret

  # pass in a car.CarControl
  # to be called @ 100hz
  def apply(self, c):
    ret = self.CC.update(c, self.CS)
    return ret
