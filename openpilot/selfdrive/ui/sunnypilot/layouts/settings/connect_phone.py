"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math
import time

import pyray as rl

from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import device
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.sunnypilot.system.connect_phone import WINDOW_SECONDS, display_name, format_code, read_window, write_request
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

POLL_INTERVAL = 0.25
START_TIMEOUT = 15
STALE_SECONDS = 3
CLOSE_REASON_MESSAGES = {
  "granted": tr_noop("Phone connected."),
  "denied": tr_noop("Phone not connected."),
  "no_answer": tr_noop("Phone not connected: Allow was not tapped in time."),
  "phone_left": tr_noop("Phone not connected: the phone disconnected."),
  "wrong_codes": tr_noop("Phone not connected: too many wrong codes. Try again."),
  "limit": tr_noop("Phone not connected: 8 phones are already connected. Remove one first."),
  "timeout": tr_noop("The connect window timed out. Try again."),
  "bluetooth_off": tr_noop("Bluetooth is off. Turn Bluetooth on to connect a phone."),
  "no_key": tr_noop("The device key is unavailable. Reboot and try again."),
}


class ConnectPhoneLayout(PairingDialog):
  def __init__(self):
    super().__init__()
    self._params = Params()
    self._name = display_name(self._params)
    self._close_btn.set_click_callback(self._close_screen)
    self._started = False
    self._closed = False
    self._seq = 0
    self._opened_at = 0.0
    self._matched_at = 0.0
    self._window: dict | None = None
    self._last_poll = float("-inf")
    self._qr_source = ""
    self._check_dialog: ConfirmDialog | None = None
    self._check_shown_for: float | None = None

  def show_event(self):
    super().show_event()
    device.set_override_interactive_timeout(WINDOW_SECONDS + 10)
    # a tick, not _update_state: it has to keep polling while the Allow dialog is on top
    gui_app.add_nav_stack_tick(self._tick)
    if not self._started:
      self._started = True
      self._seq = write_request(self._params, "open")
      self._opened_at = time.monotonic()

  def hide_event(self):
    super().hide_event()
    gui_app.remove_nav_stack_tick(self._tick)
    device.set_override_interactive_timeout(None)
    if self._seq and not self._closed:
      write_request(self._params, "cancel")
    self._closed = True

  def _update_state(self):
    pass  # stock closes itself once the device is paired to comma connect

  def _tick(self):
    if self._closed:
      return
    now = time.monotonic()
    if now - self._last_poll >= POLL_INTERVAL:
      self._last_poll = now
      window = read_window(self._params)
      if window and window.get("seq") == self._seq:
        self._window = window
        self._matched_at = now
        if window.get("state") == "closed":
          self._on_closed(window.get("reason", ""))
          return
        self._sync_check_dialog(window.get("prompt") or {})

    if self._window is not None and self._window.get("state") == "open":
      if not self._window.get("held") and now >= self._window.get("deadline", 0.0):
        self._on_closed("timeout")
      elif self._matched_at and now - self._matched_at > STALE_SECONDS:
        self._finish(None)
    elif now - self._opened_at > START_TIMEOUT:
      write_request(self._params, "cancel")
      self._finish(tr("Bluetooth did not start"))

  def _sync_check_dialog(self, prompt: dict):
    if prompt.get("step") == "allow" and self._check_shown_for != prompt.get("until"):
      self._check_shown_for = prompt.get("until")
      text = tr("Code {}\nIs the same code on your phone?").format(prompt.get("check", ""))
      self._check_dialog = ConfirmDialog(text, tr("Allow"), tr("Deny"), callback=self._answer)
      gui_app.push_widget(self._check_dialog)
    elif prompt.get("step") != "allow" and self._check_dialog is not None:
      gui_app.pop_widgets_to(self, instant=True)
      self._check_dialog = None

  def _answer(self, result: DialogResult):
    self._check_dialog = None
    write_request(self._params, "allow" if result == DialogResult.CONFIRM else "deny")

  def _on_closed(self, reason: str):
    message = CLOSE_REASON_MESSAGES.get(reason)
    self._finish(tr(message) if message else None)

  def _finish(self, message: str | None):
    self._closed = True
    gui_app.pop_widgets_to(self, instant=True)
    self._close_screen()
    if message:
      gui_app.push_widget(ConfirmDialog(message, tr("OK"), cancel_text=""))

  def _close_screen(self):
    if gui_app.get_active_widget() is self:
      gui_app.pop_widget()

  def _get_pairing_url(self) -> str:
    return self._qr_source

  def _check_qr_refresh(self):
    qr = (self._window or {}).get("qr", "") if self._is_open() else ""
    if qr and qr != self._qr_source:
      self._qr_source = qr
      self._generate_qr_code()

  def _is_open(self) -> bool:
    return self._window is not None and self._window.get("state") == "open" and not self._window.get("held")

  def _render(self, rect: rl.Rectangle) -> int:
    # copied from PairingDialog._render: stock hardcodes its title and steps there
    rl.clear_background(rl.Color(224, 224, 224, 255))
    self._check_qr_refresh()

    margin = 70
    content_rect = rl.Rectangle(rect.x + margin, rect.y + margin, rect.width - 2 * margin, rect.height - 2 * margin)
    y = content_rect.y
    close_size = 80
    pad = 20
    self._close_btn.render(rl.Rectangle(content_rect.x - pad, y - pad, close_size + pad * 2, close_size + pad * 2))
    y += close_size + 40

    title_font = gui_app.font(FontWeight.NORMAL)
    left_width = int(content_rect.width * 0.5 - 15)
    title_wrapped = wrap_text(title_font, tr("Connect a phone to {}").format(self._name), 75, left_width)
    rl.draw_text_ex(title_font, "\n".join(title_wrapped), rl.Vector2(content_rect.x, y), 75, 0.0, rl.BLACK)
    y += len(title_wrapped) * 75 + 60

    remaining_height = content_rect.height - (y - content_rect.y)
    right_width = content_rect.width // 2 - 20
    self._render_instructions(rl.Rectangle(content_rect.x, y, left_width, remaining_height))

    qr_size = min(right_width, content_rect.height) - 40
    qr_rect = rl.Rectangle(content_rect.x + left_width + 40 + (right_width - qr_size) // 2, content_rect.y, qr_size, qr_size)
    if self._is_open():
      self._render_qr_code(qr_rect)
    else:
      text = tr("Connecting phone") if self._window is not None and self._window.get("held") else tr("Starting Bluetooth")
      rl.draw_rectangle_rounded(qr_rect, 0.1, 20, rl.Color(240, 240, 240, 255))
      font = gui_app.font(FontWeight.BOLD)
      size = measure_text_cached(font, text, 47)
      rl.draw_text_ex(font, text, rl.Vector2(qr_rect.x + (qr_rect.width - size.x) / 2, qr_rect.y + (qr_rect.height - size.y) / 2), 47, 0,
                      rl.BLACK)
    return -1

  def _render_instructions(self, rect: rl.Rectangle) -> None:
    window = self._window if self._is_open() else None
    instructions = [
      tr("Open the sunnylink app and tap Connect phone"),
      tr("Scan the QR code on the right, or type {}").format(format_code(int(window["code"]))) if window else tr("Scan the QR code on the right"),
      tr("Check that both screens show the same code, then tap Allow"),
    ]
    font = gui_app.font(FontWeight.BOLD)
    y = rect.y
    for i, text in enumerate(instructions):
      circle_radius = 25
      circle_x = rect.x + circle_radius + 15
      text_x = rect.x + circle_radius * 2 + 40
      wrapped = wrap_text(font, text, 47, int(rect.width - (circle_radius * 2 + 40)))
      text_height = len(wrapped) * 47
      circle_y = y + text_height // 2
      rl.draw_circle(int(circle_x), int(circle_y), circle_radius, rl.Color(70, 70, 70, 255))
      number = str(i + 1)
      number_size = measure_text_cached(font, number, 30)
      rl.draw_text_ex(font, number, (int(circle_x - number_size.x // 2), int(circle_y - number_size.y // 2)), 30, 0, rl.WHITE)
      rl.draw_text_ex(font, "\n".join(wrapped), rl.Vector2(text_x, y), 47, 0.0, rl.BLACK)
      y += text_height + 50

    if window:
      remaining = max(0, math.ceil(window.get("deadline", 0.0) - time.monotonic()))
      rl.draw_text_ex(gui_app.font(FontWeight.NORMAL), tr("Time left {}:{:02d}").format(remaining // 60, remaining % 60),
                      rl.Vector2(rect.x, y), 47, 0.0, rl.Color(70, 70, 70, 255))
