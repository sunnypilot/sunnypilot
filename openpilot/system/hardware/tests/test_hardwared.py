import fcntl
import queue
import threading
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import Mock, mock_open

import pytest

from openpilot.system.hardware import hardwared
from openpilot.common.params import Params


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
  report.assert_called_once_with('Hardware loop slow stage', stage='system_stats', elapsed=5., error=True)


@pytest.mark.parametrize('elapsed,error', [(.2, False), (1.2, True)])
def test_long_health_stalls_are_included_in_quick_logs(monkeypatch, elapsed, error):
  report = Mock()
  monkeypatch.setattr(hardwared.time, 'monotonic', lambda: elapsed)
  monkeypatch.setattr(hardwared.cloudlog, 'event', report)
  hardwared.log_slow_hardware_stage('power_draw_read', 0.)
  # logmessaged copies ERROR events to errorLogMessage, which is in qlogs.
  report.assert_called_once_with('Hardware loop slow stage', stage='power_draw_read', elapsed=elapsed, error=error)


@pytest.fixture
def health_loop(monkeypatch):
  """Run the production loop with a deterministic clock and peripheral inputs."""
  clock = SimpleNamespace(now=10.)
  inputs = SimpleNamespace(update=lambda: None)
  hw_queue = queue.Queue()
  end = threading.Event()
  sent = []
  writes = []
  values = {'HasAcceptedTerms': hardwared.terms_version, 'HasAcceptedTermsSP': hardwared.terms_version_sp,
            'CompletedTrainingVersion': hardwared.training_version, 'UptimeOffroad': 0., 'UptimeOnroad': 0.}
  stalled_keys = set()

  def put(key, value, block=False):
    writes.append((key, value, block))
    # Model the persisted-write delay seen in route 183. A queued write does
    # not consume time in this thread, even when disk persistence is stalled.
    if block and key in stalled_keys:
      clock.now += 5.5
    values[key] = value

  params = Mock(get=lambda key, **kwargs: values.get(key), get_bool=lambda key: bool(values.get(key)), put=put, put_bool=put)
  sm = {
    'pandaStates': [hardwared.log.PandaState.new_message(pandaType='dos', ignitionLine=True, harnessStatus='normal')],
    'peripheralState': hardwared.log.PeripheralState.new_message(pandaType='dos', voltage=12000),
    'selfdriveState': hardwared.log.SelfdriveState.new_message(),
    'gpsLocationExternal': hardwared.log.GpsLocationData.new_message(),
    'chestnutState': hardwared.log.ChestnutState.new_message(),
  }

  class SubMaster(dict):
    frame = 0
    updated = defaultdict(lambda: True)
    alive = defaultdict(lambda: False)
    valid = defaultdict(lambda: True)

    def update(self, timeout):
      clock.now += hardwared.DT_HW
      self.frame += round(hardwared.SERVICE_LIST['pandaStates'].frequency * hardwared.DT_HW)
      self['selfdriveState'].enabled = len(sent) % 4 in (1, 2)
      inputs.update()

  def publish(service, message):
    assert service == 'deviceState'
    sent.append((clock.now, message.to_dict()))
    if len(sent) == 125:  # includes the periodic one-minute uptime save
      end.set()

  hw = Mock()
  hw.get_device_type.return_value = 'mici'
  hw.get_thermal_config.return_value.get_msg.return_value = {'cpuTempC': [60.] * 8, 'gpuTempC': [60.], 'memoryTempC': 60.}
  hw.get_screen_brightness.return_value = 50
  hw.get_gpu_usage_percent.return_value = 10
  hw.get_current_power_draw.return_value = 5
  hw.get_som_power_draw.return_value = 3
  hw.booted.return_value = True
  monkeypatch.setattr(hardwared, 'HARDWARE', hw)
  monkeypatch.setattr(hardwared, 'Params', lambda: params)
  monkeypatch.setattr(hardwared, 'get_short_branch', lambda: 'test')
  monkeypatch.setattr(hardwared, 'get_build_metadata', lambda: SimpleNamespace(channel='test', channel_type='test'))
  monkeypatch.setattr(hardwared, 'get_available_percent', lambda **kwargs: 50.)
  monkeypatch.setattr(hardwared, 'set_offroad_alert_if_changed', Mock())
  monkeypatch.setattr(hardwared, 'Chestnut', Mock())
  monkeypatch.setattr(hardwared, 'ChestnutStatus', Mock())
  monkeypatch.setattr(hardwared, 'statlog', Mock())
  monkeypatch.setattr(hardwared, 'cloudlog', Mock())
  monkeypatch.setattr(hardwared, 'open', mock_open(), raising=False)
  monkeypatch.setattr(hardwared, 'LinuxSystemStats', lambda: Mock(memory_usage_percent=lambda: 50., cpu_usage_percent=lambda: [20.] * 8))
  monkeypatch.setattr(hardwared, 'PowerMonitoring', lambda: Mock(get_power_used=lambda: 0, get_car_battery_capacity=lambda: 1000,
                                                             should_shutdown=lambda *args: False))
  monkeypatch.setattr(hardwared.time, 'monotonic', lambda: clock.now)
  monkeypatch.setattr(hardwared.messaging, 'SubMaster', lambda *args, **kwargs: SubMaster(sm))
  monkeypatch.setattr(hardwared.messaging, 'PubMaster', lambda *args: Mock(send=publish))
  return SimpleNamespace(run=lambda: hardwared.hardware_thread(end, hw_queue), sent=sent, writes=writes,
                         stalled_keys=stalled_keys, hw=hw, params=params, values=values, sm=sm, inputs=inputs, queue=hw_queue)


@pytest.mark.parametrize('key', ['IsEngaged', 'UptimeOnroad', 'UptimeOffroad', 'LastOffroadStatusPacket'])
def test_persistence_cannot_stall_health_heartbeat(health_loop, key):
  health_loop.stalled_keys.add(key)
  health_loop.run()
  times = [t for t, _ in health_loop.sent]
  assert max(b - a for a, b in zip(times[:-1], times[1:], strict=True)) <= hardwared.DT_HW
  assert any(k == key for k, _, _ in health_loop.writes)
  assert all(msg['valid'] for _, msg in health_loop.sent)
  assert health_loop.sent[-1][1]['deviceState']['started']


def test_steady_hardware_flags_do_not_keep_writing_to_disk(health_loop):
  health_loop.run()
  for key in ('NetworkMetered', 'GithubRunnerSufficientVoltage'):
    assert len([w for w in health_loop.writes if w[0] == key]) == 1
  # Keep the periodic uptime accounting and every engagement edge.
  assert len([w for w in health_loop.writes if w[0] == 'UptimeOnroad']) == 2
  engaged = [v for k, v, _ in health_loop.writes if k == 'IsEngaged']
  assert True in engaged and False in engaged


def test_slow_persistence_does_not_bypass_overtemperature(health_loop):
  health_loop.stalled_keys.update(('IsEngaged', 'UptimeOnroad'))
  health_loop.hw.get_thermal_config.return_value.get_msg.return_value = {'cpuTempC': [120.] * 8, 'gpuTempC': [120.], 'memoryTempC': 120.}
  health_loop.run()
  assert not any(msg['deviceState']['started'] for _, msg in health_loop.sent)
  assert health_loop.sent[-1][1]['deviceState']['thermalStatus'] == 'critical'
  assert health_loop.sent[-1][1]['deviceState']['fanSpeedPercentDesired'] == 100


def test_hardware_flags_still_persist_each_transition(health_loop):
  def update():
    if len(health_loop.sent) in (10, 20):
      metered = len(health_loop.sent) == 10
      health_loop.sm['peripheralState'].voltage = 5000 if metered else 12000
      health_loop.queue.put(hardwared.HardwareState(
        network_type=hardwared.NetworkType.wifi, network_info=None, network_metered=metered,
        network_strength=hardwared.NetworkStrength.unknown, network_stats={'wwanTx': -1, 'wwanRx': -1},
        modem_temps=[], usb_state=[],
      ))
  health_loop.inputs.update = update
  health_loop.run()
  assert [v for k, v, _ in health_loop.writes if k == 'NetworkMetered'] == [False, True, False]
  assert [v for k, v, _ in health_loop.writes if k == 'GithubRunnerSufficientVoltage'] == [True, False, True]


def test_health_loop_keeps_publishing_while_real_params_lock_is_held(health_loop, tmp_path):
  # Exercise the native writer and its real cross-process lock, not only a
  # simulated delay. The previous blocking call stops before the first publish.
  params = Params(str(tmp_path))
  health_loop.params.put = params.put
  health_loop.params.put_bool = params.put_bool
  done = threading.Event()
  failures = []

  def run():
    try:
      health_loop.run()
    except Exception as exc:
      failures.append(exc)
    finally:
      done.set()

  with (tmp_path / '.lock').open('w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    worker = threading.Thread(target=run)
    worker.start()
    try:
      completed_while_locked = done.wait(2.)
      published_while_locked = len(health_loop.sent)
    finally:
      fcntl.flock(lock, fcntl.LOCK_UN)
      worker.join(5.)
  assert not worker.is_alive()
  assert not failures
  assert completed_while_locked and published_while_locked == 125
  params.flush()
  assert params.get('UptimeOnroad') > 0
  assert params.get_bool('GithubRunnerSufficientVoltage')
  assert not params.get_bool('IsEngaged')  # last edge is retained in write order
