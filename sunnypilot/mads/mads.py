from cereal import car, custom

from panda import ALTERNATIVE_EXPERIENCE

from openpilot.sunnypilot.mads.state import StateMachine

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
ButtonType = car.CarState.ButtonEvent.Type
EventName = car.OnroadEvent.EventName


class ModifiedAssistDrivingSystem:
  def __init__(self, selfdrive=None):
    self.enabled = False
    self.active = False
    self.state_machine = StateMachine(self)

    if selfdrive is not None:
      self.selfdrive = selfdrive

    self.enabled_toggle = True  # TODO-SP: Apply with toggle
    self.main_enabled_toggle = True  # TODO-SP: Apply with toggle
    self.disengage_lateral_on_brake_toggle = False  # TODO-SP: Apply with toggle

    self.available = False
    self.mads_alt_button_enabled = False

  def set_alternative_experience(self, alt_experience: int = 0):
    alt_experience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS
    if not self.disengage_lateral_on_brake_toggle:
      alt_experience |= ALTERNATIVE_EXPERIENCE.DISABLE_DISENGAGE_LATERAL_ON_BRAKE

    return alt_experience

  def update_availability(self, CS: car.CarState, available: bool = False) -> bool:
    if self.main_enabled_toggle:
      available |= CS.cruiseState.available

    available |= self.mads_alt_button_enabled

    return available

  def update_events(self, CS: car.CarState):
    self.selfdrive.events.remove(EventName.pcmEnable)
    self.selfdrive.events.remove(EventName.pcmDisable)

    if self.selfdrive.enabled:
      if self.selfdrive.events.has(EventName.wrongGear) and CS.vEgo < 5:
        self.selfdrive.events.add(EventName.silentWrongGear)
        self.selfdrive.events.remove(EventName.wrongGear)

    if not self.selfdrive.enabled:
      self.selfdrive.events.remove(EventName.buttonEnable)
      self.selfdrive.events.remove(EventName.buttonCancel)
      self.selfdrive.events.remove(EventName.wrongCruiseMode)
      self.selfdrive.events.remove(EventName.wrongCarMode)

    if self.disengage_lateral_on_brake_toggle:
      if self.selfdrive.events.has(EventName.brakeHold):
        self.selfdrive.events.remove(EventName.brakeHold)
        self.selfdrive.events.add(EventName.silentBrakeHold)

      if self.selfdrive.events.has(EventName.pedalPressed):
        self.selfdrive.events.remove(EventName.pedalPressed)
        self.selfdrive.events.add(EventName.silentPedalPressed)

      if not CS.brakePressed and not CS.brakeHoldActive and not CS.parkingBrake and not CS.regenBraking:
        if self.current_state == State.paused and self.available:
          self.selfdrive.events.add(EventName.silentButtonEnable)

    for be in CS.buttonEvents:
      if be.type == ButtonType.cancel:
        if self.selfdrive.enabled:
          self.selfdrive.events.add(EventName.manualLongitudinalRequired)
      if be.type == ButtonType.altButton1 and be.pressed:
        if not self.available:
          if not self.selfdrive.enabled:
            self.selfdrive.events.add(EventName.buttonCancel)
          else:
            self.selfdrive.events.add(EventName.manualSteeringRequired)
        else:
          if not self.selfdrive.enabled:
            self.selfdrive.events.add(EventName.buttonEnable)

  def update(self, CS: car.CarState):
    if not self.enabled_toggle:
      return

    self.available = self.update_availability(CS)

    self.update_events(CS)

    if not self.selfdrive.CP.passive and self.selfdrive.initialized:
      self.enabled, self.active = self.state_machine.update(self.selfdrive.events)
