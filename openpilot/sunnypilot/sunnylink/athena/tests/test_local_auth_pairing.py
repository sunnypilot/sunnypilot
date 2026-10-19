from typing import Any, cast
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.athena import local_auth_daemon
from openpilot.sunnypilot.sunnylink.athena.local_auth import decode_qr, encode64


class _FakeParams:
  """In-memory stand-in for the tiny Params surface the pairing window uses."""

  def __init__(self, fail_reads: bool = False):
    self.values: dict[str, Any] = {}
    self.removed: list[str] = []
    self.fail_reads = fail_reads

  def get_bool(self, key: str) -> bool:
    if self.fail_reads:
      raise RuntimeError("params unavailable")
    return bool(self.values.get(key))

  def put_bool(self, key: str, value: bool, block: bool = False) -> None:
    self.values[key] = bool(value)

  def get(self, key: str) -> Any:
    if self.fail_reads:
      raise RuntimeError("params unavailable")
    return self.values.get(key)

  def put(self, key: str, value: Any, block: bool = False) -> None:
    self.values[key] = value

  def remove(self, key: str) -> None:
    self.values.pop(key, None)
    self.removed.append(key)


class TestLocalAuthPairingWindow(OpenpilotTestCase):
  """The UI (another process) arms through Params; the daemon owns the authority window."""

  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.private_pem = self.device_key.private_bytes(
      serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    self.store = _FakeParams()
    self.params = cast(Params, self.store)

    local_auth_daemon.reset_authority()
    self.addCleanup(local_auth_daemon.reset_authority)
    patchers = [
      mock.patch.object(local_auth_daemon.BaseApi, "get_key_pair", return_value=("ES256", self.private_pem, "pub")),
      mock.patch.object(local_auth_daemon, "_read_registry", return_value=None),
    ]
    for patcher in patchers:
      patcher.start()
      self.addCleanup(patcher.stop)

  def request_window(self) -> None:
    """What the device UI does when the user taps the secure-pairing button."""
    self.store.put_bool(local_auth_daemon.PAIRING_REQUEST_KEY, True)

  def arm(self) -> str:
    self.request_window()
    qr = local_auth_daemon.service_pairing_window(self.params)
    assert qr is not None
    return qr

  def published(self) -> str | None:
    return local_auth_daemon.read_pairing_qr(self.params)

  def test_arming_publishes_the_qr_and_clears_the_request(self):
    qr = self.arm()
    # The QR is the compact pointer the app scans: which device, which window, for how long.
    payload = decode_qr(qr)
    authority = local_auth_daemon.get_authority()
    self.assertEqual(payload.cloud_device_id, authority.cloud_device_id)
    self.assertEqual(encode64(payload.session), authority.window.nonce)
    self.assertEqual(payload.ttl_s, 120)
    self.assertEqual(qr, self.published())
    # The request is consumed, so a UI restart cannot arm a second window by accident.
    self.assertNotIn(local_auth_daemon.PAIRING_REQUEST_KEY, self.store.values)
    self.assertEqual(qr, authority.window.qr)
    self.assertIsNone(authority.pending)

  def test_an_armed_window_is_not_rearmed_or_rotated(self):
    qr = self.arm()
    authority = local_auth_daemon.get_authority()
    window = authority.window
    # Ticks while the window is live must keep the SAME QR: the app may already have scanned it.
    for _ in range(3):
      self.assertEqual(qr, local_auth_daemon.service_pairing_window(self.params))
    self.assertIs(window, authority.window)
    self.assertEqual(qr, self.published())

  def test_a_live_window_outlives_a_missing_request_flag(self):
    qr = self.arm()
    # The arm request is already consumed on arming; its absence never closes a live window.
    self.assertNotIn(local_auth_daemon.PAIRING_REQUEST_KEY, self.store.values)
    self.assertEqual(qr, local_auth_daemon.service_pairing_window(self.params))
    self.assertIsNotNone(local_auth_daemon.get_authority().window)

  def test_clearing_the_published_qr_is_the_cancel_signal(self):
    self.arm()
    self.store.remove(local_auth_daemon.PAIRING_QR_KEY)
    # The UI cancel only reaches the params; the daemon's tick then cancels the real window.
    self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))
    self.assertIsNone(self.published())
    self.assertIsNone(local_auth_daemon.get_authority().window)

  def test_an_expired_window_is_hidden_but_its_session_survives_the_tick(self):
    self.arm()
    authority = local_auth_daemon.get_authority()
    window = authority.window
    with mock.patch.object(authority, "clock", lambda: window.deadline + 1):
      self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))
    self.assertIsNone(self.published())
    # The code is off the screen, so it can no longer be scanned — but an enrollment for it may
    # still be travelling through the cloud, so the session outlives the displayed window. Only
    # the window itself (and any grant it staged) is gone.
    self.assertIsNone(authority.window)
    self.assertEqual([w.nonce for w in authority.recent], [window.nonce])
    self.assertIsNone(authority.pending)
    # Past the delivery grace the session is forgotten too.
    with mock.patch.object(authority, "clock", lambda: window.usable_until + 1):
      self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))
    self.assertEqual(authority.recent, [])

  def test_a_new_request_after_a_closed_window_arms_a_fresh_qr(self):
    first = self.arm()
    self.store.remove(local_auth_daemon.PAIRING_QR_KEY)
    local_auth_daemon.service_pairing_window(self.params)
    second = self.arm()
    self.assertNotEqual(first, second)
    self.assertEqual(second, self.published())

  def test_missing_identity_fails_closed(self):
    self.request_window()
    with mock.patch.object(local_auth_daemon.BaseApi, "get_key_pair", return_value=(None, None, None)):
      local_auth_daemon.reset_authority()
      self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))
    # Nothing is published and the stale request is dropped, so the UI cannot show a window
    # that could never complete.
    self.assertIsNone(self.published())
    self.assertNotIn(local_auth_daemon.PAIRING_REQUEST_KEY, self.store.values)

  def test_clear_pairing_window_clears_both_params_and_the_window(self):
    self.arm()
    local_auth_daemon.clear_pairing_window(self.params)
    self.assertIsNone(self.published())
    self.assertNotIn(local_auth_daemon.PAIRING_REQUEST_KEY, self.store.values)
    self.assertIsNone(local_auth_daemon.get_authority().window)
    # A cleared window is idempotent: another tick publishes nothing.
    self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))

  def test_unreadable_params_never_raise(self):
    broken = _FakeParams(fail_reads=True)
    broken.values[local_auth_daemon.PAIRING_REQUEST_KEY] = True
    self.assertIsNone(local_auth_daemon.service_pairing_window(cast(Params, broken)))
    self.assertIsNone(local_auth_daemon.service_pairing_window(self.params))
