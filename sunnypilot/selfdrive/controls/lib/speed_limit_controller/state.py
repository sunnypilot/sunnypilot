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
    # INACTIVE
    if self.state == State.inactive:
      if events_sp.has(EventNameSP.speedLimitEnable):
        self.state = State.preActive
      elif events_sp.has(EventNameSP.speedLimitAdapting):
        self.state = State.adapting
      elif events_sp.has(EventNameSP.speedLimitActive):
        self.state = State.active

    # PRE ACTIVE
    elif self.state == State.preActive:
      if events_sp.has(EventNameSP.speedLimitDisable):
        self.state = State.inactive
      elif events_sp.has(EventNameSP.speedLimitUserCancel):
        self.state = State.inactive
      elif events_sp.has(EventNameSP.speedLimitUserConfirm):
        self.state = State.active
      elif events_sp.has(EventNameSP.speedLimitActive):
        self.state = State.active

    # ACTIVE
    elif self.state == State.active:
      if events_sp.has(EventNameSP.speedLimitDisable):
        self.state = State.inactive
      elif events_sp.has(EventNameSP.speedLimitUserCancel):
        self.state = State.tempInactive
      elif events_sp.has(EventNameSP.speedLimitAdapting):
        self.state = State.adapting
      elif events_sp.has(EventNameSP.speedLimitValueChange):
        # For user confirm mode, transition to preActive on speed limit change
        if events_sp.has(EventNameSP.speedLimitEnable):
          self.state = State.preActive

    # ADAPTING
    elif self.state == State.adapting:
      if events_sp.has(EventNameSP.speedLimitDisable):
        self.state = State.inactive
      elif events_sp.has(EventNameSP.speedLimitUserCancel):
        self.state = State.tempInactive
      elif events_sp.has(EventNameSP.speedLimitReached):
        self.state = State.active

    # TEMP INACTIVE
    elif self.state == State.tempInactive:
      if events_sp.has(EventNameSP.speedLimitDisable):
        self.state = State.inactive
      elif events_sp.has(EventNameSP.speedLimitValueChange):
        # When speed limit changes, reactivate
        if events_sp.has(EventNameSP.speedLimitEnable):
          self.state = State.preActive
        else:
          self.state = State.inactive

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES

    return enabled, active
