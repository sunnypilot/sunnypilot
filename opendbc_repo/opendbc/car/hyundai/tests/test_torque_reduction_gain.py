import time
import pytest
from opendbc.car.hyundai.torque_reduction_gain import TorqueReductionGainController


class FakeTime:
    def __init__(self):
        self._now = 1000.0

    def monotonic(self):
        return self._now

    def advance(self, dt):
        self._now += dt


@pytest.fixture
def fake_time(monkeypatch):
    # Patch time.monotonic to use our controllable FakeTime for deterministic tests
    ft = FakeTime()
    monkeypatch.setattr(time, 'monotonic', ft.monotonic)
    return ft


def test_gain_increases_when_saturated(fake_time):
    # Test: Gain should increase when angle error is above threshold and after debounce
    ctrl = TorqueReductionGainController(angle_threshold=2.0, debounce_time=0.2, ramp_up_rate=0.5)
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    # Initially, gain should be at minimum (0.0)
    assert gain == 0.0
    fake_time.advance(0.3)  # Advance time past debounce
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    # After debounce, gain should start increasing
    assert gain > 0.0
    prev_gain = gain
    fake_time.advance(1.0)
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    # Gain should continue to increase but not exceed 1.0
    assert gain > prev_gain
    assert gain <= 1.0


def test_gain_resets_when_not_active(fake_time):
    # Test: Gain should reset to minimum when lateral control is not active
    ctrl = TorqueReductionGainController(angle_threshold=2.0, debounce_time=0.1, ramp_up_rate=1.0)
    ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    fake_time.advance(0.2)
    ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    fake_time.advance(0.2)
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    assert gain > 0.0  # Gain has increased
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=False)
    # When lat_active is False, gain should reset to 0.0
    assert gain == 0.0


def test_gain_decreases_when_not_saturated(fake_time):
    # Test: Gain should decrease when angle error drops below threshold (not saturated)
    ctrl = TorqueReductionGainController(angle_threshold=2.0, debounce_time=0.1, ramp_up_rate=1.0, ramp_down_rate=0.5)
    ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    fake_time.advance(0.2)
    ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    fake_time.advance(0.2)
    gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    assert gain > 0.0  # Gain has increased
    prev_gain = gain
    fake_time.advance(0.5)
    # Now, requested and actual angles are equal (no error)
    gain = ctrl.update(last_requested_angle=10, actual_angle=10, lat_active=True)
    # Gain should decrease
    assert gain < prev_gain


def test_gain_clamped(fake_time):
    # Test: Gain should be clamped between min_gain and max_gain
    ctrl = TorqueReductionGainController(angle_threshold=1.0, debounce_time=0.0, ramp_up_rate=10.0, min_gain=0.2, max_gain=0.8)
    gain = 0.
    for _ in range(10):
        fake_time.advance(0.1)
        gain = ctrl.update(last_requested_angle=10, actual_angle=0, lat_active=True)
    # Gain should not exceed max_gain and not go below min_gain
    assert 0.2 <= gain <= 0.8
    assert gain == 0.8


def test_gain_no_increase_below_threshold(fake_time):
    # Test: Gain should not increase if angle error is below the threshold
    ctrl = TorqueReductionGainController(angle_threshold=5.0, debounce_time=0.1, ramp_up_rate=1.0)
    ctrl.update(last_requested_angle=2, actual_angle=0, lat_active=True)
    fake_time.advance(0.2)
    gain = ctrl.update(last_requested_angle=2, actual_angle=0, lat_active=True)
    # Since error is below threshold, gain should remain at minimum
    assert gain == 0.0
