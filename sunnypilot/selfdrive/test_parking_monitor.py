#!/usr/bin/env python3
import pytest

from openpilot.sunnypilot.selfdrive.parking_monitor import ParkingMonitor


@pytest.fixture
def monitor(mocker):
  mocker.patch('openpilot.sunnypilot.selfdrive.parking_monitor.messaging')
  return ParkingMonitor()


def test_is_parked_no_ignition(monitor, mocker):
  mock_state = mocker.Mock()
  mock_state.ignitionLine = False
  monitor.sm = {'pandaStates': [mock_state]}
  monitor.sm.valid = {'pandaStates': True}

  assert monitor.is_parked()


def test_is_parked_with_ignition(monitor, mocker):
  mock_state = mocker.Mock()
  mock_state.ignitionLine = True
  monitor.sm = {'pandaStates': [mock_state]}
  monitor.sm.valid = {'pandaStates': True}

  assert not monitor.is_parked()


def test_detect_shock_below_threshold(monitor, mocker):
  mock_accel = mocker.Mock()
  mock_accel.acceleration.v = [0.5, 0.5, 9.81]  # ~1.0g total
  monitor.sm = {'accelerometer': mock_accel}
  monitor.sm.valid = {'accelerometer': True}

  shock, magnitude = monitor.detect_shock()
  assert not shock
  assert magnitude < 2.0


def test_detect_shock_above_threshold(monitor, mocker):
  mock_accel = mocker.Mock()
  mock_accel.acceleration.v = [10.0, 10.0, 9.81]  # >2.0g total
  monitor.sm = {'accelerometer': mock_accel}
  monitor.sm.valid = {'accelerometer': True}

  shock, magnitude = monitor.detect_shock()
  assert shock
  assert magnitude > 2.0


def test_check_battery_voltage_normal(monitor, mocker):
  mock_device = mocker.Mock()
  mock_device.batteryVoltage = 12.5
  monitor.sm = {'deviceState': mock_device}
  monitor.sm.valid = {'deviceState': True}

  voltage = monitor.check_battery_voltage()
  assert abs(voltage - 12.5) < 0.01


def test_should_shutdown_low_voltage(monitor, mocker):
  mock_device = mocker.Mock()
  mock_device.batteryVoltage = 11.5  # Below 11.8V threshold
  monitor.sm = {'deviceState': mock_device}
  monitor.sm.valid = {'deviceState': True}

  assert monitor.should_shutdown()


def test_should_shutdown_max_duration(monitor, mocker):
  mock_device = mocker.Mock()
  mock_device.batteryVoltage = 12.5
  monitor.sm = {'deviceState': mock_device}
  monitor.sm.valid = {'deviceState': True}

  monitor.parking_start_time = 0
  mocker.patch('time.monotonic', return_value=13 * 3600)  # 13 hours
  assert monitor.should_shutdown()
