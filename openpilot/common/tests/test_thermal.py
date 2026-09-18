from unittest.mock import Mock, mock_open

import pytest

from openpilot.common.hardware import base
from openpilot.common.swaglog import cloudlog


@pytest.mark.parametrize('elapsed', [.05, 1.5])
def test_thermal_read_preserves_value_and_identifies_slow_sensor(monkeypatch, elapsed):
  sensor = base.ThermalZone('cpu0-gold-usr')
  sensor.zone_number = 7
  read = mock_open(read_data='62000')
  report = Mock()
  monkeypatch.setattr(base, 'open', read, raising=False)
  monkeypatch.setattr(base.time, 'monotonic', Mock(side_effect=[0., elapsed]))
  monkeypatch.setattr(cloudlog, 'event', report)
  assert sensor.read() == 62.
  read.assert_called_once_with('/sys/devices/virtual/thermal/thermal_zone7/temp')
  if elapsed > 1.:
    report.assert_called_once_with('Thermal sensor read slow', sensor='cpu0-gold-usr', zone=7, elapsed=elapsed, error=True)
  else:
    report.assert_not_called()


def test_slow_thermal_failure_is_reported_without_hiding_error(monkeypatch):
  sensor = base.ThermalZone('memory')
  sensor.zone_number = 8
  monkeypatch.setattr(base, 'open', Mock(side_effect=OSError('sensor read failed')), raising=False)
  monkeypatch.setattr(base.time, 'monotonic', Mock(side_effect=[0., 2.]))
  report = Mock()
  monkeypatch.setattr(cloudlog, 'event', report)
  with pytest.raises(OSError, match='sensor read failed'):
    sensor.read()
  report.assert_called_once_with('Thermal sensor read slow', sensor='memory', zone=8, elapsed=2., error=True)
