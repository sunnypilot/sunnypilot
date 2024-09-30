from abc import ABC, abstractmethod

from cereal import car, custom
from openpilot.selfdrive.selfdrived.events import ET, Events
from openpilot.selfdrive.selfdrived.state import SOFT_DISABLE_TIME
from openpilot.common.realtime import DT_CTRL

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
EventName = car.OnroadEvent.EventName

ENABLED_STATES = (State.enabled, State.softDisabling, State.overriding)
ACTIVE_STATES = (State.paused, *ENABLED_STATES)


class StateMachineBase(ABC):
  def __init__(self, mads):
    self.mads = mads
    self.selfdrive = mads.selfdrive
    self.ss_state_machine = mads.selfdrive.state_machine

    self.state = State.disabled

  def __call__(self, events: Events) -> tuple[State, bool, bool]:
    if self.state != State.disabled:
      if events.contains(ET.USER_DISABLE):
        if events.has(EventName.silentPedalPressed) or events.has(EventName.silentBrakeHold):
          self.state = State.paused
        else:
          self.state = State.disabled
        self.add_current_alert_types(ET.USER_DISABLE)

      elif events.contains(ET.IMMEDIATE_DISABLE):
        self.state = State.disabled
        self.add_current_alert_types(ET.IMMEDIATE_DISABLE)

      else:
        self.handle(events)

    elif self.state == State.disabled:
      self.handle(events)

    enabled = self.state in ENABLED_STATES and self.mads.available
    active = self.state in ACTIVE_STATES and self.mads.available
    if active:
      self.add_current_alert_types(ET.WARNING)

    return self.state, enabled, active

  @abstractmethod
  def handle(self, events: Events):
    pass

  def add_current_alert_types(self, alert_type):
    if not self.selfdrive.active:
      self.ss_state_machine.current_alert_types.append(alert_type)


class InactiveBase(StateMachineBase):
  def handle(self, events: Events):
    if events.contains(ET.ENABLE):
      if events.contains(ET.NO_ENTRY):
        self.add_current_alert_types(ET.NO_ENTRY)

      else:
        if events.contains(ET.OVERRIDE_LATERAL):
          self.state = State.overriding
        else:
          self.state = State.enabled
        self.add_current_alert_types(ET.ENABLE)


class Disabled(InactiveBase):
  pass


class Paused(InactiveBase):
  pass


class Enabled(StateMachineBase):
  def handle(self, events: Events):
    if events.contains(ET.SOFT_DISABLE):
      self.state = State.softDisabling
      if not self.selfdrive.active:
        self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
        self.ss_state_machine.current_alert_types.append(ET.SOFT_DISABLE)

    elif events.contains(ET.OVERRIDE_LATERAL):
      self.state = State.overriding
      self.add_current_alert_types(ET.OVERRIDE_LATERAL)


class SoftDisabling(StateMachineBase):
  def handle(self, events: Events):
    if not events.contains(ET.SOFT_DISABLE):
      # no more soft disabling condition, so go back to ENABLED
      self.state = State.enabled

    elif self.ss_state_machine.soft_disable_timer > 0:
      self.add_current_alert_types(ET.SOFT_DISABLE)

    elif self.ss_state_machine.soft_disable_timer <= 0:
      self.state = State.disabled


class Overriding(StateMachineBase):
  def handle(self, events: Events):
    if events.contains(ET.SOFT_DISABLE):
      self.state = State.softDisabling
      if not self.selfdrive.active:
        self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
        self.ss_state_machine.current_alert_types.append(ET.SOFT_DISABLE)
    elif not events.contains(ET.OVERRIDE_LATERAL):
      self.state = State.enabled
    else:
      self.ss_state_machine.current_alert_types += [ET.OVERRIDE_LATERAL]
