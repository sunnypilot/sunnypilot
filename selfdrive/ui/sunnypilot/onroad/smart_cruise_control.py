"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.onroad.hud_renderer import COLORS
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.sunnypilot.lib.utils import AlertFadeAnimator
from openpilot.system.ui.widgets import Widget


class SmartCruiseControlRenderer(Widget):
  def __init__(self):
    super().__init__()
    self.vision_enabled = False
    self.vision_active = False
    self.map_enabled = False
    self.map_active = False
    self.long_override = False

    self._vision_fade = AlertFadeAnimator(gui_app.target_fps)
    self._map_fade = AlertFadeAnimator(gui_app.target_fps)

    self.font = gui_app.font(FontWeight.BOLD)

  def update(self):
    sm = ui_state.sm
    if sm.updated["longitudinalPlanSP"]:
      lp_sp = sm["longitudinalPlanSP"]
      vision = lp_sp.smartCruiseControl.vision
      map_ = lp_sp.smartCruiseControl.map

      self.vision_enabled = vision.enabled
      self.vision_active = vision.active
      self.map_enabled = map_.enabled
      self.map_active = map_.active

    if sm.updated["carControl"]:
      self.long_override = sm["carControl"].cruiseControl.override

    self._vision_fade.update(self.vision_active)
    self._map_fade.update(self.map_active)

  def _draw_icon(self, rect_center_x, rect_height, x_offset, y_offset, name, alpha=1.0):
    text = name
    font_size = 36
    padding_v = 5
    box_width = 160

    sz = measure_text_cached(self.font, text, font_size)
    box_height = int(sz.y + padding_v * 2)

    if self.long_override:
      color = COLORS.OVERRIDE
      box_color = rl.Color(color.r, color.g, color.b, int(alpha * 255))
    else:
      box_color = rl.Color(0, 255, 0, int(alpha * 255))

    text_color = rl.Color(0, 0, 0, int(alpha * 255))

    screen_y = rect_height / 4 + y_offset

    box_x = rect_center_x + x_offset - box_width / 2
    box_y = screen_y - box_height / 2

    # Draw rounded background box
    if alpha > 0.01:
      rl.draw_rectangle_rounded(rl.Rectangle(box_x, box_y, box_width, box_height), 0.2, 10, box_color)

      # Draw text centered in the box (black color for contrast against bright green/grey)
      text_pos_x = box_x + (box_width - sz.x) / 2
      text_pos_y = box_y + (box_height - sz.y) / 2

      rl.draw_text_ex(self.font, text, rl.Vector2(text_pos_x, text_pos_y), font_size, 0, text_color)

  def _render(self, rect: rl.Rectangle):
    x_offset = -260
    y1_offset = -40
    y2_offset = -100

    orders = [y1_offset, y2_offset]
    y_scc_v = 0
    y_scc_m = 0
    idx = 0

    if self.vision_enabled:
      y_scc_v = orders[idx]
      idx += 1

    if self.map_enabled:
      y_scc_m = orders[idx]
      idx += 1

    if self.vision_enabled:
      alpha = self._vision_fade.alpha if self.vision_active else 1.0
      self._draw_icon(rect.x + rect.width / 2, rect.height, x_offset, y_scc_v, "SCC-V", alpha)

    if self.map_enabled:
      alpha = self._map_fade.alpha if self.map_active else 1.0
      self._draw_icon(rect.x + rect.width / 2, rect.height, x_offset, y_scc_m, "SCC-M", alpha)
