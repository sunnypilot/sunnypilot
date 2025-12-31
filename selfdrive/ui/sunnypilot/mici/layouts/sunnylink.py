"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from cereal import custom
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog, BigConfirmationDialogV2
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.onboarding import SunnylinkConsentPage
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.system.ui.lib.application import gui_app, MousePos
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import NavWidget
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.version import sunnylink_consent_version, sunnylink_consent_declined


class SunnylinkLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self._restore_in_progress = False
    self._backup_in_progress = False
    self._sunnylink_enabled = ui_state.params.get("SunnylinkEnabled")

    self._sunnylink_toggle = BigToggle(text=tr("enable sunnylink"),
                                       initial_state=self._sunnylink_enabled,
                                       toggle_callback=self._sunnylink_toggle_callback)
    self._sunnylink_sponsor_button = SunnylinkPairBigButton(sponsor_pairing=False)
    self._sunnylink_pair_button = SunnylinkPairBigButton(sponsor_pairing=True)
    self._backup_btn = BigButton(tr("backup settings"), "", "")
    self._backup_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=False))
    self._restore_btn = BigButton(tr("restore settings"), "", "")
    self._restore_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=True))
    self._sunnylink_uploader_toggle = BigToggle(text=tr("sunnylink uploader"), initial_state=False,
                                                toggle_callback=self._sunnylink_uploader_callback)

    self._scroller = Scroller([
      self._sunnylink_toggle,
      self._sunnylink_sponsor_button,
      self._sunnylink_pair_button,
      self._backup_btn,
      self._restore_btn,
      self._sunnylink_uploader_toggle
    ], snap_items=False)

  def _update_state(self):
    super()._update_state()
    self._sunnylink_enabled = ui_state.params.get("SunnylinkEnabled")
    self._sunnylink_toggle.set_checked(self._sunnylink_enabled)
    self._sunnylink_pair_button.set_visible(self._sunnylink_enabled)
    self._sunnylink_sponsor_button.set_visible(self._sunnylink_enabled)
    self._backup_btn.set_visible(self._sunnylink_enabled)
    self._restore_btn.set_visible(self._sunnylink_enabled)
    self._sunnylink_uploader_toggle.set_visible(self._sunnylink_enabled)
    self.handle_backup_restore_progress()

    if ui_state.sunnylink_state.is_sponsor():
      self._sunnylink_sponsor_button.set_text(tr("thanks"))
      self._sunnylink_sponsor_button.set_value(ui_state.sunnylink_state.get_sponsor_tier().name.lower())
      self._sunnylink_sponsor_button.set_enabled(False)
    else:
      self._sunnylink_sponsor_button.set_text(tr("sponsor"))
      self._sunnylink_sponsor_button.set_value("")

    if ui_state.sunnylink_state.is_paired():
      self._sunnylink_pair_button.set_text(tr("paired"))
    else:
      self._sunnylink_pair_button.set_text(tr("pair"))

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    ui_state.update_params()

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)

  @staticmethod
  def _sunnylink_toggle_callback(state: bool):
    sl_consent: bool = ui_state.params.get("CompletedSunnylinkConsentVersion") == sunnylink_consent_version
    sl_enabled: bool = ui_state.params.get("SunnylinkEnabled")

    def sl_terms_accepted():
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_version)
      ui_state.params.put_bool("SunnylinkEnabled", True)
      gui_app.set_modal_overlay(None)

    def sl_terms_declined():
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_declined)
      ui_state.params.put_bool("SunnylinkEnabled", False)
      gui_app.set_modal_overlay(None)

    if state and not sl_consent and not sl_enabled:
      sl_terms_dlg = SunnylinkConsentPage(on_accept=sl_terms_accepted, on_decline=sl_terms_declined)
      gui_app.set_modal_overlay(sl_terms_dlg)
    else:
      ui_state.params.put_bool("SunnylinkEnabled", state)

    ui_state.update_params()

  @staticmethod
  def _sunnylink_uploader_callback(state: bool):
    ui_state.params.put_bool("EnableSunnylinkUploader", state)

  def _handle_backup_restore_btn(self, restore: bool = False):
    lbl = tr("slide to restore") if restore else tr("slide to backup")
    icon = "icons_mici/settings/device/update.png"
    dlg = BigConfirmationDialogV2(lbl, icon, confirm_callback=self._restore_handler if restore else self._backup_handler)
    gui_app.set_modal_overlay(dlg)

  def _backup_handler(self):
    self._backup_in_progress = True
    self._backup_btn.set_enabled(False)
    ui_state.params.put_bool("BackupManager_CreateBackup", True)

  def _restore_handler(self):
    self._restore_in_progress = True
    self._restore_btn.set_enabled(False)
    ui_state.params.put("BackupManager_RestoreVersion", "latest")

  def handle_backup_restore_progress(self):
    sunnylink_backup_manager = ui_state.sm["backupManagerSP"]

    backup_status = sunnylink_backup_manager.backupStatus
    restore_status = sunnylink_backup_manager.restoreStatus
    backup_progress = sunnylink_backup_manager.backupProgress
    restore_progress = sunnylink_backup_manager.restoreProgress

    if self._backup_in_progress:
      self._restore_btn.set_enabled(False)
      self._backup_btn.set_enabled(False)

      if backup_status == custom.BackupManagerSP.Status.inProgress:
        self._backup_in_progress = True
        self._backup_btn.set_text(tr("backing up"))
        text = tr(f"{backup_progress}%")
        self._backup_btn.set_value(text)

      elif backup_status == custom.BackupManagerSP.Status.failed:
        self._backup_in_progress = False
        self._backup_btn.set_enabled(not ui_state.is_onroad())
        self._backup_btn.set_text(tr("backup"))
        self._backup_btn.set_value(tr("failed"))

      elif (backup_status == custom.BackupManagerSP.Status.completed or
            (backup_status == custom.BackupManagerSP.Status.idle and backup_progress == 100.0)):
        self._backup_in_progress = False
        gui_app.set_modal_overlay(BigDialog(title=tr("settings backed up"), description=""))
        self._backup_btn.set_enabled(not ui_state.is_onroad())

    elif self._restore_in_progress:
      self._restore_btn.set_enabled(False)
      self._backup_btn.set_enabled(False)

      if restore_status == custom.BackupManagerSP.Status.inProgress:
        self._restore_in_progress = True
        self._restore_btn.set_text(tr("restoring"))
        text = tr(f"{restore_progress}%")
        self._restore_btn.set_value(text)

      elif restore_status == custom.BackupManagerSP.Status.failed:
        self._restore_in_progress = False
        self._restore_btn.set_enabled(not ui_state.is_onroad())
        self._restore_btn.set_text(tr("restore"))
        self._restore_btn.set_value(tr("failed"))
        gui_app.set_modal_overlay(BigDialog(title=tr("unable to restore"), description="try again later."))

      elif (restore_status == custom.BackupManagerSP.Status.completed or
            (restore_status == custom.BackupManagerSP.Status.idle and restore_progress == 100.0)):
        self._restore_in_progress = False
        gui_app.set_modal_overlay(BigConfirmationDialogV2(
          title="slide to restart", icon="icons_mici/settings/device/reboot.png",
          confirm_callback=lambda: gui_app.request_close()))

    else:
      can_enable = self._sunnylink_enabled and not ui_state.is_onroad()
      self._backup_btn.set_enabled(can_enable)
      self._backup_btn.set_text(tr("backup settings"))
      self._backup_btn.set_value("")
      self._restore_btn.set_enabled(can_enable)
      self._restore_btn.set_text(tr("restore settings"))
      self._restore_btn.set_value("")


class SunnylinkPairBigButton(BigButton):
  def __init__(self, sponsor_pairing: bool = False):
    self.sponsor_pairing = sponsor_pairing
    super().__init__("", "", "")

  def _update_state(self):
    super()._update_state()

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    dlg: BigDialog | SunnylinkPairingDialog | None = None
    if UNREGISTERED_SUNNYLINK_DONGLE_ID == (ui_state.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID):
      dlg = BigDialog(tr("sunnylink Dongle ID not found. Please reboot & try again."), "")
    elif self.sponsor_pairing:
      dlg = SunnylinkPairingDialog(sponsor_pairing=True)
    elif not self.sponsor_pairing:
      dlg = SunnylinkPairingDialog(sponsor_pairing=False)
    if dlg:
      gui_app.set_modal_overlay(dlg)
