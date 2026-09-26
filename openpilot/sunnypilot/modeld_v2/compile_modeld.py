#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import atexit
import codecs
import gc
import math
import multiprocessing as mp
import os
import pickle
import shutil
import tempfile
import time
from functools import partial
from typing import Any

import numpy as np

from openpilot.common.file_chunker import chunk_file, get_chunk_targets, open_file_chunked
from openpilot.sunnypilot.modeld_v2.helpers import dump_oob, load_oob
import openpilot.sunnypilot.modeld_v2.stock_dependencies as stock
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info

from tinygrad import dtypes
from tinygrad.device import Device
from tinygrad.engine.jit import TinyJit
from tinygrad.helpers import Context
from tinygrad.nn.onnx import OnnxRunner, OnnxPBParser
from tinygrad.tensor import Tensor

os.environ['GMMU'] = '0'

def _patch_tinygrad_fetch_fw():
  try:
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
  except ImportError:
    pass
_patch_tinygrad_fetch_fw()

def _patch_ops_serialization():
  try:
    from tinygrad.uop.ops import Ops
    def __reduce_ex__(self, proto):
      return (getattr, (self.__class__, self.name))
    Ops.__reduce_ex__ = __reduce_ex__
  except ImportError:
    pass
_patch_ops_serialization()

MODEL_TYPES = ('vision_policy', 'supercombo', 'vision_multi_policy')
WARP_INPUTS = ['tfm', 'big_tfm']
POLICY_INPUTS = ['img_q', 'big_img_q', 'feat_q', 'desire_q', 'packed_npy_inputs']

class MetadataOnnxPBParser(OnnxPBParser):
  def _parse_ModelProto(self) -> dict:
    obj: dict[str, Any] = {"graph": {"input": [], "output": []}, "metadata_props": []}
    for fid, wire_type in self._parse_message(self.reader.len):
      match fid:
        case 7:
          obj["graph"] = self._parse_GraphProto()
        case 14:
          obj["metadata_props"].append(self._parse_StringStringEntryProto())
        case _:
          self.reader.skip_field(wire_type)
    return obj

def get_name_and_shape(value_info: dict[str, Any]) -> tuple[str, tuple[int, ...]]:
  shape = tuple(int(dim) if isinstance(dim, int) else 0 for dim in value_info["parsed_type"].shape)
  name = value_info["name"]
  return name, shape

def get_metadata_value_by_name(model: dict[str, Any], name: str) -> str | Any:
  for prop in model["metadata_props"]:
    if prop["key"] == name:
      return prop["value"]
  return None

def make_metadata_dict(model_path):
  with Context(DEV='CPU'):
    model = MetadataOnnxPBParser(model_path).parse()
    output_slices_raw = get_metadata_value_by_name(model, 'output_slices')
    assert output_slices_raw is not None, 'output_slices not found in metadata'

    output_slices = pickle.loads(codecs.decode(output_slices_raw.encode(), "base64"))
    if 'hidden_state' not in output_slices:
      output_slices['hidden_state'] = slice(0, 512)

    meta_dict = {
      'model_checkpoint': get_metadata_value_by_name(model, 'model_checkpoint'),
      'output_slices': output_slices,
      'input_shapes': dict(get_name_and_shape(x) for x in model["graph"]["input"]),
      'output_shapes': dict(get_name_and_shape(x) for x in model["graph"]["output"]),
    }
    del model
    gc.collect()
    return meta_dict


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
    'packed_npy_inputs': Tensor(packed_npy_inputs, device=device if os.getenv('CHESTNUT') else 'NPY').realize(),
  }

  if features_buffer:
    feat_dim = math.prod(features_buffer[2:])
    feat_q_len = frame_skip * features_buffer[1] if is_supercombo else frame_skip * (features_buffer[1] - 1) + 1
    queues['feat_q'] = Tensor(np.zeros((feat_q_len, features_buffer[0], feat_dim),
                       dtype=np.float32), device=device).contiguous().realize()

  for key in ('tfm', 'big_tfm'):
    if key not in npy_arrays:
      npy_arrays[key] = np.eye(3, dtype=np.float32)
    queues[key] = Tensor(npy_arrays[key], device='NPY').realize()

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

  def run_policy(warped, img_q, big_img_q, feat_q, desire_q=None, packed_npy_inputs=None, **kwargs):
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


def compile_jit(jit_or_fn, input_keys_or_make_inputs, make_queues=None, make_random_inputs=None, benchmark_runs: int = 1, clear_refs=None):
  if callable(input_keys_or_make_inputs) and make_queues is None:
    fn = jit_or_fn
    make_inputs = input_keys_or_make_inputs
    jit = TinyJit(fn, prune=True)

    def run_eval(f, seed, count):
      args, kwargs = make_inputs(seed)
      result = None
      for i in range(count):
        Device.default.synchronize()
        st = time.perf_counter()
        f(*args, **kwargs)
        Device.default.synchronize()
        print(f"  [{i+1}/{count}] {(time.perf_counter()-st)*1e3:.2f} ms")
        if i == 0:
          result = [t.numpy().copy() for t in kwargs['output_buffers'].values()]
      return result
  else:
    jit = jit_or_fn
    input_keys = input_keys_or_make_inputs
    assert make_queues is not None
    queues_maker = make_queues

    def run_eval(f, seed, count):
      queues_res = queues_maker(Device.DEFAULT)
      input_queues, npy = queues_res[0], queues_res[1]
      frame_views = queues_res[2] if len(queues_res) > 2 else {}
      rng = np.random.default_rng(seed)
      Tensor.manual_seed(seed)

      for i in range(count):
        for v in npy.values():
          v[:] = rng.standard_normal(v.shape).astype(v.dtype)
        for v in frame_views.values():
          v[:] = rng.integers(0, 256, size=v.shape, dtype=np.uint8)
        Device.default.synchronize()
        random_inputs = make_random_inputs() if make_random_inputs is not None else {}
        st = time.perf_counter()
        outs = f(**{k: input_queues[k] for k in input_keys if k in input_queues}, **random_inputs)
        mt = time.perf_counter()
        Device.default.synchronize()
        et = time.perf_counter()
        print(f"  [{i+1}/{count}] enqueue {(mt-st)*1e3:6.2f} ms -- total {(et-st)*1e3:6.2f} ms")

        if i == 0:
          val = [np.copy(v.numpy()) for v in (outs if isinstance(outs, tuple) else [outs])] if outs is not None else []
      return val

  print('capture + replay')
  gc.collect()
  test_val = run_eval(jit, 42, 3)
  print(f'pickle round trip ({benchmark_runs} runs per seed)')
  with tempfile.TemporaryFile(dir=".") as f:
    dump_oob(jit, f)
    del jit
    if clear_refs:
      clear_refs()
    gc.collect()
    f.seek(0)
    loaded_jit = load_oob(f)

  for seed in (42, 43):
    reference = test_val if seed == 42 else run_eval(jit_or_fn, seed, 1)
    actual = run_eval(loaded_jit, seed, benchmark_runs)
    for ref, val in zip(reference, actual, strict=True):
      np.testing.assert_array_equal(ref, val)
  return loaded_jit


def _parse_size(size_str: str) -> tuple[int, int]:
  width, height = size_str.lower().split('x')
  return int(width), int(height)


def read_file_chunked_to_disk(path):
  if not path:
    return None
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


def _compile_unified_resolution_worker(cam_w, cam_h, supercombo_onnx, model_w, model_h, derived_frame_skip, benchmark_runs, result_path):
  os.environ['GMMU'] = '0'
  model_metadata = make_metadata_dict(supercombo_onnx)
  model_runner = OnnxRunner(supercombo_onnx)
  features_slice = model_metadata['output_slices']['hidden_state']
  run_policy = make_run_policy(None, [model_runner], features_slice, derived_frame_skip, model_metadata['input_shapes'])
  nv12 = stock.NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
  frame_copy_size = stock.nv12_copy_size(nv12.stride, nv12.y_height, nv12.uv_height)
  make_model_queues = partial(stock.make_input_queues, model_metadata['input_shapes'], derived_frame_skip,
                              frame_copy_size=frame_copy_size)
  warp = stock.make_warp(nv12, model_w, model_h)
  run_model_jit = TinyJit(stock.make_run_model(warp, run_policy, model_metadata, frame_copy_size), prune=True)

  def cleanup_unified():
    nonlocal run_model_jit, run_policy, model_runner, warp
    run_model_jit, run_policy, model_runner, warp = None, None, None, None
  compiled_jit = compile_jit(
    run_model_jit, stock.MODELD_INPUTS, make_model_queues, benchmark_runs=benchmark_runs, clear_refs=cleanup_unified)
  result_data = (compiled_jit, Device.DEFAULT)
  with open(result_path, "wb") as f:
    dump_oob(result_data, f)

def _compile_warp_resolution_worker(cam_w, cam_h, model_w, model_h, benchmark_runs, result_path):
  os.environ['GMMU'] = '0'
  nv12 = stock.NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
  WARP_DEV = os.getenv('WARP_DEV', Device.DEFAULT)
  make_random_warp_inputs = partial(make_random_images, keys=['frame', 'big_frame'], shape=nv12.size, device=WARP_DEV)
  warp = TinyJit(stock.make_warp(nv12, model_w, model_h), prune=True)

  def cleanup_warp():
    nonlocal warp
    warp = None
  compiled_jit = compile_jit(warp, WARP_INPUTS, make_warp_queues, make_random_inputs=make_random_warp_inputs,
                            benchmark_runs=benchmark_runs, clear_refs=cleanup_warp)

  result_data = (compiled_jit, Device.DEFAULT)
  with open(result_path, "wb") as f:
    dump_oob(result_data, f)


if __name__ == "__main__":
  if 'USB' in os.getenv('DEV', '') or os.getenv('CHESTNUT'):
    from openpilot.system.hardware.chestnut.flash import link_up
    for _ in range(10):
      if link_up():
        break
      time.sleep(1)
    else:
      raise RuntimeError("Chestnut not ready, skipping big model build")

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

  is_unified_supercombo = False
  if args.model_type == 'supercombo':
    assert args.supercombo_onnx
    model_metadata = make_metadata_dict(args.supercombo_onnx)
    derived_frame_skip = args.frame_skip or derive_frame_skip({}, model_metadata['input_shapes'])
    if derived_frame_skip != 1 and os.getenv('CHESTNUT'):
      is_unified_supercombo = True

  if is_unified_supercombo:
    output_data['metadata'] = {'model': model_metadata, **model_metadata}
    print(f"Compiling supercombo ONNX JIT (model_size={model_w}x{model_h})")
    runner = OnnxRunner(args.supercombo_onnx)
    from tinygrad.dtype import _to_np_dtype
    specs = {name: (tuple(s if isinstance(s, int) else 1 for s in spec.shape), np.dtype(_to_np_dtype(spec.dtype)).str,
                    Device.DEFAULT) for name, spec in runner.graph_inputs.items()}

    def model(inputs):
      return {name: value.contiguous() for name, value in runner({name: value.to(Device.DEFAULT) for name, value in inputs.items()}).items()}

    def allocate_inputs(input_specs, initialize=None):
      arrays = {name: np.zeros(shape, dtype=dtype) for name, (shape, dtype, _) in input_specs.items()}
      if initialize is not None:
        initialize(arrays)
      return {name: Tensor(arrays[name], device=device).realize() for name, (_, _, device) in input_specs.items()}

    output_specs = {name: (value.shape, np.dtype(_to_np_dtype(value.dtype)).name, Device.DEFAULT)
                    for name, value in model(allocate_inputs(specs)).items()}

    def make_inputs(seed):
      rng = np.random.default_rng(seed)
      def initialize(arrays):
        for name, value in arrays.items():
          dtype = runner.graph_inputs[name].dtype
          value[...] = (rng.standard_normal(value.shape) if dtypes.is_float(dtype) else
                        rng.integers(0, 256, value.shape, dtype=np.uint8) if dtype == dtypes.uint8 else
                        rng.integers(0, 2 if dtype == dtypes.bool else 16, value.shape))
      return (), allocate_inputs(specs, initialize) | {'output_buffers': allocate_inputs(output_specs)}

    def run(output_buffers, **inputs):
      outputs = model(inputs)
      Tensor.realize(*outputs.values())
      Tensor.realize(*(output_buffers[name].assign(value) for name, value in outputs.items()))

    output_data['run'] = compile_jit(run, make_inputs, benchmark_runs=args.benchmark_runs)
    output_data['input_specs'] = specs
    output_data['output_specs'] = output_specs
    output_data['input_devices'] = {'model': Device.DEFAULT}
  else:
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
      for name in policy_names:
        runner_arg = getattr(args, f"{name}_onnx")
        output_data['metadata'][name] = make_metadata_dict(runner_arg)

    policy_keys = [key for key in output_data['metadata'].keys() if key != 'vision']
    first_policy_meta = output_data['metadata'][policy_keys[0]] if policy_keys else {}
    vision_meta = output_data['metadata'].get('vision', {})

    derived_frame_skip = args.frame_skip or derive_frame_skip(vision_meta.get('input_shapes', {}), first_policy_meta.get('input_shapes', {}))
    all_shapes = {
      key: value for meta in output_data['metadata'].values()
      if isinstance(meta, dict) and 'input_shapes' in meta for key, value in meta['input_shapes'].items()
    }
    feat_meta = output_data['metadata'].get('vision') or output_data['metadata'].get('model') or output_data['metadata'].get('policy')
    assert isinstance(feat_meta, dict)
    features_slice = feat_meta['output_slices']['hidden_state']
    is_supercombo = vision_runner is None
    gc.collect()

    print(f"Compiling run_policy JIT (model_size={model_w}x{model_h}, frame_skip={derived_frame_skip})...")
    run_policy_func = make_run_policy(vision_runner, policy_runners, features_slice, derived_frame_skip, all_shapes)
    run_policy_jit = TinyJit(run_policy_func, prune=True)
    make_policy_queues = partial(generate_queues_and_npy, all_shapes, derived_frame_skip, is_supercombo=is_supercombo)
    WARP_DEV = os.getenv('WARP_DEV', Device.DEFAULT)
    make_random_model_inputs = partial(make_random_images, keys=['warped'], shape=(2, 6, model_h // 2, model_w // 2), device=WARP_DEV)

    def cleanup_policy():
      global run_policy_jit, run_policy_func, vision_runner, policy_runners
      run_policy_jit, run_policy_func, vision_runner, policy_runners = None, None, None, None

    output_data['run_policy'] = compile_jit(run_policy_jit, POLICY_INPUTS, make_policy_queues,
                                            make_random_inputs=make_random_model_inputs, benchmark_runs=args.benchmark_runs, clear_refs=cleanup_policy)

    ctx = mp.get_context('spawn')
    output_data['input_devices'] = {}
    tmp_files = []
    for cam_w, cam_h in set(args.camera_resolutions):
      print(f"Compiling warp JIT for {cam_w}x{cam_h}")
      tmp_res = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl", dir=".")
      tmp_res.close()

      p = ctx.Process(target=_compile_warp_resolution_worker, args=(cam_w, cam_h, model_w, model_h, args.benchmark_runs, tmp_res.name))
      p.start()
      p.join()
      if p.exitcode != 0:
        raise RuntimeError(f"Warp compilation worker failed for {cam_w}x{cam_h}")

      tmp_files.append((cam_w, cam_h, tmp_res.name))
    for cam_w, cam_h, tmp_name in tmp_files:
      with open(tmp_name, "rb") as f:
        compiled_jit, dev_name = load_oob(f)
      output_data[(cam_w, cam_h)] = compiled_jit
      output_data['input_devices']['warp'] = dev_name
      os.remove(tmp_name)
      gc.collect()
    output_data['metadata']['warp_dev'] = Device.DEFAULT

  gc.collect()
  with open(args.output, "wb") as file:
    dump_oob(output_data, file)

  pkl_size = os.path.getsize(args.output)
  print(f"Saved combined JIT to {args.output} ({pkl_size / 1e6:.2f} MB)")
  chunk_targets = get_chunk_targets(args.output, pkl_size)
  chunk_file(args.output, chunk_targets)
  print(f"Chunked into {len(chunk_targets) - 1} file(s)")
