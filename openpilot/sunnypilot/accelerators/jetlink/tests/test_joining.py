"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The rules the late join has to keep.

Both model states are fakes; the joining state is plumbing around them. What
is pinned: modeld gets a working model immediately, a swap never lands on an
engaged frame, a large model that dies mid-drive falls back without losing the
frame, and a small-model failure still belongs to modeld.
"""
import re
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from openpilot.common.basedir import BASEDIR

from openpilot.sunnypilot.accelerators.jetlink.joining import STABLE_SECONDS, JoiningModelState


class FakeModel:
  def __init__(self, name, chestnut=False, client=None):
    self.name = name
    self.chestnut = chestnut
    self.client = client
    self.lat_delay = 0.0
    self.vision_input_names = ['img', 'big_img']
    self.calls = 0
    self.raises = None
    self.closed = False
    self.warmed = False

  def run(self, bufs, transforms, inputs, after_enqueue=None):
    self.calls += 1
    if self.raises is not None:
      raise self.raises
    return {'from': self.name}

  def warmup(self):
    self.warmed = True

  def close(self):
    self.closed = True


class JoiningTest(unittest.TestCase):
  def setUp(self):
    # The engagement watcher is the one part that needs msgq. Drive the flag by
    # hand instead; what it reads is covered by selfdrived's own tests.
    patcher = mock.patch.object(JoiningModelState, '_watch_engagement', lambda self: None)
    patcher.start()
    self.addCleanup(patcher.stop)

    # The join reports progress through a param. Mocked so this can never
    # reach a live params directory, conftest or no conftest.
    self.progress = mock.Mock()
    patcher = mock.patch('openpilot.sunnypilot.accelerators.jetlink.joining.accelerators', self.progress)
    patcher.start()
    self.addCleanup(patcher.stop)

    self.small = FakeModel('small')
    self.big = FakeModel('big', chestnut=True, client=object())
    self.joined = threading.Event()
    self.connect_calls = 0
    self.connect_error = None

  def _connect(self):
    self.connect_calls += 1
    if self.connect_error is not None:
      raise self.connect_error
    self.joined.set()
    # A link the joining state may have to close on its own, when it is torn
    # down holding a join that never found a disengaged frame to land on.
    return (mock.MagicMock(name='client'), 'spec')

  def _build(self, client, spec):
    return self.big

  def _state(self):
    s = JoiningModelState(1928, 1208, self.small, self._connect, self._build)
    self.addCleanup(s.close)
    return s

  def _wait_joined(self, s, timeout=5.0):
    # connect() returning is not publication: wait for the owner to hand off.
    deadline = time.monotonic() + timeout
    while s._joined is None and time.monotonic() < deadline:
      time.sleep(0.001)
    self.assertIsNotNone(s._joined)

  def _run(self, s):
    s._engagement_updated = time.monotonic()
    return s.run({}, {}, {})

  def test_stalled_watcher_cannot_leave_a_swap_window_open(self):
    s = self._state()
    s._engaged, s._standstill = False, True
    s._engagement_updated = time.monotonic() - 1.0
    self.assertFalse(s._window_open)

  def test_missing_or_invalid_messages_close_both_swap_windows(self):
    from types import SimpleNamespace
    sm = mock.MagicMock()
    states = {'selfdriveState': SimpleNamespace(enabled=False), 'carState': SimpleNamespace(standstill=True),
              'carControl': SimpleNamespace(latActive=False, longActive=False)}
    sm.__getitem__.side_effect = states.__getitem__
    s = self._state()
    for failed in states:
      for check in ('seen', 'alive', 'valid'):
        sm.seen = dict.fromkeys(states, True)
        sm.alive = sm.seen.copy()
        sm.valid = sm.seen.copy()
        s._update_engagement(sm)
        self.assertTrue(s._window_open)
        getattr(sm, check)[failed] = False
        # No updated flag: liveness expiry must still close the window.
        s._update_engagement(sm)
        self.assertFalse(s._window_open)
    sm.seen = dict.fromkeys(states, True)
    sm.alive = sm.seen.copy()
    sm.valid = sm.seen.copy()
    states['carState'].standstill = False
    for active in ('latActive', 'longActive'):
      states['carControl'].latActive = active == 'latActive'
      states['carControl'].longActive = active == 'longActive'
      s._update_engagement(sm)
      self.assertFalse(s._window_open)

  def test_runs_the_small_model_immediately(self):
    s = self._state()
    # No waiting on a link: this is the whole point.
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertFalse(s.chestnut)
    self.assertIsNone(s.client)

  def test_does_not_swap_while_engaged_and_moving(self):
    s = self._state()
    self._wait_joined(s)
    s._engaged, s._standstill = True, False
    for _ in range(3):
      self.assertEqual(self._run(s), {'from': 'small'})
    self.assertFalse(s.chestnut)
    self.assertFalse(self.big.warmed)

  def test_does_not_swap_at_a_standstill_while_engaged(self):
    # Even stopped, longitudinal control can hold the brake or request motion.
    s = self._state()
    self._wait_joined(s)
    s._engaged, s._standstill = True, True
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertFalse(s.chestnut)

  def test_a_standstill_the_car_stopped_reporting_is_not_a_window(self):
    # sm.alive goes false when carState stops arriving. A stale "stopped" must
    # not open a window on a car that is actually moving.
    s = self._state()
    self._wait_joined(s)
    s._engaged, s._standstill = True, False
    self.assertEqual(self._run(s), {'from': 'small'})

  def test_late_boot_announces_availability_without_switching(self):
    booted = threading.Event()
    connect = self._connect

    def after_boot():
      if not booted.wait(5):
        raise RuntimeError('test boot timeout')
      return connect()

    self._connect = after_boot
    s = self._state()
    self.addCleanup(booted.set)
    self.assertFalse(s.big_model_available)
    self.assertEqual(self._run(s), {'from': 'small'})
    booted.set()
    self._wait_joined(s)
    self.assertTrue(s.big_model_available)
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertTrue(s.loading)
    self.assertEqual(s.big_model_state, 'joining')
    s._engaged = False
    self.assertEqual(self._run(s), {'from': 'big'})
    self.assertFalse(s.big_model_available)
    self.assertEqual(s.big_model_state, 'running')

  def test_availability_survives_ping_but_not_link_loss(self):
    pinging, release = threading.Event(), threading.Event()
    client = mock.MagicMock()

    def ping(**kwargs):
      pinging.set()
      release.wait(5)
      raise RuntimeError('link lost while waiting to switch')

    client.ping.side_effect = ping
    self._connect = lambda: (client, 'spec')
    with mock.patch('openpilot.sunnypilot.accelerators.jetlink.joining.KEEPALIVE_PERIOD', 0.01):
      s = self._state()
      self.addCleanup(release.set)
      self.assertTrue(pinging.wait(5))
      self.assertIsNone(s._joined)
      self.assertTrue(s.big_model_available)
      self.assertEqual(self._run(s), {'from': 'small'})
      release.set()
      deadline = time.monotonic() + 2
      while s.big_model_available and time.monotonic() < deadline:
        time.sleep(0.001)
      self.assertFalse(s.big_model_available)
      self.assertFalse(s.chestnut)

  def test_ping_taking_the_pending_link_during_swap_check_keeps_availability(self):
    s = self._state()
    self._wait_joined(s)
    joined = s._joined
    s._engaged = False
    # The frame sees _joined before locking, then the keepalive takes it.
    with mock.patch.object(s, '_lock') as lock:
      lock.__enter__.side_effect = lambda: setattr(s, '_joined', None)
      self.assertEqual(self._run(s), {'from': 'small'})
      self.assertTrue(s.big_model_available)
    s._joined = joined

  def test_close_with_pending_model_clears_availability(self):
    s = self._state()
    self._wait_joined(s)
    self.assertTrue(s.big_model_available)
    s.close()
    self.assertFalse(s.big_model_available)

  def test_swaps_on_a_disengaged_frame(self):
    s = self._state()
    self._wait_joined(s)
    s._engaged = False
    self.assertEqual(self._run(s), {'from': 'big'})
    self.assertTrue(s.chestnut)
    self.assertIs(s.client, self.big.client)
    # No warmup at the swap: the warp was prepared in __init__ and a frame
    # over the link here was two dropped camera frames on the car.
    self.assertFalse(self.big.warmed)

  def test_large_model_failure_demotes_and_keeps_the_frame(self):
    s = self._state()
    self._wait_joined(s)
    s._engaged = False
    self._run(s)
    self.assertTrue(s.chestnut)

    self.big.raises = RuntimeError("link gone")
    # modeld still gets an output for this frame, from the small model.
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertFalse(s.chestnut)
    for _ in range(100):
      if self.big.closed:
        break
      time.sleep(0.01)
    self.assertTrue(self.big.closed)
    # And it tries again rather than staying small for the rest of the drive.
    self.assertTrue(s._rejoin_at > time.monotonic() or self.connect_calls > 1)

  def test_failed_first_inference_never_announces_ready(self):
    s = self._state()
    self._wait_joined(s)
    s._engaged = False
    self.big.raises = RuntimeError('first inference failed')
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertTrue(s.loading)
    self.assertEqual(s.big_model_state, 'retrying')
    self.assertFalse(s.big_model_available)
    self.progress.clear_progress.assert_not_called()

  def test_fallback_resets_history_without_waiting_for_teardown(self):
    entered, release = threading.Event(), threading.Event()
    reset = mock.Mock()

    def close():
      entered.set()
      release.wait(2)

    self.big.close = close
    s = JoiningModelState(1928, 1208, self.small, self._connect, self._build, reset_small=reset)
    self.addCleanup(s.close)
    self.addCleanup(release.set)
    self._wait_joined(s)
    s._engaged = False
    self._run(s)
    self.big.raises = RuntimeError('failed')
    run = self.small.run

    def small_run(*args):
      reset.assert_called_once()
      return run(*args)

    self.small.run = small_run
    self.assertEqual(self._run(s), {'from': 'small'})
    self.assertTrue(entered.wait(1))
    self.assertFalse(release.is_set())

  def test_ready_is_announced_only_after_inference_returns(self):
    s = self._state()
    self._wait_joined(s)
    s._engaged = False
    run = self.big.run

    def inspect(*args):
      # Swapped in, but not announced: the first frame has not returned yet.
      self.assertTrue(s._loading)
      self.progress.clear_progress.assert_not_called()
      return run(*args)

    self.big.run = inspect
    self.assertEqual(self._run(s), {'from': 'big'})
    self.assertFalse(s._loading)
    self.progress.clear_progress.assert_called_once()

  def test_prepare_failure_uses_startup_fallback_not_a_slow_swap(self):
    order = []
    self.connect_calls = 0

    def prepare():
      order.append('prepare')
      raise RuntimeError("no warp today")

    with self.assertRaisesRegex(RuntimeError, 'no warp today'):
      JoiningModelState(1928, 1208, self.small, self._connect, self._build, prepare)
    # Ran, and ran before anything else: modeld's main thread is blocked for
    # exactly as long as the constructor takes, so this is the only place the
    # GPU work can go without costing a frame.
    self.assertEqual(order, ['prepare'])
    self.assertEqual(self.connect_calls, 0)
    self.assertFalse(self.big.warmed)

  def test_loading_has_no_deadline(self):
    # no 60 s edge: selfdrived gates on it only while nothing publishes modelV2,
    # so a Jetson that takes a whole drive stays "getting ready"
    self.connect_error = RuntimeError("jetson still booting")
    s = self._state()
    self._run(s)
    with mock.patch('openpilot.sunnypilot.accelerators.jetlink.joining.time.monotonic',
                    return_value=time.monotonic() + 600.0):
      self._run(s)
    self.assertTrue(s.loading)
    self.assertEqual(s.big_model_state, 'joining')
    # A join that succeeds later still swaps.
    self.connect_error = None
    s._rejoin.set()
    self._wait_joined(s, 10.0)
    s._engaged = False
    for _ in range(20):
      if self._run(s) == {'from': 'big'}:
        break
      time.sleep(0.05)
    self.assertTrue(s.chestnut)
    self.assertFalse(s.loading)

  def test_state_travels_in_the_message_not_in_params(self):
    # a chestnut's load is over once; this never is, so selfdrived's edge is
    # modelV2.big turning true and the UI reads acceleratorState
    s = self._state()
    self.assertTrue(s.loading)
    self.assertEqual(s.big_model_state, 'joining')

    self._wait_joined(s)
    s._engaged = False
    self._run(s)
    self.assertFalse(s.loading)
    self.assertTrue(s.chestnut)
    self.assertEqual(s.big_model_state, 'running')

    self.big.raises = RuntimeError("link gone")
    self._run(s)
    self.assertTrue(s.loading)
    self.assertFalse(s.chestnut)
    self.assertEqual(s.big_model_state, 'retrying')
    self.progress.report_progress.assert_called_with('connect', 0.0, 'lost the jetson, reconnecting')

    s.close()
    self.assertEqual(s.big_model_state, 'unavailable')

  def test_build_failure_backs_off(self):
    self._build = mock.Mock(side_effect=RuntimeError("no warp"))
    s = JoiningModelState(1928, 1208, self.small, self._connect, self._build)
    self.addCleanup(s.close)
    self._wait_joined(s)
    s._engaged = False
    self.assertEqual(self._run(s), {'from': 'small'})
    # Not straight back onto the link: the next attempt waits REJOIN_DELAY.
    self.assertGreater(s._rejoin_at, time.monotonic() + 1.0)
    self.assertTrue(s.loading)
    self.assertEqual(s.big_model_state, 'retrying')

  def test_a_link_that_dies_before_the_swap_is_reopened(self):
    # a link waits in _joined for a window, which on a drive with no stop is the
    # whole drive; a Jetson that reboots in there must be caught before the swap
    clients = []

    def connect():
      c = mock.MagicMock(name='client')
      clients.append(c)
      self.connect_calls += 1
      self.joined.set()
      return (c, 'spec')

    self._connect = connect
    with mock.patch('openpilot.sunnypilot.accelerators.jetlink.joining.KEEPALIVE_PERIOD', 0.05), \
         mock.patch('openpilot.sunnypilot.accelerators.jetlink.joining.REJOIN_DELAY', 0.05):
      s = self._state()
      self._wait_joined(s)
      # Never a window, so nothing consumes it; the ping is what notices.
      s._engaged, s._standstill = True, False
      clients[0].ping.side_effect = RuntimeError("jetson rebooted")
      for _ in range(100):
        if len(clients) > 1:
          break
        time.sleep(0.05)
      self.assertGreater(len(clients), 1, "a dead pending link was never reopened")
      clients[0].close.assert_called()
      # And the fresh one is what the window eventually gets.
      s._engaged = False
      for _ in range(40):
        if self._run(s) == {'from': 'big'}:
          break
        time.sleep(0.05)
      self.assertTrue(s.chestnut)

  def test_failures_back_off_and_a_stable_join_starts_over(self):
    # A link that dies on its first frame every time used to cost a swap, a
    # demote, a soft disable and a chime every REJOIN_DELAY for the drive.
    s = self._state()
    s._joined_at = 0.0
    delays = []
    for _ in range(5):
      t = time.monotonic()
      s._back_off()
      delays.append(round(s._rejoin_at - t))
    self.assertEqual(delays, [5, 10, 20, 40, 60])

    # A join that held is not that link, and must not inherit its delay: a
    # Jetson that reboots once an hour should be picked up in REJOIN_DELAY.
    s._joined_at = time.monotonic() - (STABLE_SECONDS + 1)
    t = time.monotonic()
    s._back_off()
    self.assertEqual(round(s._rejoin_at - t), 5)

  def test_small_model_failure_is_modelds(self):
    s = self._state()
    self.small.raises = RuntimeError("vipc gone")
    with self.assertRaises(RuntimeError):
      self._run(s)

  def test_lat_delay_reaches_both_models(self):
    s = self._state()
    s.lat_delay = 0.25
    self.assertEqual(self.small.lat_delay, 0.25)
    self._wait_joined(s)
    s._engaged = False
    self._run(s)
    self.assertEqual(self.big.lat_delay, 0.25)


  def test_reports_loading_until_it_joins(self):
    # the UI reads this to tell "not up yet" from "failed"; modelV2.big is
    # false for the whole join
    s = self._state()
    self._run(s)
    self.assertTrue(s.loading)

    self._wait_joined(s)
    s._engaged = False
    self._run(s)
    self.assertFalse(s.loading)

    self.big.raises = RuntimeError("link gone")
    self._run(s)
    self.assertTrue(s.loading)


class ContractTest(unittest.TestCase):
  """Whatever modeld touches on the object make_model_state returns.

  Read out of modeld rather than kept by hand: `warmup` was missed once, and
  modeld reads the AttributeError as "big model load failed".
  """

  def test_provides_everything_modeld_touches(self):
    src = Path(BASEDIR) / 'openpilot' / 'selfdrive' / 'modeld' / 'modeld.py'
    text = src.read_text()
    # `model` is the one in the frame loop, `m` the one load_big just built.
    # \b keeps small_model/big_model/sm out of it.
    names = set(re.findall(r'\bmodel\.([a-zA-Z_][a-zA-Z0-9_]*)', text))
    names |= set(re.findall(r'\bm\.([a-zA-Z_][a-zA-Z0-9_]*)', text))
    self.assertIn('warmup', names, "modeld stopped calling warmup; check this test still finds the right names")
    missing = sorted(n for n in names if not hasattr(JoiningModelState, n))
    self.assertEqual(missing, [], f"JoiningModelState is missing {missing}, which modeld calls on it")


if __name__ == '__main__':
  unittest.main()
