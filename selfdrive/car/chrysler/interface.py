#!/usr/bin/env python3
from cereal import car
from panda import Panda
from openpilot.selfdrive.car import create_button_events, get_safety_config
from openpilot.selfdrive.car.chrysler.values import CAR, RAM_HD, RAM_DT, RAM_CARS, ChryslerFlags, ChryslerFlagsSP
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName
GearShifter = car.CarState.GearShifter


class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "chrysler"

    # radar parsing needs some work, see https://github.com/commaai/openpilot/issues/26842
    ret.radarUnavailable = True # DBC[candidate]['radar'] is None
    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 0.4
    ret.customStockLongAvailable = True

    # safety config
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.chrysler)]
    if candidate in RAM_HD:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_CHRYSLER_RAM_HD
    elif candidate in RAM_DT:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_CHRYSLER_RAM_DT

    CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)
    if candidate not in RAM_CARS:
      # Newer FW versions standard on the following platforms, or flashed by a dealer onto older platforms have a higher minimum steering speed.
      new_eps_platform = candidate in (CAR.CHRYSLER_PACIFICA_2019_HYBRID, CAR.CHRYSLER_PACIFICA_2020, CAR.JEEP_GRAND_CHEROKEE_2019, CAR.DODGE_DURANGO)
      new_eps_firmware = any(fw.ecu == 'eps' and fw.fwVersion[:4] >= b"6841" for fw in car_fw)
      if new_eps_platform or new_eps_firmware:
        ret.flags |= ChryslerFlags.HIGHER_MIN_STEERING_SPEED.value

    # Chrysler
    if candidate in (CAR.CHRYSLER_PACIFICA_2018, CAR.CHRYSLER_PACIFICA_2018_HYBRID, CAR.CHRYSLER_PACIFICA_2019_HYBRID,
                     CAR.CHRYSLER_PACIFICA_2020, CAR.DODGE_DURANGO):
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kpBP, ret.lateralTuning.pid.kiBP = [[9., 20.], [9., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.15, 0.30], [0.03, 0.05]]
      ret.lateralTuning.pid.kf = 0.00006

    # Jeep
    elif candidate in (CAR.JEEP_GRAND_CHEROKEE, CAR.JEEP_GRAND_CHEROKEE_2019):
      ret.steerActuatorDelay = 0.2

      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kpBP, ret.lateralTuning.pid.kiBP = [[9., 20.], [9., 20.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.15, 0.30], [0.03, 0.05]]
      ret.lateralTuning.pid.kf = 0.00006

    # Ram
    elif candidate == CAR.RAM_1500_5TH_GEN:
      ret.steerActuatorDelay = 0.2
      ret.wheelbase = 3.88
      # Older EPS FW allow steer to zero
      # Older EPS FW allow steer to zero
      if any(fw.ecu == 'eps' and b"68" < fw.fwVersion[:4] <= b"6831" for fw in car_fw):
        ret.minSteerSpeed = 0.
      if any(fw.ecu == 'eps' and fw.fwVersion in (b"68273275AF", b"68273275AG", b"68312176AE", b"68312176AG",) for fw in car_fw):
        ret.minEnableSpeed = 0.

    elif candidate == CAR.RAM_HD_5TH_GEN:
      ret.steerActuatorDelay = 0.2
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning, 1.0, False)
      ret.spFlags |= ChryslerFlagsSP.SP_RAM_HD_PARAMSD_IGNORE.value

    else:
      raise ValueError(f"Unsupported car: {candidate}")

    if ret.flags & ChryslerFlags.HIGHER_MIN_STEERING_SPEED:
      # TODO: allow these cars to steer down to 13 m/s if already engaged.
      # TODO: Durango 2020 may be able to steer to zero once above 38 kph
      ret.minSteerSpeed = 17.5  # m/s 17 on the way up, 13 on the way down once engaged.

    ret.centerToFront = ret.wheelbase * 0.44
    ret.enableBsm = 720 in fingerprint[0]

    if 0x4FF in fingerprint[0]:
      ret.spFlags |= ChryslerFlagsSP.SP_WP_S20.value
      ret.minSteerSpeed = 0.0

    return ret

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)

    self.CS.button_events = [
      *self.CS.button_events,
      *create_button_events(self.CS.distance_button, self.CS.prev_distance_button, {1: ButtonType.gapAdjustCruise}),
      *create_button_events(self.CS.lkas_enabled, self.CS.prev_lkas_enabled, {1: ButtonType.altButton1}),
    ]

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret)

    self.CS.accEnabled = self.get_sp_v_cruise_non_pcm_state(ret, c.vCruise, self.CS.accEnabled,
                                                            enable_buttons=(ButtonType.accelCruise, ButtonType.decelCruise, ButtonType.resumeCruise) if not self.CP.pcmCruiseSpeed else
                                                                           (ButtonType.accelCruise, ButtonType.decelCruise),
                                                            resume_button=(ButtonType.resumeCruise,) if not self.CP.pcmCruiseSpeed else
                                                                          (ButtonType.accelCruise, ButtonType.resumeCruise))

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        if any(b.type == ButtonType.altButton1 and b.pressed for b in self.CS.button_events):
          self.CS.madsEnabled = not self.CS.madsEnabled
          self.CS.lkas_disabled = not self.CS.lkas_disabled
        self.CS.madsEnabled = self.get_acc_mads(ret, self.CS.madsEnabled)
    else:
      self.CS.madsEnabled = False
    self.CS.madsEnabled = self.get_sp_started_mads(ret, self.CS.madsEnabled)

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.CP.pcmCruiseSpeed:
      if any(b.type == ButtonType.cancel for b in self.CS.button_events):
        self.get_sp_cancel_cruise_state()
    if self.get_sp_pedal_disengage(ret):
      self.get_sp_cancel_cruise_state()
      ret.cruiseState.enabled = ret.cruiseState.enabled if not self.enable_mads else False if self.CP.pcmCruise else self.CS.accEnabled

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.CS.accEnabled = False
      self.CS.accEnabled = ret.cruiseState.enabled or self.CS.accEnabled

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.CS.accEnabled = False
      self.CS.accEnabled = ret.cruiseState.enabled or self.CS.accEnabled

    ret = self.get_sp_common_state(ret)

    ret.buttonEvents = [
      *self.CS.button_events,
      *self.button_events.create_mads_event(self.CS.madsEnabled, self.CS.out.madsEnabled)  # MADS BUTTON
    ]

    # events
    events = self.create_common_events(ret, c, extra_gears=[car.CarState.GearShifter.low], pcm_enable=False)

    events, ret = self.create_sp_events(ret, events)

    # Low speed steer alert hysteresis logic
    if self.CP.carFingerprint in RAM_DT:
      if self.CS.out.vEgo >= self.CP.minEnableSpeed:
        self.low_speed_alert = False
      if (self.CP.minEnableSpeed >= 14.5) and (self.CS.out.gearShifter != car.CarState.GearShifter.drive):
        self.low_speed_alert = True
    else:
      if self.CP.minSteerSpeed > 0. and ret.vEgo < (self.CP.minSteerSpeed + 0.5):
        self.low_speed_alert = True
      elif ret.vEgo > (self.CP.minSteerSpeed + 1.):
        self.low_speed_alert = False
    if self.low_speed_alert:
      events.add(car.CarEvent.EventName.belowSteerSpeed)

    ret.events = events.to_msg()

    return ret
