"""Local fine-tuned Chestnut builds appear in the selector only as verified native-protocol artifacts."""
import base64
import hashlib
import json
import pickle
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from openpilot.sunnypilot.models import local_model


def metadata(*, device='USB+AMD:LLVM', extra_inputs=None, width=18452):
  inputs = {'new_img': ((2, 6, 128, 256), '|u1', device),
            'desire': ((8,), '<f4', device), 'traffic_convention': ((1, 2), '<f4', device), 'action_t': ((1, 2), '<f4', device),
            'state_img_q': ((2, 5, 6, 128, 256), '|u1', device), 'state_desire_q': ((132, 1, 8), '<f4', device),
            'state_feat_q': ((128, 1, 16384), '<f4', device)} | (extra_inputs or {})
  slices = {'plan': slice(917, 1907), 'action': slice(2062, 2066),
            'desire_state': slice(2054, 2062), 'desire_pred': slice(855, 887)}
  outputs = {'outputs': ((1, width), '<f4', device)} | {'next_' + name: value for name, value in inputs.items() if name.startswith('state_')}
  return {'input_specs': inputs, 'output_specs': outputs,
          'metadata': {'metadata': {'output_slices': base64.b64encode(pickle.dumps(slices)).decode()},
                       'output_shapes': {name: value[0] for name, value in outputs.items()}}}


class LocalModelTests(unittest.TestCase):
  def setUp(self):
    self.temporary = TemporaryDirectory()
    self.root = Path(self.temporary.name)
    self.artifact = self.root / 'local_ff_turns_0123456789abcdef_tinygrad.pkl'
    self.artifact.write_bytes(b'test-plain-artifact-no-kernel-execution')
    self.descriptor = {'version': 1, 'target': 'chestnut', 'id': 'ff_turns', 'displayName': 'Flip Flop turns FT (experimental)',
                       'shortName': 'FFTURNS', 'sourceOnnxSha256': '0' * 64,
                       'artifact': {'fileName': self.artifact.name, 'sha256': hashlib.sha256(self.artifact.read_bytes()).hexdigest()}}
    self.extras = metadata()
    local_model._validated.clear()
    reader = SimpleNamespace(read_parts=lambda _path: ({'run': ({}, b'')}, self.extras))
    self.patch = patch.dict(sys.modules, {'openpilot.sunnypilot.modeld_v2.helpers': reader})
    self.patch.start()

  def tearDown(self):
    self.patch.stop()
    self.temporary.cleanup()

  def write(self, changes=None, name=None):
    (self.root / (name or local_model.manifest_name('ff_turns'))).write_text(json.dumps(self.descriptor | (changes or {})))

  def test_no_manifest_or_artifact_means_no_entry(self):
    self.assertEqual(local_model.installed_bundles(self.root), [])
    self.write()
    self.artifact.unlink()
    self.assertEqual(local_model.installed_bundles(self.root), [])

  def test_verified_build_is_a_big_native_bundle_in_the_local_folder(self):
    self.write()
    [bundle] = local_model.installed_bundles(self.root)
    self.assertEqual(bundle['display_name'], 'Flip Flop turns FT (experimental)')
    self.assertEqual(bundle['generation'], 12)
    self.assertTrue(bundle['is_big'])
    self.assertTrue(bundle['is_20hz'])
    self.assertEqual(bundle['overrides'], {'folder': 'Local experimental models', 'lat': '.0', 'long': '.3'})
    self.assertTrue(bundle['ref'].startswith('local-ff_turns-'))
    artifact = bundle['models'][0]['artifact']
    self.assertEqual(artifact['file_name'], self.artifact.name)
    self.assertEqual(artifact['download_uri']['url'], self.artifact.resolve().as_uri())
    self.assertEqual(local_model.manifest_for_artifact(self.root, self.artifact.name), local_model.manifest_name('ff_turns'))
    self.assertIsNone(local_model.manifest_for_artifact(self.root, 'other.pkl'))

  def test_changed_artifact_bytes_are_refused(self):
    self.write()
    self.artifact.write_bytes(b'changed')
    self.assertEqual(local_model.installed_bundles(self.root), [])

  def test_navigation_or_cpu_builds_are_refused(self):
    self.write()
    self.extras = metadata(extra_inputs={'navigation': ((1, 47), '<f4', 'USB+AMD:LLVM')}, width=18580)
    self.assertEqual(local_model.installed_bundles(self.root), [])
    local_model._validated.clear()
    self.extras = metadata(device='CPU')
    self.assertEqual(local_model.installed_bundles(self.root), [])

  def test_manifest_must_name_its_own_id_and_stay_in_the_model_root(self):
    self.write(name=local_model.manifest_name('other'))
    self.assertEqual(local_model.installed_bundles(self.root), [])
    (self.root / local_model.manifest_name('other')).unlink()
    self.write({'id': 'Bad-ID'}, name=local_model.manifest_name('Bad-ID'))
    self.assertEqual(local_model.installed_bundles(self.root), [])
    self.write({'artifact': self.descriptor['artifact'] | {'fileName': '../escape.pkl'}})
    self.assertEqual(local_model.installed_bundles(self.root), [])


class StagedBuildTests(unittest.TestCase):
  def setUp(self):
    self.temporary = TemporaryDirectory()
    self.root = Path(self.temporary.name)
    staging = self.root / local_model.STAGING_DIR
    staging.mkdir()
    self.onnx = staging / 'ff_turns.onnx'
    self.onnx.write_bytes(b'fake onnx bytes')
    self.sha = hashlib.sha256(self.onnx.read_bytes()).hexdigest()
    self.sidecar = staging / 'ff_turns.json'
    self.sidecar.write_text(json.dumps({'displayName': 'Flip Flop turns FT', 'shortName': 'FFTURNS', 'sha256': self.sha}))
    self.compiler = self.root / 'fake_compiler.py'
    self.compiler.write_text("import sys\nopen(sys.argv[2], 'wb').write(b'compiled ' + open(sys.argv[1], 'rb').read())\n")
    local_model._validated.clear()
    reader = SimpleNamespace(read_parts=lambda _path: ({'run': ({}, b'')}, metadata()))
    self.patches = [patch.dict(sys.modules, {'openpilot.sunnypilot.modeld_v2.helpers': reader})]
    for item in self.patches:
      item.start()
    from openpilot.sunnypilot.models import build_local_model
    self.builder = build_local_model
    self.params = SimpleNamespace(get_bool=lambda key: key == 'IsOffroad', get=lambda key: 'queued')

  def tearDown(self):
    for item in self.patches:
      item.stop()
    self.temporary.cleanup()

  def run_build(self):
    reports = []
    with patch.object(self.builder, 'preflight', return_value=self.compiler), \
         patch.object(self.builder.shutil, 'disk_usage', return_value=SimpleNamespace(free=8 * 1024 ** 3)):
      count = self.builder.build_staged(self.root, str(self.root), self.params, True, queued=True, report=reports.append)
    return count, reports

  def test_a_staged_model_is_found_until_its_build_is_installed(self):
    [staged] = local_model.staged_models(self.root)
    self.assertEqual((staged['id'], staged['sha256'], staged['shortName']), ('ff_turns', self.sha, 'FFTURNS'))
    count, reports = self.run_build()
    self.assertEqual(count, 1)
    self.assertEqual(reports[-1]['stage'], 'ready')
    [bundle] = local_model.installed_bundles(self.root)
    self.assertEqual(bundle['display_name'], 'Flip Flop turns FT')
    self.assertEqual(local_model.staged_models(self.root), [])
    self.assertEqual(self.run_build()[0], 0)  # nothing left to build

  def test_a_changed_onnx_is_built_again_and_replaces_the_old_artifact(self):
    self.run_build()
    self.onnx.write_bytes(b'fine-tuned again')
    self.sidecar.write_text(json.dumps({'displayName': 'Flip Flop turns FT', 'shortName': 'FFTURNS',
                                        'sha256': hashlib.sha256(b'fine-tuned again').hexdigest()}))
    self.assertEqual(len(local_model.staged_models(self.root)), 1)
    self.run_build()
    self.assertEqual(len(list(self.root.glob('local_ff_turns_*_tinygrad.pkl'))), 1)
    self.assertEqual(len(local_model.installed_bundles(self.root)), 1)

  def test_a_truncated_copy_is_refused_and_nothing_registered(self):
    self.onnx.write_bytes(b'fake onnx')
    with self.assertRaises(RuntimeError):
      self.run_build()
    self.assertEqual(local_model.installed_bundles(self.root), [])

  def test_cancel_or_driving_off_stops_the_build(self):
    self.params = SimpleNamespace(get_bool=lambda key: key == 'IsOffroad', get=lambda key: None)
    with self.assertRaises(self.builder.PreparationCancelled):
      self.run_build()
    self.params = SimpleNamespace(get_bool=lambda key: False, get=lambda key: 'queued')
    with self.assertRaises(self.builder.PreparationCancelled):
      self.run_build()
    self.assertEqual(local_model.installed_bundles(self.root), [])

  def test_bad_sidecars_are_ignored(self):
    for text in ('not json', json.dumps({'displayName': 'x', 'shortName': 'X'}),
                 json.dumps({'displayName': 'x', 'shortName': 'X' * 13, 'sha256': self.sha})):
      self.sidecar.write_text(text)
      self.assertEqual(local_model.staged_models(self.root), [])
    bad = self.root / local_model.STAGING_DIR / 'Bad-Id.json'
    bad.write_text(json.dumps({'displayName': 'x', 'shortName': 'X', 'sha256': self.sha}))
    (self.root / local_model.STAGING_DIR / 'Bad-Id.onnx').write_bytes(b'x')
    self.assertEqual(local_model.staged_models(self.root), [])


if __name__ == '__main__':
  unittest.main()
