"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from cereal import custom
from openpilot.selfdrive.ui.sunnypilot.layouts.onboarding import SunnylinkConsentPage
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.sunnypilot.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.widgets.button import ButtonStyle, Button
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.list_view import dual_button_item
from openpilot.system.ui.widgets.scroller_tici import Scroller, LineSeparator
from openpilot.system.version import sunnylink_consent_version


class SunnylinkHeader(Widget):
  def __init__(self):
    super().__init__()

    self._title = UnifiedLabel(
      text="🚀 sunnylink 🚀",
      font_size=90,
      font_weight=FontWeight.AUDIOWIDE,
      text_color=rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      wrap_text=False,
      elide=False
    )

    self._description = UnifiedLabel(
      text=tr("For secure backup, restore, and remote configuration"),
      font_size=40,
      font_weight=FontWeight.LIGHT,
      text_color=rl.Color(0, 255, 0, 255),  # Green
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      wrap_text=True,
      elide=False
    )

    self._sponsor_msg = UnifiedLabel(
      text=tr("Sponsorship isn't required for basic backup/restore") + "\n" +
           tr("Click the Sponsor button for more details"),
      font_size=35,
      font_weight=FontWeight.LIGHT,
      text_color=rl.Color(255, 165, 0, 255),  # Orange
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      wrap_text=True,
      elide=False
    )

    self._padding = 20
    self._spacing = 10

  def set_parent_rect(self, parent_rect: rl.Rectangle) -> None:
    super().set_parent_rect(parent_rect)

    content_width = int(parent_rect.width - (self._padding * 2))

    title_height = self._title.get_content_height(content_width)
    desc_height = self._description.get_content_height(content_width)
    sponsor_height = self._sponsor_msg.get_content_height(content_width)

    total_height = (self._padding + title_height + self._spacing +
                    desc_height + self._spacing + sponsor_height + self._padding)

    self._rect.width = parent_rect.width
    self._rect.height = total_height

  def _render(self, rect: rl.Rectangle):
    content_width = rect.width - (self._padding * 2)
    current_y = rect.y + self._padding

    # Render title
    title_height = self._title.get_content_height(int(content_width))
    title_rect = rl.Rectangle(rect.x + self._padding, current_y, content_width, title_height)
    self._title.render(title_rect)
    current_y += title_height + self._spacing

    # Render description
    desc_height = self._description.get_content_height(int(content_width))
    desc_rect = rl.Rectangle(rect.x + self._padding, current_y, content_width, desc_height)
    self._description.render(desc_rect)
    current_y += desc_height + self._spacing

    # Render sponsor message
    sponsor_height = self._sponsor_msg.get_content_height(int(content_width))
    sponsor_rect = rl.Rectangle(rect.x + self._padding, current_y, content_width, sponsor_height)
    self._sponsor_msg.render(sponsor_rect)


class SunnylinkDescriptionItem(Widget):
  def __init__(self):
    super().__init__()
    self._description = UnifiedLabel(
      text="",
      font_size=40,
      font_weight=FontWeight.LIGHT,
      text_color=rl.WHITE,
      alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
      alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP,
      wrap_text=True,
      elide=False,
    )
    self._padding = 20

  def set_parent_rect(self, parent_rect: rl.Rectangle) -> None:
    super().set_parent_rect(parent_rect)
    desc_height = self._description.get_content_height(int(parent_rect.width)) + self._padding * 2

    self._rect.width = parent_rect.width
    self._rect.height = desc_height

  def set_text(self, text: str):
    self._description.set_text(text)

  def set_color(self, color: rl.Color):
    self._description.set_text_color(color)

  def _render(self, rect: rl.Rectangle):
    content_width = rect.width - (self._padding * 2)

    desc_height = self._description.get_content_height(int(content_width))
    desc_rect = rl.Rectangle(rect.x + self._padding, rect.y, content_width, desc_height)
    self._description.render(desc_rect)


class SunnylinkLayout(Widget):
  def __init__(self):
    super().__init__()

    self._sunnylink_pairing_dialog: SunnylinkPairingDialog | None = None
    self._restore_in_progress = False
    self._backup_in_progress = False
    self._sunnylink_enabled = ui_state.params.get("SunnylinkEnabled")

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._sunnylink_toggle = toggle_item_sp(
      title=tr("Enable sunnylink"),
      description=tr("This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that."),
      param="SunnylinkEnabled",
      callback=self._sunnylink_toggle_callback
    )

    self._sunnylink_description = SunnylinkDescriptionItem()
    self._sunnylink_description.set_visible(False)

    self._sponsor_btn = button_item_sp(
      title=tr("Sponsor Status"),
      button_text=tr("SPONSOR"),
      description=tr(
        "Become a sponsor of sunnypilot to get early access to sunnylink features when they become available."),
      callback=lambda: self._handle_pair_btn(False)
    )
    self._pair_btn = button_item_sp(
      title=tr("Pair GitHub Account"),
      button_text=tr("Not Paired"),
      description=tr(
        "Pair your GitHub account to grant your device sponsor benefits, including API access on sunnylink."),
      callback=lambda: self._handle_pair_btn(True)
    )
    self._sunnylink_uploader_toggle = toggle_item_sp(
      title=tr("Enable sunnylink uploader (infrastructure test)"),
      description=tr("Enable sunnylink uploader to allow sunnypilot to upload your driving data to sunnypilot servers. ") +
                  tr("(Only for highest tiers, and does NOT bring ANY benefit to you yet. We are just testing data volume.)"),
      param="EnableSunnylinkUploader"
    )
    self._sunnylink_backup_restore_buttons = dual_button_item(
      description="",
      left_text=tr("Backup Settings"),
      right_text=tr("Restore Settings"),
      left_callback=self._handle_backup_btn,
      right_callback=self._handle_restore_btn
    )
    self._backup_btn: Button = self._sunnylink_backup_restore_buttons.action_item.left_button  # store for easy individual access
    self._restore_btn: Button = self._sunnylink_backup_restore_buttons.action_item.right_button
    self._backup_btn.set_button_style(ButtonStyle.NORMAL)
    self._restore_btn.set_button_style(ButtonStyle.PRIMARY)

    items = [
      SunnylinkHeader(),
      LineSeparator(),
      self._sunnylink_toggle,
      self._sunnylink_description,
      LineSeparator(),
      self._sponsor_btn,
      LineSeparator(),
      self._pair_btn,
      LineSeparator(),
      self._sunnylink_uploader_toggle,
      LineSeparator(),
      self._sunnylink_backup_restore_buttons
    ]
    return items

  @staticmethod
  def _get_sunnylink_dongle_id() -> str:
    return ui_state.params.get("SunnylinkDongleId") or tr("N/A")

  def _handle_pair_btn(self, sponsor_pairing: bool = False):
    sunnylink_dongle_id = self._get_sunnylink_dongle_id()
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
      ui_state.params.put_bool("BackupManager_CreateBackup", True)

  def _restore_handler(self, dialog_result: int):
    if dialog_result == DialogResult.CONFIRM:
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
        text = tr(f"Backing up {backup_progress}%")
        self._backup_btn.set_text(text)

      elif backup_status == custom.BackupManagerSP.Status.failed:
        self._backup_in_progress = False
        self._backup_btn.set_enabled(not ui_state.is_onroad())
        self._backup_btn.set_text(tr("Backup Failed"))

      elif (backup_status == custom.BackupManagerSP.Status.completed or
            (backup_status == custom.BackupManagerSP.Status.idle and backup_progress == 100.0)):
        self._backup_in_progress = False
        dialog = alert_dialog(tr("Settings backup completed."))
        gui_app.set_modal_overlay(dialog)
        self._backup_btn.set_enabled(not ui_state.is_onroad())

    elif self._restore_in_progress:
      self._restore_btn.set_enabled(False)
      self._backup_btn.set_enabled(False)

      if restore_status == custom.BackupManagerSP.Status.inProgress:
        self._restore_in_progress = True
        text = tr(f"Restoring {restore_progress}%")
        self._restore_btn.set_text(text)

      elif restore_status == custom.BackupManagerSP.Status.failed:
        self._restore_in_progress = False
        self._restore_btn.set_enabled(not ui_state.is_onroad())
        self._restore_btn.set_text(tr("Restore Failed"))
        dialog = alert_dialog(tr("Unable to restore the settings, try again later."))
        gui_app.set_modal_overlay(dialog)

      elif (restore_status == custom.BackupManagerSP.Status.completed or
            (restore_status == custom.BackupManagerSP.Status.idle and restore_progress == 100.0)):
        self._restore_in_progress = False
        dialog = alert_dialog(tr("Settings restored. Confirm to restart the interface."))
        gui_app.set_modal_overlay(dialog, callback=lambda: gui_app.request_close())

    else:
      can_enable = self._sunnylink_enabled and not ui_state.is_onroad()
      self._backup_btn.set_enabled(can_enable)
      self._backup_btn.set_text(tr("Backup Settings"))
      self._restore_btn.set_enabled(can_enable)
      self._restore_btn.set_text(tr("Restore Settings"))

  def _sunnylink_toggle_callback(self, state: bool):
    sl_consent: bool = ui_state.params.get("CompletedSunnylinkConsentVersion") == sunnylink_consent_version
    sl_enabled: bool = ui_state.params.get_bool("SunnylinkEnabled")

    if state and not sl_consent and not sl_enabled:
      def on_consent_done():
        enabled = ui_state.params.get_bool("SunnylinkEnabled")
        self._update_description(enabled)
        gui_app.set_modal_overlay(None)

      sl_terms_dlg = SunnylinkConsentPage(done_callback=on_consent_done)
      gui_app.set_modal_overlay(sl_terms_dlg)
    else:
      ui_state.params.put_bool("SunnylinkEnabled", state)
      self._update_description(state)

  def _update_description(self, state: bool):
    if state:
      description = tr(
        "Welcome back!! We're excited to see you've enabled sunnylink again!")
      color = rl.Color(0, 255, 0, 255)  # Green
    else:
      description = ("😢 " + tr("Not going to lie, it's sad to see you disabled sunnylink") +
                     tr(", but we'll be here when you're ready to come back."))
      color = rl.Color(255, 165, 0, 255)  # Orange
    self._sunnylink_description.set_text(description)
    self._sunnylink_description.set_color(color)
    self._sunnylink_description.set_visible(True)
    self._sunnylink_toggle.show_description(False)

  def _update_state(self):
    super()._update_state()
    self._sunnylink_enabled = ui_state.params.get_bool("SunnylinkEnabled")
    self._sunnylink_toggle.set_right_value(tr("Dongle ID") + ": " + self._get_sunnylink_dongle_id())
    self._sunnylink_toggle.action_item.set_enabled(not ui_state.is_onroad())
    self._sunnylink_toggle.action_item.set_state(self._sunnylink_enabled)
    self._sunnylink_uploader_toggle.action_item.set_enabled(self._sunnylink_enabled)
    self.handle_backup_restore_progress()

    sponsor_btn_text = tr("THANKS ♥") if ui_state.sunnylink_state.is_sponsor() else tr("SPONSOR")
    tier_name = ui_state.sunnylink_state.get_sponsor_tier().name.capitalize() or tr("Not Sponsor")
    self._sponsor_btn.action_item.set_text(sponsor_btn_text)
    self._sponsor_btn.action_item.set_value(tier_name, ui_state.sunnylink_state.get_sponsor_tier_color())
    self._sponsor_btn.action_item.set_enabled(self._sunnylink_enabled)

    pair_btn_text = tr("Paired") if ui_state.sunnylink_state.is_paired() else tr("Not Paired")
    self._pair_btn.action_item.set_text(pair_btn_text)
    self._pair_btn.action_item.set_enabled(self._sunnylink_enabled)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    super().show_event()
    ui_state.sunnylink_state.set_settings_open(True)
    self._scroller.show_event()
    self._sunnylink_description.set_visible(False)

  def hide_event(self):
    super().hide_event()
    ui_state.sunnylink_state.set_settings_open(False)
