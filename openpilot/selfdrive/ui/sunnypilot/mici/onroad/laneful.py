"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Laneful visuals: faint cyan lane-center target, thin white line down the middle of the model path,
and a top-center readout of the pull, from the curvature, trust, line probs and lane width modeld publishes in modelDataV2SP.
"""
from types import SimpleNamespace

import numpy as np
import pyray as rl
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.modeld_v2.laneful import LOOKAHEAD_TIME, MIN_LOOKAHEAD, MAX_ERROR
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.shader_polygon import draw_polygon, Gradient
from openpilot.system.ui.lib.text_measure import measure_text_cached

CENTER_COLOR = (0, 200, 255)
PATH_COLOR = (255, 255, 255)

bar = SimpleNamespace(offset=0.0, pull=0.0, alpha=0.0)


class LanefulRenderer:
  def __init__(self):
    self._center_points = np.empty((0, 2), dtype=np.float32)
    self._path_points = np.empty((0, 2), dtype=np.float32)
    self._font = gui_app.font(FontWeight.BOLD)
    # smoothed copies for the readout so the numbers don't flicker
    self._pull_display = FirstOrderFilter(0.0, 0.5, DT_MDL)
    self._offset_display = FirstOrderFilter(0.0, 0.5, DT_MDL)
    self._alpha = FirstOrderFilter(0.0, 0.3, DT_MDL)
    self._readout_rect: rl.Rectangle | None = None
    self._settings_page = None

  def update(self, renderer, max_idx: int) -> None:
    """Called from the model renderer's update with its lane lines and path already in raw points."""
    laneful = ui_state.sm['modelDataV2SP']
    laneful_curvature = laneful.lanefulCurvature
    self._alpha.update(float(laneful.lanefulTrust > 0.0))
    bar.alpha = self._alpha.x

    left, right = renderer._lane_lines[1].raw_points, renderer._lane_lines[2].raw_points
    stds = list(ui_state.sm['modelV2'].laneLineStds)
    if self._alpha.x < 0.01 or len(left) == 0 or len(right) != len(left) or len(stds) < 3:
      self._center_points = np.empty((0, 2), dtype=np.float32)
      self._path_points = np.empty((0, 2), dtype=np.float32)
      return

    lookahead = max(ui_state.sm['carState'].vEgo * LOOKAHEAD_TIME, MIN_LOOKAHEAD)
    l_var = stds[1] ** 2 / max(laneful.lanefulLeftProb, 1e-4)
    r_var = stds[2] ** 2 / max(laneful.lanefulRightProb, 1e-4)
    half_width = laneful.lanefulLaneWidth / 2
    center_y = (r_var * (left[:, 1] + half_width) + l_var * (right[:, 1] - half_width)) / (l_var + r_var)

    # target and middle of the model path share the path's points, so both end at the same distance
    path = renderer._path.raw_points
    center = path.copy()
    center[:, 1] = np.interp(path[:, 0], left[:, 0], center_y)
    end_idx = renderer._get_path_length_idx(path[:, 0], min(1.5 * lookahead, left[max_idx, 0]))
    self._center_points = renderer._map_line_to_polygon(center, 0.1, renderer._path_offset_z, end_idx)
    self._path_points = renderer._map_line_to_polygon(path, 0.1, renderer._path_offset_z, end_idx)
    self._pull_display.update(laneful_curvature * lookahead ** 2 / 2)  # how far laneful moves the car at the lookahead
    if laneful.lanefulTrust > 0.0:
      bar.offset = self._offset_display.update(float(np.clip(np.interp(lookahead, path[:, 0], center[:, 1] - path[:, 1]) / MAX_ERROR, -1.0, 1.0)))
      bar.pull = float(np.clip(self._pull_display.x / MAX_ERROR, -1.0, 1.0))

  def _color(self, rgb, alpha: float) -> rl.Color:
    return rl.Color(*rgb, int(alpha * self._alpha.x))

  def _fade(self, rgb, alpha: float) -> Gradient:
    return Gradient(start=(0.0, 1.0), end=(0.0, 0.0), colors=[self._color(rgb, alpha), self._color(rgb, alpha), self._color(rgb, 0)], stops=[0.0, 0.6, 1.0])

  def draw(self, rect: rl.Rectangle) -> None:
    if self._path_points.size:
      draw_polygon(rect, self._path_points, gradient=self._fade(PATH_COLOR, 255))
      draw_polygon(rect, self._center_points, gradient=self._fade(CENTER_COLOR, 100))
    self._readout_rect = None
    if self._path_points.size:
      self._draw_readout(rect)

  def handle_tap(self, pos) -> bool:
    """Tapping the readout opens the laneful settings page. Returns True if the tap was consumed."""
    r = self._readout_rect
    if r is None or not (r.x - 20 <= pos.x <= r.x + r.width + 20 and r.y - 20 <= pos.y <= r.y + r.height + 20):
      return False
    if self._settings_page is None:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.laneful import LanefulLayoutMici
      self._settings_page = LanefulLayoutMici()
    gui_app.push_widget(self._settings_page)
    return True

  def _draw_readout(self, rect: rl.Rectangle) -> None:
    """Top-center pill: pull toward lane center in cm at the lookahead, arrow = side,
    bar grows from center toward the target (faint) and pull (solid), full at laneful's 1 m cap."""
    pull = self._pull_display.x
    w, h = 190, 76
    x, y = rect.x + (rect.width - w) / 2, rect.y + 10
    cx, cy = x + w / 2, y + 30
    self._readout_rect = rl.Rectangle(x, y, w, h)
    rl.draw_rectangle_rounded(self._readout_rect, 0.5, 12, self._color((0, 0, 0), 170))

    text = f"{abs(pull) * 100:.0f}"
    text_w = measure_text_cached(self._font, text, 44, 0).x
    rl.draw_text_ex(self._font, text, rl.Vector2(cx - text_w / 2, cy - 24), 44, 0, self._color((255, 255, 255), 255))

    active = self._color(CENTER_COLOR, np.clip(abs(pull) / 0.1, 0.0, 1.0) * 255)
    idle = self._color((255, 255, 255), 40)
    lx, rx = x + 18, x + w - 18
    rl.draw_triangle(rl.Vector2(lx, cy), rl.Vector2(lx + 16, cy + 12), rl.Vector2(lx + 16, cy - 12), active if pull < 0 else idle)
    rl.draw_triangle(rl.Vector2(rx - 16, cy - 12), rl.Vector2(rx - 16, cy + 12), rl.Vector2(rx, cy), active if pull > 0 else idle)

    track = rl.Rectangle(x + 24, y + h - 16, w - 48, 6)
    rl.draw_rectangle_rounded(track, 1.0, 6, self._color((255, 255, 255), 40))
    rl.draw_rectangle(int(cx - 1), int(track.y - 2), 2, int(track.height + 4), self._color((255, 255, 255), 120))
    for frac, strength in ((bar.offset, 0.4), (bar.pull, 1.0)):
      fill = track.width / 2 * abs(frac)
      if fill > 1:
        fill_x = cx if frac > 0 else cx - fill
        rl.draw_rectangle_rounded(rl.Rectangle(fill_x, track.y, fill, track.height), 1.0, 6,
                                  self._color(CENTER_COLOR, strength * 255))


def draw_laneful_bar(rect: rl.Rectangle, torque_r: float, torque_h: float, span: float, center: np.ndarray, alpha: float, scale: float) -> None:
  from openpilot.selfdrive.ui.mici.onroad.torque_bar import arc_bar_pts
  h = 10 * scale * bar.alpha
  if h < 1:
    return
  for frac, strength in ((bar.offset, 0.4), (bar.pull, 1.0)):
    a1 = -90 + span * 0.35 * frac
    pts = arc_bar_pts(torque_r + (torque_h + h) / 2, h, min(-90, a1), max(-90, a1), cap_radius=h / 2) + center
    draw_polygon(rect, pts, color=rl.Color(*CENTER_COLOR, int(255 * strength * alpha * bar.alpha)))
