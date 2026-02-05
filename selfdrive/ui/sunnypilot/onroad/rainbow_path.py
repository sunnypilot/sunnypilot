"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
import colorsys
import pyray as rl
from openpilot.system.ui.lib.shader_polygon import draw_polygon, Gradient


class RainbowPath:
  DEFAULT_NUM_SEGMENTS = 8
  DEFAULT_SPEED = 50.0  # degrees per second
  DEFAULT_SATURATION = 0.9
  DEFAULT_LIGHTNESS = 0.6
  BASE_ALPHA = 0.8
  ALPHA_FADE = 0.3  # Alpha reduction from bottom to top

  def __init__(self, num_segments: int = DEFAULT_NUM_SEGMENTS, speed: float = DEFAULT_SPEED,
               saturation: float = DEFAULT_SATURATION, lightness: float = DEFAULT_LIGHTNESS):
    self.num_segments = num_segments
    self.speed = speed
    self.saturation = saturation
    self.lightness = lightness

  def set_speed(self, speed: float):
    self.speed = speed

  def set_num_segments(self, num_segments: int):
    self.num_segments = num_segments

  def set_saturation(self, saturation: float):
    self.saturation = max(0.0, min(1.0, saturation))

  def set_lightness(self, lightness: float):
    self.lightness = max(0.0, min(1.0, lightness))

  def get_gradient(self) -> Gradient:
    time_offset = time.monotonic()
    hue_offset = (time_offset * self.speed) % 360.0

    segment_colors = []
    gradient_stops = []

    for i in range(self.num_segments):
      position = i / (self.num_segments - 1)
      hue = (hue_offset + position * 360.0) % 360.0
      alpha = self.BASE_ALPHA * (1.0 - position * self.ALPHA_FADE)
      color = self._hsla_to_color(
        hue / 360.0,
        self.saturation,
        self.lightness,
        alpha
      )
      gradient_stops.append(position)
      segment_colors.append(color)

    return Gradient(
      start=(0.0, 1.0),  # Bottom of path
      end=(0.0, 0.0),  # Top of path
      colors=segment_colors,
      stops=gradient_stops,
    )

  @staticmethod
  def _hsla_to_color(h: float, s: float, l: float, a: float) -> rl.Color:
    rgb = colorsys.hls_to_rgb(h, l, s)
    return rl.Color(
      int(rgb[0] * 255),
      int(rgb[1] * 255),
      int(rgb[2] * 255),
      int(a * 255)
    )

  def draw_rainbow_path(self, rect, path):
    gradient = self.get_gradient()
    draw_polygon(rect, path.projected_points, gradient=gradient)
