from cereal import car, custom
from openpilot.sunnypilot.mads.state import Disabled, Paused, Enabled, SoftDisabling, Overriding

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
EventName = car.OnroadEvent.EventName


class ModifiedAssistDrivingSystem:
  def __init__(self, selfdrive):
    self.selfdrive = selfdrive

    self.CS_prev = car.CarState.new_message()
    self.current_state = State.disabled

    self.state_machine = {
      State.disabled: Disabled(self),
      State.paused: Paused(self),
      State.enabled: Enabled(self),
      State.softDisabling: SoftDisabling(self),
      State.overriding: Overriding(self),
    }

    self.enabled = True  # TODO-SP: Apply with toggle
    self.main_enabled = True  # TODO-SP: Apply with toggle
    self.disengage_lateral_on_brake = False  # TODO-SP: Apply with toggle

  def update_availability(self, CS: car.CarState):
    if not self.enabled:
      return False

    if self.current_state == State.disabled:
      return False

  def update_events(self, CS: car.CarState):
    pass

  def update(self, CS: car.CarState):
















    self.current_state = self.state_machine[self.current_state]()

    self.CS_prev = CS.as_reader()






























