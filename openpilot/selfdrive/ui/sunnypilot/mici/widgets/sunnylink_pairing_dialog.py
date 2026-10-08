"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64

import pyray as rl
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.mici.widgets.qr import QR
from openpilot.sunnypilot.sunnylink.api import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID, API_HOST
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.label import UnifiedLabel


class SunnylinkPairingDialog(NavWidget):
  """Dialog for sunnylink pairing with QR code."""

  def __init__(self, sponsor_pairing: bool = False):
    super().__init__()
    self._params = Params()
    self._sponsor_pairing = sponsor_pairing

    self._qr = self._child(QR(self._get_pairing_url()))
    self._txt_pair = gui_app.texture("icons_mici/settings/device/pair.png", 33, 60)

    label_text = tr("pair with sunnylink") if sponsor_pairing else tr("become a sunnypilot sponsor")
    self._pair_label = self._child(UnifiedLabel(label_text, font_size=48, font_weight=FontWeight.BOLD,
                                                text_color=rl.Color(255, 255, 255, int(255 * 0.9)), line_height=0.8))

  def _get_pairing_url(self) -> str:
    qr_string = "https://github.com/sponsors/sunnyhaibin"

    if self._sponsor_pairing:
      try:
        sl_dongle_id = self._params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID
        token = SunnylinkApi(sl_dongle_id).get_token()
        inner_string = f"1|{sl_dongle_id}|{token}"
        payload_bytes = base64.b64encode(inner_string.encode('utf-8')).decode('utf-8')
        qr_string = f"{API_HOST}/sso?state={payload_bytes}"
      except Exception:
        cloudlog.exception("Failed to get pairing token")

    return qr_string

  def _update_state(self):
    # Sunnylink pairing is not comma prime, so this never auto-dismisses on prime pairing.
    NavWidget._update_state(self)

  def _render(self, _):
    qr_rect = rl.Rectangle(self._rect.x + 8, self._rect.y, self._rect.height, self._rect.height)
    self._qr.render(qr_rect)

    label_x = self._rect.x + 8 + self._rect.height + 24
    self._pair_label.set_max_width(int(self._rect.width - label_x))
    self._pair_label.set_position(label_x, self._rect.y + 16)
    self._pair_label.render()

    rl.draw_texture_ex(self._txt_pair, rl.Vector2(label_x, self._rect.y + self._rect.height - self._txt_pair.height - 16),
                       0.0, 1.0, rl.Color(255, 255, 255, int(255 * 0.35)))


if __name__ == "__main__":
  gui_app.init_window("pairing device")
  pairing = SunnylinkPairingDialog(sponsor_pairing=True)
  try:
    for _ in gui_app.render():
      result = pairing.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
      if result != -1:
        break
  finally:
    del pairing
