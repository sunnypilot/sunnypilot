import pytest

# Import the actual modules
from cereal import log, custom
from openpilot.common.realtime import DT_MDL

# Import the enums we need for testing
LongPersonality = log.LongitudinalPersonality
AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality


class MockParams:
  """Simple mock for Params class"""
  def __init__(self):
    self.data = {}
    self.bool_data = {
      'VibePersonalityEnabled': True,
      'VibeAccelPersonalityEnabled': True,
      'VibeFollowPersonalityEnabled': True
    }

  def get(self, key, encoding=None):
    return self.data.get(key)

  def get_bool(self, key):
    return self.bool_data.get(key, True)

  def put(self, key, value):
    self.data[key] = value

  def put_bool(self, key, value):
    self.bool_data[key] = value

  def reset_mock(self):
    self.call_count = 0

  @property
  def call_count(self):
    return getattr(self, '_call_count', 0)

  @call_count.setter
  def call_count(self, value):
    self._call_count = value


@pytest.fixture
def mock_params():
  """Create mock params instance"""
  return MockParams()


@pytest.fixture
def controller(mock_params, monkeypatch):
  """Create controller instance with mocked Params"""
  # Patch the Params import in the controller module
  monkeypatch.setattr('openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.vibe_personality.Params',
                      lambda: mock_params)

  from openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.vibe_personality import VibePersonalityController
  return VibePersonalityController()


class TestVibePersonalityController:

  def test_initialization(self, controller):
    """Test controller initializes with correct defaults"""
    assert controller.frame == 0
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.long_personality == LongPersonality.standard
    assert 'accel_personality' in controller.param_keys
    assert 'long_personality' in controller.param_keys

  def test_frame_increment(self, controller):
    """Test frame counter increments correctly"""
    initial_frame = controller.frame
    controller.update()
    assert controller.frame == initial_frame + 1

    controller.update()
    assert controller.frame == initial_frame + 2

  def test_parameter_reading_throttled(self, controller, mock_params):
    """Test parameters are only read every DT_MDL frames"""
    # Track calls manually
    original_get = mock_params.get
    call_count = 0

    def counting_get(*args, **kwargs):
      nonlocal call_count
      call_count += 1
      return original_get(*args, **kwargs)

    mock_params.get = counting_get

    # First call should read params (frame 0)
    controller._update_from_params()

    # Reset counter
    call_count = 0

    # Advance frame but not to threshold
    controller.frame = 5  # Less than int(1/DT_MDL)
    controller._update_from_params()
    assert call_count == 0  # Should not read params

    # Advance to threshold
    controller.frame = int(1. / DT_MDL)  # Equal to threshold
    controller._update_from_params()
    assert call_count >= 2  # Should read both personality params

  def test_accel_personality_management(self, controller, mock_params):
    """Test acceleration personality setting and cycling"""
    # Test setting valid personality
    assert controller.set_accel_personality(AccelPersonality.eco)
    assert controller.accel_personality == AccelPersonality.eco

    assert controller.set_accel_personality(AccelPersonality.sport)
    assert controller.accel_personality == AccelPersonality.sport

    # Test setting invalid personality
    assert not controller.set_accel_personality(999)
    assert controller.accel_personality == AccelPersonality.sport  # Should remain unchanged

    # Test cycling
    controller.accel_personality = AccelPersonality.eco
    next_personality = controller.cycle_accel_personality()
    assert next_personality == AccelPersonality.normal  # should cycle to normal
    assert controller.accel_personality == AccelPersonality.normal

    next_personality = controller.cycle_accel_personality()
    assert next_personality == AccelPersonality.sport  # should cycle to sport

    next_personality = controller.cycle_accel_personality()
    assert next_personality == AccelPersonality.eco  # should cycle back to eco

  def test_long_personality_management(self, controller, mock_params):
    """Test longitudinal personality setting and cycling"""
    # Test setting valid personality
    assert controller.set_long_personality(LongPersonality.relaxed)
    assert controller.long_personality == LongPersonality.relaxed

    assert controller.set_long_personality(LongPersonality.aggressive)
    assert controller.long_personality == LongPersonality.aggressive

    # Test setting invalid personality
    assert not controller.set_long_personality(999)
    assert controller.long_personality == LongPersonality.aggressive  # Should remain unchanged

    # Test cycling
    controller.long_personality = LongPersonality.standard
    next_personality = controller.cycle_long_personality()
    assert next_personality == LongPersonality.aggressive  # should cycle to aggressive
    assert controller.long_personality == LongPersonality.aggressive

    next_personality = controller.cycle_long_personality()
    assert next_personality == LongPersonality.relaxed  # should cycle to relaxed

    next_personality = controller.cycle_long_personality()
    assert next_personality == LongPersonality.standard  # should cycle back to standard

  def test_toggle_functions(self, controller, mock_params):
    """Test toggle functionality"""
    # Set initial state to False
    mock_params.bool_data['VibePersonalityEnabled'] = False

    result = controller.toggle_personality()
    assert result  # Should toggle to True
    assert mock_params.bool_data['VibePersonalityEnabled']

    # Set initial state to True
    mock_params.bool_data['VibeAccelPersonalityEnabled'] = True

    result = controller.toggle_accel_personality()
    assert not result  # Should toggle to False
    assert not mock_params.bool_data['VibeAccelPersonalityEnabled']

  def test_enable_checks(self, controller, mock_params):
    """Test various enable state checks"""
    # All enabled
    mock_params.bool_data = {
      'VibePersonalityEnabled': True,
      'VibeAccelPersonalityEnabled': True,
      'VibeFollowPersonalityEnabled': True
    }

    assert controller.is_enabled()
    assert controller.is_accel_enabled()
    assert controller.is_follow_enabled()

    # Main toggle disabled
    mock_params.bool_data['VibePersonalityEnabled'] = False

    assert not controller.is_enabled()
    assert not controller.is_accel_enabled()
    assert not controller.is_follow_enabled()

  def test_accel_limits_calculation(self, controller, mock_params):
    """Test acceleration limits calculation"""
    # Enable all features through mock_params bool_data
    mock_params.bool_data = {
      'VibePersonalityEnabled': True,
      'VibeAccelPersonalityEnabled': True,
      'VibeFollowPersonalityEnabled': True
    }

    # Test with different speeds and personalities
    controller.accel_personality = 1  # normal
    controller.long_personality = 1  # standard

    limits = controller.get_accel_limits(10.0)  # 10 m/s
    assert limits is not None
    min_a, max_a = limits
    assert isinstance(min_a, float)
    assert isinstance(max_a, float)
    assert min_a < 0  # Should be negative (braking)
    assert max_a > 0  # Should be positive (acceleration)

    # Test with disabled controller
    mock_params.bool_data['VibePersonalityEnabled'] = False
    limits = controller.get_accel_limits(10.0)
    assert limits is None

  def test_follow_distance_multiplier(self, controller, mock_params):
    """Test following distance multiplier calculation"""
    # Enable controller
    mock_params.bool_data['VibePersonalityEnabled'] = True
    mock_params.bool_data['VibeFollowPersonalityEnabled'] = True

    # Test with different speeds and personalities
    controller.long_personality = LongPersonality.relaxed

    multiplier = controller.get_follow_distance_multiplier(15.0)  # 15 m/s
    assert multiplier is not None
    assert isinstance(multiplier, float)
    assert multiplier > 0

    # Test with different personality - aggressive should have shorter distance
    controller.long_personality = LongPersonality.aggressive
    aggressive_multiplier = controller.get_follow_distance_multiplier(15.0)
    assert aggressive_multiplier is not None
    assert aggressive_multiplier < multiplier  # Aggressive should have shorter distance

    # Test with disabled controller
    mock_params.bool_data['VibeFollowPersonalityEnabled'] = False
    multiplier = controller.get_follow_distance_multiplier(15.0)
    assert multiplier is None

  def test_personality_differences(self, controller, mock_params):
    """Test that different personalities actually produce different values"""
    # Enable controller
    mock_params.bool_data['VibePersonalityEnabled'] = True
    mock_params.bool_data['VibeAccelPersonalityEnabled'] = True
    mock_params.bool_data['VibeFollowPersonalityEnabled'] = True

    # Test acceleration differences - sport should have higher max acceleration than eco
    controller.accel_personality = AccelPersonality.eco
    eco_limits = controller.get_accel_limits(20.0)

    controller.accel_personality = AccelPersonality.sport
    sport_limits = controller.get_accel_limits(20.0)

    assert sport_limits[1] > eco_limits[1]  # Sport should have higher max acceleration

    # Test following distance differences - relaxed should have longer distance than aggressive
    controller.long_personality = LongPersonality.relaxed
    relaxed_dist = controller.get_follow_distance_multiplier(20.0)

    controller.long_personality = LongPersonality.aggressive
    aggressive_dist = controller.get_follow_distance_multiplier(20.0)

    assert relaxed_dist > aggressive_dist  # Relaxed should have longer following distance

  def test_reset(self, controller):
    """Test reset functionality"""
    # Change some values
    controller.accel_personality = AccelPersonality.sport
    controller.long_personality = LongPersonality.relaxed
    controller.frame = 100

    # Reset
    controller.reset()

    # Check defaults are restored
    assert controller.accel_personality == AccelPersonality.normal
    assert controller.long_personality == LongPersonality.standard
    assert controller.frame == 0

  def test_edge_cases(self, controller, mock_params):
    """Test edge cases and error handling"""
    # Enable all features
    mock_params.bool_data = {
      'VibePersonalityEnabled': True,
      'VibeAccelPersonalityEnabled': True,
      'VibeFollowPersonalityEnabled': True
    }

    # Test with zero speed
    limits = controller.get_accel_limits(0.0)
    assert limits is not None

    multiplier = controller.get_follow_distance_multiplier(0.0)
    assert multiplier is not None

    # Test with very high speed
    limits = controller.get_accel_limits(100.0)
    assert limits is not None

    multiplier = controller.get_follow_distance_multiplier(100.0)
    assert multiplier is not None

    # Test interpolation works correctly
    low_speed_limits = controller.get_accel_limits(5.0)
    high_speed_limits = controller.get_accel_limits(50.0)
    assert low_speed_limits[1] > high_speed_limits[1]  # Max accel should decrease with speed
