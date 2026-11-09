"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.transformations.camera import get_view_frame_from_calib_frame, view_frame_from_device_frame
from openpilot.common.transformations.orientation import rot_from_euler

LIGHT_INPUT_SIZE = (512, 256)
light_intrinsics = np.array([
  [1000.0, 0.0, 256.0],
  [0.0, 1000.0, 200.0],
  [0.0, 0.0, 1.0]])
calib_from_light = np.linalg.inv((light_intrinsics @ get_view_frame_from_calib_frame(0, 0, 0, 0))[:, :3])


def get_light_warp_matrix(device_from_calib_euler: np.ndarray, intrinsics: np.ndarray) -> np.ndarray:
  camera_from_calib = intrinsics @ view_frame_from_device_frame @ rot_from_euler(device_from_calib_euler)
  return (camera_from_calib @ calib_from_light).astype(np.float32)
