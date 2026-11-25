"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import hashlib
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from openpilot.common.test import Mocker, OpenpilotTestCase
from openpilot.sunnypilot.system import connect_phone as cp

DEVICE = "/org/bluez/hci0/dev_4A_3B_2C_1D_0E_0F"


class FakeParams:
  """Stores JSON text like the real JSON params, so values that cannot be stored fail here too."""

  def __init__(self):
    self.data: dict[str, str] = {}

  def get(self, key, block=False, return_default=False):
    return json.loads(self.data[key]) if key in self.data else None

  def put(self, key, value, block=False):
    self.data[key] = json.dumps(value)

  def remove(self, key):
    self.data.pop(key, None)


def use_key(mocker: Mocker) -> ec.EllipticCurvePrivateKey:
  key = ec.generate_private_key(ec.SECP256R1())
  pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()).decode()
  mocker.patch.object(cp.BaseApi, "get_key_pair", return_value=("ES256", pem, "unused"))
  return key


def spki_hash(key: ec.EllipticCurvePrivateKey) -> bytes:
  return hashlib.sha256(key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)).digest()


class TestCode(OpenpilotTestCase):
  def test_refused_codes_are_redrawn(self, mocker):
    randbelow = mocker.patch.object(cp.secrets, "randbelow", side_effect=[11111110, 88888887, 12345677, 87654320, 0])

    assert cp.generate_code() == 1
    assert randbelow.call_args_list == [mocker.call(99_999_998)] * 5

  def test_highest_code(self, mocker):
    mocker.patch.object(cp.secrets, "randbelow", return_value=99_999_997)

    assert cp.generate_code() == 99_999_998

  def test_format(self):
    assert cp.format_code(12345679) == "1234 5679"
    assert cp.format_code(1) == "0000 0001"


class TestQr(OpenpilotTestCase):
  def test_device_key_hash_is_sha256_of_spki(self, mocker):
    key = use_key(mocker)

    assert cp.device_key_hash() == spki_hash(key)

  def test_missing_device_key_raises(self, mocker):
    mocker.patch.object(cp.BaseApi, "get_key_pair", return_value=(None, None, None))

    with self.assertRaises(RuntimeError):
      cp.device_key_hash()

  def test_payload(self, mocker):
    key = use_key(mocker)
    text = cp.qr_text(1234, b"\xaa" * 8)

    assert text.startswith("SLC1:") and len(text) == 64
    payload = base64.urlsafe_b64decode(text[5:] + "=")
    assert payload == (1234).to_bytes(4, "big") + spki_hash(key) + b"\xaa" * 8


class TestWindow(OpenpilotTestCase):
  def test_open_starts_then_reports_ready(self, mocker):
    use_key(mocker)
    mocker.patch.object(cp, "generate_code", return_value=42)
    window = cp.ConnectPhoneWindow()

    assert window.state() == {"seq": 0, "state": "closed", "reason": ""}
    assert window.open(1000.0, seq=7) == "ok"
    assert window.active
    state = window.state()
    assert state == {"seq": 7, "state": "starting", "code": "00000042", "qr": state["qr"],
                   "deadline": 1000.0 + cp.WINDOW_SECONDS, "held": False, "reason": ""}
    assert state["qr"].startswith("SLC1:")

    window.tick(1001.0, ready=False)
    assert window.state()["state"] == "starting"
    window.tick(1002.0)
    assert window.state()["state"] == "open"

  def test_same_request_again_changes_nothing(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()
    window.open(1000.0, seq=1)
    first = window.state()

    assert window.open(1050.0, seq=1) == "busy"
    assert window.state() == first

  def test_new_request_replaces_the_open_window(self, mocker):
    use_key(mocker)
    mocker.patch.object(cp, "generate_code", side_effect=[11, 22])
    window = cp.ConnectPhoneWindow()
    window.open(1000.0, seq=1)
    window.tick(1001.0)
    first = window.state()

    assert window.open(1050.0, seq=2) == "ok"
    second = window.state()
    assert second == {"seq": 2, "state": "starting", "code": "00000022", "qr": second["qr"],
                      "deadline": 1050.0 + cp.WINDOW_SECONDS, "held": False, "reason": ""}
    assert second["qr"] != first["qr"]

  def test_closes_itself_after_the_window(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()
    window.open(1000.0)
    window.tick(1004.0)

    window.tick(1004.0 + cp.WINDOW_SECONDS - 0.1)
    assert window.active
    window.tick(1004.0 + cp.WINDOW_SECONDS)
    assert not window.active
    assert window.state() == {"seq": 0, "state": "closed", "reason": "timeout"}

  def test_full_time_counts_from_ready(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()
    window.open(1000.0)
    window.tick(1003.0, ready=False)
    window.tick(1005.0)
    assert window.state()["deadline"] == 1005.0 + cp.WINDOW_SECONDS
    window.tick(1006.0, ready=False)
    window.tick(1007.0)
    assert window.state()["deadline"] == 1005.0 + cp.WINDOW_SECONDS

  def test_held_window_does_not_time_out(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()
    window.open(1000.0)
    window.tick(1000.0)
    window.hold()
    window.tick(1000.0 + cp.WINDOW_SECONDS + 60)
    assert window.active
    window.cancel("granted")
    assert window.state()["reason"] == "granted"

  def test_cancel(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()
    window.cancel()
    assert window.state()["reason"] == ""

    window.open(1000.0)
    window.cancel()
    assert window.state() == {"seq": 0, "state": "closed", "reason": "cancel"}

    window.open(1000.0)
    window.cancel("bluetooth_off")
    assert window.state() == {"seq": 0, "state": "closed", "reason": "bluetooth_off"}

  def test_reopen_draws_a_new_code_and_nonce(self, mocker):
    use_key(mocker)
    mocker.patch.object(cp, "generate_code", side_effect=[11, 22])
    window = cp.ConnectPhoneWindow()
    window.open(1000.0)
    first = window.state()
    window.cancel()

    assert window.open(1010.0) == "ok"
    second = window.state()
    assert (first["code"], second["code"]) == ("00000011", "00000022")
    assert first["qr"] != second["qr"]
    assert second["deadline"] == 1010.0 + cp.WINDOW_SECONDS

  def test_missing_device_key_leaves_the_window_closed(self, mocker):
    mocker.patch.object(cp.BaseApi, "get_key_pair", return_value=(None, None, None))
    window = cp.ConnectPhoneWindow()

    with self.assertRaises(RuntimeError):
      window.open(1000.0)
    assert not window.active

  def test_secret_only_while_open(self, mocker):
    use_key(mocker)
    window = cp.ConnectPhoneWindow()

    assert cp.PAKE_SUITE == 1
    assert window.secret() is None
    window.open(1000.0)
    digits, nonce = window.secret()
    assert len(digits) == 8 and digits.isdigit() and len(nonce) == 8
    window.cancel()
    assert window.secret() is None


class TestParams(OpenpilotTestCase):
  def test_request(self):
    params = FakeParams()

    first = cp.write_request(params, "open")
    assert params.get(cp.REQUEST_KEY) == {"seq": first, "action": "open"}
    second = cp.write_request(params, "cancel")
    assert second > first
    assert params.get(cp.REQUEST_KEY) == {"seq": second, "action": "cancel"}

  def test_unknown_action_is_refused(self):
    params = FakeParams()

    with self.assertRaises(ValueError):
      cp.write_request(params, "bogus")
    assert params.data == {}

  def test_window_round_trip(self, mocker):
    use_key(mocker)
    params = FakeParams()
    assert cp.read_window(params) is None

    window = cp.ConnectPhoneWindow()
    window.open(1000.0, seq=5)
    params.put(cp.WINDOW_KEY, window.state())
    assert cp.read_window(params) == window.state()

  def test_remove_request_carries_the_phone(self):
    params = FakeParams()

    seq = cp.write_request(params, "remove", phone="abc")
    assert params.get(cp.REQUEST_KEY) == {"seq": seq, "action": "remove", "phone": "abc"}

  def test_status_and_indicator(self):
    params = FakeParams()
    assert cp.read_status(params) == {}
    assert cp.phone_indicator({}) == "hidden"

    params.put(cp.STATUS_KEY, {"enabled": True, "connected": 0, "phones": 1})
    assert cp.phone_indicator(cp.read_status(params)) == "waiting"
    params.put(cp.STATUS_KEY, {"enabled": True, "connected": 2, "phones": 1})
    assert cp.phone_indicator(cp.read_status(params)) == "connected"
    params.put(cp.STATUS_KEY, {"enabled": False, "connected": 0, "phones": 0})
    assert cp.phone_indicator(cp.read_status(params)) == "hidden"

  def test_no_grants_yet(self, mocker):
    mocker.patch.object(cp, "Params", return_value=FakeParams())
    assert cp.grant_count() == 0
