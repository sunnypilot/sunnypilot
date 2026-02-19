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
from openpilot.system.ui.widgets import Widget


class SmartCruiseControlRenderer(Widget):
  def __init__(self):
    super().__init__()
    self.vision_enabled = False
    self.vision_active = False
    self.vision_frame = 0
    self.map_enabled = False
    self.map_active = False
    self.map_frame = 0
    self.long_override = False

    self.font = gui_app.font(FontWeight.BOLD)
    self.scc_tex = rl.load_render_texture(256, 128)

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

    if self.vision_active:
      self.vision_frame += 1
    else:
      self.vision_frame = 0

    if self.map_active:
      self.map_frame += 1
    else:
      self.map_frame = 0

  @staticmethod
  def _pulse_element(frame):
    return not (frame % gui_app.target_fps < (gui_app.target_fps / 2.5))

  def _draw_icon(self, rect_center_x, rect_height, x_offset, y_offset, name):
    text = name
    font_size = 36
    padding_v = 5
    box_width = 160

    sz = measure_text_cached(self.font, text, font_size)
    box_height = int(sz.y + padding_v * 2)

    texture_width = 256
    texture_height = 128

    rl.begin_texture_mode(self.scc_tex)
    rl.clear_background(rl.Color(0, 0, 0, 0))

    if self.long_override:
      box_color = COLORS.OVERRIDE
    else:
      box_color = rl.Color(0, 255, 0, 255)

    # Center box in texture
    box_x = (texture_width - box_width) // 2
    box_y = (texture_height - box_height) // 2

    rl.draw_rectangle_rounded(rl.Rectangle(box_x, box_y, box_width, box_height), 0.2, 10, box_color)

    # Draw text with custom blend mode to punch hole
    rl.rl_set_blend_factors(rl.RL_ZERO, rl.RL_ONE_MINUS_SRC_ALPHA, 0x8006)
    rl.rl_set_blend_mode(rl.BLEND_CUSTOM)

    text_pos_x = box_x + (box_width - sz.x) / 2
    text_pos_y = box_y + (box_height - sz.y) / 2

    rl.draw_text_ex(self.font, text, rl.Vector2(text_pos_x, text_pos_y), font_size, 0, rl.WHITE)

    rl.rl_set_blend_mode(rl.BLEND_ALPHA)  # Reset
    rl.end_texture_mode()

    screen_y = rect_height / 4 + y_offset

    dest_x = rect_center_x + x_offset - texture_width / 2
    dest_y = screen_y - texture_height / 2

    src_rect = rl.Rectangle(0, 0, texture_width, -texture_height)
    dst_rect = rl.Rectangle(dest_x, dest_y, texture_width, texture_height)

    rl.draw_texture_pro(self.scc_tex.texture, src_rect, dst_rect, rl.Vector2(0, 0), 0, rl.WHITE)

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

    scc_vision_pulse = self._pulse_element(self.vision_frame)
    if (self.vision_enabled and not self.vision_active) or (self.vision_active and scc_vision_pulse):
      self._draw_icon(rect.x + rect.width / 2, rect.height, x_offset, y_scc_v, "SCC-V")

    scc_map_pulse = self._pulse_element(self.map_frame)
    if (self.map_enabled and not self.map_active) or (self.map_active and scc_map_pulse):
      self._draw_icon(rect.x + rect.width / 2, rect.height, x_offset, y_scc_m, "SCC-M")
