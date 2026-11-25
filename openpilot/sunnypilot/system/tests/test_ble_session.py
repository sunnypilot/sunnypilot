"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from openpilot.common.test import Mocker, OpenpilotTestCase
from openpilot.sunnypilot.system import connect_phone as cp
from openpilot.sunnypilot.system.ble import cpace, grants, link, noise, session as s

DEVICE = "/org/bluez/hci0/dev_A"
WALL = 1_700_000_000


class MemParams:
  def __init__(self, values: dict | None = None, known: set[str] | None = None):
    self.data = dict(values or {})
    self.known = known if known is not None else set(self.data)

  def get(self, key, block=False, return_default=False):
    return self.data.get(key)

  def get_bool(self, key):
    return bool(self.data.get(key))

  def put(self, key, value, block=False):
    self.data[key] = value

  def put_bool(self, key, value, block=False):
    self.data[key] = value

  def remove(self, key):
    self.data.pop(key, None)

  def all_keys(self):
    return [k.encode() for k in self.known]


def spki_of(key) -> bytes:
  return key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


class Phone:
  """An initiator built from the protocol core: CPace party A, Noise KK initiator, one link id."""

  def __init__(self, h: "Harness", device: str, lid: int, name: str = "test phone"):
    self.h, self.device, self.lid, self.name = h, device, lid, name
    self.mtu = 23
    self.connected = True
    self.inbox: list[bytes] = []
    self.reasm = link.Reassembler(lid)
    self.broken = False
    self.static = X25519PrivateKey.generate()
    self.key = ec.generate_private_key(ec.SECP256R1())
    self.records: link.Records | None = None
    self.th = b""
    self.cp = None
    self.ya = self.yb = self.isk = b""
    self.sid = b""

  def receive(self, frame: bytes):
    if int.from_bytes(frame[1:3], "big") != self.lid:
      return
    try:
      msg = self.reasm.feed(frame)
    except link.LinkError:
      self.broken = True
      return
    if msg is not None:
      self.inbox.append(msg)

  def pop(self, typ: int) -> bytes:
    msg = self.inbox.pop(0)
    assert msg[0] == typ, (msg[0], typ)
    return msg[1:]

  def pop_record(self, typ: int) -> bytes:
    inner = self.records.open(self.inbox.pop(0))
    assert inner[0] == typ, (inner[0], typ)
    return inner[1:]

  def pop_error(self) -> int:
    return self.pop(s.ERROR)[0]

  def start(self, now: float):
    return self.h.send(self, bytes([s.CONNECT_START, s.PROTO]), now)

  def pake(self, prs: bytes, now: float):
    self.wbody = self.pop(s.CONNECT_WINDOW)
    self.sid = self.wbody[2:26]
    self.cp = cpace.Cpace(True, prs, self.sid, bytes([s.PROTO]), self.wbody)
    self.ya = self.cp.public
    self.h.send(self, bytes([s.PAKE_A]) + self.ya, now)
    if self.broken or not self.inbox:
      return
    self.yb = self.pop(s.PAKE_B)
    self.isk = self.cp.isk(self.yb)
    self.ta = self.cp.tag(self.isk)
    self.h.send(self, bytes([s.CONFIRM_A]) + self.ta, now)

  def confirm(self):
    tb = self.pop(s.CONFIRM_B)
    assert self.cp.check(self.isk, self.yb, tb)
    self.th = link.transcript(bytes([s.PROTO]), self.wbody, self.ya, self.yb, self.ta, tb)
    p2c, c2p, self.check = link.session_keys(self.isk, self.sid)
    self.records = link.Records(p2c, c2p, self.lid)
    self.reasm.cap = link.SESSION_CAP

  def ceremony(self, prs: bytes, now: float):
    self.start(now)
    self.pake(prs, now)
    if self.inbox and self.inbox[0][0] == s.CONFIRM_B:
      self.confirm()

  def phone_keys(self, now: float):
    dev = self.pop_record(s.DEVICE_KEYS)
    doc = json.loads(dev)
    spki, static, sig = (grants.unb64(doc[k]) for k in ("spki", "static", "sig"))
    assert spki == self.h.identity_spki
    assert link.verify(doc["alg"], spki, link.signed_bytes("D", self.th, spki, static), sig)
    own_spki = spki_of(self.key)
    own_static = self.static.public_key().public_bytes_raw()
    alg, own_sig = link.sign(self.key, link.signed_bytes("P", self.th, own_spki, own_static))
    doc = {"v": 1, "spki": grants.b64(own_spki), "alg": alg, "static": grants.b64(own_static),
           "id": {"name": self.name}, "sig": grants.b64(own_sig)}
    self.h.send_record(self, s.PHONE_KEYS, json.dumps(doc).encode(), now)

  def resume_start(self, comma_static: bytes, now: float):
    hs = noise.KKHandshake(True, self.static, comma_static)
    self.h.send(self, bytes([s.RESUME_1]) + hs.write(bytes([s.PROTO])), now)
    if self.broken or not self.inbox or self.inbox[0][0] == s.ERROR:
      return
    body = self.pop(s.RESUME_2)
    assert hs.read(body) == bytes([1])
    send, recv = hs.split()
    self.records = link.Records(send, recv, self.lid)
    self.reasm.cap = link.SESSION_CAP

  def rpc(self, method: str, now: float, params=None, rid: int = 1) -> dict:
    body = json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}).encode()
    self.h.send_record(self, s.RPC, body, now)
    return json.loads(self.pop_record(s.RPC))


class Harness:
  def __init__(self, mocker: Mocker, values=None, known=None):
    self.identity = ec.generate_private_key(ec.SECP256R1())
    self.identity_spki = spki_of(self.identity)
    pem = self.identity.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                                      serialization.NoEncryption()).decode()
    mocker.patch.object(cp.BaseApi, "get_key_pair", return_value=("ES256", pem, "unused"))
    self.clock = {"wall": WALL}
    self.params = MemParams({"DongleId": "dongle", "HardwareSerial": "serial"} | (values or {}), known=known)
    self.window = cp.ConnectPhoneWindow()
    self.engine = s.Engine(self.params, self.window, wifi=lambda: self.wifi, wall=lambda: self.clock["wall"])
    self.wifi = FakeWifi()
    self.phones: dict[str, Phone] = {}

  def new_phone(self, lid: int = 0x1234, device: str = DEVICE, name: str = "test phone") -> Phone:
    phone = self.phones[device] = Phone(self, device, lid, name)
    return phone

  def open_window(self, now: float = 0.0):
    assert self.window.open(now, 1) == "ok"

  def send(self, phone: Phone, message: bytes, now: float):
    for frame in link.frames(message, phone.lid, phone.mtu - 3):
      if not phone.connected:
        return
      self.route(self.engine.on_write(phone.device, frame, phone.mtu, now))

  def send_record(self, phone: Phone, typ: int, body: bytes, now: float):
    self.send(phone, phone.records.seal(bytes([typ]) + body), now)

  def route(self, actions):
    for kind, data in actions:
      if kind == "notify":
        for phone in self.phones.values():
          if phone.connected:
            phone.receive(data)
      else:
        self.engine.on_disconnect(data)
        self.phones[data].connected = False

  def tick(self, now: float):
    self.route(self.engine.tick(now))

  def allow(self, now: float, allow: bool = True):
    self.route(self.engine.answer(allow, now))

  def grant_list(self) -> list[dict]:
    return grants.load(self.params)


class FakeWifi:
  def __init__(self):
    self.active = False  # what the radio reports
    self.requested: bool | None = None  # last set_tethering_active call
    self.connected_ssid = "home"
    self.tethering_ssid = "weedle-test"
    self.tethering_password = "pw-test"

  def is_tethering_active(self):
    return self.active

  def set_tethering_active(self, active: bool):
    self.requested = active


def full_ceremony(h: Harness, phone: Phone, now: float = 0.0) -> int:
  prs, _ = h.window.secret()
  phone.ceremony(prs, now)
  h.allow(now)
  phone.pop_record(s.DECISION)
  phone.phone_keys(now)
  return phone.pop_record(s.GRANT_RESULT)[0]


class TestCeremony(OpenpilotTestCase):
  def test_full_ceremony(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    prs = h.window.secret()[0]
    phone.ceremony(prs, 0.0)
    assert h.window.active and h.engine.prompt(0.0) == {"step": "allow", "check": phone.check[:3] + " " + phone.check[3:],
                                                        "until": 30.0}
    h.allow(0.0)
    assert phone.pop_record(s.DECISION) == bytes([s.ALLOW])
    phone.phone_keys(0.0)
    assert phone.pop_record(s.GRANT_RESULT) == bytes([s.GRANT_ADDED])

    grant = h.grant_list()
    assert [(g["name"], g["added"], g["last_seen"]) for g in grant] == [("test phone", WALL, WALL)]
    assert not h.window.active and h.engine.connected() == 1
    assert len(phone.inbox) == 0

  def test_window_is_held_once_the_phone_proves_the_code(self, mocker):
    h = Harness(mocker)
    h.open_window()
    h.window.tick(0.0)
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 110.0)
    h.window.tick(130.0)
    assert h.window.active
    h.allow(135.0)
    phone.pop_record(s.DECISION)
    phone.phone_keys(136.0)
    assert phone.pop_record(s.GRANT_RESULT) == bytes([s.GRANT_ADDED])
    assert h.window.state()["reason"] == "granted"

  def test_phone_keys_not_sent_in_time(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.allow(0.0)
    phone.pop_record(s.DECISION)
    h.tick(30.0)
    assert h.grant_list() == [] and not phone.connected
    assert h.window.state()["reason"] == "timeout"

  def test_phone_leaving_closes_the_held_window(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.route([("disconnect", phone.device)])
    assert not h.window.active and h.window.state()["reason"] == "phone_left"

  def test_deny_closes_window_without_a_grant(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.allow(1.0, allow=False)
    assert phone.pop_record(s.DECISION) == bytes([s.DENY])
    assert not phone.connected and not h.window.active
    assert h.window.state()["reason"] == "denied" and h.grant_list() == []

  def test_no_answer_after_thirty_seconds(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.tick(29.9)
    assert phone.connected and h.engine.prompt(29.9) is not None
    h.tick(30.0)
    assert phone.pop_record(s.DECISION) == bytes([s.NO_ANSWER])
    assert not phone.connected and h.window.state()["reason"] == "no_answer"

  def test_check_code_wait_is_not_cut_by_the_idle_rule(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.tick(20.0)
    assert phone.connected and not phone.broken

  def test_no_idle_drop_after_allow(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.allow(5.0)
    phone.pop_record(s.DECISION)
    h.tick(25.0)
    assert phone.connected and h.engine.prompt(25.0) is None

  def test_wrong_code_five_times_closes_the_window(self, mocker):
    h = Harness(mocker)
    h.open_window()
    for attempt in range(5):
      phone = h.new_phone(lid=0x100 + attempt, device=f"/dev/{attempt}")
      phone.ceremony(b"00000001" if attempt % 2 else b"00000002", 0.0)
      assert phone.pop_error() == (s.ERR_WINDOW_CLOSED if attempt == 4 else s.ERR_WRONG_CODE)
      assert not phone.connected
      assert h.window.active == (attempt < 4)
    assert h.window.state()["reason"] == "wrong_codes"

  def test_wrong_code_counts_only_the_window_it_was_made_for(self, mocker):
    h = Harness(mocker)
    h.open_window(0.0)
    for attempt in range(4):
      phone = h.new_phone(lid=0x200 + attempt, device=f"/w/{attempt}")
      phone.ceremony(b"00000001", 0.0)
      assert phone.pop_error() == s.ERR_WRONG_CODE
    h.window.cancel()
    h.open_window(1.0)
    phone = h.new_phone(lid=0x300, device="/w/new")
    phone.ceremony(h.window.secret()[0], 1.0)
    assert phone.connected and not phone.broken

  def test_connect_start_with_no_window_gets_error_one(self, mocker):
    h = Harness(mocker)
    phone = h.new_phone()
    phone.start(0.0)
    assert phone.pop_error() == s.ERR_NO_WINDOW and not phone.connected

  def test_wrong_protocol_version_gets_error_three(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    h.send(phone, bytes([s.CONNECT_START, 2]), 0.0)
    assert phone.pop_error() == s.ERR_VERSION

  def test_second_ceremony_while_one_is_running_gets_busy(self, mocker):
    h = Harness(mocker)
    h.open_window()
    first = h.new_phone(lid=0x10, device="/a")
    second = h.new_phone(lid=0x20, device="/b")
    first.start(0.0)
    second.start(0.0)
    assert second.pop_error() == s.ERR_BUSY and not second.connected
    assert first.connected

  def test_unauthenticated_idle_timeout(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.start(0.0)
    phone.pop(s.CONNECT_WINDOW)
    h.tick(9.9)
    assert phone.connected
    h.tick(10.0)
    assert phone.pop_error() == s.ERR_TIMEOUT and not phone.connected

  def test_unauthenticated_total_timeout_is_sixty_seconds(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.start(0.0)
    phone.pop(s.CONNECT_WINDOW)
    h.engine.on_write(phone.device, link.frames(bytes([s.PAKE_A]) + b"\x00" * 32, phone.lid, 20)[0], 23, 55.0)
    h.tick(59.9)
    assert phone.connected
    h.tick(60.0)
    assert not phone.connected

  def test_window_closing_drops_a_ceremony_in_progress(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.window.cancel("cancel")
    h.tick(1.0)
    assert not phone.connected

  def test_new_window_drops_the_old_ceremony(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.window.open(1.0, 2)
    h.tick(1.0)
    assert not phone.connected

  def test_bad_device_signature_drops_without_a_grant(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.ceremony(h.window.secret()[0], 0.0)
    h.allow(0.0)
    phone.pop_record(s.DECISION)
    phone.pop_record(s.DEVICE_KEYS)
    bad = {"v": 1, "spki": grants.b64(spki_of(phone.key)), "alg": "ES256", "static": grants.b64(b"\x01" * 32),
           "id": {"name": "x"}, "sig": grants.b64(b"\x00" * 70)}
    h.send_record(phone, s.PHONE_KEYS, json.dumps(bad).encode(), 0.0)
    assert not phone.connected and h.grant_list() == []

  def test_limit_of_eight_phones(self, mocker):
    values = {"SunnylinkLocalBleGrants": [{"spki": f"x{i}", "static": grants.b64(b"\x02" * 32), "name": "p", "added": 1,
                                           "last_seen": 1} for i in range(grants.MAX_PHONES)]}
    h = Harness(mocker, values)
    h.open_window()
    phone = h.new_phone()
    assert full_ceremony(h, phone) == s.GRANT_REFUSED
    assert len(h.grant_list()) == grants.MAX_PHONES and not h.window.active
    assert not phone.connected

  def test_duplicate_link_id_is_dropped(self, mocker):
    h = Harness(mocker)
    h.open_window()
    first = h.new_phone(lid=0x77, device="/first")
    second = h.new_phone(lid=0x77, device="/second")
    first.start(0.0)
    second.start(0.0)
    assert not second.connected and first.connected
    assert first.pop(s.CONNECT_WINDOW)[0] == s.PROTO

  def test_bad_frame_flags_drop_the_link(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    frame = bytes([0x02]) + phone.lid.to_bytes(2, "big") + bytes([s.PROTO])
    h.engine.on_write(phone.device, frame, 23, 0.0)
    assert h.engine.on_write(phone.device, frame, 23, 0.0) == [("disconnect", phone.device)]

  def test_oversized_clear_message_before_session_is_dropped(self, mocker):
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    phone.start(0.0)
    phone.pop(s.CONNECT_WINDOW)
    phone.mtu = 247
    h.send(phone, bytes([s.PAKE_A]) + b"\x00" * 1100, 0.0)
    assert not phone.connected

  def test_grants_key_is_created_once(self, mocker):
    h = Harness(mocker)
    first = grants.static_private(h.params).public_key().public_bytes_raw()
    assert len(h.params.data[grants.KEY_KEY]) == 32
    assert grants.static_private(h.params).public_key().public_bytes_raw() == first


class TestReconnect(OpenpilotTestCase):
  def granted(self, mocker) -> tuple[Harness, Phone]:
    h = Harness(mocker)
    h.open_window()
    phone = h.new_phone()
    assert full_ceremony(h, phone) == s.GRANT_ADDED
    h.engine.on_disconnect(phone.device)
    phone.connected = False
    return h, phone

  def comma_static(self, h: Harness) -> bytes:
    return grants.static_private(h.params).public_key().public_bytes_raw()

  def test_resume_with_a_known_phone(self, mocker):
    h, phone = self.granted(mocker)
    h.clock["wall"] = WALL + 500
    again = h.new_phone(lid=0x4321, device="/again")
    again.static = phone.static
    again.resume_start(self.comma_static(h), 10.0)
    assert again.connected and again.records is not None
    assert h.grant_list()[0]["last_seen"] == WALL + 500
    assert len(again.rpc("phones.list", 10.0)["result"]) == 1

  def test_removed_phone_gets_error_eight(self, mocker):
    h, phone = self.granted(mocker)
    h.route(h.engine.remove(h.grant_list()[0]["spki"]))
    again = h.new_phone(lid=0x4321, device="/again")
    again.static = phone.static
    again.resume_start(self.comma_static(h), 10.0)
    assert again.pop_error() == s.ERR_UNKNOWN_PHONE and not again.connected
    assert h.grant_list() == []

  def test_remove_drops_a_live_link_at_once(self, mocker):
    h, phone = self.granted(mocker)
    again = h.new_phone(lid=0x4321, device="/again")
    again.static = phone.static
    again.resume_start(self.comma_static(h), 10.0)
    assert again.connected
    h.route(h.engine.remove(h.grant_list()[0]["spki"]))
    assert not again.connected

  def test_no_idle_drop_on_an_authenticated_session(self, mocker):
    h, phone = self.granted(mocker)
    again = h.new_phone(lid=0x4321, device="/again")
    again.static = phone.static
    again.resume_start(self.comma_static(h), 0.0)
    h.tick(500.0)
    assert again.connected and h.engine.connected() == 1

  def test_resumed_phone_is_the_only_live_link_for_its_grant(self, mocker):
    h, phone = self.granted(mocker)
    first = h.new_phone(lid=0x4321, device="/one")
    first.static = phone.static
    first.resume_start(self.comma_static(h), 0.0)
    second = h.new_phone(lid=0x4322, device="/two")
    second.static = phone.static
    second.resume_start(self.comma_static(h), 1.0)
    assert second.connected and not first.connected


class TestRpcOverSession(OpenpilotTestCase):
  def session(self, mocker, values=None) -> tuple[Harness, Phone]:
    known = {"DongleId", "CarParamsSP", "SunnylinkTempFault", "BluetoothAllowed", "BluetoothEnabled", "SunnylinkLocalBleGrants"}
    h = Harness(mocker, {"SunnylinkEnabled": True} | (values or {}), known)
    h.open_window()
    phone = h.new_phone()
    assert full_ceremony(h, phone) == s.GRANT_ADDED
    return h, phone

  def test_status_get(self, mocker):
    h, phone = self.session(mocker)
    mocker.patch("openpilot.sunnypilot.system.ble.rpc.get_version", return_value="0.9.0")
    mocker.patch("openpilot.sunnypilot.system.ble.rpc.HARDWARE.get_os_version", return_value="19.9")
    wpa = mocker.patch("openpilot.common.hardware.comma.hardware.wpa_supplicant_cmd",
                       return_value={"mode": "station", "wpa_state": "COMPLETED", "ssid": "home"})
    result = phone.rpc("status.get", 0.0, rid=5)
    assert result["id"] == 5
    assert result["result"]["network"] == {"wifi_ssid": "home", "hotspot": False}
    assert result["result"]["phones"] == 1 and result["result"]["dongle_id"] == "dongle"
    wpa.return_value = {"mode": "AP", "wpa_state": "COMPLETED", "ssid": "weedle-1234"}
    assert phone.rpc("status.get", 1.0, rid=6)["result"]["network"] == {"wifi_ssid": None, "hotspot": True}

  def test_unknown_method_is_not_found(self, mocker):
    h, phone = self.session(mocker)
    assert phone.rpc("nope", 0.0)["error"]["code"] == -32601

  def test_params_set_and_get(self, mocker):
    h, phone = self.session(mocker)
    assert phone.rpc("params.set", 0.0, {"values": {"CarParamsSP": "x"}})["result"] == {"ok": ["CarParamsSP"]}
    got = phone.rpc("params.get", 0.0, {"keys": ["CarParamsSP", "SunnylinkTempFault"]})
    assert got["result"] == {"values": {"CarParamsSP": "x", "SunnylinkTempFault": None}}

  def test_params_refusals_are_all_or_nothing(self, mocker):
    h, phone = self.session(mocker)
    for keys in (["BluetoothAllowed"], ["BluetoothEnabled"], ["SunnylinkLocalBleGrants"], ["AdbEnabled"]):
      assert phone.rpc("params.get", 0.0, {"keys": keys})["error"]["code"] == -32001
    refused = phone.rpc("params.set", 0.0, {"values": {"CarParamsSP": "y", "BluetoothAllowed": False}})
    assert refused["error"]["code"] == -32001
    assert h.params.data.get("CarParamsSP") is None
    assert phone.rpc("params.set", 0.0, {"values": {"NotAKey": 1}})["error"]["code"] == -32001

  def test_params_get_limits_the_key_count(self, mocker):
    h, phone = self.session(mocker)
    assert phone.rpc("params.get", 0.0, {"keys": ["DongleId"] * 33})["error"]["code"] == -32001

  def test_hotspot_start_answers_when_up(self, mocker):
    h, phone = self.session(mocker)
    h.send_record(phone, s.RPC, json.dumps({"jsonrpc": "2.0", "id": 4, "method": "hotspot.start"}).encode(), 0.0)
    assert phone.inbox == [] and h.wifi.requested is True
    h.wifi.active = True
    h.tick(1.0)
    assert json.loads(phone.pop_record(s.RPC)) == {"jsonrpc": "2.0", "id": 4, "result": {"ssid": "weedle-test", "password": "pw-test"}}

  def test_hotspot_start_times_out(self, mocker):
    h, phone = self.session(mocker)
    h.send_record(phone, s.RPC, json.dumps({"jsonrpc": "2.0", "id": 9, "method": "hotspot.start"}).encode(), 0.0)
    h.tick(30.0)
    reply = json.loads(phone.pop_record(s.RPC))
    assert reply["id"] == 9 and reply["error"]["code"] == -32001

  def test_hotspot_credentials_refused_while_off(self, mocker):
    h, phone = self.session(mocker)
    assert phone.rpc("hotspot.credentials", 0.0)["error"]["code"] == -32001
    h.wifi.active = True
    assert phone.rpc("hotspot.credentials", 0.0)["result"] == {"ssid": "weedle-test", "password": "pw-test"}

  def test_hotspot_stop(self, mocker):
    h, phone = self.session(mocker)
    h.wifi.active = True
    assert phone.rpc("hotspot.stop", 0.0)["result"] == {}
    assert h.wifi.requested is False

  def test_phones_list_marks_this_phone(self, mocker):
    h, phone = self.session(mocker)
    listing = phone.rpc("phones.list", 0.0)["result"]
    assert listing == [{"name": "test phone", "added": WALL, "last_seen": WALL, "this": True}]

  def test_forget_self_drops_the_grant_and_the_link(self, mocker):
    h, phone = self.session(mocker)
    response = phone.rpc("phones.forgetSelf", 0.0)
    assert response["result"] == {}
    assert h.grant_list() == [] and not phone.connected

  def test_record_cap_after_session(self, mocker):
    h, phone = self.session(mocker)
    phone.mtu = 247
    big = {"jsonrpc": "2.0", "id": 3, "method": "nope", "params": {"pad": "x" * 9000}}
    h.send_record(phone, s.RPC, json.dumps(big).encode(), 0.0)
    assert phone.connected and json.loads(phone.pop_record(s.RPC))["error"]["code"] == -32601
    h.send(phone, phone.records.seal(bytes([s.RPC]) + b" " * 17000), 0.0)
    assert not phone.connected
