"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.sunnypilot.selfdrive.car.button_hold_tracker import ButtonHoldTracker, ButtonType, EventName

DISTANCE_LONG_PRESS = 50


class ExperimentalSwitcher:
  def __init__(self, params, button_type=ButtonType.gapAdjustCruise):
    self.params = params
    self.button_type = button_type
    self._button_tracker = ButtonHoldTracker()
    self.experimental_mode_switched = False  # Meant to be toggled off by this class's children.

  def update(self, CS, events, experimental_mode):
    self._button_tracker.update(CS)
    if CS.cruiseState.available:
      self.update_mode(events, experimental_mode)

  def update_mode(self, events, experimental_mode) -> None:
    if self._button_tracker.get_hold_duration(self.button_type) >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      experimental_mode = not experimental_mode
      self.params.put_bool_nonblocking("ExperimentalMode", experimental_mode)
      events.add(EventName.experimentalModeSwitched)
      self.experimental_mode_switched = True
