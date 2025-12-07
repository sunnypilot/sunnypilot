import time
import pytest
import threading
import tracemalloc

from openpilot.common.params import Params
from openpilot.common.params_pyx import UnknownKeyName

from openpilot.sunnypilot.common.param_watcher import ParamWatcher, IN_MODIFY


class TestParamWatcher:
  BYTES_KEYS = ["LocationFilterInitialState", "UpdaterCurrentReleaseNotes", "UpdaterNewReleaseNotes"]
  BOOL_KEYS = [
    "IsMetric", "AdbEnabled", "AlwaysOnDM", "ExperimentalMode",
    "ExperimentalModeConfirmed", "DisengageOnAccelerator",
    "OpenpilotEnabledToggle", "RecordAudio", "RecordFront"
  ]
  _key_counter = 0

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.params = Params()
    self.key_index = TestParamWatcher._key_counter
    TestParamWatcher._key_counter += 1
    self.bytes_key = self.BYTES_KEYS[self.key_index % len(self.BYTES_KEYS)]
    self.bool_key = self.BOOL_KEYS[self.key_index % len(self.BOOL_KEYS)]

  @pytest.fixture
  def param_watcher(self):
    ParamWatcher._instance = None
    param_watch = ParamWatcher()
    param_watch._cache = {}
    param_watch._last_trigger = {}
    param_watch._version = {}
    param_watch._callbacks = []
    param_watch.start()
    assert param_watch.is_watching(), "ParamWatcher thread died"
    return param_watch

  def teardown_method(self):
    for key in (self.bytes_key, self.bool_key):
      try:
        self.params.remove(key)
      except UnknownKeyName:
        pass

  def test_watcher_detects_change(self, param_watcher):
    val = b"123"
    self.params.put(self.bytes_key, val)
    assert param_watcher.get(self.bytes_key) == val

  def test_watcher_get_bool(self, param_watcher):
    self.params.put_bool(self.bool_key, True)
    assert param_watcher.get_bool(self.bool_key) is True  # First read should populate internal cache

  def test_performance_comparison(self, param_watcher):
    plain_params = self.params

    for key in self.BYTES_KEYS:
      plain_params.put(key, b"x" * 10000)
      param_watcher.get(key)
    for key in self.BOOL_KEYS:
      plain_params.put_bool(key, True)
      param_watcher.get_bool(key)

    def bench(get_bytes, get_bool):
      tracemalloc.start()
      start_time = time.process_time()
      for _ in range(1000):
        for key in self.BYTES_KEYS:
          get_bytes(key)
        for key in self.BOOL_KEYS:
          get_bool(key)
      duration = time.process_time() - start_time
      _, memory = tracemalloc.get_traced_memory()
      tracemalloc.stop()
      return duration, memory

    plain_cpu, plain_memory = bench(plain_params.get, plain_params.get_bool)
    watcher_cpu, watcher_memory = bench(param_watcher.get, param_watcher.get_bool)

    # ParamWatcher *should* be significantly faster and use less memory than Params()
    assert watcher_cpu < plain_cpu * 0.6, f"PW CPU ({watcher_cpu:.4f}s) should be < 60% of Param call ({plain_cpu:.4f}s)"
    assert watcher_memory < plain_memory * 0.5, f"PW Memory ({watcher_memory}B) should be < 50% of Param call ({plain_memory}B)"

  def test_cache_invalidation_simulation(self, param_watcher):
    self.params.put(self.bytes_key, b"old")
    assert param_watcher.get(self.bytes_key) == b"old"
    time.sleep(0.2)

    event = threading.Event()
    param_watcher.add_watcher(lambda key, mask: event.set())
    param_watcher._trigger_callbacks(self.bytes_key, IN_MODIFY)
    assert event.wait(timeout=2), "Callback not triggered"

    self.params.put(self.bytes_key, b"new")
    assert param_watcher.get(self.bytes_key) == b"new"
