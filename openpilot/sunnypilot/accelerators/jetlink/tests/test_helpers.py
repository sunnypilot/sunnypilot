"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openpilot.sunnypilot.accelerators.jetlink import helpers


class TestGadgetStatus(unittest.TestCase):
  """The gadget is set up at boot, by root, from launch_chffrplus.sh. This file
  is the only way the reason for a failure reaches anything a user can see."""

  def setUp(self):
    self.tmp = tempfile.mkdtemp()
    self.status = Path(self.tmp) / 'jetlink-gadget'
    patcher = mock.patch.object(helpers, 'GADGET_STATUS', self.status)
    self.addCleanup(patcher.stop)
    patcher.start()

  def test_missing_file_is_not_an_error(self):
    # A build that never ran the setup at all reads the same as not installed.
    assert helpers.gadget_error() is None

  def test_ok_is_not_an_error(self):
    self.status.write_text('ok\n')
    assert helpers.gadget_error() is None

  def test_empty_is_not_an_error(self):
    self.status.write_text('')
    assert helpers.gadget_error() is None

  def test_reason_is_unwrapped(self):
    self.status.write_text('error: kernel has no USB gadget support\n')
    assert helpers.gadget_error() == 'kernel has no USB gadget support'

  def test_bare_reason_survives(self):
    self.status.write_text('something went wrong')
    assert helpers.gadget_error() == 'something went wrong'

  def test_unreadable_status_is_not_an_error(self):
    # Path.exists() and read_text() raise rather than return on a root-only
    # path; an availability check must never take a process down over one.
    with mock.patch.object(Path, 'read_text', side_effect=PermissionError):
      assert helpers.gadget_error() is None


class TestGadgetAlert(unittest.TestCase):
  """Only complain to someone who asked for the link. With it off, a device
  that cannot present the gadget should simply not offer the feature."""

  def alert_with(self, enabled: bool, reason: str | None):
    with mock.patch.object(helpers, 'enabled', return_value=enabled), \
         mock.patch.object(helpers, 'gadget_error', return_value=reason):
      return helpers.gadget_alert()

  def test_silent_when_off(self):
    assert self.alert_with(False, 'kernel has no USB gadget support') is None

  def test_speaks_up_when_switched_on(self):
    assert self.alert_with(True, 'kernel has no USB gadget support') == 'kernel has no USB gadget support'

  def test_nothing_to_say_when_healthy(self):
    assert self.alert_with(True, None) is None


class TestDormant(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    for name in ('DORMANT', 'SHUTDOWN_REQUEST'):
      patcher = mock.patch.object(helpers, name, self.tmp / name.lower())
      self.addCleanup(patcher.stop)
      patcher.start()

  def test_marker_from_a_live_process_counts(self):
    helpers.set_dormant(True)
    assert helpers.dormant()
    helpers.set_dormant(False)
    assert not helpers.dormant()

  def test_marker_from_a_dead_process_is_a_leftover(self):
    helpers.DORMANT.write_text('4194304')  # above pid_max
    assert not helpers.dormant()

  def test_garbage_is_not_dormant(self):
    helpers.DORMANT.write_text('not a pid')
    assert not helpers.dormant()

  def test_dormant_counts_as_present_without_a_host(self):
    with mock.patch.object(helpers, 'link_endpoint', return_value=None), \
         mock.patch.object(helpers, 'host_attached', return_value=False), \
         mock.patch.object(helpers, 'CC_ORIENTATION', self.tmp / 'cc'):
      (self.tmp / 'cc').write_text('1')
      helpers._last_configured = 0.0
      assert not helpers.gadget_present()
      helpers.set_dormant(True)
      assert helpers.gadget_present()
      (self.tmp / 'cc').write_text('0')
      assert not helpers.gadget_present()

  def test_shutdown_request_round_trip(self):
    assert helpers.pending_shutdown() is None
    assert helpers.request_shutdown('car battery')
    assert helpers.pending_shutdown() == 'car battery'
    helpers.finish_shutdown()
    assert helpers.pending_shutdown() is None

  def test_await_shutdown_gives_up_and_cleans_up(self):
    helpers.request_shutdown('car battery')
    assert not helpers.await_shutdown(0.3)
    assert helpers.pending_shutdown() is None

  def test_await_shutdown_returns_when_taken(self):
    helpers.request_shutdown('car battery')
    helpers.finish_shutdown()
    assert helpers.await_shutdown(0.3)


class TestUnchunkedSuffix(unittest.TestCase):
  def test_suffix_is_distinct_from_openpilots(self):
    """openpilot's own '.unchunked' files are deleted by an atexit handler.
    Ours must not collide with that or a provision loses its model mid-upload."""
    assert helpers.UNCHUNKED_SUFFIX != '.unchunked'
    assert not helpers.UNCHUNKED_SUFFIX.endswith('.unchunked')


class TestActiveModelPath(unittest.TestCase):
  def setUp(self):
    self.root = tempfile.mkdtemp()
    patcher = mock.patch('openpilot.sunnypilot.accelerators.jetlink.helpers.Paths')
    self.addCleanup(patcher.stop)
    patcher.start().model_root.return_value = self.root

  def bundle_with(self, *file_names):
    models = []
    for name in file_names:
      artifact = mock.Mock()
      artifact.fileName = name
      models.append(mock.Mock(artifact=artifact))
    return mock.Mock(models=models)

  def test_no_bundle_falls_through_to_the_pinned_model(self):
    # no chestnut bundle ships an ONNX, so what runs is the model openpilot
    # pins; None here would leave a provisioned device on the small model
    pinned = Path(self.root) / helpers.BIG_MODEL_NAME
    with mock.patch.object(helpers, 'active_bundle', return_value=None), \
         mock.patch.object(helpers, 'shipped_model_path', return_value=pinned):
      assert helpers.active_model_path() == pinned

  def test_no_bundle_and_nothing_pinned_is_no_path(self):
    with mock.patch.object(helpers, 'active_bundle', return_value=None), \
         mock.patch.object(helpers, 'shipped_model_path', return_value=None):
      assert helpers.active_model_path() is None

  def test_finds_a_plain_onnx(self):
    onnx = Path(self.root) / 'big.onnx'
    onnx.write_bytes(b'\0' * 2_000_000)
    with mock.patch.object(helpers, 'active_bundle', return_value=self.bundle_with('big.onnx')):
      assert helpers.active_model_path() == onnx

  def test_ignores_a_truncated_download(self):
    (Path(self.root) / 'big.onnx').write_bytes(b'\0' * 16)
    with mock.patch.object(helpers, 'active_bundle', return_value=self.bundle_with('big.onnx')), \
         mock.patch('openpilot.selfdrive.modeld.helpers.MODELS_DIR', Path(self.root)):
      assert helpers.active_model_path() is None

  def test_ignores_non_onnx_artifacts(self):
    (Path(self.root) / 'small.pkl').write_bytes(b'\0' * 2_000_000)
    with mock.patch.object(helpers, 'active_bundle', return_value=self.bundle_with('small.pkl')), \
         mock.patch('openpilot.selfdrive.modeld.helpers.MODELS_DIR', Path(self.root)):
      assert helpers.active_model_path() is None

  def test_cleanup_keeps_the_one_in_use(self):
    keep = Path(self.root) / f'a.onnx{helpers.UNCHUNKED_SUFFIX}'
    drop = Path(self.root) / f'b.onnx{helpers.UNCHUNKED_SUFFIX}'
    keep.write_bytes(b'k')
    drop.write_bytes(b'd')
    helpers.cleanup_unchunked(keep=keep)
    assert keep.is_file()
    assert not drop.exists()


if __name__ == '__main__':
  unittest.main()


class TestModelIndex(unittest.TestCase):
  """comma overwrites one ONNX file, so every earlier big model exists only as a
  git-lfs object no manifest lists. The index is how we keep hold of them."""

  def test_the_shipped_index_parses(self):
    models = helpers.model_index()
    assert models, "no models in models.json"

  def test_every_entry_is_complete(self):
    for m in helpers.model_index():
      for field in ('name', 'oid', 'size', 'commit', 'date'):
        assert m.get(field), f"{m.get('name')!r} is missing {field}"
      assert len(m['oid']) == 64, f"{m['name']}: oid is not a sha256"
      assert m['size'] > 1_000_000, f"{m['name']}: implausible size"

  def test_names_and_oids_are_unique(self):
    models = helpers.model_index()
    assert len({m['name'] for m in models}) == len(models)
    assert len({m['oid'] for m in models}) == len(models)

  def test_exactly_one_default(self):
    # Two defaults, or none, and selected_model() silently picks by list order.
    assert sum(1 for m in helpers.model_index() if m.get('default')) == 1

  def test_file_names_do_not_collide(self):
    names = [helpers.model_file_name(m) for m in helpers.model_index()]
    assert len(set(names)) == len(names)


class TestSelectedModel(unittest.TestCase):
  INDEX = [
    {'name': 'Alpha', 'oid': 'a' * 64, 'size': 10, 'commit': 'c1', 'date': 'd'},
    {'name': 'Beta', 'oid': 'b' * 64, 'size': 20, 'commit': 'c2', 'date': 'd', 'default': True},
  ]

  def select_with(self, param):
    with mock.patch.object(helpers, 'model_index', return_value=self.INDEX), \
         mock.patch.object(helpers, '_get', return_value=param):
      return helpers.selected_model()

  def test_unset_takes_the_default(self):
    assert self.select_with(None)['name'] == 'Beta'

  def test_a_name_selects_it(self):
    assert self.select_with('Alpha')['name'] == 'Alpha'

  def test_an_unknown_name_falls_back(self):
    # The index can shrink under a param that outlived it; leaving the device
    # with no model at all would be worse than quietly using the default.
    assert self.select_with('Gone')['name'] == 'Beta'

  def test_an_empty_index_is_no_model(self):
    with mock.patch.object(helpers, 'model_index', return_value=[]):
      assert helpers.selected_model() is None


class TestSelectedModelReadiness(unittest.TestCase):
  def test_old_cached_engine_is_not_the_new_selection(self):
    from types import SimpleNamespace
    from openpilot.sunnypilot.accelerators.jetlink import backend

    with mock.patch.object(helpers, 'enabled', return_value=True), \
         mock.patch.object(helpers, 'engine_ready_for', return_value=True), \
         mock.patch.object(backend.spec_cache, 'load', return_value=SimpleNamespace(sha256='a' * 64)), \
         mock.patch.object(helpers, 'selected_model', return_value={'oid': 'b' * 64}) as selected:
      self.assertFalse(backend.ready())
      client = mock.Mock()
      with self.assertRaisesRegex(RuntimeError, 'not been provisioned'):
        backend._open_link(client)
      client.close.assert_called_once()
      selected.return_value = {'oid': 'a' * 64}
      self.assertTrue(backend.ready())


class TestShippedModelPath(unittest.TestCase):
  """A file counts only when it is the model we mean, at the size we expect.
  Models live one file per oid so switching back does not re-download."""

  MODEL = {'name': 'Alpha', 'oid': 'a' * 64, 'size': 4096, 'commit': 'c', 'date': 'd'}

  def setUp(self):
    self.root = tempfile.mkdtemp()
    paths = mock.patch('openpilot.sunnypilot.accelerators.jetlink.helpers.Paths')
    self.addCleanup(paths.stop)
    paths.start().model_root.return_value = self.root
    chosen = mock.patch.object(helpers, 'selected_model', return_value=self.MODEL)
    self.addCleanup(chosen.stop)
    chosen.start()

  def fetched(self, size: int) -> Path:
    path = Path(self.root) / helpers.model_file_name(self.MODEL)
    path.write_bytes(b'\0' * size)
    return path

  def test_nothing_fetched_yet(self):
    assert helpers.shipped_model_path() is None

  def test_the_chosen_model_is_accepted(self):
    fetched = self.fetched(4096)
    assert helpers.shipped_model_path() == fetched

  def test_a_truncated_download_is_rejected(self):
    # Half a model is exactly what must not reach TensorRT.
    self.fetched(2048)
    assert helpers.shipped_model_path() is None

  def test_no_model_chosen_is_no_path(self):
    with mock.patch.object(helpers, 'selected_model', return_value=None):
      assert helpers.shipped_model_path() is None
