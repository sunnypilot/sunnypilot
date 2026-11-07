"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import codecs
import pickle
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.common.parameterized import parameterized

import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle
from openpilot.common.test import OpenpilotTestCase

# resolved by name from this module when a test asks for them
tmp_path = tests_helpers.tmp_path
patch_modeld = tests_helpers.patch_modeld

SOURCE_BUFFER_SIZE = 4804608
SOURCE_COPY_SIZE = 3735552
TARGET_COPY_SIZE = 1622016


def _run_model(**kwargs):
  return None


def native_model_factory(tmp_path, monkeypatch, patch_modeld):
  from openpilot.common.hardware import hw

  patch_modeld(DummyBundle(models=[DummyModel('supercombo', 'driving_test_tinygrad.pkl')]))
  monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
  error_state = SimpleNamespace(host=SimpleNamespace(view=lambda fmt: [0]))
  monkeypatch.setattr(modeld_module, 'Device', dict.fromkeys(('AMD', 'CPU'), SimpleNamespace(error_state=error_state)))

  input_specs = {'new_img': ((1, 12, 128, 256), 'uint8', 'CPU'), 'desire': ((1, 8), 'float32', 'CPU'),
                 'traffic_convention': ((1, 2), 'float32', 'CPU')}
  metadata = {'input_shapes': {'img': (1, 12, 128, 256), 'big_img': (1, 12, 128, 256)}, 'output_shapes': {},
              'metadata': {'output_slices': codecs.encode(pickle.dumps({}), 'base64').decode()}}
  (tmp_path / 'driving_test_tinygrad.pkl').write_bytes(pickle.dumps({
    'input_specs': input_specs, 'output_specs': {'outputs': ((1, 1), 'float32', 'CPU')}, 'metadata': metadata, 'run': _run_model}))

  fused_warps = []

  def load_model(path, extend=None, **_):
    fused_warps.append(Path(extend.args[0]).name)
    return pickle.loads(Path(path).read_bytes())
  monkeypatch.setattr(modeld_module, 'load_model', load_model)

  def create(*, chestnut=True, device_type='tizi', comma_hardware=True):
    monkeypatch.setattr(modeld_module, 'COMMA_HARDWARE', comma_hardware)
    monkeypatch.setattr(modeld_module.HARDWARE, 'get_device_type', lambda: device_type)
    return modeld_module.ModelState(cam_w=1928, cam_h=1208, chestnut=chestnut)

  create.fused_warps = fused_warps
  return create


class TestNativeFrameResize(OpenpilotTestCase):
  def test_resize_fuses_target_warp(self, native_model_factory):
    state = native_model_factory()
    adapter = state.adapter
    self.assertIsNotNone(adapter.frame_resize)
    self.assertEqual(native_model_factory.fused_warps, ['big_driving_warp_1344x760_tinygrad.pkl'])
    self.assertEqual(adapter.frames.shape, (2, TARGET_COPY_SIZE))
    state.warmup()

    frames = {key: SimpleNamespace(data=np.full(SOURCE_BUFFER_SIZE, value, dtype=np.uint8)) for key, value in (('img', 7), ('big_img', 9))}
    transforms = {
      'img': np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32),
      'big_img': np.array([[7, 8, 9], [10, 11, 12], [.03, .04, 1]], dtype=np.float32),
    }
    original_transforms = {key: value.copy() for key, value in transforms.items()}
    sx, sy = 1344 / 1928, 760 / 1208
    scale = np.array([[sx, 0, 0.5 * sx - 0.5], [0, sy, 0.5 * sy - 0.5], [0, 0, 1]], dtype=np.float32)
    self.assertEqual(state.run(frames, transforms, {state.desire_key: np.zeros(8, dtype=np.float32)}), {})

    for i, (key, value) in enumerate((('img', 7), ('big_img', 9))):
      self.assertTrue(np.all(adapter.frames[i] == value))
      np.testing.assert_allclose(state.numpy_inputs['tfm'][i], scale @ original_transforms[key], rtol=1e-6)
      np.testing.assert_array_equal(transforms[key], original_transforms[key])

  @parameterized.expand([
    (True, 'tici', True),
    (False, 'pc', True),
    (True, 'tizi', False),
  ], names=['comma_hardware', 'device_type', 'chestnut'])
  def test_ineligible_models_keep_source_warp(self, comma_hardware, device_type, chestnut, native_model_factory):
    state = native_model_factory(comma_hardware=comma_hardware, device_type=device_type, chestnut=chestnut)
    adapter = state.adapter
    self.assertIsNone(adapter.frame_resize)
    self.assertEqual(native_model_factory.fused_warps, [f'{"big_" if chestnut else ""}driving_warp_1928x1208_tinygrad.pkl'])
    self.assertEqual(adapter.frames.shape, (2, SOURCE_COPY_SIZE))

    source = (np.arange(SOURCE_BUFFER_SIZE, dtype=np.uint32) % 251).astype(np.uint8)
    transform = np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32)
    state.run(dict.fromkeys(state.vision_input_names, SimpleNamespace(data=memoryview(source))),
              dict.fromkeys(state.vision_input_names, transform), {state.desire_key: np.zeros(8, dtype=np.float32)})
    for i in range(2):
      np.testing.assert_array_equal(adapter.frames[i], source[:SOURCE_COPY_SIZE])
      np.testing.assert_array_equal(state.numpy_inputs['tfm'][i], transform)
