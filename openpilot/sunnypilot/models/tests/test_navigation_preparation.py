"""Preparation lifecycle tests; no GPU kernels or downloaded model code execute."""
import ast
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

import requests

SOURCE = Path(__file__).resolve().parents[1]


def load(name, path):
  spec = importlib.util.spec_from_file_location(name, path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


nav = load('preparation_nav', SOURCE / 'navigation_model.py')
with patch.dict(sys.modules, {'openpilot.sunnypilot.models.navigation_model': nav}):
  builder = load('preparation_builder', SOURCE / 'build_navigation_model.py')


class Params:
  def __init__(self):
    self.onroad, self.ref = False, nav.BUILD_REF.encode()
  def get_bool(self, _key):
    return self.onroad
  def get(self, _key):
    return self.ref


class Response:
  def __init__(self, chunks, length=None):
    self.chunks = chunks
    self.headers = {} if length is None else {'Content-Length': str(length)}
  def __enter__(self):
    return self
  def __exit__(self, *_args):
    pass
  def raise_for_status(self):
    pass
  def iter_content(self, **_kwargs):
    yield from self.chunks


class SourceDownloadTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.path = Path(self.temp.name) / 'source.onnx'
    self.body = b'official-source-stand-in'
    self.report = Mock()
    self.enterContext(patch.object(builder, 'SOURCE_ONNX_BYTES', len(self.body)))
    self.enterContext(patch.object(builder, 'SOURCE_ONNX_SHA256', hashlib.sha256(self.body).hexdigest()))

  def fetch(self, response, check=lambda: None):
    with patch.object(builder.requests, 'get', return_value=response) as get:
      builder.download_source(self.path, check, self.report)
      return get

  def test_exact_stream_and_cached_retry_skip_network(self):
    self.fetch(Response([self.body[:5], self.body[5:]], len(self.body)))
    self.assertEqual(self.path.read_bytes(), self.body)
    self.assertFalse(self.path.with_suffix('.partial').exists())
    with patch.object(builder.requests, 'get', side_effect=AssertionError('cached source must skip network')):
      builder.download_source(self.path, lambda: None, self.report)

  def test_wrong_size_short_oversized_and_corrupt_fail_closed(self):
    for response in (Response([self.body], 1), Response([self.body[:-1]]), Response([self.body + b'x']), Response([b'x' * len(self.body)])):
      with self.subTest(response=response), self.assertRaises(RuntimeError):
        self.fetch(response)
      self.assertFalse(self.path.exists())
      self.assertFalse(self.path.with_suffix('.partial').exists())

  def test_cancellation_during_stream_removes_partial(self):
    checks = iter([False, False, True])
    def check():
      if next(checks, True):
        raise builder.PreparationCancelled('canceled')
    with self.assertRaises(builder.PreparationCancelled):
      self.fetch(Response([self.body[:5], self.body[5:]]), check)
    self.assertFalse(self.path.exists())
    self.assertFalse(self.path.with_suffix('.partial').exists())

  def test_queued_cancel_and_onroad_both_abort(self):
    params = Params()
    builder.check_allowed(params, True)
    params.ref = None
    with self.assertRaises(builder.PreparationCancelled):
      builder.check_allowed(params, True)
    params.ref, params.onroad = b'queued-other-model', True
    with self.assertRaises(builder.PreparationCancelled):
      builder.check_allowed(params, True)


class BuildLifecycleTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)
    self.params = Params()
    self.report = Mock()
    self.compiler = self.root / 'compiler.py'
    self.compiler.write_text('reviewed source')
    self.enterContext(patch.object(builder, 'preflight', return_value=self.compiler))
    self.enterContext(patch.object(builder.shutil, 'disk_usage', return_value=NS(free=8 * 1024 ** 3)))
    self.enterContext(patch.object(builder, 'download_source'))

  def process(self, command, **_kwargs):
    Path(command[3]).write_bytes(b'target-plain-model')
    returncode = getattr(self, 'returncode', 0)
    process = Mock(returncode=returncode)
    process.poll.return_value = returncode
    process.__enter__ = Mock(return_value=process)
    process.__exit__ = Mock(return_value=False)
    return process

  def run_build(self, validator=None):
    validate = validator or (lambda path: {'valid': True} if (Path(path) / nav.MANIFEST_NAME).exists() else None)
    with patch.object(builder, 'installed_bundle', side_effect=validate), patch.object(builder.subprocess, 'Popen', side_effect=self.process):
      builder.prepare(self.root, self.root, self.params, True, queued=True, report=self.report)

  def test_success_registers_validated_artifact_without_selecting_model(self):
    self.run_build()
    descriptor = json.loads((self.root / nav.MANIFEST_NAME).read_text())
    artifact = self.root / descriptor['artifact']['fileName']
    self.assertEqual(nav.file_sha256(artifact), descriptor['artifact']['sha256'])
    self.assertEqual(descriptor['sourceOnnxSha256'], nav.SOURCE_ONNX_SHA256)
    self.assertEqual(self.params.ref, nav.BUILD_REF.encode())
    self.assertEqual(self.report.call_args.args[0], 'ready')

  def test_compile_failure_or_bad_protocol_never_registers(self):
    self.returncode = 1
    with self.assertRaises(RuntimeError):
      self.run_build()
    self.assertFalse((self.root / nav.MANIFEST_NAME).exists())
    self.returncode = 0
    with self.assertRaises(RuntimeError):
      self.run_build(lambda _path: None)
    self.assertFalse((self.root / nav.MANIFEST_NAME).exists())

  def test_onroad_before_publication_never_registers(self):
    def process(*args, **kwargs):
      result = self.process(*args, **kwargs)
      self.params.onroad = True
      return result
    with patch.object(builder, 'installed_bundle', return_value=None), patch.object(builder.subprocess, 'Popen', side_effect=process):
      with self.assertRaises(builder.PreparationCancelled):
        builder.prepare(self.root, self.root, self.params, True, queued=True, report=self.report)
    self.assertFalse((self.root / nav.MANIFEST_NAME).exists())

  def test_low_storage_does_not_download_or_compile(self):
    with patch.object(builder.shutil, 'disk_usage', return_value=NS(free=1)), patch.object(builder.subprocess, 'Popen') as process:
      with self.assertRaisesRegex(RuntimeError, '4 GiB'):
        builder.prepare(self.root, self.root, self.params, True)
      builder.download_source.assert_not_called()
      process.assert_not_called()


class PrerequisiteTests(unittest.TestCase):
  def test_hardware_compiler_usb_and_llvm_fail_before_download(self):
    with tempfile.TemporaryDirectory() as directory:
      basedir = Path(directory)
      compiler = basedir / 'openpilot/sunnypilot/modeld_v2/compile_modeld_v2.py'
      compiler.parent.mkdir(parents=True)
      compiler.write_text('reviewed compiler stand-in')
      with self.assertRaisesRegex(RuntimeError, 'comma device'):
        builder.preflight(basedir, False)
      with self.assertRaisesRegex(RuntimeError, 'reviewed source'):
        builder.preflight(basedir, True)
      dll = NS(findlib=Mock(return_value=None))
      with patch.object(builder, 'file_sha256', return_value=builder.COMPILER_SHA256), \
           patch.dict(sys.modules, {'tinygrad.runtime.support.c': NS(DLL=dll)}):
        with self.assertRaisesRegex(RuntimeError, 'libusb'):
          builder.preflight(basedir, True)
        dll.findlib.side_effect = ['usb.so', None]
        with patch.object(builder.ctypes, 'CDLL'), self.assertRaisesRegex(RuntimeError, 'LLVM 18'):
          builder.preflight(basedir, True)

  def test_runtime_loader_and_actual_llvm_version_are_used(self):
    with tempfile.TemporaryDirectory() as directory:
      basedir = Path(directory)
      compiler = basedir / 'openpilot/sunnypilot/modeld_v2/compile_modeld_v2.py'
      compiler.parent.mkdir(parents=True)
      compiler.touch()
      dll = NS(findlib=Mock(side_effect=['runtime-usb-path', 'runtime-unversioned-llvm-path']))
      def version(major, _minor, _patch):
        major._obj.value = 18
      llvm = NS(LLVMGetVersion=version, LLVMInitializeAMDGPUTarget=lambda: None)
      with patch.object(builder, 'file_sha256', return_value=builder.COMPILER_SHA256), \
           patch.dict(sys.modules, {'tinygrad.runtime.support.c': NS(DLL=dll)}), \
           patch.object(builder.ctypes, 'CDLL', side_effect=[NS(), llvm]):
        self.assertEqual(builder.preflight(basedir, True), compiler)
      self.assertEqual(dll.findlib.call_args_list[0].args, ('libusb', ['usb-1.0']))


class Progress:
  def __init__(self):
    self.status, self.progress, self.speed, self.eta, self.canceling = 0, 0, 0, 0, False


class Bundle:
  @property
  def models(self):
    return self._models
  @models.setter
  def models(self, values):
    self._models = [NS(artifact=NS(fileName=value['artifact']['fileName'], downloadProgress=Progress())) for value in values]


def manager_namespace():
  # Actual manager methods, with platform transport imports stubbed for Mac.
  tree = ast.parse((SOURCE / 'manager.py').read_text())
  tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom)) and not isinstance(node, ast.If)]
  status = NS(downloading=1, downloaded=2, cached=3, failed=4, verifying=5)
  namespace = {'__name__': 'manager_under_test', 'asyncio': asyncio, 'json': json, 'os': os, 'Path': Path,
               're': __import__('re'), 'signal': signal, 'subprocess': subprocess, 'sys': sys, 'tempfile': tempfile,
               'time': time, 'threading': __import__('threading'), 'requests': requests,
               'custom': NS(ModelManagerSP=NS(ModelBundle=Bundle, DownloadStatus=status)),
               'BUILD_REF': nav.BUILD_REF, 'MANIFEST_NAME': nav.MANIFEST_NAME, 'installed_bundle': Mock(return_value={'valid': True}),
               'Paths': NS(model_root=lambda: ''), 'cloudlog': Mock()}
  namespace['ModelFetcher'] = NS(active_source=lambda _present: 'chestnut')
  exec(compile(tree, str(SOURCE / 'manager.py'), 'exec'), namespace)
  return namespace


class ManagerPreparationTests(unittest.TestCase):
  def setUp(self):
    self.ns = manager_namespace()
    self.manager = self.ns['ModelManagerSP'].__new__(self.ns['ModelManagerSP'])
    self.manager.params = Params()
    self.manager.chestnut_present = True
    self.manager.active_bundle = 'unchanged-active-model'
    self.manager.source_models = {}
    self.manager.model_fetcher = NS(get_bundles_for_source=Mock(return_value=['new-selectable-local-row']))
    self.manager._report_status = Mock()
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.ns['Paths'].model_root = lambda: self.temp.name
    self.enterContext(patch.dict(sys.modules, {'openpilot.common.basedir': NS(BASEDIR=self.temp.name)}))

  def test_missing_hardware_or_onroad_is_visible_failure_without_worker(self):
    for chestnut, onroad in ((False, False), (True, True)):
      self.manager.chestnut_present, self.manager.params.onroad = chestnut, onroad
      with patch.object(subprocess, 'Popen') as process:
        self.manager._prepare_navigation()
        process.assert_not_called()
      self.assertEqual(self.manager.selected_bundle.status, 4)
      self.assertIn('Park', self.manager.selected_bundle.displayName)

  def test_success_remains_explicit_selection_and_stops_entire_job_group(self):
    process = Mock(pid=99999999, returncode=0)
    process.poll.return_value = 0
    with patch.object(subprocess, 'Popen', return_value=process) as start, patch.object(os, 'killpg') as kill:
      self.manager._prepare_navigation()
    self.assertTrue(start.call_args.kwargs['start_new_session'])
    self.assertEqual(self.manager.active_bundle, 'unchanged-active-model')
    self.assertEqual(self.manager.selected_bundle.status, 2)
    self.assertEqual(self.manager.available_models, ['new-selectable-local-row'])
    self.assertIn('select', self.manager.selected_bundle.displayName)
    kill.assert_any_call(process.pid, signal.SIGTERM)
    kill.assert_any_call(process.pid, signal.SIGKILL)

  def test_canceled_job_is_failed_and_kills_group(self):
    process = Mock(pid=99999999, returncode=0)
    process.poll.return_value = None
    self.manager.params.ref = None
    with patch.object(subprocess, 'Popen', return_value=process), patch.object(os, 'killpg') as kill:
      self.manager._prepare_navigation()
    self.assertEqual(self.manager.selected_bundle.status, 4)
    self.assertIn('canceled', self.manager.selected_bundle.displayName)
    self.assertTrue(kill.called)

  def test_special_request_dispatches_without_normal_download_or_auto_activation(self):
    self.manager.params = Mock()
    self.manager.params.get.side_effect = [nav.BUILD_REF.encode(), nav.BUILD_REF.encode(), None]
    self.manager._prepare_navigation = Mock()
    self.manager.download = Mock()
    self.manager._download_ref = None
    self.manager._process_download_requests()
    self.manager._prepare_navigation.assert_called_once()
    self.manager.download.assert_not_called()
    self.manager.params.put.assert_not_called()


class NativeSelectorTests(unittest.TestCase):
  def test_real_parser_and_verified_local_file_activation_use_no_network(self):
    try:
      if schema := os.environ.get('NAVIGATION_TEST_SCHEMA'):
        import capnp
        custom = capnp.load(schema, imports=[os.environ['NAVIGATION_TEST_INCLUDE']])
      else:
        from openpilot.cereal import custom
    except (ImportError, OSError) as error:
      self.skipTest(f'Native cereal unavailable: {error}')
    fixture = load('navigation_metadata_fixture', SOURCE / 'tests/test_navigation_model.py')
    tree = ast.parse((SOURCE / 'fetcher.py').read_text())
    parser_namespace = {'custom': custom, 'is_bundle_version_compatible': lambda _value: True}
    parser = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ModelParser')
    exec(compile(ast.Module(body=[parser], type_ignores=[]), 'actual_model_parser', 'exec'), parser_namespace)
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      artifact = root / 'test_navigation.pkl'
      artifact.write_bytes(b'plain-target-stand-in-no-code-execution')
      digest = nav.file_sha256(artifact)
      (root / nav.MANIFEST_NAME).write_text(json.dumps({'version': 1, 'target': 'chestnut',
        'sourceOnnxSha256': nav.SOURCE_ONNX_SHA256, 'artifact': {'fileName': artifact.name, 'sha256': digest}}))
      nav._validated.clear()
      with patch.dict(sys.modules, {'openpilot.sunnypilot.modeld_v2.helpers': NS(read_parts=lambda _path: ({'run': ({}, b'')}, fixture.metadata()))}):
        bundle = parser_namespace['ModelParser']._parse_bundle(nav.installed_bundle(root))
      self.assertEqual(bundle.index, 2147483000)
      self.assertTrue(bundle.ref.startswith('local-rl-nav-80eedcdd-'))
      self.assertEqual(bundle.models[0].artifact.downloadUri.uri, artifact.resolve().as_uri())
      namespace = manager_namespace()
      helper_path = SOURCE / 'helpers.py'
      helper_source = (helper_path.read_text() if helper_path.exists() else subprocess.check_output(
        ['git', '-C', str(SOURCE.parents[2]), 'show', 'HEAD:openpilot/sunnypilot/models/helpers.py'], text=True))
      helper_tree = ast.parse(helper_source)
      functions = [node for node in helper_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and node.name in ('verify_file', '_compute_hash')]
      helper_namespace = {'hashlib': hashlib}
      exec(compile(ast.Module(body=functions, type_ignores=[]), 'actual_file_verifier', 'exec'), helper_namespace)
      namespace.update(custom=custom, verify_file=helper_namespace['verify_file'], ACTIVE_BUNDLE_KEYS={'chestnut': 'ModelManager_ActiveBundleChestnut'},
                       get_active_bundle=Mock(return_value=bundle))
      manager = namespace['ModelManagerSP'].__new__(namespace['ModelManagerSP'])
      manager.params, manager.chestnut_present = Mock(), True
      manager._report_status = Mock()
      manager._download_file = Mock(side_effect=AssertionError('Verified local artifact must never attempt file:// HTTP'))
      asyncio.run(manager._download_bundle(bundle, directory, 'chestnut'))
      manager._download_file.assert_not_called()
      manager.params.put.assert_called_once()
      self.assertEqual(manager.params.put.call_args.args[0], 'ModelManager_ActiveBundleChestnut')
      # Clear cache must retain both parts of the active local installation.
      (root / 'unused-model.pkl').write_bytes(b'unused')
      namespace.update(get_selected_bundle=Mock(return_value=bundle), installed_bundle=nav.installed_bundle,
                       Paths=NS(model_root=lambda: directory))
      manager.clear_model_cache()
      self.assertFalse((root / 'unused-model.pkl').exists())
      self.assertTrue(artifact.exists())
      self.assertIsNotNone(nav.installed_bundle(root))
      namespace['get_selected_bundle'].return_value = None
      manager.clear_model_cache()
      self.assertFalse(artifact.exists())
      self.assertFalse((root / nav.MANIFEST_NAME).exists())
      self.assertIsNone(nav.installed_bundle(root))


if __name__ == '__main__':
  unittest.main()
