"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Set Speed Assist's mark: a half dial with its needle parked on the set speed. While the assist lifts the
model's acceleration, the arc fills green from the left toward the needle, reaching it at the most the
personality's approach pace allows; the needle turns green as the fill arrives.

Sized off mici's side panel at scale 1: the dial is the lead car's 35 px wide with the car's 4 px line
weight, and a teardrop needle that stops short of the arc so the two never merge at this size.
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

# at scale 1, about the dial's center (raylib degrees: 0 right, clockwise, so 270 is straight up)
STROKE = 4.0                            # the car's roof and pillars are 3-4 px
DIAL_WIDTH = 35.0                       # the car's
RADIUS = (DIAL_WIDTH - STROKE) / 2      # of the stroke's center line
ARC_FROM, ARC_TO = 180.0, 360.0         # a half dial, its round caps level with the hub
NEEDLE_DEG = 315.0                      # the set speed, up and to the right
HUB_RADIUS = 3.5
NEEDLE_TIP_RADIUS = 1.25
NEEDLE_CLEARANCE = 2.0                  # tip to the arc's inner edge: half the stroke, so they never touch
NEEDLE_LENGTH = RADIUS - STROKE / 2 - NEEDLE_CLEARANCE  # center to the tip's end
DIAL_HEIGHT = RADIUS + STROKE / 2 + HUB_RADIUS  # ink: the arc's top to the hub's bottom
ARRIVAL = (0.85, 1.0)                   # the lift over which the needle turns green
SEGMENTS_PER_DEG = 1 / 5
FILL_STEP = 0.5                         # degrees: the fill's end snaps to this so its outlines cache (0.14 px at scale 1)

GREEN = WHEEL_GREEN
IDLE = rl.Color(255, 255, 255, round(255 * 0.35))  # an unlit distance bar
NEEDLE = rl.Color(255, 255, 255, round(255 * 0.9))  # a lit one
LIFT_RC = 0.3  # the lift lets go fast; ease it so the fill doesn't flicker


def _ring(r: float, angles: np.ndarray) -> np.ndarray:
  return np.column_stack((r * np.cos(angles), r * np.sin(angles)))


# a fill sweep is about 270 snapped ends per scale, and only one device UI's scale runs at a time
@lru_cache(maxsize=320)
def arc_outline(scale: float, a1: float) -> np.ndarray:
  """the arc's stroke from its start to a1 degrees about the dial's center, round caps at both ends"""
  r, h = RADIUS * scale, STROKE * scale / 2
  angles = np.radians(np.linspace(ARC_FROM, a1, max(2, math.ceil((a1 - ARC_FROM) * SEGMENTS_PER_DEG) + 1)))
  cap = np.linspace(0, math.pi, 9)
  end, start = angles[-1], angles[0]
  return np.vstack((_ring(r + h, angles), _ring(h, end + cap) + _ring(r, np.array([end])),
                    _ring(r - h, angles[::-1]), _ring(h, start + math.pi + cap) + _ring(r, np.array([start])))).astype(np.float32)


@lru_cache(maxsize=8)
def needle_outline(scale: float) -> np.ndarray:
  """the needle and hub as one teardrop: the hub's back half, tangents to the tip, the tip's front half"""
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
  """where the green ends, in degrees: from the arc's start to the needle"""
  return ARC_FROM + (NEEDLE_DEG - ARC_FROM) * float(np.clip(lift, 0.0, 1.0))


def needle_level(lift: float) -> float:
  return float(np.clip((lift - ARRIVAL[0]) / (ARRIVAL[1] - ARRIVAL[0]), 0.0, 1.0))


def draw_dial(cx: float, top: float, scale: float = 1.0, lift: float = 0.0, alpha: float = 1.0,
              track: rl.Color = IDLE, needle: rl.Color = NEEDLE, lit: rl.Color = GREEN) -> None:
  """The dial with its ink's top center at (cx, top)."""
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
  """The lift on the model's acceleration over the personality's approach ceiling, 0..1. Only while
  openpilot drives longitudinal: not under MADS lateral-only."""
  sm = ui_state.sm
  long_engaged = ui_state.has_longitudinal_control and ui_state.started and sm['selfdriveState'].enabled
  if not long_engaged or not sm.valid['longitudinalPlanSP']:
    return 0.0
  lift = sm['longitudinalPlanSP'].setSpeedAssist.lift
  # the lift never goes negative, and the ceiling's floor is 0.5 m/s^2
  return float(np.clip(lift / approach_ceiling(sm['carState'].vEgo, sm['selfdriveState'].personality), 0.0, 1.0))


class SpeedAssistLift:
  """The eased lift, stepped once per frame."""
  def __init__(self):
    self._filter = FirstOrderFilter(0.0, LIFT_RC, 1 / gui_app.target_fps)

  def update(self) -> float:
    return self._filter.update(lift_fraction() if ui_state.speed_assist else 0.0)
