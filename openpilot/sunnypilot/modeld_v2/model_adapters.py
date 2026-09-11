"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
from tinygrad.tensor import Tensor

from openpilot.sunnypilot.modeld_v2.stock_dependencies import MODELD_INPUTS, make_input_queues as make_stock_input_queues
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
from openpilot.sunnypilot.modeld_v2.compile_modeld import (derive_frame_skip, make_split_input_queues, make_supercombo_input_queues,
                                                           WARP_INPUTS, POLICY_INPUTS, nv12_copy_size)


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
    self._blob_cache = {}
    self.frame_buffers = {}
    self.frame_views = {}
    self.nv12_info = get_nv12_info(cam_w, cam_h)

  def _init_common(self):
    self._desire_key = next((key for key in getattr(self, 'numpy_inputs', {}) if key.startswith('desire')), 'desire')
    self._road_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' not in key), 'img')
    self._wide_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' in key), 'big_img')
    self.frame_buf_params = dict.fromkeys(getattr(self, '_vision_input_names', ['img', 'big_img']), self.nv12_info)

  def get_dummy_inputs(self):
    dummy_size = getattr(self, 'frame_copy_size', self.frame_buf_params[self._road_key][3])
    if getattr(self, 'is_run_model', True) is False:
      dummy_size = self.frame_buf_params[self._road_key][3]

    dummy_frames = {k: np.zeros(dummy_size, dtype=np.uint8) for k in self._vision_input_names}
    transforms = {k: np.eye(3, dtype=np.float32) for k in [self._road_key, self._wide_key] if k}
    dummy_inputs = {k: np.zeros(v.shape, dtype=v.dtype) for k, v in self.numpy_inputs.items() if k not in ['tfm', 'big_tfm', 'prev_feat']}
    return dummy_frames, transforms, dummy_inputs


class LegacyModelAdapter(BaseModelAdapter):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    metadata = self.jits['metadata']
    self.is_run_model = 'run_model' in self.jits
    self.frame_copy_size = nv12_copy_size(*self.nv12_info[:3])

    if self.is_run_model or 'model' in metadata:
      model_metadata = metadata.get('model', metadata)
      self.input_shapes = model_metadata['input_shapes']
      self.vision_output_slices = model_metadata['output_slices']
      self._vision_input_names = [key for key in self.input_shapes if 'img' in key]
      self.frame_skip = derive_frame_skip({}, self.input_shapes)

      if self.is_run_model:
        self.input_queues, self.numpy_inputs, self.frame_buffers = make_stock_input_queues(
          self.input_shapes, self.frame_skip, device=self.DEV, frame_copy_size=self.frame_copy_size)
        self.frame_views, self.npy = self.frame_buffers, self.numpy_inputs
        self.run_model, self.run_policy, self.warp = self.jits['run_model'][(self.cam_w, self.cam_h)], None, None
      else:
        self.input_queues, self.numpy_inputs = make_supercombo_input_queues(self.input_shapes, self.frame_skip, device=self.QUEUE_DEV)
        self.run_model, self.run_policy, self.warp = None, self.jits['run_policy'], self.jits[(self.cam_w, self.cam_h)]
    else:
      self.run_model, self.run_policy, self.warp = None, self.jits['run_policy'], self.jits[(self.cam_w, self.cam_h)]
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
      self.input_queues, self.numpy_inputs = make_split_input_queues(vision_metadata['input_shapes'],
                                                                     first_policy_meta['input_shapes'],
                                                                     self.frame_skip, device=self.QUEUE_DEV)

    self._init_common()
    if self.warp is not None:
      self.full_frames = {k: Tensor(np.zeros(self.nv12_info[3], dtype=np.uint8), device=self.WARP_DEV).contiguous().realize() for k in self._vision_input_names}
      self.warp(**{k: self.input_queues[k] for k in WARP_INPUTS}, frame=self.full_frames[self._road_key], big_frame=self.full_frames[self._wide_key])

  def copy_frames(self, bufs):
    if getattr(self, 'is_run_model', True):
      for key, buf in bufs.items():
        data = buf.data if hasattr(buf, 'data') else buf
        np.copyto(self.frame_buffers[key], np.frombuffer(data, dtype=np.uint8, count=self.frame_copy_size))
    else:
      for key, buf in bufs.items():
        ptr = np.frombuffer(buf.data, dtype=np.uint8).ctypes.data
        cache_key = (key, ptr)
        if cache_key not in self._blob_cache:
          self._blob_cache[cache_key] = Tensor.from_blob(ptr, (self.frame_buf_params[key][3],), dtype='uint8', device=self.WARP_DEV)
        self.full_frames[key] = self._blob_cache[cache_key]

  def reset_warmup_buffers(self):
    if getattr(self, 'is_run_model', True):
      self.input_queues, self.numpy_inputs, self.frame_buffers = make_stock_input_queues(
        self.input_shapes, self.frame_skip, device=self.DEV, frame_copy_size=self.frame_copy_size)
      self.frame_views = self.frame_buffers
      self.npy = self.numpy_inputs
    else:
      for v in self.numpy_inputs.values():
        v[:] = 0
      self.full_frames.clear()
      self._blob_cache.clear()

  def run(self):
    if self.run_model is not None:
      outs, = self.run_model(**{k: self.input_queues[k] for k in MODELD_INPUTS})
      return outs
    else:
      warped = self.warp(**{k: self.input_queues[k] for k in WARP_INPUTS}, frame=self.full_frames[self._road_key], big_frame=self.full_frames[self._wide_key])
      raw_outputs = self.run_policy(**{k: self.input_queues[k] for k in POLICY_INPUTS if k in self.input_queues}, warped=warped)
      return raw_outputs


class NativeTinygradAdapter(BaseModelAdapter):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.input_specs = self.jits['input_specs'][(self.cam_w, self.cam_h)]
    self.npy_shapes = self.jits['npy_shapes']
    self.run_model = self.jits['run_model'][(self.cam_w, self.cam_h)]
    self.vision_output_slices = self.jits['metadata']['model']['output_slices']

    self._vision_input_names = ['img', 'big_img']

    self.reset_warmup_buffers()
    self._init_common()

  def copy_frames(self, bufs):
    for key, buf in bufs.items():
      data = buf.data if hasattr(buf, 'data') else buf
      if key in self.frame_views:
        np.copyto(self.frame_views[key], np.frombuffer(data, dtype=np.uint8, count=self.frame_copy_size))

  def reset_warmup_buffers(self) -> None:
    buffers = {name: np.zeros(shape, dtype=dtype) for name, (shape, dtype, _) in self.input_specs.items()}
    self.input_queues = {name: Tensor(buffers[name], device=device).realize() for name, (_, _, device) in self.input_specs.items()}

    sizes = [int(np.prod(shape)) for shape in self.npy_shapes.values()]
    packed = buffers['packed_npy_inputs']
    npy_size = sum(sizes) * np.dtype(np.float32).itemsize

    self.numpy_inputs = {name: v.reshape(shape) for (name, shape), v in
                zip(self.npy_shapes.items(), np.split(packed[:npy_size].view(np.float32), np.cumsum(sizes[:-1])), strict=True)}

    self.frame_copy_size = (packed.size - npy_size) // 2
    self.frame_views = {'img': packed[npy_size:npy_size+self.frame_copy_size],
                        'big_img': packed[npy_size+self.frame_copy_size:]}

  def run(self):
    outs, = self.run_model(**self.input_queues)
    return outs


def get_model_adapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=False):
  if 'input_specs' in jits:
    return NativeTinygradAdapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=chestnut)
  else:
    return LegacyModelAdapter(jits, cam_w, cam_h, model_device, queue_device, warp_device, chestnut=chestnut)
