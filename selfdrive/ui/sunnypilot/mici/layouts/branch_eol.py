"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.selfdrive.ui.mici.layouts.onboarding import QRCodeWidget
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationCircleButton
from openpilot.selfdrive.ui.sunnypilot.layouts.branch_eol import BRANCH_EOL_URL
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.scroller import Scroller


class MiciBranchEolNotice(Scroller):
  def __init__(self, on_ack: Callable[[], None]):
    super().__init__()
    self._scroller.add_widgets([
      GreyBigButton("no longer\nupdated", "scroll to continue",
                    gui_app.texture("icons_mici/setup/green_info.png", 64, 64)),
      GreyBigButton("", "This branch will not receive any more functional updates."),
      GreyBigButton("switch to", "hkg-angle-steering-2025"),
      GreyBigButton("scan the QR code", "to see what to do"),
      QRCodeWidget(BRANCH_EOL_URL),
      BigConfirmationCircleButton("I\nunderstand", gui_app.texture("icons_mici/setup/driver_monitoring/dm_check.png", 64, 64), on_ack),
    ])

  def _render(self, _):
    rl.draw_rectangle_rec(self._rect, rl.BLACK)
    super()._render(_)
