#!/usr/bin/env python3
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
ENDPOINT_BACKOFF_S = float(TICK_INTERVAL_S)
ENDPOINT_BACKOFF_MAX_S = 60.0
BACKOFF_FORGET_S = 12.0
MAX_LOCAL_SESSIONS = 8


class LocalSunnylinkd(Sunnylinkd):
  def __init__(self, params=None, discovery: LocalDiscovery | None = None):
    super().__init__(params)
    self.discovery = discovery if discovery is not None else LocalDiscovery()
    self.backoffs: dict[str, float] = {}
    self.failures: dict[str, int] = {}
    self._last_unknown_beacons: set[str] = set()
    self.stop_event = threading.Event()
    self._state_lock = threading.Lock()
    self._workers: dict[str, threading.Thread] = {}

  def enrolled(self) -> bool:
    return bool(local_auth_daemon.grants()) or local_auth_daemon.pending_enrollment() is not None

  def saveParams(self, params_to_update: dict[str, str], compression: bool = False) -> None:
    allowed = {k: v for k, v in params_to_update.items() if not is_local_param(k)}
    if len(allowed) != len(params_to_update):
      cloudlog.warning("sunnylinkd.local.saveParams.refused_local_params")
    if allowed:
      super().saveParams(allowed, compression)

  def serviceable(self) -> bool:
    return self.params.get_bool("SunnylinkEnabled") and not self.params.get_bool("SunnylinkTempFault") \
       and self.params.get_bool(LOCAL_ENABLED_PARAM)

  def run(self, exit_event: threading.Event | None = None) -> None:
    self.discovery.start()
    threading.Thread(target=self._tick_loop, name="localsunnylinkd_tick", daemon=True).start()

    try:
      while (exit_event is None or not exit_event.is_set()) and self.serviceable():
        for endpoint in self.pick_targets():
          self.start_session(endpoint, exit_event)
        time.sleep(TICK_INTERVAL_S)
    finally:
      self.stop_event.set()
      self.discovery.stop()

  def _tick_loop(self) -> None:
    while not self.stop_event.wait(TICK_INTERVAL_S) and self.serviceable():
      try:
        local_auth_daemon.service_revoke_requests()
        local_auth_daemon.claim_cloud_commands()
      except Exception:
        cloudlog.exception("sunnylinkd.local.tick_failed")

  def known_app_ids(self) -> set[str]:
    ids = {g["app_id"] for g in local_auth_daemon.grants()}
    pending = local_auth_daemon.pending_enrollment()
    if pending is not None:
      ids.add(pending["app_id"])
    return ids

  def pick_targets(self) -> list[str]:
    """Every endpoint worth dialing right now, a phone that is still PAIRING ahead of the rest.

    A car knows more than one phone (an iPhone and an Android side by side is the normal case)
    and each of them is an independent session, so "the next target" is a list rather than one
    address. The pending enrollment goes first: that is the phone whose app is showing
    "registration sent", and it must not queue behind phones that are already paired.
    """
    if not self.enrolled():
      return []
    known = self.known_app_ids()
    pending = local_auth_daemon.pending_enrollment()
    pending_app_id = pending["app_id"] if pending is not None else None
    self.forget_absent_endpoints(set(pinned_endpoints(self.discovery.fresh_endpoints(BACKOFF_FORGET_S))))
    now = time.monotonic()
    pairing: list[str] = []
    others: list[str] = []
    unknown: list[str] = []
    for endpoint, app_id in self.discovery.fresh_peers():
      if app_id not in known:
        unknown.append(app_id)
        continue
      pinned = pinned_endpoint(endpoint)
      if pinned is None or self.is_backed_off(pinned, now) or self.has_session(pinned):
        continue
      (pairing if app_id == pending_app_id else others).append(pinned)
    if unknown:
      seen = {a[:8] for a in unknown}
      if seen != self._last_unknown_beacons:
        self._last_unknown_beacons = seen
        cloudlog.debug(f"sunnylinkd.local.no_known_peer beacons={len(unknown)} unknown={sorted(seen)}")
    else:
      self._last_unknown_beacons = set()
    return pairing + others

  def pick_target(self) -> str | None:
    targets = self.pick_targets()
    return targets[0] if targets else None

  def is_backed_off(self, endpoint: str, now: float) -> bool:
    with self._state_lock:
      return self.backoffs.get(endpoint, 0.0) > now

  def has_session(self, endpoint: str) -> bool:
    with self._state_lock:
      worker = self._workers.get(endpoint)
      return worker is not None and worker.is_alive()

  def start_session(self, endpoint: str, exit_event: threading.Event | None) -> bool:
    """Serve [endpoint] on its own thread, unless one is already serving it.

    Sessions are long-lived: the phone keeps the connection for as long as its app is open so
    its reads can be answered over the LAN. They therefore cannot share the dial loop, or the
    first phone to connect is the only phone that ever will be.
    """
    with self._state_lock:
      existing = self._workers.get(endpoint)
      if existing is not None and existing.is_alive():
        return False
      if len(self._workers) >= MAX_LOCAL_SESSIONS:
        cloudlog.warning("sunnylinkd.local.sessions.saturated")
        return False
      worker = threading.Thread(
        target=self._session_thread,
        args=(endpoint, exit_event),
        name=f"localsunnylinkd_session_{endpoint}",
        daemon=True,
      )
      self._workers[endpoint] = worker
    worker.start()
    return True

  def _session_thread(self, endpoint: str, exit_event: threading.Event | None) -> None:
    try:
      self.serve(endpoint, exit_event)
    except Exception:
      cloudlog.exception("sunnylinkd.local.session_thread_failed")
    finally:
      with self._state_lock:
        if self._workers.get(endpoint) is threading.current_thread():
          del self._workers[endpoint]

  def forget_absent_endpoints(self, present: set[str]) -> None:
    with self._state_lock:
      for endpoint in [k for k in self.backoffs if k not in present]:
        self.backoffs.pop(endpoint, None)
        self.failures.pop(endpoint, None)

  def _note_failure(self, endpoint: str) -> None:
    with self._state_lock:
      failures = self.failures.get(endpoint, 0) + 1
      self.failures[endpoint] = failures
      self.backoffs[endpoint] = time.monotonic() + min(ENDPOINT_BACKOFF_S * (2 ** (failures - 1)), ENDPOINT_BACKOFF_MAX_S)

  def _note_success(self, endpoint: str) -> None:
    with self._state_lock:
      self.backoffs.pop(endpoint, None)
      self.failures.pop(endpoint, None)

  def serve(self, endpoint: str, exit_event: threading.Event | None) -> None:
    try:
      self.dial(endpoint, exit_event)
    except Exception as e:
      self._note_failure(endpoint)
      # LastSunnylinkPingTime belongs to the CLOUD link: sunnylinkd's pong handler and SunnylinkApi
      # own it, and the sidebar reads it to decide ONLINE/ERROR/OFFLINE. Clearing it here on a
      # failed LOCAL dial made a perfectly healthy cloud connection read as offline on the device
      # for as long as the next cloud ping took — which is what switching local mode off on the
      # phone looked like from the car.
      log_connection_error(e)
      return
    self._note_success(endpoint)

  def serve_rpc(self, ws: WebSocket, methods: dict[str, Callable[..., object]],
                exit_event: threading.Event | None = None) -> None:
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
    authority = local_auth_daemon.get_authority()
    if authority is None:
      raise AuthorizationError("enrollment unavailable")

    with authority.lock:
      pending_key_id = authority.pending.app_id if authority.pending is not None else None
      candidates = list(dict.fromkeys(([pending_key_id] if pending_key_id is not None else []) + list(authority.grants)))

    ws: WebSocket | None = None
    matched: str | None = None
    last_error: Exception | None = None
    cloudlog.debug(f"sunnylinkd.local.dial {endpoint} candidates={len(candidates)}")
    for key_id in candidates:
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
          cloudlog.exception("sunnylinkd.local.confirm_failed")
          local_auth_daemon.clear_pending_enrollment()
          raise
      with authority.lock:
        grant = authority.grants.get(matched)
      if grant is None:
        raise AuthorizationError("peer is not enrolled")
      session = authority.session(grant, matched)
      local_auth_daemon.note_grant_seen(grant.app_id)
      cloudlog.event("sunnylinkd.local.session_opened", endpoint=endpoint, app_id=grant.app_id)
      self.serve_rpc(ws, self.session_methods(session), exit_event)
    finally:
      if session is not None:
        session.close()
      if ws is not None:
        try:
          ws.close()
        except Exception:
          pass

  def authenticate_phone(self, ws: WebSocket, authority: LocalAuthority, phone_key_id: str) -> None:
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
    def gated(name: str, handler: Callable[..., object]) -> Callable[..., object]:
      def call(*args: object, **kwargs: object) -> object:
        return session.invoke(name, handler, *args, **kwargs)
      return call

    def unpair_local_app(app_id: str = "") -> dict[str, bool]:
      removed = local_auth_daemon.revoke_local_app(session.grant.app_id)
      return {"success": bool(removed), "removed": bool(removed)}

    def update_local_app_alias(app_id: str = "", alias: str = "") -> dict[str, bool | str]:
      try:
        local_auth_daemon.set_grant_alias(session.grant.app_id, alias)
      except AuthorizationError:
        return {"success": False, "error": "invalid alias"}
      return {"success": True, "updated": True}

    local = {"unpairLocalApp": unpair_local_app, "updateLocalAppAlias": update_local_app_alias}
    surface = self.methods()
    methods: dict[str, Callable[..., object]] = {}
    for name in LOCAL_METHODS:
      handler = local.get(name) or surface.get(name) or dispatcher.get(name)
      if handler is not None:
        methods[name] = gated(name, handler)
    return methods


def pinned_endpoint(beacon_endpoint: str) -> str | None:
  parsed = urlsplit(beacon_endpoint)
  if parsed.scheme != "ws" or parsed.hostname is None or parsed.port is None:
    return None
  return f"wss://{parsed.hostname}:{parsed.port}"


def pinned_endpoints(beacons: list[str]) -> list[str]:
  return [pinned for pinned in map(pinned_endpoint, beacons) if pinned is not None]


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

  LocalSunnylinkd().run(exit_event)


if __name__ == "__main__":
  main()
