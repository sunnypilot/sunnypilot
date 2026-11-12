"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.common.qrcode import make_texture
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, TextAlignment, TextAlignmentVertical, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label

CCNC_PORT_EOL_URL = "https://community.sunnypilot.ai/t/ccnc-port-non-hda2-hda2-supported-vehicles-features/1064/337?u=sunnyhaibin"


class CcncPortEolGate:
  # The ack param clears on boot and on every offroad transition, so the notice is shown again after each drive.
  def __init__(self, main: Widget, notice_cls: Callable[[Callable[[], None]], Widget]):
    self._main = main
    self._notice = notice_cls(self._on_ack)
    self._acked = False
    gui_app.add_nav_stack_tick(self._tick)

  def _tick(self):
    if ui_state.started:
      self._acked = False
    elif not self._acked and gui_app.get_active_widget() is self._main:
      gui_app.push_widget(self._notice)

  def _on_ack(self):
    self._acked = True
    ui_state.params.put_bool("CcncPortEolAck", True, block=True)
    gui_app.pop_widgets_to(self._main, instant=True)


class CcncPortEolNotice(Widget):
  def __init__(self, on_ack: Callable[[], None]):
    super().__init__()
    self._title = Label(tr("This branch is no longer updated"), font_size=75, font_weight=FontWeight.BOLD,
                        text_alignment=TextAlignment.LEFT, text_alignment_vertical=TextAlignmentVertical.TOP)
    self._desc = Label(tr("ccnc-port will not receive any more functional updates. ccNC support is moving to master.\n\n" +
                          "Scan the QR code to see what you need to do."),
                       font_size=55, font_weight=FontWeight.MEDIUM,
                       text_alignment=TextAlignment.LEFT, text_alignment_vertical=TextAlignmentVertical.TOP)
    self._ack_btn = Button(tr("I understand"), button_style=ButtonStyle.PRIMARY, click_callback=on_ack)
    self._qr_texture = make_texture(CCNC_PORT_EOL_URL)

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, rl.BLACK)

    qr_size = 560
    qr_x = rect.x + rect.width - qr_size - 90
    text_x = rect.x + 90
    text_w = qr_x - text_x - 60
    self._title.render(rl.Rectangle(text_x, rect.y + 90, text_w, 200))
    self._desc.render(rl.Rectangle(text_x, rect.y + 300, text_w, 450))

    if self._qr_texture:
      src = rl.Rectangle(0, 0, self._qr_texture.width, self._qr_texture.height)
      rl.draw_texture_pro(self._qr_texture, src, rl.Rectangle(qr_x, rect.y + 90, qr_size, qr_size), rl.Vector2(0, 0), 0, rl.WHITE)

    self._ack_btn.render(rl.Rectangle(rect.x + 45, rect.y + rect.height - 160 - 45, rect.width - 90, 160))

  def __del__(self):
    if self._qr_texture and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
