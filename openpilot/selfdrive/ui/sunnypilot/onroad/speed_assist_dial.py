"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from functools import lru_cache

import numpy as np
import raylib_nb as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad.hud_renderer import WHEEL_GREEN
from openpilot.selfdrive.ui.mici.onroad.status import lerp_color
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.set_speed_assist import approach_ceiling
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.polygon import draw_polygon

# px at scale 1, matching mici's lead car. Degrees are raylib's, clockwise from the right
STROKE = 4.0
DIAL_WIDTH = 35.0
RADIUS = (DIAL_WIDTH - STROKE) / 2
ARC_FROM, ARC_TO = 180.0, 360.0
NEEDLE_DEG = 315.0
HUB_RADIUS = 3.5
NEEDLE_TIP_RADIUS = 1.25
NEEDLE_CLEARANCE = 2.0  # tip to the arc's inner edge
NEEDLE_LENGTH = RADIUS - STROKE / 2 - NEEDLE_CLEARANCE
DIAL_HEIGHT = RADIUS + STROKE / 2 + HUB_RADIUS
ARRIVAL = (0.85, 1.0)  # lift over which the needle turns green
SEGMENTS_PER_DEG = 1 / 5
FILL_STEP = 0.5  # degrees, so the fill outlines cache

GREEN = WHEEL_GREEN
IDLE = rl.Color(255, 255, 255, round(255 * 0.35))  # an unlit distance bar
NEEDLE = rl.Color(255, 255, 255, round(255 * 0.9))  # a lit one
LIFT_RC = 0.3  # the lift lets go fast, so ease the fill


def _ring(r: float, angles: np.ndarray) -> np.ndarray:
  return np.column_stack((r * np.cos(angles), r * np.sin(angles)))


@lru_cache(maxsize=320)  # ~270 snapped fill ends per scale
def arc_outline(scale: float, a1: float) -> np.ndarray:
  """Stroke outline from ARC_FROM to a1 degrees about the dial's center, with round caps"""
  r, h = RADIUS * scale, STROKE * scale / 2
  angles = np.radians(np.linspace(ARC_FROM, a1, max(2, math.ceil((a1 - ARC_FROM) * SEGMENTS_PER_DEG) + 1)))
  cap = np.linspace(0, math.pi, 9)
  end, start = angles[-1], angles[0]
  return np.vstack((_ring(r + h, angles), _ring(h, end + cap) + _ring(r, np.array([end])),
                    _ring(r - h, angles[::-1]), _ring(h, start + math.pi + cap) + _ring(r, np.array([start])))).astype(np.float32)


@lru_cache(maxsize=8)
def needle_outline(scale: float) -> np.ndarray:
  """Needle and hub as one teardrop outline"""
  a = math.radians(NEEDLE_DEG)
  hub, tip_r = HUB_RADIUS * scale, NEEDLE_TIP_RADIUS * scale
  d = (NEEDLE_LENGTH - NEEDLE_TIP_RADIUS) * scale  # center to the tip's center
  tip = (d * math.cos(a), d * math.sin(a))
  side = math.asin((hub - tip_r) / d)  # the tangent's tilt off the needle's axis
  front = [(tip[0] + tip_r * math.cos(a + q), tip[1] + tip_r * math.sin(a + q))
           for q in np.linspace(-math.pi / 2 - side, math.pi / 2 + side, 9)]
  back = [(hub * math.cos(a + q), hub * math.sin(a + q)) for q in np.linspace(math.pi / 2 + side, 3 * math.pi / 2 - side, 13)]
  return np.array(front + back, dtype=np.float32)


def _faded(color: rl.Color, alpha: float) -> rl.Color:
  return rl.Color(color.r, color.g, color.b, round(color.a * alpha))


def fill_to(lift: float) -> float:
  return ARC_FROM + (NEEDLE_DEG - ARC_FROM) * float(np.clip(lift, 0.0, 1.0))


def needle_level(lift: float) -> float:
  return float(np.clip((lift - ARRIVAL[0]) / (ARRIVAL[1] - ARRIVAL[0]), 0.0, 1.0))


def draw_dial(cx: float, top: float, scale: float = 1.0, lift: float = 0.0, alpha: float = 1.0,
              track: rl.Color = IDLE, needle: rl.Color = NEEDLE, lit: rl.Color = GREEN) -> None:
  """Draws the dial with its top center at (cx, top)."""
  if alpha < 1e-2:
    return
  screen = rl.Rectangle(0, 0, gui_app.width, gui_app.height)
  center = np.array([cx, top + (RADIUS + STROKE / 2) * scale], dtype=np.float32)
  key = round(scale, 3)
  draw_polygon(screen, arc_outline(key, ARC_TO) + center, color=_faded(track, alpha))
  if lift > 0.01:
    draw_polygon(screen, arc_outline(key, round(fill_to(lift) / FILL_STEP) * FILL_STEP) + center, color=_faded(lit, alpha))
  draw_polygon(screen, needle_outline(key) + center, color=_faded(lerp_color(needle, lit, needle_level(lift)), alpha))


def lift_fraction() -> float:
  """The lift over the personality's approach ceiling, 0..1, while openpilot controls longitudinal"""
  sm = ui_state.sm
  long_engaged = ui_state.has_longitudinal_control and ui_state.started and sm['selfdriveState'].enabled
  if not long_engaged or not sm.valid['longitudinalPlanSP']:
    return 0.0
  lift = sm['longitudinalPlanSP'].setSpeedAssist.lift
  # the ceiling is at least 0.5 m/s^2
  return float(np.clip(lift / approach_ceiling(sm['carState'].vEgo, sm['selfdriveState'].personality), 0.0, 1.0))


class SpeedAssistLift:
  """The eased lift, stepped once per frame."""
  def __init__(self):
    self._filter = FirstOrderFilter(0.0, LIFT_RC, 1 / gui_app.target_fps)

  def update(self) -> float:
    return self._filter.update(lift_fraction() if ui_state.speed_assist else 0.0)
