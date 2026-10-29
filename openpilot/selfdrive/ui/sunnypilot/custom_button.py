"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
from enum import IntEnum

from opendbc.car.structs import car
from openpilot.selfdrive.ui.ui_state import ui_state

ALT_BUTTON_2_BIT = int(car.CarState.ButtonEvent.Type.altButton2)


class CustomButtonAction(IntEnum):
  NONE = 0
  BOOKMARK = 1
  CYCLE_UI = 3


class CustomButton:
  """Runs the selected action on each custom button release, read from selfdriveStateSP.buttonsReleaseToggle."""
  def __init__(self, callbacks: dict[int, Callable[[], None]]):
    self._callbacks = callbacks
    self._prev_toggle: int | None = None

  def update(self) -> None:
    if not (ui_state.started and ui_state.has_custom_button):
      self._prev_toggle = None
      return

    toggle = ui_state.sm["selfdriveStateSP"].buttonsReleaseToggle
    released = self._prev_toggle is not None and (self._prev_toggle ^ toggle) >> ALT_BUTTON_2_BIT & 1
    self._prev_toggle = toggle

    # unknown values (e.g. a removed option) map to no callback
    if released and (callback := self._callbacks.get(ui_state.params.get("HyundaiCustomButtonAction", return_default=True))):
      callback()
