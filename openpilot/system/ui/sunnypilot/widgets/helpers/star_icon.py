"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl


def draw_star(center_x, center_y, radius, is_filled, color):
  center = rl.Vector2(center_x, center_y)
  points = []

  for i in range(10):
    angle = -(i * 36 + 18) * math.pi / 180
    r = radius if i % 2 == 0 else radius / 2
    x = center_x + r * math.cos(angle)
    y = center_y + r * math.sin(angle)
    points.append(rl.Vector2(x, y))

  for i in range(10):
    if is_filled:
      rl.draw_triangle(center, points[i], points[(i + 1) % 10], color)
    rl.draw_line_ex(points[i], points[(i + 1) % 10], 2, color)
