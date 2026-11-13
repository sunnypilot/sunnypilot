"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.selfdrive.ui.mici.layouts.onboarding import QRCodeWidget
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationCircleButton
from openpilot.selfdrive.ui.sunnypilot.layouts.ccnc_port_eol import CCNC_PORT_EOL_URL
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.scroller import Scroller


class MiciCcncPortEolNotice(Scroller):
  def __init__(self, on_ack: Callable[[], None], on_switch: Callable[[], None], car_name: str | None):
    super().__init__()
    check = gui_app.texture("icons_mici/setup/driver_monitoring/dm_check.png", 64, 64)
    if car_name:
      self._scroller.add_widgets([
        GreyBigButton("officially\nsupported", "scroll to continue",
                      gui_app.texture("icons_mici/setup/green_info.png", 64, 64)),
        GreyBigButton(car_name.lower(), "is supported on master"),
        GreyBigButton("", "ccnc-port is no longer updated."),
        GreyBigButton("switch to staging", "to keep getting updates"),
        BigConfirmationCircleButton("switch to\nstaging", gui_app.texture("icons_mici/settings/device/update.png", 64, 64), on_switch),
        GreyBigButton("scan the QR code", "for details"),
        QRCodeWidget(CCNC_PORT_EOL_URL),
        BigConfirmationCircleButton("not\nnow", check, on_ack),
      ])
    else:
      self._scroller.add_widgets([
        GreyBigButton("no longer\nupdated", "scroll to continue",
                      gui_app.texture("icons_mici/setup/green_info.png", 64, 64)),
        GreyBigButton("", "ccnc-port will not receive any more functional updates. ccNC support is moving to master."),
        GreyBigButton("scan the QR code", "to see what to do"),
        QRCodeWidget(CCNC_PORT_EOL_URL),
        BigConfirmationCircleButton("I\nunderstand", check, on_ack),
      ])

  def _render(self, _):
    rl.draw_rectangle_rec(self._rect, rl.BLACK)
    super()._render(_)
