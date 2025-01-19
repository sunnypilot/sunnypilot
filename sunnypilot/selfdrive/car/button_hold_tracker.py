"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, log
ButtonType = car.CarState.ButtonEvent.Type
EventName = log.OnroadEvent.EventName


class ButtonHoldTracker:
  def __init__(self):
    self.button_frame_counts = {}

  def update(self, CS) -> None:
    if CS.cruiseState.available:
      self.update_button_timers(CS)

  def update_button_timers(self, CS) -> None:
    for button_type, held_frames in self.button_frame_counts.items():
      if held_frames > 0:
        self.button_frame_counts[button_type] += 1

    for event in CS.buttonEvents:
      event_type = event.type.raw
      if not (event.pressed and self.button_frame_counts.get(event_type, 0) > 0):  # No need to reset if the button is "pulsing" always "pressed"
        self.button_frame_counts[event_type] = int(event.pressed)

  def get_hold_duration(self, button_type):
    return self.button_frame_counts.get(button_type, 0)
