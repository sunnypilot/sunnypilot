import pyray as rl
from collections.abc import Callable
from cereal import log, custom
from openpilot.common.params_pyx import Params
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog, BigConfirmationDialogV2
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.system.ui.lib.multilang import tr

from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigButton, BigToggle
from openpilot.system.ui.lib.application import gui_app, MousePos
from openpilot.system.ui.widgets import NavWidget
from openpilot.selfdrive.ui.layouts.settings.common import restart_needed_callback
from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp



class SunnylinkLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self._restore_in_progress = False
    self._backup_in_progress = False
    self._sunnylink_enabled = ui_state_sp.params.get("SunnylinkEnabled")

    self._sunnylink_toggle = BigToggle(text="enable sunnylink",
                                       initial_state=self._sunnylink_enabled,
                                       toggle_callback=self._sunnylink_toggle_callback)
    self._sunnylink_pair_button = SunnylinkPairBigButton()
    self._sunnylink_sponsor_button = SunnylinkPairBigButton(sponsor_pairing=True)
    self._backup_btn = BigButton("backup settings", "", "")
    self._backup_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=False))
    self._restore_btn = BigButton("restore settings", "", "")
    self._restore_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=True))

    self._scroller = Scroller([
      self._sunnylink_toggle,
      self._sunnylink_pair_button,
      self._sunnylink_sponsor_button,
      self._backup_btn,
      self._restore_btn,
    ], snap_items=False)

  def _update_state(self):
    super()._update_state()
    self._sunnylink_enabled = ui_state_sp.sunnylink_enabled
    self._sunnylink_toggle.set_text("disable sunnylink" if self._sunnylink_enabled else "enable sunnylink")
    self._sunnylink_pair_button.set_visible(self._sunnylink_enabled)
    self._sunnylink_sponsor_button.set_visible(self._sunnylink_enabled)
    self._backup_btn.set_visible(self._sunnylink_enabled)
    self._restore_btn.set_visible(self._sunnylink_enabled)
    self.handle_backup_restore_progress()

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    ui_state_sp.update_params()

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)

  def _sunnylink_toggle_callback(self, state: bool):
    ui_state_sp.params.put_bool("SunnylinkEnabled", state)
    ui_state_sp.update_params()

  def _handle_backup_restore_btn(self, restore:bool = False):
    lbl = tr("slide to restore") if restore else tr("slide to backup")
    icon = "icons_mici/settings/network/new/trash.png"
    dlg = BigConfirmationDialogV2(lbl, icon, confirm_callback=None)
    gui_app.set_modal_overlay(dlg, callback=self._restore_handler if restore else self._backup_handler)

  def _backup_handler(self, dialog_result: int):
    self._backup_in_progress = True
    self._backup_btn.set_enabled(False)
    ui_state_sp.params.put_bool("BackupManager_CreateBackup", True)

  def _restore_handler(self, dialog_result: int):
    self._restore_in_progress = True
    self._restore_btn.set_enabled(False)
    ui_state_sp.params.put("BackupManager_RestoreVersion", "latest")

  def handle_backup_restore_progress(self):
    sunnylink_backup_manager = ui_state_sp.sm["backupManagerSP"]

    backup_status = sunnylink_backup_manager.backupStatus
    restore_status = sunnylink_backup_manager.restoreStatus
    backup_progress = sunnylink_backup_manager.backupProgress
    restore_progress = sunnylink_backup_manager.restoreProgress

    if self._backup_in_progress:
      if backup_status == custom.BackupManagerSP.Status.inProgress:
        text = tr(f"{backup_progress}%")
        self._backup_btn.set_value(text)

      elif backup_status == custom.BackupManagerSP.Status.failed:
        self._backup_in_progress = False
        self._backup_btn.set_enabled(not ui_state_sp.is_onroad())
        self._backup_btn.set_value(tr("Failed"))

      elif backup_status == custom.BackupManagerSP.Status.completed:
        self._backup_in_progress = False
        dialog = BigDialog(title=tr("Settings backed up"), description="")
        gui_app.set_modal_overlay(dialog)
        self._backup_btn.set_enabled(not ui_state_sp.is_onroad())

    elif self._restore_in_progress:
      if restore_status == custom.BackupManagerSP.Status.inProgress:
        self._restore_btn.set_enabled(False)
        text = tr(f"{restore_progress}%")
        self._restore_btn.set_value(text)

      elif restore_status == custom.BackupManagerSP.Status.failed:
        self._restore_in_progress = False
        self._restore_btn.set_enabled(not ui_state_sp.is_onroad())
        self._restore_btn.set_value(tr("Failed"))
        dialog = BigDialog(title=tr("Unable to restore"), description="Try again later.")
        gui_app.set_modal_overlay(dialog)

      elif restore_status == custom.BackupManagerSP.Status.completed:
        self._restore_in_progress = False
        dialog = BigConfirmationDialogV2("slide to restart", "", confirm_callback=None)
        gui_app.set_modal_overlay(dialog, callback=lambda: {
          gui_app.request_close()
        })

    else:
      can_enable = self._sunnylink_enabled and not ui_state_sp.is_onroad()
      self._backup_btn.set_enabled(can_enable)
      self._backup_btn.set_text(tr("backup settings"))
      self._restore_btn.set_enabled(can_enable)
      self._restore_btn.set_text(tr("restore settings"))



class SunnylinkPairBigButton(BigButton):
  def __init__(self, sponsor_pairing: bool = False):
    self.sponsor_pairing = sponsor_pairing
    super().__init__("", "", "")

  def _update_state(self):
    self.set_value("")
    self.set_enabled(True)

    if self.sponsor_pairing:
      if ui_state_sp.sunnylink_state.is_sponsor():
        self.set_text("thanks")
        self.set_value("for sponsoring")
        self.set_enabled(False)
      else:
        self.set_text("sponsor")
    else:
      if ui_state_sp.sunnylink_state.is_paired():
        self.set_text(tr("paired"))
        self.set_enabled(False)
      else:
        self.set_text(tr("pair"))

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    dlg: BigDialog | SunnylinkPairingDialog | None = None
    if UNREGISTERED_SUNNYLINK_DONGLE_ID == (ui_state_sp.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID):
      dlg = BigDialog(tr("sunnylink Dongle ID not found. Please reboot & try again."), "")
    elif self.sponsor_pairing and not ui_state_sp.sunnylink_state.is_sponsor():
      dlg = SunnylinkPairingDialog(sponsor_pairing=True)
    elif not self.sponsor_pairing and not ui_state_sp.sunnylink_state.is_paired():
      dlg = SunnylinkPairingDialog(sponsor_pairing=False)
    if dlg:
      gui_app.set_modal_overlay(dlg)
