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
    self.assertTrue(self.resizer._indices.flags['W'])
    source_y = self.source[:2490368].reshape(1216, 2048)
    source_uv = self.source[2490368:].reshape(608, 2048)
    source_y[:1208, :1928] = (3 * np.arange(1208)[:, None] + 5 * np.arange(1928)) % 251
    source_uv[:604, :1928:2] = (7 * np.arange(604)[:, None] + 11 * np.arange(964)) % 113
    source_uv[:604, 1:1928:2] = 128 + (13 * np.arange(604)[:, None] + 17 * np.arange(964)) % 113
    original = self.source.copy()

    self.resizer.resize(self.source, self.destination)

    target_y = self.destination[:1081344].reshape(768, 1408)
    target_uv = self.destination[1081344:].reshape(384, 1408)
    y_rows, y_cols = np.arange(760) * 1208 // 760, np.arange(1344) * 1928 // 1344
    uv_rows, uv_cols = np.arange(380) * 604 // 380, np.arange(672) * 964 // 672
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

  def test_writes_only_supplied_packed_frame_views(self):
    size = self.resizer.target_copy_size
    packed = np.full(64 + 2 * size + 32, 201, dtype=np.uint8)
    road = packed[64:64 + size]
    wide = packed[64 + size:64 + 2 * size]
    self.source.fill(7)
    self.resizer.resize(self.source, road)
    self.source.fill(9)
    self.resizer.resize(self.source, wide)

    self.assertTrue(np.all(packed[:64] == 201))
    self.assertTrue(np.all(road == 7))
    self.assertTrue(np.all(wide == 9))
    self.assertTrue(np.all(packed[-32:] == 201))
