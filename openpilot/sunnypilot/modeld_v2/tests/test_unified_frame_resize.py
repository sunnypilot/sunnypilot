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
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, ARCHETYPES, CAM_W, CAM_H
from openpilot.common.test import OpenpilotTestCase

# resolved by name from this module when a test asks for them
tmp_path = tests_helpers.tmp_path
patch_modeld = tests_helpers.patch_modeld

ModelState = modeld_module.ModelState


def _unified_jit(**kwargs):
  return (Tensor(np.zeros(1, dtype=np.float32), device='CPU').realize(),)


def _native_unified_jit(**kwargs):
  return _unified_jit(**kwargs)


def unified_model_factory(tmp_path, monkeypatch, patch_modeld):
  from openpilot.common.hardware import hw
  from openpilot.selfdrive.modeld.helpers import dump_oob

  shapes = {'img': (1, 12, 128, 256), 'big_img': (1, 12, 128, 256), 'features_buffer': (1, 24, 32, 512),
            'desire_pulse': (1, 25, 8), 'traffic_convention': (1, 2), 'action_t': (1, 2)}
  bundle = DummyBundle(models=[DummyModel('supercombo', 'driving_test_tinygrad.pkl')])
  patch_modeld(bundle)
  monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
  make_queues = modeld_module.make_stock_input_queues
  monkeypatch.setattr(modeld_module, 'make_stock_input_queues',
                     lambda input_shapes, frame_skip, device, frame_copy_size:
                     make_queues(input_shapes, frame_skip, device='CPU', frame_copy_size=frame_copy_size))

  def create(*, cam_size=(CAM_W, CAM_H), chestnut=True, device_type='tizi', comma_hardware=True, include_target=True):
    pkl_data = {'metadata': {'model': {'input_shapes': shapes, 'output_slices': {}}},
                'run_model': {cam_size: _native_unified_jit}}
    if include_target and cam_size != (1344, 760):
      pkl_data['run_model'][(1344, 760)] = _unified_jit
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
    self.assertEqual(state.source_frame_copy_size, 3735552)
    self.assertEqual(state.frame_copy_size, 1622016)
    self.assertIs(state.run_model, _unified_jit)
    self.assertEqual(state.WARP_DEV, 'QCOM')
    old_frames = state.frame_buffers.copy()
    state.warmup()
    self.assertIs(state.frame_views, state.frame_buffers)
    self.assertIs(state.npy, state.numpy_inputs)
    self.assertEqual(state.input_queues['packed_npy_inputs'].shape, (3309688,))
    for key, frame in state.frame_buffers.items():
      self.assertIsNot(frame, old_frames[key])
      self.assertEqual(frame.size, 1622016)

    frames = {key: np.full(3735552, value, dtype=np.uint8) for key, value in (('img', 7), ('big_img', 9))}
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
    self.assertTrue(np.all(state.frame_buffers['img'] == 7))
    self.assertTrue(np.all(state.frame_buffers['big_img'] == 9))
    for key in transforms:
      np.testing.assert_array_equal(transforms[key], original_transforms[key])
      self.assertTrue(np.all(old_frames[key] == 0))

  def test_missing_target_entry_is_rejected(self, unified_model_factory):
    with self.assertRaisesRegex(RuntimeError, "requires a compiled 1344x760 run_model entry"):
      unified_model_factory(include_target=False)

  @parameterized.expand([
    (True, 'tici', True, (1928, 1208)),
    (True, 'mici', True, (1344, 760)),
    (False, 'pc', True, (1928, 1208)),
    (True, 'tizi', False, (1928, 1208)),
    (True, 'tizi', True, (1344, 760)),
  ], names=['comma_hardware', 'device_type', 'chestnut', 'cam_size'])
  def test_ineligible_models_keep_native_inputs(self, comma_hardware, device_type, chestnut, cam_size, unified_model_factory):
    state = unified_model_factory(comma_hardware=comma_hardware, device_type=device_type, chestnut=chestnut, cam_size=cam_size,
                                  include_target=False)
    self.assertIsNone(state.frame_resize)
    self.assertIs(state.run_model, _native_unified_jit)
    layout = modeld_module.get_nv12_info(*cam_size)
    self.assertEqual(state.frame_copy_size, modeld_module.nv12_copy_size(*layout[:3]))
    source = (np.arange(state.frame_copy_size, dtype=np.uint32) % 251).astype(np.uint8)
    frames = dict.fromkeys(state.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transform = np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32)
    state.run(frames, dict.fromkeys(state.vision_input_names, transform), {state.desire_key: np.zeros(8, dtype=np.float32)})
    for key in state.vision_input_names:
      np.testing.assert_array_equal(state.frame_buffers[key], source)
    for key in ('tfm', 'big_tfm'):
      np.testing.assert_array_equal(state.numpy_inputs[key], transform)

  @parameterized.expand(['AMD', 'QCOM'], names=['warp_dev'])
  def test_separate_warp_is_not_resized(self, warp_dev, tmp_path, monkeypatch, patch_modeld):
    from openpilot.common.hardware import hw
    from openpilot.selfdrive.modeld.helpers import dump_oob

    arch = ARCHETYPES['supercombo_non20hz']
    data = tests_helpers.make_pkl_data(arch)
    data['metadata'] = {**data['metadata'], 'warp_dev': warp_dev}
    with open(tmp_path / 'driving_test_tinygrad.pkl', 'wb') as f:
      dump_oob(data, f)
    patch_modeld(tests_helpers.make_bundle(arch))
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    monkeypatch.setattr(modeld_module, 'COMMA_HARDWARE', True)
    monkeypatch.setattr(modeld_module.HARDWARE, 'get_device_type', lambda: 'tizi')
    make_queues = modeld_module.make_supercombo_input_queues
    monkeypatch.setattr(modeld_module, 'make_supercombo_input_queues',
                       lambda input_shapes, frame_skip, device: make_queues(input_shapes, frame_skip, device='CPU'))
    monkeypatch.setattr(modeld_module, 'Tensor', lambda data, device: Tensor(data, device='CPU'))

    state = ModelState(cam_w=CAM_W, cam_h=CAM_H, chestnut=True)
    self.assertFalse(state.is_run_model)
    self.assertEqual(state.DEV, 'AMD')
    self.assertIsNone(state.frame_resize)
    self.assertEqual(state.frame_copy_size, 3735552)
    for frame in state.full_frames.values():
      self.assertEqual(frame.shape, (4804608,))

  def test_shared_vision_buffer_is_packed_before_enqueue(self, unified_model_factory):
    state = unified_model_factory()
    source = np.full(4804608, 255, dtype=np.uint8)
    source[:state.source_frame_copy_size] = 17
    frames = dict.fromkeys(state.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transforms = dict.fromkeys(state.vision_input_names, np.eye(3, dtype=np.float32))
    captured = []

    def capture(**kwargs):
      captured.append(kwargs['packed_npy_inputs'].numpy().copy())
      return _unified_jit(**kwargs)

    state.run_model = capture
    state.run(frames, transforms, {state.desire_key: np.zeros(8, dtype=np.float32)})
    self.assertEqual(captured[0].shape, (3309688,))
    self.assertTrue(np.all(captured[0][-2 * state.frame_copy_size:] == 17))
    self.assertFalse(np.shares_memory(state.frame_buffers['img'], state.frame_buffers['big_img']))
    np.testing.assert_array_equal(state.frame_buffers['img'], state.frame_buffers['big_img'])
    self.assertTrue(np.all(source[:state.source_frame_copy_size] == 17))
    self.assertTrue(np.all(source[state.source_frame_copy_size:] == 255))

  def test_short_source_error_prevents_enqueue(self, unified_model_factory):
    state = unified_model_factory()
    state.run_model = Mock(wraps=state.run_model)
    frames = dict.fromkeys(state.vision_input_names, SimpleNamespace(data=np.zeros(state.source_frame_copy_size - 1, dtype=np.uint8)))
    transforms = dict.fromkeys(state.vision_input_names, np.eye(3, dtype=np.float32))
    with self.assertRaises(ValueError):
      state.run(frames, transforms, {state.desire_key: np.zeros(8, dtype=np.float32)})
    state.run_model.assert_not_called()

  def test_small_model_inputs_are_isolated_after_big_model_failure(self, unified_model_factory):
    big = unified_model_factory()
    small = unified_model_factory(chestnut=False)
    source = (np.arange(big.source_frame_copy_size, dtype=np.uint32) % 251).astype(np.uint8)
    frames = dict.fromkeys(big.vision_input_names, SimpleNamespace(data=memoryview(source)))
    transform = np.array([[1, 2, 3], [4, 5, 6], [.01, .02, 1]], dtype=np.float32)
    original = transform.copy()
    transforms = dict.fromkeys(big.vision_input_names, transform)
    big.run_model = Mock(side_effect=RuntimeError("AMD failed"))
    with self.assertRaisesRegex(RuntimeError, "AMD failed"):
      big.run(frames, transforms, {big.desire_key: np.zeros(8, dtype=np.float32)})

    self.assertEqual(small.run(frames, transforms, {small.desire_key: np.zeros(8, dtype=np.float32)}), {})
    self.assertIsNone(small.frame_resize)
    self.assertEqual(small.frame_copy_size, 3735552)
    np.testing.assert_array_equal(transform, original)
    for key in small.vision_input_names:
      np.testing.assert_array_equal(small.frame_buffers[key], source)
    for key in ('tfm', 'big_tfm'):
      np.testing.assert_array_equal(small.numpy_inputs[key], original)
