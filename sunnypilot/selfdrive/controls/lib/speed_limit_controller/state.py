"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName
State = custom.LongitudinalPlanSP.SpeedLimitControlState

ACTIVE_STATES = (State.active, State.adapting)
ENABLED_STATES = (State.preActive, State.tempInactive, *ACTIVE_STATES)


class StateMachine:
  def __init__(self):
    self.state = State.inactive

  def update(self, events_sp: EventsSP) -> tuple[bool, bool]:
    # TEMP INACTIVE, ADAPTING, ACTIVE, PRE ACTIVE
    if self.state != State.inactive:
      if events_sp.has(EventNameSP.speedLimitInactive):
        self.state = State.inactive

      elif events_sp.has(EventNameSP.speedLimitTempInactive):
        self.state = State.tempInactive

      else:
        # ACTIVE
        if self.state == State.active:
          if events_sp.has(EventNameSP.speedLimitTempInactive):
            self.state = State.tempInactive
          elif events_sp.has(EventNameSP.speedLimitPreActive):
            self.state = State.preActive
          elif events_sp.has(EventNameSP.speedLimitAdapting):
            self.state = State.adapting

        # PRE ACTIVE
        elif self.state == State.preActive:
          if events_sp.has(EventNameSP.speedLimitInactive):
            self.state = State.inactive
          elif events_sp.has(EventNameSP.speedLimitActive):
            self.state = State.active

        # ADAPTING
        elif self.state == State.adapting:
          if events_sp.has(EventNameSP.speedLimitActive):
            self.state = State.active

        # TEMP INACTIVE
        elif self.state == State.tempInactive:
          if events_sp.has(EventNameSP.speedLimitPreActive):
            self.state = State.preActive
          elif events_sp.has(EventNameSP.speedLimitInactive):
            self.state = State.inactive

    # INACTIVE
    elif self.state == State.inactive:
      if events_sp.has(EventNameSP.speedLimitPreActive):
        self.state = State.preActive
      elif events_sp.has(EventNameSP.speedLimitAdapting):
        self.state = State.adapting
      elif events_sp.has(EventNameSP.speedLimitActive):
        self.state = State.active

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES

    return enabled, active
