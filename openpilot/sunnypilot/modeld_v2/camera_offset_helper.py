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
  def get_v_horizon(intrinsics, rpy_calib):
    cy = intrinsics[1, 2]
    if len(rpy_calib) == 3 and np.isfinite(rpy_calib).all():
      fy = intrinsics[1, 1]
      pitch = rpy_calib[1]
      return float(cy - fy * np.tan(pitch))
    return float(cy)

  @staticmethod
  def apply_camera_offset(model_transform, height, offset_param, v_horizon):
    shear = np.eye(3, dtype=np.float32)
    shear[0, 1] = offset_param / height
    shear[0, 2] = -offset_param / height * v_horizon
    model_transform = (shear @ model_transform).astype(np.float32)
    return model_transform

  def set_offset(self, offset):
    self.camera_offset = offset

  def update(self, model_transform_main, model_transform_extra, sm, main_wide_camera):
    self.actual_camera_offset = (0.9 * self.actual_camera_offset) + (0.1 * self.camera_offset)
    dc = DEVICE_CAMERAS[(str(sm['deviceState'].deviceType), str(sm['narrowRoadCameraState'].sensor))]
    height = sm["extrinsicsCalibration"].height[0] if sm['extrinsicsCalibration'].height else 1.22
    rpy_calib = sm['extrinsicsCalibration'].rpyCalib

    intrinsics_main = dc.wide_road.intrinsics if main_wide_camera else dc.narrow_road.intrinsics
    v_horizon_main = self.get_v_horizon(intrinsics_main, rpy_calib)
    model_transform_main = self.apply_camera_offset(model_transform_main, height, self.actual_camera_offset, v_horizon_main)

    intrinsics_extra = dc.wide_road.intrinsics
    v_horizon_extra = self.get_v_horizon(intrinsics_extra, rpy_calib)
    model_transform_extra = self.apply_camera_offset(model_transform_extra, height, self.actual_camera_offset, v_horizon_extra)
    return model_transform_main, model_transform_extra
