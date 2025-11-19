"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.system.ui.widgets.button import ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.list_view import button_item, dual_button_item
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


class SunnylinkLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    self._sunnylink_pairing_dialog: SunnylinkPairingDialog | None = None

    self.sunnylink_enabled = self._params.get_bool("SunnylinkEnabled")

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._sunnylink_toggle = toggle_item_sp(
      title=tr("Enable sunnylink"),
      description=tr(
        "This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that."),
      param="SunnylinkEnabled"
    )
    self._sponsor_btn = button_item(
      title=tr("Sponsor Status"),
      button_text=tr("SPONSOR"),
      description=tr(
        "Become a sponsor of sunnypilot to get early access to sunnylink features when they become available."),
      callback=lambda: self._handle_pair_btn(False)
    )
    self._pair_btn = button_item(
      title=tr("Pair GitHub Account"),
      button_text=tr("PAIR"),
      description=tr(
        "Pair your GitHub account to grant your device sponsor benefits, including API access on sunnylink."),
      callback=lambda: self._handle_pair_btn(True)
    )
    self._sunnylink_uploader_toggle = toggle_item_sp(
      title=tr("Enable sunnylink uploader (infrastructure test)"),
      description=tr("Enable sunnylink uploader to allow sunnypilot to upload your driving data to sunnypilot servers.") +
                  tr(" (Only for highest tiers, and does NOT bring ANY benefit to you yet. We are just testing data volume.)"),
      param="EnableSunnylinkUploader"
    )
    self._sunnylink_backup_restore_buttons = dual_button_item(
      description="",
      left_text=tr("Backup Settings"),
      right_text=tr("Restore Settings"),
      left_callback=self._handle_backup_btn,
      right_callback=self._handle_restore_btn
    )
    self._sunnylink_backup_restore_buttons.action_item.left_button.set_button_style(ButtonStyle.NORMAL)
    self._sunnylink_backup_restore_buttons.action_item.right_button.set_button_style(ButtonStyle.NORMAL)

    items = [
      self._sunnylink_toggle,
      self._sponsor_btn,
      self._pair_btn,
      self._sunnylink_uploader_toggle,
      self._sunnylink_backup_restore_buttons
    ]
    return items

  def _handle_pair_btn(self, sponsor_pairing: bool = False):
    if not self._sunnylink_pairing_dialog:
      self._sunnylink_pairing_dialog = SunnylinkPairingDialog(sponsor_pairing)
    gui_app.set_modal_overlay(self._sunnylink_pairing_dialog, callback=lambda result: setattr(self, '_sunnylink_pairing_dialog', None))

  def _handle_backup_btn(self):
    gui_app.set_modal_overlay(alert_dialog(message=tr("Backup functionality is currently not available."
                                                      " It will be back once all settings are implemented on raylib.")))

  def _handle_restore_btn(self):
    gui_app.set_modal_overlay(alert_dialog(message=tr("Restore functionality is currently not available.")))

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
