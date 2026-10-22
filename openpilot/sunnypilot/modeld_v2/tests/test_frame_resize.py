"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import unittest

import numpy as np

from openpilot.sunnypilot.modeld_v2.frame_resize import FrameResize


class TestFrameResize(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.resizer = FrameResize()

  def setUp(self):
    self.source = np.full(self.resizer.source_copy_size, 255, dtype=np.uint8)
    self.destination = np.empty(self.resizer.target_copy_size, dtype=np.uint8)

  def test_sampling_and_padding(self):
    source_y = self.source[:2490368].reshape(1216, 2048)
    source_uv = self.source[2490368:].reshape(608, 2048)
    source_y[:1208, :1928] = (3 * np.arange(1208)[:, None] + 5 * np.arange(1928)) % 251
    source_uv[:604, :1928:2] = (7 * np.arange(604)[:, None] + 11 * np.arange(964)) % 113
    source_uv[:604, 1:1928:2] = 128 + (13 * np.arange(604)[:, None] + 17 * np.arange(964)) % 113
    original = self.source.copy()

    self.resizer.resize(self.source, self.destination)

    target_y = self.destination[:1081344].reshape(768, 1408)
    target_uv = self.destination[1081344:].reshape(384, 1408)
    y_rows, y_cols = ((2 * np.arange(760) + 1) * 1208) // (2 * 760), ((2 * np.arange(1344) + 1) * 1928) // (2 * 1344)
    uv_rows, uv_cols = ((2 * np.arange(380) + 1) * 604) // (2 * 380), ((2 * np.arange(672) + 1) * 964) // (2 * 672)
    np.testing.assert_array_equal(target_y[:760, :1344], (3 * y_rows[:, None] + 5 * y_cols) % 251)
    np.testing.assert_array_equal(target_uv[:380, :1344:2], (7 * uv_rows[:, None] + 11 * uv_cols) % 113)
    np.testing.assert_array_equal(target_uv[:380, 1:1344:2], 128 + (13 * uv_rows[:, None] + 17 * uv_cols) % 113)
    self.assertFalse(np.any(self.destination == 255))
    np.testing.assert_array_equal(self.source, original)
    uv_pairs = target_uv.reshape(384, 704, 2)
    np.testing.assert_array_equal(target_y[:, 1344:], np.broadcast_to(target_y[:, 1343:1344], (768, 64)))
    np.testing.assert_array_equal(target_y[760:], np.broadcast_to(target_y[759:760], (8, 1408)))
    np.testing.assert_array_equal(uv_pairs[:, 672:], np.broadcast_to(uv_pairs[:, 671:672], (384, 32, 2)))
    np.testing.assert_array_equal(uv_pairs[380:], np.broadcast_to(uv_pairs[379:380], (4, 704, 2)))

  def test_matches_numpy_gather(self):
    self.source[:] = np.random.default_rng(0).integers(0, 256, self.source.size, dtype=np.uint8)
    x = ((2 * np.minimum(np.arange(1408), 1343) + 1) * 1928) // (2 * 1344)
    y = ((2 * np.minimum(np.arange(768), 759) + 1) * 1208) // (2 * 760)
    y_indices = y[:, None] * 2048 + x
    uv_bytes = np.arange(1408)
    x = ((2 * np.minimum(uv_bytes // 2, 671) + 1) * 964) // (2 * 672) * 2 + uv_bytes % 2
    y = ((2 * np.minimum(np.arange(384), 379) + 1) * 604) // (2 * 380)
    uv_indices = 2490368 + y[:, None] * 2048 + x
    indices = np.concatenate((y_indices.ravel(), uv_indices.ravel()))

    self.resizer.resize(memoryview(self.source).toreadonly(), self.destination)
    np.testing.assert_array_equal(self.destination, np.take(self.source, indices, mode='clip'))

  def test_rejects_invalid_destinations(self):
    size = self.resizer.target_copy_size
    readonly = self.destination.view()
    readonly.setflags(write=False)
    for destination in (self.destination[:-1], np.empty(size + 1, dtype=np.uint8), self.destination.reshape(2, -1),
                        self.destination.view(np.int8), np.empty(2 * size, dtype=np.uint8)[::2], readonly):
      with self.subTest(shape=destination.shape, dtype=destination.dtype, flags=str(destination.flags)):
        original = destination.copy()
        with self.assertRaisesRegex(ValueError, "destination must be"):
          self.resizer.resize(self.source, destination)
        np.testing.assert_array_equal(destination, original)

  def test_native_rejects_invalid_buffers_before_writing(self):
    self.destination.fill(201)
    src, dst = self.source.ctypes.data, self.destination.ctypes.data
    src_size, dst_size = self.source.size, self.destination.size
    for args in ((None, src_size, dst, dst_size), (src, src_size, None, dst_size),
                 (src, src_size - 1, dst, dst_size), (src, src_size, dst, dst_size - 1),
                 (src, src_size, dst, dst_size + 1)):
      with self.subTest(args=args):
        self.assertNotEqual(self.resizer._resize(*args), 0)
        self.assertTrue(np.all(self.source == 255))
        self.assertTrue(np.all(self.destination == 201))

    overlap = np.full(src_size + 1, 255, dtype=np.uint8)
    for source, destination in ((overlap[:src_size], overlap[1:dst_size + 1]), (overlap[1:], overlap[:dst_size])):
      with self.assertRaisesRegex(ValueError, "overlapping buffers"):
        self.resizer.resize(source, destination)
      self.assertTrue(np.all(overlap == 255))

  def test_writes_only_supplied_packed_frame_views(self):
    size = self.resizer.target_copy_size
    packed = np.full(65 + 2 * size + 32, 201, dtype=np.uint8)
    road = packed[65:65 + size]
    wide = packed[65 + size:65 + 2 * size]
    self.source.fill(7)
    self.resizer.resize(self.source, road)
    self.source.fill(9)
    self.resizer.resize(self.source, wide)

    self.assertTrue(np.all(packed[:65] == 201))
    self.assertTrue(np.all(road == 7))
    self.assertTrue(np.all(wide == 9))
    self.assertTrue(np.all(packed[-32:] == 201))
