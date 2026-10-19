"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
import pyray as rl
from functools import partial

from openpilot.cereal import custom
from openpilot.common.qrcode import make_texture
from openpilot.common.swaglog import cloudlog
from openpilot.common.version import sunnylink_consent_version, sunnylink_consent_declined
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog, BigConfirmationDialog, BigDialogBase
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.onboarding import SunnylinkConsentPage
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.sunnylink_pairing_dialog import SunnylinkPairingDialog
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
from openpilot.system.ui.lib.application import gui_app, MousePos, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.scroller import NavScroller

class SunnylinkInfo(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    self.device_id_header = UnifiedLabel(tr("device id"), 48, max_width=max_width, text_color=header_color,
                                         font_weight=FontWeight.DISPLAY, shimmer=True)
    self.device_id_text = UnifiedLabel(UNREGISTERED_SUNNYLINK_DONGLE_ID, 32, max_width=max_width, text_color=subheader_color,
                                       font_weight=FontWeight.ROMAN, scroll=True)

    self.sponsor_header = UnifiedLabel(tr("sponsor tier"), 48, max_width=max_width, text_color=header_color,
                                       font_weight=FontWeight.DISPLAY, shimmer=True)
    self.sponsor_text = UnifiedLabel("N/A", 32, max_width=max_width, text_color=subheader_color, font_weight=FontWeight.ROMAN)

  def _render(self, _):
    self.device_id_header.set_position(self._rect.x + 20, self._rect.y - 10)
    self.device_id_header.render()

    self.device_id_text.set_position(self._rect.x + 20, self._rect.y + 68 - 25)
    self.device_id_text.render()

    self.sponsor_header.set_position(self._rect.x + 20, self._rect.y + 114 - 30)
    self.sponsor_header.render()

    self.sponsor_text.set_position(self._rect.x + 20, self._rect.y + 161 - 25)
    self.sponsor_text.render()

class SunnylinkLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._restore_in_progress = False
    self._backup_in_progress = False
    self._sunnylink_enabled = ui_state.params.get("SunnylinkEnabled")

    self._sunnylink_info = SunnylinkInfo()

    self._sunnylink_toggle = BigToggle(text=tr("enable sunnylink"),
                                       initial_state=self._sunnylink_enabled,
                                       toggle_callback=self._sunnylink_toggle_callback)
    self._sunnylink_sponsor_button = SunnylinkPairBigButton(sponsor_pairing=False)
    self._sunnylink_pair_button = SunnylinkPairBigButton(sponsor_pairing=True)
    self._backup_btn = BigButton(tr("backup settings"), "")
    self._backup_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=False))
    self._restore_btn = BigButton(tr("restore settings"), "")
    self._restore_btn.set_click_callback(lambda: self._handle_backup_restore_btn(restore=True))
    self._sunnylink_uploader_toggle = BigToggle(text=tr("sunnylink uploader"), initial_state=False,
                                                toggle_callback=self._sunnylink_uploader_callback)

    self._local_toggle = BigToggle(text=tr("local connections"), initial_state=False,
                                   toggle_callback=self._local_connections_callback)
    self._mobile_app_btn = BigButton(tr("sunnylink local"), "")
    self._mobile_app_btn.set_click_callback(lambda: gui_app.push_widget(LocalAppsPanelMici()))

    self._scroller.add_widgets([
      self._sunnylink_info,
      self._sunnylink_toggle,
      self._sunnylink_sponsor_button,
      self._sunnylink_pair_button,
      self._local_toggle,
      self._mobile_app_btn,
      self._backup_btn,
      self._restore_btn,
      self._sunnylink_uploader_toggle
    ])

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

    self._sunnylink_info.device_id_text.set_text(ui_state.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID)
    self._sunnylink_info.sponsor_text.set_text(ui_state.sunnylink_state.get_sponsor_tier().name.lower() or "N/A")
    self._sunnylink_info.set_visible(self._sunnylink_enabled)

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

    local_enabled = ui_state.params.get_bool("SunnylinkLocalEnabled")
    self._local_toggle.set_visible(self._sunnylink_enabled)
    self._local_toggle.set_checked(local_enabled)
    self._mobile_app_btn.set_visible(self._sunnylink_enabled and local_enabled)

  def show_event(self):
    super().show_event()
    ui_state.update_params()
    ui_state.sunnylink_state.set_settings_open(True)

  def hide_event(self):
    super().hide_event()
    ui_state.sunnylink_state.set_settings_open(False)

  @staticmethod
  def _sunnylink_toggle_callback(state: bool):
    sl_consent: bool = ui_state.params.get("CompletedSunnylinkConsentVersion") == sunnylink_consent_version
    sl_enabled: bool = ui_state.params.get("SunnylinkEnabled")

    def sl_terms_accepted():
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_version)
      ui_state.params.put_bool("SunnylinkEnabled", True)
      gui_app.pop_widget()

    def sl_terms_declined():
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_declined)
      ui_state.params.put_bool("SunnylinkEnabled", False)
      gui_app.pop_widget()

    if state and not sl_consent and not sl_enabled:
      sl_terms_dlg = SunnylinkConsentPage(on_accept=sl_terms_accepted, on_decline=sl_terms_declined)
      gui_app.push_widget(sl_terms_dlg)
    else:
      ui_state.params.put_bool("SunnylinkEnabled", state)
      if not state:
        clear_pairing_params()

    ui_state.update_params()

  @staticmethod
  def _sunnylink_uploader_callback(state: bool):
    ui_state.params.put_bool("EnableSunnylinkUploader", state)

  @staticmethod
  def _local_connections_callback(state: bool):
    ui_state.params.put_bool("SunnylinkLocalEnabled", state)
    ui_state.update_params()

  def _handle_backup_restore_btn(self, restore: bool = False):
    lbl = tr("slide to restore") if restore else tr("slide to backup")
    icon = gui_app.texture("icons_mici/settings/device/update.png", 64, 64)
    dlg = BigConfirmationDialog(lbl, icon, confirm_callback=self._restore_handler if restore else self._backup_handler)
    gui_app.push_widget(dlg)

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
        gui_app.push_widget(BigDialog(title=tr("settings backed up"), description=""))
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
        gui_app.push_widget(BigDialog(title=tr("unable to restore"), description="try again later."))

      elif (restore_status == custom.BackupManagerSP.Status.completed or
            (restore_status == custom.BackupManagerSP.Status.idle and restore_progress == 100.0)):
        self._restore_in_progress = False
        gui_app.push_widget(BigConfirmationDialog(
          title="slide to restart", icon=gui_app.texture("icons_mici/settings/device/reboot.png", 64, 64),
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
    super().__init__("")

  def _update_state(self):
    super()._update_state()

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    network_type = ui_state.sm["deviceState"].networkType

    dlg: BigDialog | SunnylinkPairingDialog | None = None

    if network_type == 0:
      dlg = BigDialog(tr("no internet"), tr("please connect to WiFi & try again"))
    elif UNREGISTERED_SUNNYLINK_DONGLE_ID == (ui_state.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID):
      dlg = BigDialog(tr("sunnylink dongle id not found"), tr("please reboot & try again"))
    elif self.sponsor_pairing:
      dlg = SunnylinkPairingDialog(sponsor_pairing=True)
    elif not self.sponsor_pairing:
      dlg = SunnylinkPairingDialog(sponsor_pairing=False)
    if dlg:
      gui_app.push_widget(dlg)


class LocalAppsPanelMici(NavScroller):

  def __init__(self):
    super().__init__()
    self._rows_cache: list[LocalAppRow] = []

    self._pair_app_btn = BigButton(tr("pair app"), "")
    self._pair_app_btn.set_click_callback(lambda: gui_app.push_widget(LocalPairingDialogMici()))

    self._revoke_all_btn = BigButton(tr("revoke all phones"), "")
    self._revoke_all_btn.set_click_callback(self._confirm_revoke_all)

    self._local_app_btns: list[BigButton] = []
    for i in range(MAX_LOCAL_APP_ROWS):
      btn = BigButton("", "")
      btn.set_click_callback(partial(self._confirm_unpair_row, i))
      self._local_app_btns.append(btn)

    self._scroller.add_widgets([self._pair_app_btn, self._revoke_all_btn, *self._local_app_btns])

  def _update_state(self):
    super()._update_state()
    grants = read_granted_apps()
    self._rows_cache = build_local_app_rows(grants, read_grant_meta(), time.monotonic())
    self._revoke_all_btn.set_visible(bool(grants))
    for i, btn in enumerate(self._local_app_btns):
      btn.set_visible(i < len(self._rows_cache))
      if i < len(self._rows_cache):
        row = self._rows_cache[i]
        btn.set_text(row.title)
        btn.set_value(row.subtitle)

  def _confirm_revoke_all(self):
    icon = gui_app.texture("icons_mici/settings/device/update.png", 64, 64)
    dlg = BigConfirmationDialog(
      tr("revoke all phones"),
      icon,
      confirm_callback=request_revoke_all,
      red=True,
    )
    gui_app.push_widget(dlg)

  def _confirm_unpair_row(self, index: int):
    rows = self._rows_cache
    if index >= len(rows):
      return
    row = rows[index]

    def unpair():
      # A request only: sunnylinkd revokes through its live authority on its next tick.
      request_revoke(row.app_id)

    icon = gui_app.texture("icons_mici/settings/device/update.png", 64, 64)
    dlg = BigConfirmationDialog(
      tr("slide to unpair"),
      icon,
      confirm_callback=unpair,
      red=True,
    )
    gui_app.push_widget(dlg)


class LocalPairingDialogMici(BigDialogBase):
  """Pairing for the small display. This dialog only requests the window the local daemon
  publishes and renders it; the phone scans it, enrolls through the cloud, then dials."""

  # sunnylinkd services the request about once a second; taking longer means it is not running.
  ARM_GRACE_S = 5.0

  def __init__(self):
    super().__init__()
    self._requested_at = time.monotonic()
    self._seen_qr = False
    self._qr_string: str | None = None
    self._qr_texture: rl.Texture | None = None
    self._request_window()
    self.set_back_callback(self._cancel)

    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    # One label doubles as the instruction and the live status: 240px of height has no room for a
    # title, an instruction and a status line beside a full-height QR. Scanning is the only way
    # in, and this payload is not something anyone could type from a screen.
    self._hint = UnifiedLabel(tr("scan this code in the sunnylink app"), font_size=26,
                              text_color=subheader_color, line_height=0.9)

  def _request_window(self) -> None:
    try:
      ui_state.params.put_bool(PAIRING_REQUEST_KEY, True, block=True)
    except Exception:
      cloudlog.exception("sunnylink.local_pairing.request_failed")

  def _cancel(self) -> None:
    # Params only: this process does not own the window, the daemon cancels it on its next tick.
    clear_pairing_params()

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
      # Standard polarity (dark modules, the encoder's own light quiet zone), not light-on-dark:
      # on a panel this small the code is dense enough already without asking every scanner to
      # handle an inverted symbol too.
      self._qr_texture = make_texture(qr)
      # The texture is drawn smaller than it is built, and the modules must stay hard-edged for
      # a camera to read them.
      rl.set_texture_filter(self._qr_texture, rl.TextureFilter.TEXTURE_FILTER_POINT)
    except Exception:
      cloudlog.exception("sunnylink.local_pairing.qr_texture_failed")

  def _update_state(self):
    super()._update_state()
    if self.is_dismissing:
      return
    if read_pairing_qr() is not None:
      self._seen_qr = True
      return
    # The daemon clears the published QR when the window ends (enrolled, expired or cancelled).
    if self._seen_qr or time.monotonic() - self._requested_at > self.ARM_GRACE_S:
      self.dismiss()

  def _render(self, _):
    self._refresh_qr_texture(read_pairing_qr())

    rect = self._rect
    # The QR takes the full height, the way the cloud pairing dialog sizes it and the only size the
    # code can be scanned at on this display. Four pixels of margin is the border the panel needs;
    # the quiet zone the scanner needs is inside the texture.
    pad = 4
    qr_size = int(rect.height - 2 * pad)
    if self._qr_texture is not None:
      qr_rect = rl.Rectangle(rect.x + pad, rect.y + pad, qr_size, qr_size)
      source = rl.Rectangle(0, 0, self._qr_texture.width, self._qr_texture.height)
      rl.draw_texture_pro(self._qr_texture, source, qr_rect, rl.Vector2(0, 0), 0, rl.WHITE)

    text_x = int(rect.x + pad + qr_size + 20)
    text_width = int(rect.x + rect.width - pad - text_x)

    discovered = latest_discovered_app()
    if discovered is not None:
      endpoint, age = discovered
      self._hint.set_text(endpoint if age < 2 else f"{endpoint} ({age}s)")
      self._hint.set_text_color(rl.Color(0, 255, 0, 255))
    else:
      self._hint.set_text(tr("scan this code in the sunnylink app"))
      self._hint.set_text_color(rl.Color(255, 255, 255, int(255 * 0.9 * 0.65)))
    self._hint.set_max_width(text_width)
    self._hint.set_position(text_x, rect.y + pad)
    self._hint.render()

  def __del__(self):
    if self._qr_texture is not None and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
