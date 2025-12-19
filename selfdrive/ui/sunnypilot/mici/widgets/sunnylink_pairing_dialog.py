"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64

import pyray as rl
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.mici.widgets.pairing_dialog import PairingDialog
from openpilot.sunnypilot.sunnylink.api import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID, API_HOST
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import NavWidget
from openpilot.system.ui.widgets.label import MiciLabel


class SunnylinkPairingDialog(PairingDialog):
  """Dialog for device pairing with QR code."""

  def __init__(self, sponsor_pairing: bool = False):
    PairingDialog.__init__(self)
    self._sponsor_pairing = sponsor_pairing
    label_text = tr("pair with sunnylink") if sponsor_pairing else tr("become a sunnypilot sponsor")
    self._pair_label = MiciLabel(label_text, 48, font_weight=FontWeight.BOLD,
                                 color=rl.Color(255, 255, 255, int(255 * 0.9)), line_height=40, wrap_text=True)

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
    NavWidget._update_state(self)


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
