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
from collections import defaultdict
from functools import partial
import numpy as np

from tinygrad import dtypes
from tinygrad.device import Device
from tinygrad.engine.jit import TinyJit
from tinygrad.tensor import Tensor

from openpilot.selfdrive.modeld.compile_modeld import NV12Frame, make_frame_prepare, sample_desire, sample_skip, shift_and_sample


MODEL_TYPES = ('vision_policy', 'supercombo', 'vision_multi_policy')


def _detect_desire_key(shapes: dict) -> str | None:
  return next((key for key in shapes if key.startswith('desire')), None)


def _detect_vision_keys(shapes: dict) -> tuple[str | None, str | None]:
  img_keys = sorted(key for key in shapes if 'img' in key)
  return (
    next((key for key in img_keys if 'big' not in key), None),
    next((key for key in img_keys if 'big' in key), None)
  )


def derive_frame_skip(vision_input_shapes: dict, policy_input_shapes: dict) -> int:
  features_buffer = policy_input_shapes.get('features_buffer')
  return 1 if not features_buffer or features_buffer[1] >= 99 else 4


def generate_queues_and_npy(input_shapes: dict, frame_skip: int, device: str = Device.DEFAULT) -> tuple[dict, dict]:
  road_key, _ = _detect_vision_keys(input_shapes)
  if not road_key:
    raise ValueError("Vision road key missing from input shapes.")

  img_shape = input_shapes[road_key]
  n_frames = img_shape[1] // 6
  img_buf_shape = (frame_skip * (n_frames - 1) + 1, 6, img_shape[2], img_shape[3])

  desire_key = _detect_desire_key(input_shapes)
  if not desire_key:
    raise ValueError("Desire key missing from input shapes.")

  desire_shape = input_shapes[desire_key]
  features_buffer = input_shapes.get('features_buffer')

  npy_arrays = {
    'desire': np.zeros(desire_shape[2], dtype=np.float32),
    'tfm': np.zeros((3, 3), dtype=np.float32),
    'big_tfm': np.zeros((3, 3), dtype=np.float32)
  }

  for key, shape in input_shapes.items():
    if key not in npy_arrays and 'img' not in key and key not in ('features_buffer', desire_key):
      npy_arrays[key] = np.zeros(shape, dtype=np.float32)

  queues = {
    'img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'big_img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'desire_q': Tensor(np.zeros((frame_skip * desire_shape[1], desire_shape[0], desire_shape[2]),
                                  dtype=np.float32), device=device).contiguous().realize()
  }

  if features_buffer:
    queues['feat_q'] = Tensor(np.zeros((frame_skip * (features_buffer[1] - 1) + 1, features_buffer[0], features_buffer[2]),
                                        dtype=np.float32), device=device).contiguous().realize()

  queues.update({key: Tensor(value, device='NPY').realize() for key, value in npy_arrays.items()})
  return queues, npy_arrays


def make_split_input_queues(vision_input_shapes: dict, policy_input_shapes: dict, frame_skip: int, device: str = Device.DEFAULT) -> tuple[dict, dict]:
  return generate_queues_and_npy({**vision_input_shapes, **policy_input_shapes}, frame_skip, device)


def make_supercombo_input_queues(input_shapes: dict, frame_skip: int, device: str = Device.DEFAULT) -> tuple[dict, dict]:
  return generate_queues_and_npy(input_shapes, frame_skip, device)


def create_jit_runner(vision_runner, policy_runners: list, nv12: NV12Frame, model_size: tuple[int, int],
                      features_slice: slice, frame_skip: int, input_shapes: dict, prepare_only: bool):
  frame_prepare = make_frame_prepare(nv12, *model_size)
  sample_skip_fn = partial(sample_skip, frame_skip=frame_skip)
  sample_desire_fn = partial(sample_desire, frame_skip=frame_skip)

  desire_key = _detect_desire_key(input_shapes)
  road_key, wide_key = _detect_vision_keys(input_shapes)

  if not desire_key or not road_key or not wide_key:
    raise ValueError("Missing required vision or desire keys in input shapes.")

  extra_keys = [key for key in input_shapes if key not in (desire_key, 'features_buffer', 'traffic_convention') and 'img' not in key]

  def runner(img_q, big_img_q, feat_q, frame, big_frame, tfm, big_tfm, **kwargs):
    desire_q = kwargs['desire_q']
    desire = kwargs['desire']
    traffic_convention = kwargs.get('traffic_convention')

    npys = [tfm.to(Device.DEFAULT), big_tfm.to(Device.DEFAULT), desire.to(Device.DEFAULT)]
    if traffic_convention is not None:
      npys.append(traffic_convention.to(Device.DEFAULT))

    extra_tensors = {key: kwargs[key].to(Device.DEFAULT) for key in extra_keys if key in kwargs}
    Tensor.realize(*npys, *extra_tensors.values())

    tfm_dev, big_tfm_dev, desire_dev = npys[:3]
    traffic_conv_dev = npys[3] if traffic_convention is not None else None

    img = shift_and_sample(img_q, frame_prepare(frame, tfm_dev).unsqueeze(0), sample_skip_fn)
    big_img = shift_and_sample(big_img_q, frame_prepare(big_frame, big_tfm_dev).unsqueeze(0), sample_skip_fn)

    if prepare_only:
      return img, big_img

    desire_buf = shift_and_sample(desire_q, desire_dev.reshape(1, 1, -1), sample_desire_fn)
    inputs = {desire_key: desire_buf, **extra_tensors}
    if traffic_conv_dev is not None:
      inputs['traffic_convention'] = traffic_conv_dev

    if vision_runner:
      vision_out = next(iter(vision_runner({road_key: img, wide_key: big_img}).values())).cast('float32')
      new_feat = vision_out[:, features_slice].reshape(1, -1).unsqueeze(0)
      inputs['features_buffer'] = shift_and_sample(feat_q, new_feat, sample_skip_fn)
      policy_outs = [next(iter(runner(inputs).values())).cast('float32') for runner in policy_runners]
      return (vision_out, *policy_outs) if len(policy_outs) > 1 else (vision_out, policy_outs[0])

    inputs.update({road_key: img, wide_key: big_img, 'features_buffer': sample_skip_fn(feat_q)})
    policy_out = next(iter(policy_runners[0](inputs).values())).cast('float32')
    new_feat = policy_out[:, features_slice].reshape(1, -1).unsqueeze(0)
    shift_and_sample(feat_q, new_feat, sample_skip_fn)
    return policy_out

  return runner


def compile_and_warmup(nv12: NV12Frame, model_size: tuple[int, int], prepare_only: bool, frame_skip: int, vision_runner, policy_runners: list, metadata: dict):
  print(f"Compiling combined JIT for {nv12.width}x{nv12.height} (prepare_only={prepare_only})...")

  all_shapes = {key: value for meta in metadata.values() for key, value in meta['input_shapes'].items()}

  feat_meta = metadata.get('vision') or metadata.get('model') or metadata.get('policy')
  if not feat_meta:
    raise ValueError("Could not find vision, model, or policy metadata.")

  features_slice = feat_meta['output_slices']['hidden_state']

  run_func = create_jit_runner(vision_runner, policy_runners, nv12, model_size, features_slice, frame_skip, all_shapes, prepare_only)
  run_jit = TinyJit(run_func, prune=True)
  queues, npy_arrays = generate_queues_and_npy(all_shapes, frame_skip, Device.DEFAULT)

  for i in range(3):
    np.random.seed(42 + i)
    frame = Tensor.randint(nv12.size, low=0, high=256, dtype=dtypes.uint8).realize()
    big_frame = Tensor.randint(nv12.size, low=0, high=256, dtype=dtypes.uint8).realize()
    for arr in npy_arrays.values():
        arr[:] = np.random.randn(*arr.shape).astype(arr.dtype)

    Device.default.synchronize()
    start_time = time.perf_counter()
    run_jit(**queues, frame=frame, big_frame=big_frame)
    mid_time = time.perf_counter()
    Device.default.synchronize()
    print(f"  [{i + 1}/3] enqueue {(mid_time - start_time) * 1e3:6.2f} ms -- total {(time.perf_counter() - start_time) * 1e3:6.2f} ms")

  return pickle.loads(pickle.dumps(run_jit)) if not prepare_only else run_jit


def _parse_size(size_str: str) -> tuple[int, int]:
  width, height = size_str.lower().split('x')
  return int(width), int(height)


def _compile_for_resolutions(camera_resolutions: list, model_size: tuple[int, int], frame_skip: int,
                             vision_runner, policy_runners: list, metadata: dict) -> dict:
  return {
    (cam_w, cam_h): {
      name: compile_and_warmup(NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h)), model_size, prepare_only,
                                frame_skip, vision_runner, policy_runners, metadata)
      for name, prepare_only in [('warp_enqueue', True), ('run_policy', False)]
    }
    for cam_w, cam_h in camera_resolutions
  }


def _load_policy_runners(args: argparse.Namespace) -> tuple[list, list]:
  runners, keys = [], []
  for name, onnx_arg in [('policy', args.policy_onnx), ('off_policy', args.off_policy_onnx), ('on_policy', args.on_policy_onnx)]:
    if onnx_arg:
      runners.append(OnnxRunner(onnx_arg))
      keys.append(name)
  return runners, keys


if __name__ == "__main__":
  from tinygrad.nn.onnx import OnnxRunner
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  from openpilot.selfdrive.modeld.get_model_metadata import make_metadata_dict

  parser = argparse.ArgumentParser(description="Compile combined JIT pkl for sunnypilot modeld_v2")
  parser.add_argument('--model-type', choices=MODEL_TYPES, required=True)
  parser.add_argument('--model-size', type=_parse_size, required=True, help='model input WxH')
  parser.add_argument('--camera-resolutions', type=_parse_size, nargs='+', required=True)
  parser.add_argument('--frame-skip', type=int, default=None, help='frame skip value (auto-derived if not provided)')
  parser.add_argument('--output', required=True)

  parser.add_argument('--vision-onnx', help='vision ONNX (for split models)')
  parser.add_argument('--policy-onnx', help='policy ONNX (for vision_policy)')
  parser.add_argument('--off-policy-onnx', help='off-policy ONNX (for vision_multi_policy)')
  parser.add_argument('--on-policy-onnx', help='on-policy ONNX (for vision_multi_policy)')
  parser.add_argument('--supercombo-onnx', help='supercombo ONNX (for supercombo)')

  args = parser.parse_args()
  output_data = defaultdict(dict)

  vision_runner = OnnxRunner(args.vision_onnx) if args.vision_onnx else None

  if args.model_type == 'vision_policy':
    assert vision_runner and args.policy_onnx
    policy_runners = [OnnxRunner(args.policy_onnx)]
    output_data['metadata'] = {'vision': make_metadata_dict(args.vision_onnx), 'policy': make_metadata_dict(args.policy_onnx)}
  elif args.model_type == 'supercombo':
    assert args.supercombo_onnx
    policy_runners = [OnnxRunner(args.supercombo_onnx)]
    output_data['metadata'] = {'model': make_metadata_dict(args.supercombo_onnx)}
  elif args.model_type == 'vision_multi_policy':
    assert vision_runner
    policy_runners, policy_names = _load_policy_runners(args)
    output_data['metadata'] = {'vision': make_metadata_dict(args.vision_onnx)}
    for name, runner_arg in zip(policy_names, [args.policy_onnx, args.off_policy_onnx, args.on_policy_onnx], strict=True):
      if runner_arg:
        output_data['metadata'][name] = make_metadata_dict(runner_arg)

  first_policy_meta = output_data['metadata'].get('policy', output_data['metadata'].get('model', output_data['metadata'].get('off_policy', {})))
  vision_meta = output_data['metadata'].get('vision', {})

  derived_frame_skip = args.frame_skip or derive_frame_skip(vision_meta.get('input_shapes', {}), first_policy_meta.get('input_shapes', {}))
  output_data.update(_compile_for_resolutions(args.camera_resolutions, args.model_size, derived_frame_skip,
                                              vision_runner, policy_runners, output_data['metadata']))

  with open(args.output, "wb") as file:
    pickle.dump(output_data, file)

  pkl_size = os.path.getsize(args.output)
  print(f"Saved combined JIT to {args.output} ({pkl_size / 1e6:.2f} MB)")

  from openpilot.common.file_chunker import chunk_file, get_chunk_targets
  chunk_targets = get_chunk_targets(args.output, pkl_size)
  chunk_file(args.output, chunk_targets)
  print(f"Chunked into {len(chunk_targets) - 1} file(s)")
