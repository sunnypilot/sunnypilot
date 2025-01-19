"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest

from cereal import car
from sunnypilot.selfdrive.car.experimental_switcher import ExperimentalSwitcher, ButtonType, EventName, DISTANCE_LONG_PRESS


@pytest.fixture
def setup_switcher(mocker):
  mock_params = mocker.Mock()
  return ExperimentalSwitcher(mock_params), mock_params


class TestExperimentalSwitcher:
  @pytest.mark.parametrize(
    "use_experimental_mode, long_press, expected_mode, expected_experimental_mode",
    [
      (False, True, True, True),  # Normal -> Experimental via long press
      (True, True, False, True),  # Experimental -> Normal via long press
      (False, False, False, False)  # No change without long press
    ],
    ids=[
      "enable_experimental_mode",
      "disable_experimental_mode",
      "no_mode_change_without_long_press"
    ]
  )
  def test_update_mode_switches(self, mocker, setup_switcher, use_experimental_mode, long_press, expected_mode, expected_experimental_mode):
    switcher, params = setup_switcher
    mock_events = mocker.Mock()
    mock_CS = mocker.Mock(
      buttonEvents=[car.CarState.ButtonEvent(type=ButtonType.gapAdjustCruise, pressed=True)],
      cruiseState=mocker.Mock(available=True)
    )

    if long_press:
      for _ in range(DISTANCE_LONG_PRESS + 1):
        switcher.update(mock_CS, mock_events, use_experimental_mode)

    switcher.update_mode(mock_events, use_experimental_mode)

    if expected_experimental_mode:
      params.put_bool_nonblocking.assert_called_once_with("ExperimentalMode", expected_mode)
      mock_events.add.assert_called_once_with(EventName.experimentalModeSwitched)
      assert switcher.experimental_mode_switched is True
    else:
      params.put_bool_nonblocking.assert_not_called()
      mock_events.add.assert_not_called()
      assert switcher.experimental_mode_switched is False
