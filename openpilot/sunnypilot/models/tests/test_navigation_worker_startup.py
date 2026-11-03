"""Actual worker subprocess checks with the device's checkout/module layout.

Only native platform interfaces and unavailable GPU libraries are fixtures. The
worker, navigation descriptor and BASEDIR sources execute unchanged. No network,
model kernels, GPU build or Popen mock is used.
"""
import importlib.util
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preparation_test_support', SOURCE / 'tests/test_navigation_preparation.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def tracked_source(relative):
  path = SOURCE.parents[2] / relative
  return path.read_text() if path.exists() else subprocess.check_output(
    ['git', '-C', str(SOURCE.parents[2]), 'show', 'HEAD:' + relative], text=True)


class ActualWorkerStartupTests(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.addCleanup(self.temporary.cleanup)
    self.root = Path(self.temporary.name).resolve() / 'checkout'
    self.root.mkdir()
    self.models = Path(self.temporary.name) / 'models'
    self.models.mkdir()
    for relative in ('openpilot/sunnypilot/models/build_navigation_model.py',
                     'openpilot/sunnypilot/models/navigation_model.py',
                     'openpilot/common/basedir.py',
                     'openpilot/sunnypilot/modeld_v2/compile_modeld_v2.py'):
      self.write(relative, tracked_source(relative))
    # Regular packages must win over any editable-install finder in the host
    # interpreter. Namespace-only fixtures can accidentally import the workspace.
    for package in ('openpilot', 'openpilot/common', 'openpilot/sunnypilot', 'openpilot/sunnypilot/models',
                    'openpilot/sunnypilot/modeld_v2', 'tinygrad', 'tinygrad/runtime', 'tinygrad/runtime/support'):
      self.write(package + '/__init__.py', '')
    self.write('openpilot/common/params.py', '''import os
class Params:
  def get_bool(self, key):
    if key != 'IsOffroad': raise KeyError('UnknownKeyName: ' + key)
    return True
  def get(self, key):
    if key != 'ModelManager_DownloadRef': raise KeyError('UnknownKeyName: ' + key)
    return 'local-prepare-rl-navigation-80eedcdd'
''')
    self.write('openpilot/common/hardware/__init__.py', '''import os
if os.environ.get('NAV_STARTUP_FIXTURE') == 'import-error':
  raise ImportError('fixture-worker-platform-import-error')
COMMA_HARDWARE = True
''')
    self.write('openpilot/common/hardware/hw.py', '''import os
class Paths:
  @staticmethod
  def model_root(): return os.environ['NAV_TEST_MODEL_ROOT']
''')
    self.write('tinygrad/runtime/support/c.py', '''class DLL:
  @staticmethod
  def findlib(_name, _paths): return None
''')
    self.write('sitecustomize.py', '''import os, time
if os.environ.get('NAV_STARTUP_FIXTURE') == 'stall-before-worker':
  time.sleep(30)
''')
    # The production launcher exports checkout-root PYTHONPATH before starting manager.
    self.environment = {'PYTHONPATH': str(self.root), 'NAV_TEST_MODEL_ROOT': str(self.models),
                        'NAV_STARTUP_FIXTURE': 'normal'}
    self.basedir = runpy.run_path(str(self.root / 'openpilot/common/basedir.py'))['BASEDIR']
    self.assertEqual(Path(self.basedir), self.root)
    self.ns = support.manager_namespace()
    self.manager = self.ns['ModelManagerSP'].__new__(self.ns['ModelManagerSP'])
    self.manager.params = support.Params()
    self.manager.chestnut_present = True
    self.manager.active_bundle = 'unchanged-active-model'
    self.manager.source_models = {}
    self.manager.model_fetcher = NS(get_bundles_for_source=Mock(return_value=[]))
    self.manager._report_status = Mock()
    self.ns['Paths'].model_root = lambda: str(self.models)
    self.ns['installed_bundle'].return_value = None
    self.enterContext(patch.dict(sys.modules, {'openpilot.common.basedir': NS(BASEDIR=self.basedir)}))

  def write(self, relative, text):
    path = self.root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

  def run_actual_worker(self, mode='normal'):
    self.environment['NAV_STARTUP_FIXTURE'] = mode
    with patch.dict(os.environ, self.environment):
      self.manager._prepare_navigation()
    self.assertEqual(self.manager.active_bundle, 'unchanged-active-model')
    self.assertEqual(self.manager.selected_bundle.status, 4)

  def test_actual_layout_imports_and_first_worker_status_reach_prerequisite_check(self):
    self.run_actual_worker()
    logs = '\n'.join(path.read_text() for path in self.models.glob('*.log'))
    self.assertIn('libusb', self.manager.selected_bundle.displayName, logs[-4096:])
    self.assertNotIn('compiler is missing', self.manager.selected_bundle.displayName)
    self.assertFalse((self.models / support.nav.MANIFEST_NAME).exists())

  def test_before_status_import_error_is_failed_and_persisted_in_worker_log(self):
    self.run_actual_worker('import-error')
    logs = '\n'.join(path.read_text() for path in self.models.glob('*.log'))
    self.assertIn('fixture-worker-platform-import-error', logs)
    self.assertNotIn('Checking navigation model preparation requirements', self.manager.selected_bundle.displayName)

  def test_no_first_status_has_bounded_timeout_and_kills_worker(self):
    self.ns['NAV_PREPARE_STARTUP_TIMEOUT'] = .3
    started = time.monotonic()
    self.run_actual_worker('stall-before-worker')
    self.assertLess(time.monotonic() - started, 3)
    self.assertIn('start', self.manager.selected_bundle.displayName.lower())
    self.assertFalse((self.models / support.nav.MANIFEST_NAME).exists())


if __name__ == '__main__':
  unittest.main()
