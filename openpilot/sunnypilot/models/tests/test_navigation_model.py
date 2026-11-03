"""Local selector entries require an installed verified target artifact."""
import ast
import base64
import builtins
import hashlib
import importlib.util
import json
import io
import mmap
from pathlib import Path
import pickle
import sys
import struct
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_nav_model_under_test', SOURCE / 'navigation_model.py')
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)


def metadata(*, device='USB+AMD:LLVM'):
  inputs = {'new_img': ((2, 6, 128, 256), '|u1', device),
            'desire': ((8,), '<f4', device), 'traffic_convention': ((1, 2), '<f4', device), 'action_t': ((1, 2), '<f4', device),
            'nav_map': ((1, 1, 256, 256), '<f4', device), 'navigation': ((1, 47), '<f4', device),
            'state_img_q': ((2, 5, 6, 128, 256), '|u1', device), 'state_desire_q': ((132, 1, 8), '<f4', device),
            'state_feat_q': ((128, 1, 16384), '<f4', device),
            'state_map_features_q': ((128, 1, 64), '<f4', device),
            'state_navigation_features_q': ((128, 1, 64), '<f4', device)}
  slices = {'plan': slice(917, 1907), 'action': slice(2062, 2066),
            'desire_state': slice(2054, 2062), 'desire_pred': slice(855, 887)}
  outputs = {'outputs': ((1, 18580), '<f4', device)} | {'next_' + name: value for name, value in inputs.items() if name.startswith('state_')}
  return {'input_specs': inputs, 'output_specs': outputs,
          'metadata': {'metadata': {'output_slices': base64.b64encode(pickle.dumps(slices)).decode()},
                       'output_shapes': {name: value[0] for name, value in outputs.items()}}}


class LocalNavigationModelTests(unittest.TestCase):
  def setUp(self):
    self.temporary = TemporaryDirectory()
    self.root = Path(self.temporary.name)
    self.artifact = self.root / 'local_nav_test.pkl'
    self.artifact.write_bytes(b'test-plain-artifact-no-kernel-execution')
    self.descriptor = {'version': 1, 'target': 'chestnut', 'sourceOnnxSha256': nav.SOURCE_ONNX_SHA256,
                       'artifact': {'fileName': self.artifact.name, 'sha256': hashlib.sha256(self.artifact.read_bytes()).hexdigest()}}
    self.extras = metadata()
    nav._validated.clear()
    self.reader = SimpleNamespace(read_parts=lambda _path: ({'run': ({}, b'')}, self.extras))
    self.patch = patch.dict(sys.modules, {'openpilot.sunnypilot.modeld_v2.helpers': self.reader})
    self.patch.start()

  def tearDown(self):
    self.patch.stop()
    self.temporary.cleanup()

  def write(self, changes=None):
    (self.root / nav.MANIFEST_NAME).write_text(json.dumps(self.descriptor | (changes or {})))

  def test_no_installed_manifest_means_no_selectable_entry(self):
    self.assertIsNone(nav.installed_bundle(self.root))
    self.write()
    self.artifact.unlink()
    self.assertIsNone(nav.installed_bundle(self.root))

  def test_verified_native_target_is_normal_explicit_bundle_not_n16_claim(self):
    self.write()
    bundle = nav.installed_bundle(self.root)
    self.assertEqual(bundle['generation'], 12)
    self.assertTrue(bundle['is_20hz'])
    self.assertEqual(bundle['minimum_selector_version'], 21)
    self.assertEqual(bundle['runner'], 'tinygrad')
    self.assertIn('80eedcdd', bundle['display_name'])
    self.assertNotIn('N16', bundle['display_name'])
    self.assertEqual(bundle['overrides']['lat'], '.0')
    self.assertEqual(bundle['models'][0]['artifact']['download_uri']['sha256'], self.descriptor['artifact']['sha256'])
    self.assertNotIn('selected', bundle)

  def test_model_hash_source_or_path_tamper_never_registers(self):
    for change in ({'sourceOnnxSha256': '0' * 64}, {'target': 'metal'},
                   {'artifact': {'fileName': '../escape.pkl', 'sha256': 'a' * 64}},
                   {'artifact': {'fileName': self.artifact.name, 'sha256': 'a' * 64}}):
      self.write(change)
      self.assertIsNone(nav.installed_bundle(self.root))

  def test_mac_cpu_small_or_missing_nav_metadata_never_registers(self):
    self.write()
    for extras in (metadata(device='METAL'), metadata(device='CPU'), {'input_specs': {}, 'metadata': {}},
                   metadata() | {'metadata': {'output_shapes': {'outputs': (1, 2576)}}}):
      self.extras = extras
      nav._validated.clear()
      self.assertIsNone(nav.installed_bundle(self.root))

  def test_changed_installed_bytes_are_reverified(self):
    self.write()
    self.assertIsNotNone(nav.installed_bundle(self.root))
    self.artifact.write_bytes(b'changed artifact bytes')
    self.assertIsNone(nav.installed_bundle(self.root))

  def test_incompatible_action_layout_cannot_claim_generation12(self):
    self.write()
    slices = {'plan': slice(917, 1907), 'action': slice(2062, 2070),
              'desire_state': slice(2054, 2062), 'desire_pred': slice(855, 887)}
    self.extras['metadata']['metadata']['output_slices'] = base64.b64encode(pickle.dumps(slices)).decode()
    self.assertIsNone(nav.installed_bundle(self.root))

  def test_every_state_pair_needs_matching_output_shape_and_dtype(self):
    for name in ('state_img_q', 'state_desire_q', 'state_feat_q', 'state_map_features_q', 'state_navigation_features_q'):
      for change in ('missing', 'shape', 'dtype'):
        extras = metadata()
        output = 'next_' + name
        if change == 'missing':
          extras['metadata']['output_shapes'].pop(output)
        elif change == 'shape':
          extras['metadata']['output_shapes'][output] = (1,)
        else:
          shape, _, device = extras['output_specs'][output]
          extras['output_specs'][output] = (shape, '<f8', device)
        self.assertFalse(nav.compatible_metadata(extras), (name, change))

  def test_host_input_and_malformed_metadata_contracts_fail_closed(self):
    for name in ('desire', 'traffic_convention', 'action_t'):
      extras = metadata()
      extras['input_specs'][name] = ((99,), '<f4', 'USB+AMD:LLVM')
      self.assertFalse(nav.compatible_metadata(extras))
    for extras in (None, [], {}, {'input_specs': []}, metadata() | {'input_specs': {'new_img': ()}}):
      self.assertFalse(nav.compatible_metadata(extras))

  def test_invalid_plain_metadata_fails_closed_without_code_execution(self):
    self.write()
    def invalid(_path):
      raise pickle.UnpicklingError('Rejected arbitrary metadata class')
    self.reader.read_parts = invalid
    self.assertIsNone(nav.installed_bundle(self.root))


def real_navigation_metadata():
  fixture = json.loads((SOURCE / 'tests/fixtures/rl_nav_80eedcdd_metadata.json').read_text())
  for name, value in fixture['input_specs'].items():
    fixture['input_specs'][name] = (tuple(value[0]), nav.np.dtype(value[1]).str, value[2])
  for name, value in fixture['output_specs'].items():
    fixture['output_specs'][name] = (tuple(value[0]), nav.np.dtype(value[1]).name, value[2])
  for kind in ('input_shapes', 'output_shapes'):
    fixture['metadata'][kind] = {name: tuple(shape) for name, shape in fixture['metadata'][kind].items()}
  return fixture


def plain_io_functions():
  """Execute the exact plain writer/reader definitions, with no GPU imports."""
  path = SOURCE.parents[0] / 'modeld_v2/helpers.py'
  text = path.read_text() if path.exists() else subprocess.check_output(
    ['git', '-C', str(SOURCE.parents[2]), 'show', 'HEAD:openpilot/sunnypilot/modeld_v2/helpers.py'], text=True)
  names = {'Blob', '_MetadataUnpickler', '_relocate', 'write_bundle', 'read_parts'}
  constants = {'MAGIC', 'ALIGNMENT', 'METADATA_TYPES'}
  selected = []
  for node in ast.parse(text).body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
      selected.append(node)
    elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets):
      selected.append(node)
  namespace = {'hashlib': hashlib, 'builtins': builtins, 'pickle': pickle, 'struct': struct, 'json': json,
               'io': io, 'mmap': mmap}
  exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
  return namespace['write_bundle'], namespace['read_parts']


class RealNavigationMetadataTests(unittest.TestCase):
  def test_exact_official_wrapped_metadata_survives_actual_plain_roundtrip(self):
    fixture = real_navigation_metadata()
    self.assertEqual(fixture['provenance']['officialOnnxSha256'], nav.SOURCE_ONNX_SHA256)
    self.assertEqual(fixture['provenance']['officialOnnxBytes'], nav.SOURCE_ONNX_BYTES)
    self.assertEqual(fixture['metadata']['metadata']['output_slices'].count('\n'), 9)
    write_bundle, read_parts = plain_io_functions()
    with TemporaryDirectory() as directory:
      path = Path(directory) / 'real_metadata_plain_fixture.pkl'
      # An empty, non-executable run part is sufficient to test the actual format.
      write_bundle(path, {'run': ({'calls': [], 'buffers': []}, b'')}, fixture)
      parts, decoded = read_parts(path)
      self.assertIn('run', parts)
      self.assertEqual(decoded, fixture)
      self.assertTrue(nav.compatible_metadata(decoded))
      (Path(directory) / nav.MANIFEST_NAME).write_text(json.dumps({'version': 1, 'target': 'chestnut',
        'sourceOnnxSha256': nav.SOURCE_ONNX_SHA256,
        'artifact': {'fileName': path.name, 'sha256': nav.file_sha256(path)}}))
      with patch.dict(sys.modules, {'openpilot.sunnypilot.modeld_v2.helpers': SimpleNamespace(read_parts=read_parts)}):
        self.assertIsNotNone(nav.installed_bundle(directory))

  def test_ascii_wrapping_is_allowed_but_corrupt_base64_is_rejected(self):
    fixture = real_navigation_metadata()
    original = fixture['metadata']['metadata']['output_slices']
    compact = ''.join(original.split())
    fixture['metadata']['metadata']['output_slices'] = ' \t\r\n'.join(compact[i:i+16] for i in range(0, len(compact), 16))
    self.assertTrue(nav.compatible_metadata(fixture))
    for encoded in (compact[:8] + '!' + compact[8:], compact[:-1], compact[:8] + '\u00a0' + compact[8:]):
      with self.subTest(encoded=encoded[:20]):
        fixture['metadata']['metadata']['output_slices'] = encoded
        self.assertFalse(nav.compatible_metadata(fixture))

  def test_wrapping_does_not_permit_executable_or_wrong_slice_metadata(self):
    class ExecutableMetadata:
      def __reduce__(self):
        return builtins.eval, ('1 + 1',)
    fixture = real_navigation_metadata()
    payload = base64.encodebytes(pickle.dumps(ExecutableMetadata())).decode('ascii')
    fixture['metadata']['metadata']['output_slices'] = payload
    with patch.object(builtins, 'eval', side_effect=AssertionError('Metadata must never execute')) as execute:
      self.assertFalse(nav.compatible_metadata(fixture))
      execute.assert_not_called()
    original = real_navigation_metadata()['metadata']['metadata']['output_slices']
    slices = nav._SliceMetadata(io.BytesIO(base64.b64decode(original))).load()
    slices['action'] = slice(2062, 2070)
    fixture['metadata']['metadata']['output_slices'] = base64.encodebytes(pickle.dumps(slices)).decode('ascii')
    self.assertFalse(nav.compatible_metadata(fixture))
    fixture['metadata']['metadata']['output_slices'] = base64.encodebytes(pickle.dumps([])).decode('ascii')
    self.assertFalse(nav.compatible_metadata(fixture))


class CatalogHookTests(unittest.TestCase):
  def test_cached_offline_model_is_selectable_without_changing_remote_cache(self):
    tree = ast.parse((SOURCE / 'fetcher.py').read_text())
    methods = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ('_with_local_navigation', 'get_cached_bundles')]
    local, remote = SimpleNamespace(ref='local-verified'), SimpleNamespace(ref='remote')
    payload = {'bundles': [{'ref': 'remote'}]}
    namespace = {'Params': object, 'custom': SimpleNamespace(ModelManagerSP=SimpleNamespace(ModelBundle=object)),
                 'ModelFetcher': SimpleNamespace(MODEL_SOURCES={'chestnut': ('url', '_Chestnut'), 'qcom': ('url', '')}),
                 'ModelParser': SimpleNamespace(parse_models=lambda value: [remote], _parse_bundle=lambda value: local),
                 'cloudlog': SimpleNamespace(warning=lambda *_args: None)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])), 'actual_catalog_hook', 'exec'), namespace)
    modules = {'openpilot.common.hardware.hw': SimpleNamespace(Paths=SimpleNamespace(model_root=lambda: '/test/models')),
               'openpilot.sunnypilot.models.navigation_model': SimpleNamespace(installed_bundle=lambda path: {'ref': local.ref})}
    with patch.dict(sys.modules, modules):
      cached = namespace['get_cached_bundles'](SimpleNamespace(get=lambda _key: payload), 'chestnut')
      self.assertEqual(cached, [remote, local])
      self.assertEqual(payload, {'bundles': [{'ref': 'remote'}]})
      offline = namespace['get_cached_bundles'](SimpleNamespace(get=lambda _key: None), 'chestnut')
      self.assertEqual(offline, [local])
      self.assertEqual(namespace['_with_local_navigation']([remote], 'qcom'), [remote])


class OffroadBuilderTests(unittest.TestCase):
  def test_cli_failure_is_nonzero_and_never_registers(self):
    # Detailed stream/build/cancel behavior is covered in test_navigation_preparation.
    with TemporaryDirectory() as directory:
      root = Path(directory)
      modules = {
        'openpilot.sunnypilot.models.navigation_model': nav,
        'openpilot.common.basedir': SimpleNamespace(BASEDIR=str(SOURCE.parents[2])),
        'openpilot.common.hardware': SimpleNamespace(COMMA_HARDWARE=False),
        'openpilot.common.hardware.hw': SimpleNamespace(Paths=SimpleNamespace(model_root=lambda: str(root))),
        'openpilot.common.params': SimpleNamespace(Params=lambda: SimpleNamespace(get_bool=lambda _key: False)),
      }
      with patch.dict(sys.modules, modules), patch.object(sys, 'argv', ['build_navigation_model']):
        builder_spec = importlib.util.spec_from_file_location('nav_builder_under_test', SOURCE / 'build_navigation_model.py')
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        with patch.object(builder.subprocess, 'Popen', side_effect=AssertionError('Compiler must not start')):
          with self.assertRaises(SystemExit) as error:
            builder.main()
          self.assertEqual(error.exception.code, 1)
        self.assertFalse((root / nav.MANIFEST_NAME).exists())


if __name__ == '__main__':
  unittest.main()
