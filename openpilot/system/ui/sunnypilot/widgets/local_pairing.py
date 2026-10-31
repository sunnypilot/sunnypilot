"""Plumbing shared by the two local pairing dialogs.

The window belongs to the local daemon in another process, so a dialog only files a request and
renders the QR that gets published. The published QR is the window's state: removing it (Cancel,
or the daemon's own expiry) closes the window.
"""
from __future__ import annotations

import time

import pyray as rl

from openpilot.common.params import Params
from openpilot.common.qrcode import make_texture
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.sunnylink.athena.local_auth_daemon import clear_pairing_params, read_pairing_qr
from openpilot.sunnypilot.sunnylink.athena.local_state import PAIRING_REQUEST_KEY


class LocalPairingWindow:
  # The daemon services the request about once a second; taking longer means it is not running.
  ARM_GRACE_S = 5.0

  def __init__(self):
    self._requested_at = time.monotonic()
    self._seen_qr = False
    self._qr: str | None = None
    self._texture: rl.Texture | None = None
    try:
      Params().put_bool(PAIRING_REQUEST_KEY, True, block=True)
    except Exception:
      cloudlog.exception("sunnylink.local_pairing.request_failed")

  def texture(self) -> rl.Texture | None:
    """The published code as a texture, rebuilt only when the code changes."""
    qr = read_pairing_qr()
    if qr != self._qr:
      self.release()
      self._qr = qr
      if qr:
        try:
          self._texture = make_texture(qr)
          # Drawn smaller than it is built, so the modules have to stay hard-edged for a camera.
          rl.set_texture_filter(self._texture, rl.TextureFilter.TEXTURE_FILTER_POINT)
        except Exception:
          cloudlog.exception("sunnylink.local_pairing.qr_texture_failed")
    return self._texture

  def ended(self) -> bool:
    """True once the daemon's window is gone: enrolled, expired or cancelled."""
    if read_pairing_qr() is not None:
      self._seen_qr = True
      return False
    return self._seen_qr or time.monotonic() - self._requested_at > self.ARM_GRACE_S

  def cancel(self) -> None:
    clear_pairing_params()

  def release(self) -> None:
    if self._texture is not None and self._texture.id != 0:
      rl.unload_texture(self._texture)
    self._texture = None
