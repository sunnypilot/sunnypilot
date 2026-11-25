"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass

from openpilot.sunnypilot.system import connect_phone
from openpilot.sunnypilot.system.ble import cpace, grants, link, noise
from openpilot.sunnypilot.system.ble.rpc import Rpc

PROTO = 1
CONNECT_START, CONNECT_WINDOW, PAKE_A, PAKE_B, CONFIRM_A, CONFIRM_B = 0x01, 0x02, 0x03, 0x04, 0x05, 0x06
RESUME_1, RESUME_2, ERROR = 0x10, 0x11, 0x7F
DECISION, DEVICE_KEYS, PHONE_KEYS, GRANT_RESULT, RPC = 0x30, 0x31, 0x32, 0x33, 0x40
ERR_NO_WINDOW, ERR_BUSY, ERR_VERSION, ERR_WRONG_CODE, ERR_WINDOW_CLOSED, ERR_TIMEOUT, ERR_UNKNOWN_PHONE = 1, 2, 3, 4, 5, 6, 8
ALLOW, DENY, NO_ANSWER = 1, 2, 3
GRANT_ADDED, GRANT_REFUSED = 1, 2  # 3 reserved
RESUMED = 1
RESUME_1_LEN = 32 + 1 + 16  # e, then one AEAD of the proto byte
MAX_WRONG = 5
IDLE_SECONDS = 10.0
TOTAL_SECONDS = 60.0
ALLOW_SECONDS = 30.0
PRE_AUTH = ("new", "start", "confirm")
CEREMONY = ("start", "confirm", "decide", "keys")
HELD = ("decide", "keys")  # the phone proved the code; the window waits on these

Action = tuple[str, object]  # ("notify", frame bytes) or ("disconnect", device path)


@dataclass(eq=False)
class _Link:
  device: str
  connected: float
  last: float
  mtu: int = 23
  link_id: int = 0
  reasm: link.Reassembler | None = None
  phase: str = "new"
  since: float = 0.0
  nonce: bytes = b""
  sid: bytes = b""
  start_body: bytes = b""
  window_body: bytes = b""
  cp: cpace.Cpace | None = None
  isk: bytes = b""
  ya: bytes = b""
  yb: bytes = b""
  th: bytes = b""
  check: str = ""
  records: link.Records | None = None
  phone: dict | None = None
  grant: str = ""


class Engine:
  def __init__(self, params, window, *, wifi: Callable | None = None, wall: Callable[[], float] = time.time):  # noqa: TID251 unix time: the app shows added and last_seen
    self._params = params
    self._window = window
    self._wall = wall
    self._links: dict[str, _Link] = {}
    self._fail_nonce = b""
    self._fails = 0
    self._rpc = Rpc(params, wifi)

  def on_write(self, device: str, value: bytes, mtu: int, now: float) -> list[Action]:
    lk = self._links.get(device)
    if lk is None:
      lk = self._links[device] = _Link(device, connected=now, last=now)
    lk.mtu = mtu
    if lk.reasm is None:
      if len(value) < 3:
        return self._drop(lk)
      lid = int.from_bytes(value[1:3], "big")
      # the id is bound to the first connection that uses it; a newcomer with a used id is dropped
      if lid == 0 or any(o.link_id == lid for o in self._links.values() if o is not lk):
        return self._drop(lk)
      lk.link_id, lk.reasm = lid, link.Reassembler(lid)
    lk.last = now
    try:
      msg = lk.reasm.feed(value)
      if msg is None:
        return []
      return self._message(lk, msg, now)
    except (ValueError, KeyError, TypeError):
      return self._drop(lk)

  def on_disconnect(self, device: str):
    if (lk := self._links.get(device)) is not None:
      self._drop(lk)

  def tick(self, now: float) -> list[Action]:
    acts: list[Action] = []
    secret = self._window.secret()
    for lk in list(self._links.values()):
      if self._links.get(lk.device) is not lk:
        continue
      if lk.phase in CEREMONY and (secret is None or lk.nonce != secret[1]):
        acts += self._drop(lk)
      elif lk.phase in PRE_AUTH and (now - lk.last >= IDLE_SECONDS or now - lk.connected >= TOTAL_SECONDS):
        acts += self._error(lk, ERR_TIMEOUT)
      elif lk.phase == "decide" and now - lk.since >= ALLOW_SECONDS:
        self._window.cancel("no_answer")
        acts += self._record(lk, DECISION, bytes([NO_ANSWER])) + self._drop(lk)
      elif lk.phase == "keys" and now - lk.since >= ALLOW_SECONDS:
        self._window.cancel("timeout")
        acts += self._drop(lk)
    for device, response in self._rpc.poll(now):
      lk = self._links.get(device)
      if lk is not None and lk.phase == "session":
        acts += self._record(lk, RPC, _json(response))
    return acts

  def prompt(self, now: float) -> dict | None:
    lk = next((o for o in self._links.values() if o.phase == "decide"), None)
    if lk is None:
      return None
    return {"step": "allow", "check": f"{lk.check[:3]} {lk.check[3:]}", "until": lk.since + ALLOW_SECONDS}

  def connected(self) -> int:
    return sum(1 for lk in self._links.values() if lk.phase == "session")

  def answer(self, allow: bool, now: float) -> list[Action]:
    lk = next((o for o in self._links.values() if o.phase == "decide"), None)
    if lk is None:
      return []
    if not allow:
      self._window.cancel("denied")
      return self._record(lk, DECISION, bytes([DENY])) + self._drop(lk)
    acts = self._record(lk, DECISION, bytes([ALLOW]))
    try:
      spki, key = connect_phone.device_identity()
    except RuntimeError:
      self._window.cancel("no_key")
      return acts + self._drop(lk)
    static = grants.static_private(self._params).public_key().public_bytes_raw()
    alg, sig = link.sign(key, link.signed_bytes("D", lk.th, spki, static))
    ids = {"dongle_id": self._params.get("DongleId"), "serial": self._params.get("HardwareSerial")}
    doc = {"v": 1, "spki": grants.b64(spki), "alg": alg, "static": grants.b64(static), "id": ids, "sig": grants.b64(sig)}
    lk.phase, lk.since, lk.last = "keys", now, now
    return acts + self._record(lk, DEVICE_KEYS, _json(doc))

  def remove(self, phone: str | None) -> list[Action]:
    if not phone or not any(g["spki"] == phone for g in grants.load(self._params)):
      return []
    return self._remove_grant(phone)

  def _message(self, lk: _Link, msg: bytes, now: float) -> list[Action]:
    if lk.records is not None:
      inner = lk.records.open(msg)
      if not inner:
        return self._drop(lk)
      typ, body = inner[0], inner[1:]
      if lk.phase == "keys" and typ == PHONE_KEYS:
        return self._phone_keys(lk, body, now)
      if lk.phase == "session" and typ == RPC:
        return self._rpc_request(lk, body, now)
      return self._drop(lk)
    typ, body = msg[0], msg[1:]
    if lk.phase == "new" and typ == CONNECT_START:
      return self._start(lk, body, now)
    if lk.phase == "new" and typ == RESUME_1:
      return self._resume(lk, body, now)
    if lk.phase == "start" and typ == PAKE_A:
      return self._pake(lk, body)
    if lk.phase == "confirm" and typ == CONFIRM_A:
      return self._confirm(lk, body, now)
    return self._drop(lk)

  def _start(self, lk: _Link, body: bytes, now: float) -> list[Action]:
    if body != bytes([PROTO]):
      return self._error(lk, ERR_VERSION)
    secret = self._window.secret()
    if secret is None:
      return self._error(lk, ERR_NO_WINDOW)
    if any(o is not lk and o.phase in CEREMONY for o in self._links.values()):
      return self._error(lk, ERR_BUSY)
    prs, nonce = secret
    attempt = secrets.token_bytes(16)
    lk.nonce, lk.sid = nonce, nonce + attempt
    lk.start_body = body
    lk.window_body = bytes([PROTO, link.PAKE_SUITE]) + nonce + attempt
    lk.cp = cpace.Cpace(False, prs, lk.sid, lk.start_body, lk.window_body)
    lk.phase, lk.since = "start", now
    return self._plain(lk, CONNECT_WINDOW, lk.window_body)

  def _pake(self, lk: _Link, body: bytes) -> list[Action]:
    if len(body) != 32:
      return self._drop(lk)
    try:
      lk.isk = lk.cp.isk(body)
    except cpace.CpaceError:
      return self._drop(lk)
    lk.ya, lk.yb = body, lk.cp.public
    lk.phase = "confirm"
    return self._plain(lk, PAKE_B, lk.yb)

  def _confirm(self, lk: _Link, body: bytes, now: float) -> list[Action]:
    if len(body) != 64:
      return self._drop(lk)
    if not lk.cp.check(lk.isk, lk.ya, body):
      return self._wrong_code(lk)
    tag = lk.cp.tag(lk.isk)
    lk.th = link.transcript(lk.start_body, lk.window_body, lk.ya, lk.yb, body, tag)
    p2c, c2p, lk.check = link.session_keys(lk.isk, lk.sid)
    lk.records = link.Records(c2p, p2c, lk.link_id)
    lk.reasm.cap = link.SESSION_CAP
    lk.phase, lk.since, lk.last = "decide", now, now
    self._window.hold()
    return self._plain(lk, CONFIRM_B, tag)

  def _wrong_code(self, lk: _Link) -> list[Action]:
    if lk.nonce != self._fail_nonce:
      self._fail_nonce, self._fails = lk.nonce, 0
    self._fails += 1
    if self._fails >= MAX_WRONG:
      self._window.cancel("wrong_codes")
      return self._error(lk, ERR_WINDOW_CLOSED)
    return self._error(lk, ERR_WRONG_CODE)

  def _phone_keys(self, lk: _Link, body: bytes, now: float) -> list[Action]:
    doc = json.loads(body)
    if doc.get("v") != 1 or doc.get("alg") != "ES256":
      return self._drop(lk)
    spki, static, sig = grants.unb64(doc["spki"]), grants.unb64(doc["static"]), grants.unb64(doc["sig"])
    name = doc["id"]["name"]
    if len(static) != 32 or not isinstance(name, str) or len(name.encode()) > 80:
      return self._drop(lk)
    if not link.verify("ES256", spki, link.signed_bytes("P", lk.th, spki, static), sig):
      return self._drop(lk)
    lk.phone = {"spki": grants.b64(spki), "static": grants.b64(static), "name": name}
    lk.last = now
    saved = grants.load(self._params)
    known = any(g["spki"] == lk.phone["spki"] for g in saved)
    if not known and len(saved) >= grants.MAX_PHONES:
      self._window.cancel("limit")
      return self._record(lk, GRANT_RESULT, bytes([GRANT_REFUSED])) + self._drop(lk)
    return self._grant(lk)

  def _grant(self, lk: _Link) -> list[Action]:
    wall = int(self._wall())
    saved = grants.load(self._params)
    old = next((g for g in saved if g["spki"] == lk.phone["spki"]), None)
    kept = [g for g in saved if g is not old]
    kept.append(lk.phone | {"added": old["added"] if old else wall, "last_seen": wall})
    grants.save(self._params, kept)
    self._window.cancel("granted")
    lk.grant, lk.phone, lk.phase = lk.phone["spki"], None, "session"
    return self._drop_grant(lk.grant, keep=lk) + self._record(lk, GRANT_RESULT, bytes([GRANT_ADDED]))

  def _resume(self, lk: _Link, body: bytes, now: float) -> list[Action]:
    if len(body) != RESUME_1_LEN:
      return self._drop(lk)
    static = grants.static_private(self._params)
    for g in grants.load(self._params):
      hs = noise.KKHandshake(False, static, grants.unb64(g["static"]))
      try:
        payload = hs.read(body)
      except noise.NoiseError:
        continue
      if payload != bytes([PROTO]):
        return self._error(lk, ERR_VERSION)
      reply = hs.write(bytes([RESUMED]))
      send, recv = hs.split()
      lk.records = link.Records(send, recv, lk.link_id)
      lk.reasm.cap = link.SESSION_CAP
      lk.grant, lk.phase, lk.last = g["spki"], "session", now
      self._touch(g["spki"])
      return self._drop_grant(lk.grant, keep=lk) + self._plain(lk, RESUME_2, reply)
    return self._error(lk, ERR_UNKNOWN_PHONE)

  def _touch(self, spki: str):
    saved = grants.load(self._params)
    for g in saved:
      if g["spki"] == spki:
        g["last_seen"] = int(self._wall())
    grants.save(self._params, saved)

  def _rpc_request(self, lk: _Link, body: bytes, now: float) -> list[Action]:
    response, after = self._rpc.handle(lk.device, body, grants.load(self._params), lk.grant, now)
    acts = self._record(lk, RPC, _json(response)) if response is not None else []
    if after == "forget":
      acts += self._remove_grant(lk.grant)
    return acts

  def _remove_grant(self, spki: str) -> list[Action]:
    grants.save(self._params, [g for g in grants.load(self._params) if g["spki"] != spki])
    return self._drop_grant(spki)

  def _drop_grant(self, spki: str, keep: _Link | None = None) -> list[Action]:
    acts: list[Action] = []
    for lk in list(self._links.values()):
      if lk.grant == spki and lk is not keep:
        acts += self._drop(lk)
    return acts

  def _send(self, lk: _Link, message: bytes) -> list[Action]:
    return [("notify", frame) for frame in link.frames(message, lk.link_id, lk.mtu - link.FRAME_HEADER)]

  def _plain(self, lk: _Link, typ: int, body: bytes) -> list[Action]:
    return self._send(lk, bytes([typ]) + body)

  def _record(self, lk: _Link, typ: int, body: bytes) -> list[Action]:
    return self._send(lk, lk.records.seal(bytes([typ]) + body))

  def _error(self, lk: _Link, code: int) -> list[Action]:
    return self._plain(lk, ERROR, bytes([code])) + self._drop(lk)

  def _drop(self, lk: _Link) -> list[Action]:
    if self._links.get(lk.device) is lk:
      del self._links[lk.device]
    if lk.phase in HELD:
      # the window was held for this phone; it does not reopen for another
      self._window.cancel("phone_left")
    return [("disconnect", lk.device)]


def _json(obj) -> bytes:
  return json.dumps(obj, separators=(",", ":")).encode()
