"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
from openpilot.common.transformations.model import get_warp_matrix
from openpilot.common.transformations.orientation import rot_from_euler
from openpilot.sunnypilot.modeld_v2.camera_offset_helper import CameraOffsetHelper
from openpilot.common.test import OpenpilotTestCase


class MockStruct:
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)

  def __getitem__(self, item):
    return getattr(self, item)


class TestCameraOffset(OpenpilotTestCase):
  def setup_method(self):
    self.camera_offset = CameraOffsetHelper()
    self.dc = DEVICE_CAMERAS[('mici', 'os04c10')]

  def test_smoothing(self):
    self.camera_offset.set_offset(0.2)

    sm = MockStruct(
      deviceState=MockStruct(deviceType='mici'),
      narrowRoadCameraState=MockStruct(sensor='os04c10'),
      extrinsicsCalibration=MockStruct(rpyCalib=[0.0, 0.0, 0.0], height=[1.22])
    )

    intrinsics_main = self.dc.narrow_road.intrinsics
    intrinsics_extra = self.dc.wide_road.intrinsics
    device_from_calib_euler = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    main_transform = get_warp_matrix(device_from_calib_euler, intrinsics_main, False).astype(np.float32)
    extra_transform = get_warp_matrix(device_from_calib_euler, intrinsics_extra, True).astype(np.float32)

    self.camera_offset.update(main_transform, extra_transform, sm, False)
    np.testing.assert_almost_equal(self.camera_offset.actual_camera_offset, 0.02)
    self.camera_offset.update(main_transform, extra_transform, sm, False)
    np.testing.assert_almost_equal(self.camera_offset.actual_camera_offset, 0.038)

  def test_apply_camera_offset(self):
    intrinsics = self.dc.narrow_road.intrinsics
    v_horizon = CameraOffsetHelper.get_v_horizon(intrinsics, [])  # pitch = 0 fallback: v_horizon == cy
    transform = np.eye(3, dtype=np.float32)
    height = 1.22
    offset = 0.1

    expected_shear = np.eye(3, dtype=np.float32)
    expected_shear[0, 1] = offset / height
    expected_shear[0, 2] = -offset / height * v_horizon

    result = CameraOffsetHelper.apply_camera_offset(transform, height, offset, v_horizon)
    np.testing.assert_array_almost_equal(result, expected_shear)

  def test_v_horizon_empty_rpy(self):
    intrinsics = self.dc.narrow_road.intrinsics
    v_horizon = CameraOffsetHelper.get_v_horizon(intrinsics, [])
    np.testing.assert_almost_equal(v_horizon, intrinsics[1, 2])

  def test_v_horizon_projection(self):
    intrinsics = self.dc.narrow_road.intrinsics
    f, cy = intrinsics[1, 1], intrinsics[1, 2]

    for pitch_deg in [6.0, -6.0, 0.0]:
      rpy = [0.0, np.radians(pitch_deg), 0.0]
      d_dev = rot_from_euler(rpy) @ np.array([1.0, 0.0, 0.0])
      view = view_frame_from_device_frame @ d_dev
      expected = cy + f * view[1] / view[2]

      v_horizon = CameraOffsetHelper.get_v_horizon(intrinsics, rpy)
      np.testing.assert_almost_equal(v_horizon, expected, decimal=4)

  def test_update(self):
    height = 1.2
    pitch = np.radians(-8.0)

    sm = MockStruct(
      deviceState=MockStruct(deviceType='mici'),
      narrowRoadCameraState=MockStruct(sensor='os04c10'),
      extrinsicsCalibration=MockStruct(rpyCalib=[0.0, pitch, 0.0], height=[height])
    )
    intrinsics_main = self.dc.narrow_road.intrinsics
    intrinsics_extra = self.dc.wide_road.intrinsics
    device_from_calib_euler = np.array(sm['extrinsicsCalibration'].rpyCalib, dtype=np.float32)
    main_transform = get_warp_matrix(device_from_calib_euler, intrinsics_main, False).astype(np.float32)
    extra_transform = get_warp_matrix(device_from_calib_euler, intrinsics_extra, True).astype(np.float32)

    self.camera_offset.set_offset(0.0)  # test default offset doesn't change transformation
    main_out, extra_out = self.camera_offset.update(main_transform, extra_transform, sm, False)
    np.testing.assert_array_equal(main_out, main_transform)
    np.testing.assert_array_equal(extra_out, extra_transform)

    self.camera_offset.set_offset(0.2)  # test valid offset changes transformation
    main_out, extra_out = self.camera_offset.update(main_transform, extra_transform, sm, False)
    assert not np.array_equal(main_out, main_transform)
    assert not np.array_equal(extra_out, extra_transform)

    # settle the low-pass filter
    for _ in range(100):
      main_out, extra_out = self.camera_offset.update(main_transform, extra_transform, sm, False)

    # undo main_transform dot product to get shear matrix
    shear = main_out @ np.linalg.inv(main_transform)
    expected_v_horizon = intrinsics_main[1, 2] - intrinsics_main[1, 1] * np.tan(pitch)
    np.testing.assert_almost_equal(shear[0, 1], self.camera_offset.actual_camera_offset / height, decimal=4)
    np.testing.assert_almost_equal(shear[0, 2], -self.camera_offset.actual_camera_offset / height * expected_v_horizon, decimal=4)
