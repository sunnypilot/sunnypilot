"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroll_panel_sp import GuiScrollPanel2SP


class MiciMainLayoutSP(MiciMainLayout):
  def __init__(self):
    super().__init__()
    scroller = self._scroller
    scroller.scroll_panel = GuiScrollPanel2SP(scroller._horizontal, handle_out_of_bounds=not scroller._snap_items)

  def _should_auto_scroll_to_onroad(self) -> bool:
    return not self._onroad_layout.is_on_info_panel()
