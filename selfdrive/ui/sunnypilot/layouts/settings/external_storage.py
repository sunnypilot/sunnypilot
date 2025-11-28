"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
import threading
import subprocess
import copy
from enum import Enum
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.system.hardware import PC
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.list_view import (
  ItemAction,
  ListItem,
  BUTTON_HEIGHT,
  BUTTON_BORDER_RADIUS,
  BUTTON_FONT_SIZE,
  BUTTON_WIDTH,
)

VALUE_FONT_SIZE = 48


# ──────────────────────────────────────────────────────────────────────────────
# STATE MACHINE
# ──────────────────────────────────────────────────────────────────────────────
class ExternalStorageState(Enum):
  DISABLED = tr_noop("DISABLED")
  LOADING = tr_noop("LOADING")
  CHECK = tr_noop("CHECK")
  MOUNT = tr_noop("MOUNT")
  UNMOUNT = tr_noop("UNMOUNT")
  FORMAT = tr_noop("FORMAT")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ACTION ITEM
# ──────────────────────────────────────────────────────────────────────────────
class ExternalStorageAction(ItemAction):
  MAX_WIDTH = 500

  def __init__(self):
    super().__init__(self.MAX_WIDTH, True)

    self._params = Params()
    self._error_message = ""
    self._text_font = gui_app.font(FontWeight.NORMAL)

    self._button = Button(
      "",
      click_callback=self._handle_button_click,
      button_style=ButtonStyle.LIST_ACTION,
      border_radius=BUTTON_BORDER_RADIUS,
      font_size=BUTTON_FONT_SIZE,
    )

    self._value_text = ""   # left-side display value
    self._formatting = False
    self._refresh_pending = False

    self._state = ExternalStorageState.CHECK
    self._refresh_state()

    # run initial refresh
    self.refresh()

  # Propagate touch handling to sub-button
  def set_touch_valid_callback(self, callback):
    def wrapped():
      if self._state == ExternalStorageState.DISABLED:
        return False
      return callback()
    super().set_touch_valid_callback(wrapped)
    self._button.set_touch_valid_callback(wrapped)


  # ────────────────────────────────────────────────────────────────────────────
  # EXEC HELPERS
  # ────────────────────────────────────────────────────────────────────────────

  def _run(self, cmd: str) -> bool:
    return subprocess.call(["sh", "-c", cmd]) == 0

  def _run_output(self, cmd: str) -> str:
    try:
      out = subprocess.check_output(["sh", "-c", cmd], universal_newlines=True)
      return out.strip()
    except:
      return ""

  # ────────────────────────────────────────────────────────────────────────────
  # BUTTON RENDER
  # ────────────────────────────────────────────────────────────────────────────

  def _render(self, rect: rl.Rectangle) -> bool:
    # Show error dialog if needed
    if self._error_message:
      msg = copy.copy(self._error_message)
      gui_app.set_modal_overlay(alert_dialog(msg))
      self._error_message = ""

    # Draw left-side status text (value text)
    if self._value_text:
      text_size = measure_text_cached(self._text_font, self._value_text, VALUE_FONT_SIZE)
      rl.draw_text_ex(
        self._text_font,
        self._value_text,
        (rect.x + rect.width - BUTTON_WIDTH - text_size.x - 30,
         rect.y + (rect.height - text_size.y) / 2),
        VALUE_FONT_SIZE,
        1.0,
        rl.Color(170, 170, 170, 255),
      )

    # Draw the action button on the right
    button_rect = rl.Rectangle(
      rect.x + rect.width - BUTTON_WIDTH,
      rect.y + (rect.height - BUTTON_HEIGHT) / 2,
      BUTTON_WIDTH,
      BUTTON_HEIGHT
    )
    self._button.set_rect(button_rect)
    self._button.set_text(tr(self._state.value))

    # Button enabled only when NOT LOADING and NOT DISABLED
    self._button.set_enabled(self._state not in (ExternalStorageState.LOADING,
                                                 ExternalStorageState.DISABLED))

    self._button.render(button_rect)
    return False

  # ────────────────────────────────────────────────────────────────────────────
  # STATE MACHINE REFRESH
  # ────────────────────────────────────────────────────────────────────────────

  def _refresh_state(self):
    if PC:
      self._state = ExternalStorageState.DISABLED
      self._button.set_enabled(False)
      self._value_text = ""

  def debounced_refresh(self):
    if self._refresh_pending:
      return
    self._refresh_pending = True

    def _timer():
      import time
      time.sleep(0.25)
      self._refresh_pending = False
      self.refresh()

    threading.Thread(target=_timer, daemon=True).start()

  def refresh(self):
    def _work():
      is_mounted = self._run("findmnt -n /mnt/external_realdata")
      has_drive = self._run("lsblk -f /dev/sdg")
      has_fs = self._run("lsblk -f /dev/sdg1 | grep -q ext4")
      has_label = self._run("blkid /dev/sdg1 | grep -q 'LABEL=\"openpilot\"'")

      info = ""
      if is_mounted and has_label:
        info = self._run_output(
          "df -h /mnt/external_realdata | awk 'NR==2 {print $3 \"/\" $2}'"
        )

      def apply():
        if self._formatting:
          self._value_text = tr("formatting")
          self._state = ExternalStorageState.FORMAT
          return

        if not has_drive:
          self._value_text = tr("insert drive")
          self._state = ExternalStorageState.CHECK

        elif not has_fs or not has_label:
          self._value_text = tr("needs format")
          self._state = ExternalStorageState.FORMAT

        elif is_mounted:
          self._value_text = info
          self._state = ExternalStorageState.UNMOUNT

        else:
          self._value_text = tr("drive detected")
          self._state = ExternalStorageState.MOUNT

      apply()

    threading.Thread(target=_work, daemon=True).start()

  # ────────────────────────────────────────────────────────────────────────────
  # ACTION HANDLERS
  # ────────────────────────────────────────────────────────────────────────────

  def _handle_button_click(self):
    st = self._state

    if st == ExternalStorageState.DISABLED:
      return

    if st in (ExternalStorageState.CHECK, ExternalStorageState.MOUNT):
      self.mount_storage()

    elif st == ExternalStorageState.UNMOUNT:
      self.unmount_storage()

    elif st == ExternalStorageState.FORMAT:
      gui_app.set_modal_overlay(
        alert_dialog(
          tr("Are you sure you want to format this drive? This will erase all data."),
          confirm_text=tr("Format"),
          callback=self._confirm_format,
        )
      )

  def _confirm_format(self, result: DialogResult):
    if result == DialogResult.CONFIRM:
      self.format_storage()

  # ────────────────────────────────────────────────────────────────────────────
  # MOUNT
  # ────────────────────────────────────────────────────────────────────────────

  def mount_storage(self):
    self._value_text = tr("mounting")
    self._state = ExternalStorageState.LOADING

    def _work():
      cmd = """
        sudo mount -o remount,rw / &&
        sudo mkdir -p /mnt/external_realdata &&
        (grep -q '/dev/sdg1 /mnt/external_realdata' /etc/fstab ||
         echo '/dev/sdg1 /mnt/external_realdata ext4 defaults,nofail 0 2' >> /etc/fstab) &&
        sudo systemctl daemon-reexec &&
        sudo mount /mnt/external_realdata &&
        sudo chown -R comma:comma /mnt/external_realdata &&
        sudo chmod -R 775 /mnt/external_realdata &&
        sudo mount -o remount,ro /
      """
      subprocess.call(["sh", "-c", cmd])
      self.debounced_refresh()

    threading.Thread(target=_work, daemon=True).start()

  # ────────────────────────────────────────────────────────────────────────────
  # UNMOUNT
  # ────────────────────────────────────────────────────────────────────────────

  def unmount_storage(self):
    self._value_text = tr("unmounting")
    self._state = ExternalStorageState.LOADING

    def _work():
      subprocess.call(["sh", "-c", "sudo umount /mnt/external_realdata"])
      self.debounced_refresh()

    threading.Thread(target=_work, daemon=True).start()

  # ────────────────────────────────────────────────────────────────────────────
  # FORMAT
  # ────────────────────────────────────────────────────────────────────────────

  def format_storage(self):
    self._formatting = True
    self._value_text = tr("formatting")
    self._state = ExternalStorageState.LOADING

    def _work():
      cmd = """
        sudo wipefs -a /dev/sdg &&
        sudo parted -s /dev/sdg mklabel gpt mkpart primary ext4 0% 100% &&
        sudo mkfs.ext4 -F -L openpilot /dev/sdg1
      """
      exitcode = subprocess.call(["sh", "-c", cmd])

      def apply():
        self._formatting = False
        if exitcode == 0:
          self.mount_storage()
        else:
          self._value_text = tr("needs format")
          self._state = ExternalStorageState.FORMAT

      apply()

    threading.Thread(target=_work, daemon=True).start()


# ──────────────────────────────────────────────────────────────────────────────
# LIST ITEM HELPER
# ──────────────────────────────────────────────────────────────────────────────

def external_storage_item(title: str | Callable[[], str], description: str | Callable[[], str]) -> ListItem:
  return ListItem(
    title=title,
    description=description,
    action_item=ExternalStorageAction()
  )
