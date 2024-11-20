from cereal import log, custom
from openpilot.selfdrive.selfdrived.events import ET, Events
from openpilot.selfdrive.selfdrived.state import SOFT_DISABLE_TIME
from openpilot.common.realtime import DT_CTRL

State = custom.SelfdriveStateSP.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState
EventName = log.OnroadEvent.EventName

ACTIVE_STATES = (State.enabled, State.softDisabling, State.overriding)
ENABLED_STATES = (State.paused, *ACTIVE_STATES)

GEARS_ALLOW_PAUSED_SILENT = [EventName.silentWrongGear, EventName.silentReverseGear, EventName.silentBrakeHold]
GEARS_ALLOW_PAUSED = [EventName.wrongGear, EventName.reverseGear, EventName.brakeHold, *GEARS_ALLOW_PAUSED_SILENT]
ALLOW_PAUSED = [EventName.silentPedalPressed, *GEARS_ALLOW_PAUSED]


class StateMachine:
  def __init__(self, mads):
    self.selfdrive = mads.selfdrive
    self.ss_state_machine = mads.selfdrive.state_machine

    self.state = State.disabled

  def add_current_alert_types(self, alert_type):
    if not self.selfdrive.enabled:
      self.ss_state_machine.current_alert_types.append(alert_type)

  def update(self, events: Events):
    # soft disable timer and current alert types are from the state machine of openpilot
    # decrement the soft disable timer at every step, as it's reset on
    # entrance in SOFT_DISABLING state

    # ENABLED, SOFT DISABLING, PAUSED, OVERRIDING
    if self.state != State.disabled:
      # user and immediate disable always have priority in a non-disabled state
      if events.contains(ET.USER_DISABLE):
        if events.has(EventName.silentLkasDisable) or events.has(EventName.silentPedalPressed) or \
           events.has(EventName.silentBrakeHold):
          self.state = State.paused
        else:
          self.state = State.disabled
        self.ss_state_machine.current_alert_types.append(ET.USER_DISABLE)

      elif events.contains(ET.IMMEDIATE_DISABLE):
        self.state = State.disabled
        self.add_current_alert_types(ET.IMMEDIATE_DISABLE)

      else:
        # ENABLED
        if self.state == State.enabled:
          if events.contains(ET.SOFT_DISABLE):
            self.state = State.softDisabling
            if not self.selfdrive.enabled:
              self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
              self.ss_state_machine.current_alert_types.append(ET.SOFT_DISABLE)

          elif events.contains(ET.OVERRIDE_LATERAL):
            self.state = State.overriding
            self.add_current_alert_types(ET.OVERRIDE_LATERAL)

        # SOFT DISABLING
        elif self.state == State.softDisabling:
          if not events.contains(ET.SOFT_DISABLE):
            # no more soft disabling condition, so go back to ENABLED
            self.state = State.enabled

          elif self.ss_state_machine.soft_disable_timer > 0:
            self.add_current_alert_types(ET.SOFT_DISABLE)

          elif self.ss_state_machine.soft_disable_timer <= 0:
            self.state = State.disabled

        # PAUSED
        elif self.state == State.paused:
          if events.contains(ET.ENABLE):
            if events.contains(ET.NO_ENTRY):
              self.add_current_alert_types(ET.NO_ENTRY)

            else:
              if events.contains(ET.OVERRIDE_LATERAL):
                self.state = State.overriding
              else:
                self.state = State.enabled
              self.add_current_alert_types(ET.ENABLE)

        # OVERRIDING
        elif self.state == State.overriding:
          if events.contains(ET.SOFT_DISABLE):
            self.state = State.softDisabling
            if not self.selfdrive.enabled:
              self.ss_state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)
              self.ss_state_machine.current_alert_types.append(ET.SOFT_DISABLE)
          elif not events.contains(ET.OVERRIDE_LATERAL):
            self.state = State.enabled
          else:
            self.ss_state_machine.current_alert_types += [ET.OVERRIDE_LATERAL]

    # DISABLED
    elif self.state == State.disabled:
      if events.contains(ET.ENABLE):
        if events.contains(ET.NO_ENTRY):
          if events.has_list(ALLOW_PAUSED):
            self.state = State.paused
          self.add_current_alert_types(ET.NO_ENTRY)

        else:
          if events.contains(ET.OVERRIDE_LATERAL):
            self.state = State.overriding
          else:
            self.state = State.enabled
          self.add_current_alert_types(ET.ENABLE)

    # check if MADS is engaged and actuators are enabled
    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES
    if active:
      self.add_current_alert_types(ET.WARNING)

    return enabled, active
