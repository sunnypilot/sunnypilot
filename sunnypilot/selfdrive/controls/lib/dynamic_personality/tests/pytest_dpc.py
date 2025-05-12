import pytest
import numpy as np
from cereal import log

from openpilot.sunnypilot.selfdrive.controls.lib.dynamic_personality.dynamic_personality_controller import DynamicPersonalityController

class TestDynamicPersonalityController:

  def setup_method(self):
    """Set up the controller before each test"""
    self.controller = DynamicPersonalityController()

  def test_compute_symmetric_slopes(self):
    """Test the symmetric slope computation method"""
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([2.0, 3.0, 5.0, 8.0])

    # Manual calculation of expected slopes based on the algorithm:
    # First slope: direct derivative from first segment
    # Middle slopes: average of adjacent segments
    # Last slope: direct derivative from last segment
    expected_slopes = np.zeros(4)
    expected_slopes[0] = (y[1] - y[0]) / (x[1] - x[0])  # 1.0
    expected_slopes[1] = ((y[2] - y[1]) / (x[2] - x[1]) + (y[1] - y[0]) / (x[1] - x[0])) / 2  # (2.0 + 1.0) / 2 = 1.5
    expected_slopes[2] = ((y[3] - y[2]) / (x[3] - x[2]) + (y[2] - y[1]) / (x[2] - x[1])) / 2  # (3.0 + 2.0) / 2 = 2.5
    expected_slopes[3] = (y[3] - y[2]) / (x[3] - x[2])  # 3.0

    computed_slopes = self.controller.compute_symmetric_slopes(x, y)

    np.testing.assert_allclose(computed_slopes, expected_slopes, rtol=1e-5)

  def test_hermite_interpolate(self):
    """Test hermite interpolation with known values"""
    xp = np.array([0.0, 10.0, 20.0])
    yp = np.array([5.0, 15.0, 10.0])
    slopes = np.array([1.0, 0.0, -1.0])

    # Test at data points
    assert self.controller.hermite_interpolate(0.0, xp, yp, slopes) == pytest.approx(5.0)
    assert self.controller.hermite_interpolate(10.0, xp, yp, slopes) == pytest.approx(15.0)
    assert self.controller.hermite_interpolate(20.0, xp, yp, slopes) == pytest.approx(10.0)

    # Test interpolation
    assert self.controller.hermite_interpolate(5.0, xp, yp, slopes) == pytest.approx(11.25)
    assert self.controller.hermite_interpolate(15.0, xp, yp, slopes) == pytest.approx(13.75)

  def test_hermite_interpolate_clipping(self):
    """Test that hermite interpolation properly clips values outside the range"""
    xp = np.array([0.0, 10.0, 20.0])
    yp = np.array([5.0, 15.0, 10.0])
    slopes = np.array([1.0, 0.0, -1.0])

    # Test clipping below minimum
    assert self.controller.hermite_interpolate(-5.0, xp, yp, slopes) == pytest.approx(5.0)

    # Test clipping above maximum
    assert self.controller.hermite_interpolate(25.0, xp, yp, slopes) == pytest.approx(10.0)

  def test_get_dynamic_follow_distance_relaxed(self):
    """Test follow distance calculation for relaxed personality"""
    # Test at specific data points
    assert self.controller.get_dynamic_follow_distance(0.0, log.LongitudinalPersonality.relaxed) == pytest.approx(1.25)
    assert self.controller.get_dynamic_follow_distance(5.0, log.LongitudinalPersonality.relaxed) == pytest.approx(1.3)
    assert self.controller.get_dynamic_follow_distance(40.0, log.LongitudinalPersonality.relaxed) == pytest.approx(1.75)

    # Test interpolation
    assert self.controller.get_dynamic_follow_distance(20.0, log.LongitudinalPersonality.relaxed) > 1.3
    assert self.controller.get_dynamic_follow_distance(20.0, log.LongitudinalPersonality.relaxed) < 1.75

  def test_get_dynamic_follow_distance_standard(self):
    """Test follow distance calculation for standard personality"""
    # Test at specific data points
    assert self.controller.get_dynamic_follow_distance(0.0, log.LongitudinalPersonality.standard) == pytest.approx(1.20)
    assert self.controller.get_dynamic_follow_distance(5.0, log.LongitudinalPersonality.standard) == pytest.approx(1.275)
    assert self.controller.get_dynamic_follow_distance(40.0, log.LongitudinalPersonality.standard) == pytest.approx(1.50)

    # Test interpolation
    mid_value = self.controller.get_dynamic_follow_distance(21.0, log.LongitudinalPersonality.standard)
    assert mid_value > 1.275
    assert mid_value < 1.50

  def test_get_dynamic_follow_distance_aggressive(self):
    """Test follow distance calculation for aggressive personality"""
    # Test at specific data points
    assert self.controller.get_dynamic_follow_distance(0.0, log.LongitudinalPersonality.aggressive) == pytest.approx(0.92)
    assert self.controller.get_dynamic_follow_distance(6.0, log.LongitudinalPersonality.aggressive) == pytest.approx(1.25)
    assert self.controller.get_dynamic_follow_distance(40.0, log.LongitudinalPersonality.aggressive) == pytest.approx(1.30)

    # Test intermediate value
    assert self.controller.get_dynamic_follow_distance(4.0, log.LongitudinalPersonality.aggressive) > 0.9
    assert self.controller.get_dynamic_follow_distance(4.0, log.LongitudinalPersonality.aggressive) < 1.25

  def test_get_dynamic_follow_distance_invalid(self):
    """Test that an invalid personality raises NotImplementedError"""
    with pytest.raises(NotImplementedError, match="Dynamic personality not supported"):
      self.controller.get_dynamic_follow_distance(10.0, 999)  # Using an invalid personality value

  def test_get_dynamic_follow_distance_comparison(self):
    """Test that relaxed > standard > aggressive for follow distances"""
    speed = 20.0
    relaxed = self.controller.get_dynamic_follow_distance(speed, log.LongitudinalPersonality.relaxed)
    standard = self.controller.get_dynamic_follow_distance(speed, log.LongitudinalPersonality.standard)
    aggressive = self.controller.get_dynamic_follow_distance(speed, log.LongitudinalPersonality.aggressive)

    assert relaxed > standard
    assert standard > aggressive

  def test_speed_impact_on_follow_distance(self):
    """Test that follow distance increases with speed"""
    personality = log.LongitudinalPersonality.standard

    low_speed = self.controller.get_dynamic_follow_distance(5.0, personality)
    high_speed = self.controller.get_dynamic_follow_distance(30.0, personality)

    assert high_speed > low_speed
