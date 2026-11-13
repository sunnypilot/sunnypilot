"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Set Speed Assist's mark: a set-speed gauge with a swoosh over it, its arrow ending on the needle's
line. Drawn as polygons rather than a texture, so it stays sharp at any size, and sized by its ink,
not a padded box, so a status bar's spacing is the gap you see.
"""
import math

import numpy as np
import pyray as rl

from openpilot.system.ui.widgets import Widget

STATUS_ICON_HEIGHT = 40  # upstream's footer icons (network, chestnut, usb) are 40 px of ink
STATUS_ICON_ALPHA = 0.9  # settings and network draw at 90%

# gauge, in units of its scale s, about the dial's center (raylib degrees: 0 right, clockwise).
# Strokes sit near the wheel's rim (~6 px at 50) at the onroad 44 px; the swoosh rides out with its
# thickness so the gap to the dial stays open, which is what keeps the weight from reading heavy.
DIAL_FROM, DIAL_TO = 135, 405
DIAL_R, DIAL_T = 0.378, 0.115
NEEDLE_DEG = 285          # about 12:30
NEEDLE_LEN = DIAL_R - DIAL_T - 0.04
HUB_R = 0.085
SWOOSH_FROM = 195
SWOOSH_T0, SWOOSH_T1 = 0.05, 0.10  # tapers up to the head
SWOOSH_GAP = 0.09
SWOOSH_R = DIAL_R + SWOOSH_GAP + SWOOSH_T1 / 2
HEAD_HALF = 1.3 * SWOOSH_T1
HEAD_DEG = math.degrees(1.7 * HEAD_HALF / SWOOSH_R)  # the head's length along the arc
SWOOSH_TO = NEEDLE_DEG - HEAD_DEG  # so the arrow's tip lies on the needle's line
SWOOSH_SEGMENTS = 24
DIAL_SEGMENTS = 64
HUB_SEGMENTS = 12


def _pt(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
  return cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg))


def _swoosh_t(f: float) -> float:
  return SWOOSH_T0 + (SWOOSH_T1 - SWOOSH_T0) * f


def _ink_bounds() -> tuple[float, float, float, float]:
  """(left, top, right, bottom) of the gauge's ink at s = 1 about the dial's center."""
  pts = []
  for deg in np.linspace(DIAL_FROM, DIAL_TO, 271):
    pts += [_pt(0, 0, DIAL_R, deg), _pt(0, 0, DIAL_R - DIAL_T, deg)]
  for f in np.linspace(0, 1, 101):
    deg, t = SWOOSH_FROM + (SWOOSH_TO - SWOOSH_FROM) * f, _swoosh_t(f)
    pts += [_pt(0, 0, SWOOSH_R + t / 2, deg), _pt(0, 0, SWOOSH_R - t / 2, deg)]
  pts += [_pt(0, 0, SWOOSH_R, NEEDLE_DEG), _pt(0, 0, SWOOSH_R - HEAD_HALF, SWOOSH_TO), _pt(0, 0, SWOOSH_R + HEAD_HALF, SWOOSH_TO)]
  xs, ys = zip(*pts, strict=True)
  return min(xs), min(ys), max(xs), max(ys)


_LEFT, _TOP, _RIGHT, _BOTTOM = _ink_bounds()
GAUGE_ASPECT = (_RIGHT - _LEFT) / (_BOTTOM - _TOP)  # ink width / height


Point = tuple[float, float]


def _strip(left: list[Point], right: list[Point]) -> np.ndarray:
  """One triangle strip between two chains, so a translucent color lays each pixel once: separate
  overlapping shapes would show darker seams wherever they meet."""
  (lx, ly), (rx, ry), (nx, ny) = left[0], right[0], left[1]
  if (rx - lx) * (ny - ly) - (ry - ly) * (nx - lx) > 0:
    left, right = right, left  # raylib culls clockwise triangles; the strip's first one sets the winding
  return np.array([p for pair in zip(left, right, strict=True) for p in pair])


def _unit_strips() -> list[np.ndarray]:
  """The gauge's three strips at s = 1 about the dial's center."""
  dial = np.linspace(DIAL_FROM, DIAL_TO, DIAL_SEGMENTS + 1)
  strips = [_strip([_pt(0, 0, DIAL_R, d) for d in dial], [_pt(0, 0, DIAL_R - DIAL_T, d) for d in dial])]

  # needle and hub as one teardrop: the tip, then the hub's back half from where the sides meet it
  tip = _pt(0, 0, NEEDLE_LEN, NEEDLE_DEG)
  side = math.degrees(math.acos(HUB_R / NEEDLE_LEN))
  back = np.linspace(side, 180, HUB_SEGMENTS)
  strips.append(_strip([tip] + [_pt(0, 0, HUB_R, NEEDLE_DEG + d) for d in back],
                       [tip] + [_pt(0, 0, HUB_R, NEEDLE_DEG - d) for d in back]))

  # swoosh and arrowhead as one ribbon: the tapered shaft, its barbs, then the tip
  outer, inner = [], []
  for f in np.linspace(0, 1, SWOOSH_SEGMENTS + 1):
    deg, t = SWOOSH_FROM + (SWOOSH_TO - SWOOSH_FROM) * f, _swoosh_t(f)
    outer.append(_pt(0, 0, SWOOSH_R + t / 2, deg))
    inner.append(_pt(0, 0, SWOOSH_R - t / 2, deg))
  outer.append(_pt(0, 0, SWOOSH_R + HEAD_HALF, SWOOSH_TO))
  inner.append(_pt(0, 0, SWOOSH_R - HEAD_HALF, SWOOSH_TO))
  arrow_tip = _pt(0, 0, SWOOSH_R, NEEDLE_DEG)
  strips.append(_strip(outer + [arrow_tip], inner + [arrow_tip]))
  return strips


_UNIT_STRIPS = _unit_strips()
# vertex arrays by (x, y, height): the gauge only moves while it slides in or out
_placed: dict[tuple[float, float, float], list[tuple]] = {}
PLACED_MAX = 8


def draw_gauge(x: float, y: float, height: float, alpha: float = 1.0) -> None:
  """The Set Speed Assist gauge with its ink's top-left at (x, y), `height` tall."""
  # rounded: a sliding filter only approaches its rest, so its last digits never settle
  key = (round(x, 1), round(y, 1), round(height, 1))
  strips = _placed.get(key)
  if strips is None:
    x, y, height = key
    s = height / (_BOTTOM - _TOP)
    origin = np.array([x - _LEFT * s, y - _TOP * s])
    strips = []
    for unit in _UNIT_STRIPS:
      points = rl.ffi.new("Vector2[]", (unit * s + origin).tolist())
      strips.append((points, rl.ffi.cast("Vector2 *", points), len(unit)))  # the array owns the memory
    if len(_placed) >= PLACED_MAX:
      _placed.clear()
    _placed[key] = strips
  color = rl.color_alpha(rl.WHITE, alpha)
  for _, points, count in strips:
    rl.draw_triangle_strip(points, count, color)


def draw_gauge_centered(cx: float, cy: float, height: float, alpha: float = 1.0) -> None:
  """Its ink box centered on (cx, cy), to sit beside other icons."""
  draw_gauge(cx - GAUGE_ASPECT * height / 2, cy - height / 2, height, alpha)


DIAL_DROP = 1 / 16  # of the height: the swoosh weighs the top, so a dial on the center looks high


def draw_gauge_on_dial(cx: float, cy: float, height: float, alpha: float = 1.0) -> None:
  """For a round button: the dial's center on (cx, cy), dropped a touch to look centered, so dial,
  swoosh and button ring read as one; centring the ink box sets the dial low and right instead."""
  s = height / (_BOTTOM - _TOP)
  draw_gauge(cx + _LEFT * s, cy + (_TOP + DIAL_DROP * (_BOTTOM - _TOP)) * s, height, alpha)


class SpeedAssistIcon(Widget):
  """The gauge as a status bar icon, its rect exactly its ink."""
  def __init__(self, height: int = STATUS_ICON_HEIGHT):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, round(GAUGE_ASPECT * height), float(height)))
    self.set_enabled(False)

  def _render(self, _) -> None:
    draw_gauge(self._rect.x, self._rect.y, self._rect.height, STATUS_ICON_ALPHA)
