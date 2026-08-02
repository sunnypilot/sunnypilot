"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.structs import car
from openpilot.sunnypilot.selfdrive.selfdrived.button_state_tracker import ButtonStateTracker

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type


class TestButtonStateTracker:
  def setup_method(self) -> None:
    self.tracker = ButtonStateTracker()

  def make_cs(self, events: list) -> car.CarState:
    CS = car.CarState()
    CS.buttonEvents = events
    return CS

  def test_initial_state(self) -> None:
    assert self.tracker.pressed == 0
    assert self.tracker.release_toggle == 0

  def test_press_sets_bit(self) -> None:
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=True)]))
    assert self.tracker.pressed == (1 << ButtonType.accelCruise)
    assert self.tracker.release_toggle == 0

  def test_release_clears_and_toggles(self) -> None:
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=True)]))
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=False)]))
    assert self.tracker.pressed == 0
    assert self.tracker.release_toggle == (1 << ButtonType.accelCruise)

  def test_multiple_buttons(self) -> None:
    self.tracker.update(self.make_cs([
      ButtonEvent(type=ButtonType.accelCruise, pressed=True),
      ButtonEvent(type=ButtonType.decelCruise, pressed=True),
    ]))
    assert self.tracker.pressed == (1 << ButtonType.accelCruise) | (1 << ButtonType.decelCruise)

    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=False)]))
    assert self.tracker.pressed == (1 << ButtonType.decelCruise)
    assert self.tracker.release_toggle == (1 << ButtonType.accelCruise)

  def test_release_toggle_flips(self) -> None:
    for _ in range(2):
      self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=True)]))
      self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=False)]))
    assert self.tracker.release_toggle == 0

  def test_publish(self) -> None:
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=True)]))
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.decelCruise, pressed=True)]))
    self.tracker.update(self.make_cs([ButtonEvent(type=ButtonType.accelCruise, pressed=False)]))

    class MockSP:
      buttonsPressed = 0
      buttonsReleaseToggle = 0

    sp = MockSP()
    self.tracker.publish(sp)
    assert sp.buttonsPressed == self.tracker.pressed
    assert sp.buttonsReleaseToggle == self.tracker.release_toggle
