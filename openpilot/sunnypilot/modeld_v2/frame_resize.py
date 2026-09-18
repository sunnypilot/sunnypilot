"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections.abc import Buffer

import numpy as np

from openpilot.system.camerad.cameras.nv12_info import get_nv12_info

SOURCE_SIZE = (1928, 1208)
TARGET_SIZE = (1344, 760)


class FrameResize:
  """Fixed NV12 point sampling: center-anchored floor((2*dst + 1) * source / (2 * target)), with edge-filled padding."""

  def __init__(self):
    source_w, source_h = SOURCE_SIZE
    target_w, target_h = TARGET_SIZE
    source_stride, source_y_height, source_uv_height, _ = get_nv12_info(*SOURCE_SIZE)
    target_stride, target_y_height, target_uv_height, _ = get_nv12_info(*TARGET_SIZE)
    self.source_copy_size = source_stride * (source_y_height + source_uv_height)
    self.target_copy_size = target_stride * (target_y_height + target_uv_height)
    # np.take copies read-only indices, so keep this private map writable.
    self._indices = np.empty(self.target_copy_size, dtype=np.intp)

    x = ((2 * np.minimum(np.arange(target_stride, dtype=np.intp), target_w - 1) + 1) * source_w) // (2 * target_w)
    y = ((2 * np.minimum(np.arange(target_y_height, dtype=np.intp), target_h - 1) + 1) * source_h) // (2 * target_h)
    target_uv_offset = target_stride * target_y_height
    self._indices[:target_uv_offset].reshape(target_y_height, target_stride)[:] = y[:, None] * source_stride + x

    # Resize chroma pairs on their own grid, retaining the U/V byte within each pair.
    uv_bytes = np.arange(target_stride, dtype=np.intp)
    x = ((2 * np.minimum(uv_bytes // 2, target_w // 2 - 1) + 1) * (source_w // 2)) // (2 * (target_w // 2)) * 2 + uv_bytes % 2
    y = ((2 * np.minimum(np.arange(target_uv_height, dtype=np.intp), target_h // 2 - 1) + 1) * (source_h // 2)) // (2 * (target_h // 2))
    self._indices[target_uv_offset:].reshape(target_uv_height, target_stride)[:] = source_stride * source_y_height + y[:, None] * source_stride + x

    assert self._indices.min() >= 0 and self._indices.max() < self.source_copy_size

  def resize(self, source: Buffer, destination: np.ndarray) -> None:
    """Write into a contiguous uint8 frame view of target_copy_size bytes."""
    frame = np.frombuffer(source, dtype=np.uint8, count=self.source_copy_size)
    # Bounds are established above; clip avoids take's buffered output in raise mode.
    np.take(frame, self._indices, out=destination, mode='clip')
