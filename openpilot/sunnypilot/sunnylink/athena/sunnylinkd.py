#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import base64
import errno
import gzip
import json
import os
import ssl
import threading
import time

from functools import partial
from openpilot.system.athena.rpc import dispatcher
from openpilot.common.params import Params, ParamKeyType
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from openpilot.common.hardware.hw import Paths
from openpilot.system.athena.athenad import ws_send, jsonrpc_handler, \
  recv_queue, UploadQueueCache, upload_queue, cur_upload_items, backoff, ws_manage, log_handler, start_local_proxy_shim, upload_handler, stat_handler
from websocket import (ABNF, WebSocket, WebSocketException, WebSocketTimeoutException,
                       create_connection, WebSocketConnectionClosedException)

import openpilot.cereal.messaging as messaging
from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL, DEFAULT_BIG_MODEL
from openpilot.sunnypilot.selfdrive.car.sync_sunnylink_params import update_car_list_param
from openpilot.system.athena import rpc as rpc_module
from openpilot.sunnypilot.sunnylink.api import SunnylinkApi
from openpilot.sunnypilot.sunnylink.utils import sunnylink_need_register, sunnylink_ready, get_param_as_byte, save_param_from_base64_encoded_string
from openpilot.sunnypilot.sunnylink.capabilities import generate_capabilities, CAPABILITY_LABELS
from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
from openpilot.sunnypilot.sunnylink.athena.local_discovery import LOCAL_BEACON_FRESH_S, AppBeacon, LocalDiscovery
from openpilot.sunnypilot.sunnylink.athena.local_pairing import (
  PAIRING_WINDOW_S,
  LocalApp,
  PairingCodeRotator,
  add_local_app,
  clear_pairing_request,
  get_local_apps,
  is_locally_paired,
  local_identity,
  pairing_requested,
  remove_local_app,
  set_local_app_alias,
  verify_pairing_code,
)

SUNNYLINK_ATHENA_HOST = os.getenv('SUNNYLINK_ATHENA_HOST', 'wss://athena.sunnylink.ai')
HANDLER_THREADS = int(os.getenv('HANDLER_THREADS', "4"))
LOCAL_PORT_WHITELIST = {8022}
SUNNYLINK_LOG_ATTR_NAME = "user.sunny.upload"
SUNNYLINK_RECONNECT_TIMEOUT_S = 70  # FYI changing this will also would require a change on sidebar.cc
DISALLOW_LOG_UPLOAD = threading.Event()

LOCAL_PAIRING_SESSION_TIMEOUT_S = PAIRING_WINDOW_S
LOCAL_PROBE_INTERVAL_S = 60
LOCAL_ENDPOINT_BACKOFF_S = 300
PAIRING_WATCHDOG_INTERVAL_S = 2.0

_active_local_endpoint: str | None = None
_active_ws: WebSocket | None = None
_pairing_in_progress = threading.Event()

params = Params()

# Parameters that should never be remotely modified
BLOCKED_PARAMS = {
  "AdbEnabled",
  "CompletedSunnylinkConsentVersion",
  "CompletedTrainingVersion",
  "GithubUsername",  # Could grant SSH access
  "GithubSshKeys",   # Direct SSH key injection
  "HasAcceptedTerms",
  "HasAcceptedTermsSP",
  "OnroadCycleRequested",      # Prevent remote cycle trigger
  "ParamsVersion",         # Device-managed version counter
}


def handle_long_poll(ws: WebSocket, exit_event: threading.Event | None) -> None:
  cloudlog.info("sunnylinkd.handle_long_poll started")
  sm = messaging.SubMaster(['deviceState'])
  end_event = threading.Event()
  comma_prime_cellular_end_event = threading.Event()

  threads = [
              threading.Thread(target=ws_manage, args=(ws, end_event), name='ws_manage'),
              threading.Thread(target=ws_recv, args=(ws, end_event), name='ws_recv'),
              threading.Thread(target=ws_send, args=(ws, end_event), name='ws_send'),
              threading.Thread(target=ws_ping, args=(ws, end_event), name='ws_ping'),
              threading.Thread(target=upload_handler, args=(end_event,), name='upload_handler'),
              threading.Thread(target=sunny_log_handler, args=(end_event, comma_prime_cellular_end_event), name='log_handler'),
              threading.Thread(target=stat_handler, args=(end_event, Paths.stats_sp_root(), True), name='stat_handler'),
            ] + [
              threading.Thread(target=jsonrpc_handler, args=(end_event, partial(startLocalProxy, end_event),), name=f'worker_{x}')
              for x in range(HANDLER_THREADS)
            ]

  for thread in threads:
    thread.start()
  try:
    while not end_event.wait(0.1):
      if not sunnylink_ready(params):
        cloudlog.warning("Exiting sunnylinkd.handle_long_poll as SunnylinkEnabled is False")
        break

      sm.update(0)
      if exit_event is not None and exit_event.is_set():
        end_event.set()
        comma_prime_cellular_end_event.set()

      prime_type = params.get("PrimeType") or 0
      metered = sm['deviceState'].networkMetered

      if DISALLOW_LOG_UPLOAD.is_set() and not comma_prime_cellular_end_event.is_set():
        cloudlog.debug("sunnylinkd.handle_long_poll: DISALLOW_LOG_UPLOAD, setting comma_prime_cellular_end_event")
        comma_prime_cellular_end_event.set()
      elif metered and int(prime_type) > 2:
        cloudlog.debug(f"sunnylinkd.handle_long_poll: PrimeType({prime_type}) > 2 and networkMetered({metered})")
        comma_prime_cellular_end_event.set()
      elif comma_prime_cellular_end_event.is_set() and not DISALLOW_LOG_UPLOAD.is_set():
        cloudlog.debug(
          f"sunnylinkd.handle_long_poll: comma_prime_cellular_end_event is set and not PrimeType({prime_type}) > 2 or not networkMetered({metered})")
        comma_prime_cellular_end_event.clear()
  finally:
    end_event.set()
    comma_prime_cellular_end_event.set()
    for thread in threads:
      cloudlog.debug(f"sunnylinkd athena.joining {thread.name}")
      thread.join()
      cloudlog.debug(f"sunnylinkd athena.joined {thread.name}")


def ws_recv(ws: WebSocket, end_event: threading.Event) -> None:
  last_ping = int(time.monotonic() * 1e9)
  while not end_event.is_set():
    try:
      opcode, data = ws.recv_data(control_frame=True)
      if opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY):
        if opcode == ABNF.OPCODE_TEXT:
          data = data.decode("utf-8")
        recv_queue.put_nowait(data)
        cloudlog.debug(f"sunnylinkd.ws_recv.recv {data}")
      elif opcode in (ABNF.OPCODE_PING, ABNF.OPCODE_PONG):
        cloudlog.debug("sunnylinkd.ws_recv.pong")
        last_ping = int(time.monotonic() * 1e9)
        Params().put("LastSunnylinkPingTime", last_ping, block=True)
    except WebSocketTimeoutException:
      ns_since_last_ping = int(time.monotonic() * 1e9) - last_ping
      if ns_since_last_ping > SUNNYLINK_RECONNECT_TIMEOUT_S * 1e9:
        cloudlog.warning("sunnylinkd.ws_recv.timeout")
        end_event.set()
    except Exception as e:
      if isinstance(e, WebSocketConnectionClosedException):
        cloudlog.warning(f"sunnylinkd.ws_recv.{type(e).__name__}")
      else:
        cloudlog.exception("sunnylinkd.ws_recv.exception")
      end_event.set()


def ws_ping(ws: WebSocket, end_event: threading.Event) -> None:
  ws.ping()  # Send the first ping
  while not end_event.wait(SUNNYLINK_RECONNECT_TIMEOUT_S * 0.7):  # Sleep about 70% before a timeout
    try:
      ws.ping()
      cloudlog.debug("sunnylinkd.ws_recv.ws_ping: Pinging")
    except Exception:
      cloudlog.exception("sunnylinkd.ws_ping.exception")
      end_event.set()
  cloudlog.debug("sunnylinkd.ws_ping.end_event is set, exiting ws_ping thread")


def sunny_log_handler(end_event: threading.Event, comma_prime_cellular_end_event: threading.Event) -> None:
  while not end_event.wait(0.1):
    if not comma_prime_cellular_end_event.is_set():
      log_handler(comma_prime_cellular_end_event, SUNNYLINK_LOG_ATTR_NAME)
  comma_prime_cellular_end_event.set()


@dispatcher.add_method
def toggleLogUpload(enabled: bool):
  DISALLOW_LOG_UPLOAD.clear() if enabled and DISALLOW_LOG_UPLOAD.is_set() else DISALLOW_LOG_UPLOAD.set()


@dispatcher.add_method
def getParamsAllKeys() -> list[str]:
  keys: list[str] = [k.decode('utf-8') for k in Params().all_keys()]
  return keys


@dispatcher.add_method
def getParamsMetadata() -> str:
  """Return settings_ui.json + live capabilities as gzip-compressed, base64-encoded string.

  Reads settings_ui.json, injects live capabilities from CarParams, compresses,
  and returns. Single RPC for the frontend to get the complete settings UI and
  runtime capabilities.
  """
  try:
    schema = generate_schema()
    schema["capabilities"] = generate_capabilities()
    schema["capability_labels"] = CAPABILITY_LABELS
    schema["default_model"] = DEFAULT_MODEL
    schema["default_big_model"] = DEFAULT_BIG_MODEL
    schema["chestnut_active"] = params.get_bool("ChestnutActive")
    raw = json.dumps(schema, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(raw)).decode("utf-8")
  except Exception:
    cloudlog.exception("sunnylinkd.getParamsMetadata.exception")
    raise


@dispatcher.add_method
def getParams(params_keys: list[str], compression: bool = False) -> str | dict[str, str]:
  params = Params()
  available_keys: list[str] = [k.decode('utf-8') for k in Params().all_keys()]

  try:
    zero_values: dict[int, bytes] = {
      ParamKeyType.STRING.value: b"",
      ParamKeyType.BOOL.value: b"0",
      ParamKeyType.INT.value: b"0",
      ParamKeyType.FLOAT.value: b"0.0",
      ParamKeyType.TIME.value: b"",
      ParamKeyType.JSON.value: b"{}",
      ParamKeyType.BYTES.value: b"",
    }

    param_keys_validated = [key for key in params_keys if key in available_keys]
    params_dict: dict[str, list[dict[str, str | bool | int]]] = {"params": []}
    for key in param_keys_validated:
      value = get_param_as_byte(key)
      if value is None:
        value = get_param_as_byte(key, get_default=True)
      if value is None:
        param_type = params.get_type(key)
        value = zero_values.get(param_type.value, b"")

      params_dict["params"].append({
        "key": key,
        "value": base64.b64encode(gzip.compress(value) if compression else value).decode('utf-8'),
        "type": int(params.get_type(key).value),
        "is_compressed": compression
      })

    response = {str(param.get('key')): str(param.get('value')) for param in params_dict.get("params", [])}
    response |= {"params": json.dumps(params_dict.get("params", []))} # Upcoming for settings v1
    return response

  except Exception as e:
    cloudlog.exception("sunnylinkd.getParams.exception", e)
    raise


@dispatcher.add_method
def saveParams(params_to_update: dict[str, str], compression: bool = False) -> None:
  for key, value in params_to_update.items():
    # disallow modifications to blocked parameters
    if key in BLOCKED_PARAMS:
      cloudlog.warning(f"sunnylinkd.saveParams.blocked: Attempted to modify blocked parameter '{key}'")
      continue

    try:
      save_param_from_base64_encoded_string(key, value, compression)
    except Exception as e:
      cloudlog.error(f"sunnylinkd.saveParams.exception {e}")

  # Increment version counter for frontend change detection
  try:
    current = int(params.get("ParamsVersion") or "0")
    params.put("ParamsVersion", str(current + 1), block=True)
  except Exception:
    pass


def startLocalProxy(global_end_event: threading.Event, remote_ws_uri: str, local_port: int) -> dict[str, int]:
  sunnylink_dongle_id = params.get("SunnylinkDongleId")
  sunnylink_api = SunnylinkApi(sunnylink_dongle_id)

  cloudlog.debug("athena.startLocalProxy.starting")
  ws = create_connection(
    remote_ws_uri, header={"Authorization": f"Bearer {sunnylink_api.get_token()}"}, enable_multithread=True, sslopt={"cert_reqs": ssl.CERT_NONE}
  )

  return start_local_proxy_shim(global_end_event, local_port, ws)


@dispatcher.add_method
def pairLocalApp(code: str, app_id: str = "", app_name: str = "", alias: str = "") -> dict[str, bool | str]:
  """Complete pairing with the app on the CURRENT local connection."""
  if _active_local_endpoint is None:
    return {"success": False, "error": "not connected to a local app"}
  if not verify_pairing_code(code):
    cloudlog.warning("sunnylinkd.pairLocalApp.invalid_code")
    return {"success": False, "error": "invalid code"}
  add_local_app(LocalApp(app_id=app_id or f"app@{_active_local_endpoint}",
                         endpoint=_active_local_endpoint, app_name=app_name, alias=alias))
  clear_pairing_request()
  return {"success": True}


@dispatcher.add_method
def updateLocalAppAlias(app_id: str, alias: str) -> dict[str, bool | str]:
  if _active_local_endpoint is None:
    return {"success": False, "error": "not connected to a local app"}
  updated = set_local_app_alias(app_id, alias)
  return {"success": True, "updated": updated}


@dispatcher.add_method
def unpairLocalApp(app_id: str) -> dict[str, bool | str]:
  if _active_local_endpoint is None:
    return {"success": False, "error": "not connected to a local app"}
  removed = remove_local_app(app_id)
  return {"success": True, "removed": removed}


def _auth_header(is_local: bool) -> dict[str, str]:
  """Bearer header for a dial."""
  api = SunnylinkApi(params.get("SunnylinkDongleId"))
  payload = {"identity": local_identity()} if is_local else None
  return {"Authorization": f"Bearer {api.get_token(payload_extra=payload)}"}


def _pairing_session(ws: WebSocket, timeout_s: float = LOCAL_PAIRING_SESSION_TIMEOUT_S) -> bool:
  """Serve only the pairing RPCs to an app that isn't in the registry yet —
  everything else is refused. Returns True if pairing completed (the connection may then
  serve normally)."""
  cloudlog.info("sunnylinkd.pairing_session.started")
  ws.settimeout(10)
  deadline = time.monotonic() + timeout_s
  try:
    while time.monotonic() < deadline and pairing_requested():
      try:
        raw = ws.recv()  # auto-pongs pings; blocks up to the socket timeout
      except WebSocketTimeoutException:
        continue
      except Exception as e:
        cloudlog.warning(f"sunnylinkd.pairing_session.{type(e).__name__}")
        return is_locally_paired()
      try:
        msg = rpc_module.loads(raw)
      except Exception:
        continue
      if not rpc_module.is_call(msg):
        continue
      if msg.get("method") not in ("pairLocalApp", "unpairLocalApp"):
        continue  # refuse anything but pairing until paired
      try:
        ws.send(rpc_module.handle(msg, dispatcher))
      except Exception as e:
        cloudlog.warning(f"sunnylinkd.pairing_session.{type(e).__name__}")
        return is_locally_paired()
    return is_locally_paired()
  finally:
    ws.settimeout(SUNNYLINK_RECONNECT_TIMEOUT_S)


def _pick_ws_uri(discovery: LocalDiscovery, backoffs: dict[str, float]) -> tuple[str, str]:
  now = time.monotonic()
  apps = get_local_apps()
  app_ids = {app.app_id for app in apps}
  if pairing_requested():
    latest = discovery.latest_endpoint()
    seen = discovery.last_seen_ago()
    app_id = discovery.latest_app_id()
    if latest is not None and seen is not None and seen <= LOCAL_BEACON_FRESH_S \
       and app_id is not None and app_id not in app_ids \
       and backoffs.get(latest, 0.0) <= now:
      return latest, "pairing_offer"
    return SUNNYLINK_ATHENA_HOST, "cloud"
  fresh_endpoint = discovery.latest_paired_endpoint()
  fresh_seen = discovery.latest_paired_seen_ago()
  fresh_app_id = discovery.latest_paired_app_id()
  fresh_ok = (fresh_endpoint is not None and fresh_seen is not None
              and fresh_seen <= LOCAL_BEACON_FRESH_S and fresh_app_id is not None
              and fresh_app_id in app_ids)
  if fresh_ok and backoffs.get(fresh_endpoint, 0.0) <= now:
    return fresh_endpoint, "paired_local"
  for app in reversed(apps):
    if fresh_ok and app.app_id == fresh_app_id:
      continue
    if backoffs.get(app.endpoint, 0.0) <= now:
      return app.endpoint, "paired_local"
  return SUNNYLINK_ATHENA_HOST, "cloud"


def _probe_local_apps(active_ws: WebSocket, discovery: LocalDiscovery,
                      backoffs: dict[str, float], stop_event: threading.Event) -> None:
  while not stop_event.wait(LOCAL_PROBE_INTERVAL_S):
    if pairing_requested():
      # The pairing watchdog owns an armed window; don't migrate mid-window.
      continue
    now = time.monotonic()
    candidate: str | None = None
    for app in reversed(get_local_apps()):
      if backoffs.get(app.endpoint, 0.0) <= now:
        candidate = app.endpoint
        break
    if candidate is None:
      continue
    try:
      probe = create_connection(candidate, header=_auth_header(is_local=True), timeout=10)
      probe.close()
    except Exception:
      backoffs[candidate] = now + LOCAL_ENDPOINT_BACKOFF_S
      continue
    cloudlog.event("sunnylinkd.local_probe.reachable", endpoint=candidate)
    try:
      active_ws.close()
    except Exception:
      pass
    break


def _handle_paired_refresh(backoffs: dict[str, float], force_attempts: dict[str, float],
                           beacon: AppBeacon) -> None:
  if not any(app.app_id == beacon.app_id for app in get_local_apps()):
    return
  for app in get_local_apps():
    if app.app_id == beacon.app_id:
      backoffs.pop(app.endpoint, None)
  backoffs.pop(beacon.endpoint, None)
  if _pairing_in_progress.is_set():
    return
  if _active_local_endpoint == beacon.endpoint:
    return
  if _active_local_endpoint is not None:
    return
  now = time.monotonic()
  if force_attempts.get(beacon.endpoint, 0.0) + LOCAL_BEACON_FRESH_S > now:
    return
  force_attempts[beacon.endpoint] = now
  ws = _active_ws
  if ws is not None:
    cloudlog.event("sunnylinkd.paired_refresh.reconnect",
                   app_id=beacon.app_id, endpoint=beacon.endpoint)
    try:
      ws.close()
    except Exception:
      pass


def _pairing_watchdog(active_ws: WebSocket, backoffs: dict[str, float],
                      stop_event: threading.Event,
                      interval_s: float = PAIRING_WATCHDOG_INTERVAL_S) -> None:
  """Watch for the pairing window being armed mid-session and force a
  re-selection to the newly-discovered app."""
  while not stop_event.wait(interval_s):
    if not pairing_requested():
      continue
    cloudlog.event("sunnylinkd.pairing_watchdog.arm_detected")
    for key in list(backoffs):
      backoffs.pop(key, None)
    try:
      active_ws.close()
    except Exception:
      pass
    break


def main(exit_event: threading.Event | None = None):
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  discovery = LocalDiscovery()
  code_rotator = PairingCodeRotator()
  discovery.start()
  code_rotator.start()

  try:
    _connection_loop(exit_event, discovery)
  finally:
    discovery.stop()
    code_rotator.stop_event.set()


def _serviceable(params: Params) -> bool:
  """sunnylinkd should run when sunnylink is enabled and not on a temporary
  fault. This deliberately includes the unregistered/unpaired state so a
  never-registered device can still be discovered and paired over the LAN (the
  actual session gates — registration/local pairing — are handled per
  connection inside the loop)."""
  return params.get_bool("SunnylinkEnabled") and not params.get_bool("SunnylinkTempFault")


def _connection_loop(exit_event: threading.Event | None, discovery: LocalDiscovery) -> None:
  """Local-first, cloud-fallback connection loop: a paired local endpoint
  first, cloud when unreachable, and a pairing session to a freshly-discovered
  app when a window is armed."""
  global _active_local_endpoint, _active_ws

  UploadQueueCache.initialize(upload_queue)
  update_car_list_param()

  conn_start = None
  conn_retries = 0
  backoffs: dict[str, float] = {}
  force_attempts: dict[str, float] = {}
  discovery.paired_refresh_cb = partial(_handle_paired_refresh, backoffs, force_attempts)

  while (exit_event is None or not exit_event.is_set()) and _serviceable(params):
    ws_uri, kind = _pick_ws_uri(discovery, backoffs)

    if kind == "cloud" and pairing_requested():
      cloudlog.debug("sunnylinkd.main.pairing_waiting_for_beacon")
      time.sleep(3)
      continue

    if kind == "cloud" and sunnylink_need_register(params):
      cloudlog.info("Waiting for sunnylink registration or local pairing to complete")
      time.sleep(10)
      continue

    if conn_start is None:
      conn_start = time.monotonic()

    cloudlog.event("sunnylinkd.main.connecting_ws", ws_uri=ws_uri, kind=kind, retries=conn_retries)
    try:
      ws = create_connection(
        ws_uri,
        header=_auth_header(is_local=kind != "cloud"),
        enable_multithread=True,
        sslopt={"cert_reqs": ssl.CERT_NONE if "localhost" in ws_uri else ssl.CERT_REQUIRED},
        timeout=SUNNYLINK_RECONNECT_TIMEOUT_S,
      )
    except Exception as e:
      if kind != "cloud":
        backoffs[ws_uri] = time.monotonic() + LOCAL_ENDPOINT_BACKOFF_S
      conn_retries += 1
      params.remove("LastSunnylinkPingTime")
      _log_connection_error(e)
      time.sleep(backoff(conn_retries))
      continue

    cloudlog.event("sunnylinkd.main.connected_ws", ws_uri=ws_uri, kind=kind, retries=conn_retries,
                   duration=time.monotonic() - conn_start)
    conn_start = None
    conn_retries = 0
    cur_upload_items.clear()
    _active_ws = ws

    probe_stop: threading.Event | None = None
    watch_stop: threading.Event | None = None
    session_endpoint: str | None = ws_uri if kind != "cloud" else None
    try:
      if kind == "pairing_offer":
        _active_local_endpoint = ws_uri
        _pairing_in_progress.set()
        try:
          paired_ok = _pairing_session(ws)
        finally:
          _pairing_in_progress.clear()
        if not paired_ok:
          backoffs[ws_uri] = time.monotonic() + LOCAL_ENDPOINT_BACKOFF_S
          conn_retries += 1
          params.remove("LastSunnylinkPingTime")
          try:
            ws.close()
          except Exception:
            pass
          time.sleep(backoff(conn_retries))
          continue
        # Paired during the session — this connection may now serve normally.
        kind = "paired_local"

      if kind == "paired_local":
        _active_local_endpoint = ws_uri
      else:
        _active_local_endpoint = None
        # While on the cloud link, watch for the local app and migrate back.
        probe_stop = threading.Event()
        threading.Thread(target=_probe_local_apps,
                         args=(ws, discovery, backoffs, probe_stop),
                         name="sunnylinkd_local_probe", daemon=True).start()

      # Started after any pairing session on this connection, so it can never
      # close the connection the code is typed over.
      watch_stop = threading.Event()
      threading.Thread(target=_pairing_watchdog, args=(ws, backoffs, watch_stop),
                       name="sunnylinkd_pairing_watchdog", daemon=True).start()

      handle_long_poll(ws, exit_event)
    except (KeyboardInterrupt, SystemExit):
      break
    except Exception as e:
      conn_retries += 1
      params.remove("LastSunnylinkPingTime")
      _log_connection_error(e)
    finally:
      if probe_stop is not None:
        probe_stop.set()
      if watch_stop is not None:
        watch_stop.set()
      if session_endpoint is not None and kind == "paired_local":
        backoffs.pop(session_endpoint, None)
      if _active_local_endpoint == session_endpoint:
        _active_local_endpoint = None
      if _active_ws is ws:
        _active_ws = None

    time.sleep(backoff(conn_retries))

  if not _serviceable(params):
    cloudlog.debug("Reached end of sunnylinkd.main while sunnylink is not serviceable. Waiting 60s before retrying")
    time.sleep(60)


def _log_connection_error(e: Exception) -> None:
  if isinstance(e, (ConnectionError, TimeoutError, WebSocketException)):
    cloudlog.warning(f"sunnylinkd.main.{type(e).__name__}")
  elif isinstance(e, OSError):
    name = errno.errorcode.get(e.errno or -1, "UNKNOWN")
    msg = f"sunnylinkd.main.OSError.{name} ({e.errno})"
    is_expected_error = e.errno in (errno.ENETDOWN, errno.ENETRESET, errno.ENETUNREACH)
    cloudlog.warning(msg) if is_expected_error else cloudlog.exception(msg)
  else:
    cloudlog.exception("sunnylinkd.main.exception")


if __name__ == "__main__":
  main()
