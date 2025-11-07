#!/usr/bin/env python3

from __future__ import annotations

import base64
import errno
import gzip
import json
import os
import ssl
import threading
import time

from jsonrpc import dispatcher
from functools import partial
from openpilot.common.params import Params
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths
from openpilot.system.athena.athenad import ws_send, jsonrpc_handler, \
  recv_queue, UploadQueueCache, upload_queue, cur_upload_items, backoff, ws_manage, log_handler, start_local_proxy_shim, upload_handler, stat_handler
from websocket import (ABNF, WebSocket, WebSocketException, WebSocketTimeoutException,
                       create_connection, WebSocketConnectionClosedException)

import cereal.messaging as messaging
from sunnypilot.sunnylink.api import SunnylinkApi
from sunnypilot.sunnylink.utils import sunnylink_need_register, sunnylink_ready, get_param_as_byte, save_param_from_base64_encoded_string

SUNNYLINK_ATHENA_HOST = os.getenv('SUNNYLINK_ATHENA_HOST', 'wss://ws.stg.api.sunnypilot.ai')
HANDLER_THREADS = int(os.getenv('HANDLER_THREADS', "4"))
LOCAL_PORT_WHITELIST = {8022}
SUNNYLINK_LOG_ATTR_NAME = "user.sunny.upload"
SUNNYLINK_RECONNECT_TIMEOUT_S = 70  # FYI changing this will also would require a change on sidebar.cc
DISALLOW_LOG_UPLOAD = threading.Event()

params = Params()

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
              threading.Thread(target=ws_queue, args=(end_event,), name='ws_queue'),
              threading.Thread(target=upload_handler, args=(end_event,), name='upload_handler'),
              # threading.Thread(target=sunny_log_handler, args=(end_event, comma_prime_cellular_end_event), name='log_handler'),
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
        Params().put("LastSunnylinkPingTime", last_ping)
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


def ws_queue(end_event: threading.Event) -> None:
  sunnylink_dongle_id = params.get("SunnylinkDongleId")
  sunnylink_api = SunnylinkApi(sunnylink_dongle_id)
  resume_requested = False
  tries = 0

  while not end_event.is_set() and not resume_requested:
    try:
      if not resume_requested:
        cloudlog.debug("sunnylinkd.ws_queue.resume_queued")
        sunnylink_api.resume_queued(timeout=29)
        resume_requested = True
        tries = 0
    except Exception as e:
      if isinstance(e, (ConnectionError, TimeoutError)):
        cloudlog.warning(f"sunnylinkd.ws_queue.resume_queued.{type(e).__name__}")
      else:
        cloudlog.exception("sunnylinkd.ws_queue.resume_queued.exception")

      resume_requested = False
      tries += 1
      time.sleep(backoff(tries))

  if end_event.is_set():
    cloudlog.debug("end_event is set, exiting ws_queue thread")
  elif resume_requested:
    cloudlog.debug(f"Resume requested to server after {tries} tries")
  else:
    cloudlog.error(f"Reached end of ws_queue while end_event is not set and resume_requested is {resume_requested}")


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
def getParamsAllKeysV1() -> dict[str, str]:
  available_keys: list[str] = [k.decode('utf-8') for k in Params().all_keys()]

  params_dict: dict[str, list[dict[str, str | bool | int | None]]] = {"params": []}
  for key in available_keys:
    value = get_param_as_byte(key, get_default=True)
    params_dict["params"].append({
      "key": key,
      "type": int(params.get_type(key).value),
      "default_value": base64.b64encode(value).decode('utf-8') if value else None,
    })

  return {"keys": json.dumps(params_dict.get("params", []))}


@dispatcher.add_method
def getParams(params_keys: list[str], compression: bool = False) -> str | dict[str, str]:
  params = Params()
  available_keys: list[str] = [k.decode('utf-8') for k in Params().all_keys()]

  try:
    param_keys_validated = [key for key in params_keys if key in available_keys]
    params_dict: dict[str, list[dict[str, str | bool | int]]] = {"params": []}
    for key in param_keys_validated:
      value = get_param_as_byte(key)
      if value is None:
        continue

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
    try:
      save_param_from_base64_encoded_string(key, value, compression)
    except Exception as e:
      cloudlog.error(f"sunnylinkd.saveParams.exception {e}")


def startLocalProxy(global_end_event: threading.Event, remote_ws_uri: str, local_port: int) -> dict[str, int]:
  sunnylink_dongle_id = params.get("SunnylinkDongleId")
  sunnylink_api = SunnylinkApi(sunnylink_dongle_id)

  cloudlog.debug("athena.startLocalProxy.starting")
  ws = create_connection(
    remote_ws_uri,
    header={"Authorization": f"Bearer {sunnylink_api.get_token()}"},
    enable_multithread=True,
    sslopt={"cert_reqs": ssl.CERT_NONE}
  )

  return start_local_proxy_shim(global_end_event, local_port, ws)


def main(exit_event: threading.Event = None):
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  while sunnylink_need_register(params):
    cloudlog.info("Waiting for sunnylink registration to complete")
    time.sleep(10)

  sunnylink_dongle_id = params.get("SunnylinkDongleId")
  sunnylink_api = SunnylinkApi(sunnylink_dongle_id)
  UploadQueueCache.initialize(upload_queue)

  ws_uri = f"{SUNNYLINK_ATHENA_HOST}"
  conn_start = None
  conn_retries = 0
  while (exit_event is None or not exit_event.is_set()) and sunnylink_ready(params):
    try:
      if conn_start is None:
        conn_start = time.monotonic()

      cloudlog.event("sunnylinkd.main.connecting_ws", ws_uri=ws_uri, retries=conn_retries)
      ws = create_connection(
        ws_uri,
        header={"Authorization": f"Bearer {sunnylink_api.get_token()}"},
        enable_multithread=True,
        sslopt={"cert_reqs": ssl.CERT_NONE if "localhost" in ws_uri else ssl.CERT_REQUIRED},
        timeout=SUNNYLINK_RECONNECT_TIMEOUT_S,
      )
      cloudlog.event("sunnylinkd.main.connected_ws", ws_uri=ws_uri, retries=conn_retries,
                     duration=time.monotonic() - conn_start)
      conn_start = None

      conn_retries = 0
      cur_upload_items.clear()

      handle_long_poll(ws, exit_event)
    except (KeyboardInterrupt, SystemExit):
      break
    except Exception as e:
      conn_retries += 1
      params.remove("LastSunnylinkPingTime")

      if isinstance(e, (ConnectionError, TimeoutError, WebSocketException)):
        cloudlog.warning(f"sunnylinkd.main.{type(e).__name__}")
      elif isinstance(e, OSError):
        name = errno.errorcode.get(e.errno or -1, "UNKNOWN")
        msg = f"sunnylinkd.main.OSError.{name} ({e.errno})"
        is_expected_error = e.errno in (errno.ENETDOWN, errno.ENETRESET, errno.ENETUNREACH)
        cloudlog.warning(msg) if is_expected_error else cloudlog.exception(msg)
      else:
        cloudlog.exception("sunnylinkd.main.exception")

    time.sleep(backoff(conn_retries))

  if not sunnylink_ready(params):
    cloudlog.debug("Reached end of sunnylinkd.main while sunnylink is not ready. Waiting 60s before retrying")
    time.sleep(60)


if __name__ == "__main__":
  main()
