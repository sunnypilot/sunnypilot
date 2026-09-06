"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
from openpilot.common.parameterized import parameterized

from openpilot.common.file_chunker import chunk_file, get_chunk_targets
from openpilot.sunnypilot.modeld_v2.compile_modeld import derive_frame_skip, _detect_desire_key, read_file_chunked_to_disk
from openpilot.common.test import OpenpilotTestCase


class TestDeriveFrameSkip(OpenpilotTestCase):
  def test_non20hz_supercombo(self):
    vision = {}
    policy = {'features_buffer': (1, 99, 512), 'desire': (1, 100, 8)}
    assert derive_frame_skip(vision, policy) == 1

  def test_20hz_supercombo(self):
    vision = {}
    policy = {'features_buffer': (1, 24, 512), 'desire': (1, 25, 8)}
    assert derive_frame_skip(vision, policy) == 4

  def test_split_vision_policy(self):
    vision = {'img': (1, 12, 128, 256)}
    policy = {'features_buffer': (1, 25, 512), 'desire_pulse': (1, 25, 8)}
    assert derive_frame_skip(vision, policy) == 4

  def test_no_features_buffer(self):
    assert derive_frame_skip({}, {}) == 1


class TestFrameSkipBufferLengthEquivalence(OpenpilotTestCase):
  @parameterized.expand([
    (1, 2),
    (4, 5),
  ], names=["frame_skip", "expected_buffer_length"])
  def test_img_buffer_size_matches_warp_buffer_length(self, frame_skip, expected_buffer_length):
    n_frames = 2
    img_buf_dim0 = frame_skip * (n_frames - 1) + 1
    assert img_buf_dim0 == expected_buffer_length, \
      f"frame_skip={frame_skip}: img_buf[0]={img_buf_dim0}, expected {expected_buffer_length}"

  @parameterized.expand([
    (False, 1, 2),
    (True, 4, 5),
  ], names=["is_20hz", "expected_frame_skip", "expected_buffer_length"])
  def test_is_20hz_to_frame_skip_to_buffer_length(self, is_20hz, expected_frame_skip, expected_buffer_length):
    if is_20hz:
      policy_shapes = {'features_buffer': (1, 24, 512)}
    else:
      policy_shapes = {'features_buffer': (1, 99, 512)}
    frame_skip = derive_frame_skip({}, policy_shapes)
    assert frame_skip == expected_frame_skip

    n_frames = 2
    img_buf_dim0 = frame_skip * (n_frames - 1) + 1
    assert img_buf_dim0 == expected_buffer_length


class TestTemporalSamplingEquivalence(OpenpilotTestCase):
  def test_non20hz_desire_sampling_identity(self):
    buf = np.random.default_rng(0).standard_normal((100, 1, 8)).astype(np.float32)
    frame_skip = 1
    sampled = buf[::frame_skip].reshape(-1, 8)
    assert sampled.shape == (100, 8)
    np.testing.assert_array_equal(sampled, buf[:, 0, :])

  def test_20hz_desire_sampling_max(self):
    buf = np.zeros((100, 1, 8), dtype=np.float32)
    buf[99, 0, 3] = 1.0
    frame_skip = 4
    reshaped = buf.reshape(-1, frame_skip, 1, 8).max(axis=1)
    sampled = reshaped.reshape(-1, 8)
    assert sampled.shape == (25, 8)
    assert sampled[24, 3] == 1.0
    assert sampled[23, 3] == 0.0

  def test_split_features_buffer_sampling_skip(self):
    buf = np.arange(100 * 512, dtype=np.float32).reshape(100, 1, 512)
    frame_skip = 4
    sampled = buf[::frame_skip].reshape(-1, 512)
    assert sampled.shape == (25, 512)
    np.testing.assert_array_equal(sampled[0], buf[0, 0])
    np.testing.assert_array_equal(sampled[1], buf[4, 0])
    np.testing.assert_array_equal(sampled[24], buf[96, 0])

  def test_non20hz_features_buffer_sampling_identity(self):
    buf = np.arange(99 * 512, dtype=np.float32).reshape(99, 1, 512)
    frame_skip = 1
    sampled = buf[::frame_skip].reshape(-1, 512)
    assert sampled.shape == (99, 512)
    np.testing.assert_array_equal(sampled, buf[:, 0, :])


class TestTemporalIdxEquivalence(OpenpilotTestCase):
  @parameterized.expand([
    ('non20hz', (1, 100, 8), (1, 99, 512), 1),
    ('20hz', (1, 25, 8), (1, 24, 512), 4),
    ('split', (1, 25, 8), (1, 25, 512), 4),
  ], names=["mode", "desire_shape", "fb_shape", "frame_skip"])
  def test_features_buffer_idx_equivalence(self, mode, desire_shape, fb_shape, frame_skip):
    history = fb_shape[1]

    if mode == 'non20hz':
      modelstate_idxs = np.arange(history)
      buf_len = history
    elif mode == '20hz':
      buf_len = (history + 1) * 4
      step = int(-buf_len / history)
      modelstate_idxs = np.arange(step, step * (history + 1), step)[::-1]
    elif mode == 'split':
      buf_len = history * 4
      skip = buf_len // history
      modelstate_idxs = np.arange(buf_len)[-1 - (skip * (history - 1))::skip]

    assert len(modelstate_idxs) == fb_shape[1], \
      f"{mode}: ModelState idx count {len(modelstate_idxs)} != input shape {fb_shape[1]}"

  @parameterized.expand([
    ('non20hz', (1, 100, 8), (1, 99, 512), 1),
    ('20hz', (1, 25, 8), (1, 24, 512), 4),
    ('split', (1, 25, 8), (1, 25, 512), 4),
  ], names=["mode", "desire_shape", "fb_shape", "frame_skip"])
  def test_desire_idx_equivalence(self, mode, desire_shape, fb_shape, frame_skip):
    history = desire_shape[1]

    compile_desire_buf_len = frame_skip * history if mode != 'non20hz' else history
    compile_sampled_count = compile_desire_buf_len // frame_skip if frame_skip > 1 else compile_desire_buf_len
    assert compile_sampled_count == history, \
      f"{mode}: compile desire samples {compile_sampled_count} != model input {history}"


class TestDetectDesireKey(OpenpilotTestCase):
  def test_finds_desire(self):
    shapes = {'features_buffer': (1, 99, 512), 'desire': (1, 100, 8), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) == 'desire'

  def test_finds_desire_pulse(self):
    shapes = {'features_buffer': (1, 25, 512), 'desire_pulse': (1, 25, 8), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) == 'desire_pulse'

  def test_returns_none_when_no_desire(self):
    shapes = {'features_buffer': (1, 99, 512), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) is None


class TestOutputSlicePreservation(OpenpilotTestCase):
  def test_vision_hidden_state_slice_used_for_features(self):
    mock_slices = {'hidden_state': slice(0, 512), 'plan': slice(512, 1024)}
    features_slice = mock_slices['hidden_state']
    fake_output = np.random.default_rng(0).standard_normal((1, 1024)).astype(np.float32)
    features = fake_output[:, features_slice]
    assert features.shape == (1, 512)

  def test_policy_output_slices_independent(self):
    vision_slices = {'hidden_state': slice(0, 512)}
    policy_slices = {'plan': slice(0, 495), 'meta': slice(495, 550)}
    assert set(vision_slices.keys()) & set(policy_slices.keys()) == set(), \
      "vision and policy slices should not overlap in keys"


class TestReadFileChunkedToDisk(OpenpilotTestCase):
  def test_none_passthrough(self):
    assert read_file_chunked_to_disk(None) is None

  def test_unchunked_source_staged_on_disk(self):
    with tempfile.TemporaryDirectory() as d:
      src = Path(d) / "driving_supercombo.onnx"
      payload = os.urandom(1024)
      src.write_bytes(payload)

      out = Path(read_file_chunked_to_disk(str(src)))

      assert out.parent == Path(d)
      assert out.name == "driving_supercombo.onnx.unchunked"
      assert out.read_bytes() == payload

  def test_chunked_source_reassembled_on_disk(self):
    with tempfile.TemporaryDirectory() as d:
      src = Path(d) / "driving_supercombo.onnx"
      payload = os.urandom(4096)
      src.write_bytes(payload)
      chunk_file(str(src), get_chunk_targets(str(src), len(payload)))
      assert not src.exists()

      out = Path(read_file_chunked_to_disk(str(src)))

      assert out.parent == Path(d)
      assert out.read_bytes() == payload


class Test4DFeaturesBuffer(OpenpilotTestCase):
  def test_get_policy_npy_shapes_4d(self):
    from openpilot.sunnypilot.modeld_v2.compile_modeld import get_policy_npy_shapes
    input_shapes = {
      'desire_pulse': (1, 25, 8),
      'features_buffer': (1, 24, 32, 512),  # compare 4d to 3d for regression
      'traffic_convention': (1, 2),
      'action_t': (1, 2)
    }
    shapes, sizes = get_policy_npy_shapes(input_shapes, is_supercombo=True)
    assert shapes['prev_feat'] == (1, 16384)
    assert sizes == [8, 2, 2, 16384]

  def test_get_policy_npy_shapes_3d(self):
    from openpilot.sunnypilot.modeld_v2.compile_modeld import get_policy_npy_shapes
    input_shapes = {
      'desire_pulse': (1, 25, 8),
      'features_buffer': (1, 24, 512),
      'traffic_convention': (1, 2),
      'action_t': (1, 2)
    }
    shapes, sizes = get_policy_npy_shapes(input_shapes, is_supercombo=True)
    assert shapes['prev_feat'] == (1, 512)
    assert sizes == [8, 2, 2, 512]


class TestStockCompileModeldEquivalence(OpenpilotTestCase):
  def test_get_policy_npy_shapes_matches_stock(self):
    from openpilot.selfdrive.modeld.compile_modeld import get_policy_npy_shapes as stock_get_policy_npy_shapes
    from openpilot.sunnypilot.modeld_v2.compile_modeld import get_policy_npy_shapes as sunny_get_policy_npy_shapes

    stock_input_shapes = {
      'desire_pulse': (1, 25, 8),
      'features_buffer': (1, 24, 512), # see below comment
      'traffic_convention': (1, 2),
      'action_t': (1, 2),
    }

    stock_shapes, stock_sizes = stock_get_policy_npy_shapes(stock_input_shapes)
    sunny_shapes, sunny_sizes = sunny_get_policy_npy_shapes(stock_input_shapes, is_supercombo=True)

    assert sunny_shapes == stock_shapes
    assert sunny_sizes == stock_sizes
    assert sunny_shapes['prev_feat'] == (1, 512)

  def test_make_input_queues_full_stock_equivalence(self):
    from openpilot.selfdrive.modeld.compile_modeld import make_input_queues as stock_make_input_queues
    from openpilot.sunnypilot.modeld_v2.compile_modeld import make_supercombo_input_queues as sunny_make_supercombo_input_queues
    input_shapes = {
      'img': (1, 12, 128, 256),
      'desire_pulse': (1, 25, 8),
      'features_buffer': (1, 24, 32, 512),
      'traffic_convention': (1, 2),
      'action_t': (1, 2),
    }
    frame_skip = 4

    stock_queues, stock_npy, _frame_views = stock_make_input_queues(input_shapes, frame_skip, device='NPY', frame_copy_size=49152)
    sunny_queues, sunny_npy = sunny_make_supercombo_input_queues(input_shapes, frame_skip, device='NPY')
    # sunnypilot split pipeline has tfm/big_tfm as queues; packed_npy_inputs size differs (different frame packing)
    assert set(stock_queues.keys()) <= set(sunny_queues.keys())
    for key in stock_queues:
      if key == 'packed_npy_inputs':
        continue
      assert sunny_queues[key].shape == stock_queues[key].shape, \
        f"Queue shape mismatch for {key}: sunny {sunny_queues[key].shape} != stock {stock_queues[key].shape}"
    assert set(stock_npy.keys()) <= set(sunny_npy.keys())
    for key in stock_npy:
      assert sunny_npy[key].shape == stock_npy[key].shape, \
        f"Numpy array shape mismatch for {key}: sunny {sunny_npy[key].shape} != stock {stock_npy[key].shape}"

  @unittest.skip("upstream removed make_warp_input_queues — warp merged into run_model")
  def test_make_warp_queues_stock_equivalence(self):
    from openpilot.selfdrive.modeld.compile_modeld import make_warp_input_queues as stock_make_warp_queues
    from openpilot.sunnypilot.modeld_v2.compile_modeld import make_warp_queues as sunny_make_warp_queues
    stock_vision_shapes = {'img': (1, 12, 128, 256)}  # for now?
    stock_queues, stock_npy = stock_make_warp_queues(stock_vision_shapes, frame_skip=4, device='NPY')
    sunny_queues, sunny_npy = sunny_make_warp_queues(device='NPY')

    assert set(sunny_npy.keys()) == set(stock_npy.keys()) == {'tfm', 'big_tfm'}
    for key in sunny_npy:
      assert sunny_npy[key].shape == stock_npy[key].shape == (3, 3)


