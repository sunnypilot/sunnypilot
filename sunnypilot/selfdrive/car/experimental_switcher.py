"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, log

ButtonType = car.CarState.ButtonEvent.Type
EventName = log.OnroadEvent.EventName

DISTANCE_LONG_PRESS = 50


class ExperimentalSwitcher:
  def __init__(self, params):
    self.params = params

    self.button_timers = {ButtonType.gapAdjustCruise: 0}
    self.experimental_mode_switched = False

  def update(self, CS, events, experimental_mode):
    if CS.cruiseState.available:
      self.update_button_timers(CS)
      self.update_mode(events, experimental_mode)

  def update_button_timers(self, CS) -> None:
    for k in self.button_timers:
      if self.button_timers[k] > 0:
        self.button_timers[k] += 1

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers:
        self.button_timers[b.type.raw] = 1 if b.pressed else 0

  def update_mode(self, events, experimental_mode) -> None:
    if self.button_timers[ButtonType.gapAdjustCruise] >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      experimental_mode = not experimental_mode
      self.params.put_bool_nonblocking("ExperimentalMode", experimental_mode)
      events.add(EventName.experimentalModeSwitched)
      self.experimental_mode_switched = True
