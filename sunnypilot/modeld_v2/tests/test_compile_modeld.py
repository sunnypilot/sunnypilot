"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2.compile_modeld import derive_frame_skip, _detect_desire_key


class TestDeriveFrameSkip:
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


class TestFrameSkipBufferLengthEquivalence:
  @pytest.mark.parametrize("frame_skip,expected_buffer_length", [
    (1, 2),
    (4, 5),
  ])
  def test_img_buffer_size_matches_warp_buffer_length(self, frame_skip, expected_buffer_length):
    n_frames = 2
    img_buf_dim0 = frame_skip * (n_frames - 1) + 1
    assert img_buf_dim0 == expected_buffer_length, \
      f"frame_skip={frame_skip}: img_buf[0]={img_buf_dim0}, expected {expected_buffer_length}"

  @pytest.mark.parametrize("is_20hz,expected_frame_skip,expected_buffer_length", [
    (False, 1, 2),
    (True, 4, 5),
  ])
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


class TestTemporalSamplingEquivalence:
  def test_non20hz_desire_sampling_identity(self):
    buf = np.random.randn(100, 1, 8).astype(np.float32)
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


class TestTemporalIdxEquivalence:
  @pytest.mark.parametrize("mode,desire_shape,fb_shape,frame_skip", [
    ('non20hz', (1, 100, 8), (1, 99, 512), 1),
    ('20hz', (1, 25, 8), (1, 24, 512), 4),
    ('split', (1, 25, 8), (1, 25, 512), 4),
  ])
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

  @pytest.mark.parametrize("mode,desire_shape,fb_shape,frame_skip", [
    ('non20hz', (1, 100, 8), (1, 99, 512), 1),
    ('20hz', (1, 25, 8), (1, 24, 512), 4),
    ('split', (1, 25, 8), (1, 25, 512), 4),
  ])
  def test_desire_idx_equivalence(self, mode, desire_shape, fb_shape, frame_skip):
    history = desire_shape[1]

    compile_desire_buf_len = frame_skip * history if mode != 'non20hz' else history
    compile_sampled_count = compile_desire_buf_len // frame_skip if frame_skip > 1 else compile_desire_buf_len
    assert compile_sampled_count == history, \
      f"{mode}: compile desire samples {compile_sampled_count} != model input {history}"


class TestDetectDesireKey:
  def test_finds_desire(self):
    shapes = {'features_buffer': (1, 99, 512), 'desire': (1, 100, 8), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) == 'desire'

  def test_finds_desire_pulse(self):
    shapes = {'features_buffer': (1, 25, 512), 'desire_pulse': (1, 25, 8), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) == 'desire_pulse'

  def test_returns_none_when_no_desire(self):
    shapes = {'features_buffer': (1, 99, 512), 'traffic_convention': (1, 2)}
    assert _detect_desire_key(shapes) is None


class TestOutputSlicePreservation:
  def test_vision_hidden_state_slice_used_for_features(self):
    mock_slices = {'hidden_state': slice(0, 512), 'plan': slice(512, 1024)}
    features_slice = mock_slices['hidden_state']
    fake_output = np.random.randn(1, 1024).astype(np.float32)
    features = fake_output[:, features_slice]
    assert features.shape == (1, 512)

  def test_policy_output_slices_independent(self):
    vision_slices = {'hidden_state': slice(0, 512)}
    policy_slices = {'plan': slice(0, 495), 'meta': slice(495, 550)}
    assert set(vision_slices.keys()) & set(policy_slices.keys()) == set(), \
      "vision and policy slices should not overlap in keys"
