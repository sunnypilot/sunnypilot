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


class LocalSunnylinkd(Sunnylinkd):
  def __init__(self, params=None, discovery: LocalDiscovery | None = None):
    super().__init__(params)
    self.discovery = discovery if discovery is not None else LocalDiscovery()
    self.backoffs: dict[str, float] = {}
    self.failures: dict[str, int] = {}
    self.stop_event = threading.Event()

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
    while not self.stop_event.wait(TICK_INTERVAL_S) and self.serviceable():
      try:
        local_auth_daemon.service_pairing_window()
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

  def pick_target(self) -> str | None:
    if not self.enrolled():
      return None
    known = self.known_app_ids()
    self.forget_absent_endpoints(set(pinned_endpoints(self.discovery.fresh_endpoints(BACKOFF_FORGET_S))))
    now = time.monotonic()
    for endpoint, app_id in self.discovery.fresh_peers():
      if app_id not in known:
        continue
      pinned = pinned_endpoint(endpoint)
      if pinned is not None and self.backoffs.get(pinned, 0.0) <= now:
        return pinned
    return None

  def forget_absent_endpoints(self, present: set[str]) -> None:
    for endpoint in [k for k in self.backoffs if k not in present]:
      self.backoffs.pop(endpoint, None)
      self.failures.pop(endpoint, None)

  def _note_failure(self, endpoint: str) -> None:
    failures = self.failures.get(endpoint, 0) + 1
    self.failures[endpoint] = failures
    self.backoffs[endpoint] = time.monotonic() + min(ENDPOINT_BACKOFF_S * (2 ** (failures - 1)), ENDPOINT_BACKOFF_MAX_S)

  def _note_success(self, endpoint: str) -> None:
    self.backoffs.pop(endpoint, None)
    self.failures.pop(endpoint, None)

  def serve(self, endpoint: str, exit_event: threading.Event | None) -> None:
    try:
      self.dial(endpoint, exit_event)
    except Exception as e:
      self._note_failure(endpoint)
      self.params.remove("LastSunnylinkPingTime")
      log_connection_error(e)
      return
    self._note_success(endpoint)
    time.sleep(TICK_INTERVAL_S)

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
          local_auth_daemon.cancel_local_pairing()
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
