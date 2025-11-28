"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import datetime
import os

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.layouts.settings.developer import DeveloperLayout
from openpilot.system.hardware import PC
from openpilot.system.hardware.hw import Paths
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.external_storage import external_storage_item

PREBUILT_PATH = os.path.join(Paths.comma_home(), "openpilot", "prebuilt") if PC else "/data/openpilot/prebuilt"


class DeveloperLayoutSP(DeveloperLayout):
  def __init__(self):
    super().__init__()
    self.error_log_path = os.path.join(Paths.crash_log_root(), "error.log")
    self._initialize_items()
    for item in self.items:
      self._scroller.add_widget(item)

  def _initialize_items(self):
    self.enable_github_runner_toggle = toggle_item_sp(tr("Enable GitHub runner service"), tr("Enables or disables the github runner service."),
                                                      param="EnableGithubRunner")

    self.enable_copyparty_toggle = toggle_item_sp(tr("Enable Copyparty service"),
                                                  tr("Copyparty is a very capable file server, you can use it to download your routes, view your logs " +
                                                     "and even make some edits on some files from your browser. " +
                                                     "Requires you to connect to your comma locally via it's IP."), param="EnableCopyparty")

    self.prebuilt_toggle = toggle_item_sp(tr("Enable Quickboot Mode"), "", param="QuickBootToggle", callback=self._on_prebuilt_toggled)

    self.error_log_btn = button_item(tr("Error Log"), tr("View"), tr("View the error log for sunnypilot crashes."), callback=self._on_error_log_clicked)

    self.external_storage = external_storage_item(tr("External Storage"), description=tr("Extend your comma device's storage by inserting a USB drive " +
                                                                                         "into the aux port."))

    self.items: list = [self.enable_github_runner_toggle, self.enable_copyparty_toggle, self.prebuilt_toggle, self.external_storage, self.error_log_btn,]

  def _on_prebuilt_toggled(self, state):
    if state:
      open(PREBUILT_PATH, 'w').close()
    elif os.path.exists(PREBUILT_PATH):
      os.remove(PREBUILT_PATH)

  def _on_delete_confirm(self, result):
    if result == DialogResult.CONFIRM:
      if os.path.exists(self.error_log_path):
        os.remove(self.error_log_path)

  def _on_error_log_closed(self, result, log_exists):
    if result == DialogResult.CONFIRM and log_exists:
      dialog2 = ConfirmDialog(tr("Would you like to delete this log?"), tr("Yes"), tr("No"), rich=False)
      gui_app.set_modal_overlay(dialog2, callback=self._on_delete_confirm)

  def _on_error_log_clicked(self):
    text = ""
    if os.path.exists(self.error_log_path):
      text = f"<b>{datetime.datetime.fromtimestamp(os.path.getmtime(self.error_log_path)).strftime('%d-%b-%Y %H:%M:%S').upper()}</b><br><br>"
      try:
        with open(self.error_log_path) as file:
          text += file.read()
      except Exception:
        pass
    dialog = ConfirmDialog(text, tr("OK"), cancel_text="", rich=True)
    gui_app.set_modal_overlay(dialog, callback=lambda result: self._on_error_log_closed(result, os.path.exists(self.error_log_path)))

  def _update_toggles(self):
    super()._update_toggles()
    disable_updates = ui_state.params.get_bool("DisableUpdates")
    is_release = self._is_release or ui_state.params.get_bool("IsReleaseSpBranch")

    self.prebuilt_toggle.set_visible(not (is_release or ui_state.params.get_bool("IsTestedBranch") or ui_state.params.get_bool("IsDevelopmentBranch")))
    self.prebuilt_toggle.action_item.set_enabled(disable_updates)
    ui_state.params.put_bool("QuickBootToggle", os.path.exists(PREBUILT_PATH))

    if disable_updates:
      self.prebuilt_toggle.set_description(tr("When toggled on, this creates a prebuilt file to allow accelerated boot times. When toggled off, it " +
                                              "removes the prebuilt file so compilation of locally edited cpp files can be made."))
    else:
      self.prebuilt_toggle.set_description(tr("Quickboot mode requires updates to be disabled.<br>Enable 'Disable Updates' in the Software panel first."))

    self.enable_github_runner_toggle.set_visible(not is_release)
    self.error_log_btn.set_visible(not is_release)
