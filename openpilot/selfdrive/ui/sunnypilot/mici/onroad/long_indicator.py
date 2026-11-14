"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Set Speed Assist over mici's long indicator. Off, the car and bars sit where upstream puts them. On, the
dial joins the top of the stack at the bars' own pitch, and the group sits between the driver monitor (ink
bottom at 62) and the wheel (ink top at 178), a pixel above center: the wheel's glow and the monitor's
rounded base make equal gaps look closer at the bottom.
"""
import raylib_nb as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad.long_indicator import LongIndicator
from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_dial import DIAL_HEIGHT, SpeedAssistLift, draw_dial
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app

DM_BOTTOM, WHEEL_TOP = 62.0, 178.0
STACK_TOP, STACK_HEIGHT = 86.5, 71.0  # upstream's car (centered at 100, 27 tall) down to the third bar
DIAL_GAP = 6.0  # dial to car: the bars' pitch, so the dial reads as part of the stack
MARGIN = (WHEEL_TOP - DM_BOTTOM - DIAL_HEIGHT - DIAL_GAP - STACK_HEIGHT) / 2
OPTICAL_LIFT = 1.0
DIAL_TOP = DM_BOTTOM + MARGIN - OPTICAL_LIFT
STACK_SHIFT = DIAL_TOP + DIAL_HEIGHT + DIAL_GAP - STACK_TOP
SLIDE_RC = 0.25  # the status fade's


class LongIndicatorSP(LongIndicator):
  def __init__(self):
    super().__init__()
    self._speed_assist_filter = FirstOrderFilter(0.0, SLIDE_RC, 1 / gui_app.target_fps)
    self._speed_assist_lift = SpeedAssistLift()

  def _render(self, rect: rl.Rectangle) -> None:
    shown = self._speed_assist_filter.update(float(ui_state.speed_assist))
    shift = STACK_SHIFT * shown
    super()._render(rl.Rectangle(rect.x, rect.y + shift, rect.width, rect.height))
    # the dial rides down with the stack and fades in as the stack makes room, at the stack's own alpha
    # (super() zeroes it when there is no openpilot longitudinal)
    draw_dial(rect.x + rect.width / 2, rect.y + DIAL_TOP + shift - STACK_SHIFT, lift=self._speed_assist_lift.update(),
              alpha=self._alpha_filter.x * self._dim_filter.x * shown)
