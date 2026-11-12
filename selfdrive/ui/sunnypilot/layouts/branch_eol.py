"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import numpy as np
import pyray as rl
import qrcode
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label

BRANCH_EOL_URL = "https://community.sunnypilot.ai/t/support-for-newer-vehicles-equipped-with-angle-steering-lfa2/22/751?u=sunnyhaibin"
BRANCH_EOL_TEXT = "hkg-angle-steering-2025-hda1 will not receive any more functional updates. Switch to hkg-angle-steering-2025."


class BranchEolGate:
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
    ui_state.params.put_bool("BranchEolAck", True)
    gui_app.pop_widgets_to(self._main, instant=True)


class BranchEolNotice(Widget):
  def __init__(self, on_ack: Callable[[], None]):
    super().__init__()
    self._title = Label(tr("This branch is no longer updated"), font_size=75, font_weight=FontWeight.BOLD,
                        text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                        text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)
    self._desc = Label(tr(BRANCH_EOL_TEXT + "\n\nScan the QR code to see what you need to do."),
                       font_size=55, font_weight=FontWeight.MEDIUM,
                       text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                       text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)
    self._ack_btn = Button(tr("I understand"), button_style=ButtonStyle.PRIMARY, click_callback=on_ack)

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(BRANCH_EOL_URL)
    qr.make(fit=True)
    pil_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    img_array = np.array(pil_img, dtype=np.uint8)
    rl_image = rl.Image()
    rl_image.data = rl.ffi.cast("void *", img_array.ctypes.data)
    rl_image.width = pil_img.width
    rl_image.height = pil_img.height
    rl_image.mipmaps = 1
    rl_image.format = rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
    self._qr_texture = rl.load_texture_from_image(rl_image)

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, rl.BLACK)

    qr_size = 560
    qr_x = rect.x + rect.width - qr_size - 90
    text_x = rect.x + 90
    text_w = qr_x - text_x - 60
    self._title.render(rl.Rectangle(text_x, rect.y + 90, text_w, 200))
    self._desc.render(rl.Rectangle(text_x, rect.y + 300, text_w, 450))

    src = rl.Rectangle(0, 0, self._qr_texture.width, self._qr_texture.height)
    rl.draw_texture_pro(self._qr_texture, src, rl.Rectangle(qr_x, rect.y + 90, qr_size, qr_size), rl.Vector2(0, 0), 0, rl.WHITE)

    self._ack_btn.render(rl.Rectangle(rect.x + 45, rect.y + rect.height - 160 - 45, rect.width - 90, 160))

  def __del__(self):
    if self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
