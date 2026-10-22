"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
from openpilot.system.ui.widgets.scroller import NavScroller


class BlendfulLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._toggle = BigParamControl("blendful", "Blendful",
                                   description="Keeps the car centered in its lane.\n" +
                                               "Leans on the lane lines when they are clear, drives laneless when they are not.")
    self._scroller.add_widget(self._toggle)

  def show_event(self):
    super().show_event()
    self._toggle.refresh()
