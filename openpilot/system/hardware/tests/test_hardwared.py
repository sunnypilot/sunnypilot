from unittest.mock import Mock

import pytest

from openpilot.system.hardware import hardwared


@pytest.fixture(autouse=True)
def clear_alert_cache(monkeypatch):
  monkeypatch.setattr(hardwared, 'prev_offroad_states', {})


def test_hidden_alert_does_not_repeat_blocking_param_operation(monkeypatch):
  persist = Mock()
  monkeypatch.setattr(hardwared, 'set_offroad_alert', persist)
  # The first call must remove an alert left by a previous process.
  hardwared.set_offroad_alert_if_changed('Offroad_TemperatureTooHigh', False, '42.0C')
  persist.assert_called_once_with('Offroad_TemperatureTooHigh', False, None)
  # An unrelated writer may now hold the shared Params lock. Hidden temperature
  # changes must not touch it again, nor delay the deviceState heartbeat.
  persist.side_effect = AssertionError('Unexpected blocking Params operation')
  for temp in ('42.1C', '42.2C', '45.0C'):
    hardwared.set_offroad_alert_if_changed('Offroad_TemperatureTooHigh', False, temp)


def test_visible_alert_text_and_clear_still_persist(monkeypatch):
  persist = Mock()
  monkeypatch.setattr(hardwared, 'set_offroad_alert', persist)
  for show, text in [(False, '42C'), (True, '107C'), (True, '107C'), (True, '108C'), (False, '90C')]:
    hardwared.set_offroad_alert_if_changed('Offroad_TemperatureTooHigh', show, text)
  assert [call.args for call in persist.call_args_list] == [
    ('Offroad_TemperatureTooHigh', False, None),
    ('Offroad_TemperatureTooHigh', True, '107C'),
    ('Offroad_TemperatureTooHigh', True, '108C'),
    ('Offroad_TemperatureTooHigh', False, None),
  ]


def test_failed_alert_write_is_retried(monkeypatch):
  persist = Mock(side_effect=[OSError('write failed'), None])
  monkeypatch.setattr(hardwared, 'set_offroad_alert', persist)
  with pytest.raises(OSError):
    hardwared.set_offroad_alert_if_changed('Offroad_TiciSupport', False)
  hardwared.set_offroad_alert_if_changed('Offroad_TiciSupport', False)
  assert persist.call_count == 2


def test_stage_timing_reports_slow_stage_only(monkeypatch):
  report = Mock()
  monkeypatch.setattr(hardwared.cloudlog, 'event', report)
  monkeypatch.setattr(hardwared.time, 'monotonic', Mock(side_effect=[1.05, 6.05, 6.07]))
  start = hardwared.log_slow_hardware_stage('thermal_read', 1.)
  start = hardwared.log_slow_hardware_stage('system_stats', start)
  hardwared.log_slow_hardware_stage('chestnut_status', start)
  report.assert_called_once_with('Hardware loop slow stage', stage='system_stats', elapsed=5.)
