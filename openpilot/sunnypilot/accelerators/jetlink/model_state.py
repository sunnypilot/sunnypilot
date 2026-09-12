"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

A ModelState whose policy runs on the Jetson.

Everything that touches the car stays on the comma: cameras, calibration, the
warp, the parser, controlsd, panda, CAN. The Jetson is a pure function, warped
frames and context in, 18452 floats out, and holds no control state.

The split is at `run_policy`. The warp stays on the comma's GPU: its input is a
2 MB camera buffer already there and its output the 393 KB the link carries
anyway. The history queues live on the Jetson, shipping them would cost ~10 MB
a frame instead of ~0.5 MB. Upstream fused warp and policy into one JIT, so
scons compiles a standalone warp at build time; see warp_cache.
"""
from __future__ import annotations

import os
import time
from collections.abc import Callable

import numpy as np
from tinygrad.device import Device
from tinygrad.tensor import Tensor

from msgq.visionipc import VisionBuf

from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.modeld.parse_model_outputs import Parser
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
from openpilot.sunnypilot.accelerators.jetlink import warp_cache
from openpilot.sunnypilot.modeld_v2.modeld_base import ModelStateBase

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
SLOW_FRAME = 0.05  # the full 20 Hz budget, not just the largest outliers


class JetlinkModelState(ModelStateBase):
  """Duck-types selfdrive.modeld.modeld.ModelState."""

  prev_desire: np.ndarray  # for tracking the rising edge of the pulse

  def __init__(self, cam_w: int, cam_h: int, client, spec, small=None, warp=None):
    ModelStateBase.__init__(self)
    self.client = client
    self.spec = spec
    # not chestnut hardware, but the same role: modelV2.big, the UI and the
    # model manager key off this flag
    self.chestnut = True

    # make_warp is sized in NV12 pixels and the model input after deinterleave,
    # so img (1, 12, 128, 256) is a 512x256 warp, MEDMODEL_INPUT_SIZE
    img_h, img_w = spec.input_shapes['img'][2:]
    # a warm warp is handed in when there is one: the first call costs ~2 s and
    # this can run on modeld's frame thread (warp_cache.warm)
    self.warp = warp if warp is not None else warp_cache.load_warp(cam_w, cam_h, img_w * 2, img_h * 2)

    # the small ModelState is only a geometry cross-check now
    small_img = small.input_shapes['img'] if small is not None else None
    if small_img is not None and tuple(small_img[2:]) != tuple(spec.input_shapes['img'][2:]):
      raise RuntimeError(f"warp geometry {small_img[2:]} does not match the large model "
                         + f"{spec.input_shapes['img'][2:]}; a large-model warp JIT is needed")

    self.input_shapes = spec.input_shapes
    self.output_slices = spec.output_slices
    self.vision_input_names = [k for k in spec.input_shapes if 'img' in k]
    # from the spec, not ModelConstants: the server derives its history stride
    # from the same field
    self.frame_skip = spec.frame_skip

    # the warp's own two inputs stay separate NPY tensors; everything past the
    # warp is the server's. Writing the numpy array is what feeds the JIT
    self.npy = {'tfm': np.zeros((3, 3), dtype=np.float32),
                'big_tfm': np.zeros((3, 3), dtype=np.float32)}
    self.warp_inputs = {k: Tensor(v, device='NPY').realize() for k, v in self.npy.items()}

    # compile_modeld.make_input_queues' packed_npy_inputs, minus the GPU queues
    # the server owns
    self.packed = np.zeros(spec.packed_nelem, dtype=np.float32)
    views = np.split(self.packed, np.cumsum(spec.packed_sizes[:-1]))
    self.npy.update({k: v.reshape(s) for (k, s), v in
                     zip(spec.packed_shapes.items(), views, strict=True)})

    # read once: it must be the device the cached JIT was compiled against
    self.warp_dev = Device.DEFAULT
    self.prev_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
    self.parser = Parser()
    self.frame_buf_params = {k: get_nv12_info(cam_w, cam_h) for k in ('img', 'big_img')}
    self.full_frames: dict[str, Tensor] = {}
    self._blob_cache: dict[tuple[str, int], Tensor] = {}
    self._need_reset = True
    self._frame_id = 0

  def slice_outputs(self, model_outputs: np.ndarray, output_slices: dict[str, slice]) -> dict[str, np.ndarray]:
    return {k: model_outputs[np.newaxis, v] for k, v in output_slices.items()}

  def run(self, bufs: dict[str, VisionBuf], transforms: dict[str, np.ndarray],
          inputs: dict[str, np.ndarray], after_enqueue: Callable[[], None] | None = None) -> dict[str, np.ndarray]:
    for key in bufs.keys():
      ptr = np.frombuffer(bufs[key].data, dtype=np.uint8).ctypes.data
      yuv_size = self.frame_buf_params[key][3]
      cache_key = (key, ptr)
      if cache_key not in self._blob_cache:
        self._blob_cache[cache_key] = Tensor.from_blob(ptr, (yuv_size,), dtype='uint8', device=self.warp_dev)
      self.full_frames[key] = self._blob_cache[cache_key]

    # Model decides when action is completed, so desire input is just a pulse triggered on rising edge
    inputs['desire_pulse'][0] = 0
    self.npy['desire'][:] = np.where(inputs['desire_pulse'] - self.prev_desire > .99, inputs['desire_pulse'], 0)
    self.prev_desire[:] = inputs['desire_pulse']
    self.npy['traffic_convention'][:] = inputs['traffic_convention']
    self.npy['action_t'][:] = inputs['action_t']
    self.npy['tfm'][:, :] = transforms['img'][:, :]
    self.npy['big_tfm'][:, :] = transforms['big_img'][:, :]

    t0 = time.perf_counter()
    warped = warp_cache.call_warp(self.warp, **self.warp_inputs,
                                  frame=self.full_frames['img'], big_frame=self.full_frames['big_img'])
    t1 = time.perf_counter()
    # .data() rather than .numpy(): same ~2.5 ms mean (a write-combined GPU
    # mapping read), but no per-frame allocation and no 52 ms outlier
    data = warped.data()
    t2 = time.perf_counter()

    self._frame_id += 1
    seq = self.client.infer_begin(data, self.packed, self._frame_id,
                                  reset=self._need_reset, want_state=after_enqueue is not None)
    t3 = time.perf_counter()
    self._need_reset = False
    # publish health while the Jetson works
    if after_enqueue is not None:
      after_enqueue()
    callback_done = time.perf_counter()
    # blocks like a chestnut frame; a long frame is a dropped camera frame.
    # Only a stall past the client's deadline raises, into the joining
    # state's demotion to the small model
    model_output = self.client.infer_end(seq)
    t4 = time.perf_counter()
    # a frame past the budget is a dropped camera frame and three in a row
    # are modeldLagging; send against reply says which end it was
    if self._frame_id <= 3 or t4 - t0 > SLOW_FRAME:
      # persisted on the comma so a drive can separate server execution from
      # receive stalls once the Jetson is offline; server total excludes USB
      gpu_us, queue_us, total_us = self.client.last_timings
      cloudlog.warning("jetlink: frame %d warp %.1f data %.1f send %.1f reply %.1f ms; "
                       + "server gpu %.1f queue %.1f total %.1f ms", self._frame_id,
                       (t1 - t0) * 1e3, (t2 - t1) * 1e3, (t3 - t2) * 1e3, (t4 - t3) * 1e3,
                       gpu_us / 1e3, queue_us / 1e3, total_us / 1e3)
      receive = getattr(self.client.t, 'last_receive', {})
      cloudlog.warning("jetlink: frame %d health %.1f wait %.1f ms; "
                       + "ffs maxima prepare %.1f read_wait %.1f handoff %.1f ms", self._frame_id,
                       (callback_done - t3) * 1e3, (t4 - callback_done) * 1e3,
                       receive.get('prepare', 0.0) * 1e3, receive.get('read_wait', 0.0) * 1e3,
                       receive.get('handoff', 0.0) * 1e3)

    # the non-finite check runs on the server (Status.NOT_FINITE -> LinkError),
    # so modeld's big->small failover fires as it does for a chestnut
    outputs_dict = self.parser.parse_outputs(self.slice_outputs(model_output, self.output_slices))
    self.npy['prev_feat'][:] = model_output[self.output_slices['hidden_state']]
    if SEND_RAW_PRED:
      outputs_dict['raw_pred'] = model_output.copy()
    return outputs_dict

  def close(self) -> None:
    """Let go of the link; modeld calls this on a big model that finished loading too late."""
    self.client.close()

  def warmup(self) -> None:
    dummy_frames = {k: np.zeros(self.frame_buf_params[k][3], dtype=np.uint8) for k in self.vision_input_names}
    eye = np.eye(3, dtype=np.float32)
    dims = {'desire_pulse': ModelConstants.DESIRE_LEN, 'traffic_convention': 2, 'action_t': 2}
    self.run(dummy_frames, dict.fromkeys(self.vision_input_names, eye),
             {k: np.zeros(v, dtype=np.float32) for k, v in dims.items()})
    # drop the warm-up frame from both ends' history
    self.packed[:] = 0
    self.prev_desire[:] = 0
    self.full_frames.clear()
    self._blob_cache.clear()
    self._need_reset = True
    cloudlog.warning("jetlink: warmup complete")
