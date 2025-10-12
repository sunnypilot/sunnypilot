#!/usr/bin/env python3
import pytest
from unittest.mock import Mock

from openpilot.sunnypilot.selfdrive.parking_monitor import ParkingMonitor


@pytest.fixture
def monitor(mocker):
  mocker.patch('openpilot.sunnypilot.selfdrive.parking_monitor.messaging')
  pm = ParkingMonitor()
  # Mock the SubMaster object properly
  pm.sm = Mock()
  return pm


def test_is_parked_ignition_off_and_standstill(monitor):
  # Car is parked: ignition is off and speed is zero
  monitor.sm['pandaStates'].__iter__.return_value = [Mock(ignitionLine=False)]
  monitor.sm['carState'].vEgo = 0.1
  monitor.sm.valid = {'pandaStates': True, 'carState': True}

  assert monitor.is_parked() is True


def test_is_parked_ignition_on(monitor):
  # Car is not parked: ignition is on
  monitor.sm['pandaStates'].__iter__.return_value = [Mock(ignitionLine=True)]
  monitor.sm['carState'].vEgo = 0.0
  monitor.sm.valid = {'pandaStates': True, 'carState': True}

  assert monitor.is_parked() is False


def test_is_parked_moving(monitor):
  # Car is not parked: moving, even if ignition is off
  monitor.sm['pandaStates'].__iter__.return_value = [Mock(ignitionLine=False)]
  monitor.sm['carState'].vEgo = 1.0
  monitor.sm.valid = {'pandaStates': True, 'carState': True}

  assert monitor.is_parked() is False


def test_detect_shock_below_threshold(monitor):
  # Simulates accelerometer data that is below the shock threshold
  monitor.sm['accelerometer'].acceleration.v = [0.5, 0.5, 9.81]  # ~1.0g total
  monitor.sm.valid = {'accelerometer': True}

  # We need to mock a calibrated state for this test
  monitor.mean_accel = [0.0, 0.0, 9.81]
  monitor.cov_inv_accel = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

  shock, _ = monitor.detect_shock_mahalanobis()
  assert shock is False


def test_detect_shock_above_threshold(monitor):
  # Simulates accelerometer data that is above the shock threshold
  monitor.sm['accelerometer'].acceleration.v = [15.0, 15.0, 9.81]  # High deviation
  monitor.sm.valid = {'accelerometer': True}

  # We need to mock a calibrated state for this test
  monitor.mean_accel = [0.0, 0.0, 9.81]
  monitor.cov_inv_accel = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

  shock, _ = monitor.detect_shock_mahalanobis()
  assert shock is True


def test_check_battery_voltage_normal(monitor):
  # Battery voltage is normal
  monitor.sm['deviceState'].batteryVoltage = 12.5
  monitor.sm.valid = {'deviceState': True}

  voltage = monitor.check_battery_voltage()
  assert abs(voltage - 12.5) < 0.01


def test_should_shutdown_low_voltage(monitor):
  # Shutdown condition: low voltage
  monitor.sm['deviceState'].batteryVoltage = 11.5  # Below 11.8V threshold
  monitor.sm.valid = {'deviceState': True}

  assert monitor.should_shutdown() is True


def test_should_shutdown_max_duration(monitor, mocker):
  # Shutdown condition: max parking duration exceeded
  monitor.sm['deviceState'].batteryVoltage = 12.5
  monitor.sm.valid = {'deviceState': True}

  monitor.parking_start_time = 0
  mocker.patch('time.monotonic', return_value=13 * 3600)  # 13 hours
  assert monitor.should_shutdown() is True