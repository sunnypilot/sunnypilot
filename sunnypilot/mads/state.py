from abc import ABC, abstractmethod

from cereal import car, custom
from openpilot.selfdrive.selfdrived.events import ET
from openpilot.selfdrive.selfdrived.state import ACTIVE_STATES, SOFT_DISABLE_TIME
from openpilot.common.realtime import DT_CTRL

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
EventName = car.OnroadEvent.EventName


class StateMachineBase(ABC):
  def __init__(self, mads):
    self.mads = mads
    self.selfdrive = mads.selfdrive
    self.ss_state_machine = mads.ss_state_machine

    self.state = State.disabled

  def __call__(self) -> State:
    if self.state != State.disabled:
      if self.selfdrive.events.contains(ET.USER_DISABLE):
        if EventName.silentPedalPressed in self.selfdrive.events.events:
          self.state = State.paused
        else:
          self.state = State.disabled
        self.add_current_alert_types(ET.USER_DISABLE)
        return self.state

      elif self.selfdrive.events.contains(ET.IMMEDIATE_DISABLE):
        self.state = State.disabled
        self.add_current_alert_types(ET.IMMEDIATE_DISABLE)
        return self.state

    self.handle()

    if self.state in ACTIVE_STATES:
      self.add_current_alert_types(ET.WARNING)

    return self.state

  def add_current_alert_types(self, alert_type):
    if not self.selfdrive.active:
      self.add_current_alert_types(alert_type)

  @abstractmethod
  def handle(self):
    pass


class InactiveBase(StateMachineBase):
  def handle(self):
    if self.selfdrive.events.contain(ET.ENABLE):
      if self.selfdrive.events.contain(ET.NO_ENTRY):
        self.add_current_alert_types(ET.NO_ENTRY)

      else:
        if self.selfdrive.events.contain(ET.OVERRIDE_LATERAL):
          self.state = State.overriding
        else:
          self.state = State.enabled
        self.add_current_alert_types(ET.ENABLE)


class Disabled(InactiveBase):
  pass


class Paused(InactiveBase):
  pass


class Enabled(StateMachineBase):
  def handle(self):
    if self.selfdrive.events.contain(ET.SOFT_DISABLE):
      self.state = State.softDisabling
      if not self.selfdrive.active:
        self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
      self.add_current_alert_types(ET.SOFT_DISABLE)

    elif self.selfdrive.events.contains(ET.OVERRIDE_LATERAL):
      self.state = State.overriding
      self.add_current_alert_types(ET.OVERRIDE_LATERAL)


class SoftDisabling(StateMachineBase):
  def handle(self):
    if not self.selfdrive.events.contain(ET.SOFT_DISABLE):
      # no more soft disabling condition, so go back to ENABLED
      self.state = State.enabled

    elif self.ss_state_machine.soft_disable_timer > 0:
      self.add_current_alert_types(ET.SOFT_DISABLE)

    elif self.ss_state_machine.soft_disable_timer <= 0:
      self.state = State.disabled


class Overriding(StateMachineBase):
  def handle(self):
    if self.selfdrive.events.contain(ET.SOFT_DISABLE):
      self.state = State.softDisabling
      if not self.selfdrive.active:
        self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
      self.add_current_alert_types(ET.SOFT_DISABLE)
    elif not self.selfdrive.events.contain(ET.OVERRIDE_LATERAL):
      self.state = State.enabled
    else:
      self.ss_state_machine.current_alert_types += [ET.OVERRIDE_LATERAL]
