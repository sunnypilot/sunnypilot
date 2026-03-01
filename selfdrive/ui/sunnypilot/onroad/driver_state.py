"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.selfdrive.ui import UI_BORDER_SIZE
from openpilot.selfdrive.ui.onroad.driver_state import DriverStateRenderer, BTN_SIZE, ARC_LENGTH
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiRenderer


class DriverStateRendererSP(DriverStateRenderer):
  def __init__(self):
    super().__init__()
    self.dev_ui_offset = DeveloperUiRenderer.get_bottom_dev_ui_offset()

  def _pre_calculate_drawing_elements(self):
    """Pre-calculate all drawing elements based on the current rectangle"""
    # Calculate icon position (bottom-left or bottom-right)
    width, height = self._rect.width, self._rect.height
    offset = UI_BORDER_SIZE + BTN_SIZE // 2
    self.position_x = self._rect.x + (width - offset if self.is_rhd else offset)
    self.position_y = self._rect.y + height - offset - self.dev_ui_offset

    # Pre-calculate the face lines positions
    positioned_keypoints = self.face_keypoints_transformed + np.array([self.position_x, self.position_y])
    for i in range(len(positioned_keypoints)):
      self.face_lines[i].x = positioned_keypoints[i][0]
      self.face_lines[i].y = positioned_keypoints[i][1]

    # Calculate arc dimensions based on head rotation
    delta_x = -self.driver_pose_sins[1] * ARC_LENGTH / 2.0  # Horizontal movement
    delta_y = -self.driver_pose_sins[0] * ARC_LENGTH / 2.0  # Vertical movement

    # Horizontal arc
    h_width = abs(delta_x)
    self.h_arc_data = self._calculate_arc_data(
      delta_x, h_width, self.position_x, self.position_y - ARC_LENGTH / 2,
      self.driver_pose_sins[1], self.driver_pose_diff[1], is_horizontal=True
    )

    # Vertical arc
    v_height = abs(delta_y)
    self.v_arc_data = self._calculate_arc_data(
      delta_y, v_height, self.position_x - ARC_LENGTH / 2, self.position_y,
      self.driver_pose_sins[0], self.driver_pose_diff[0], is_horizontal=False
    )
