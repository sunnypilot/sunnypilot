import os
os.environ['DEV'] = 'CPU'
import pytest
import numpy as np
from openpilot.selfdrive.modeld.compile_warp import get_nv12_info, CAMERA_CONFIGS
from openpilot.sunnypilot.modeld_v2.warp import Warp, MODEL_W, MODEL_H

VISION_NAME_PAIRS = [  # needed to account for supercombos input_imgs
  ('img', 'big_img'),
  ('input_imgs', 'big_input_imgs'),
]


class MockVisionBuf:
  def __init__(self, w, h):
    self.width = w
    self.height = h
    _, _, _, yuv_size = get_nv12_info(w, h)
    self.data = np.zeros(yuv_size, dtype=np.uint8)


@pytest.mark.parametrize("buffer_length", [2, 5])
def test_warp_initialization(buffer_length):
  warp = Warp(buffer_length)
  assert warp.buffer_length == buffer_length
  assert warp.img_buffer_shape == (buffer_length * 6, MODEL_H // 2, MODEL_W // 2)


@pytest.mark.parametrize("buffer_length", [2, 5])
@pytest.mark.parametrize("cam_w, cam_h", CAMERA_CONFIGS)
@pytest.mark.parametrize("road, wide", VISION_NAME_PAIRS)
def test_warp_process(buffer_length, cam_w, cam_h, road, wide):
  warp = Warp(buffer_length)
  mock_buf = MockVisionBuf(cam_w, cam_h)
  transform = np.eye(3, dtype=np.float32).flatten()
  bufs = {road: mock_buf, wide: mock_buf}
  transforms = {road: transform, wide: transform}

  out = warp.process(bufs, transforms)
  assert isinstance(out, dict)
  assert road in out and wide in out
  assert out[road].shape == (1, 12, MODEL_H // 2, MODEL_W // 2)
  assert out[wide].shape == (1, 12, MODEL_H // 2, MODEL_W // 2)

  key = (cam_w, cam_h)
  assert key in warp.jit_cache

  out2 = warp.process(bufs, transforms)
  assert out2[road].shape == out[road].shape


@pytest.mark.parametrize("road, wide", VISION_NAME_PAIRS)
def test_warp_buffer_shift(road, wide):
  warp = Warp(2)
  cam_w, cam_h = CAMERA_CONFIGS[1]
  transform = np.eye(3, dtype=np.float32).flatten()

  buf1 = MockVisionBuf(cam_w, cam_h)
  buf1.data[0] = 255
  bufs1 = {road: buf1, wide: buf1}
  transforms = {road: transform, wide: transform}
  out1 = warp.process(bufs1, transforms)
  road1 = out1[road].numpy().copy()

  buf2 = MockVisionBuf(cam_w, cam_h)
  buf2.data[0] = 128
  bufs2 = {road: buf2, wide: buf2}
  out2 = warp.process(bufs2, transforms)
  assert not np.array_equal(road1, out2[road].numpy())


@pytest.mark.parametrize("buffer_length", [2, 5])
@pytest.mark.parametrize("road, wide", VISION_NAME_PAIRS)
def test_warp_buffer_accumulation(buffer_length, road, wide):
  warp = Warp(buffer_length)
  cam_w, cam_h = CAMERA_CONFIGS[0]
  transform = np.eye(3, dtype=np.float32).flatten()
  transforms = {road: transform, wide: transform}
  outputs = []

  for i in range(buffer_length + 1):
    buf = MockVisionBuf(cam_w, cam_h)
    buf.data[:] = i * 10
    out = warp.process({road: buf, wide: buf}, transforms)
    outputs.append(out[road].numpy().copy())

  assert warp.full_buffers['img'].shape == (buffer_length * 6, MODEL_H // 2, MODEL_W // 2)
  for i in range(1, len(outputs)):
    assert not np.array_equal(outputs[i - 1], outputs[i])


def test_warp_different_cameras_same_instance():
  warp = Warp(2)
  transform = np.eye(3, dtype=np.float32).flatten()

  buf1 = MockVisionBuf(*CAMERA_CONFIGS[0])
  warp.process({'img': buf1, 'big_img': buf1}, {'img': transform, 'big_img': transform})
  assert len(warp.jit_cache) == 1

  buf2 = MockVisionBuf(*CAMERA_CONFIGS[1])
  warp.process({'img': buf2, 'big_img': buf2}, {'img': transform, 'big_img': transform})
  assert len(warp.jit_cache) == 2
