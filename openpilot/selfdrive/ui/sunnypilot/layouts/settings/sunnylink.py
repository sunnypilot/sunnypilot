"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
import pyray as rl
from functools import partial
from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.qrcode import make_texture
from openpilot.common.swaglog import cloudlog
from openpilot.common.version import sunnylink_consent_version
from openpilot.selfdrive.ui.sunnypilot.layouts.onboarding import SunnylinkConsentPage
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.sunnypilot.sunnylink.athena.local_auth_daemon import (
  clear_pairing_params,
  read_grant_meta,
  read_granted_apps,
  read_pairing_qr,
  request_revoke,
  request_revoke_all,
)
from openpilot.sunnypilot.sunnylink.athena.local_app_rows import (
  MAX_LOCAL_APP_ROWS,
  LocalAppRow,
  build_local_app_rows,
)
from openpilot.sunnypilot.sunnylink.athena.local_discovery import latest_discovered_app
from openpilot.sunnypilot.sunnylink.athena.local_state import PAIRING_REQUEST_KEY
from openpilot.system.ui.lib.application import gui_app, FontWeight, TextAlignment, TextAlignmentVertical
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP, button_item_sp, toggle_item_sp
from openpilot.system.ui.sunnypilot.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
from openpilot.system.ui.widgets import Widget, DialogResult
from openpilot.system.ui.widgets.button import ButtonStyle, Button, IconButton
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.list_view import dual_button_item
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller, LineSeparator

# Read-only value colors used by the local-mode rows.
_LOCAL_DISCOVERED_COLOR = rl.Color(170, 170, 170, 255)  # grey: no app in sight
_LOCAL_ACTIVE_COLOR = rl.Color(0, 255, 0, 255)          # green: discovered / pairing code


class SunnylinkHeader(Widget):
  def __init__(self):
    super().__init__()

    self._title = UnifiedLabel(
      text="🚀 sunnylink 🚀",
      font_size=90,
      font_weight=FontWeight.AUDIOWIDE,
      text_color=rl.WHITE,
      alignment=TextAlignment.CENTER,
      alignment_vertical=TextAlignmentVertical.TOP,
      wrap_text=False,
      elide=False
    )

    self._description = UnifiedLabel(
      text=tr("For secure backup, restore, and remote configuration"),
      font_size=40,
      font_weight=FontWeight.NORMAL,
      text_color=rl.Color(0, 255, 0, 255),  # Green
      alignment=TextAlignment.CENTER,
      alignment_vertical=TextAlignmentVertical.TOP,
      wrap_text=True,
      elide=False
    )

    self._sponsor_msg = UnifiedLabel(
      text=tr("Sponsorship isn't required for basic backup/restore") + "\n" +
           tr("Click the Sponsor button for more details"),
      font_size=35,
      font_weight=FontWeight.NORMAL,
      text_color=rl.Color(255, 165, 0, 255),  # Orange
      alignment=TextAlignment.CENTER,
      alignment_vertical=TextAlignmentVertical.TOP,
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
      font_weight=FontWeight.NORMAL,
      text_color=rl.WHITE,
      alignment=TextAlignment.LEFT,
      alignment_vertical=TextAlignmentVertical.TOP,
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
    self._local_enabled = ui_state.params.get_bool("SunnylinkLocalEnabled")

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

    self._local_connections_toggle = toggle_item_sp(
      title=tr("Enable local connections"),
      description=tr("Let the sunnylink mobile app connect to this device over Wi-Fi. ") +
                  tr("Turn this off to stop the local daemon and keep sunnylink itself running."),
      param="SunnylinkLocalEnabled",
    )
    self._local_connections_toggle.set_visible(lambda: self._sunnylink_enabled)

    self._mobile_app_btn = button_item_sp(
      title=tr("Sunnylink Local Connections"),
      button_text=tr("CONFIGURE"),
      description=tr("Manage the mobile app(s) connected over Wi-Fi: pair a new app ") +
                  tr("or unpair existing ones."),
      callback=self._open_local_apps,
    )
    self._mobile_app_btn.set_visible(lambda: self._sunnylink_enabled and self._local_enabled)

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
      self._local_connections_toggle,
      LineSeparator(),
      self._mobile_app_btn,
      LineSeparator(),
      self._sunnylink_uploader_toggle,
      LineSeparator(),
      self._sunnylink_backup_restore_buttons,
    ]
    return items

  @staticmethod
  def _get_sunnylink_dongle_id() -> str:
    return ui_state.params.get("SunnylinkDongleId") or tr("N/A")

  def _handle_pair_btn(self, sponsor_pairing: bool = False):
    sunnylink_dongle_id = self._get_sunnylink_dongle_id()
    if sunnylink_dongle_id == UNREGISTERED_SUNNYLINK_DONGLE_ID:
      gui_app.push_widget(alert_dialog(message=tr("sunnylink Dongle ID not found. ") +
                                                     tr("This may be due to weak internet connection or sunnylink registration issue. ") +
                                                     tr("Please reboot and try again.")))
    elif not self._sunnylink_pairing_dialog:
      self._sunnylink_pairing_dialog = SunnylinkPairingDialog(sponsor_pairing)
      gui_app.push_widget(self._sunnylink_pairing_dialog)

  def _handle_backup_btn(self):
    backup_dialog = ConfirmDialog(text=tr("Are you sure you want to backup your current sunnypilot settings?"), confirm_text="Backup",
                                  callback=self._backup_handler)
    gui_app.push_widget(backup_dialog)

  def _handle_restore_btn(self):
    self._restore_btn.set_enabled(False)
    restore_dialog = ConfirmDialog(text=tr("Are you sure you want to restore the last backed up sunnypilot settings?"),
                                   confirm_text="Restore", callback=self._restore_handler)
    gui_app.push_widget(restore_dialog)

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
        gui_app.push_widget(dialog)
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
        gui_app.push_widget(dialog)

      elif (restore_status == custom.BackupManagerSP.Status.completed or
            (restore_status == custom.BackupManagerSP.Status.idle and restore_progress == 100.0)):
        self._restore_in_progress = False
        dialog = ConfirmDialog(tr("Settings restored. Confirm to restart the interface."), tr("OK"), cancel_text="", callback=lambda _: gui_app.request_close())
        gui_app.push_widget(dialog)

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
        gui_app.pop_widget()

      sl_terms_dlg = SunnylinkConsentPage(done_callback=on_consent_done)
      gui_app.push_widget(sl_terms_dlg)
    else:
      ui_state.params.put_bool("SunnylinkEnabled", state)
      if not state:
        clear_pairing_params()
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
    self._local_enabled = ui_state.params.get_bool("SunnylinkLocalEnabled")
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

  def _open_local_apps(self):
    gui_app.push_widget(SunnylinkLocalAppLayout())

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


class SunnylinkLocalAppLayout(Widget):

  def __init__(self):
    super().__init__()
    self._rows_cache: list[LocalAppRow] = []
    self._has_grants = False

    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(gui_app.pop_widget)

    self._pair_app_btn = button_item_sp(
      title=tr("Pair App"),
      button_text=tr("SCAN"),
      description=tr("Show a QR code the sunnylink app scans to enroll this phone's key. ") +
                  tr("The app must be signed in, and the code expires after 2 minutes."),
      callback=self._show_pairing_dialog,
    )

    self._revoke_all_btn = button_item_sp(
      title=tr("Unpair all phones"),
      button_text=tr("REVOKE ALL"),
      description=tr("Revoke every enrolled phone at once. Each phone must pair again ") +
                  tr("from the sunnylink app to reconnect."),
      callback=self._revoke_all,
    )
    self._revoke_all_btn.set_visible(lambda: self._has_grants)

    self._local_app_rows: list[ListItemSP] = []
    self._local_app_seps: list[LineSeparator] = []
    for i in range(MAX_LOCAL_APP_ROWS):
      row = button_item_sp(
        title=lambda i=i: self._row_title(i),
        button_text=tr("UNPAIR"),
        description=lambda i=i: self._row_subtitle(i),
        callback=partial(self._unpair_row, i),
      )
      sep = LineSeparator()
      row.set_visible(lambda i=i: self._local_row_visible(i))
      sep.set_visible(lambda i=i: self._local_row_visible(i))
      self._local_app_rows.append(row)
      self._local_app_seps.append(sep)

    items = [self._pair_app_btn, LineSeparator(), self._revoke_all_btn, LineSeparator()]
    for row, sep in zip(self._local_app_rows, self._local_app_seps, strict=True):
      items.extend((row, sep))
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _local_row_visible(self, i: int) -> bool:
    return i < len(self._rows_cache)

  def _row_title(self, i: int) -> str:
    return self._rows_cache[i].title if i < len(self._rows_cache) else ""

  def _row_subtitle(self, i: int) -> str:
    return self._rows_cache[i].subtitle if i < len(self._rows_cache) else ""

  def _show_pairing_dialog(self):
    gui_app.push_widget(SunnylinkLocalPairingDialog())

  def _revoke_all(self):
    def on_confirm(_dialog_result: int):
      # A request the daemon applies on its next tick.
      request_revoke_all()

    dialog = ConfirmDialog(
      text=tr("Revoke all phones?") + " " + tr("They will need to pair again from the app."),
      confirm_text=tr("Revoke all"),
      callback=on_confirm,
    )
    gui_app.push_widget(dialog)

  def _unpair_row(self, index: int):
    rows = self._rows_cache
    if index >= len(rows):
      return
    row = rows[index]

    def on_confirm(_dialog_result: int):
      # A request only: the daemon revokes through its live authority on its next tick, so a
      # phone enrolled after this row was read cannot be dropped by a stale snapshot.
      request_revoke(row.app_id)

    dialog = ConfirmDialog(
      text=tr("Unpair") + f" {row.title}? " + tr("You will need to enroll this phone again from the app."),
      confirm_text=tr("Unpair"),
      callback=on_confirm,
    )
    gui_app.push_widget(dialog)

  def _update_state(self):
    super()._update_state()
    grants = read_granted_apps()
    self._has_grants = bool(grants)
    self._rows_cache = build_local_app_rows(grants, read_grant_meta(), time.monotonic())

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()

  def hide_event(self):
    super().hide_event()
    self._scroller.hide_event()


class SunnylinkLocalPairingDialog(Widget):
  """Pairing: the phone scans this QR, enrolls through the cloud and only then dials the device
  over pinned TLS.

  The window belongs to the local daemon (another process): this dialog sets the arm request and
  renders the QR that gets published. The published QR is the window state — removing it (Cancel,
  or the daemon's own expiry) closes the window.
  """

  # sunnylinkd services the request about once a second; taking longer means it is not running.
  ARM_GRACE_S = 5.0

  def __init__(self):
    super().__init__()
    self._params = Params()
    self._requested_at = time.monotonic()
    self._seen_qr = False
    self._qr_string: str | None = None
    self._qr_texture: rl.Texture | None = None
    self._request_window()
    self._close_btn = IconButton(gui_app.texture("icons/close.png", 80, 80))
    self._close_btn.set_click_callback(self._cancel)

  def _request_window(self) -> None:
    try:
      self._params.put_bool(PAIRING_REQUEST_KEY, True, block=True)
    except Exception:
      cloudlog.exception("sunnylink.local_pairing.request_failed")

  def _cancel(self) -> None:
    # Params only: this process does not own the window, the daemon cancels it on its next tick.
    clear_pairing_params()
    gui_app.pop_widget()

  def _refresh_qr_texture(self, qr: str | None) -> None:
    """Regenerate the texture only when the published QR actually changed."""
    if qr == self._qr_string:
      return
    if self._qr_texture is not None and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
    self._qr_texture = None
    self._qr_string = qr
    if not qr:
      return
    try:
      self._qr_texture = make_texture(qr)
      # The texture is drawn smaller than it is built, and the modules must stay hard-edged for
      # a camera to read them.
      rl.set_texture_filter(self._qr_texture, rl.TextureFilter.TEXTURE_FILTER_POINT)
    except Exception:
      cloudlog.exception("sunnylink.local_pairing.qr_texture_failed")

  def _update_state(self):
    if read_pairing_qr() is not None:
      self._seen_qr = True
      return
    # The daemon clears the published QR when the window ends (enrolled, expired or cancelled).
    if self._seen_qr or time.monotonic() - self._requested_at > self.ARM_GRACE_S:
      gui_app.pop_widget()

  def _render(self, rect) -> int:
    rl.clear_background(rl.Color(224, 224, 224, 255))

    self._refresh_qr_texture(read_pairing_qr())

    margin = 70
    content_rect = rl.Rectangle(rect.x + margin, rect.y + margin,
                                rect.width - 2 * margin, rect.height - 2 * margin)
    y = content_rect.y

    close_size = 80
    pad = 20
    close_rect = rl.Rectangle(content_rect.x - pad, y - pad, close_size + pad * 2, close_size + pad * 2)
    self._close_btn.render(close_rect)
    y += close_size + 40

    # Two columns, the layout the cloud pairing dialog uses: the QR takes half the width and the
    # full height, which is 900px at this display's 2160x1080 — 31 px per module for the compact
    # 29-module pointer, read easily from any scanning distance.
    left_width = int(content_rect.width * 0.5 - 15)
    right_width = int(content_rect.width // 2 - 20)

    title_font = gui_app.font(FontWeight.NORMAL)
    title_wrapped = wrap_text(title_font, tr("Pair with mobile app"), 70, left_width)
    rl.draw_text_ex(title_font, "\n".join(title_wrapped), rl.Vector2(content_rect.x, y), 70, 0.0, rl.BLACK)
    y += len(title_wrapped) * 70 + 40

    qr_size = int(min(right_width, content_rect.height) - 40)
    qr_rect = rl.Rectangle(content_rect.x + left_width + 40 + (right_width - qr_size) / 2,
                           content_rect.y, qr_size, qr_size)
    card = rl.Rectangle(qr_rect.x - 10, qr_rect.y - 10, qr_rect.width + 20, qr_rect.height + 20)
    rl.draw_rectangle_rounded(card, 0.05, 10, rl.WHITE)
    if self._qr_texture is not None:
      source = rl.Rectangle(0, 0, self._qr_texture.width, self._qr_texture.height)
      rl.draw_texture_pro(self._qr_texture, source, qr_rect, rl.Vector2(0, 0), 0, rl.WHITE)

    # Left column: what to do. The QR is the only way to enroll, so what matters here is that the
    # steps are readable next to a code that is as large as the panel allows inside the QR's own
    # calm zone.
    hint_font = gui_app.font(FontWeight.NORMAL)
    hints = [
      tr("In the sunnylink app, open Local Connectivity → Pair a device."),
      tr("Sign in to the same sunnypilot account on both."),
      tr("The code expires after 2 minutes."),
    ] if self._qr_texture is not None else [tr("Preparing a secure pairing code…")]
    for hint in hints:
      wrapped = wrap_text(hint_font, hint, 38, left_width)
      rl.draw_text_ex(hint_font, "\n".join(wrapped), rl.Vector2(content_rect.x, y), 38, 0.0, rl.BLACK)
      y += len(wrapped) * 38 + 14

    discovered = latest_discovered_app()
    if discovered is not None:
      endpoint, age = discovered
      status = endpoint if age < 2 else f"{endpoint} ({age}s)"
      color = _LOCAL_ACTIVE_COLOR
    else:
      status = tr("Waiting for the phone…")
      color = _LOCAL_DISCOVERED_COLOR
    status_font = gui_app.font(FontWeight.NORMAL)
    rl.draw_text_ex(status_font, status, rl.Vector2(content_rect.x, y + 10), 40, 0.0, color)
    return -1

  def __del__(self):
    if self._qr_texture is not None and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
