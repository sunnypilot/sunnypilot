"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64

import pyray as rl
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.sunnypilot.sunnylink.api import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID, API_HOST
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.lib.text_measure import measure_text_cached


class SunnylinkPairingDialog(PairingDialog):
  """Dialog for device pairing with QR code."""

  QR_REFRESH_INTERVAL = 300  # 5 minutes in seconds

  def __init__(self, sponsor_pairing: bool = False):
    PairingDialog.__init__(self)
    self._sponsor_pairing = sponsor_pairing
    self._is_paired_prev = ui_state.sunnylink_state.is_paired()

  def _get_pairing_url(self) -> str:
    qr_string = "https://github.com/sponsors/sunnyhaibin"

    if self._sponsor_pairing:
      try:
        sl_dongle_id = self.params.get("SunnylinkDongleId") or UNREGISTERED_SUNNYLINK_DONGLE_ID
        token = SunnylinkApi(sl_dongle_id).get_token()
        inner_string = f"1|{sl_dongle_id}|{token}"
        payload_bytes = base64.b64encode(inner_string.encode('utf-8')).decode('utf-8')
        qr_string = f"{API_HOST}/sso?state={payload_bytes}"
      except Exception:
        cloudlog.exception("Failed to get pairing token")

    return qr_string

  def _update_state(self):
    is_paired = ui_state.sunnylink_state.is_paired()
    if not self._is_paired_prev and is_paired:
      gui_app.set_modal_overlay(None)

  def _render(self, rect: rl.Rectangle) -> int:
    rl.clear_background(rl.Color(224, 224, 224, 255))

    self._check_qr_refresh()

    margin = 70
    content_rect = rl.Rectangle(rect.x + margin, rect.y + margin, rect.width - 2 * margin, rect.height - 2 * margin)
    y = content_rect.y

    # Close button
    close_size = 80
    pad = 20
    close_rect = rl.Rectangle(content_rect.x - pad, y - pad, close_size + pad * 2, close_size + pad * 2)
    self._close_btn.render(close_rect)

    y += close_size + 40

    # Title
    title = tr("Pair your GitHub account") if self._sponsor_pairing else tr("Early Access: Become a sunnypilot Sponsor")
    title_font = gui_app.font(FontWeight.NORMAL)
    left_width = int(content_rect.width * 0.5 - 15)

    title_wrapped = wrap_text(title_font, title, 75, left_width)
    rl.draw_text_ex(title_font, "\n".join(title_wrapped), rl.Vector2(content_rect.x, y), 75, 0.0, rl.BLACK)
    y += len(title_wrapped) * 75 + 60

    # Two columns: instructions and QR code
    remaining_height = content_rect.height - (y - content_rect.y)
    right_width = content_rect.width // 2 - 20

    # Instructions
    self._render_instructions(rl.Rectangle(content_rect.x, y, left_width, remaining_height))

    # QR code
    qr_size = min(right_width, content_rect.height) - 40
    qr_x = content_rect.x + left_width + 40 + (right_width - qr_size) // 2
    qr_y = content_rect.y
    self._render_qr_code(rl.Rectangle(qr_x, qr_y, qr_size, qr_size))

    return -1

  def _render_instructions(self, rect: rl.Rectangle) -> None:
    if self._sponsor_pairing:
      instructions = [
        tr("Scan the QR code to login to your GitHub account"),
        tr("Follow the prompts to complete the pairing process"),
        tr("Re-enter the \"sunnylink\" panel to verify sponsorship status"),
        tr("If sponsorship status was not updated, please contact a moderator on the community forum at https://community.sunnypilot.ai")
      ]
    else:
      instructions = [
        tr("Scan the QR code to visit sunnyhaibin's GitHub Sponsors page"),
        tr("Choose your sponsorship tier and confirm your support"),
        tr("Join our Community Forum at https://community.sunnypilot.ai and reach out to a moderator if you have issues")
      ]

    font = gui_app.font(FontWeight.BOLD)
    y = rect.y

    for i, text in enumerate(instructions):
      circle_radius = 25
      circle_x = rect.x + circle_radius + 15
      text_x = rect.x + circle_radius * 2 + 40
      text_width = rect.width - (circle_radius * 2 + 40)

      wrapped = wrap_text(font, text, 47, int(text_width))
      text_height = len(wrapped) * 47
      circle_y = y + text_height // 2

      # Circle and number
      rl.draw_circle(int(circle_x), int(circle_y), circle_radius, rl.Color(70, 70, 70, 255))
      number = str(i + 1)
      number_size = measure_text_cached(font, number, 30)
      rl.draw_text_ex(font, number, (int(circle_x - number_size.x // 2), int(circle_y - number_size.y // 2)), 30, 0, rl.WHITE)

      # Text
      rl.draw_text_ex(font, "\n".join(wrapped), rl.Vector2(text_x, y), 47, 0.0, rl.BLACK)
      y += text_height + 50


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
