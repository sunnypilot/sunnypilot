#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import json
import threading
import time

from collections.abc import Callable
from urllib.parse import urlsplit

from websocket import WebSocket, WebSocketTimeoutException

from openpilot.system.athena.rpc import dispatcher
from openpilot.system.athena import rpc as rpc_module
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.sunnylink.athena import local_auth_daemon
from openpilot.sunnypilot.sunnylink.athena.local_auth import (
  AUTHENTICATE_PURPOSE,
  LOCAL_METHODS,
  VERSION,
  AuthorizationError,
  AuthorizedSession,
  LocalAuthority,
  connect_pinned,
  parse_object,
)
from openpilot.sunnypilot.sunnylink.athena.local_discovery import LocalDiscovery
from openpilot.sunnypilot.sunnylink.athena.local_params import is_local_param
from openpilot.sunnypilot.sunnylink.athena.sunnylinkd import SUNNYLINK_RECONNECT_TIMEOUT_S, Sunnylinkd, log_connection_error

LOCAL_ENABLED_PARAM = "SunnylinkLocalEnabled"
SESSION_READ_TIMEOUT_S = 5
TICK_INTERVAL_S = 1.0
# A local endpoint is THE phone, and the app is a foreground-only server the user opens and closes,
# so a dial that failed because the app was closed must not outlive it: the first failure costs a
# single tick and doubles from there. The ramp is capped at a minute, because every step of it is a
# few seconds of the user's device sitting on the cloud instead of the LAN. A
# phone whose beacons have lapsed clears its own record entirely (see `forget_absent_endpoints`).
ENDPOINT_BACKOFF_S = float(TICK_INTERVAL_S)
ENDPOINT_BACKOFF_MAX_S = 60.0
# How long a phone may stay silent before its backoff record is dropped. Deliberately shorter than
# the beacon freshness window: a Wi-Fi roam or a switch to another network (home -> the car's
# hotspot) silences the app for a few beacon intervals while it reassociates, and the ramp it had
# accumulated on the old link has nothing to do with the new one. While it is inside that window
# the endpoint stays dialable, so the next beacon gets an immediate attempt rather than a penalty.
BACKOFF_FORGET_S = 12.0


class LocalSunnylinkd(Sunnylinkd):
  """The LAN half of sunnylink, in its own process.

  It inherits the settings RPCs and adds what is local: discovery, pinned-TLS sessions with the
  cloud-enrolled phones, and the UI's trust requests. It never dials the cloud, so the cloud link
  keeps running while a phone is connected here.
  """

  def __init__(self, params=None, discovery: LocalDiscovery | None = None):
    super().__init__(params)
    self.discovery = discovery if discovery is not None else LocalDiscovery(pairing_window_cb=self.pairing_window_open)
    self.backoffs: dict[str, float] = {}
    # Consecutive failed dials per endpoint, which is what turns the backoff into a ramp.
    self.failures: dict[str, int] = {}
    self.stop_event = threading.Event()

  # --- local trust --------------------------------------------------------

  def enrolled(self) -> bool:
    """True once any phone is enrolled, or an enrollment is waiting to be confirmed."""
    return bool(local_auth_daemon.grants()) or local_auth_daemon.pending_enrollment() is not None

  def pairing_window_open(self) -> bool:
    """A live pairing window counts as a beacon-display window for the settings screen."""
    try:
      return local_auth_daemon.read_pairing_qr() is not None
    except Exception:
      return False

  def saveParams(self, params_to_update: dict[str, str], compression: bool = False) -> None:
    """Local sessions never touch local params: enrollment and revocation only ever arrive
    through the cloud settings-write, so a phone cannot enroll or rename itself here."""
    allowed = {key: value for key, value in params_to_update.items() if not is_local_param(key)}
    if len(allowed) != len(params_to_update):
      cloudlog.warning("sunnylinkd.local.saveParams.refused_local_params")
    if allowed:
      super().saveParams(allowed, compression)

  # --- loop ---------------------------------------------------------------

  def serviceable(self) -> bool:
    """Serve the LAN while sunnylink is on, this process is switched on, and there is no fault.

    A locally paired device is often not cloud-registered at all, so registration is not part of
    this: the cloud daemon waits for it, the local one never does.
    """
    return self.params.get_bool("SunnylinkEnabled") and not self.params.get_bool("SunnylinkTempFault") \
       and self.params.get_bool(LOCAL_ENABLED_PARAM)

  def run(self, exit_event: threading.Event | None = None) -> None:
    self.discovery.start()
    threading.Thread(target=self._tick_loop, name="localsunnylinkd_tick", daemon=True).start()

    try:
      while (exit_event is None or not exit_event.is_set()) and self.serviceable():
        endpoint = self.pick_target()
        if endpoint is None:
          time.sleep(TICK_INTERVAL_S)
        else:
          self.serve(endpoint, exit_event)
    finally:
      self.stop_event.set()
      self.discovery.stop()
      local_auth_daemon.clear_pairing_window()

  def _tick_loop(self) -> None:
    """The UI's trust requests and the cloud's local commands, ~once a second, in their own
    thread: the serving loop above blocks for as long as a session lasts."""
    while not self.stop_event.wait(TICK_INTERVAL_S) and self.serviceable():
      try:
        local_auth_daemon.service_pairing_window()
        local_auth_daemon.service_revoke_requests()
        local_auth_daemon.claim_cloud_commands()
      except Exception:
        cloudlog.exception("sunnylinkd.local.tick_failed")

  def pick_target(self) -> str | None:
    """Where to dial next: the freshest phone beacon that is not backing off.

    Dialing finds the phone by its pinned TLS key, so any fresh endpoint is worth one attempt: the
    key is the authorization, and a peer without it cannot complete the handshake.
    """
    if not self.enrolled():
      return None

    now = time.monotonic()
    pinned_targets = [pinned for pinned in (pinned_endpoint(beacon) for beacon in self.discovery.fresh_endpoints())
                      if pinned is not None]
    # Backoff bookkeeping reads a shorter window than dialing does: a phone that went quiet for a
    # few beacon intervals (a roam, a network switch) keeps its endpoint but loses its ramp.
    recent = {pinned for pinned in (pinned_endpoint(beacon) for beacon in self.discovery.fresh_endpoints(max_age_s=BACKOFF_FORGET_S))
              if pinned is not None}
    self.forget_absent_endpoints(recent)
    for pinned in pinned_targets:
      if self.backoffs.get(pinned, 0.0) <= now:
        return pinned
    return None

  def forget_absent_endpoints(self, present: set[str]) -> None:
    """Drop the backoff of a phone that stopped announcing.

    While the app is closed there is no beacon and nothing to dial, so a failure recorded then says
    nothing about the phone the user opens next: the silence window is what tells "the app is gone"
    apart from "the app cannot be served". Only a phone that keeps announcing keeps backing off.
    The caller passes the short `BACKOFF_FORGET_S` window, so a phone that went quiet across a
    network change also loses the ramp it earned on the link it is no longer on.
    """
    for endpoint in [key for key in self.backoffs if key.startswith("wss://") and key not in present]:
      self.backoffs.pop(endpoint, None)
      self.failures.pop(endpoint, None)

  def serve(self, endpoint: str, exit_event: threading.Event | None) -> None:
    try:
      self.dial(endpoint, exit_event)
    except Exception as e:
      failures = self.failures.get(endpoint, 0) + 1
      self.failures[endpoint] = failures
      self.backoffs[endpoint] = time.monotonic() + min(ENDPOINT_BACKOFF_S * (2 ** (failures - 1)),
                                                       ENDPOINT_BACKOFF_MAX_S)
      self.params.remove("LastSunnylinkPingTime")
      log_connection_error(e)
      return

    self.backoffs.pop(endpoint, None)
    self.failures.pop(endpoint, None)
    # A finished session is not an error, but never redial in a tight loop.
    time.sleep(TICK_INTERVAL_S)

  def serve_rpc(self, ws: WebSocket, methods: dict[str, Callable[..., object]],
                exit_event: threading.Event | None = None) -> None:
    """Answer JSON-RPC calls on one socket until the peer goes away or the session ends."""
    ws.settimeout(SESSION_READ_TIMEOUT_S)
    while exit_event is None or not exit_event.is_set():
      try:
        raw = ws.recv()
      except WebSocketTimeoutException:
        continue
      except Exception as e:
        cloudlog.warning(f"sunnylinkd.session.{type(e).__name__}")
        return
      try:
        msg = rpc_module.loads(raw)
      except Exception:
        continue
      if not rpc_module.is_call(msg):
        continue
      try:
        response = rpc_module.handle(msg, methods)
      except ValueError:
        continue
      try:
        ws.send(response)
      except Exception as e:
        cloudlog.warning(f"sunnylinkd.send.{type(e).__name__}")
        return

  def dial(self, endpoint: str, exit_event: threading.Event | None) -> None:
    """Dial an enrolled (or enrolling) phone over pinned TLS and serve it.

    The pinned key IS the authorization, so trying each known key is safe: a peer without the
    matching private key cannot complete the handshake.
    """
    authority = local_auth_daemon.get_authority()
    if authority is None:
      raise AuthorizationError("enrollment unavailable")

    with authority.lock:
      pending_key_id = authority.pending.key_id if authority.pending is not None else None
      candidates = ([pending_key_id] if pending_key_id is not None else []) + list(authority.grants)

    ws: WebSocket | None = None
    matched: str | None = None
    last_error: Exception | None = None
    for key_id in dict.fromkeys(candidates):
      try:
        ws = connect_pinned(endpoint, key_id)
        matched = key_id
        break
      except Exception as e:
        last_error = e
    if ws is None or matched is None:
      raise last_error or AuthorizationError("no enrolled app at this endpoint")

    session: AuthorizedSession | None = None
    try:
      self.authenticate_phone(ws, authority, matched)

      if pending_key_id is not None and matched == pending_key_id:
        try:
          local_auth_daemon.confirm_enrollment_tls(matched)
        except Exception:
          # The window closed or failed: drop the stale pending rather than redial forever.
          cloudlog.exception("sunnylinkd.local.confirm_failed")
          local_auth_daemon.cancel_local_pairing()
          raise

      with authority.lock:
        grant = authority.grants.get(matched)
      if grant is None:
        raise AuthorizationError("peer is not enrolled")

      session = authority.session(grant, matched)
      local_auth_daemon.note_grant_seen(grant.key_id)
      cloudlog.event("sunnylinkd.local.session_opened", endpoint=endpoint, app_id=grant.app_id)
      self.serve_rpc(ws, self.session_methods(session), exit_event)
    finally:
      if session is not None:
        session.close()
      close_quietly(ws)

  def authenticate_phone(self, ws: WebSocket, authority: LocalAuthority, phone_key_id: str) -> None:
    """Answer the phone's fresh challenge, so it can authenticate THIS device first.

    Nothing else is sent, and no request is served, on a session the phone has not verified.
    """
    ws.settimeout(SUNNYLINK_RECONNECT_TIMEOUT_S)
    raw = ws.recv()
    if not isinstance(raw, str):
      raise AuthorizationError("invalid challenge")
    data = parse_object(raw)
    if set(data) != {"v", "purpose", "phone_key_id", "challenge"} \
       or type(data["v"]) is not int or data["v"] != VERSION \
       or data["purpose"] != AUTHENTICATE_PURPOSE \
       or data["phone_key_id"] != phone_key_id:
      raise AuthorizationError("invalid challenge")
    ws.send(json.dumps(authority.authenticate_device(phone_key_id, data["challenge"]), separators=(",", ":")))

  def session_methods(self, session: AuthorizedSession) -> dict[str, Callable[..., object]]:
    """Strictly LOCAL_METHODS, re-authorized by the session immediately before each call."""
    def gated(name: str, handler: Callable[..., object]) -> Callable[..., object]:
      def call(*args: object, **kwargs: object) -> object:
        return session.invoke(name, handler, *args, **kwargs)
      return call

    def unpair_local_app(app_id: str = "") -> dict[str, bool]:
      removed = local_auth_daemon.revoke_local_app(session.grant.key_id)
      return {"success": bool(removed), "removed": bool(removed)}

    def update_local_app_alias(app_id: str = "", alias: str = "") -> dict[str, bool | str]:
      # The principal is the session's grant, so a phone can only rename itself.
      try:
        local_auth_daemon.set_grant_alias(session.grant.key_id, alias)
      except AuthorizationError:
        return {"success": False, "error": "invalid alias"}
      return {"success": True, "updated": True}

    # This daemon's own handlers win, so an overridden method is the one a session reaches.
    overridden = ("unpairLocalApp", "updateLocalAppAlias")
    surface = self.methods()
    methods: dict[str, Callable[..., object]] = {}
    for name in LOCAL_METHODS:
      if name in overridden:
        continue
      handler = surface.get(name) or dispatcher.get(name)
      if handler is not None:
        methods[name] = gated(name, handler)
    methods["unpairLocalApp"] = gated("unpairLocalApp", unpair_local_app)
    methods["updateLocalAppAlias"] = gated("updateLocalAppAlias", update_local_app_alias)
    return methods


def pinned_endpoint(beacon_endpoint: str) -> str | None:
  """Beacons announce `ws://ip:port`; a dial uses the same host and port over pinned TLS."""
  parsed = urlsplit(beacon_endpoint)
  if parsed.scheme != "ws" or parsed.hostname is None or parsed.port is None:
    return None
  return f"wss://{parsed.hostname}:{parsed.port}"


def close_quietly(ws: WebSocket | None) -> None:
  if ws is None:
    return
  try:
    ws.close()
  except Exception:
    pass


def main(exit_event: threading.Event | None = None):
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  daemon = LocalSunnylinkd()
  for method in daemon.methods().values():
    dispatcher.add_method(method)
  daemon.run(exit_event)


if __name__ == "__main__":
  main()
