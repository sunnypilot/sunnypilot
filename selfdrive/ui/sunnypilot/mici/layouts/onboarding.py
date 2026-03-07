"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

from openpilot.selfdrive.ui.mici.widgets.button import BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialogV2
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.scroller import NavScroller


class SunnylinkConsentPage(NavScroller):
  def __init__(self, on_accept: Callable | None = None, on_decline: Callable | None = None):
    super().__init__()

    def show_accept_dialog():
      gui_app.push_widget(BigConfirmationDialogV2("enable\nsunnylink", "icons_mici/setup/driver_monitoring/dm_check.png",
                                                  confirm_callback=on_accept))

    def show_decline_dialog():
      gui_app.push_widget(BigConfirmationDialogV2("disable\nsunnylink", "icons_mici/setup/cancel.png",
                                                  red=True, confirm_callback=on_decline))

    self._accept_button = BigCircleButton("icons_mici/setup/driver_monitoring/dm_check.png")
    self._accept_button.set_click_callback(show_accept_dialog)

    self._decline_button = BigCircleButton("icons_mici/setup/cancel.png", red=True)
    self._decline_button.set_click_callback(show_decline_dialog)

    self._scroller.add_widgets([
      GreyBigButton("sunnylink", "scroll to continue",
                    gui_app.texture("../../sunnypilot/selfdrive/assets/logo.png", 64, 64)),
      GreyBigButton("", "sunnylink enables secured remote access to your comma device from anywhere."),
      self._accept_button,
      self._decline_button,
    ])
