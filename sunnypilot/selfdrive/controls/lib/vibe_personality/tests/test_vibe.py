"""
Test suite for VibePersonalityController

Tests the core functionality of the vibe personality system including
acceleration profiles, following distance, and personality management.
"""

import pytest
import numpy as np
from pytest_mock import MockerFixture
from cereal import log, custom

from openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.vibe_personality import VibePersonalityController

AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality
LongPersonality = log.LongitudinalPersonality


class TestVibePersonalityController:
  """Test suite for VibePersonalityController"""

  @pytest.fixture
  def mock_params(self, mocker: MockerFixture):
    """Mock Params with realistic behavior"""
    mock = mocker.Mock()
    mock.get.return_value = None
    mock.get_bool.return_value = True
    mock.put.return_value = None
    mock.put_bool.return_value = None
    return mock

  @pytest.fixture
  def controller(self, mock_params, mocker: MockerFixture):
    """Create controller with mocked dependencies"""
    mocker.patch('openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.vibe_personality.Params', return_value=mock_params)
    controller = VibePersonalityController()
    controller.params = mock_params
    return controller

  def test_initialization_sets_correct_defaults(self, controller):
    """Controller should initialize with expected default values"""
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.long_personality == LongPersonality.standard
    assert controller.frame == 0
    assert hasattr(controller, 'max_accel_slopes')
    assert hasattr(controller, 'min_accel_slopes')
    assert hasattr(controller, 'follow_distance_slopes')

  def test_accel_personality_management(self, controller):
    """Test acceleration personality setting and cycling"""
    # Valid personality setting
    result = controller.set_accel_personality(AccelPersonality.sport)
    assert result is True
    assert controller.accel_personality == AccelPersonality.sport
    controller.params.put.assert_called_with('AccelPersonality', str(AccelPersonality.sport))

    # Invalid personality setting
    result = controller.set_accel_personality(999)
    assert result is False
    assert controller.accel_personality == AccelPersonality.sport  # unchanged

    # Cycling behavior
    controller.set_accel_personality(AccelPersonality.eco)
    assert controller.cycle_accel_personality() == AccelPersonality.normal
    assert controller.cycle_accel_personality() == AccelPersonality.sport
    assert controller.cycle_accel_personality() == AccelPersonality.eco

  def test_long_personality_management(self, controller):
    """Test longitudinal personality setting and cycling"""
    # Valid setting
    result = controller.set_long_personality(LongPersonality.aggressive)
    assert result is True
    assert controller.long_personality == LongPersonality.aggressive

    # Invalid setting
    result = controller.set_long_personality(-1)
    assert result is False

    # Cycling
    controller.set_long_personality(LongPersonality.relaxed)
    assert controller.cycle_long_personality() == LongPersonality.standard
    assert controller.cycle_long_personality() == LongPersonality.aggressive
    assert controller.cycle_long_personality() == LongPersonality.relaxed

  def test_enable_disable_logic(self, controller):
    """Test feature enable/disable states"""
    # Mock enabled state
    controller.params.get_bool.return_value = True
    assert controller.is_enabled() is True
    assert controller.is_accel_enabled() is True
    assert controller.is_follow_enabled() is True

    # Mock disabled state
    controller.params.get_bool.return_value = False
    assert controller.is_enabled() is False
    assert controller.is_accel_enabled() is False
    assert controller.is_follow_enabled() is False

    # Test partial disable (only main toggle off)
    def mock_get_bool(key):
      return key != 'VibePersonalityEnabled'
    controller.params.get_bool.side_effect = mock_get_bool
    assert controller.is_accel_enabled() is False
    assert controller.is_follow_enabled() is False

  def test_get_accel_limits_returns_valid_range(self, controller):
    """Acceleration limits should return valid min/max values"""
    controller.params.get_bool.return_value = True

    # Test at multiple speeds
    for speed in [0.0, 15.0, 30.0]:
      limits = controller.get_accel_limits(speed)
      assert limits is not None, f"Failed at speed {speed}"

      min_a, max_a = limits
      assert isinstance(min_a, float)
      assert isinstance(max_a, float)
      assert min_a < 0, "Min acceleration should be negative (braking)"
      assert max_a > 0, "Max acceleration should be positive"
      assert min_a < max_a, "Min should be less than max"

  def test_get_accel_limits_returns_none_when_disabled(self, controller):
    """Should return None when acceleration control is disabled"""
    controller.params.get_bool.return_value = False
    assert controller.get_accel_limits(20.0) is None

  def test_get_follow_distance_multiplier_returns_positive_value(self, controller):
    """Follow distance multiplier should be positive"""
    controller.params.get_bool.return_value = True

    multiplier = controller.get_follow_distance_multiplier(20.0)
    assert multiplier is not None
    assert isinstance(multiplier, float)
    assert multiplier > 0

  def test_get_follow_distance_multiplier_returns_none_when_disabled(self, controller):
    """Should return None when follow distance control is disabled"""
    controller.params.get_bool.return_value = False
    assert controller.get_follow_distance_multiplier(20.0) is None

  def test_personality_differences_produce_different_results(self, controller):
    """Different personalities should produce measurably different outputs"""
    controller.params.get_bool.return_value = True

    # Test acceleration personality differences
    controller.set_accel_personality(AccelPersonality.eco)
    eco_limits = controller.get_accel_limits(15.0)

    controller.set_accel_personality(AccelPersonality.sport)
    sport_limits = controller.get_accel_limits(15.0)

    assert sport_limits[1] > eco_limits[1], "Sport should allow higher acceleration than eco"

    # Test following distance personality differences
    controller.set_long_personality(LongPersonality.relaxed)
    relaxed_dist = controller.get_follow_distance_multiplier(20.0)

    controller.set_long_personality(LongPersonality.aggressive)
    aggressive_dist = controller.get_follow_distance_multiplier(20.0)

    assert relaxed_dist > aggressive_dist, "Relaxed should have longer following distance"

  def test_interpolation_functions_work_correctly(self, controller):
    """Test mathematical interpolation functions"""
    # Test slope computation
    x = np.array([0., 10., 20.])
    y = np.array([1.0, 2.0, 1.5])
    slopes = controller._compute_slopes(x, y)

    assert len(slopes) == len(x)
    assert all(np.isfinite(slope) for slope in slopes)

    # Test interpolation accuracy at known points
    result_0 = controller._interpolate(0.0, x, y, slopes)
    result_10 = controller._interpolate(10.0, x, y, slopes)

    assert abs(result_0 - 1.0) < 1e-6, "Interpolation should be exact at breakpoints"
    assert abs(result_10 - 2.0) < 1e-6, "Interpolation should be exact at breakpoints"

    # Test interpolation bounds
    result_below = controller._interpolate(-5.0, x, y, slopes)
    result_above = controller._interpolate(25.0, x, y, slopes)
    assert abs(result_below - y[0]) < 1e-6, "Should clamp to first value"
    assert abs(result_above - y[-1]) < 1e-6, "Should clamp to last value"

  def test_get_personality_info_returns_complete_info(self, controller):
    """Personality info should contain all required fields"""
    info = controller.get_personality_info()

    required_fields = [
      'accel_personality', 'accel_personality_int',
      'long_personality', 'long_personality_int',
      'enabled', 'accel_enabled', 'follow_enabled'
    ]

    for field in required_fields:
      assert field in info, f"Missing required field: {field}"

    assert info['accel_personality'] in ['Eco', 'Normal', 'Sport']
    assert info['long_personality'] in ['Relaxed', 'Standard', 'Aggressive']
    assert isinstance(info['enabled'], bool)

  def test_toggle_functions_change_state(self, controller):
    """Toggle functions should change parameter states"""
    # Mock current enabled state
    controller.params.get_bool.return_value = True

    # Test main toggle
    result = controller.toggle_personality()
    assert result is False  # should return new state
    controller.params.put_bool.assert_called_with('VibePersonalityEnabled', False)

    # Test specific toggles
    controller.params.get_bool.return_value = True
    controller.toggle_accel_personality()
    controller.params.put_bool.assert_called_with('VibeAccelPersonalityEnabled', False)

    controller.toggle_follow_distance_personality()
    controller.params.put_bool.assert_called_with('VibeFollowPersonalityEnabled', False)

  def test_reset_restores_defaults(self, controller):
    """Reset should restore controller to default state"""
    # Change from defaults
    controller.set_accel_personality(AccelPersonality.sport)
    controller.set_long_personality(LongPersonality.aggressive)
    controller.frame = 1000

    # Reset and verify defaults
    controller.reset()
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.long_personality == LongPersonality.standard
    assert controller.frame == 0

  def test_update_increments_frame_counter(self, controller):
    """Update should increment frame counter with wraparound"""
    initial_frame = controller.frame
    controller.update()
    assert controller.frame == initial_frame + 1

    # Test wraparound
    controller.frame = 999999
    controller.update()
    assert controller.frame == 0

  def test_individual_accel_methods(self, controller):
    """Test individual min/max accel convenience methods"""
    controller.params.get_bool.return_value = True

    min_accel = controller.get_min_accel(15.0)
    max_accel = controller.get_max_accel(15.0)

    assert min_accel is not None
    assert max_accel is not None
    assert min_accel < 0
    assert max_accel > 0

    # Test disabled state
    controller.params.get_bool.return_value = False
    assert controller.get_min_accel(15.0) is None
    assert controller.get_max_accel(15.0) is None

  @pytest.mark.parametrize("speed", [0.0, 5.0, 15.0, 25.0, 40.0, 55.0])
  def test_accel_limits_at_various_speeds(self, controller, speed):
    """Test acceleration limits across speed range"""
    controller.params.get_bool.return_value = True

    limits = controller.get_accel_limits(speed)
    assert limits is not None

    min_a, max_a = limits
    assert min_a < max_a
    assert -2.0 < min_a < 0  # Reasonable braking range
    assert 0 < max_a < 3.0   # Reasonable acceleration range

  def test_error_handling_in_interpolation(self, controller):
    """Test interpolation handles edge cases gracefully"""
    # Test with minimal points
    x = [0., 1.]
    y = [1.0, 2.0]
    slopes = controller._compute_slopes(x, y)
    result = controller._interpolate(0.5, x, y, slopes)
    assert 1.0 <= result <= 2.0

    # Test with insufficient points
    with pytest.raises(ValueError):
      controller._compute_slopes([0.], [1.0])
