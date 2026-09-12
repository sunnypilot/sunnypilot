"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

When the warp JIT is trusted, and when it is not.

The compile needs a GPU and is not exercised here. Staleness is scons' job now,
so what is left is the file on disk being wrong: a TinyJit from another
tinygrad, or one pickled before it captured, loads into something that does not
compute the warp. Each is a raise out of load_warp into the small-model fallback.
"""
import importlib
import pickle
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from openpilot.sunnypilot.accelerators.jetlink import warp_cache

GEOM = (1928, 1208, 512, 256)


class FakeCaptured:
  def __init__(self, names):
    self.expected_names = names


class FakeJit:
  """Just enough of a TinyJit to be pickled and inspected."""

  def __init__(self, names):
    self.captured = FakeCaptured(names) if names is not None else None


class WarpCacheTest(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    patcher = mock.patch.object(warp_cache, 'CACHE_DIR', Path(self.tmp.name))
    patcher.start()
    self.addCleanup(patcher.stop)

  def write(self, geom=GEOM, body=b'pickle'):
    pkl = warp_cache.warp_path(*geom)
    pkl.parent.mkdir(parents=True, exist_ok=True)
    pkl.write_bytes(body)
    return pkl


class TestValidity(WarpCacheTest):
  def test_a_warp_that_is_there_is_used(self):
    self.write()
    self.assertTrue(warp_cache.is_cached(*GEOM))

  def test_nothing_cached_is_a_miss(self):
    self.assertFalse(warp_cache.is_cached(*GEOM))

  def test_a_bare_pickle_needs_no_sidecar(self):
    """What scons writes, and all it writes; asking for a sidecar would reject every warp the build produces."""
    self.write()
    self.assertFalse(warp_cache.warp_path(*GEOM).with_suffix('.json').exists())
    self.assertTrue(warp_cache.is_cached(*GEOM))

  def test_the_cache_is_in_the_tree_where_scons_can_write_it(self):
    """Not under comma_home: on AGNOS that is a tmpfs overlay that loses the
    pickle every boot, and OPENPILOT_PREFIX moves it out from under a replay."""
    with mock.patch.dict('os.environ', {'OPENPILOT_PREFIX': 'replaytest'}):
      importlib.reload(warp_cache)
    self.addCleanup(importlib.reload, warp_cache)
    self.assertEqual(warp_cache.CACHE_DIR.name, 'models')
    self.assertEqual(warp_cache.CACHE_DIR.parent.name, 'jetlink')

  def test_another_camera_does_not_answer_for_this_one(self):
    """A device that changed camera, or a cache copied between devices. The
    warp is baked against the frame geometry, so the wrong one is silently
    wrong rather than an error."""
    self.write(geom=(1344, 760, 512, 256))
    self.assertFalse(warp_cache.is_cached(*GEOM))

  def test_another_model_input_size_does_not_answer_either(self):
    self.write(geom=(1928, 1208, 256, 128))
    self.assertFalse(warp_cache.is_cached(*GEOM))


class TestLoad(WarpCacheTest):
  def test_a_miss_raises_rather_than_returning_none(self):
    """modeld's big-model load is wrapped in the one-way fallback to the small
    model. Raising lands there; returning None would reach the car."""
    with self.assertRaises(RuntimeError):
      warp_cache.load_warp(*GEOM)

  def test_a_pickle_that_will_not_load_raises(self):
    """The incompatible-tinygrad case: unpickling fails and modeld's big-model load falls back."""
    self.write(body=b'not a pickle at all')
    with self.assertRaises(pickle.UnpicklingError):
      warp_cache.load_warp(*GEOM)


class TestLoadValidation(WarpCacheTest):
  """A pickle that loads is not yet a warp that can be trusted."""

  def test_a_good_warp_loads(self):
    self.write(body=pickle.dumps(FakeJit(warp_cache.WARP_INPUT_NAMES)))
    self.assertIsInstance(warp_cache.load_warp(*GEOM), FakeJit)

  def test_the_wrong_call_convention_is_refused_at_load(self):
    # This is the shape of the bug that reached the car: captured positionally,
    # called by keyword, JitError on the first frame of the drive.
    self.write(body=pickle.dumps(FakeJit([0, 1, 2, 3])))
    with self.assertRaises(RuntimeError) as e:
      warp_cache.load_warp(*GEOM)
    self.assertIn('call_warp passes', str(e.exception))

  def test_an_uncaptured_jit_is_refused(self):
    # Pickled before TinyJit captured: loads fine, computes nothing.
    self.write(body=pickle.dumps(FakeJit(None)))
    with self.assertRaises(RuntimeError) as e:
      warp_cache.load_warp(*GEOM)
    self.assertIn('computes nothing', str(e.exception))


class TestEnsure(WarpCacheTest):
  def test_a_cached_warp_is_not_rebuilt(self):
    self.write()
    with mock.patch.object(warp_cache, 'compile_warp') as compile_warp:
      self.assertTrue(warp_cache.ensure(*GEOM))
    compile_warp.assert_not_called()

  def test_a_failed_compile_is_reported_not_raised(self):
    """jetlinkd's loop must survive this: no warp costs the large model, and
    taking the daemon down with it would also drop the USB gadget."""
    with mock.patch.object(warp_cache, 'compile_warp', side_effect=RuntimeError("no gpu")):
      self.assertFalse(warp_cache.ensure(*GEOM))

  def test_a_successful_build_prunes_the_others(self):
    stale = self.write(geom=(1344, 760, 512, 256))
    fresh = warp_cache.warp_path(*GEOM)
    with mock.patch.object(warp_cache, 'compile_warp', side_effect=lambda *a: self.write()):
      self.assertTrue(warp_cache.ensure(*GEOM))
    self.assertTrue(fresh.is_file())
    self.assertFalse(stale.is_file())


class TestGeometry(WarpCacheTest):
  def test_mici_and_tici_want_different_warps(self):
    """The same split accelerators/SConscript makes, so the build produces what
    modeld asks for. If these ever drift, load_warp misses and the drive is
    small-model."""
    with mock.patch("openpilot.common.hardware.HARDWARE.get_device_type", return_value="mici"):
      mici = warp_cache.device_geometry()
    with mock.patch("openpilot.common.hardware.HARDWARE.get_device_type", return_value="tici"):
      tici = warp_cache.device_geometry()
    self.assertNotEqual(mici[:2], tici[:2])
    # both warp to MEDMODEL_INPUT_SIZE, which is what the model input needs
    self.assertEqual(mici[2:], tici[2:])
    self.assertEqual(tici[2:], (512, 256))


class TestInitDevice(unittest.TestCase):
  """prepare() runs this before modeld goes realtime: tinygrad's compile pool
  is otherwise created on the warp's first call, and its handler threads then
  sit at FIFO 54 on the frame loop's core."""

  def setUp(self):
    self.pool = mock.Mock(name='get_worker_pool')
    worker = types.ModuleType('tinygrad.engine.worker')
    worker.get_worker_pool = self.pool
    modules = {'tinygrad': mock.MagicMock(), 'tinygrad.tensor': mock.MagicMock(),
               'tinygrad.engine': mock.MagicMock(), 'tinygrad.engine.worker': worker}
    patcher = mock.patch.dict(sys.modules, modules)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_the_compile_pool_is_created_with_the_device(self):
    warp_cache.init_device()
    self.pool.assert_called_once_with()

  def test_a_pool_that_will_not_start_is_logged_not_raised(self):
    # An older tinygrad without the module, or PARALLEL=0, must not veto the accelerator.
    self.pool.side_effect = RuntimeError('no pool')
    with mock.patch.object(warp_cache.cloudlog, 'exception') as log:
      warp_cache.init_device()
    log.assert_called_once()


class TestCallConvention(unittest.TestCase):
  """The compile and the per-frame call have to name the JIT's inputs the same way.

  TinyJit refuses a call whose names differ from the capture, so a positional
  compile and a keyword call raise JitError on the first frame of a drive.
  """

  def test_call_warp_passes_everything_by_keyword(self):
    seen = {}

    def recorder(*args, **kwargs):
      seen['args'], seen['kwargs'] = args, kwargs
      return 'warped'

    out = warp_cache.call_warp(recorder, 'T', 'BT', 'F', 'BF')
    self.assertEqual(out, 'warped')
    self.assertEqual(seen['args'], (), "positional args make TinyJit capture [0, 1, 2, 3]")
    self.assertEqual(seen['kwargs'], {'tfm': 'T', 'big_tfm': 'BT', 'frame': 'F', 'big_frame': 'BF'})

  def test_both_call_sites_go_through_the_helper(self):
    # a second direct call site would diverge again. Read the sources: importing
    # model_state pulls in tinygrad and msgq, and this runs off the device
    pkg = Path(warp_cache.__file__).parent
    for name in ('warp_cache.py', 'model_state.py'):
      for line in (pkg / name).read_text().splitlines():
        stripped = line.strip()
        if ('warp_jit(' in stripped or 'self.warp(' in stripped) and 'call_warp' not in stripped:
          self.fail(f"{name} calls the warp JIT directly: {stripped}")


if __name__ == "__main__":
  unittest.main()
