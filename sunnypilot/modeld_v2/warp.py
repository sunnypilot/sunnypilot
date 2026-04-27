import pickle
import time
import numpy as np
from pathlib import Path
from tinygrad.tensor import Tensor
from tinygrad.engine.jit import TinyJit
from tinygrad.device import Device

# https://github.com/tinygrad/tinygrad/issues/15682
from tinygrad.uop.ops import UOp, Ops
_orig = UOp.__reduce__
UOp.__reduce__ = lambda self: (UOp.unique, ()) if self.op is Ops.UNIQUE else _orig(self)
from typing import NamedTuple
from tinygrad.helpers import Context
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
from openpilot.common.transformations.camera import _ar_ox_fisheye, _os_fisheye

class NV12Frame(NamedTuple):
  cam_w: int
  cam_h: int
  stride: int
  y_height: int
  uv_height: int
  size: int

UV_SCALE_MATRIX = np.array([[0.5, 0, 0], [0, 0.5, 0], [0, 0, 1]], dtype=np.float32)
UV_SCALE_MATRIX_INV = np.linalg.inv(UV_SCALE_MATRIX)

CAMERA_CONFIGS = [
  (_ar_ox_fisheye.width, _ar_ox_fisheye.height),  # tici: 1928x1208
  (_os_fisheye.width, _os_fisheye.height),        # mici: 1344x760
]
from openpilot.common.transformations.model import MEDMODEL_INPUT_SIZE

MODELS_DIR = Path(__file__).parent / 'models'

UPSTREAM_BUFFER_LENGTH = 5

def warp_pkl_path(cam_w, cam_h):
  return MODELS_DIR / f'warp_{cam_w}x{cam_h}_tinygrad.pkl'

def warp_perspective_tinygrad(src_flat, M_inv, dst_shape, src_shape, stride_pad):
  w_dst, h_dst = dst_shape
  h_src, w_src = src_shape

  x = Tensor.arange(w_dst).reshape(1, w_dst).expand(h_dst, w_dst).reshape(-1)
  y = Tensor.arange(h_dst).reshape(h_dst, 1).expand(h_dst, w_dst).reshape(-1)

  # inline 3x3 matmul as elementwise to avoid reduce op (enables fusion with gather)
  src_x = M_inv[0, 0] * x + M_inv[0, 1] * y + M_inv[0, 2]
  src_y = M_inv[1, 0] * x + M_inv[1, 1] * y + M_inv[1, 2]
  src_w = M_inv[2, 0] * x + M_inv[2, 1] * y + M_inv[2, 2]

  src_x = src_x / src_w
  src_y = src_y / src_w

  x_nn_clipped = Tensor.round(src_x).clip(0, w_src - 1).cast('int')
  y_nn_clipped = Tensor.round(src_y).clip(0, h_src - 1).cast('int')
  idx = y_nn_clipped * (w_src + stride_pad) + x_nn_clipped

  return src_flat[idx]

def frames_to_tensor(frames, model_w, model_h):
  H = (frames.shape[0] * 2) // 3
  W = frames.shape[1]
  in_img1 = Tensor.cat(frames[0:H:2, 0::2],
                       frames[1:H:2, 0::2],
                       frames[0:H:2, 1::2],
                       frames[1:H:2, 1::2],
                       frames[H:H+H//4].reshape((H//2, W//2)),
                       frames[H+H//4:H+H//2].reshape((H//2, W//2)), dim=0).reshape((6, H//2, W//2))
  return in_img1

def make_frame_prepare(cam_w, cam_h, model_w, model_h):
  stride, y_height, uv_height, _ = get_nv12_info(cam_w, cam_h)
  uv_offset = stride * y_height
  stride_pad = stride - cam_w

  def frame_prepare_tinygrad(input_frame, M_inv):
    # UV_SCALE @ M_inv @ UV_SCALE_INV simplifies to elementwise scaling
    M_inv_uv = M_inv * Tensor([[1.0, 1.0, 0.5], [1.0, 1.0, 0.5], [2.0, 2.0, 1.0]])
    # deinterleave NV12 UV plane (UVUV... -> separate U, V)
    uv = input_frame[uv_offset:uv_offset + uv_height * stride].reshape(uv_height, stride)
    with Context(SPLIT_REDUCEOP=0):
      y = warp_perspective_tinygrad(input_frame[:cam_h*stride],
                                    M_inv, (model_w, model_h),
                                    (cam_h, cam_w), stride_pad).realize()
      u = warp_perspective_tinygrad(uv[:cam_h//2, :cam_w:2].flatten(),
                                    M_inv_uv, (model_w//2, model_h//2),
                                    (cam_h//2, cam_w//2), 0).realize()
      v = warp_perspective_tinygrad(uv[:cam_h//2, 1:cam_w:2].flatten(),
                                    M_inv_uv, (model_w//2, model_h//2),
                                    (cam_h//2, cam_w//2), 0).realize()
    yuv = y.cat(u).cat(v).reshape((model_h * 3 // 2, model_w))
    tensor = frames_to_tensor(yuv, model_w, model_h)
    return tensor
  return frame_prepare_tinygrad

def make_update_img_input(frame_prepare, model_w, model_h):
  def update_img_input_tinygrad(tensor, frame, M_inv):
    M_inv = M_inv.to(Device.DEFAULT)
    new_img = frame_prepare(frame, M_inv)
    updated_tensor = tensor[6:].cat(new_img, dim=0).contiguous()
    tensor.assign(updated_tensor)
    return updated_tensor, Tensor.cat(updated_tensor[:6], updated_tensor[-6:], dim=0).contiguous().reshape(1, 12, model_h//2, model_w//2)
  return update_img_input_tinygrad

def make_update_both_imgs(frame_prepare, model_w, model_h):
  update_img = make_update_img_input(frame_prepare, model_w, model_h)

  def update_both_imgs_tinygrad(calib_img_buffer, new_img, M_inv,
                                calib_big_img_buffer, new_big_img, M_inv_big):
    r1, r2 = update_img(calib_img_buffer, new_img, M_inv)
    w1, w2 = update_img(calib_big_img_buffer, new_big_img, M_inv_big)
    return r1, r2, w1, w2
  return update_both_imgs_tinygrad


def v2_warp_pkl_path(cam_w, cam_h, buffer_length):
  return MODELS_DIR / f'warp_{cam_w}x{cam_h}_b{buffer_length}_tinygrad.pkl'


def compile_v2_warp(cam_w, cam_h, buffer_length, model_w=MEDMODEL_INPUT_SIZE[0], model_h=MEDMODEL_INPUT_SIZE[1], pkl_path=None):
  _, _, _, yuv_size = get_nv12_info(cam_w, cam_h)
  img_buffer_shape = (buffer_length * 6, model_h // 2, model_w // 2)

  print(f"Compiling v2 warp for {cam_w}x{cam_h} buffer_length={buffer_length}...")

  frame_prepare = make_frame_prepare(cam_w, cam_h, model_w, model_h)
  update_both_imgs = make_update_both_imgs(frame_prepare, model_w, model_h)
  update_img_jit = TinyJit(update_both_imgs, prune=True)

  full_buffer = Tensor.zeros(img_buffer_shape, dtype='uint8').contiguous().realize()
  big_full_buffer = Tensor.zeros(img_buffer_shape, dtype='uint8').contiguous().realize()
  new_frame_np = np.random.randint(0, 256, yuv_size, dtype=np.uint8)
  new_big_frame_np = np.random.randint(0, 256, yuv_size, dtype=np.uint8)
  for i in range(10):
    img_inputs = [full_buffer,
                  Tensor.from_blob(new_frame_np.ctypes.data, (yuv_size,), dtype='uint8').realize(),
                  Tensor(Tensor.randn(3, 3).mul(8).realize().numpy(), device='NPY')]
    big_img_inputs = [big_full_buffer,
                      Tensor.from_blob(new_big_frame_np.ctypes.data, (yuv_size,), dtype='uint8').realize(),
                      Tensor(Tensor.randn(3, 3).mul(8).realize().numpy(), device='NPY')]
    inputs = img_inputs + big_img_inputs
    Device.default.synchronize()

    st = time.perf_counter()
    out = update_img_jit(*inputs)
    full_buffer, big_full_buffer = out[0].realize(), out[2].realize()
    mt = time.perf_counter()
    Device.default.synchronize()
    et = time.perf_counter()
    print(f"  [{i+1}/10] enqueue {(mt-st)*1e3:6.2f} ms -- total {(et-st)*1e3:6.2f} ms")

  if pkl_path is None:
    pkl_path = v2_warp_pkl_path(cam_w, cam_h, buffer_length)
  with open(pkl_path, "wb") as f:
    pickle.dump(update_img_jit, f)
  print(f"  Saved to {pkl_path}")


class Warp:
  def __init__(self, buffer_length=2, model_w=MEDMODEL_INPUT_SIZE[0], model_h=MEDMODEL_INPUT_SIZE[1]):
    self.buffer_length = buffer_length
    self.model_w = model_w
    self.model_h = model_h
    self.img_buffer_shape = (buffer_length * 6, model_h // 2, model_w // 2)

    self.jit_cache = {}
    self.full_buffers = {k: Tensor.zeros(self.img_buffer_shape, dtype='uint8').contiguous().realize() for k in ['img', 'big_img']}
    self._blob_cache: dict[int, Tensor] = {}
    self._nv12_cache: dict[tuple[int, int], int] = {}
    self.transforms_np = {k: np.zeros((3, 3), dtype=np.float32) for k in ['img', 'big_img']}
    self.transforms = {k: Tensor(v, device='NPY').realize() for k, v in self.transforms_np.items()}

  def process(self, bufs, transforms):
    if not bufs:
      return {}
    road = next(n for n in bufs if 'big' not in n)
    wide = next(n for n in bufs if 'big' in n)
    cam_w, cam_h = bufs[road].width, bufs[road].height
    key = (cam_w, cam_h)

    if key not in self.jit_cache:
      v2_pkl = v2_warp_pkl_path(cam_w, cam_h, self.buffer_length)
      if v2_pkl.exists():
        with open(v2_pkl, 'rb') as f:
          self.jit_cache[key] = pickle.load(f)
      elif self.buffer_length == UPSTREAM_BUFFER_LENGTH:
        upstream_pkl = warp_pkl_path(cam_w, cam_h)
        if upstream_pkl.exists():
          with open(upstream_pkl, 'rb') as f:
            self.jit_cache[key] = pickle.load(f)
      if key not in self.jit_cache:
        frame_prepare = make_frame_prepare(cam_w, cam_h, self.model_w, self.model_h)
        update_both_imgs = make_update_both_imgs(frame_prepare, self.model_w, self.model_h)
        self.jit_cache[key] = TinyJit(update_both_imgs, prune=True)

    if key not in self._nv12_cache:
      self._nv12_cache[key] = get_nv12_info(cam_w, cam_h)[3]
    yuv_size = self._nv12_cache[key]

    road_ptr = bufs[road].data.ctypes.data
    wide_ptr = bufs[wide].data.ctypes.data
    if road_ptr not in self._blob_cache:
      self._blob_cache[road_ptr] = Tensor.from_blob(road_ptr, (yuv_size,), dtype='uint8')
    if wide_ptr not in self._blob_cache:
      self._blob_cache[wide_ptr] = Tensor.from_blob(wide_ptr, (yuv_size,), dtype='uint8')
    road_blob = self._blob_cache[road_ptr]
    wide_blob = self._blob_cache[wide_ptr] if wide_ptr != road_ptr else Tensor.from_blob(wide_ptr, (yuv_size,), dtype='uint8')
    np.copyto(self.transforms_np['img'], transforms[road].reshape(3, 3))
    np.copyto(self.transforms_np['big_img'], transforms[wide].reshape(3, 3))

    Device.default.synchronize()
    res = self.jit_cache[key](
      self.full_buffers['img'], road_blob, self.transforms['img'],
      self.full_buffers['big_img'], wide_blob, self.transforms['big_img'],
    )
    self.full_buffers['img'], out_road = res[0].realize(), res[1].realize()
    self.full_buffers['big_img'], out_wide = res[2].realize(), res[3].realize()

    return {road: out_road, wide: out_wide}


if __name__ == "__main__":
  for cam_w, cam_h in CAMERA_CONFIGS:
    compile_v2_warp(cam_w, cam_h, 5, pkl_path=warp_pkl_path(cam_w, cam_h))
    for bl in [2, 5]:
      compile_v2_warp(cam_w, cam_h, bl)
