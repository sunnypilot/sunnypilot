"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationCircleButton
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.scroller import NavScroller


class SunnylinkConsentPage(NavScroller):
  def __init__(self, on_accept: Callable | None = None, on_decline: Callable | None = None):
    super().__init__()

    self._accept_button = BigConfirmationCircleButton("enable\nsunnylink", gui_app.texture("icons_mici/setup/driver_monitoring/dm_check.png", 64, 64),
                                                      on_accept,  exit_on_confirm=False)

    self._decline_button = BigConfirmationCircleButton("disable\nsunnylink", gui_app.texture("icons_mici/setup/cancel.png", 64, 64),
                                                       on_decline, red=True, exit_on_confirm=False)

    self._scroller.add_widgets([
      GreyBigButton("sunnylink", "scroll to continue",
                    gui_app.texture("../../sunnypilot/selfdrive/assets/logo.png", 64, 64)),
      GreyBigButton("", "sunnylink enables secured remote access to your comma device from anywhere."),
      self._accept_button,
      self._decline_button,
    ])
