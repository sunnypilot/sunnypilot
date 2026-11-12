"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.transformations.camera import get_view_frame_from_calib_frame, view_frame_from_device_frame
from openpilot.common.transformations.orientation import rot_from_euler

TURN_INPUT_SIZE = (512, 256)
turn_intrinsics = np.array([
  [180.0, 0.0, 256.0],
  [0.0, 440.0, 70.0],
  [0.0, 0.0, 1.0]])
calib_from_turn = np.linalg.inv((turn_intrinsics @ get_view_frame_from_calib_frame(0, 0, 0, 0))[:, :3])


def get_turn_warp_matrix(device_from_calib_euler: np.ndarray, wide_intrinsics: np.ndarray) -> np.ndarray:
  camera_from_calib = wide_intrinsics @ view_frame_from_device_frame @ rot_from_euler(device_from_calib_euler)
  return (camera_from_calib @ calib_from_turn).astype(np.float32)
