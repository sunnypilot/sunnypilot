"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
from tinygrad.tensor import Tensor

from openpilot.common.parameterized import parameterized

import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
import openpilot.sunnypilot.modeld_v2.model_adapters as model_adapters
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, ARCHETYPES, CAM_W, CAM_H
from openpilot.common.test import OpenpilotTestCase

# resolved by name from this module when a test asks for them
tmp_path = tests_helpers.tmp_path
patch_modeld = tests_helpers.patch_modeld

ModelState = modeld_module.ModelState
SHAPES = {'img': (1, 12, 128, 256), 'big_img': (1, 12, 128, 256), 'features_buffer': (1, 24, 32, 512),
          'desire_pulse': (1, 25, 8), 'traffic_convention': (1, 2), 'action_t': (1, 2)}


def _unified_jit(**kwargs):
  return Tensor(np.zeros(1, dtype=np.float32), device='CPU').realize()


def _native_unified_jit(**kwargs):
  return _unified_jit(**kwargs)


def _warp_jit(**kwargs):
  return None


def cpu_queues(monkeypatch):
  for name in ('make_supercombo_input_queues', 'make_split_input_queues'):
    make_queues = getattr(model_adapters, name)
    monkeypatch.setattr(model_adapters, name, lambda *args, make_queues=make_queues, **kwargs: make_queues(*args, **{**kwargs, 'device': 'CPU'}))
  make_stock_queues = model_adapters.stock_make_input_queues
  monkeypatch.setattr(model_adapters, 'stock_make_input_queues',
                     lambda input_shapes, frame_skip, device, frame_copy_size:
                     make_stock_queues(input_shapes, frame_skip, device='CPU', frame_copy_size=frame_copy_size))


def unified_model_factory(tmp_path, monkeypatch, patch_modeld, cpu_queues):
  from openpilot.common.hardware import hw
  from openpilot.sunnypilot.modeld_v2.helpers import dump_oob

  bundle = DummyBundle(models=[DummyModel('supercombo', 'driving_test_tinygrad.pkl')])
  patch_modeld(bundle)
  monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))

  def create(*, cam_size=(CAM_W, CAM_H), chestnut=True, device_type='tizi', comma_hardware=True, include_target=True):
    if chestnut:
      pkl_data = {'metadata': {'model': {'input_shapes': SHAPES, 'output_slices': {}}}, cam_size: _native_unified_jit}
      if include_target and cam_size != (1344, 760):
        pkl_data[(1344, 760)] = _unified_jit
    else:
      pkl_data = {'metadata': {'model': {'input_shapes': SHAPES, 'output_slices': {}}, 'warp_dev': 'CPU'},
                  'run_policy': _unified_jit, cam_size: _warp_jit}
    with open(tmp_path / 'driving_test_tinygrad.pkl', 'wb') as f:
      dump_oob(pkl_data, f)
    monkeypatch.setattr(modeld_module, 'COMMA_HARDWARE', comma_hardware)
    monkeypatch.setattr(modeld_module.HARDWARE, 'get_device_type', lambda: device_type)
    return ModelState(cam_w=cam_size[0], cam_h=cam_size[1], chestnut=chestnut)

  return create


class TestUnifiedFrameResize(OpenpilotTestCase):
  def test_resize_transforms_and_warmup(self, unified_model_factory):
    from openpilot.common.transformations.camera import DEVICE_CAMERAS
    from openpilot.common.transformations.model import get_warp_matrix
    from openpilot.sunnypilot.modeld_v2.camera_offset_helper import CameraOffsetHelper

    state = unified_model_factory()
    adapter = state.adapter
    self.assertIsNotNone(adapter.frame_resize)
    self.assertIs(adapter.run_policy, _unified_jit)
    self.assertEqual(adapter.frame_copy_size, 1622016)
    self.assertEqual(adapter.input_queues['packed_npy_inputs'].shape, (3309688,))
    state.warmup()
    for frame in adapter.frame_slots.values():
      self.assertEqual(frame.size, 1622016)

    frames = {key: np.full(4804608, value, dtype=np.uint8) for key, value in (('img', 7), ('big_img', 9))}
    cameras = DEVICE_CAMERAS[('tizi', 'ox03c10')]
    rpy_calib = np.array([.02, -.03, .01])
    transforms = {}
    for key, camera, wide in (('img', cameras.narrow_road, False), ('big_img', cameras.wide_road, True)):
      native = get_warp_matrix(rpy_calib, camera.intrinsics, wide).astype(np.float32)
      v_horizon = CameraOffsetHelper.get_v_horizon(camera.intrinsics, rpy_calib)
      transforms[key] = CameraOffsetHelper.apply_camera_offset(native, height=1.22, offset_param=.2, v_horizon=v_horizon)
    original_transforms = {key: value.copy() for key, value in transforms.items()}
    sx, sy = 1344 / 1928, 760 / 1208
    scale = np.array([[sx, 0, 0.5 * sx - 0.5], [0, sy, 0.5 * sy - 0.5], [0, 0, 1]], dtype=np.float32)
    inputs = {state.desire_key: np.zeros(8, dtype=np.float32)}
    for _ in range(2):
      self.assertEqual(state.run(frames, transforms, inputs), {})
      np.testing.assert_allclose(state.numpy_inputs['tfm'], scale @ original_transforms['img'], rtol=1e-6, atol=1e-5)
      np.testing.assert_allclose(state.numpy_inputs['big_tfm'], scale @ original_transforms['big_img'], rtol=1e-6, atol=1e-5)
    self.assertTrue(np.all(adapter.frame_slots['img'] == 7))
    self.assertTrue(np.all(adapter.frame_slots['big_img'] == 9))
    for key in transforms:
      np.testing.assert_array_equal(transforms[key], original_transforms[key])

  def test_missing_target_entry_is_rejected(self, unified_model_factory):
    with self.assertRaisesRegex(RuntimeError, "requires a compiled 1344x760 model entry"):
      unified_model_factory(include_target=False)

  @parameterized.expand([
    (True, 'tici', (1928, 1208)),
    (True, 'mici', (1344, 760)),
    (False, 'pc', (1928, 1208)),
    (True, 'tizi', (1344, 760)),
  ], names=['comma_hardware', 'device_type', 'cam_size'])
  def test_ineligible_models_keep_native_inputs(self, comma_hardware, device_type, cam_size, unified_model_factory):
    state = unified_model_factory(comma_hardware=comma_hardware, device_type=device_type, cam_size=cam_size, include_target=False)
    adapter = state.adapter
    self.assertIsNone(adapter.frame_resize)
    self.assertIs(adapter.run_policy, _native_unified_jit)
    layout = model_adapters.get_nv12_info(*cam_size)
    self.assertEqual(adapter.frame_copy_size, model_adapters.nv12_copy_size(*layout[:3]))
    source = (np.arange(layout[3], dtype=np.uint32) % 251).astype(np.uint8)
    frames = dict.fromkeys(state.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transform = np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32)
    state.run(frames, dict.fromkeys(state.vision_input_names, transform), {state.desire_key: np.zeros(8, dtype=np.float32)})
    for key in state.vision_input_names:
      np.testing.assert_array_equal(adapter.frame_slots[key], source[:adapter.frame_copy_size])
    for key in ('tfm', 'big_tfm'):
      np.testing.assert_array_equal(state.numpy_inputs[key], transform)

  @parameterized.expand(['supercombo_non20hz', 'vision_policy_split'], names=['archetype'])
  def test_separate_warp_is_not_resized(self, archetype, tmp_path, monkeypatch, patch_modeld, cpu_queues):
    from openpilot.common.hardware import hw
    from openpilot.sunnypilot.modeld_v2.helpers import dump_oob

    arch = ARCHETYPES[archetype]
    with open(tmp_path / 'driving_test_tinygrad.pkl', 'wb') as f:
      dump_oob(tests_helpers.make_pkl_data(arch), f)
    patch_modeld(tests_helpers.make_bundle(arch))
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    monkeypatch.setattr(modeld_module, 'COMMA_HARDWARE', True)
    monkeypatch.setattr(modeld_module.HARDWARE, 'get_device_type', lambda: 'tizi')

    state = ModelState(cam_w=CAM_W, cam_h=CAM_H, chestnut=True)
    self.assertEqual(state.DEV, 'AMD')
    self.assertIsNone(state.adapter.frame_resize)
    self.assertEqual(state.adapter.frame_copy_size, 3735552)

  def test_shared_vision_buffer_is_packed_before_enqueue(self, unified_model_factory):
    state = unified_model_factory()
    adapter = state.adapter
    source_copy_size = adapter.frame_resize.source_copy_size
    source = np.full(4804608, 255, dtype=np.uint8)
    source[:source_copy_size] = 17
    frames = dict.fromkeys(state.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transforms = dict.fromkeys(state.vision_input_names, np.eye(3, dtype=np.float32))
    captured = []

    def capture(**kwargs):
      captured.append(kwargs['packed_npy_inputs'].numpy().copy())
      return _unified_jit(**kwargs)

    adapter.run_policy = capture
    state.run(frames, transforms, {state.desire_key: np.zeros(8, dtype=np.float32)})
    self.assertEqual(captured[0].shape, (3309688,))
    self.assertTrue(np.all(captured[0][-2 * adapter.frame_copy_size:] == 17))
    self.assertFalse(np.shares_memory(adapter.frame_slots['img'], adapter.frame_slots['big_img']))
    np.testing.assert_array_equal(adapter.frame_slots['img'], adapter.frame_slots['big_img'])
    self.assertTrue(np.all(source[:source_copy_size] == 17))
    self.assertTrue(np.all(source[source_copy_size:] == 255))

  def test_short_source_error_prevents_enqueue(self, unified_model_factory):
    state = unified_model_factory()
    adapter = state.adapter
    adapter.run_policy = Mock(wraps=adapter.run_policy)
    frames = dict.fromkeys(state.vision_input_names,
                           SimpleNamespace(data=np.zeros(adapter.frame_resize.source_copy_size - 1, dtype=np.uint8)))
    transforms = dict.fromkeys(state.vision_input_names, np.eye(3, dtype=np.float32))
    with self.assertRaises(ValueError):
      state.run(frames, transforms, {state.desire_key: np.zeros(8, dtype=np.float32)})
    adapter.run_policy.assert_not_called()

  def test_small_model_inputs_are_isolated_after_big_model_failure(self, unified_model_factory):
    big = unified_model_factory()
    small = unified_model_factory(chestnut=False)
    source = (np.arange(4804608, dtype=np.uint32) % 251).astype(np.uint8)
    frames = dict.fromkeys(big.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transform = np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32)
    original = transform.copy()
    transforms = dict.fromkeys(big.vision_input_names, transform)
    big.adapter.run_policy = Mock(side_effect=RuntimeError("AMD failed"))
    with self.assertRaisesRegex(RuntimeError, "AMD failed"):
      big.run(frames, transforms, {big.desire_key: np.zeros(8, dtype=np.float32)})

    self.assertEqual(small.run(frames, transforms, {small.desire_key: np.zeros(8, dtype=np.float32)}), {})
    self.assertIsNone(small.adapter.frame_resize)
    np.testing.assert_array_equal(transform, original)
    for key in small.vision_input_names:
      np.testing.assert_array_equal(small.adapter.full_frames[key].numpy(), source)
    for key in ('tfm', 'big_tfm'):
      np.testing.assert_array_equal(small.numpy_inputs[key], original)
