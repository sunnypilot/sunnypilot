"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, custom
from opendbc.car import structs

ButtonType = car.CarState.ButtonEvent.Type
EventNameSP = custom.OnroadEventSP.EventName

DISTANCE_LONG_PRESS = 50


class CruiseHelper:
  def __init__(self, CP: structs.CarParams, selfdrived):
    self.CP = CP
    self.selfdrived = selfdrived
    self.params = self.selfdrived.params

    self.button_frame_counts = {ButtonType.gapAdjustCruise: 0}
    self.experimental_mode_switched = False
    self.experimental_mode = self.selfdrived.experimental_mode
    self.dynamic_experimental_control = False

  def read_params(self):
    self.dynamic_experimental_control = self.params.get_bool("DynamicExperimentalControl")

  def update(self, CS, events) -> None:
    if self.CP.openpilotLongitudinalControl:
      if CS.cruiseState.available:
        self.update_button_frame_counts(CS)

        # toggle experimental mode once on distance button hold
        self.update_experimental_mode(events)

  def update_button_frame_counts(self, CS) -> None:
    for button in self.button_frame_counts:
      if self.button_frame_counts[button] > 0:
        self.button_frame_counts[button] += 1

    for button_event in CS.buttonEvents:
      button = button_event.type.raw
      if button in self.button_frame_counts:
        self.button_frame_counts[button] = int(button_event.pressed)

  def update_experimental_mode(self, events) -> None:
    if self.button_frame_counts[ButtonType.gapAdjustCruise] >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      if not self.experimental_mode and not self.dynamic_experimental_control:
        # State 1 -> 2: Turn on experimental mode only
        experimental_mode = True
        dynamic_experimental_control = False
      elif self.experimental_mode and not self.dynamic_experimental_control:
        # State 2 -> 3: Keep experimental mode on, turn on DEC
        experimental_mode = True
        dynamic_experimental_control = True
      else:
        # State 3 -> 1: Turn everything off, so back to chill mode
        experimental_mode = False
        dynamic_experimental_control = False

      self.params.put_bool_nonblocking("ExperimentalMode", experimental_mode)
      self.params.put_bool_nonblocking("DynamicExperimentalControl", dynamic_experimental_control)

      events.add(EventNameSP.experimentalModeSwitched)
      self.experimental_mode_switched = True
