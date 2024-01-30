from cereal import car
from panda import Panda
from openpilot.selfdrive.car import get_safety_config, create_mads_event
from openpilot.selfdrive.car.interfaces import CarInterfaceBase
from openpilot.selfdrive.car.nissan.values import CAR

ButtonType = car.CarState.ButtonEvent.Type
GearShifter = car.CarState.GearShifter


class CarInterface(CarInterfaceBase):

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "nissan"
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.nissan)]
    ret.autoResumeSng = False

    ret.steerLimitTimer = 1.0

    ret.steerActuatorDelay = 0.1
    ret.steerRatio = 17

    ret.steerControlType = car.CarParams.SteerControlType.angle
    ret.radarUnavailable = True

    if candidate in (CAR.ROGUE, CAR.XTRAIL):
      ret.mass = 1610
      ret.wheelbase = 2.705
      ret.centerToFront = ret.wheelbase * 0.44
    elif candidate in (CAR.LEAF, CAR.LEAF_IC):
      ret.mass = 1610
      ret.wheelbase = 2.705
      ret.centerToFront = ret.wheelbase * 0.44
    elif candidate == CAR.ALTIMA:
      # Altima has EPS on C-CAN unlike the others that have it on V-CAN
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_NISSAN_ALT_EPS_BUS
      ret.mass = 1492
      ret.wheelbase = 2.824
      ret.centerToFront = ret.wheelbase * 0.44

    return ret

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_adas, self.cp_cam)
    self.CS = self.sp_update_params(self.CS)

    buttonEvents = []
    #be = car.CarState.ButtonEvent.new_message()
    #be.type = car.CarState.ButtonEvent.Type.accelCruise
    #buttonEvents.append(be)

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret, self.CS)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        self.CS.madsEnabled = self.get_acc_mads(ret.cruiseState.enabled, self.CS.accEnabled, self.CS.madsEnabled)
    else:
      self.CS.madsEnabled = False

    if (not ret.cruiseState.enabled and self.CS.out.cruiseState.enabled) or \
       self.get_sp_pedal_disengage(ret):
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

    events = self.create_common_events(ret, c, extra_gears=[GearShifter.sport, GearShifter.low, GearShifter.brake],
                                       pcm_enable=False)

    events, ret = self.create_sp_events(self.CS, ret, events)

    if self.CS.lkas_enabled:
      events.add(car.CarEvent.EventName.invalidLkasSetting)

    ret.events = events.to_msg()

    return ret

  def apply(self, c, now_nanos):
    return self.CC.update(c, self.CS, now_nanos)
