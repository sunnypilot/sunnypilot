from cereal import car, log, custom

from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

from openpilot.sunnypilot.mads.helpers import MadsParams
from openpilot.sunnypilot.mads.state import StateMachine

State = custom.SelfdriveStateSP.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState
ButtonType = car.CarState.ButtonEvent.Type
EventName = log.OnroadEvent.EventName


class ModularAssistiveDrivingSystem:
  def __init__(self, selfdrive):
    mads_params = MadsParams()

    self.enabled = False
    self.active = False
    self.available = False
    self.allow_always = False
    self.selfdrive = selfdrive
    self.selfdrive.enabled_prev = False
    self.state_machine = StateMachine(self)

    if self.selfdrive.CP.carName == "hyundai":
      if (self.selfdrive.CP.sunnyParams.flags & HyundaiFlagsSP.HAS_LFA_BUTTON) or \
            (self.selfdrive.CP.flags & HyundaiFlags.CANFD):
        self.allow_always = True

    self.enabled_toggle = mads_params.read_param("Mads")
    self.main_enabled_toggle = mads_params.read_param("MadsCruiseMain")
    self.disengage_lateral_on_brake_toggle = mads_params.read_param("MadsDisengageLateralOnBrake")
    self.unified_engagement_mode = mads_params.read_param("MadsUnifiedEngagementMode")

  def update_events(self, CS: car.CarState):
    def update_unified_engagement_mode():
      if (self.unified_engagement_mode and self.active) or not self.unified_engagement_mode:
        self.selfdrive.events.remove(EventName.pcmEnable)
        self.selfdrive.events.remove(EventName.buttonEnable)

    def update_silent_lkas_enable():
      if self.state_machine.state == State.paused and self.active:
        self.selfdrive.events.add(EventName.silentLkasEnable)

    if not self.selfdrive.enabled:
      if self.selfdrive.events.has(EventName.wrongGear) and not self.selfdrive.events.has(EventName.reverseGear):
        self.selfdrive.events.replace(EventName.wrongGear, EventName.silentWrongGear)
      if self.selfdrive.events.has(EventName.reverseGear) and CS.vEgo < 5:
        self.selfdrive.events.replace(EventName.reverseGear, EventName.silentReverseGear)

      if not self.selfdrive.events.has(EventName.silentWrongGear) and not self.selfdrive.events.has(EventName.silentReverseGear):
        update_silent_lkas_enable()

    if self.disengage_lateral_on_brake_toggle:
      if self.selfdrive.events.has(EventName.brakeHold):
        self.selfdrive.events.replace(EventName.brakeHold, EventName.silentBrakeHold)

      if self.selfdrive.events.has(EventName.pedalPressed):
        self.selfdrive.events.add(EventName.silentPedalPressed)

      if not CS.brakePressed and not CS.brakeHoldActive and not CS.parkingBrake and not CS.regenBraking:
        update_silent_lkas_enable()

    if self.selfdrive.events.has(EventName.pcmEnable) or self.selfdrive.events.has(EventName.buttonEnable):
      update_unified_engagement_mode()
    else:
      if self.main_enabled_toggle:
        if CS.cruiseState.available and not self.selfdrive.CS_prev.cruiseState.available:
          self.selfdrive.events.add(EventName.lkasEnable)

    for be in CS.buttonEvents:
      if be.type == ButtonType.cancel:
        if not self.selfdrive.enabled and self.selfdrive.enabled_prev:
          self.selfdrive.events.add(EventName.manualLongitudinalRequired)
      if be.type == ButtonType.lkas and be.pressed and (CS.cruiseState.available or self.allow_always):
        if self.active:
          if self.selfdrive.enabled:
            self.selfdrive.events.add(EventName.manualSteeringRequired)
          else:
            self.selfdrive.events.add(EventName.lkasDisable)
        else:
          self.selfdrive.events.add(EventName.lkasEnable)

    if not CS.cruiseState.available:
      self.selfdrive.events.remove(EventName.buttonEnable)
      if self.selfdrive.CS_prev.cruiseState.available:
        self.selfdrive.events.add(EventName.lkasDisable)

    self.selfdrive.events.remove(EventName.pcmDisable)
    self.selfdrive.events.remove(EventName.buttonCancel)
    self.selfdrive.events.remove(EventName.pedalPressed)
    self.selfdrive.events.remove(EventName.wrongCruiseMode)
    self.selfdrive.events.remove(EventName.wrongCarMode)

  def update(self, CS: car.CarState):
    if not self.enabled_toggle:
      return

    self.update_events(CS)

    if not self.selfdrive.CP.passive and self.selfdrive.initialized:
      self.enabled, self.active = self.state_machine.update(self.selfdrive.events)

    # Copy of previous SelfdriveD states for MADS events handling
    self.selfdrive.enabled_prev = self.selfdrive.enabled
