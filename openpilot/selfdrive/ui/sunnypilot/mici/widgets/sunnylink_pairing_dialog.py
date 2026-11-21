"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import time

import pyray as rl
from openpilot.common.params import Params
from openpilot.common.qrcode import make_texture
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.sunnylink.api import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID, API_HOST
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.label import UnifiedLabel


class SunnylinkPairingDialog(NavWidget):
  """Dialog for device pairing with QR code."""

  QR_REFRESH_INTERVAL = 300  # 5 minutes in seconds

  def __init__(self, sponsor_pairing: bool = False):
    super().__init__()
    self._params = Params()
    self._qr_texture: rl.Texture | None = None
    self._last_qr_generation = float("-inf")
    self._txt_pair = gui_app.texture("icons_mici/settings/device/pair.png", 33, 60)
    self._sponsor_pairing = sponsor_pairing
    label_text = tr("pair with sunnylink") if sponsor_pairing else tr("become a sunnypilot sponsor")
    self._pair_label = UnifiedLabel(label_text, font_size=48, font_weight=FontWeight.BOLD,
                                    text_color=rl.Color(255, 255, 255, int(255 * 0.9)), line_height=0.8)

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

  def _generate_qr_code(self) -> None:
    try:
      if self._qr_texture and self._qr_texture.id != 0:
        rl.unload_texture(self._qr_texture)
      self._qr_texture = make_texture(self._get_pairing_url(), inverted=True)
    except Exception as e:
      cloudlog.warning(f"QR code generation failed: {e}")
      self._qr_texture = None

  def _check_qr_refresh(self) -> None:
    current_time = time.monotonic()
    if current_time - self._last_qr_generation >= self.QR_REFRESH_INTERVAL:
      self._generate_qr_code()
      self._last_qr_generation = current_time

  def _render(self, rect: rl.Rectangle):
    self._check_qr_refresh()

    self._render_qr_code()

    label_x = self._rect.x + 8 + self._rect.height + 24
    self._pair_label.set_max_width(int(self._rect.width - label_x))
    self._pair_label.set_position(label_x, self._rect.y + 16)
    self._pair_label.render()

    rl.draw_texture_ex(self._txt_pair, rl.Vector2(label_x, self._rect.y + self._rect.height - self._txt_pair.height - 16),
                       0.0, 1.0, rl.Color(255, 255, 255, int(255 * 0.35)))

  def _render_qr_code(self) -> None:
    if not self._qr_texture:
      error_font = gui_app.font(FontWeight.BOLD)
      rl.draw_text_ex(
        error_font, "QR Code Error", rl.Vector2(self._rect.x + 20, self._rect.y + self._rect.height // 2 - 15), 30, 0.0, rl.RED
      )
      return

    scale = self._rect.height / self._qr_texture.height
    pos = rl.Vector2(round(self._rect.x + 8), round(self._rect.y))
    rl.draw_texture_ex(self._qr_texture, pos, 0.0, scale, rl.WHITE)

  def __del__(self):
    if self._qr_texture and self._qr_texture.id != 0:
      rl.unload_texture(self._qr_texture)


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
