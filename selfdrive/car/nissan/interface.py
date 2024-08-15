from cereal import car
from panda import Panda
from openpilot.selfdrive.car import create_button_events, get_safety_config
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

    ret.steerControlType = car.CarParams.SteerControlType.angle
    ret.radarUnavailable = True

    if candidate == CAR.NISSAN_ALTIMA:
      # Altima has EPS on C-CAN unlike the others that have it on V-CAN
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_NISSAN_ALT_EPS_BUS

    return ret

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_adas, self.cp_cam)

    self.CS.button_events = create_button_events(self.CS.distance_button, self.CS.prev_distance_button, {1: ButtonType.gapAdjustCruise})

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        self.CS.madsEnabled = self.get_acc_mads(ret, self.CS.madsEnabled)
    else:
      self.CS.madsEnabled = False

    if (not ret.cruiseState.enabled and self.CS.out.cruiseState.enabled) or \
       self.get_sp_pedal_disengage(ret):
      self.get_sp_cancel_cruise_state()
      ret.cruiseState.enabled = ret.cruiseState.enabled if not self.enable_mads else False if self.CP.pcmCruise else self.CS.accEnabled

    ret = self.get_sp_common_state(ret)

    ret.buttonEvents = [
      *self.CS.button_events,
      *self.button_events.create_cancel_event(ret.cruiseState.enabled, self.CS.out.cruiseState.enabled),
      *self.button_events.create_mads_event(self.CS.madsEnabled, self.CS.out.madsEnabled)  # MADS BUTTON
    ]

    events = self.create_common_events(ret, c, extra_gears=[GearShifter.sport, GearShifter.low, GearShifter.brake],
                                       pcm_enable=False)

    events, ret = self.create_sp_events(ret, events)

    if self.CS.lkas_enabled:
      events.add(car.CarEvent.EventName.invalidLkasSetting)

    ret.events = events.to_msg()

    return ret
