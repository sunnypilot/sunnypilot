"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiToggle, GreyBigButton
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller

# above 1.0 the pull overshoots lane center and ping-pongs
STRENGTHS = {"off": 0.0, "0.25": 0.25, "0.5": 0.5, "0.75": 0.75, "1.0": 1.0}


class LanefulStrengthToggle(BigMultiToggle):
  """Tap to cycle LanefulStrength. Value shown as text, so no option pills."""
  def __init__(self):
    super().__init__("laneful strength", list(STRENGTHS), select_callback=self._on_select)
    self.refresh()

  def refresh(self):
    strength = ui_state.params.get("LanefulStrength", return_default=True)
    self.set_value(min(STRENGTHS, key=lambda k: abs(STRENGTHS[k] - strength)))

  def _on_select(self, value: str):
    ui_state.params.put("LanefulStrength", STRENGTHS[value])

  def _draw_content(self, btn_y: float):
    BigButton._draw_content(self, btn_y)


class LanefulLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._strength = LanefulStrengthToggle()
    self._scroller.add_widgets([
      self._strength,
      GreyBigButton("", "Nudges the car toward the center of the lane lines."),
      GreyBigButton("", "Fades out when the lines are unclear and during lane changes."),
      GreyBigButton("", "0.5 is gentle. 1.0 centers fastest."),
    ])

  def show_event(self):
    super().show_event()
    self._strength.refresh()
