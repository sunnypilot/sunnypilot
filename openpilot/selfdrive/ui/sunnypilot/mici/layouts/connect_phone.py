"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time

import pyray as rl

from openpilot.common.qrcode import make_texture
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationCircleButton, BigDialog
from openpilot.selfdrive.ui.ui_state import device, ui_state
from openpilot.sunnypilot.system.connect_phone import WINDOW_SECONDS, format_code, read_window, write_request
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.scroller import NavScroller

POLL_SECONDS = 0.25
START_TIMEOUT = 15  # seconds from open to the first window for this request
LOST_SECONDS = 3  # the daemon restarted mid-window and no longer reports our seq
INTERACTIVE_TIMEOUT = WINDOW_SECONDS + 10  # the offroad idle timeout would pop the screen mid-window


def _closed_message(reason: str) -> str | None:
  messages = {
    "granted": tr("phone connected"),
    "denied": tr("phone not connected"),
    "no_answer": tr("allow not tapped in time"),
    "phone_left": tr("phone disconnected"),
    "wrong_codes": tr("too many wrong codes"),
    "limit": tr("8 phones already connected"),
    "timeout": tr("connect timed out"),
    "bluetooth_off": tr("turn on bluetooth"),
    "no_key": tr("device key unavailable"),
  }
  return messages.get(reason)


def start_connect_phone() -> None:
  gui_app.push_widget(ConnectPhoneDialog())


class ConnectPhoneDialog(NavWidget):
  def __init__(self):
    super().__init__()
    self._params = ui_state.params
    self._seq = write_request(self._params, "open")
    self._opened_at = time.monotonic()
    self._next_poll = 0.0
    self._was_open = False
    self._lost_since: float | None = None
    self._window: dict | None = None
    self._closing = False
    self._check_shown_for: float | None = None
    self._qr_source = ""
    self._qr_texture: rl.Texture | None = None

    self._title = UnifiedLabel(tr("connect phone"), font_size=48, font_weight=FontWeight.BOLD,
                               text_color=rl.Color(255, 255, 255, int(255 * 0.9)), line_height=0.8)
    self._status = UnifiedLabel("", font_size=36, font_weight=FontWeight.ROMAN,
                                text_color=rl.Color(255, 255, 255, int(255 * 0.65)))
    self._code = UnifiedLabel("", font_size=48, font_weight=FontWeight.BOLD,
                              text_color=rl.Color(255, 255, 255, int(255 * 0.9)))

    self.set_back_callback(self._cancel)

  def show_event(self):
    super().show_event()
    device.set_override_interactive_timeout(INTERACTIVE_TIMEOUT)

  def hide_event(self):
    super().hide_event()
    device.set_override_interactive_timeout(None)
    if not self._closing:
      self._cancel()

  def _update_state(self):
    super()._update_state()
    if self._closing:
      return
    now = time.monotonic()
    if now < self._next_poll:
      return
    self._next_poll = now + POLL_SECONDS

    window = read_window(self._params)
    # the request seq guards against a window left over from an earlier open
    if window is None or window.get("seq") != self._seq:
      self._window = None
      if self._was_open:
        # a daemon restart writes seq 0 and never reports our window again
        if self._lost_since is None:
          self._lost_since = now
        if now - self._lost_since > LOST_SECONDS:
          self._finish(None)
      elif now - self._opened_at > START_TIMEOUT:
        self._cancel()
        self._finish(tr("bluetooth did not start"))
      return
    self._lost_since = None
    self._window = window
    prompt = window.get("prompt") or {}
    if prompt.get("step") == "allow" and self._check_shown_for != prompt.get("until"):
      self._check_shown_for = prompt.get("until")
      gui_app.push_widget(ConnectPhoneCheckDialog(prompt.get("check", ""), self._params))
    if window.get("state") == "closed":
      self._finish(_closed_message(window.get("reason", "")))
    elif window.get("state") == "open":
      self._was_open = True
      if not window.get("held") and now >= window["deadline"]:
        self._finish(_closed_message("timeout"))

  def _cancel(self) -> None:
    if not self._closing:
      self._closing = True
      write_request(self._params, "cancel")

  def _finish(self, message: str | None) -> None:
    self._closing = True
    gui_app.pop_widgets_to(self, instant=True)
    if message is None:
      self.dismiss(lambda: None)
    else:
      self.dismiss(lambda: gui_app.push_widget(BigDialog(message, "")))

  def _render(self, _):
    window = self._window
    held = window is not None and window.get("held", False)
    show_code = window is not None and window.get("state") == "open" and not held

    if show_code:
      if window["qr"] != self._qr_source:
        self._load_qr(window["qr"])
      self._draw_qr()

    label_x = self._rect.x + 8 + self._rect.height + 24 if show_code else self._rect.x + 20
    max_width = int(self._rect.x + self._rect.width - label_x)
    y = self._rect.y + 16
    self._title.set_text(tr("scan or type") if show_code else tr("connect phone"))
    self._title.set_max_width(max_width)
    self._title.set_position(label_x, y)
    self._title.render()
    y += self._title.get_content_height(max_width) + 16

    if show_code:
      remaining = max(0, int(window["deadline"] - time.monotonic()))
      self._code.set_text(format_code(int(window["code"])))
      self._code.set_max_width(max_width)
      self._code.set_position(label_x, y)
      self._code.render()
      y += self._code.get_content_height(max_width) + 12
      self._status.set_text(f"{tr('expires in')} {remaining // 60}:{remaining % 60:02d}")
    elif held:
      self._status.set_text(tr("connecting phone"))
    else:
      self._status.set_text("" if self._closing else tr("starting bluetooth"))
    self._status._shimmer = not show_code and not self._closing
    self._status.set_max_width(max_width)
    self._status.set_position(label_x, y)
    self._status.render()

  def _load_qr(self, text: str) -> None:
    self._unload_qr()
    self._qr_source = text
    try:
      self._qr_texture = make_texture(text, inverted=True)
    except Exception:
      cloudlog.exception("connect phone QR generation failed")
      self._qr_texture = None

  def _draw_qr(self) -> None:
    if self._qr_texture is None:
      return
    scale = self._rect.height / self._qr_texture.height
    rl.draw_texture_ex(self._qr_texture, rl.Vector2(round(self._rect.x + 8), round(self._rect.y)), 0.0, scale, rl.WHITE)

  def _unload_qr(self) -> None:
    if self._qr_texture and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
    self._qr_texture = None

  def __del__(self):
    self._unload_qr()


class ConnectPhoneCheckDialog(NavScroller):
  def __init__(self, check: str, params):
    super().__init__()
    self._params = params
    allow = BigConfirmationCircleButton(tr("allow\nthis phone"), gui_app.texture("icons_mici/setup/driver_monitoring/dm_check.png", 64, 64),
                                        lambda: self._answer("allow"))
    deny = BigConfirmationCircleButton(tr("deny"), gui_app.texture("icons_mici/setup/cancel.png", 64, 64), lambda: self._answer("deny"))
    self._scroller.add_widgets([GreyBigButton(check, tr("same code on your phone?"), gui_app.texture("icons_mici/setup/green_info.png", 64, 64)),
                                allow, deny])

  def _answer(self, action: str) -> None:
    self.dismiss(lambda: write_request(self._params, action))
