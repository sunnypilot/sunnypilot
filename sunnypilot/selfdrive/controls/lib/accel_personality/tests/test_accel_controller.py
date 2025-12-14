"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest
import numpy as np
from cereal import custom
from sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller import (
  AccelPersonalityController,
  MAX_ACCEL_PROFILES,
  MIN_ACCEL_PROFILES,
  MAX_ACCEL_BREAKPOINTS,
  MIN_ACCEL_BREAKPOINTS,
)

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality


class TestAccelPersonalityController:

  @pytest.fixture
  def mock_params(self, mocker):
    params = mocker.Mock()
    params.get = mocker.Mock(return_value=None)
    params.get_bool = mocker.Mock(return_value=False)
    params.put = mocker.Mock()
    params.put_bool = mocker.Mock()
    return params

  @pytest.fixture
  def controller(self, mock_params, mocker):
    mocker.patch('sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller.Params', return_value=mock_params)
    ctrl = AccelPersonalityController()
    ctrl.params = mock_params
    return ctrl

  def test_initialization_defaults(self, controller):
    assert controller.frame == 0
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.param_keys == {
      'personality': 'AccelPersonality',
      'enabled': 'AccelPersonalityEnabled'
    }

  @pytest.mark.parametrize("personality,expected", [
    (AccelPersonality.eco, AccelPersonality.eco),
    (AccelPersonality.normal, AccelPersonality.normal),
    (AccelPersonality.sport, AccelPersonality.sport),
  ])
  def test_load_personality_valid(self, mocker, personality, expected):
    mock_params = mocker.Mock()
    mock_params.get = mocker.Mock(return_value=str(personality).encode())
    mock_params.get_bool = mocker.Mock(return_value=False)
    mocker.patch('sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller.Params', return_value=mock_params)
    controller = AccelPersonalityController()
    assert controller.accel_personality == expected

  def test_load_personality_invalid_value(self, mocker):
    mock_params = mocker.Mock()
    mock_params.get = mocker.Mock(return_value=b'999')
    mock_params.get_bool = mocker.Mock(return_value=False)
    mocker.patch('sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller.Params', return_value=mock_params)
    controller = AccelPersonalityController()
    assert controller.accel_personality == AccelPersonality.normal

  def test_load_personality_parse_error(self, mocker):
    mock_params = mocker.Mock()
    mock_params.get = mocker.Mock(return_value=b'invalid_data')
    mock_params.get_bool = mocker.Mock(return_value=False)
    mocker.patch('sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller.Params', return_value=mock_params)
    controller = AccelPersonalityController()
    assert controller.accel_personality == AccelPersonality.normal

  def test_load_personality_none(self, mocker):
    mock_params = mocker.Mock()
    mock_params.get = mocker.Mock(return_value=None)
    mock_params.get_bool = mocker.Mock(return_value=False)
    mocker.patch('sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller.Params', return_value=mock_params)
    controller = AccelPersonalityController()
    assert controller.accel_personality == AccelPersonality.normal

  def test_get_accel_personality(self, controller):
    controller.accel_personality = AccelPersonality.sport
    result = controller.get_accel_personality()
    assert result == AccelPersonality.sport
    assert isinstance(result, int)

  @pytest.mark.parametrize("personality", [
    AccelPersonality.eco,
    AccelPersonality.normal,
    AccelPersonality.sport,
  ])
  def test_set_accel_personality_valid(self, controller, mock_params, personality):
    controller.set_accel_personality(personality)
    assert controller.accel_personality == personality
    mock_params.put.assert_called_once_with('AccelPersonality', str(personality))

  def test_set_accel_personality_invalid(self, controller, mock_params):
    original = controller.accel_personality
    controller.set_accel_personality(999)
    assert controller.accel_personality == original
    mock_params.put.assert_not_called()

  def test_cycle_accel_personality_full_cycle(self, controller):
    controller.accel_personality = AccelPersonality.eco

    result = controller.cycle_accel_personality()
    assert result == AccelPersonality.normal
    assert controller.accel_personality == AccelPersonality.normal

    result = controller.cycle_accel_personality()
    assert result == AccelPersonality.sport
    assert controller.accel_personality == AccelPersonality.sport

    result = controller.cycle_accel_personality()
    assert result == AccelPersonality.eco
    assert controller.accel_personality == AccelPersonality.eco

  def test_cycle_accel_personality_return_type(self, controller):
    result = controller.cycle_accel_personality()
    assert isinstance(result, int)

  @pytest.mark.parametrize("personality", [
    AccelPersonality.eco,
    AccelPersonality.normal,
    AccelPersonality.sport,
  ])
  def test_get_accel_limits_at_zero_speed(self, controller, personality):
    controller.accel_personality = personality
    min_a, max_a = controller.get_accel_limits(0.0)

    expected_max = MAX_ACCEL_PROFILES[personality][0]
    expected_min = MIN_ACCEL_PROFILES[personality][0]

    assert abs(max_a - expected_max) < 1e-6
    assert abs(min_a - expected_min) < 1e-6

  @pytest.mark.parametrize("v_ego,personality", [
    (0.0, AccelPersonality.eco),
    (10.0, AccelPersonality.normal),
    (25.0, AccelPersonality.sport),
    (50.0, AccelPersonality.eco),
    (4.0, AccelPersonality.normal),
    (30.0, AccelPersonality.sport),
  ])
  def test_get_accel_limits_interpolation(self, controller, v_ego, personality):
    controller.accel_personality = personality
    min_a, max_a = controller.get_accel_limits(v_ego)

    expected_max = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[personality])
    expected_min = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[personality])

    assert abs(max_a - expected_max) < 1e-6
    assert abs(min_a - expected_min) < 1e-6

  def test_get_accel_limits_return_types(self, controller):
    min_a, max_a = controller.get_accel_limits(10.0)
    assert isinstance(min_a, float)
    assert isinstance(max_a, float)

  def test_get_min_accel(self, controller):
    controller.accel_personality = AccelPersonality.sport
    v_ego = 15.0
    min_a = controller.get_min_accel(v_ego)
    expected = controller.get_accel_limits(v_ego)[0]
    assert min_a == expected
    assert isinstance(min_a, float)

  def test_get_max_accel(self, controller):
    controller.accel_personality = AccelPersonality.eco
    v_ego = 20.0
    max_a = controller.get_max_accel(v_ego)
    expected = controller.get_accel_limits(v_ego)[1]
    assert max_a == expected
    assert isinstance(max_a, float)

  def test_is_enabled_true(self, controller, mock_params):
    mock_params.get_bool.return_value = True
    assert controller.is_enabled() is True

  def test_is_enabled_false(self, controller, mock_params):
    mock_params.get_bool.return_value = False
    assert controller.is_enabled() is False

  def test_is_enabled_calls_params(self, controller, mock_params):
    controller.is_enabled()
    mock_params.get_bool.assert_called_once_with('AccelPersonalityEnabled')

  @pytest.mark.parametrize("enabled", [True, False])
  def test_set_enabled(self, controller, mock_params, enabled):
    controller.set_enabled(enabled)
    mock_params.put_bool.assert_called_once_with('AccelPersonalityEnabled', enabled)

  def test_toggle_enabled_from_false(self, controller, mock_params):
    mock_params.get_bool.return_value = False
    result = controller.toggle_enabled()
    assert result is True
    mock_params.put_bool.assert_called_once_with('AccelPersonalityEnabled', True)

  def test_toggle_enabled_from_true(self, controller, mock_params):
    mock_params.get_bool.return_value = True
    result = controller.toggle_enabled()
    assert result is False
    mock_params.put_bool.assert_called_once_with('AccelPersonalityEnabled', False)

  def test_reset(self, controller):
    controller.accel_personality = AccelPersonality.sport
    controller.frame = 100
    controller.reset()
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.frame == 0

  def test_update_increments_frame(self, controller):
    initial_frame = controller.frame
    controller.update()
    assert controller.frame == initial_frame + 1

  def test_update_multiple_calls(self, controller):
    for i in range(1, 11):
      controller.update()
      assert controller.frame == i

  @pytest.mark.parametrize("v_ego", [0, 5, 10, 15, 20, 25, 30, 40, 50, 55])
  @pytest.mark.parametrize("personality", [
    AccelPersonality.eco,
    AccelPersonality.normal,
    AccelPersonality.sport,
  ])
  def test_accel_limits_physical_constraints(self, controller, v_ego, personality):
    controller.accel_personality = personality
    min_a, max_a = controller.get_accel_limits(v_ego)
    assert min_a < 0
    assert max_a > 0
    assert min_a < max_a

  def test_max_accel_decreases_with_speed(self, controller):
    test_speeds = [0, 10, 20, 30, 40, 50]
    for personality in [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]:
      controller.accel_personality = personality
      max_accels = [controller.get_max_accel(v) for v in test_speeds]
      assert max_accels[-1] < max_accels[0]

  @pytest.mark.parametrize("v_ego", [5, 10, 15, 20, 25])
  def test_acceleration_personality_ordering(self, controller, v_ego):
    controller.accel_personality = AccelPersonality.eco
    _, eco_max = controller.get_accel_limits(v_ego)

    controller.accel_personality = AccelPersonality.normal
    _, normal_max = controller.get_accel_limits(v_ego)

    controller.accel_personality = AccelPersonality.sport
    _, sport_max = controller.get_accel_limits(v_ego)

    assert sport_max >= normal_max
    assert normal_max >= eco_max

  @pytest.mark.parametrize("v_ego", [5, 10, 15, 20])
  def test_braking_personality_ordering(self, controller, v_ego):
    controller.accel_personality = AccelPersonality.eco
    eco_min, _ = controller.get_accel_limits(v_ego)

    controller.accel_personality = AccelPersonality.sport
    sport_min, _ = controller.get_accel_limits(v_ego)

    assert sport_min <= eco_min

  def test_accel_limits_at_max_speed(self, controller):
    max_speed = MAX_ACCEL_BREAKPOINTS[-1]
    min_a, max_a = controller.get_accel_limits(max_speed)
    assert isinstance(min_a, float)
    assert isinstance(max_a, float)

  def test_accel_limits_beyond_max_speed(self, controller):
    beyond_max = MAX_ACCEL_BREAKPOINTS[-1] + 10
    min_a, max_a = controller.get_accel_limits(beyond_max)
    assert isinstance(min_a, float)
    assert isinstance(max_a, float)

  def test_accel_limits_very_low_speed(self, controller):
    min_a, max_a = controller.get_accel_limits(0.5)
    assert isinstance(min_a, float)
    assert isinstance(max_a, float)
    assert min_a >= -2.0
