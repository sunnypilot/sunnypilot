#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import os
import pickle
import time
from functools import partial
from collections import defaultdict

import numpy as np
from tinygrad.tensor import Tensor
from tinygrad.device import Device
from tinygrad.engine.jit import TinyJit

from openpilot.selfdrive.modeld.compile_modeld import (
  NV12Frame, make_frame_prepare,
  shift_and_sample, sample_skip, sample_desire,
)

MODEL_TYPES = ('vision_policy', 'supercombo', 'vision_multi_policy')


def _detect_desire_key(policy_input_shapes):
  for k in policy_input_shapes:
    if k.startswith('desire'):
      return k
  return None


def _detect_vision_keys(vision_input_shapes):
  img_keys = sorted([k for k in vision_input_shapes if 'img' in k])
  road_key = next((k for k in img_keys if 'big' not in k), None)
  wide_key = next((k for k in img_keys if 'big' in k), None)
  if road_key is None or wide_key is None:
    raise ValueError(f"Cannot determine road/wide image keys from {list(vision_input_shapes.keys())}")
  return road_key, wide_key


def make_split_input_queues(vision_input_shapes, policy_input_shapes, frame_skip, device):
  road_key, _ = _detect_vision_keys(vision_input_shapes)
  img = vision_input_shapes[road_key]
  n_frames = img[1] // 6
  img_buf_shape = (frame_skip * (n_frames - 1) + 1, 6, img[2], img[3])

  fb = policy_input_shapes['features_buffer']
  desire_key = _detect_desire_key(policy_input_shapes)
  dp = policy_input_shapes[desire_key]
  tc = policy_input_shapes.get('traffic_convention', (1, 2))

  npy = {
    'desire': np.zeros(dp[2], dtype=np.float32),
    'traffic_convention': np.zeros(tc, dtype=np.float32),
    'tfm': np.zeros((3, 3), dtype=np.float32),
    'big_tfm': np.zeros((3, 3), dtype=np.float32),
  }

  handled = {'features_buffer', desire_key, 'traffic_convention'}
  for key, shape in policy_input_shapes.items():
    if key in handled:
      continue
    npy[key] = np.zeros(shape, dtype=np.float32)

  input_queues = {
    'img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'big_img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'feat_q': Tensor(np.zeros((frame_skip * (fb[1] - 1) + 1, fb[0], fb[2]), dtype=np.float32), device=device).contiguous().realize(),
    'desire_q': Tensor(np.zeros((frame_skip * dp[1], dp[0], dp[2]), dtype=np.float32), device=device).contiguous().realize(),
    **{k: Tensor(v, device='NPY').realize() for k, v in npy.items()},
  }
  return input_queues, npy


def make_run_split_policy(vision_runner, policy_runner, nv12: NV12Frame, model_w, model_h,
                          vision_features_slice, frame_skip, desire_key, extra_policy_keys,
                          vision_road_key, vision_wide_key, prepare_only=False):
  frame_prepare = make_frame_prepare(nv12, model_w, model_h)
  sample_skip_fn = partial(sample_skip, frame_skip=frame_skip)
  sample_desire_fn = partial(sample_desire, frame_skip=frame_skip)

  def run_policy(img_q, big_img_q, feat_q, desire_q, desire, traffic_convention, tfm, big_tfm, frame, big_frame, **extra):
    npy_tensors = [tfm.to(Device.DEFAULT), big_tfm.to(Device.DEFAULT),
                   desire.to(Device.DEFAULT), traffic_convention.to(Device.DEFAULT)]
    extra_device = {k: extra[k].to(Device.DEFAULT) for k in extra_policy_keys}
    Tensor.realize(*npy_tensors, *extra_device.values())
    tfm, big_tfm, desire, traffic_convention = npy_tensors

    img = shift_and_sample(img_q, frame_prepare(frame, tfm).unsqueeze(0), sample_skip_fn)
    big_img = shift_and_sample(big_img_q, frame_prepare(big_frame, big_tfm).unsqueeze(0), sample_skip_fn)

    if prepare_only:
      return img, big_img

    vision_out = next(iter(vision_runner({vision_road_key: img, vision_wide_key: big_img}).values())).cast('float32')

    new_feat = vision_out[:, vision_features_slice].reshape(1, -1).unsqueeze(0)
    feat_buf = shift_and_sample(feat_q, new_feat, sample_skip_fn)
    desire_buf = shift_and_sample(desire_q, desire.reshape(1, 1, -1), sample_desire_fn)

    inputs = {'features_buffer': feat_buf, desire_key: desire_buf, 'traffic_convention': traffic_convention, **extra_device}
    policy_out = next(iter(policy_runner(inputs).values())).cast('float32')

    return vision_out, policy_out
  return run_policy


def compile_split_policy(nv12: NV12Frame, model_w, model_h, prepare_only, frame_skip,
                         vision_runner, policy_runner, vision_metadata, policy_metadata):
  print(f"Compiling combined policy JIT for {nv12.width}x{nv12.height} (prepare_only={prepare_only})...")

  vision_features_slice = vision_metadata['output_slices']['hidden_state']
  vision_input_shapes = vision_metadata['input_shapes']
  policy_input_shapes = policy_metadata['input_shapes']
  desire_key = _detect_desire_key(policy_input_shapes)
  extra_policy_keys = [k for k in policy_input_shapes if k not in ('features_buffer', desire_key, 'traffic_convention')]
  vision_road_key, vision_wide_key = _detect_vision_keys(vision_input_shapes)

  _run = make_run_split_policy(vision_runner, policy_runner, nv12, model_w, model_h,
                               vision_features_slice, frame_skip, desire_key, extra_policy_keys,
                               vision_road_key, vision_wide_key, prepare_only)
  run_policy_jit = TinyJit(_run, prune=True)

  SEED = 42

  def random_inputs_run_fn(fn, seed, test_val=None, test_buffers=None, expect_match=True):
    input_queues, npy = make_split_input_queues(vision_input_shapes, policy_input_shapes, frame_skip, Device.DEFAULT)
    np.random.seed(seed)
    Tensor.manual_seed(seed)

    testing = test_val is not None or test_buffers is not None
    n_runs = 1 if testing else 3

    for i in range(n_runs):
      frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8').realize()
      big_frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8').realize()
      for v in npy.values():
        v[:] = np.random.randn(*v.shape).astype(v.dtype)
      Device.default.synchronize()
      st = time.perf_counter()
      outs = fn(**input_queues, frame=frame, big_frame=big_frame)
      mt = time.perf_counter()
      Device.default.synchronize()
      et = time.perf_counter()
      print(f"  [{i+1}/{n_runs}] enqueue {(mt-st)*1e3:6.2f} ms -- total {(et-st)*1e3:6.2f} ms")

      if i == 0:
        val = [np.copy(v.numpy()) for v in outs]
        buffers = [np.copy(v.numpy().copy()) for v in input_queues.values()]

    if test_val is not None:
      match = all(np.array_equal(a, b) for a, b in zip(val, test_val, strict=True))
      assert match == expect_match, f"outputs {'differ from' if expect_match else 'match'} baseline (seed={seed})"
    if test_buffers is not None:
      match = all(np.array_equal(a, b) for a, b in zip(buffers, test_buffers, strict=True))
      assert match == expect_match, f"buffers {'differ from' if expect_match else 'match'} baseline (seed={seed})"
    return fn, val, buffers

  print('capture + replay')
  run_policy_jit, test_val, test_buffers = random_inputs_run_fn(run_policy_jit, SEED)

  print('pickle round trip')
  run_policy_jit = pickle.loads(pickle.dumps(run_policy_jit))
  random_inputs_run_fn(run_policy_jit, SEED, test_val, test_buffers, expect_match=True)
  random_inputs_run_fn(run_policy_jit, SEED+1, test_val, test_buffers, expect_match=False)
  return run_policy_jit


def derive_frame_skip(vision_input_shapes, policy_input_shapes):
  fb = policy_input_shapes.get('features_buffer')
  if fb is None:
    return 1
  fb_history = fb[1]
  if fb_history >= 99:
    return 1
  return 4


def make_supercombo_input_queues(input_shapes, frame_skip, device):
  img_shape = input_shapes.get('img', input_shapes.get('input_imgs'))
  if img_shape is None:
    raise ValueError("No img input found in model shapes")

  n_frames = img_shape[1] // 6
  img_buf_shape = (frame_skip * (n_frames - 1) + 1, 6, img_shape[2], img_shape[3])

  numpy_keys = {}
  queue_keys = {}

  for key, shape in input_shapes.items():
    if 'img' in key:
      continue
    if len(shape) == 3 and shape[1] > 1:
      if key.startswith('desire'):
        numpy_keys[key] = np.zeros(shape[2], dtype=np.float32)
        queue_keys[f'{key}_q'] = Tensor(
          np.zeros((frame_skip * shape[1], shape[0], shape[2]), dtype=np.float32),
          device=device).contiguous().realize()
      elif key == 'features_buffer':
        queue_keys['feat_q'] = Tensor(
          np.zeros((frame_skip * (shape[1] - 1) + 1, shape[0], shape[2]), dtype=np.float32),
          device=device).contiguous().realize()
      else:
        numpy_keys[key] = np.zeros(shape, dtype=np.float32)
    elif len(shape) == 2:
      numpy_keys[key] = np.zeros(shape, dtype=np.float32)

  if 'traffic_convention' not in numpy_keys:
    tc_shape = input_shapes.get('traffic_convention', (1, 2))
    numpy_keys['traffic_convention'] = np.zeros(tc_shape, dtype=np.float32)

  numpy_keys['tfm'] = np.zeros((3, 3), dtype=np.float32)
  numpy_keys['big_tfm'] = np.zeros((3, 3), dtype=np.float32)

  input_queues = {
    'img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'big_img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    **queue_keys,
    **{k: Tensor(v, device='NPY').realize() for k, v in numpy_keys.items()},
  }
  return input_queues, numpy_keys


def make_run_supercombo(model_runner, nv12: NV12Frame, model_w, model_h,
                        features_slice, frame_skip, input_shapes, prepare_only=False):
  frame_prepare = make_frame_prepare(nv12, model_w, model_h)
  sample_skip_fn = partial(sample_skip, frame_skip=frame_skip)
  sample_desire_fn = partial(sample_desire, frame_skip=frame_skip)

  desire_key = _detect_desire_key(input_shapes)
  if desire_key is None:
    raise ValueError(f"No desire* key found in input_shapes: {list(input_shapes.keys())}")
  road_img_key, wide_img_key = _detect_vision_keys(input_shapes)
  extra_policy_keys = [k for k in input_shapes
                       if k not in (desire_key, 'features_buffer', 'traffic_convention')
                       and 'img' not in k]

  def run_supercombo(img_q, big_img_q, feat_q, desire_q,
                     frame, big_frame, **kwargs):
    desire = kwargs.get(desire_key)
    traffic_convention = kwargs.get('traffic_convention')
    tfm = kwargs['tfm']
    big_tfm = kwargs['big_tfm']

    tfm = tfm.to(Device.DEFAULT)
    big_tfm = big_tfm.to(Device.DEFAULT)
    desire = desire.to(Device.DEFAULT)
    traffic_convention = traffic_convention.to(Device.DEFAULT)
    Tensor.realize(tfm, big_tfm, desire, traffic_convention)

    img = shift_and_sample(img_q, frame_prepare(frame, tfm).unsqueeze(0), sample_skip_fn)
    big_img = shift_and_sample(big_img_q, frame_prepare(big_frame, big_tfm).unsqueeze(0), sample_skip_fn)

    if prepare_only:
      return img, big_img

    desire_buf = shift_and_sample(desire_q, desire.reshape(1, 1, -1), sample_desire_fn)
    feat_buf = sample_skip_fn(feat_q)

    inputs = {road_img_key: img, wide_img_key: big_img,
              desire_key: desire_buf, 'features_buffer': feat_buf,
              'traffic_convention': traffic_convention}
    for k in extra_policy_keys:
      if k in kwargs:
        inputs[k] = kwargs[k].to(Device.DEFAULT)

    model_out = next(iter(model_runner(inputs).values())).cast('float32')

    new_feat = model_out[:, features_slice].reshape(1, -1).unsqueeze(0)
    shift_and_sample(feat_q, new_feat, sample_skip_fn)

    return model_out

  return run_supercombo


def make_run_vision_multi_policy(vision_runner, policy_runners, nv12: NV12Frame, model_w, model_h,
                                 vision_features_slice, frame_skip, desire_key, extra_policy_keys,
                                 vision_road_key, vision_wide_key, prepare_only=False):
  frame_prepare = make_frame_prepare(nv12, model_w, model_h)
  sample_skip_fn = partial(sample_skip, frame_skip=frame_skip)
  sample_desire_fn = partial(sample_desire, frame_skip=frame_skip)

  def run_multi_policy(img_q, big_img_q, feat_q, desire_q, desire,
                       traffic_convention, tfm, big_tfm, frame, big_frame, **extra):
    npy_tensors = [tfm.to(Device.DEFAULT), big_tfm.to(Device.DEFAULT),
                   desire.to(Device.DEFAULT), traffic_convention.to(Device.DEFAULT)]
    extra_device = {k: extra[k].to(Device.DEFAULT) for k in extra_policy_keys}
    Tensor.realize(*npy_tensors, *extra_device.values())
    tfm, big_tfm, desire, traffic_convention = npy_tensors

    img = shift_and_sample(img_q, frame_prepare(frame, tfm).unsqueeze(0), sample_skip_fn)
    big_img = shift_and_sample(big_img_q, frame_prepare(big_frame, big_tfm).unsqueeze(0), sample_skip_fn)

    if prepare_only:
      return img, big_img

    vision_out = next(iter(vision_runner({vision_road_key: img, vision_wide_key: big_img}).values())).cast('float32')

    new_feat = vision_out[:, vision_features_slice].reshape(1, -1).unsqueeze(0)
    feat_buf = shift_and_sample(feat_q, new_feat, sample_skip_fn)
    desire_buf = shift_and_sample(desire_q, desire.reshape(1, 1, -1), sample_desire_fn)

    inputs = {'features_buffer': feat_buf, desire_key: desire_buf, 'traffic_convention': traffic_convention, **extra_device}

    policy_outputs = []
    for runner in policy_runners:
      policy_out = next(iter(runner(inputs).values())).cast('float32')
      policy_outputs.append(policy_out)

    return (vision_out, *policy_outputs)

  return run_multi_policy


def _warmup_and_serialize(run_jit, input_queues, npy, nv12):
  for i in range(3):
    np.random.seed(42 + i)
    frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8').realize()
    big_frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8').realize()
    for v in npy.values():
      v[:] = np.random.randn(*v.shape).astype(v.dtype)
    Device.default.synchronize()
    st = time.perf_counter()
    run_jit(**input_queues, frame=frame, big_frame=big_frame)
    mt = time.perf_counter()
    Device.default.synchronize()
    et = time.perf_counter()
    print(f"  [{i + 1}/3] enqueue {(mt - st) * 1e3:6.2f} ms -- total {(et - st) * 1e3:6.2f} ms")
  return pickle.loads(pickle.dumps(run_jit))


def compile_supercombo(nv12: NV12Frame, model_w, model_h, prepare_only, frame_skip,
                       model_runner, metadata):
  print(f"Compiling combined supercombo JIT for {nv12.width}x{nv12.height} (prepare_only={prepare_only})...")

  features_slice = metadata['output_slices']['hidden_state']
  input_shapes = metadata['input_shapes']

  _run = make_run_supercombo(model_runner, nv12, model_w, model_h,
                             features_slice, frame_skip, input_shapes, prepare_only)
  run_jit = TinyJit(_run, prune=True)

  input_queues, npy = make_supercombo_input_queues(input_shapes, frame_skip, Device.DEFAULT)

  run_jit = _warmup_and_serialize(run_jit, input_queues, npy, nv12)
  return run_jit


def compile_multi_policy(nv12: NV12Frame, model_w, model_h, prepare_only, frame_skip,
                         vision_runner, policy_runners, vision_metadata, policy_metadata):
  print(f"Compiling combined multi-policy JIT for {nv12.width}x{nv12.height} (prepare_only={prepare_only})...")

  vision_features_slice = vision_metadata['output_slices']['hidden_state']
  vision_input_shapes = vision_metadata['input_shapes']
  policy_input_shapes = policy_metadata['input_shapes']
  desire_key = _detect_desire_key(policy_input_shapes)
  extra_policy_keys = [k for k in policy_input_shapes if k not in ('features_buffer', desire_key, 'traffic_convention')]
  vision_road_key, vision_wide_key = _detect_vision_keys(vision_input_shapes)

  _run = make_run_vision_multi_policy(vision_runner, policy_runners, nv12, model_w, model_h,
                                      vision_features_slice, frame_skip, desire_key, extra_policy_keys,
                                      vision_road_key, vision_wide_key, prepare_only)
  run_jit = TinyJit(_run, prune=True)

  input_queues, npy = make_split_input_queues(vision_input_shapes, policy_input_shapes, frame_skip, Device.DEFAULT)

  run_jit = _warmup_and_serialize(run_jit, input_queues, npy, nv12)
  return run_jit


def _parse_size(s):
  w, h = s.lower().split('x')
  return int(w), int(h)


if __name__ == "__main__":
  from tinygrad.nn.onnx import OnnxRunner
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  from openpilot.selfdrive.modeld.get_model_metadata import make_metadata_dict

  p = argparse.ArgumentParser(description="Compile combined JIT pkl for sunnypilot modeld_v2")
  p.add_argument('--model-type', choices=MODEL_TYPES, required=True)
  p.add_argument('--model-size', type=_parse_size, required=True, help='model input WxH')
  p.add_argument('--camera-resolutions', type=_parse_size, nargs='+', required=True)
  p.add_argument('--frame-skip', type=int, default=None, help='frame skip value (auto-derived if not provided)')
  p.add_argument('--output', required=True)

  p.add_argument('--vision-onnx', help='vision ONNX (for split models)')
  p.add_argument('--policy-onnx', help='policy ONNX (for vision_policy)')
  p.add_argument('--off-policy-onnx', help='off-policy ONNX (for vision_multi_policy)')
  p.add_argument('--on-policy-onnx', help='on-policy ONNX (for vision_multi_policy)')
  p.add_argument('--supercombo-onnx', help='supercombo ONNX (for supercombo)')

  args = p.parse_args()
  out = defaultdict(dict)

  if args.model_type == 'vision_policy':
    assert args.vision_onnx and args.policy_onnx
    vision_runner = OnnxRunner(args.vision_onnx)
    policy_runner = OnnxRunner(args.policy_onnx)
    out['metadata']['vision'] = make_metadata_dict(args.vision_onnx)
    out['metadata']['policy'] = make_metadata_dict(args.policy_onnx)

    frame_skip = args.frame_skip if args.frame_skip is not None else derive_frame_skip(out['metadata']['vision']['input_shapes'],
                                                                                       out['metadata']['policy']['input_shapes'])

    for cam_w, cam_h in args.camera_resolutions:
      nv12 = NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
      model_w, model_h = args.model_size
      out[(cam_w, cam_h)] = {
        name: compile_split_policy(nv12, model_w, model_h, prepare_only, frame_skip,
                                   vision_runner, policy_runner,
                                   out['metadata']['vision'], out['metadata']['policy'])
        for name, prepare_only in [('warp_enqueue', True), ('run_policy', False)]
      }

  elif args.model_type == 'supercombo':
    assert args.supercombo_onnx
    model_runner = OnnxRunner(args.supercombo_onnx)
    out['metadata']['model'] = make_metadata_dict(args.supercombo_onnx)

    frame_skip = args.frame_skip if args.frame_skip is not None else derive_frame_skip({}, out['metadata']['model']['input_shapes'])

    for cam_w, cam_h in args.camera_resolutions:
      nv12 = NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
      model_w, model_h = args.model_size
      out[(cam_w, cam_h)] = {
        name: compile_supercombo(nv12, model_w, model_h, prepare_only, frame_skip,
                                 model_runner, out['metadata']['model'])
        for name, prepare_only in [('warp_enqueue', True), ('run_policy', False)]
      }

  elif args.model_type == 'vision_multi_policy':
    assert args.vision_onnx
    vision_runner = OnnxRunner(args.vision_onnx)
    out['metadata']['vision'] = make_metadata_dict(args.vision_onnx)

    policy_runners = []
    policy_onnxes = []
    if args.policy_onnx:
      policy_onnxes.append(('policy', args.policy_onnx))
    if args.off_policy_onnx:
      policy_onnxes.append(('off_policy', args.off_policy_onnx))
    if args.on_policy_onnx:
      policy_onnxes.append(('on_policy', args.on_policy_onnx))

    for name, onnx_path in policy_onnxes:
      runner = OnnxRunner(onnx_path)
      policy_runners.append(runner)
      out['metadata'][name] = make_metadata_dict(onnx_path)

    first_policy_key = policy_onnxes[0][0]
    frame_skip = args.frame_skip if args.frame_skip is not None else derive_frame_skip(out['metadata']['vision']['input_shapes'],
                                                                                       out['metadata'][first_policy_key]['input_shapes'])

    for cam_w, cam_h in args.camera_resolutions:
      nv12 = NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
      model_w, model_h = args.model_size
      out[(cam_w, cam_h)] = {
        name: compile_multi_policy(nv12, model_w, model_h, prepare_only, frame_skip,
                                   vision_runner, policy_runners,
                                   out['metadata']['vision'], out['metadata'][first_policy_key])
        for name, prepare_only in [('warp_enqueue', True), ('run_policy', False)]
      }

  with open(args.output, "wb") as f:
    pickle.dump(out, f)
  pkl_size = os.path.getsize(args.output)
  print(f"Saved combined JIT to {args.output} ({pkl_size / 1e6:.2f} MB)")

  from openpilot.common.file_chunker import chunk_file, get_chunk_targets
  chunk_targets = get_chunk_targets(args.output, pkl_size)
  chunk_file(args.output, chunk_targets)
  num_chunks = len(chunk_targets) - 1
  print(f"Chunked into {num_chunks} file(s)")
