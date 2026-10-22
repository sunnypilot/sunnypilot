"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Blendful visuals: cyan lane-center target, thin white line down the middle of the model path,
and a top-center readout of the pull, from the curvature modeld publishes in modelDataV2SP.blendfulCurvature.
"""
import numpy as np
import pyray as rl
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.modeld_v2.blendful import LANE_WIDTH_CLIP, LOOKAHEAD_TIME, MIN_LOOKAHEAD, MAX_ERROR
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.shader_polygon import draw_polygon
from openpilot.system.ui.lib.text_measure import measure_text_cached

CENTER_COLOR = (0, 200, 255)
PATH_COLOR = (255, 255, 255)


class BlendfulRenderer:
  def __init__(self):
    self._center_points = np.empty((0, 2), dtype=np.float32)
    self._path_points = np.empty((0, 2), dtype=np.float32)
    self._trust = 0.0
    self._font = gui_app.font(FontWeight.BOLD)
    # smoothed copies for the readout so the numbers don't flicker
    self._pull_display = FirstOrderFilter(0.0, 0.5, DT_MDL)
    self._trust_display = FirstOrderFilter(0.0, 0.5, DT_MDL)
    self._alpha = FirstOrderFilter(0.0, 0.3, DT_MDL) # fades that hoe

  def update(self, renderer, max_idx: int) -> None:
    """Called from the model renderer's update with its lane lines and path already in raw points."""
    blendful = ui_state.sm['modelDataV2SP']
    blendful_curvature = blendful.blendfulCurvature
    self._alpha.update(float(blendful.blendfulTrust > 0.0))

    left, right = renderer._lane_lines[1].raw_points, renderer._lane_lines[2].raw_points
    stds = list(ui_state.sm['modelV2'].laneLineStds)
    if self._alpha.x < 0.01 or len(left) == 0 or len(right) != len(left) or len(stds) < 3:
      self._center_points = np.empty((0, 2), dtype=np.float32)
      self._path_points = np.empty((0, 2), dtype=np.float32)
      return

    l_prob, r_prob = blendful.blendfulLeftProb, blendful.blendfulRightProb
    half_width = np.clip(right[:, 1] - left[:, 1], *LANE_WIDTH_CLIP) / 2 if l_prob * r_prob > 0.5 else blendful.blendfulLaneWidth / 2
    l_var = stds[1] ** 2 / max(l_prob, 1e-4)
    r_var = stds[2] ** 2 / max(r_prob, 1e-4)
    center = left.copy()
    center[:, 1] = (r_var * (left[:, 1] + half_width) + l_var * (right[:, 1] - half_width)) / (l_var + r_var)
    self._trust = blendful.blendfulTrust
    self._center_points = renderer._map_line_to_polygon(center, 0.1, 0.0, max_idx)

    # middle of the model path, ending at the lookahead
    path = renderer._path.raw_points
    lookahead = max(ui_state.sm['carState'].vEgo * LOOKAHEAD_TIME, MIN_LOOKAHEAD)
    self._pull_display.update(blendful_curvature * lookahead ** 2 / 2)  # how far blendful moves the car at the lookahead
    self._trust_display.update(self._trust)
    self._path_points = renderer._map_line_to_polygon(path, 0.15, renderer._path_offset_z,
                                                      renderer._get_path_length_idx(path[:, 0], lookahead))

  def _color(self, rgb, alpha: float) -> rl.Color:
    return rl.Color(*rgb, int(alpha * self._alpha.x))

  def draw(self, rect: rl.Rectangle) -> None:
    if self._center_points.size and self._trust > 0.05:
      draw_polygon(rect, self._center_points, self._color(CENTER_COLOR, np.clip(self._trust, 0.2, 1.0) * 255))
    if self._path_points.size:
      draw_polygon(rect, self._path_points, self._color(PATH_COLOR, 200))
      self._draw_readout(rect)

  def _draw_readout(self, rect: rl.Rectangle) -> None:
    """Top-center pill: pull toward lane center in cm at the lookahead, arrow = side,
    bar grows from center toward the pull (full at the cap), brighter with more lane line trust."""
    pull, trust = self._pull_display.x, self._trust_display.x
    w, h = 190, 76
    x, y = rect.x + (rect.width - w) / 2, rect.y + 10
    cx, cy = x + w / 2, y + 30
    rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), 0.5, 12, self._color((0, 0, 0), 170))

    text = f"{abs(pull) * 100:.0f}"
    text_w = measure_text_cached(self._font, text, 44, 0).x
    rl.draw_text_ex(self._font, text, rl.Vector2(cx - text_w / 2, cy - 24), 44, 0, self._color((255, 255, 255), 255))

    active = self._color(CENTER_COLOR, np.clip(abs(pull) / 0.1, 0.0, 1.0) * 255)
    idle = self._color((255, 255, 255), 40)
    lx, rx = x + 18, x + w - 18
    rl.draw_triangle(rl.Vector2(lx, cy), rl.Vector2(lx + 16, cy + 12), rl.Vector2(lx + 16, cy - 12), active if pull < 0 else idle)
    rl.draw_triangle(rl.Vector2(rx - 16, cy - 12), rl.Vector2(rx - 16, cy + 12), rl.Vector2(rx, cy), active if pull > 0 else idle)

    bar = rl.Rectangle(x + 24, y + h - 16, w - 48, 6)
    rl.draw_rectangle_rounded(bar, 1.0, 6, self._color((255, 255, 255), 40))
    rl.draw_rectangle(int(cx - 1), int(bar.y - 2), 2, int(bar.height + 4), self._color((255, 255, 255), 120))
    fill = bar.width / 2 * float(np.clip(abs(pull) / MAX_ERROR, 0.0, 1.0))
    if fill > 1:
      fill_x = cx if pull > 0 else cx - fill
      rl.draw_rectangle_rounded(rl.Rectangle(fill_x, bar.y, fill, bar.height), 1.0, 6,
                                self._color(CENTER_COLOR, np.clip(0.3 + 0.7 * trust, 0.0, 1.0) * 255))
