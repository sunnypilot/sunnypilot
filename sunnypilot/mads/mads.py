from cereal import car, log, custom

from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

from openpilot.sunnypilot.mads.helpers import MadsParams
from openpilot.sunnypilot.mads.state import StateMachine, GEARS_ALLOW_PAUSED_SILENT

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
    self.events = self.selfdrive.events

    if self.selfdrive.CP.carName == "hyundai":
      if (self.selfdrive.CP.sunnypilotFlags & HyundaiFlagsSP.HAS_LFA_BUTTON) or \
            (self.selfdrive.CP.flags & HyundaiFlags.CANFD):
        self.allow_always = True

    self.enabled_toggle = mads_params.read_param("Mads")
    self.main_enabled_toggle = mads_params.read_param("MadsCruiseMain")
    self.disengage_lateral_on_brake_toggle = mads_params.read_param("MadsDisengageLateralOnBrake")
    self.unified_engagement_mode = mads_params.read_param("MadsUnifiedEngagementMode")

  def update_events(self, CS: car.CarState):
    def update_unified_engagement_mode():
      if (self.unified_engagement_mode and self.enabled) or not self.unified_engagement_mode:
        self.events.remove(EventName.pcmEnable)
        self.events.remove(EventName.buttonEnable)

    def transition_paused_state():
      if self.state_machine.state != State.paused:
        self.events.add(EventName.silentLkasDisable)

    if not self.selfdrive.enabled and self.enabled:
      if self.events.has(EventName.wrongGear):
        self.events.replace(EventName.wrongGear, EventName.silentWrongGear)
        transition_paused_state()
      if self.events.has(EventName.reverseGear):
        self.events.replace(EventName.reverseGear, EventName.silentReverseGear)
        transition_paused_state()
      if self.events.has(EventName.brakeHold):
        self.events.replace(EventName.brakeHold, EventName.silentBrakeHold)
        transition_paused_state()
      if self.events.has(EventName.doorOpen):
        self.events.replace(EventName.doorOpen, EventName.silentDoorOpen)
        transition_paused_state()
      if self.events.has(EventName.seatbeltNotLatched):
        self.events.replace(EventName.seatbeltNotLatched, EventName.silentSeatbeltNotLatched)
        transition_paused_state()
      if self.events.has(EventName.parkBrake):
        self.events.replace(EventName.parkBrake, EventName.silentParkBrake)
        transition_paused_state()

      if self.disengage_lateral_on_brake_toggle:
        if self.events.has(EventName.pedalPressed):
          transition_paused_state()

      if not (self.disengage_lateral_on_brake_toggle and self.events.has(EventName.pedalPressed)) and \
         not self.events.contains_in_list(GEARS_ALLOW_PAUSED_SILENT):
        if self.state_machine.state == State.paused:
          self.events.add(EventName.silentLkasEnable)

    if self.events.has(EventName.pcmEnable) or self.events.has(EventName.buttonEnable):
      update_unified_engagement_mode()
    else:
      if self.main_enabled_toggle:
        if CS.cruiseState.available and not self.selfdrive.CS_prev.cruiseState.available:
          self.events.add(EventName.lkasEnable)

    for be in CS.buttonEvents:
      if be.type == ButtonType.cancel:
        if not self.selfdrive.enabled and self.selfdrive.enabled_prev:
          self.events.add(EventName.manualLongitudinalRequired)
      if be.type == ButtonType.lkas and be.pressed and (CS.cruiseState.available or self.allow_always):
        if self.enabled:
          if self.selfdrive.enabled:
            self.events.add(EventName.manualSteeringRequired)
          else:
            self.events.add(EventName.lkasDisable)
        else:
          self.events.add(EventName.lkasEnable)

    if not CS.cruiseState.available:
      self.events.remove(EventName.buttonEnable)
      if self.selfdrive.CS_prev.cruiseState.available:
        self.events.add(EventName.lkasDisable)

    self.events.remove(EventName.pcmDisable)
    self.events.remove(EventName.buttonCancel)
    self.events.remove(EventName.pedalPressed)
    self.events.remove(EventName.wrongCruiseMode)
    self.events.remove(EventName.wrongCarMode)

  def update(self, CS: car.CarState):
    if not self.enabled_toggle:
      return

    self.update_events(CS)

    if not self.selfdrive.CP.passive and self.selfdrive.initialized:
      self.enabled, self.active = self.state_machine.update(self.events)

    # Copy of previous SelfdriveD states for MADS events handling
    self.selfdrive.enabled_prev = self.selfdrive.enabled
