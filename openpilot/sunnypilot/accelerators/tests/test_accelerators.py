"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The answers core openpilot gets from the accelerators module.

modeld, manager, hardwared and the UI all reach the Jetson through this
module, so what is pinned here is selection: what a device with the feature
off, on but not provisioned, and ready gets told, and that a missing package
or a backend that hangs costs the large model and nothing else. No hardware.
"""
import sys
import threading
import time
import unittest
from types import SimpleNamespace
from unittest import mock

from openpilot.sunnypilot import accelerators
from openpilot.sunnypilot.accelerators import Daemon
from openpilot.sunnypilot.accelerators.jetlink import backend, helpers


class SelectionTest(unittest.TestCase):
  """ready() is params only, and every answer follows from three params."""

  def configure(self, enabled=None, model=None, ready_sha=None, spec_sha=None, gadget_error=None):
    params = {helpers.P_ENABLED: enabled, helpers.P_MODEL: model, helpers.P_READY: ready_sha}
    for p in (mock.patch.object(helpers, '_get', side_effect=lambda k, d=None: params.get(k, d)),
              mock.patch.object(helpers, 'gadget_error', return_value=gadget_error),
              mock.patch.object(helpers, 'host_attached', return_value=False),
              mock.patch.object(helpers, 'dormant', return_value=False),
              mock.patch.object(helpers, 'selected_model',
                                return_value={'name': model, 'oid': 'a' * 64} if model else None),
              mock.patch.object(backend.spec_cache, 'load',
                                return_value=SimpleNamespace(sha256=spec_sha) if spec_sha else None)):
      p.start()
      self.addCleanup(p.stop)
    helpers._last_configured = 0.0

  def test_disabled_by_absence(self):
    self.configure(enabled=None, model='m', ready_sha='a' * 64, spec_sha='a' * 64)
    self.assertFalse(accelerators.present())
    self.assertFalse(accelerators.ready())
    self.assertIsNone(accelerators.unavailable_reason())
    self.assertFalse(accelerators.uses_stock_runner())

  def test_disabled_explicitly(self):
    self.configure(enabled=False, model='m', ready_sha='a' * 64, spec_sha='a' * 64, gadget_error='no gadget')
    self.assertFalse(accelerators.present())
    self.assertFalse(accelerators.ready())
    # A device with the feature off is never nagged about its kernel.
    self.assertIsNone(accelerators.unavailable_reason())
    self.assertFalse(accelerators.uses_stock_runner())

  def test_enabled_but_not_provisioned(self):
    self.configure(enabled=True, model='m', ready_sha=None, spec_sha=None)
    self.assertFalse(accelerators.ready())
    self.assertIsNone(accelerators.unavailable_reason())
    self.assertIsNone(accelerators.active_model_name())

  def test_enabled_with_a_broken_gadget_says_why(self):
    self.configure(enabled=True, model='m', ready_sha='a' * 64, spec_sha='a' * 64, gadget_error='no gadget')
    self.assertFalse(accelerators.ready())
    self.assertEqual(accelerators.unavailable_reason(), 'no gadget')

  def test_ready(self):
    self.configure(enabled=True, model='m', ready_sha='a' * 64, spec_sha='a' * 64)
    self.assertTrue(accelerators.ready())
    self.assertIsNone(accelerators.unavailable_reason())
    self.assertTrue(accelerators.uses_stock_runner())

  def test_an_old_engine_is_not_the_new_selection(self):
    self.configure(enabled=True, model='m', ready_sha='b' * 64, spec_sha='b' * 64)
    self.assertFalse(accelerators.ready())

  def test_stock_runner_is_the_toggle_alone(self):
    # configuration only, never link state or ready(): a late boot cannot move
    # manager between modelds mid-drive. The model defaults through
    # selected_model(), so it is not part of it either
    self.configure(enabled=True, model=None)
    self.assertTrue(accelerators.uses_stock_runner())
    self.configure(enabled=True, model='m')
    with mock.patch.object(helpers, 'link_configured', return_value=False):
      self.assertTrue(accelerators.uses_stock_runner())
    self.configure(enabled=None, model='m')
    with mock.patch.object(helpers, 'link_configured', return_value=True):
      self.assertFalse(accelerators.uses_stock_runner())

  def test_present_is_usb_independent_while_dormant(self):
    self.configure(enabled=True, model='m')
    with mock.patch.object(helpers, 'dormant', return_value=True), \
         mock.patch.object(helpers, 'CC_ORIENTATION', mock.Mock(read_text=lambda: '1')):
      self.assertTrue(accelerators.present())


class MissingPackageTest(unittest.TestCase):
  """The jetlink client package can be absent; nothing may raise for it."""

  def hide_package(self):
    p = mock.patch.dict(sys.modules, {'jetlink': None, 'jetlink.client': None})
    p.start()
    self.addCleanup(p.stop)
    backend._missing_reported = False

  def test_prepare_answers_false(self):
    self.hide_package()
    with mock.patch.object(backend.cloudlog, 'warning') as warn:
      self.assertFalse(accelerators.prepare())
      self.assertFalse(accelerators.prepare())
    # Once, not per poll.
    self.assertEqual(warn.call_count, 1)

  def test_make_model_state_answers_none(self):
    self.hide_package()
    self.assertIsNone(accelerators.make_model_state(1928, 1208, object()))

  def test_the_cheap_questions_still_import_and_answer(self):
    self.hide_package()
    with mock.patch.object(helpers, '_get', return_value=None):
      self.assertFalse(accelerators.ready())
      self.assertFalse(accelerators.uses_stock_runner())


class DaemonTest(unittest.TestCase):
  def test_jetlinkd_is_offered_and_gated_on_enabled(self):
    (d,) = accelerators.daemons()
    self.assertIsInstance(d, Daemon)
    self.assertEqual(d.name, 'jetlinkd')
    __import__(d.module)
    with mock.patch.object(helpers, 'enabled', return_value=False):
      self.assertFalse(d.should_run(False, None, None))
    with mock.patch.object(helpers, 'enabled', return_value=True):
      self.assertTrue(d.should_run(False, None, None))


class TestProgress(unittest.TestCase):
  def test_a_missing_param_is_no_progress(self):
    with mock.patch.object(accelerators, 'Params') as params:
      params.return_value.get.return_value = None
      self.assertIsNone(accelerators.progress())

  def test_a_dict_comes_through(self):
    payload = {'stage': 'build', 'frac': 0.5, 'msg': ''}
    with mock.patch.object(accelerators, 'Params') as params:
      params.return_value.get.return_value = payload
      self.assertEqual(accelerators.progress(), payload)

  def test_a_non_dict_is_ignored(self):
    with mock.patch.object(accelerators, 'Params') as params:
      params.return_value.get.return_value = "build 50%"
      self.assertIsNone(accelerators.progress())

  def test_an_unknown_key_does_not_take_down_the_ui(self):
    # A params library older than this key raises rather than returning None.
    with mock.patch.object(accelerators, 'Params') as params:
      params.return_value.get.side_effect = RuntimeError("UnknownKeyName")
      self.assertIsNone(accelerators.progress())

  def test_reporting_never_raises(self):
    # Called from except handlers in the daemons.
    with mock.patch.object(accelerators, 'Params') as params:
      params.return_value.put.side_effect = RuntimeError("params gone")
      accelerators.report_progress('build', 0.5)
      params.return_value.remove.side_effect = RuntimeError("params gone")
      accelerators.clear_progress()


class TestShutdown(unittest.TestCase):
  def test_disabled_costs_one_param_read_and_nothing_else(self):
    with mock.patch.object(helpers, 'enabled', return_value=False), \
         mock.patch.object(backend, 'shutdown') as request:
      accelerators.shutdown('car battery')
    request.assert_not_called()

  def test_the_request_is_forwarded_with_the_bound(self):
    with mock.patch.object(helpers, 'enabled', return_value=True), \
         mock.patch.object(backend, 'shutdown') as request:
      accelerators.shutdown('car battery', timeout=3.0)
    request.assert_called_once_with('car battery', 3.0)

  def test_a_backend_that_hangs_cannot_hold_hardwared(self):
    release = threading.Event()
    self.addCleanup(release.set)
    with mock.patch.object(helpers, 'enabled', return_value=True), \
         mock.patch.object(backend, 'shutdown', side_effect=lambda *a: release.wait(30)), \
         mock.patch.object(accelerators.cloudlog, 'warning') as warn:
      t0 = time.monotonic()
      accelerators.shutdown('car battery', timeout=0.2)
      self.assertLess(time.monotonic() - t0, 2.0)
    warn.assert_called_once()

  def test_a_backend_that_raises_is_logged_not_propagated(self):
    with mock.patch.object(helpers, 'enabled', return_value=True), \
         mock.patch.object(backend, 'shutdown', side_effect=RuntimeError('no')), \
         mock.patch.object(accelerators.cloudlog, 'exception') as log:
      accelerators.shutdown('car battery', timeout=1.0)
    log.assert_called_once()


if __name__ == '__main__':
  unittest.main()
