"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.transformations.camera import DEVICE_CAMERAS


class CameraOffsetHelper:
  def __init__(self):
    self.camera_offset = 0.0
    self.actual_camera_offset = 0.0

  @staticmethod
  def apply_camera_offset(model_transform, intrinsics, height, offset_param):
    cy = intrinsics[1, 2]
    shear = np.eye(3, dtype=np.float32)
    shear[0, 1] = offset_param / height
    shear[0, 2] = -offset_param / height * cy
    model_transform = (shear @ model_transform).astype(np.float32)
    return model_transform

  def set_offset(self, offset):
    self.camera_offset = offset

  def update(self, model_transform_main, model_transform_extra, sm, main_wide_camera):
    self.actual_camera_offset = (0.9 * self.actual_camera_offset) + (0.1 * self.camera_offset)
    dc = DEVICE_CAMERAS[(str(sm['deviceState'].deviceType), str(sm['roadCameraState'].sensor))]
    height = sm["liveCalibration"].height[0] if sm['liveCalibration'].height else 1.22

    intrinsics_main = dc.ecam.intrinsics if main_wide_camera else dc.fcam.intrinsics
    model_transform_main = self.apply_camera_offset(model_transform_main, intrinsics_main, height, self.actual_camera_offset)

    intrinsics_extra = dc.ecam.intrinsics
    model_transform_extra = self.apply_camera_offset(model_transform_extra, intrinsics_extra, height, self.actual_camera_offset)
    return model_transform_main, model_transform_extra
