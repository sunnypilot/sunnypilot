"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import codecs
import pickle
import numpy as np
from tinygrad.tensor import Tensor
from tinygrad.dtype import DType, dtypes
from tinygrad.device import Buffer
from tinygrad.uop.ops import UOp
from tinygrad.helpers import round_up
import math
from openpilot.common.basedir import BASEDIR
from pathlib import Path
from openpilot.sunnypilot.modeld_v2.helpers import DynamicTinygradUnpickler

def input_view(buffer: Buffer, shape: tuple[int, ...], dtype: DType, offset: int) -> Tensor:
  view = buffer.view(math.prod(shape), dtype, offset).ensure_allocated()
  return Tensor(UOp.from_buffer(view)).reshape(shape)

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
    self.is_native = False

  def _init_common(self):
    self._desire_key = next((key for key in getattr(self, 'numpy_inputs', {}) if key.startswith('desire')), 'desire')
    self._road_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' not in key), 'img')
    self._wide_key = next((key for key in getattr(self, '_vision_input_names', []) if 'big' in key), 'big_img')
    self.frame_buf_params = dict.fromkeys(getattr(self, '_vision_input_names', ['img', 'big_img']), self.nv12_info)

  def get_dummy_inputs(self):
    dummy_size = getattr(self, 'frame_copy_size', self.frame_buf_params[self._road_key][3])
    if getattr(self, 'is_run_model', True) is False:
      dummy_size = self.frame_buf_params[self._road_key][3]

    dummy_frames = {
      k: np.zeros(self.frame_views[k].size, dtype=np.uint8) if self.is_native else np.zeros(dummy_size, dtype=np.uint8)
      for k in self._vision_input_names
    }
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
      assert self.warp is not None and self.run_policy is not None
      warped = self.warp(**{k: self.input_queues[k] for k in WARP_INPUTS}, frame=self.full_frames[self._road_key], big_frame=self.full_frames[self._wide_key])
      raw_outputs = self.run_policy(**{k: self.input_queues[k] for k in POLICY_INPUTS if k in self.input_queues}, warped=warped)
      return raw_outputs


class NativeTinygradAdapter(BaseModelAdapter):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.is_native = True
    self.input_specs = self.jits['input_specs']
    self.packed_specs = self.jits['packed_specs']

    self.model_device = self.input_specs['new_img'][2]
    self.input_shapes = {name: (shape, np.dtype(dtype)) for name, (shape, dtype, _) in self.input_specs.items()}
    self.state_pairs = {name: f'next_{name}' for name in self.input_shapes if f'next_{name}' in self.jits['metadata']['output_shapes']}

    stride, y_height, uv_height, _ = get_nv12_info(self.cam_w, self.cam_h)
    self.frame_copy_size = stride * (y_height + uv_height)

    self.input_shapes_orig = self.jits['metadata']['input_shapes']
    self._vision_input_names = [k for k in self.input_shapes_orig if 'img' in k]
    self.vision_output_slices = pickle.loads(codecs.decode(self.jits['metadata']['metadata']['output_slices'].encode(), 'base64'))

    self.reset_warmup_buffers()
    self._init_common()

    warp_dir = Path(BASEDIR) / "openpilot/sunnypilot/modeld_v2/models"
    with open(warp_dir / f'{"big_" if self.chestnut else ""}driving_warp_{self.cam_w}x{self.cam_h}_tinygrad.pkl', 'rb') as f:
      self.run_warp = DynamicTinygradUnpickler(f).load()['run']
    self.run_model = self.jits['run']

    self.outputs = {name: Tensor(np.zeros(shape, dtype=dtype), device=device).realize() for name, (shape, dtype, device) in self.jits['output_specs'].items()}
    for name, next_name in self.state_pairs.items():
      state = self.input_queues[name]
      self.outputs[next_name] = input_view(state._buffer(), state.shape, state.dtype, 0)

  def copy_frames(self, bufs):
    for i, key in enumerate(self._vision_input_names):
      if key in bufs:
        data = bufs[key].data if hasattr(bufs[key], 'data') else bufs[key]
        np.copyto(self.frames[i], np.frombuffer(data, dtype=np.uint8, count=self.frame_copy_size))

  def reset_warmup_buffers(self) -> None:
    self.input_queues = {name: Tensor(np.zeros(shape, dtype=dtype), device=self.model_device).realize()
                         for name, (shape, dtype) in self.input_shapes.items() if name in self.state_pairs}
    shapes = {'tfm': (2, 3, 3)} | {name: shape for name, (shape, _) in self.input_shapes.items()
                                   if name not in self.state_pairs and name != 'new_img'}
    npy_size = sum(round_up(math.prod(shape) * 4, 128) for shape in shapes.values())
    self.packed_input = np.zeros(npy_size + 2 * self.frame_copy_size, dtype=np.uint8)
    self.input_host = Tensor(self.packed_input, device='NPY')._buffer()
    self.input_device = Tensor(self.packed_input, device=self.model_device)._buffer()
    self.numpy_inputs = {}
    offset = 0
    for name, shape in shapes.items():
      self.numpy_inputs[name] = np.ndarray(shape, dtype=np.float32, buffer=self.packed_input, offset=offset)
      self.input_queues[name] = input_view(self.input_device, shape, dtypes.float32, offset)
      offset += round_up(self.numpy_inputs[name].nbytes, 128)
    self.frames = self.packed_input[npy_size:].reshape(2, self.frame_copy_size)
    self.warp_inputs = {'input_frame': input_view(self.input_device, self.frames.shape, dtypes.uint8, npy_size), 'M_inv': self.input_queues.pop('tfm')}

    # Split tfm into tfm and big_tfm for modeld compatibility
    if 'tfm' in self.numpy_inputs and self.numpy_inputs['tfm'].shape == (2, 3, 3):
      real_tfm = self.numpy_inputs.pop('tfm')
      self.numpy_inputs['tfm'] = real_tfm[0]
      self.numpy_inputs['big_tfm'] = real_tfm[1]

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
