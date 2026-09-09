#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import math
import os
import tempfile
import time
from functools import partial
from openpilot.selfdrive.modeld.helpers import dump_oob, load_oob
import numpy as np
os.environ['GMMU'] = '0'

def _patch_tinygrad_fetch_fw():
  import hashlib
  import pathlib
  import zstandard
  from tinygrad import helpers
  _orig_fetch_fw = helpers.fetch_fw
  def fetch_fw(path, name, sha256):
    p = pathlib.Path(f"/lib/firmware/{path}/{name}.zst")
    if p.is_file():
      blob = zstandard.ZstdDecompressor().stream_reader(p.read_bytes()).read()
      if hashlib.sha256(blob).hexdigest() == sha256:
        return blob
    return _orig_fetch_fw(path, name, sha256)
  helpers.fetch_fw = fetch_fw
_patch_tinygrad_fetch_fw()

import openpilot.selfdrive.modeld.compile_modeld as stock
from tinygrad import dtypes
from tinygrad.device import Device
from tinygrad.engine.jit import TinyJit
from tinygrad.tensor import Tensor

MODEL_TYPES = ('vision_policy', 'supercombo', 'vision_multi_policy')
WARP_INPUTS = ['tfm', 'big_tfm']
POLICY_INPUTS = ['img_q', 'big_img_q', 'feat_q', 'desire_q', 'packed_npy_inputs']
nv12_copy_size = stock.nv12_copy_size

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


def get_policy_npy_shapes(input_shapes: dict, is_supercombo: bool = False) -> tuple[dict, list[int]]:
  desire_key = _detect_desire_key(input_shapes)
  shapes = {}
  if desire_key:
    shapes['desire'] = (input_shapes[desire_key][2],)

  for key, shape in input_shapes.items():
    if key not in (desire_key, 'features_buffer') and 'img' not in key:
      shapes[key] = tuple(shape)

  if is_supercombo and 'features_buffer' in input_shapes:
    fb = input_shapes['features_buffer']
    feat_dim = math.prod(fb[2:])
    shapes['prev_feat'] = (fb[0], feat_dim)

  sizes = [int(np.prod(size)) for size in shapes.values()]
  return shapes, sizes


def generate_queues_and_npy(input_shapes: dict, frame_skip: int, device: str = Device.DEFAULT,
                            is_supercombo: bool = False) -> tuple[dict, dict]:
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
    'tfm': np.zeros((3, 3), dtype=np.float32),
    'big_tfm': np.zeros((3, 3), dtype=np.float32)
  }

  shapes, sizes = get_policy_npy_shapes(input_shapes, is_supercombo=is_supercombo)
  packed_npy_inputs = np.zeros(sum(sizes), dtype=np.float32)

  split_indices = np.cumsum(sizes[:-1]) if len(sizes) > 1 else []
  split_views = np.split(packed_npy_inputs, split_indices) if len(sizes) > 0 else []
  for (k, s), v in zip(shapes.items(), split_views, strict=True):
    npy_arrays[k] = v.reshape(s)

  queues = {
    'img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'big_img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'desire_q': Tensor(np.zeros((frame_skip * desire_shape[1], desire_shape[0], desire_shape[2]),
                  dtype=np.float32), device=device).contiguous().realize(),
    'packed_npy_inputs': Tensor(packed_npy_inputs, device='NPY').realize(),
  }

  if features_buffer:
    feat_dim = math.prod(features_buffer[2:])
    feat_q_len = frame_skip * features_buffer[1] if is_supercombo else frame_skip * (features_buffer[1] - 1) + 1
    queues['feat_q'] = Tensor(np.zeros((feat_q_len, features_buffer[0], feat_dim),
                       dtype=np.float32), device=device).contiguous().realize()

  queues.update({key: Tensor(value, device='NPY').realize() for key, value in npy_arrays.items() if key in ('tfm', 'big_tfm')})

  return queues, npy_arrays


def make_split_input_queues(vision_input_shapes: dict, policy_input_shapes: dict,
                            frame_skip: int, device: str = Device.DEFAULT) -> tuple[dict, dict]:
  return generate_queues_and_npy({**vision_input_shapes, **policy_input_shapes}, frame_skip, device, is_supercombo=False)


def make_supercombo_input_queues(input_shapes: dict, frame_skip: int,
                                 device: str = Device.DEFAULT) -> tuple[dict, dict]:
  return generate_queues_and_npy(input_shapes, frame_skip, device, is_supercombo=True)


def make_random_images(keys, shape, device, rng=None):
  return {k: Tensor.randint(shape, low=0, high=256, dtype=dtypes.uint8, device=device).realize() for k in keys}


def make_warp_queues(device=Device.DEFAULT):
  npy = {
    'tfm': np.zeros((3, 3), dtype=np.float32),
    'big_tfm': np.zeros((3, 3), dtype=np.float32),
  }
  queues = {k: Tensor(v, device='NPY').realize() for k, v in npy.items()}
  return queues, npy


def make_run_policy(vision_runner, policy_runners: list, features_slice: slice, frame_skip: int, input_shapes: dict):
  sample_skip_fn = partial(stock.sample_skip, frame_skip=frame_skip)
  sample_desire_fn = partial(stock.sample_desire, frame_skip=frame_skip)

  desire_key = _detect_desire_key(input_shapes)
  road_key, wide_key = _detect_vision_keys(input_shapes)

  if not desire_key or not road_key or not wide_key:
    raise ValueError("Missing required vision or desire keys in input shapes.")

  is_supercombo = vision_runner is None
  npy_shapes, npy_sizes = get_policy_npy_shapes(input_shapes, is_supercombo=is_supercombo)

  def run_policy(warped, img_q, big_img_q, feat_q, packed_npy_inputs, **kwargs):
    desire_q = kwargs['desire_q']
    packed_npy_inputs_dev = packed_npy_inputs.to(Device.DEFAULT)
    warped_dev = warped.to(Device.DEFAULT)
    Tensor.realize(packed_npy_inputs_dev, warped_dev)

    img = stock.shift_and_sample(img_q, warped_dev[0:1], sample_skip_fn)
    big_img = stock.shift_and_sample(big_img_q, warped_dev[1:2], sample_skip_fn)

    unpacked_tensors = [tensor.reshape(shape) for tensor, shape in zip(packed_npy_inputs_dev.split(npy_sizes), npy_shapes.values(), strict=True)]
    unpacked_dict = dict(zip(npy_shapes.keys(), unpacked_tensors, strict=True))

    desire_dev = unpacked_dict['desire']
    desire_buf = stock.shift_and_sample(desire_q, desire_dev.reshape(1, 1, -1), sample_desire_fn)

    inputs = {desire_key: desire_buf}
    for key, tensor_val in unpacked_dict.items():
      if key not in ('desire', 'prev_feat'):
        inputs[key] = tensor_val

    if 'prev_feat' in unpacked_dict:
      prev_feat_dev = unpacked_dict['prev_feat']
      inputs['features_buffer'] = stock.shift_and_sample(feat_q, prev_feat_dev.reshape(1, 1, -1), sample_skip_fn).reshape(input_shapes['features_buffer'])

    if vision_runner:
      vision_out_cast = next(iter(vision_runner({road_key: img, wide_key: big_img}).values())).cast('float32').realize()
      if 'features_buffer' not in inputs:
        new_feat = vision_out_cast[:, features_slice].reshape(1, -1).unsqueeze(0)
        inputs['features_buffer'] = stock.shift_and_sample(feat_q, new_feat, sample_skip_fn).realize()
      policy_outs = [next(iter(pol_runner(inputs).values())).cast('float32').realize() for pol_runner in policy_runners]
      return (vision_out_cast, *policy_outs) if len(policy_outs) > 1 else (vision_out_cast, policy_outs[0])

    inputs.update({road_key: img, wide_key: big_img})
    if 'features_buffer' not in inputs:
      inputs['features_buffer'] = sample_skip_fn(feat_q).reshape(input_shapes['features_buffer'])

    policy_out = next(iter(policy_runners[0](inputs).values())).cast('float32').realize()
    if 'features_buffer' not in inputs and features_slice is not None:
      new_feat = policy_out[:, features_slice].reshape(1, -1).unsqueeze(0)
      stock.shift_and_sample(feat_q, new_feat, sample_skip_fn).realize()
    return policy_out

  return run_policy


def compile_jit(jit, input_keys, make_queues, make_random_inputs=None, benchmark_runs: int = 1):
  SEED = 42
  def random_inputs_run(fn, seed, n_runs, test_val=None, test_buffers=None, expect_match=True):
    queues_res = make_queues(Device.DEFAULT)
    input_queues, npy = queues_res[0], queues_res[1]
    frame_views = queues_res[2] if len(queues_res) > 2 else {}
    rng = np.random.default_rng(seed)
    Tensor.manual_seed(seed)

    for i in range(n_runs):
      for v in npy.values():
        v[:] = rng.standard_normal(v.shape).astype(v.dtype)
      for v in frame_views.values():
        v[:] = rng.integers(0, 256, size=v.shape, dtype=np.uint8)
      Device.default.synchronize()
      random_inputs = make_random_inputs(rng=rng) if make_random_inputs is not None else {}
      st = time.perf_counter()
      outs = fn(**{k: input_queues[k] for k in input_keys if k in input_queues}, **random_inputs)
      mt = time.perf_counter()
      Device.default.synchronize()
      et = time.perf_counter()
      print(f"  [{i+1}/{n_runs}] enqueue {(mt-st)*1e3:6.2f} ms -- total {(et-st)*1e3:6.2f} ms")

      if i == 0:
        val = [np.copy(v.numpy()) for v in (outs if isinstance(outs, tuple) else [outs])] if outs is not None else []
        buffers = [np.copy(v.numpy().copy()) for v in input_queues.values()]

    if test_val is not None:
      match = all(np.array_equal(a, b) for a, b in zip(val, test_val, strict=True))
      assert match == expect_match, f"outputs {'differ from' if expect_match else 'match'} baseline (seed={seed})"
    if test_buffers is not None:
      match = all(np.array_equal(a, b) for a, b in zip(buffers, test_buffers, strict=True))
      assert match == expect_match, f"buffers {'differ from' if expect_match else 'match'} baseline (seed={seed})"
    return val, buffers

  print('capture + replay')
  test_val, test_buffers = random_inputs_run(jit, SEED, 3)
  print(f'pickle round trip ({benchmark_runs} runs per seed)')
  with tempfile.TemporaryFile(dir=".") as f:
    dump_oob(jit, f)
    f.seek(0)
    loaded_jit = load_oob(f)
  random_inputs_run(loaded_jit, SEED, benchmark_runs, test_val, test_buffers, expect_match=True)
  random_inputs_run(loaded_jit, SEED+1, benchmark_runs, test_val, test_buffers, expect_match=False)
  return jit


def _parse_size(size_str: str) -> tuple[int, int]:
  width, height = size_str.lower().split('x')
  return int(width), int(height)


def read_file_chunked_to_disk(path):
  if not path:
    return None
  import atexit
  import shutil
  from openpilot.common.file_chunker import open_file_chunked
  tmp_path = f'{path}.unchunked'
  with open(tmp_path, 'wb') as f, open_file_chunked(path) as src:
    shutil.copyfileobj(src, f)
  atexit.register(lambda: os.path.exists(tmp_path) and os.remove(tmp_path))
  return tmp_path


def _load_policy_runners(args: argparse.Namespace) -> tuple[list, list]:
  runners, keys = [], []
  for name, onnx_arg in [('policy', args.policy_onnx), ('off_policy', args.off_policy_onnx), ('on_policy', args.on_policy_onnx)]:
    if onnx_arg:
      runners.append(OnnxRunner(onnx_arg))
      keys.append(name)
  return runners, keys


if __name__ == "__main__":
  if 'USB' in os.getenv('DEV', '') or os.getenv('CHESTNUT'):
    from openpilot.system.hardware.chestnut.flash import link_up
    for _ in range(10):
      if link_up():
        break
      time.sleep(1)
    else:
      raise RuntimeError("Chestnut not ready, skipping big model build")

  from openpilot.selfdrive.modeld.get_model_metadata import make_metadata_dict
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  from tinygrad.nn.onnx import OnnxRunner

  parser = argparse.ArgumentParser(description="Compile combined JIT pkl for sunnypilot modeld_v2")
  parser.add_argument('--model-type', choices=MODEL_TYPES, required=True)
  parser.add_argument('--model-size', type=_parse_size, required=True, help='model input WxH')
  parser.add_argument('--camera-resolutions', type=_parse_size, nargs='+', required=True)
  parser.add_argument('--frame-skip', type=int, default=None, help='frame skip value (auto-derived if not provided)')
  parser.add_argument('--benchmark-runs', type=int, default=1, help='benchmark runs')
  parser.add_argument('--output', required=True)

  parser.add_argument('--vision-onnx', help='vision ONNX (for split models)')
  parser.add_argument('--policy-onnx', help='policy ONNX (for vision_policy)')
  parser.add_argument('--off-policy-onnx', help='off-policy ONNX (for vision_multi_policy)')
  parser.add_argument('--on-policy-onnx', help='on-policy ONNX (for vision_multi_policy)')
  parser.add_argument('--supercombo-onnx', help='supercombo ONNX (for supercombo)')

  args = parser.parse_args()
  model_w, model_h = args.model_size
  output_data = {}

  args.vision_onnx = read_file_chunked_to_disk(args.vision_onnx)
  args.policy_onnx = read_file_chunked_to_disk(args.policy_onnx)
  args.off_policy_onnx = read_file_chunked_to_disk(args.off_policy_onnx)
  args.on_policy_onnx = read_file_chunked_to_disk(args.on_policy_onnx)
  args.supercombo_onnx = read_file_chunked_to_disk(args.supercombo_onnx)

  if args.model_type == 'supercombo':
    assert args.supercombo_onnx
    model_metadata = make_metadata_dict(args.supercombo_onnx)
    output_data['metadata'] = {'model': model_metadata, **model_metadata}
    output_data['input_devices'] = {'model': Device.DEFAULT}
    output_data['run_model'] = {}
    derived_frame_skip = args.frame_skip or derive_frame_skip({}, model_metadata['input_shapes'])
    model_runner = OnnxRunner(args.supercombo_onnx)
    run_policy = stock.make_run_policy(model_runner, model_metadata, derived_frame_skip)
    for cam_w, cam_h in args.camera_resolutions:
      print(f"Compiling unified run_model JIT for {cam_w}x{cam_h}...")
      nv12 = stock.NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
      frame_copy_size = stock.nv12_copy_size(nv12.stride, nv12.y_height, nv12.uv_height)
      make_model_queues = partial(stock.make_input_queues, model_metadata['input_shapes'], derived_frame_skip,
                                  frame_copy_size=frame_copy_size)
      warp = stock.make_warp(nv12, model_w, model_h)
      run_model_jit = TinyJit(stock.make_run_model(warp, run_policy, model_metadata, frame_copy_size), prune=True)
      output_data['run_model'][(cam_w, cam_h)] = compile_jit(run_model_jit, stock.MODELD_INPUTS, make_model_queues, benchmark_runs=args.benchmark_runs)
  else:
    vision_runner = OnnxRunner(args.vision_onnx) if args.vision_onnx else None
    if args.model_type == 'vision_policy':
      assert vision_runner and args.policy_onnx
      policy_runners = [OnnxRunner(args.policy_onnx)]
      output_data['metadata'] = {'vision': make_metadata_dict(args.vision_onnx), 'policy': make_metadata_dict(args.policy_onnx)}
    elif args.model_type == 'vision_multi_policy':
      assert vision_runner
      policy_runners, policy_names = _load_policy_runners(args)
      output_data['metadata'] = {'vision': make_metadata_dict(args.vision_onnx)}
      for name in policy_names:
        runner_arg = getattr(args, f"{name}_onnx")
        output_data['metadata'][name] = make_metadata_dict(runner_arg)

    policy_keys = [key for key in output_data['metadata'].keys() if key != 'vision']
    first_policy_meta = output_data['metadata'][policy_keys[0]] if policy_keys else {}
    vision_meta = output_data['metadata'].get('vision', {})

    derived_frame_skip = args.frame_skip or derive_frame_skip(vision_meta.get('input_shapes', {}), first_policy_meta.get('input_shapes', {}))
    all_shapes = {key: value for meta in output_data['metadata'].values() for key, value in meta['input_shapes'].items()}
    feat_meta = output_data['metadata'].get('vision') or output_data['metadata'].get('policy')
    assert feat_meta is not None
    features_slice = feat_meta['output_slices']['hidden_state']

    print(f"Compiling run_policy JIT (model_size={model_w}x{model_h}, frame_skip={derived_frame_skip})...")
    run_policy_func = make_run_policy(vision_runner, policy_runners, features_slice, derived_frame_skip, all_shapes)
    run_policy_jit = TinyJit(run_policy_func, prune=True)
    make_policy_queues = partial(generate_queues_and_npy, all_shapes, derived_frame_skip, is_supercombo=False)
    make_random_model_inputs = partial(make_random_images, keys=['warped'], shape=(2, 6, model_h // 2, model_w // 2), device=Device.DEFAULT)
    output_data['run_policy'] = compile_jit(run_policy_jit, POLICY_INPUTS, make_policy_queues, make_random_inputs=make_random_model_inputs)

    for cam_w, cam_h in args.camera_resolutions:
      print(f"Compiling warp JIT for {cam_w}x{cam_h}...")
      nv12 = stock.NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
      frame_copy_size = stock.nv12_copy_size(nv12.stride, nv12.y_height, nv12.uv_height)
      make_random_warp_inputs = partial(make_random_images, keys=['frame', 'big_frame'], shape=frame_copy_size, device=Device.DEFAULT)
      warp = TinyJit(stock.make_warp(nv12, model_w, model_h), prune=True)
      output_data[(cam_w, cam_h)] = compile_jit(warp, WARP_INPUTS, make_warp_queues, make_random_inputs=make_random_warp_inputs)

    output_data['metadata']['warp_dev'] = Device.DEFAULT

  with open(args.output, "wb") as file:
    dump_oob(output_data, file)

  # published whole: the model manager fetches it with parallel byte ranges
  pkl_size = os.path.getsize(args.output)
  print(f"Saved combined JIT to {args.output} ({pkl_size / 1e6:.2f} MB)")
