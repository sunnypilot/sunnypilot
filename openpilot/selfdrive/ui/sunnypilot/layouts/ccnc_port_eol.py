"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import subprocess
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
SWITCH_BRANCH = "staging"

# Merged into master and built into staging. Keyed on ccnc-port platform names, which never change; the FW is the
# camera and radar FW master also lists, so a car whose FW master lacks is not sent to a branch that won't recognize it.
CCNC_PORT_SUPPORTED: dict[str, tuple[str, set[bytes]]] = {
  "HYUNDAI_SONATA_HEV_2024": ("Hyundai Sonata Hybrid 2024-26", {
    b'\xf1\x00DN8HMFC  AT KOR LHD 1.00 1.01 99211-L1800 230512',
    b'\xf1\x00DN8HMFC  AT USA LHD 1.00 1.01 99211-L1800 230512',
    b'\xf1\x00DN8HMFC  AT USA LHD 1.00 1.02 99211-L1800 250613',
    b'\xf1\x00DN8_ RDR -----      1.00 1.00 99110-L1800         ',
  }),
  "HYUNDAI_TUCSON_HEV_2025": ("Hyundai Tucson Hybrid 2025-26", {
    b'\xf1\x00NX4 FR_CMR AT EUR LHD 1.00 1.00 99211-N7030 C55',
    b'\xf1\x00NX4 FR_CMR AT USA LHD 1.00 1.00 99211-N7030 C55',
    b'\xf1\x00NX4 FR_CMR AT USA LHD 1.00 1.00 99211-N7035 C5C',
    b'\xf1\x00NX4 FR_CMR AT USA LHD 1.00 1.00 99211-N7060 C5B',
    b'\xf1\x00NX4__               1.00 1.02 99110N7000          ',
    b'\xf1\x00NX4__               1.00 1.02 99110N7100          ',
    b'\xf1\x00NX4__               1.00 1.03 99110N7100          ',
  }),
}


def supported_car_name() -> str | None:
  CP = ui_state.CP
  if CP is None or CP.carFingerprint not in CCNC_PORT_SUPPORTED:
    return None
  name, fw_versions = CCNC_PORT_SUPPORTED[CP.carFingerprint]
  seen = {(str(fw.ecu), fw.fwVersion) for fw in CP.carFw if str(fw.ecu) in ("fwdCamera", "fwdRadar") and not fw.logging}
  if {ecu for ecu, _ in seen} != {"fwdCamera", "fwdRadar"} or any(v not in fw_versions for _, v in seen):
    return None
  return name


class CcncPortEolGate:
  # The ack param clears on boot and on every offroad transition, so the notice is shown again after each drive.
  def __init__(self, main: Widget, notice_cls: Callable[[Callable[[], None], Callable[[], None], str | None], Widget]):
    self._main = main
    self._notice_cls = notice_cls
    self._notice: Widget | None = None
    self._acked = False
    gui_app.add_nav_stack_tick(self._tick)

  def _tick(self):
    if ui_state.started:
      self._acked = False
    elif not self._acked and gui_app.get_active_widget() is self._main:
      # built per drive: CarParamsPersistent first appears after the device's first drive
      self._notice = self._notice_cls(self._on_ack, self._on_switch, supported_car_name())
      gui_app.push_widget(self._notice)

  def _on_ack(self):
    self._acked = True
    ui_state.params.put_bool("CcncPortEolAck", True, block=True)
    gui_app.pop_widgets_to(self._main, instant=True)

  def _on_switch(self):
    ui_state.params.put("UpdaterTargetBranch", SWITCH_BRANCH, block=True)
    subprocess.run(["pkill", "-SIGUSR1", "-f", "openpilot.system.updated.updated"], check=False)
    self._on_ack()


class CcncPortEolNotice(Widget):
  def __init__(self, on_ack: Callable[[], None], on_switch: Callable[[], None], car_name: str | None):
    super().__init__()
    self._car_name = car_name
    if car_name:
      title = tr("Your car is now officially supported")
      desc = tr("ccnc-port will not receive any more functional updates. Your car is supported on sunnypilot master.\n\n" +
                "Switch to staging to keep getting updates. Scan the QR code for details.")
    else:
      title = tr("This branch is no longer updated")
      desc = tr("ccnc-port will not receive any more functional updates. ccNC support is moving to master.\n\n" +
                "Scan the QR code to see what you need to do.")
    self._title = Label(title, font_size=75, font_weight=FontWeight.BOLD,
                        text_alignment=TextAlignment.LEFT, text_alignment_vertical=TextAlignmentVertical.TOP)
    self._car = Label(car_name or "", font_size=55, font_weight=FontWeight.MEDIUM, text_color=rl.Color(150, 150, 150, 255),
                      text_alignment=TextAlignment.LEFT, text_alignment_vertical=TextAlignmentVertical.TOP)
    self._desc = Label(desc, font_size=55, font_weight=FontWeight.MEDIUM,
                       text_alignment=TextAlignment.LEFT, text_alignment_vertical=TextAlignmentVertical.TOP)
    self._ack_btn = Button(tr("Not now") if car_name else tr("I understand"),
                           button_style=ButtonStyle.NORMAL if car_name else ButtonStyle.PRIMARY, click_callback=on_ack)
    self._switch_btn = Button(tr("Switch to staging"), button_style=ButtonStyle.PRIMARY, click_callback=on_switch)
    self._qr_texture = make_texture(CCNC_PORT_EOL_URL)

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, rl.BLACK)

    qr_size = 560
    qr_x = rect.x + rect.width - qr_size - 90
    text_x = rect.x + 90
    text_w = qr_x - text_x - 60
    if self._car_name:
      self._title.render(rl.Rectangle(text_x, rect.y + 90, text_w, 100))
      self._car.render(rl.Rectangle(text_x, rect.y + 190, text_w, 80))
      self._desc.render(rl.Rectangle(text_x, rect.y + 330, text_w, 450))
    else:
      self._title.render(rl.Rectangle(text_x, rect.y + 90, text_w, 200))
      self._desc.render(rl.Rectangle(text_x, rect.y + 300, text_w, 450))

    if self._qr_texture:
      src = rl.Rectangle(0, 0, self._qr_texture.width, self._qr_texture.height)
      rl.draw_texture_pro(self._qr_texture, src, rl.Rectangle(qr_x, rect.y + 90, qr_size, qr_size), rl.Vector2(0, 0), 0, rl.WHITE)

    btn_y = rect.y + rect.height - 160 - 45
    if self._car_name:
      btn_w = (rect.width - 90 - 30) / 2
      self._ack_btn.render(rl.Rectangle(rect.x + 45, btn_y, btn_w, 160))
      self._switch_btn.render(rl.Rectangle(rect.x + 45 + btn_w + 30, btn_y, btn_w, 160))
    else:
      self._ack_btn.render(rl.Rectangle(rect.x + 45, btn_y, rect.width - 90, 160))

  def __del__(self):
    if self._qr_texture and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)
