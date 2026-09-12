"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car import structs


class ButtonStateTracker:
  def __init__(self) -> None:
    self.pressed: int = 0
    self.release_toggle: int = 0

  def update(self, CS: structs.CarState) -> None:
    for b in CS.buttonEvents:
      bit = 1 << b.type.raw
      if b.pressed:
        self.pressed |= bit
      else:
        self.pressed &= ~bit
        self.release_toggle ^= bit

  def publish(self, ss_sp) -> None:
    ss_sp.buttonsPressed = self.pressed
    ss_sp.buttonsReleaseToggle = self.release_toggle
