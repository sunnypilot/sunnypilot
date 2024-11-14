from cereal import car, log, custom

from openpilot.sunnypilot.mads.helpers import MadsParams
from openpilot.sunnypilot.mads.state import StateMachine

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
ButtonType = car.CarState.ButtonEvent.Type
EventName = log.OnroadEvent.EventName


class ModifiedAssistDrivingSystem:
  def __init__(self, selfdrive):
    mads_params = MadsParams()

    self.enabled = False
    self.active = False
    self.available = False
    self.selfdrive = selfdrive
    self.selfdrive.enabled_prev = False
    self.selfdrive.active_prev = False
    self.state_machine = StateMachine(self)

    # TODO-SP: do we need to pass the params object from SelfdriveD?
    self.enabled_toggle = mads_params.read_param("Mads", self.selfdrive.params)
    self.main_enabled_toggle = mads_params.read_param("MadsCruiseMain", self.selfdrive.params)
    self.disengage_lateral_on_brake_toggle = mads_params.read_param("MadsDisengageLateralOnBrake", self.selfdrive.params)
    self.unified_engagement_mode = mads_params.read_param("MadsUnifiedEngagementMode", self.selfdrive.params)

  def update_availability(self, CS: car.CarState, available: bool = False) -> None:
    if self.main_enabled_toggle:
      available |= CS.cruiseState.available

    if self.selfdrive.CP.carName == "hyundai":
      if any(be.type == ButtonType.lkas and be.pressed for be in CS.buttonEvents):
        available = True

    self.available = available

  def update_events(self, CS: car.CarState):
    self.selfdrive.events.remove(EventName.pcmDisable)
    self.selfdrive.events.remove(EventName.buttonCancel)

    if self.selfdrive.enabled_prev:
      if self.selfdrive.events.has(EventName.wrongGear) and CS.vEgo < 5:
        self.selfdrive.events.add(EventName.silentWrongGear)
        self.selfdrive.events.remove(EventName.wrongGear)

    else:
      self.selfdrive.events.remove(EventName.wrongCruiseMode)
      self.selfdrive.events.remove(EventName.wrongCarMode)

    if self.disengage_lateral_on_brake_toggle:
      if self.selfdrive.events.has(EventName.brakeHold):
        self.selfdrive.events.remove(EventName.brakeHold)
        self.selfdrive.events.add(EventName.silentBrakeHold)

      if self.selfdrive.events.has(EventName.pedalPressed):
        self.selfdrive.events.add(EventName.silentPedalPressed)

      if not CS.brakePressed and not CS.brakeHoldActive and not CS.parkingBrake and not CS.regenBraking:
        if self.state_machine.state == State.paused and self.active:
          self.selfdrive.events.add(EventName.silentLkasEnable)

    if (self.unified_engagement_mode and self.active) or not self.unified_engagement_mode:
      if self.selfdrive.events.has(EventName.pcmEnable):
        self.selfdrive.events.remove(EventName.pcmEnable)
      if self.selfdrive.events.has(EventName.buttonEnable):
        self.selfdrive.events.remove(EventName.buttonEnable)

    if self.main_enabled_toggle:
      if self.selfdrive.CP.pcmCruise:
        if CS.cruiseState.available and not self.selfdrive.CS_prev.cruiseState.available:
          self.selfdrive.events.add(EventName.lkasEnable)
      else:
        if any(be.type == ButtonType.mainCruise and not be.pressed for be in CS.buttonEvents):
          self.selfdrive.events.add(EventName.lkasEnable)

    for be in CS.buttonEvents:
      if be.type == ButtonType.cancel:
        if self.selfdrive.enabled_prev:
          self.selfdrive.events.add(EventName.manualLongitudinalRequired)
      if be.type == ButtonType.lkas and be.pressed:
        if self.active:
          if self.selfdrive.enabled_prev:
            self.selfdrive.events.add(EventName.manualSteeringRequired)
          else:
            self.selfdrive.events.add(EventName.lkasDisable)
        else:
          if not self.selfdrive.enabled_prev:
            self.selfdrive.events.add(EventName.lkasEnable)

    self.selfdrive.events.remove(EventName.pedalPressed)

  def update(self, CS: car.CarState):
    if not self.enabled_toggle:
      return

    self.update_availability(CS)

    self.update_events(CS)

    if not self.selfdrive.CP.passive and self.selfdrive.initialized:
      self.enabled, self.active = self.state_machine.update(self.selfdrive.events)

    # Copy of previous SelfdriveD states for MADS events handling
    self.selfdrive.enabled_prev, self.selfdrive.active_prev = self.selfdrive.enabled, self.selfdrive.active
