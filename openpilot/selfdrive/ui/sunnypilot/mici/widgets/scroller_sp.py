"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroll_panel_sp import GuiScrollPanel2SP


class ScrollerSP(Scroller):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    inner = self._scroller
    inner.scroll_panel = GuiScrollPanel2SP(inner._horizontal, handle_out_of_bounds=not inner._snap_items)
