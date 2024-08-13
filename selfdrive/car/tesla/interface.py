#!/usr/bin/env python3
from cereal import car
from panda import Panda
from openpilot.selfdrive.car.tesla.values import CAR
from openpilot.selfdrive.car import get_safety_config
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

ButtonType = car.CarState.ButtonEvent.Type


class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "tesla"

    # There is no safe way to do steer blending with user torque,
    # so the steering behaves like autopilot. This is not
    # how openpilot should be, hence dashcamOnly
    # ret.dashcamOnly = True

    ret.steerControlType = car.CarParams.SteerControlType.angle

    ret.longitudinalActuatorDelay = 0.5 # s
    ret.radarUnavailable = True

    if candidate in [CAR.TESLA_AP3_MODEL3, CAR.TESLA_AP3_MODELY]:
      flags = Panda.FLAG_TESLA_MODEL3_Y
      flags |= Panda.FLAG_TESLA_LONG_CONTROL
      ret.openpilotLongitudinalControl = True
      ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.tesla, flags)]
      ret.enableBsm = True

    ret.steerLimitTimer = 1.0
    ret.steerActuatorDelay = 0.25
    return ret

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam, self.cp_adas)

    if ret.cruiseState.available:
      if self.enable_mads:
        for b in self.CS.button_events:
          if b.type == ButtonType.altButton1 and b.pressed:
            self.CS.madsEnabled = True
          elif b.type == ButtonType.altButton2 and b.pressed:
            self.CS.madsEnabled = False
        self.CS.madsEnabled = self.get_acc_mads(ret.cruiseState.enabled, self.CS.accEnabled, self.CS.madsEnabled)
        self.CS.madsEnabled = False if self.CS.steer_warning == "EAC_ERROR_HANDS_ON" and self.CS.hands_on_level >= 3 else self.CS.madsEnabled
    else:
      self.CS.madsEnabled = False

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0) or not self.CP.pcmCruiseSpeed:
      if any(b.type == ButtonType.cancel for b in self.CS.button_events):
        self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
    if self.get_sp_pedal_disengage(ret):
      self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
      ret.cruiseState.enabled = ret.cruiseState.enabled if not self.enable_mads else False if self.CP.pcmCruise else self.CS.accEnabled

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.CS.accEnabled = False
      self.CS.accEnabled = ret.cruiseState.enabled or self.CS.accEnabled

    ret, self.CS = self.get_sp_common_state(ret, self.CS)

    ret.buttonEvents = [
      *self.CS.button_events,
      *self.button_events.create_mads_event(self.CS.madsEnabled, self.CS.out.madsEnabled)  # MADS BUTTON
    ]

    events = self.create_common_events(ret, c, pcm_enable=False)

    events, ret = self.create_sp_events(self.CS, ret, events)

    ret.events = events.to_msg()

    return ret
