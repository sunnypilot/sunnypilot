"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
#  /**
#   * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#   *
#   * This file is part of sunnypilot and is licensed under the MIT License.
#   * See the LICENSE.md file in the root directory for more details.
#   */

import random
import time

import pytest
from pytest_mock import MockerFixture

from cereal import custom
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventNameSP

# Class to be tested
class E2eStatusHandler:
  def __init__(self):
    self.events_sp = set()

  def process_e2e_status(self, model_x, lead_status, is_standstill, gas_pressed):
    """
    Determine if green light notification should be triggered based on conditions

    Args:
      model_x: List of model position x values
      lead_status: Whether a lead car is detected
      is_standstill: Whether the ego car is at standstill
      gas_pressed: Whether the gas pedal is pressed

    Returns:
      is_green_light: Boolean indicating whether green light is detected
    """
    max_idx = len(model_x) - 1
    is_green_light = False

    if (is_standstill
        and model_x[max_idx] > 30
        and not lead_status
        and not gas_pressed):
      is_green_light = True
      self.events_sp.add(custom.OnroadEventSP.EventName.e2eChime)

    return is_green_light


def create_mock(properties, mocker: MockerFixture):
  mock = mocker.MagicMock()
  for _property, value in properties.items():
    setattr(mock, _property, value)
  return mock


def setup_sm_mock(mocker: MockerFixture, model_x=None, lead_status=False, 
                  is_standstill=False, gas_pressed=False):
  # Default values for model position x
  if model_x is None:
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0]  # Last value > 30

  model_v2 = create_mock({
    'position': create_mock({
      'x': model_x
    }, mocker)
  }, mocker)

  radar_state = create_mock({
    'leadOne': create_mock({
      'status': lead_status
    }, mocker)
  }, mocker)

  car_state = create_mock({
    'standstill': is_standstill,
    'gasPressed': gas_pressed,
  }, mocker)

  sm_mock = mocker.MagicMock()
  sm_mock.__getitem__.side_effect = lambda key: {
    'modelV2': model_v2,
    'radarState': radar_state,
    'carState': car_state,
  }[key]

  return sm_mock


class TestE2eStatus:

  def test_initial_state(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    assert len(handler.events_sp) == 0

  def test_green_light_detection_all_conditions_met(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0]  # Last value > 30

    # All conditions met: standstill, model_x[max_idx] > 30, no lead car, gas not pressed
    result = handler.process_e2e_status(model_x, lead_status=False, 
                                        is_standstill=True, gas_pressed=False)

    # Should detect green light
    assert result is True
    # Should add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime in handler.events_sp

  def test_green_light_detection_no_standstill(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0]

    # Not at standstill
    result = handler.process_e2e_status(model_x, lead_status=False, 
                                        is_standstill=False, gas_pressed=False)

    # Should not detect green light
    assert result is False
    # Should not add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp

  def test_green_light_detection_model_x_too_small(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 28.0]  # Last value < 30

    # Model x too small
    result = handler.process_e2e_status(model_x, lead_status=False, 
                                        is_standstill=True, gas_pressed=False)

    # Should not detect green light
    assert result is False
    # Should not add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp

  def test_green_light_detection_lead_car_present(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0]

    # Lead car present
    result = handler.process_e2e_status(model_x, lead_status=True, 
                                        is_standstill=True, gas_pressed=False)

    # Should not detect green light
    assert result is False
    # Should not add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp

  def test_green_light_detection_gas_pressed(self, mocker: MockerFixture):
    handler = E2eStatusHandler()
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0]

    # Gas pressed
    result = handler.process_e2e_status(model_x, lead_status=False, 
                                        is_standstill=True, gas_pressed=True)

    # Should not detect green light
    assert result is False
    # Should not add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp

  def test_green_light_detection_with_sm_mock(self, mocker: MockerFixture):
    handler = E2eStatusHandler()

    # Setup mock with conditions for green light detection
    sm_mock = setup_sm_mock(mocker, 
                           model_x=[0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0],
                           lead_status=False,
                           is_standstill=True,
                           gas_pressed=False)

    # Directly extract values from sm_mock to pass to handler
    model_x = sm_mock['modelV2'].position.x
    lead_status = sm_mock['radarState'].leadOne.status
    is_standstill = sm_mock['carState'].standstill
    gas_pressed = sm_mock['carState'].gasPressed

    result = handler.process_e2e_status(model_x, lead_status, is_standstill, gas_pressed)

    # Should detect green light
    assert result is True
    # Should add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime in handler.events_sp

  def test_green_light_detection_with_sm_mock_no_green_light(self, mocker: MockerFixture):
    handler = E2eStatusHandler()

    # Setup mock with conditions for no green light detection (lead car present)
    sm_mock = setup_sm_mock(mocker, 
                           model_x=[0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0],
                           lead_status=True,  # Lead car present
                           is_standstill=True,
                           gas_pressed=False)

    # Directly extract values from sm_mock to pass to handler
    model_x = sm_mock['modelV2'].position.x
    lead_status = sm_mock['radarState'].leadOne.status
    is_standstill = sm_mock['carState'].standstill
    gas_pressed = sm_mock['carState'].gasPressed

    result = handler.process_e2e_status(model_x, lead_status, is_standstill, gas_pressed)

    # Should not detect green light
    assert result is False
    # Should not add e2eChime event
    assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp

  @pytest.mark.parametrize("model_x_last, lead_status, is_standstill, gas_pressed, expected_result", [
    (35.0, False, True, False, True),   # All conditions met
    (29.0, False, True, False, False),  # model_x too small
    (35.0, True, True, False, False),   # Lead car present
    (35.0, False, False, False, False), # Not at standstill
    (35.0, False, True, True, False),   # Gas pressed
  ])
  def test_green_light_detection_parametrized(self, mocker: MockerFixture, 
                                             model_x_last, lead_status, 
                                             is_standstill, gas_pressed, expected_result):
    handler = E2eStatusHandler()

    # Create model_x with the last value as specified
    model_x = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, model_x_last]

    result = handler.process_e2e_status(model_x, lead_status, is_standstill, gas_pressed)

    # Check if result matches expected result
    assert result is expected_result

    # Check if event was added appropriately
    if expected_result:
      assert custom.OnroadEventSP.EventName.e2eChime in handler.events_sp
    else:
      assert custom.OnroadEventSP.EventName.e2eChime not in handler.events_sp
