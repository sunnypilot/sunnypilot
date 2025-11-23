from cereal import custom
from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.system.ui.widgets.button import ButtonStyle, Button
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.list_view import button_item, dual_button_item
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


class SunnylinkLayout(Widget):
  def __init__(self):
    super().__init__()

    self._sunnylink_pairing_dialog: SunnylinkPairingDialog | None = None
    self._restore_in_progress = False
    self._backup_in_progress = False
    self._sunnylink_enabled = ui_state_sp.params.get("SunnylinkEnabled")

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._sunnylink_toggle = toggle_item_sp(
      title=tr("Enable sunnylink"),
      description=tr(
        "This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that."),
      param="SunnylinkEnabled",
      callback=self._sunnylink_toggle_callback
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
      button_text=tr("Not Paired"),
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
    self._backup_btn: Button = self._sunnylink_backup_restore_buttons.action_item.left_button # store for easy individual access
    self._restore_btn: Button = self._sunnylink_backup_restore_buttons.action_item.right_button
    self._backup_btn.set_button_style(ButtonStyle.NORMAL)
    self._restore_btn.set_button_style(ButtonStyle.PRIMARY)

    items = [
      self._sunnylink_toggle,
      self._sponsor_btn,
      self._pair_btn,
      self._sunnylink_uploader_toggle,
      self._sunnylink_backup_restore_buttons
    ]
    return items

  def _handle_pair_btn(self, sponsor_pairing: bool = False):
    sunnylink_dongle_id = ui_state_sp.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID
    if sunnylink_dongle_id == UNREGISTERED_SUNNYLINK_DONGLE_ID:
      gui_app.set_modal_overlay(alert_dialog(message=tr("sunnylink Dongle ID not found. ") +
                                                     tr("This may be due to weak internet connection or sunnylink registration issue. ") +
                                                     tr("Please reboot and try again.")))
    elif not self._sunnylink_pairing_dialog:
      self._sunnylink_pairing_dialog = SunnylinkPairingDialog(sponsor_pairing)
      gui_app.set_modal_overlay(self._sunnylink_pairing_dialog, callback=lambda result: setattr(self, '_sunnylink_pairing_dialog', None))

  def _handle_backup_btn(self):
    backup_dialog = ConfirmDialog(text=tr("Are you sure you want to backup your current sunnypilot settings?"), confirm_text="Backup")
    gui_app.set_modal_overlay(backup_dialog, callback=self._backup_handler)

  def _handle_restore_btn(self):
    self._restore_btn.set_enabled(False)
    restore_dialog = ConfirmDialog(text=tr("Are you sure you want to restore the last backed up sunnypilot settings?"), confirm_text="Restore")
    gui_app.set_modal_overlay(restore_dialog, callback=self._restore_handler)

  def _backup_handler(self, dialog_result: int):
    if dialog_result == DialogResult.CONFIRM:
      self._backup_in_progress = True
      self._backup_btn.set_enabled(False)
      ui_state_sp.params.put_bool("BackupManager_CreateBackup", True)

  def _restore_handler(self, dialog_result: int):
    if dialog_result == DialogResult.CONFIRM:
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
        text = tr(f"Backing up {backup_progress}%")
        self._backup_btn.set_text(text)

      elif backup_status == custom.BackupManagerSP.Status.failed:
        self._backup_in_progress = False
        self._backup_btn.set_enabled(not ui_state_sp.is_onroad())
        self._backup_btn.set_text(tr("Backup Failed"))

      elif backup_status == custom.BackupManagerSP.Status.completed:
        self._backup_in_progress = False
        dialog = alert_dialog(tr("Settings backup completed."))
        gui_app.set_modal_overlay(dialog)
        self._backup_btn.set_enabled(not ui_state_sp.is_onroad())

    elif self._restore_in_progress:
      if restore_status == custom.BackupManagerSP.Status.inProgress:
        self._restore_btn.set_enabled(False)
        text = tr(f"Restoring {restore_progress}%")
        self._restore_btn.set_text(text)

      elif restore_status == custom.BackupManagerSP.Status.failed:
        self._restore_in_progress = False
        self._restore_btn.set_enabled(not ui_state_sp.is_onroad())
        self._restore_btn.set_text(tr("Restore Failed"))
        dialog = alert_dialog(tr("Unable to restore the settings, try again later."))
        gui_app.set_modal_overlay(dialog)

      elif restore_status == custom.BackupManagerSP.Status.completed:
        self._restore_in_progress = False
        dialog = alert_dialog(tr("Settings restored. Confirm to restart the interface."))
        gui_app.set_modal_overlay(dialog, callback=lambda: {
          gui_app.request_close()
        })

    else:
      can_enable =  self._sunnylink_enabled and not ui_state_sp.is_onroad()
      self._backup_btn.set_enabled(can_enable)
      self._backup_btn.set_text(tr("Backup Settings"))
      self._restore_btn.set_enabled(can_enable)
      self._restore_btn.set_text(tr("Restore Settings"))

  def _sunnylink_toggle_callback(self, state: bool):
    ui_state_sp.params.put_bool("SunnylinkEnabled", state)
    ui_state_sp.update_params()

  def _update_state(self):
    super()._update_state()
    self._sunnylink_enabled = ui_state_sp.sunnylink_enabled
    self._sunnylink_toggle.action_item.set_enabled(not ui_state_sp.is_onroad())
    self._sunnylink_toggle.action_item.set_state(self._sunnylink_enabled)
    self._sunnylink_uploader_toggle.action_item.set_enabled(self._sunnylink_enabled)
    self.handle_backup_restore_progress()

    sponsor_btn_text = tr("THANKS ♥") if ui_state_sp.sunnylink_state.is_sponsor() else tr("SPONSOR")
    self._sponsor_btn.action_item.set_text(sponsor_btn_text)
    self._sponsor_btn.action_item.set_enabled(self._sunnylink_enabled)

    pair_btn_text = tr("Paired") if ui_state_sp.sunnylink_state.is_paired() else tr("Not Paired")
    self._pair_btn.action_item.set_text(pair_btn_text)
    self._pair_btn.action_item.set_enabled(self._sunnylink_enabled)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    ui_state_sp.update_params()
