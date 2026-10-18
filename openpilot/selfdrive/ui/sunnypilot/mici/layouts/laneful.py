"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiToggle
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller

# above 1.0 the pull overshoots lane center and ping-pongs
STRENGTHS = {"off": 0.0, "gentle": 0.5, "firm": 1.0}


class LanefulStrengthToggle(BigMultiToggle):
  """Tap to cycle LanefulStrength, like the driving personality toggle."""
  def __init__(self):
    super().__init__("laneful strength", list(STRENGTHS), select_callback=self._on_select,
                     description="Nudges the car toward lane center.\n" +
                                 "Firm centers faster than gentle.")
    self.refresh()

  def refresh(self):
    strength = ui_state.params.get("LanefulStrength", return_default=True)
    self.set_value(min(STRENGTHS, key=lambda k: abs(STRENGTHS[k] - strength)))

  def _on_select(self, value: str):
    ui_state.params.put("LanefulStrength", STRENGTHS[value])


class LanefulLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._strength = LanefulStrengthToggle()
    self._scroller.add_widget(self._strength)

  def show_event(self):
    super().show_event()
    self._strength.refresh()
