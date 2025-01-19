"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest

from cereal import car
from sunnypilot.selfdrive.car.button_hold_tracker import ButtonHoldTracker, ButtonType


@pytest.fixture
def setup_button_tracker():
  return ButtonHoldTracker()


class TestButtonHoldTracker:
  @pytest.mark.parametrize(
    "button_type, button_events, initial_timer, expected_timer",
    [
      # Basic button press scenarios
      (ButtonType.gapAdjustCruise, [car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=True)], 0, 1),
      (ButtonType.gapAdjustCruise, [car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=False)], 1, 0),

      # Auto-increment when already held
      (ButtonType.gapAdjustCruise, [], 5, 6),
      (ButtonType.cancel, [], 10, 11),
      (ButtonType.leftBlinker, [], 1, 2),

      # Multiple button events in same frame
      (ButtonType.gapAdjustCruise,
       [
         car.CarState.ButtonEvent(type=ButtonType.cancel, pressed=True),
         car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=False)
       ], 0, 0),

      # Events for different buttons shouldn't affect each other
      (ButtonType.gapAdjustCruise, [car.CarState.ButtonEvent(type=ButtonType.cancel, pressed=True)], 5, 6),

      # Press while already held (like if it was pulsing the event for some reason)
      (ButtonType.cancel, [car.CarState.ButtonEvent(type=ButtonType.cancel, pressed=True)], 5, 6),

      # Edge cases
      (ButtonType.leftBlinker, [], 0, 0),
      (ButtonType.cancel, [car.CarState.ButtonEvent(type=ButtonType.cancel, pressed=False)], 0, 0),
    ],
    ids=[
      "initial_button_press",
      "button_release",
      "increment_held_gap_adjust",
      "increment_held_cancel",
      "increment_held_blinker",
      "multiple_events_same_frame",
      "different_button_no_effect",
      "press_while_held",
      "zero_state_no_events",
      "release_when_not_held"
    ]
  )
  def test_update_button_timers(self, mocker, setup_button_tracker, button_type, button_events, initial_timer, expected_timer):
    tracker = setup_button_tracker
    mock_CS = mocker.Mock(buttonEvents=button_events, cruiseState=mocker.Mock(available=True))

    if initial_timer > 0:
      tracker.button_frame_counts[button_type] = initial_timer

    tracker.update(mock_CS)
    timer_value = tracker.get_hold_duration(button_type)
    assert timer_value == expected_timer, f"Expected timer for {button_type} to be {expected_timer}, but got {timer_value}"

  def test_cruise_state_unavailable(self, mocker, setup_button_tracker):
    tracker = setup_button_tracker
    mock_CS = mocker.Mock(
      buttonEvents=[car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=True)],
      cruiseState=mocker.Mock(available=False)
    )

    tracker.update(mock_CS)
    assert tracker.get_hold_duration(ButtonType.gapAdjustCruise) == 0
