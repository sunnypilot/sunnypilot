"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad.hud_renderer import SET_SPEED_PERSISTENCE, HudRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.blind_spot_indicators import BlindSpotIndicators
from openpilot.selfdrive.ui.sunnypilot.onroad.speed_assist_badge import draw_gauge_centered
from openpilot.selfdrive.ui.ui_state import ChestnutState, UIStatus, ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.set_speed_assist import approach_ceiling
from openpilot.system.ui.lib.application import gui_app

# Set Speed Assist's gauge mirrors the steering wheel in the bottom-right corner
SPEED_ASSIST_HEIGHT = 44  # the wheel is 50, and round; the gauge's swoosh carries it to the same weight
# the HUD's idle and lit levels: armed draws like an unlit distance bar, and brightens to the
# wheel's 0.9 as the lift nears the most the personality's approach pace asks for at this speed
SPEED_ASSIST_ALPHA_IDLE = 0.35
SPEED_ASSIST_ALPHA_LIFT = 0.9


class HudRendererSP(HudRenderer):
  def __init__(self):
    super().__init__()
    self.blind_spot_indicators = BlindSpotIndicators()
    self._sp_engaged: bool = False
    # the wheel's filters, so the two corners come and go together
    self._speed_assist_shown_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps)
    self._speed_assist_y_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)
    # the lift lets go fast; ease the glow so it doesn't blink
    self._speed_assist_lift_filter = FirstOrderFilter(0.0, 0.3, 1 / gui_app.target_fps)

  def _update_state(self) -> None:
    super()._update_state()
    self.blind_spot_indicators.update()

    sp_engaged = ui_state.engaged
    if sp_engaged != self._sp_engaged:
      self._chestnut_fade_time = rl.get_time() if sp_engaged else 0
    self._sp_engaged = sp_engaged

  def _render(self, rect: rl.Rectangle) -> None:
    super()._render(rect)
    self.blind_spot_indicators.render(rect)
    self._draw_speed_assist(rect)

  def _chestnut_showing(self) -> bool:
    """The model icon wants the corner while loading, and for its persistence after a change
    (HudRenderer._draw_model_source)."""
    state = ui_state.chestnut_state
    if state == ChestnutState.LOADING:
      return True
    if state not in (ChestnutState.UNCOMPILED, ChestnutState.FAILED, ChestnutState.ACTIVE):
      return False
    return rl.get_time() - self._chestnut_fade_time < SET_SPEED_PERSISTENCE

  def _draw_speed_assist(self, rect: rl.Rectangle) -> None:
    # comes and goes with the wheel, and gives the corner to the right blind spot and the model icon
    wheel = self._txt_wheel
    shown = (ui_state.speed_assist_active and ui_state.status != UIStatus.DISENGAGED and
             not self.blind_spot_indicators.right_detected and not self._chestnut_showing())
    lift = self._speed_assist_lift_filter.update(self._speed_assist_lift_fraction() if shown else 0.0)
    alpha = self._speed_assist_shown_filter.update(float(shown)) * \
      (SPEED_ASSIST_ALPHA_IDLE + (SPEED_ASSIST_ALPHA_LIFT - SPEED_ASSIST_ALPHA_IDLE) * lift)
    y_offset = self._speed_assist_y_filter.update(0.0 if shown else wheel.height / 2)
    if alpha < 1e-2:
      return
    draw_gauge_centered(rect.x + rect.width - 21 - wheel.width / 2, rect.y + rect.height - 14 - wheel.height / 2 + y_offset,
                        SPEED_ASSIST_HEIGHT, alpha)

  @staticmethod
  def _speed_assist_lift_fraction() -> float:
    """The lift on the model's acceleration over the personality's approach ceiling, 0..1."""
    sm = ui_state.sm
    if not sm.valid['longitudinalPlanSP']:
      return 0.0
    lift = sm['longitudinalPlanSP'].setSpeedAssist.lift
    return min(lift / approach_ceiling(sm['carState'].vEgo, sm['selfdriveState'].personality), 1.0)

  def _has_blind_spot_detected(self) -> bool:

    return self.blind_spot_indicators.detected
