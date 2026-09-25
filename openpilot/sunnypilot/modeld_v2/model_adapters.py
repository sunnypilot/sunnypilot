"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import codecs
import math
from pathlib import Path
import pickle
import numpy as np

from openpilot.common.basedir import BASEDIR
from openpilot.sunnypilot.modeld_v2.compile_modeld import (POLICY_INPUTS, derive_frame_skip,
                                                           make_split_input_queues, make_supercombo_input_queues)
from openpilot.sunnypilot.modeld_v2.stock_dependencies import nv12_copy_size
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
from tinygrad.device import Buffer
from tinygrad.dtype import DType, dtypes
from tinygrad.helpers import round_up
from tinygrad.tensor import Tensor
from tinygrad.uop.ops import UOp


def input_view(buffer: Buffer, shape: tuple[int, ...], dtype: DType, offset: int) -> Tensor:
  view = buffer.view(math.prod(shape), dtype, offset).ensure_allocated()
  return Tensor(UOp.from_buffer(view)).reshape(shape)


class BaseModelAdapter:
  def __init__(self, jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=False):
    self.jits = jits
    self.DEV = model_device
    self.QUEUE_DEV = queue_device
    self.WARP_DEV = warp_device
    self.chestnut = chestnut
    self.cam_w = cam_w
    self.cam_h = cam_h
    self._combined_model_type = 'supercombo'
    self._policy_slices_list = []
    self._has_on_policy = False
    self.policy_output_slices = {}
    self._policy_keys = []
    self.full_frames = {}
    self.nv12_info = get_nv12_info(cam_w, cam_h)
    self.is_native = False

  def _init_common(self):
    self._desire_key = next((key for key in getattr(self, 'numpy_inputs', {}) if key.startswith('desire')), 'desire')
    self._road_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' not in key), 'img')
    self._wide_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' in key), 'big_img')
    self.frame_buf_params = dict.fromkeys(getattr(self, '_vision_input_names', ['img', 'big_img']), self.nv12_info)

  def get_dummy_inputs(self):
    dummy_size = getattr(self, 'warp_frame_size', self.frame_copy_size if self.is_native else self.frame_buf_params[self._road_key][3])
    dummy_frames = {k: np.zeros(dummy_size, dtype=np.uint8) for k in self._vision_input_names}
    transforms = {k: np.eye(3, dtype=np.float32) for k in [self._road_key, self._wide_key] if k}
    dummy_inputs = {k: np.zeros(v.shape, dtype=v.dtype) for k, v in self.numpy_inputs.items() if k not in ['tfm', 'big_tfm', 'prev_feat']}
    return dummy_frames, transforms, dummy_inputs

  def _load_warp(self):
    if (self.cam_w, self.cam_h) in self.jits:
      self.warp_frame_size = self.nv12_info[3]
      return self.jits[(self.cam_w, self.cam_h)]

    warp_dir = Path(BASEDIR) / "openpilot/sunnypilot/modeld_v2/models"
    warp_name = f'{"big_" if self.chestnut else ""}driving_warp_{self.cam_w}x{self.cam_h}_tinygrad.pkl'
    with open(warp_dir / warp_name, 'rb') as f:
      warp_data = pickle.load(f)
      run_warp = warp_data['run']
      if 'input_specs' in warp_data and 'input_frame' in warp_data['input_specs']:
        self.warp_frame_size = warp_data['input_specs']['input_frame'][0][1]
      else:
        self.warp_frame_size = self.nv12_info[3] if self.chestnut else self.frame_copy_size
      return run_warp


class LegacyModelAdapter(BaseModelAdapter):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    metadata = self.jits['metadata']
    self.frame_copy_size = nv12_copy_size(*self.nv12_info[:3])

    if self.chestnut:
      self.WARP_DEV = self.DEV

    if 'model' in metadata:
      model_metadata = metadata.get('model', metadata)
      self.input_shapes = model_metadata['input_shapes']
      self.vision_output_slices = model_metadata['output_slices']
      self._vision_input_names = [key for key in self.input_shapes if 'img' in key]
      self.frame_skip = derive_frame_skip({}, self.input_shapes)
      self.input_queues, self.numpy_inputs = make_supercombo_input_queues(self.input_shapes, self.frame_skip, device=self.QUEUE_DEV)
      self.run_policy = self.jits['run_policy']
    else:
      self.run_policy = self.jits['run_policy']
      vision_metadata = metadata['vision']
      policy_keys = [k for k in metadata if k not in ('vision', 'warp_dev')]
      self._combined_model_type = 'split' if policy_keys == ['policy'] else 'multi_policy'
      self.vision_output_slices = vision_metadata['output_slices']
      self._policy_keys = policy_keys
      self._policy_slices_list = [metadata[k]['output_slices'] for k in policy_keys]
      self.policy_output_slices = self._policy_slices_list[0]
      self._has_on_policy = any('on' in k.lower() for k in policy_keys)
      self._vision_input_names = [key for key in vision_metadata['input_shapes'] if 'img' in key]
      first_policy_meta = metadata[policy_keys[0]]
      self.frame_skip = derive_frame_skip(vision_metadata['input_shapes'], first_policy_meta['input_shapes'])
      self.input_queues, self.numpy_inputs = make_split_input_queues(vision_metadata['input_shapes'], first_policy_meta['input_shapes'],
                                                                     self.frame_skip, device=self.QUEUE_DEV)

    self.run_warp = self._load_warp()
    self._init_common()
    if self.chestnut:
      self._init_chestnut_packed_buffers()
    else:
      yuv_size = self.frame_buf_params[self._road_key][3]
      frame_tensor = Tensor(np.zeros(yuv_size, dtype=np.uint8), device=self.WARP_DEV).contiguous().realize()
      big_frame_tensor = Tensor(np.zeros(yuv_size, dtype=np.uint8), device=self.WARP_DEV).contiguous().realize()
      self.run_warp(**{k: self.input_queues[k] for k in ('tfm', 'big_tfm')},
                    frame=frame_tensor, big_frame=big_frame_tensor)

  def _init_chestnut_packed_buffers(self):
    raw_npy_bytes = self.numpy_inputs['packed_npy_inputs'] if 'packed_npy_inputs' in self.numpy_inputs else self.input_queues['packed_npy_inputs'].numpy()
    self.npy_bytes_len = raw_npy_bytes.nbytes

    self.tfm_bytes_len = round_up(2 * 3 * 3 * 4, 128)
    self.npy_aligned_len = round_up(self.npy_bytes_len, 128)

    total_packed_size = self.tfm_bytes_len + self.npy_aligned_len + 2 * self.warp_frame_size
    self.packed_input = np.zeros(total_packed_size, dtype=np.uint8)
    self.input_host = Tensor(self.packed_input, device='NPY')._buffer()
    self.input_device = Tensor(self.packed_input, device=self.DEV)._buffer()

    self.tfm_host_view = np.ndarray((2, 3, 3), dtype=np.float32, buffer=self.packed_input, offset=0)
    frames_offset = self.tfm_bytes_len + self.npy_aligned_len
    self.frame_slots = {self._road_key: self.packed_input[frames_offset : frames_offset + self.warp_frame_size],
                        self._wide_key: self.packed_input[frames_offset + self.warp_frame_size : frames_offset + 2 * self.warp_frame_size]}

    self.device_tfm = input_view(self.input_device, (2, 3, 3), dtypes.float32, 0)
    self.input_queues['packed_npy_inputs'] = input_view(self.input_device, (self.npy_bytes_len // 4,), dtypes.float32, self.tfm_bytes_len)
    self.device_frames = input_view(self.input_device, (2, self.warp_frame_size), dtypes.uint8, frames_offset)

  def copy_frames(self, bufs):
    if self.chestnut:
      for key in self._vision_input_names:
        if key in bufs:
          data = bufs[key].data if hasattr(bufs[key], 'data') else bufs[key]
          np.copyto(self.frame_slots[key], np.frombuffer(data, dtype=np.uint8, count=self.warp_frame_size))
    else:
      for key in bufs.keys():
        data = bufs[key].data if hasattr(bufs[key], 'data') else bufs[key]
        ptr = np.frombuffer(data, dtype=np.uint8).ctypes.data
        yuv_size = self.frame_buf_params[key][3]
        cache_key = (key, ptr)
        if cache_key not in self._blob_cache:
          self._blob_cache[cache_key] = Tensor.from_blob(ptr, (yuv_size,), dtype='uint8', device=self.WARP_DEV)
        self.full_frames[key] = self._blob_cache[cache_key]

  def reset_warmup_buffers(self):
    for v in self.numpy_inputs.values():
      v[:] = 0
    if self.chestnut:
      self.packed_input[:] = 0
    else:
      self.full_frames.clear()
      self._blob_cache.clear()

  def run(self):
    if self.chestnut:
      self.tfm_host_view[0] = self.numpy_inputs['tfm']
      self.tfm_host_view[1] = self.numpy_inputs['big_tfm']

      if 'packed_npy_inputs' in self.numpy_inputs:
        self.packed_input[self.tfm_bytes_len : self.tfm_bytes_len + self.npy_bytes_len] = \
          self.numpy_inputs['packed_npy_inputs'].view(np.uint8)
      self.input_device.copy_from(self.input_host)
      warped = self.run_warp(input_frame=self.device_frames, M_inv=self.device_tfm)
    else:
      warped = self.run_warp(**{k: self.input_queues[k] for k in ('tfm', 'big_tfm')},
                             frame=self.full_frames[self._road_key], big_frame=self.full_frames[self._wide_key])
    return self.run_policy(**{k: self.input_queues[k] for k in POLICY_INPUTS if k in self.input_queues}, warped=warped)


class NativeTinygradAdapter(BaseModelAdapter):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.is_native = True
    self.input_specs = self.jits['input_specs']

    self.model_device = self.input_specs['new_img'][2]
    self.input_shapes = {name: (shape, np.dtype(dtype)) for name, (shape, dtype, _) in self.input_specs.items()}
    self.state_pairs = {name: f'next_{name}' for name in self.input_shapes if f'next_{name}' in self.jits['metadata']['output_shapes']}

    stride, y_height, uv_height, _ = get_nv12_info(self.cam_w, self.cam_h)
    self.frame_copy_size = stride * (y_height + uv_height)

    self.input_shapes_orig = self.jits['metadata']['input_shapes']
    self._vision_input_names = [k for k in self.input_shapes_orig if 'img' in k]
    self.vision_output_slices = pickle.loads(codecs.decode(self.jits['metadata']['metadata']['output_slices'].encode(), 'base64'))

    self.run_warp = self._load_warp()
    self._init_common()
    self.run_model = self.jits['run']

    warp_frame_size = getattr(self, 'warp_frame_size', self.nv12_info[3])
    self.input_queues = {name: Tensor(np.zeros(shape, dtype=dtype), device=self.model_device).realize()
                         for name, (shape, dtype) in self.input_shapes.items() if name in self.state_pairs}
    shapes = {'tfm': (2, 3, 3)} | {name: shape for name, (shape, _) in self.input_shapes.items()
                                   if name not in self.state_pairs and name != 'new_img'}
    npy_size = sum(round_up(math.prod(shape) * 4, 128) for shape in shapes.values())
    self.packed_input = np.zeros(npy_size + 2 * warp_frame_size, dtype=np.uint8)
    self.input_host = Tensor(self.packed_input, device='NPY')._buffer()
    self.input_device = Tensor(self.packed_input, device=self.model_device)._buffer()
    self.numpy_inputs = {}
    offset = 0
    for name, shape in shapes.items():
      self.numpy_inputs[name] = np.ndarray(shape, dtype=np.float32, buffer=self.packed_input, offset=offset)
      self.input_queues[name] = input_view(self.input_device, shape, dtypes.float32, offset)
      offset += round_up(self.numpy_inputs[name].nbytes, 128)
    self.frames = self.packed_input[npy_size:].reshape(2, warp_frame_size)
    self.warp_inputs = {'input_frame': input_view(self.input_device, self.frames.shape, dtypes.uint8, npy_size), 'M_inv': self.input_queues.pop('tfm')}

    self.outputs = {name: Tensor(np.zeros(shape, dtype=dtype), device=device).realize() for name, (shape, dtype, device) in self.jits['output_specs'].items()}
    for name, next_name in self.state_pairs.items():
      state = self.input_queues[name]
      self.outputs[next_name] = input_view(state._buffer(), state.shape, state.dtype, 0)

  def copy_frames(self, bufs):
    for i, key in enumerate(self._vision_input_names):
      if key in bufs:
        data = bufs[key].data if hasattr(bufs[key], 'data') else bufs[key]
        np.copyto(self.frames[i], np.frombuffer(data, dtype=np.uint8, count=self.warp_frame_size))

  def reset_warmup_buffers(self) -> None:
    self.packed_input[:] = 0
    for key in self.state_pairs:
      self.input_queues[key].assign(0).realize()

  def run(self):
    self.input_device.copy_from(self.input_host)
    self.input_queues['new_img'] = self.run_warp(**self.warp_inputs)
    self.run_model(output_buffers=self.outputs, **self.input_queues)
    return self.outputs['outputs']


def get_model_adapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=False):
  if 'input_specs' in jits:
    return NativeTinygradAdapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=chestnut)
  else:
    return LegacyModelAdapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=chestnut)
