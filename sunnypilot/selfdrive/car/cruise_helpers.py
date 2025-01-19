"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, log
from opendbc.car import structs
from openpilot.common.params import Params

ButtonType = car.CarState.ButtonEvent.Type
EventName = log.OnroadEvent.EventName

DISTANCE_LONG_PRESS = 50


class CruiseHelper:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.params = Params()

    self.button_timers = {ButtonType.gapAdjustCruise: 0}
    self._experimental_mode = False
    self.experimental_mode_switched = False

  def update(self, CS, events, experimental_mode) -> None:
    if self.CP.openpilotLongitudinalControl:
      if CS.cruiseState.available:
        self.update_button_timers(CS)

        # toggle experimental mode once on distance button hold
        self.update_experimental_mode(events, experimental_mode)

  def update_button_timers(self, CS) -> None:
    for k in self.button_timers:
      if self.button_timers[k] > 0:
        self.button_timers[k] += 1

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers:
        self.button_timers[b.type.raw] = 1 if b.pressed else 0

  def update_experimental_mode(self, events, experimental_mode) -> None:
    if self.button_timers[ButtonType.gapAdjustCruise] >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      self._experimental_mode = not experimental_mode
      self.params.put_bool_nonblocking("ExperimentalMode", self._experimental_mode)
      events.add(EventName.experimentalModeSwitched)
      self.experimental_mode_switched = True
