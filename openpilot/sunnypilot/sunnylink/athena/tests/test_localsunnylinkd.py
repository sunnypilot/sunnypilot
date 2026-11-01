"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import json
import shutil
import tempfile
import threading
import time
from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest import mock

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from websocket import WebSocket

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.system.athena import rpc as rpc_module
from openpilot.sunnypilot.sunnylink.athena import local_auth_daemon, localsunnylinkd, sunnylinkd
from openpilot.sunnypilot.sunnylink.athena.local_auth import (
  AUTHENTICATE_PURPOSE,
  VERSION,
  AuthorizationError,
  AuthorizedSession,
  LocalAuthority,
  Origin,
  encode64,
  key_id,
  statement,
)
from openpilot.sunnypilot.sunnylink.athena.local_discovery import LocalDiscovery
from openpilot.sunnypilot.sunnylink.athena.local_params import ENROLL, REVOKE, cloud_may_write, is_local_param

CHALLENGE = "A" * 43  # base64url of 32 zero bytes: the canonical challenge shape

ENROLLMENT_TRANSPORT_VALUE = "eyJ2IjozfQ=="  # base64 of {"v":3}


class _FakeParams(dict):
  """Only the Params calls the daemon makes; a dict is enough to steer them."""

  def get_bool(self, key):
    return bool(self.get(key))

  def put_bool(self, key, value, block=False):
    self[key] = value

  def put(self, key, value, block=False):
    self[key] = value

  def remove(self, key):
    self.pop(key, None)

  def all_keys(self):
    return [key.encode() for key in self]

  def get_type(self, key):
    return SimpleNamespace(value=1)


class _FakeWs:
  """A WebSocket that replays queued frames, then reports the peer gone."""

  def __init__(self, messages=()):
    self._messages = list(messages)
    self.sent: list[str] = []
    self.closed = False
    self.timeouts: list[float] = []

  def settimeout(self, timeout):
    self.timeouts.append(timeout)

  def recv(self):
    if self._messages:
      return self._messages.pop(0)
    raise sunnylinkd.WebSocketConnectionClosedException("peer gone")

  def send(self, payload):
    self.sent.append(payload)

  def close(self):
    self.closed = True


class _FakeSession:
  """Stands in for an AuthorizedSession: records the gated method, never executes it."""

  def __init__(self, key_id: str = "grant-key"):
    self.calls: list[str] = []
    self.grant = SimpleNamespace(app_id=key_id)
    self.closed = False

  def invoke(self, method, handler, *args, **kwargs):
    self.calls.append(method)
    return {"ok": True}

  def close(self):
    self.closed = True


class _CallingSession(_FakeSession):
  """Like _FakeSession, but actually runs the gated handler, as AuthorizedSession.invoke does."""

  def invoke(self, method, handler, *args, **kwargs):
    return handler(*args, **kwargs)


class _FakeDiscovery:
  def __init__(self, endpoints: Iterable[str] = (), recent: Iterable[str] | None = None,
               app_ids: dict[str, str] | None = None):
    self._endpoints: list[str] = list(endpoints)
    # What the shorter backoff window returns; None means "same as the dial window".
    self._recent: list[str] | None = None if recent is None else list(recent)
    self._app_ids: dict[str, str] = dict(app_ids or {})

  def fresh_endpoints(self, max_age_s=None):
    if max_age_s is not None and self._recent is not None:
      return list(self._recent)
    return list(self._endpoints)

  def fresh_peers(self, max_age_s=None):
    return [(e, self._app_ids.get(e, "grant-key")) for e in self.fresh_endpoints(max_age_s)]

  def start(self):
    pass

  def stop(self):
    pass


class _Daemon(localsunnylinkd.LocalSunnylinkd):
  """A local daemon with scripted trust state, so target selection is testable in isolation."""

  def __init__(self, endpoints=(), enrolled=True, discovery=None, known=("grant-key",),
               app_ids=None, **params):
    fake_discovery = discovery if discovery is not None else _FakeDiscovery(endpoints, app_ids=app_ids)
    super().__init__(params=cast(Params, _FakeParams(**params)),
                     discovery=cast(LocalDiscovery, fake_discovery))
    self._enrolled = enrolled
    self._known = set(known)

  def enrolled(self):
    return self._enrolled

  def known_app_ids(self):
    return set(self._known)


def _challenge(phone_key_id: str) -> str:
  return json.dumps({"v": VERSION, "purpose": AUTHENTICATE_PURPOSE, "phone_key_id": phone_key_id, "challenge": CHALLENGE})


def _authority():
  device_key = ec.generate_private_key(ec.SECP256R1())
  return LocalAuthority("cloud-device", "comma-device", device_key, persist=lambda _registry: None)


def _enrollment_json(authority: LocalAuthority, app_key: ec.EllipticCurvePrivateKey, name="Test phone") -> str:
  public = encode64(app_key.public_key().public_bytes(
    serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo))
  data = {"v": VERSION, "cloud_device_id": authority.cloud_device_id, "comma_device_id": authority.comma_device_id,
          "device_key_id": authority.device_key_id, "public_key": public,
          "key_id": key_id(app_key.public_key()), "app_name": name}
  signed_fields = ("cloud_device_id", "comma_device_id", "device_key_id",
                   "public_key", "key_id", "app_name")
  proof = statement("enroll", *(str(data[field]) for field in signed_fields))
  data["signature"] = encode64(app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
  return json.dumps(data)


def _await(condition, timeout=5.0, description="condition") -> bool:
  """Bounded polling: a failure fails fast instead of hanging the suite."""
  deadline = time.monotonic() + timeout
  while time.monotonic() < deadline:
    if condition():
      return True
    time.sleep(0.01)
  return False


class TestLocalTargets(OpenpilotTestCase):
  """What the local daemon dials, and when it runs at all."""

  def test_pinned_endpoint_converts_a_beacon_to_tls(self):
    self.assertEqual("wss://10.0.0.7:8443", localsunnylinkd.pinned_endpoint("ws://10.0.0.7:8443"))
    self.assertIsNone(localsunnylinkd.pinned_endpoint("wss://10.0.0.7:8443"))
    self.assertIsNone(localsunnylinkd.pinned_endpoint("ws://10.0.0.7"))

  def test_an_enrolled_phone_is_dialed_over_pinned_tls(self):
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"])
    self.assertEqual("wss://10.0.0.7:8443", daemon.pick_target())

    daemon.backoffs["wss://10.0.0.7:8443"] = time.monotonic() + 60
    self.assertIsNone(daemon.pick_target())

  def test_a_failed_dial_backs_off_for_a_tick_then_ramps(self):
    """A phone that keeps announcing while it refuses to serve ramps up, and no further."""
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"])
    endpoint = "wss://10.0.0.7:8443"
    with mock.patch.object(daemon, "dial", side_effect=AuthorizationError("refused")):
      daemon.serve(endpoint, None)
      first = daemon.backoffs[endpoint] - time.monotonic()
      for _ in range(8):
        daemon.serve(endpoint, None)
      last = daemon.backoffs[endpoint] - time.monotonic()

    # The app is a foreground-only server: one missed dial is worth a beacon interval, not the
    # five-minute cloud reconnect ceiling.
    self.assertLess(first, localsunnylinkd.ENDPOINT_BACKOFF_S)
    self.assertGreater(first, 0)
    self.assertLessEqual(last, localsunnylinkd.ENDPOINT_BACKOFF_MAX_S)
    self.assertEqual(9, daemon.failures[endpoint])

  def test_a_failed_local_dial_leaves_the_cloud_links_state_alone(self):
    """LastSunnylinkPingTime is the CLOUD link's heartbeat, not ours to clear.

    The sidebar reads it for ONLINE/ERROR/OFFLINE. A local dial failing (the phone switched local
    connections off, walked away, went to sleep) says nothing about the cloud connection, which
    keeps running in sunnylinkd; wiping the timestamp made the car claim it was offline until the
    next cloud ping, which is exactly the "device is in an error state" after the switch.
    """
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"], LastSunnylinkPingTime=12345)
    with mock.patch.object(daemon, "dial", side_effect=AuthorizationError("refused")):
      daemon.serve("wss://10.0.0.7:8443", None)

    self.assertEqual(12345, daemon.params.get("LastSunnylinkPingTime"))
    self.assertEqual(1, daemon.failures["wss://10.0.0.7:8443"])

  def test_the_first_failed_dial_waits_only_one_tick(self):
    """One missed dial is worth a tick, not a beacon interval: nothing else re-dials before then."""
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"])
    endpoint = "wss://10.0.0.7:8443"
    with mock.patch.object(daemon, "dial", side_effect=AuthorizationError("refused")):
      daemon.serve(endpoint, None)
      delay = daemon.backoffs[endpoint] - time.monotonic()

    self.assertGreater(delay, 0)
    self.assertLessEqual(delay, localsunnylinkd.TICK_INTERVAL_S + 0.05)

  def test_a_phone_that_went_quiet_past_the_forget_window_clears_its_ramp(self):
    """A network change silences the app for a moment without moving it out of the dial window.

    Moving from home Wi-Fi to the car's hotspot (or roaming between mesh nodes) reassociates the
    phone: a few beacon intervals pass with no announcement, and the ramp it earned on the old link
    must not follow it onto the new one. The endpoint stays dialable for the full beacon window, so
    the very next beacon is an immediate attempt rather than the rest of a penalty.
    """
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443"], recent=[])
    daemon = _Daemon(discovery=discovery)
    endpoint = "wss://10.0.0.7:8443"
    daemon.backoffs[endpoint] = time.monotonic() + 300
    daemon.failures[endpoint] = 5

    self.assertEqual(endpoint, daemon.pick_target())
    self.assertNotIn(endpoint, daemon.backoffs)
    self.assertNotIn(endpoint, daemon.failures)

  def test_a_phone_still_announcing_keeps_its_ramp(self):
    """The short window must not reset a ramp for a phone that is right there and refusing to serve."""
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443"], recent=["ws://10.0.0.7:8443"])
    daemon = _Daemon(discovery=discovery)
    endpoint = "wss://10.0.0.7:8443"
    daemon.backoffs[endpoint] = time.monotonic() + 300

    self.assertIsNone(daemon.pick_target())
    self.assertIn(endpoint, daemon.backoffs)

  def test_a_served_session_clears_the_backoff_ramp(self):
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"])
    endpoint = "wss://10.0.0.7:8443"
    daemon.backoffs[endpoint] = time.monotonic() + 60
    daemon.failures[endpoint] = 3

    with mock.patch.object(daemon, "dial", lambda endpoint, exit_event: None), \
         mock.patch.object(localsunnylinkd, "TICK_INTERVAL_S", 0):
      daemon.serve(endpoint, None)

    self.assertNotIn(endpoint, daemon.backoffs)
    self.assertNotIn(endpoint, daemon.failures)

  def test_a_phone_that_stopped_announcing_forgets_its_backoff(self):
    """Closing the app must not cost cloud-only service after it is reopened.

    The app is a foreground-only server the user opens and closes: a dial that failed while it
    was closed recorded a backoff against an endpoint that then had no beacons at all. Reopening
    the app re-announces within seconds, and that record would otherwise hold the device on the
    cloud for the rest of the backoff.
    """
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443"])
    daemon = _Daemon(discovery=discovery)
    endpoint = "wss://10.0.0.7:8443"
    daemon.backoffs[endpoint] = time.monotonic() + 300
    daemon.failures[endpoint] = 1

    # The app was closed: it announces nothing, so the failure outlives its reason.
    discovery._endpoints = []
    self.assertIsNone(daemon.pick_target())
    self.assertNotIn(endpoint, daemon.backoffs)
    self.assertNotIn(endpoint, daemon.failures)

    # The app is opened again: the device dials it now instead of waiting the record out.
    discovery._endpoints = ["ws://10.0.0.7:8443"]
    self.assertEqual(endpoint, daemon.pick_target())

  def test_a_pending_enrollment_is_dialed_even_before_any_grant(self):
    daemon = _Daemon(endpoints=["ws://10.0.0.7:8443"], known=("pending",),
                     app_ids={"ws://10.0.0.7:8443": "pending"})
    self.assertEqual("wss://10.0.0.7:8443", daemon.pick_target())

  def test_a_second_phone_is_dialed_while_the_first_holds_a_session(self):
    """The second-pairing bug: one long-lived session used to block every other phone.

    A phone keeps its session for as long as its app is open, so the old dial loop sat inside the
    first phone's session and never looked at the second. Pairing the Android phone next to an
    already-paired iPhone therefore never happened, and its app waited on "registration sent".
    """
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443", "ws://10.0.0.8:8443"],
                               app_ids={"ws://10.0.0.7:8443": "iphone", "ws://10.0.0.8:8443": "android"})
    daemon = _Daemon(discovery=discovery, known=("iphone", "android"))
    first, second = "wss://10.0.0.7:8443", "wss://10.0.0.8:8443"
    holding = threading.Event()
    with mock.patch.object(daemon, "dial", lambda endpoint, exit_event: holding.wait(10)):
      self.assertTrue(daemon.start_session(first, None))
      self.assertTrue(daemon.has_session(first))

      # The first phone's session is live: the second is STILL a target and still gets served.
      self.assertEqual([second], daemon.pick_targets())
      self.assertTrue(daemon.start_session(second, None))
      self.assertTrue(daemon.has_session(second))
      self.assertFalse(daemon.start_session(second, None), "one session per phone")
      holding.set()
    self.assertTrue(_await(lambda: not daemon._workers, description="session threads to exit"))

  def test_the_phone_that_is_still_pairing_is_dialed_first(self):
    """A phone being paired must not queue behind phones that are already paired."""
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443", "ws://10.0.0.8:8443"],
                               app_ids={"ws://10.0.0.7:8443": "iphone", "ws://10.0.0.8:8443": "android"})
    daemon = _Daemon(discovery=discovery, known=("iphone", "android"))

    with mock.patch.object(local_auth_daemon, "pending_enrollment",
                           return_value={"app_id": "android"}):
      self.assertEqual(["wss://10.0.0.8:8443", "wss://10.0.0.7:8443"], daemon.pick_targets())

  def test_the_run_loop_serves_every_known_phone_at_once(self):
    """End to end: both phones are dialed while neither has hung up."""
    discovery = _FakeDiscovery(["ws://10.0.0.7:8443", "ws://10.0.0.8:8443"],
                               app_ids={"ws://10.0.0.7:8443": "iphone", "ws://10.0.0.8:8443": "android"})
    daemon = _Daemon(discovery=discovery, known=("iphone", "android"),
                     SunnylinkEnabled=True, SunnylinkLocalEnabled=True)
    holding = threading.Event()
    dialed: list[str] = []

    def fake_dial(endpoint, exit_event):
      dialed.append(endpoint)
      holding.wait(10)

    stop = threading.Event()
    with mock.patch.object(daemon, "dial", fake_dial), \
         mock.patch.object(local_auth_daemon, "service_revoke_requests", lambda *a, **k: False), \
         mock.patch.object(local_auth_daemon, "claim_cloud_commands", lambda *a, **k: None), \
         mock.patch.object(localsunnylinkd, "TICK_INTERVAL_S", 0.01):
      loop = threading.Thread(target=daemon.run, args=(stop,), daemon=True)
      loop.start()
      both = {"wss://10.0.0.7:8443", "wss://10.0.0.8:8443"}
      self.assertTrue(_await(lambda: both <= set(dialed), description="both phones to be dialed"))
      stop.set()
      holding.set()
      loop.join(5)

    # Both were dialed while the other was still connected; a redial after the sessions ended is
    # expected, so only the set of phones matters.
    self.assertEqual(both, set(dialed))

  def test_a_beacon_from_an_unknown_phone_is_never_dialed(self):
    daemon = _Daemon(endpoints=["ws://10.0.0.9:8443"],
                     app_ids={"ws://10.0.0.9:8443": "stranger"})
    self.assertIsNone(daemon.pick_target())

  def test_the_local_switch_gates_the_process(self):
    running = _Daemon(SunnylinkEnabled=True, SunnylinkLocalEnabled=True)
    self.assertTrue(running.serviceable())

    switched_off = _Daemon(SunnylinkEnabled=True, SunnylinkLocalEnabled=False)
    self.assertFalse(switched_off.serviceable())

    sunnylink_off = _Daemon(SunnylinkEnabled=False, SunnylinkLocalEnabled=True)
    self.assertFalse(sunnylink_off.serviceable())

class TestLocalSurface(OpenpilotTestCase):
  """What a local peer may reach, and what it may never touch."""

  def test_a_local_session_can_never_write_local_params(self):
    """Enrollment only ever arrives through the cloud, so a local write is refused outright."""
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    saved: list[str] = []
    with mock.patch.object(sunnylinkd, "save_param_from_base64_encoded_string",
                           lambda key, value, compression=False: saved.append(key)):
      daemon.saveParams({ENROLL: ENROLLMENT_TRANSPORT_VALUE, "SunnylinkLocalApps": "{}", "SpeedLimitOffset": "5"})
    self.assertEqual(["SpeedLimitOffset"], saved)

  def test_session_methods_are_local_only_and_gated(self):
    session = _FakeSession()
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    methods = daemon.session_methods(cast(AuthorizedSession, session))
    self.assertTrue("getParams" in methods)
    self.assertTrue("saveParams" in methods)
    self.assertTrue("unpairLocalApp" in methods)
    self.assertNotIn("startLocalProxy", methods)
    self.assertNotIn("echo", methods)
    self.assertEqual(methods["getParams"](params_keys=[]), {"ok": True})
    self.assertEqual(session.calls, ["getParams"])

  def test_a_session_serves_local_methods_and_refuses_the_rest(self):
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    session = _FakeSession()
    methods = daemon.session_methods(cast(AuthorizedSession, session))
    ws = _FakeWs([
      rpc_module.dumps_call("getParams", {"params_keys": []}, 1),
      rpc_module.dumps_call("startLocalProxy", {"port": 8022}, 2),
    ])
    daemon.serve_rpc(cast(WebSocket, ws), methods)
    self.assertEqual(session.calls, ["getParams"])
    first, second = (json.loads(payload) for payload in ws.sent)
    self.assertEqual(1, first["id"])
    self.assertEqual({"ok": True}, first["result"])
    self.assertEqual(2, second["id"])
    self.assertEqual(rpc_module.METHOD_NOT_FOUND, second["error"]["code"])

class TestLocalDial(OpenpilotTestCase):
  """The pinned TLS dial and the challenge the phone must answer."""

  def test_the_device_proves_itself_to_the_phone_first(self):
    authority = SimpleNamespace(authenticate_device=lambda phone, challenge: {"phone_key_id": phone,
                                                                             "challenge": challenge})
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    ws = _FakeWs([_challenge("pinned-key")])
    daemon.authenticate_phone(cast(WebSocket, ws), cast(LocalAuthority, authority), "pinned-key")
    proof = json.loads(ws.sent[0])
    self.assertEqual("pinned-key", proof["phone_key_id"])
    self.assertEqual(CHALLENGE, proof["challenge"])

  def test_a_challenge_for_another_key_is_refused(self):
    authority = SimpleNamespace(authenticate_device=lambda phone, challenge: {})
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    with self.assertRaises(AuthorizationError):
      daemon.authenticate_phone(cast(WebSocket, _FakeWs([_challenge("someone-else")])),
                                cast(LocalAuthority, authority), "pinned-key")

  def test_a_malformed_challenge_is_refused(self):
    authority = SimpleNamespace(authenticate_device=lambda phone, challenge: {})
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    with self.assertRaises(AuthorizationError):
      daemon.authenticate_phone(cast(WebSocket, _FakeWs(["not json"])),
                                cast(LocalAuthority, authority), "pinned-key")

  def test_the_dial_confirms_a_pending_enrollment_before_serving(self):
    pending = SimpleNamespace(app_id="pending-key")
    grant = SimpleNamespace(app_id="pending-key")
    authority = SimpleNamespace(lock=threading.RLock(), pending=pending, grants={},
                                authenticate_device=lambda phone, challenge: {"phone_key_id": phone,
                                                                              "challenge": challenge})
    session = _FakeSession("pending-key")
    confirmed: list[str] = []
    ws = _FakeWs([_challenge(pending.app_id)])

    def confirm(key_id):
      confirmed.append(key_id)
      authority.grants[key_id] = grant
      authority.pending = None
      return {"app_id": grant.app_id, "app_name": "phone"}

    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    with mock.patch.object(authority, "session", lambda g, peer: session, create=True), \
         mock.patch.object(local_auth_daemon, "get_authority", lambda: authority), \
         mock.patch.object(local_auth_daemon, "confirm_enrollment_tls", confirm), \
         mock.patch.object(localsunnylinkd, "connect_pinned", lambda endpoint, key_id, timeout_s=10: ws):
      daemon.dial("wss://10.0.0.7:8443", None)

    self.assertEqual(["pending-key"], confirmed)
    self.assertTrue(session.closed)
    self.assertTrue(ws.closed)
    self.assertEqual("pending-key", json.loads(ws.sent[0])["phone_key_id"])

  def test_a_dial_without_an_enrolled_peer_never_serves(self):
    daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
    authority = SimpleNamespace(lock=threading.RLock(), pending=None, grants={})
    with mock.patch.object(local_auth_daemon, "get_authority", lambda: authority), \
         mock.patch.object(localsunnylinkd, "connect_pinned",
                           mock.Mock(side_effect=AuthorizationError("wrong TLS peer"))):
      with self.assertRaises(AuthorizationError):
        daemon.dial("wss://10.0.0.7:8443", None)

  def test_a_rename_only_ever_renames_the_sessions_own_grant(self):
    calls: list[tuple[str, str]] = []
    session = _CallingSession("grant-key")
    with mock.patch.object(local_auth_daemon, "set_grant_alias",
                           lambda key_id, alias: calls.append((key_id, alias)) or True):
      daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
      methods = daemon.session_methods(cast(AuthorizedSession, session))
      result = methods["updateLocalAppAlias"](app_id="another-phone", alias="Nayan's phone")
    self.assertEqual([("grant-key", "Nayan's phone")], calls)
    self.assertEqual({"success": True, "updated": True}, result)

  def test_an_alias_the_protocol_rejects_is_refused(self):
    def refuse(key_id, alias):
      raise AuthorizationError("invalid alias")

    session = _CallingSession("grant-key")
    with mock.patch.object(local_auth_daemon, "set_grant_alias", refuse):
      daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
      methods = daemon.session_methods(cast(AuthorizedSession, session))
      result = methods["updateLocalAppAlias"](app_id="grant-key", alias="bad\u0000alias")
    self.assertEqual({"success": False, "error": "invalid alias"}, result)

  def test_unpair_revokes_the_sessions_own_grant(self):
    revoked: list[str] = []
    session = _CallingSession("grant-key")
    with mock.patch.object(local_auth_daemon, "revoke_local_app",
                           lambda key_id: revoked.append(key_id) or True):
      daemon = localsunnylinkd.LocalSunnylinkd(params=cast(Params, _FakeParams()))
      methods = daemon.session_methods(cast(AuthorizedSession, session))
      result = methods["unpairLocalApp"](app_id="another-phone")
    self.assertEqual(["grant-key"], revoked)
    self.assertEqual({"success": True, "removed": True}, result)


class TestCloudCommandClaim(OpenpilotTestCase):
  """The handoff: the cloud daemon stores a command, the local daemon claims it."""

  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.persisted: list[dict] = []
    self.authority = LocalAuthority("cloud-device", "comma-device", self.device_key, persist=self.persisted.append)
    patcher = mock.patch.object(local_auth_daemon, "get_authority", lambda: self.authority)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_a_valid_enrollment_is_staged_and_the_command_is_claimed_once(self):
    params = _FakeParams({ENROLL: _enrollment_json(self.authority, self.app_key)})
    local_auth_daemon.claim_cloud_commands(cast(Params, params))

    self.assertIsNotNone(self.authority.pending)
    self.assertEqual("Test phone", self.authority.pending.app_name)
    self.assertEqual(key_id(self.app_key.public_key()), self.authority.pending.app_id)
    # Staged, not yet authorized, and never replayable.
    self.assertEqual([], self.persisted)
    self.assertNotIn(ENROLL, params)

  def test_a_bad_payload_is_refused_and_still_cleared(self):
    params = _FakeParams({ENROLL: "not an enrollment"})
    local_auth_daemon.claim_cloud_commands(cast(Params, params))

    self.assertIsNone(self.authority.pending)
    self.assertNotIn(ENROLL, params)

  def test_a_revocation_drops_the_phones_own_grant(self):
    committed = self.authority.enroll(_enrollment_json(self.authority, self.app_key), origin=Origin.CLOUD)
    self.authority.confirm(committed, committed.app_id)

    proof = statement("revoke", self.authority.cloud_device_id, self.authority.comma_device_id, committed.app_id)
    revocation = json.dumps({"v": VERSION, "cloud_device_id": self.authority.cloud_device_id,
                             "comma_device_id": self.authority.comma_device_id, "key_id": committed.app_id,
                             "signature": encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))})
    params = _FakeParams({REVOKE: revocation})
    local_auth_daemon.claim_cloud_commands(cast(Params, params))

    self.assertEqual({}, self.authority.grants)
    self.assertNotIn(REVOKE, params)

  def test_no_command_means_no_work(self):
    params = _FakeParams()
    local_auth_daemon.claim_cloud_commands(cast(Params, params))
    self.assertIsNone(self.authority.pending)

  def test_the_command_round_trips_through_the_real_library(self):
    """The declared param is a STRING, so the JSON the app pushes is what the claim reads."""
    directory = tempfile.mkdtemp(prefix="sunnylink_params_")
    self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
    params = Params(directory)

    params.put(ENROLL, _enrollment_json(self.authority, self.app_key), block=True)
    payload = params.get(ENROLL)
    if isinstance(payload, bytes):
      payload = payload.decode()

    local_auth_daemon.claim_cloud_commands(params)

    self.assertIsNotNone(self.authority.pending)
    self.assertEqual(b"", params.get(ENROLL) or b"")

  def test_local_param_policy(self):
    for key in ("SunnylinkLocalApps", "SunnylinkLocalNewTrustKey", "_sec_anything"):
      self.assertTrue(is_local_param(key))
    self.assertFalse(is_local_param("SpeedLimitOffset"))

    # The cloud's only way into the local side is its two commands.
    self.assertTrue(cloud_may_write(ENROLL))
    self.assertTrue(cloud_may_write(REVOKE))
    self.assertTrue(cloud_may_write("SpeedLimitOffset"))
    for key in ("SunnylinkLocalApps", "SunnylinkLocalRevoke", "_sec_x"):
      self.assertFalse(cloud_may_write(key))


class TestLocalDiscovery(OpenpilotTestCase):
  BEACON = b'SUNNYLINK1 {"v":1,"role":"app","app_id":"phone-1","ws_port":8443}'

  def test_fresh_beacons_are_recorded(self):
    discovery = LocalDiscovery()
    discovery._handle(self.BEACON, "10.0.0.7")
    discovery._handle(b'not a beacon', "10.0.0.8")
    self.assertEqual(["ws://10.0.0.7:8443"], discovery.fresh_endpoints())
    self.assertEqual([], discovery.fresh_endpoints(max_age_s=-1))

  def test_fresh_peers_carry_the_announcing_app_id(self):
    discovery = LocalDiscovery()
    discovery._handle(self.BEACON, "10.0.0.7")
    self.assertEqual([("ws://10.0.0.7:8443", "phone-1")], discovery.fresh_peers())


class TestEnrollmentTransportValue(OpenpilotTestCase):
  """The exact bytes the app pushes, kept in step with the mobile constant."""

  def test_the_transport_value_is_standard_base64(self):
    self.assertEqual('{"v":3}', base64.b64decode(ENROLLMENT_TRANSPORT_VALUE).decode())
