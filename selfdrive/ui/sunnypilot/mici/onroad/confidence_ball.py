"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus


class ConfidenceBallSP:
  @staticmethod
  def get_animate_status_probs():
    if ui_state.status == UIStatus.LAT_ONLY:
      return ui_state.sm['modelV2'].meta.disengagePredictions.steerOverrideProbs

    # UIStatus.LONG_ONLY
    return ui_state.sm['modelV2'].meta.disengagePredictions.brakeDisengageProbs

  @staticmethod
  def get_lat_long_dot_color():
    from openpilot.selfdrive.ui.onroad.augmented_road_view import BORDER_COLORS

    if ui_state.status == UIStatus.LAT_ONLY:
      return BORDER_COLORS[UIStatus.LAT_ONLY]

    # UIStatus.LONG_ONLY
    return BORDER_COLORS[UIStatus.LONG_ONLY]

  def update_confidence_visual(self, content_rect, status_dot_radius, dot_height, top_dot_color, bottom_dot_color) -> bool:
    if self._visual == 2:
      bar_width = int(20 * self._scale)
      bar_x = content_rect.x + content_rect.width - bar_width
      fill_h = int(content_rect.height * self._confidence_filter.x)
      fill_y = int(content_rect.y + (content_rect.height - fill_h))
      rl.draw_rectangle(int(bar_x), int(content_rect.y), bar_width, int(content_rect.height), rl.Color(20, 20, 20, 180))
      rl.draw_rectangle_gradient_v(int(bar_x), fill_y, bar_width, fill_h, top_dot_color, bottom_dot_color)
      return True
    elif self._visual == 1:
      rl.draw_circle_gradient(int(content_rect.x + content_rect.width - status_dot_radius),
                           int(dot_height), status_dot_radius,
                           top_dot_color, bottom_dot_color)
      return True
    return False
